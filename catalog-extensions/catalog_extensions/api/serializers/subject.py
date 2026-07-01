from rest_framework import serializers


class SubjectSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()

    name = serializers.CharField()

    slug = serializers.CharField()

    banner_image_url = serializers.CharField(
        allow_blank=True,
        required=False,
    )

    card_image_url = serializers.CharField(
        allow_blank=True,
        required=False,
    )

    created = serializers.DateTimeField()

    modified = serializers.DateTimeField()
