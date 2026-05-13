from rest_framework import serializers


class UnifiedCourseSerializer(serializers.Serializer):
    key = serializers.CharField()
    title = serializers.CharField()
    short_description = serializers.CharField(allow_blank=True, required=False)
    marketing_url = serializers.CharField(allow_blank=True, required=False)
