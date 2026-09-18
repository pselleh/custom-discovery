from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("course_metadata", "0356_add_course_editor_update_bulk_operation"),
    ]

    operations = [
        migrations.CreateModel(
            name="MicrocourseCatalogMetadata",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("duration_minutes", models.PositiveIntegerField(default=60, validators=[django.core.validators.MinValueValidator(1)])),
                ("catalog_status", models.CharField(choices=[("draft", "Draft"), ("waitlist_open", "Waitlist open"), ("enrollment_open", "Enrollment open"), ("enrollment_closed", "Enrollment closed"), ("archived", "Archived")], db_index=True, default="draft", max_length=32)),
                ("course_overview", models.TextField(blank=True)),
                ("learning_outcomes", models.JSONField(blank=True, default=list)),
                ("references", models.JSONField(blank=True, default=list)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("course_run", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="cba_catalog", to="course_metadata.courserun")),
            ],
            options={"verbose_name": "CBA microcourse catalog metadata", "verbose_name_plural": "CBA microcourse catalog metadata"},
        ),
        migrations.CreateModel(
            name="CertificateProgramCatalogMetadata",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("program_code", models.CharField(db_index=True, max_length=64, unique=True)),
                ("short_description", models.TextField(blank=True)),
                ("full_description", models.TextField(blank=True)),
                ("catalog_status", models.CharField(choices=[("draft", "Draft"), ("waitlist_open", "Waitlist open"), ("enrollment_open", "Enrollment open"), ("enrollment_closed", "Enrollment closed"), ("archived", "Archived")], db_index=True, default="draft", max_length=32)),
                ("duration_minutes", models.PositiveIntegerField(default=60, validators=[django.core.validators.MinValueValidator(1)])),
                ("price", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal("0.00"))])),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("pacing", models.CharField(default="self_paced", max_length=32)),
                ("course_overview", models.TextField(blank=True)),
                ("syllabus", models.TextField(blank=True)),
                ("completion_requirements", models.TextField(blank=True)),
                ("learning_outcomes", models.JSONField(blank=True, default=list)),
                ("references", models.JSONField(blank=True, default=list)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("program", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="cba_catalog", to="course_metadata.program")),
            ],
            options={"verbose_name": "CBA certificate program catalog metadata", "verbose_name_plural": "CBA certificate program catalog metadata"},
        ),
        migrations.CreateModel(
            name="CourseRunFacultyAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("program_director", "Program Director"), ("lead_sme", "Lead Subject-Matter Expert"), ("instructor", "Instructor"), ("facilitator", "Facilitator"), ("course_author", "Course Author"), ("technical_reviewer", "Technical Reviewer")], default="instructor", max_length=32)),
                ("credentials", models.CharField(blank=True, max_length=255)),
                ("display_order", models.PositiveIntegerField(default=0)),
                ("course_run", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cba_faculty_assignments", to="course_metadata.courserun")),
                ("person", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cba_course_assignments", to="course_metadata.person")),
            ],
            options={"ordering": ("display_order", "id")},
        ),
        migrations.CreateModel(
            name="ProgramCourseRequirement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sequence", models.PositiveIntegerField(default=1)),
                ("required", models.BooleanField(default=True)),
                ("course_run", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cba_program_requirements", to="course_metadata.courserun")),
                ("program", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cba_course_requirements", to="course_metadata.program")),
            ],
            options={"ordering": ("sequence", "id")},
        ),
        migrations.CreateModel(
            name="ProgramFacultyAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("program_director", "Program Director"), ("lead_sme", "Lead Subject-Matter Expert"), ("instructor", "Instructor"), ("facilitator", "Facilitator"), ("course_author", "Course Author"), ("technical_reviewer", "Technical Reviewer")], default="instructor", max_length=32)),
                ("credentials", models.CharField(blank=True, max_length=255)),
                ("display_order", models.PositiveIntegerField(default=0)),
                ("is_primary", models.BooleanField(default=False)),
                ("person", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cba_program_assignments", to="course_metadata.person")),
                ("program", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cba_faculty_assignments", to="course_metadata.program")),
            ],
            options={"ordering": ("display_order", "id")},
        ),
        migrations.AddConstraint(model_name="courserunfacultyassignment", constraint=models.UniqueConstraint(fields=("course_run", "person", "role"), name="cba_unique_course_run_person_role")),
        migrations.AddConstraint(model_name="programcourserequirement", constraint=models.UniqueConstraint(fields=("program", "course_run"), name="cba_unique_program_course_run")),
        migrations.AddConstraint(model_name="programcourserequirement", constraint=models.UniqueConstraint(fields=("program", "sequence"), name="cba_unique_program_sequence")),
        migrations.AddConstraint(model_name="programfacultyassignment", constraint=models.UniqueConstraint(fields=("program", "person", "role"), name="cba_unique_program_person_role")),
    ]
