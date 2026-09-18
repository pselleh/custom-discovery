from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from catalog_extensions.api.serializers.course import (
    CourseListSerializer,
    CourseRunSerializer,
    FacultyAssignmentSerializer,
)
from catalog_extensions.api.serializers.organization import OrganizationSerializer
from catalog_extensions.api.serializers.subject import SubjectSerializer


def _metadata(program):
    try:
        return program.cba_catalog
    except ObjectDoesNotExist:
        return None


class ProgramFacultyAssignmentSerializer(FacultyAssignmentSerializer):
    is_primary = serializers.BooleanField(read_only=True)


class ProgramCourseRequirementSerializer(serializers.Serializer):
    sequence = serializers.IntegerField(read_only=True)
    required = serializers.BooleanField(read_only=True)
    microcourse = CourseRunSerializer(source="course_run", read_only=True)
    short_description = serializers.CharField(source="course_run.course.short_description", read_only=True)
    full_description = serializers.CharField(source="course_run.course.full_description", read_only=True)
    syllabus = serializers.CharField(source="course_run.course.syllabus_raw", read_only=True)


class ProgramSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    program_code = serializers.SerializerMethodField()
    title = serializers.CharField(read_only=True)
    subtitle = serializers.CharField(read_only=True)
    short_description = serializers.SerializerMethodField()
    full_description = serializers.SerializerMethodField()
    marketing_slug = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    catalog_status = serializers.SerializerMethodField()
    overview = serializers.CharField(read_only=True)
    course_overview = serializers.SerializerMethodField()
    syllabus = serializers.SerializerMethodField()
    completion_requirements = serializers.SerializerMethodField()
    learning_outcomes = serializers.SerializerMethodField()
    references = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    pacing = serializers.SerializerMethodField()
    marketing_url = serializers.CharField(read_only=True)
    banner_image = serializers.SerializerMethodField()
    card_image = serializers.SerializerMethodField()
    organizations = OrganizationSerializer(source="authoring_organizations", many=True, read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)
    courses = CourseListSerializer(many=True, read_only=True)
    microcourses = ProgramCourseRequirementSerializer(source="cba_course_requirements", many=True, read_only=True)
    program_faculty = ProgramFacultyAssignmentSerializer(source="cba_faculty_assignments", many=True, read_only=True)
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    def get_program_code(self, obj):
        metadata = _metadata(obj)
        return metadata.program_code if metadata else ""

    def get_short_description(self, obj):
        metadata = _metadata(obj)
        return metadata.short_description if metadata else obj.subtitle

    def get_full_description(self, obj):
        metadata = _metadata(obj)
        return metadata.full_description if metadata else (obj.overview or "")

    def get_catalog_status(self, obj):
        metadata = _metadata(obj)
        return metadata.catalog_status if metadata else "draft"

    def get_course_overview(self, obj):
        metadata = _metadata(obj)
        return metadata.course_overview if metadata else (obj.overview or "")

    def get_syllabus(self, obj):
        metadata = _metadata(obj)
        return metadata.syllabus if metadata else ""

    def get_completion_requirements(self, obj):
        metadata = _metadata(obj)
        return metadata.completion_requirements if metadata else ""

    def get_learning_outcomes(self, obj):
        metadata = _metadata(obj)
        return metadata.learning_outcomes if metadata else []

    def get_references(self, obj):
        metadata = _metadata(obj)
        return metadata.references if metadata else []

    def get_duration_minutes(self, obj):
        metadata = _metadata(obj)
        return metadata.duration_minutes if metadata else None

    def get_price(self, obj):
        metadata = _metadata(obj)
        return str(metadata.price) if metadata else None

    def get_currency(self, obj):
        metadata = _metadata(obj)
        return metadata.currency if metadata else None

    def get_pacing(self, obj):
        metadata = _metadata(obj)
        return metadata.pacing if metadata else None

    def get_banner_image(self, obj):
        if obj.banner_image:
            return obj.banner_image.url
        return ""

    def get_card_image(self, obj):
        if obj.card_image:
            return obj.card_image.url
        return ""
