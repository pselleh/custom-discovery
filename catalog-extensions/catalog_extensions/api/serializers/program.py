from rest_framework import serializers

from catalog_extensions.api.serializers.course import CourseListSerializer
from catalog_extensions.api.serializers.organization import OrganizationSerializer
from catalog_extensions.api.serializers.subject import SubjectSerializer


class ProgramSerializer(serializers.Serializer):

    uuid = serializers.UUIDField()

    title = serializers.CharField()

    subtitle = serializers.CharField()

    marketing_slug = serializers.CharField()

    status = serializers.CharField()

    overview = serializers.CharField()

    marketing_url = serializers.CharField()

    banner_image = serializers.SerializerMethodField()

    card_image = serializers.SerializerMethodField()

    organizations = OrganizationSerializer(
        source="authoring_organizations",
        many=True,
    )

    subjects = SubjectSerializer(
        many=True,
    )

    courses = CourseListSerializer(
        many=True,
    )

    created = serializers.DateTimeField()

    modified = serializers.DateTimeField()

    def get_banner_image(self, obj):
        if obj.banner_image:
            return obj.banner_image.url
        return ""

    def get_card_image(self, obj):
        if obj.card_image:
            return obj.card_image.url
        return ""
