# CBA Studio course-shell and image loader

`import_cba_studio_courses.py` creates or updates Open edX Studio course shells
from a CBA catalog JSON file and stores each microcourse's native Studio course
image.

## Environment variables

Run the loader through the CMS Django shell. It reads:

- `CBA_CATALOG_FILE`: container path to the catalog JSON file.
- `CBA_STUDIO_USER`: username or email that owns created or updated courses.
- `CBA_VALIDATE_ONLY`: set to `true` for a read-only validation run.
- `CBA_UPDATE_EXISTING`: set to `true` only when existing courses and their
  images may be updated.

## Microcourse image contract

Each microcourse record must contain `course_image` and `image_alt`:

```json
{
  "course_key": "course-v1:CBA+RMP103+2027",
  "course_image": "images/microcourses/RMP103/images_course_image.jpg",
  "image_alt": "Introduction to Mastering Risk Management"
}
```

The image path must:

- Be relative to the directory containing the catalog JSON file.
- Remain inside the catalog package.
- Use the native Studio filename `images_course_image.jpg`.
- Point to a valid JPEG image.

The loader stores the file in Studio under the native asset key:

```text
asset-v1:CBA+RMP103+2027+type@asset+block@images_course_image.jpg
```

After Studio-to-Discovery synchronization, Discovery supplies the corresponding
native `image_url` through the catalog API.

## Validation first

Always run with `CBA_VALIDATE_ONLY=true` first. A successful validation reports:

- The expected number of validated course records and images.
- Course keys under `would_create` or `would_update`.
- Image keys under `would_upload_images`.
- Empty `created`, `updated`, `uploaded_images`, and `errors` lists.

Validation mode does not create courses, update courses, or upload images.

## Example

```bash
tutor local run --rm --no-deps \
  -v "/absolute/package/path:/mnt/cba-bulk:ro" \
  -v "/absolute/tool/path:/mnt/cba-tools:ro" \
  -e CBA_CATALOG_FILE="/mnt/cba-bulk/catalog.json" \
  -e CBA_STUDIO_USER="cbaadmin" \
  -e CBA_VALIDATE_ONLY="true" \
  -e CBA_UPDATE_EXISTING="false" \
  cms \
  sh -c 'python manage.py cms shell < /mnt/cba-tools/import_cba_studio_courses.py'
```

Creating courses and uploading images are production writes. Before setting
`CBA_VALIDATE_ONLY=false`, back up the Open edX MySQL database and MongoDB
modulestore, review the exact course-key list, and confirm every image.
