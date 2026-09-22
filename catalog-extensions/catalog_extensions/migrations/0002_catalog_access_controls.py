from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog_extensions", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="microcoursecatalogmetadata",
            options={
                "permissions": [
                    ("view_restricted_catalog", "Can view the restricted CBA catalog"),
                ],
                "verbose_name": "CBA microcourse catalog metadata",
                "verbose_name_plural": "CBA microcourse catalog metadata",
            },
        ),
        migrations.AddField(
            model_name="microcoursecatalogmetadata",
            name="catalog_visibility",
            field=models.CharField(
                choices=[("public", "Public"), ("hidden", "Hidden")],
                db_index=True,
                default="public",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="microcoursecatalogmetadata",
            name="access_scope",
            field=models.CharField(
                choices=[
                    ("public", "Public"),
                    ("organization_code", "Organization code"),
                    ("program_only", "Certificate program only"),
                ],
                db_index=True,
                default="public",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="microcoursecatalogmetadata",
            name="access_policy_key",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Stable Wagtail policy identifier; never store an organization code here.",
                max_length=128,
            ),
        ),
        migrations.AddField(
            model_name="microcoursecatalogmetadata",
            name="standalone_enrollment_allowed",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="certificateprogramcatalogmetadata",
            name="catalog_visibility",
            field=models.CharField(
                choices=[("public", "Public"), ("hidden", "Hidden")],
                db_index=True,
                default="public",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="certificateprogramcatalogmetadata",
            name="access_scope",
            field=models.CharField(
                choices=[("public", "Public"), ("organization_code", "Organization code")],
                db_index=True,
                default="public",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="certificateprogramcatalogmetadata",
            name="access_policy_key",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Stable Wagtail policy identifier; never store an organization code here.",
                max_length=128,
            ),
        ),
    ]
