# CBA Discovery Catalog Extensions

This Django application extends Open edX Discovery with the CBA fields required
by the Wagtail catalog. It supports microcourses, certificate programs, ordered
program pathways, exact duration, waitlist state, structured outcomes and
references, syllabi, completion requirements, and multiple faculty members.

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

The public CBA routes are mounted at `/api/cba/v1/` by the supplied URL override.

## Data flow

1. Create or bulk-create the microcourse shells in Studio.
2. Refresh/synchronize Studio course metadata into Discovery.
3. Validate the CBA JSON catalog file.
4. Import the complete catalog data into Discovery.
5. Have Wagtail consume the read-only `/api/cba/v1/` endpoints.

The importer intentionally refuses to invent a missing Studio course. This
prevents a catalog record from claiming that a usable Open edX course exists
when no corresponding Studio shell has been created.

See `docs/api/CATALOG_API.md` for fields and commands.
