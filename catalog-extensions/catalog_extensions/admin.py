from django.contrib import admin

from catalog_extensions.models.course import (
    CourseRunFacultyAssignment,
    MicrocourseCatalogMetadata,
)
from catalog_extensions.models.program import (
    CertificateProgramCatalogMetadata,
    ProgramCourseRequirement,
    ProgramFacultyAssignment,
)


@admin.register(MicrocourseCatalogMetadata)
class MicrocourseCatalogMetadataAdmin(admin.ModelAdmin):
    list_display = ("course_run", "duration_minutes", "catalog_status", "modified")
    list_filter = ("catalog_status",)
    search_fields = ("course_run__key", "course_run__course__title")


@admin.register(CertificateProgramCatalogMetadata)
class CertificateProgramCatalogMetadataAdmin(admin.ModelAdmin):
    list_display = (
        "program_code",
        "program",
        "catalog_status",
        "pacing",
        "price",
        "currency",
        "modified",
    )
    list_filter = ("catalog_status", "currency")
    search_fields = ("program_code", "program__title")


@admin.register(ProgramCourseRequirement)
class ProgramCourseRequirementAdmin(admin.ModelAdmin):
    list_display = ("program", "sequence", "course_run", "required")
    list_filter = ("required",)
    search_fields = ("program__title", "course_run__key")


@admin.register(ProgramFacultyAssignment)
class ProgramFacultyAssignmentAdmin(admin.ModelAdmin):
    list_display = ("program", "display_order", "person", "role", "is_primary")
    list_filter = ("role", "is_primary")
    search_fields = ("program__title", "person__given_name", "person__family_name")


@admin.register(CourseRunFacultyAssignment)
class CourseRunFacultyAssignmentAdmin(admin.ModelAdmin):
    list_display = ("course_run", "display_order", "person", "role")
    list_filter = ("role",)
    search_fields = ("course_run__key", "person__given_name", "person__family_name")
