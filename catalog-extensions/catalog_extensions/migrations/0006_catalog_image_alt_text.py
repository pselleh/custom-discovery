from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog_extensions", "0005_seed_certificate_program_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="microcoursecatalogmetadata",
            name="image_alt",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="certificateprogramcatalogmetadata",
            name="image_alt",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
