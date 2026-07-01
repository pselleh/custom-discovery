from rest_framework import serializers


class OrganizationSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()

    key = serializers.CharField()

    name = serializers.CharField()

    certificate_name = serializers.CharField(
        allow_blank=True,
        required=False,
    )

    slug = serializers.CharField()

    description = serializers.CharField(
        allow_blank=True,
        required=False,
    )

    homepage_url = serializers.CharField(
        allow_blank=True,
        required=False,
    )

    marketing_url = serializers.SerializerMethodField()

    logo_image = serializers.SerializerMethodField()

    banner_image = serializers.SerializerMethodField()

    organization_hex_color = serializers.CharField(
        allow_blank=True,
        required=False,
    )

    created = serializers.DateTimeField()

    modified = serializers.DateTimeField()

    def get_marketing_url(self, obj):
        return obj.marketing_url or ""

    def get_logo_image(self, obj):
        if obj.logo_image:
            return obj.logo_image.url
        return ""

    def get_banner_image(self, obj):
        if obj.banner_image:
            return obj.banner_image.url
        return ""
