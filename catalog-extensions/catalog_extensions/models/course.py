from django.core.validators import MinValueValidator
from django.db import models

from course_discovery.apps.course_metadata.models import CourseRun, Person


class CatalogStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    WAITLIST_OPEN = "waitlist_open", "Waitlist open"
    ENROLLMENT_OPEN = "enrollment_open", "Enrollment open"
    ENROLLMENT_CLOSED = "enrollment_closed", "Enrollment closed"
    ARCHIVED = "archived", "Archived"


class FacultyRole(models.TextChoices):
    PROGRAM_DIRECTOR = "program_director", "Program Director"
    LEAD_SUBJECT_MATTER_EXPERT = "lead_sme", "Lead Subject-Matter Expert"
    INSTRUCTOR = "instructor", "Instructor"
    FACILITATOR = "facilitator", "Facilitator"
    COURSE_AUTHOR = "course_author", "Course Author"
    TECHNICAL_REVIEWER = "technical_reviewer", "Technical Reviewer"


class MicrocourseCatalogMetadata(models.Model):
    """CBA catalog fields that are not represented by native Discovery fields."""

    course_run = models.OneToOneField(
        CourseRun,
        on_delete=models.CASCADE,
        related_name="cba_catalog",
    )
    duration_minutes = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1)],
    )
    catalog_status = models.CharField(
        max_length=32,
        choices=CatalogStatus.choices,
        default=CatalogStatus.DRAFT,
        db_index=True,
    )
    course_overview = models.TextField(blank=True)
    learning_outcomes = models.JSONField(default=list, blank=True)
    references = models.JSONField(default=list, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CBA microcourse catalog metadata"
        verbose_name_plural = "CBA microcourse catalog metadata"

    def __str__(self):
        return str(self.course_run.key)


class CourseRunFacultyAssignment(models.Model):
    """Public-facing course faculty; separate from Studio course-team permissions."""

    course_run = models.ForeignKey(
        CourseRun,
        on_delete=models.CASCADE,
        related_name="cba_faculty_assignments",
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="cba_course_assignments",
    )
    role = models.CharField(
        max_length=32,
        choices=FacultyRole.choices,
        default=FacultyRole.INSTRUCTOR,
    )
    credentials = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("course_run", "person", "role"),
                name="cba_unique_course_run_person_role",
            )
        ]

    def __str__(self):
        return f"{self.person.full_name} — {self.get_role_display()}"
