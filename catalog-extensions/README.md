# CBA Discovery Catalog Extensions

This Django application extends Open edX Discovery with the CBA fields required
by the Wagtail catalog. It supports microcourses, certificate programs, ordered
program pathways, exact duration, waitlist state, structured outcomes and
references, syllabi, completion requirements, and multiple faculty members.
Version 0.3.0 also separates public catalog discovery from restricted access.
Organization codes and learner grants remain in the LMS `orgcode-enterprise`
application; Discovery stores only a non-secret `access_policy_key`.

## Installation

The Docker image installs this package. Discovery must also register the Django
application through its deployment configuration:

```yaml
EXTRA_APPS:
  - catalog_extensions
```

After deploying the image, run:

```bash
python manage.py migrate catalog_extensions
python manage.py check
```

The public CBA routes are mounted at `/api/cba/v1/`. Authenticated Wagtail
service calls use `/api/cba/v1/internal/` when retrieving restricted records.

## Data flow

1. Validate and bulk-create the microcourse shells in Studio with the supplied
   Verawood Studio loader.
2. Refresh/synchronize Studio course metadata into Discovery.
3. Validate the CBA JSON catalog file.
4. Import the complete catalog data into Discovery.
5. Have Wagtail consume the read-only `/api/cba/v1/` endpoints.
6. Have Wagtail obtain the signed-in learner's grants from the LMS and use a
   dedicated service account to read restricted Discovery records.

The importer intentionally refuses to invent a missing Studio course. This
prevents a catalog record from claiming that a usable Open edX course exists
when no corresponding Studio shell has been created.

See `docs/api/CATALOG_API.md` for fields and commands.
