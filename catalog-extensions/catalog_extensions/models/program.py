from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from course_discovery.apps.course_metadata.models import CourseRun, Person, Program

from catalog_extensions.models.course import (
    AccessScope,
    CatalogStatus,
    CatalogVisibility,
    FacultyRole,
)


class CertificateProgramCatalogMetadata(models.Model):
    """CBA catalog fields for a certificate program."""

    program = models.OneToOneField(
        Program,
        on_delete=models.CASCADE,
        related_name="cba_catalog",
    )
    primary_catalog_category = models.ForeignKey(
        "catalog_extensions.CatalogCategory",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="primary_certificate_programs",
    )
    catalog_categories = models.ManyToManyField(
        "catalog_extensions.CatalogCategory",
        blank=True,
        related_name="certificate_programs",
    )
    program_code = models.CharField(max_length=64, unique=True, db_index=True)
    short_description = models.TextField(blank=True)
    full_description = models.TextField(blank=True)
    catalog_status = models.CharField(
        max_length=32,
        choices=CatalogStatus.choices,
        default=CatalogStatus.DRAFT,
        db_index=True,
    )
    catalog_visibility = models.CharField(
        max_length=16,
        choices=CatalogVisibility.choices,
        default=CatalogVisibility.PUBLIC,
        db_index=True,
    )
    access_scope = models.CharField(
        max_length=32,
        choices=(
            (AccessScope.PUBLIC, "Public"),
            (AccessScope.ORGANIZATION_CODE, "Organization code"),
        ),
        default=AccessScope.PUBLIC,
        db_index=True,
    )
    access_policy_key = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
        help_text="Stable Wagtail policy identifier; never store an organization code here.",
    )
    duration_minutes = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1)],
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    currency = models.CharField(max_length=3, default="USD")
    pacing = models.CharField(max_length=32, default="self_paced")
    course_overview = models.TextField(blank=True)
    syllabus = models.TextField(blank=True)
    completion_requirements = models.TextField(blank=True)
    learning_outcomes = models.JSONField(default=list, blank=True)
    references = models.JSONField(default=list, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CBA certificate program catalog metadata"
        verbose_name_plural = "CBA certificate program catalog metadata"

    def __str__(self):
        return f"{self.program_code}: {self.program.title}"


class ProgramCourseRequirement(models.Model):
    """Explicit ordered microcourse membership for the Wagtail catalog."""

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="cba_course_requirements",
    )
    course_run = models.ForeignKey(
        CourseRun,
        on_delete=models.CASCADE,
        related_name="cba_program_requirements",
    )
    sequence = models.PositiveIntegerField(default=1)
    required = models.BooleanField(default=True)

    class Meta:
        ordering = ("sequence", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("program", "course_run"),
                name="cba_unique_program_course_run",
            ),
            models.UniqueConstraint(
                fields=("program", "sequence"),
                name="cba_unique_program_sequence",
            ),
        ]

    def __str__(self):
        return f"{self.program.title} #{self.sequence}: {self.course_run.key}"


class ProgramFacultyAssignment(models.Model):
    """Allows each certificate program to display any number of faculty members."""

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="cba_faculty_assignments",
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="cba_program_assignments",
    )
    role = models.CharField(
        max_length=32,
        choices=FacultyRole.choices,
        default=FacultyRole.INSTRUCTOR,
    )
    credentials = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ("display_order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("program", "person", "role"),
                name="cba_unique_program_person_role",
            )
        ]

    def __str__(self):
        return f"{self.person.full_name} — {self.get_role_display()}"
