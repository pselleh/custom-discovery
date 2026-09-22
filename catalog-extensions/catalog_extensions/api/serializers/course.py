from django.core.exceptions import ObjectDoesNotExist
from opaque_keys.edx.keys import CourseKey
from rest_framework import serializers

from catalog_extensions.api.serializers.organization import OrganizationSerializer
from catalog_extensions.api.serializers.subject import SubjectSerializer


def _parse_course_key(value):
    try:
        key = CourseKey.from_string(str(value))
        return key.org, key.course, key.run
    except (TypeError, ValueError):
        return "", "", ""


def _catalog_metadata(course_run):
    if not course_run:
        return None
    try:
        return course_run.cba_catalog
    except ObjectDoesNotExist:
        return None


def _catalog_run(course):
    advertised = getattr(course, "advertised_course_run", None)
    if advertised:
        return advertised
    canonical = getattr(course, "canonical_course_run", None)
    if canonical:
        return canonical
    return next(iter(course.course_runs.all()), None)


def _seat(course_run):
    if not course_run:
        return None
    seats = list(course_run.seats.all())
    return seats[0] if seats else None


class FacultyAssignmentSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(source="person.uuid", read_only=True)
    name = serializers.CharField(source="person.full_name", read_only=True)
    role = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    credentials = serializers.CharField(read_only=True)
    bio = serializers.CharField(source="person.bio", read_only=True)
    profile_url = serializers.CharField(source="person.profile_url", read_only=True)
    profile_image_url = serializers.CharField(source="person.get_profile_image_url", read_only=True)
    display_order = serializers.IntegerField(read_only=True)


class SeatSerializer(serializers.Serializer):
    type = serializers.CharField(source="type.slug", read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    currency = serializers.CharField(source="currency.code", read_only=True)
    upgrade_deadline = serializers.DateTimeField(read_only=True)
    credit_provider = serializers.CharField(allow_blank=True, required=False, read_only=True)
    credit_hours = serializers.IntegerField(required=False, allow_null=True, read_only=True)
    sku = serializers.CharField(allow_blank=True, required=False, read_only=True)
    bulk_sku = serializers.CharField(allow_blank=True, required=False, read_only=True)
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)


class CourseRunSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    key = serializers.CharField(read_only=True)
    course_key = serializers.CharField(source="key", read_only=True)
    organization = serializers.SerializerMethodField()
    course_number = serializers.SerializerMethodField()
    course_run = serializers.SerializerMethodField()
    title = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    catalog_status = serializers.SerializerMethodField()
    catalog_visibility = serializers.SerializerMethodField()
    access_scope = serializers.SerializerMethodField()
    access_policy_key = serializers.SerializerMethodField()
    standalone_enrollment_allowed = serializers.SerializerMethodField()
    start = serializers.DateTimeField(read_only=True)
    end = serializers.DateTimeField(read_only=True)
    enrollment_start = serializers.DateTimeField(read_only=True)
    enrollment_end = serializers.DateTimeField(read_only=True)
    pacing_type = serializers.CharField(read_only=True)
    pacing = serializers.CharField(source="pacing_type", read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    weeks_to_complete = serializers.IntegerField(read_only=True)
    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    seats = SeatSerializer(many=True, read_only=True)
    learning_outcomes = serializers.SerializerMethodField()
    course_overview = serializers.SerializerMethodField()
    references = serializers.SerializerMethodField()
    faculty = FacultyAssignmentSerializer(source="cba_faculty_assignments", many=True, read_only=True)

    def get_organization(self, obj):
        return _parse_course_key(obj.key)[0]

    def get_course_number(self, obj):
        return _parse_course_key(obj.key)[1]

    def get_course_run(self, obj):
        return _parse_course_key(obj.key)[2]

    def get_catalog_status(self, obj):
        metadata = _catalog_metadata(obj)
        return metadata.catalog_status if metadata else "draft"

    def get_catalog_visibility(self, obj):
        metadata = _catalog_metadata(obj)
        return metadata.catalog_visibility if metadata else "hidden"

    def get_access_scope(self, obj):
        metadata = _catalog_metadata(obj)
        return metadata.access_scope if metadata else "program_only"

    def get_access_policy_key(self, obj):
        metadata = _catalog_metadata(obj)
        return metadata.access_policy_key if metadata else ""

    def get_standalone_enrollment_allowed(self, obj):
        metadata = _catalog_metadata(obj)
        return metadata.standalone_enrollment_allowed if metadata else False

    def get_duration_minutes(self, obj):
        metadata = _catalog_metadata(obj)
        return metadata.duration_minutes if metadata else None

    def get_price(self, obj):
        seat = _seat(obj)
        return str(seat.price) if seat and seat.price is not None else None

    def get_currency(self, obj):
        seat = _seat(obj)
        currency = getattr(seat, "currency", None) if seat else None
        return getattr(currency, "code", None)

    def get_learning_outcomes(self, obj):
        metadata = _catalog_metadata(obj)
        return metadata.learning_outcomes if metadata else []

    def get_course_overview(self, obj):
        metadata = _catalog_metadata(obj)
        return metadata.course_overview if metadata else ""

    def get_references(self, obj):
        metadata = _catalog_metadata(obj)
        return metadata.references if metadata else []


class CourseListSerializer(serializers.Serializer):
    key = serializers.CharField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    course_key = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    course_number = serializers.SerializerMethodField()
    course_run = serializers.SerializerMethodField()
    title = serializers.CharField(read_only=True)
    short_description = serializers.CharField(read_only=True)
    pacing = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    catalog_status = serializers.SerializerMethodField()
    catalog_visibility = serializers.SerializerMethodField()
    access_scope = serializers.SerializerMethodField()
    access_policy_key = serializers.SerializerMethodField()
    standalone_enrollment_allowed = serializers.SerializerMethodField()
    image_url = serializers.CharField(read_only=True)
    marketing_url = serializers.CharField(read_only=True)
    organizations = OrganizationSerializer(source="authoring_organizations", many=True, read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)

    def _run(self, obj):
        return _catalog_run(obj)

    def get_course_key(self, obj):
        run = self._run(obj)
        return run.key if run else ""

    def get_organization(self, obj):
        run = self._run(obj)
        return _parse_course_key(run.key)[0] if run else ""

    def get_course_number(self, obj):
        run = self._run(obj)
        return _parse_course_key(run.key)[1] if run else getattr(obj, "number", "")

    def get_course_run(self, obj):
        run = self._run(obj)
        return _parse_course_key(run.key)[2] if run else ""

    def get_pacing(self, obj):
        run = self._run(obj)
        return run.pacing_type if run else None

    def get_duration_minutes(self, obj):
        metadata = _catalog_metadata(self._run(obj))
        return metadata.duration_minutes if metadata else None

    def get_price(self, obj):
        seat = _seat(self._run(obj))
        return str(seat.price) if seat and seat.price is not None else None

    def get_currency(self, obj):
        seat = _seat(self._run(obj))
        currency = getattr(seat, "currency", None) if seat else None
        return getattr(currency, "code", None)

    def get_catalog_status(self, obj):
        metadata = _catalog_metadata(self._run(obj))
        return metadata.catalog_status if metadata else "draft"

    def get_catalog_visibility(self, obj):
        metadata = _catalog_metadata(self._run(obj))
        return metadata.catalog_visibility if metadata else "hidden"

    def get_access_scope(self, obj):
        metadata = _catalog_metadata(self._run(obj))
        return metadata.access_scope if metadata else "program_only"

    def get_access_policy_key(self, obj):
        metadata = _catalog_metadata(self._run(obj))
        return metadata.access_policy_key if metadata else ""

    def get_standalone_enrollment_allowed(self, obj):
        metadata = _catalog_metadata(self._run(obj))
        return metadata.standalone_enrollment_allowed if metadata else False


class CourseDetailSerializer(CourseListSerializer):
    full_description = serializers.CharField(read_only=True)
    learning_outcomes = serializers.SerializerMethodField()
    course_overview = serializers.SerializerMethodField()
    syllabus = serializers.CharField(source="syllabus_raw", read_only=True)
    references = serializers.SerializerMethodField()
    faculty = serializers.SerializerMethodField()
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    course_runs = CourseRunSerializer(many=True, read_only=True)

    def get_learning_outcomes(self, obj):
        metadata = _catalog_metadata(self._run(obj))
        return metadata.learning_outcomes if metadata else []

    def get_course_overview(self, obj):
        metadata = _catalog_metadata(self._run(obj))
        return metadata.course_overview if metadata else ""

    def get_references(self, obj):
        metadata = _catalog_metadata(self._run(obj))
        return metadata.references if metadata else []

    def get_faculty(self, obj):
        run = self._run(obj)
        if not run:
            return []
        return FacultyAssignmentSerializer(run.cba_faculty_assignments.all(), many=True).data
