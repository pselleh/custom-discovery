from rest_framework import serializers

from catalog_extensions.api.serializers.organization import OrganizationSerializer
from catalog_extensions.api.serializers.subject import SubjectSerializer

class SeatSerializer(serializers.Serializer):

    type = serializers.CharField(
        source="type.slug",
        read_only=True,
    )

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    currency = serializers.CharField(
        source="currency.code",
        read_only=True,
    )

    upgrade_deadline = serializers.DateTimeField(
        read_only=True,
    )

    credit_provider = serializers.CharField(
        allow_blank=True,
        required=False,
        read_only=True,
    )

    credit_hours = serializers.IntegerField(
        required=False,
        allow_null=True,
        read_only=True,
    )

    sku = serializers.CharField(
        allow_blank=True,
        required=False,
        read_only=True,
    )

    bulk_sku = serializers.CharField(
        allow_blank=True,
        required=False,
        read_only=True,
    )

    created = serializers.DateTimeField(
        read_only=True,
    )

    modified = serializers.DateTimeField(
        read_only=True,
    )


class CourseRunSerializer(serializers.Serializer):

    uuid = serializers.UUIDField(
        read_only=True,
    )

    key = serializers.CharField(
        read_only=True,
    )

    title = serializers.CharField(
        read_only=True,
    )

    status = serializers.CharField(
        read_only=True,
    )

    start = serializers.DateTimeField(
        read_only=True,
    )

    end = serializers.DateTimeField(
        read_only=True,
    )

    enrollment_start = serializers.DateTimeField(
        read_only=True,
    )

    enrollment_end = serializers.DateTimeField(
        read_only=True,
    )

    pacing_type = serializers.CharField(
        read_only=True,
    )

    weeks_to_complete = serializers.IntegerField(
        read_only=True,
    )

    seats = SeatSerializer(
        many=True,
        read_only=True,
)

class CourseListSerializer(serializers.Serializer):
    key = serializers.CharField()

    uuid = serializers.UUIDField()

    title = serializers.CharField()

    short_description = serializers.CharField()

    image_url = serializers.CharField(
    read_only=True,
)

    marketing_url = serializers.CharField()

    organizations = OrganizationSerializer(
        source="authoring_organizations",
        many=True,
    )

    subjects = SubjectSerializer(
        many=True,
    )


class CourseDetailSerializer(CourseListSerializer):

    full_description = serializers.CharField()

    created = serializers.DateTimeField()

    modified = serializers.DateTimeField()

    course_runs = CourseRunSerializer(
        many=True,
    )
