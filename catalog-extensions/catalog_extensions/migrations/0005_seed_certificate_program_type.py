import uuid

from django.db import migrations


PROGRAM_TYPE_SLUG = "certificate"
PROGRAM_TYPE_NAME = "Certificate"

PROGRAM_TYPE_UUID = uuid.uuid5(
    uuid.NAMESPACE_URL,
    (
        "https://centerforbusinessacceleration.com/"
        "discovery/program-types/certificate"
    ),
)


def seed_certificate_program_type(apps, schema_editor):
    ProgramType = apps.get_model(
        "course_metadata",
        "ProgramType",
    )

    if ProgramType.objects.filter(
        slug=PROGRAM_TYPE_SLUG,
    ).exists():
        return

    program_type = ProgramType(
        name=PROGRAM_TYPE_NAME,
        slug=PROGRAM_TYPE_SLUG,
        uuid=PROGRAM_TYPE_UUID,
        logo_image="",
        coaching_supported=False,
    )

    # Discovery's AutoSlugField uses the runtime translation alias
    # ``name_t``. Historical migration models do not expose that
    # property, so provide it explicitly before saving.
    program_type.name_t = PROGRAM_TYPE_NAME
    program_type.save(force_insert=True)


class Migration(migrations.Migration):
    dependencies = [
        (
            "catalog_extensions",
            "0004_seed_catalog_categories",
        ),
    ]

    operations = [
        migrations.RunPython(
            seed_certificate_program_type,
            migrations.RunPython.noop,
        ),
    ]
