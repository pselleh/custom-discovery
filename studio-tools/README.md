# CBA Studio course-shell loader

`import_cba_studio_courses.py` creates or updates Open edX Studio course shells from a CBA catalog JSON file.

Run it through the CMS Django shell. The loader reads these environment variables:

- `CBA_CATALOG_FILE`: container path to the catalog JSON file.
- `CBA_STUDIO_USER`: username that owns created or updated courses.
- `CBA_VALIDATE_ONLY`: set to `true` for a read-only validation run.
- `CBA_UPDATE_EXISTING`: set to `true` only when existing courses may be updated.

Always run with `CBA_VALIDATE_ONLY=true` first and review the JSON summary.
A validation run must report no errors and must leave `created`, `updated`, and `existing` empty when all course keys are new.

Example:

```bash
tutor local run --no-deps \
  -v "/absolute/package/path:/mnt/cba-bulk:ro" \
  -v "/absolute/tool/path:/mnt/cba-tools:ro" \
  -e CBA_CATALOG_FILE="/mnt/cba-bulk/catalog.json" \
  -e CBA_STUDIO_USER="cbaadmin" \
  -e CBA_VALIDATE_ONLY="true" \
  -e CBA_UPDATE_EXISTING="false" \
  cms \
  sh -c 'python manage.py cms shell < /mnt/cba-tools/import_cba_studio_courses.py'
```

Creating courses is a production write. Before changing `CBA_VALIDATE_ONLY` to `false`, back up the modulestore and relational databases and confirm the validated course-key list.
