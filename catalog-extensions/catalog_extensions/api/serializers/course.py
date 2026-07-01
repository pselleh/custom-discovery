from rest_framework import serializers


class CourseRunSerializer(serializers.Serializer):
    key = serializers.CharField()
    title = serializers.CharField(allow_blank=True, required=False)
    start = serializers.DateTimeField(required=False, allow_null=True)
    end = serializers.DateTimeField(required=False, allow_null=True)
    enrollment_start = serializers.DateTimeField(required=False, allow_null=True)
    enrollment_end = serializers.DateTimeField(required=False, allow_null=True)
    pacing_type = serializers.CharField(allow_blank=True, required=False)
    status = serializers.CharField(allow_blank=True, required=False)


class CourseListSerializer(serializers.Serializer):
    key = serializers.CharField()
    uuid = serializers.CharField(allow_blank=True, required=False)
    title = serializers.CharField()
    short_description = serializers.CharField(allow_blank=True, required=False)
    full_description = serializers.CharField(allow_blank=True, required=False)
    marketing_url = serializers.CharField(allow_blank=True, required=False)
    image_url = serializers.CharField(allow_blank=True, required=False)
    course_runs = CourseRunSerializer(many=True, required=False)


class CourseDetailSerializer(CourseListSerializer):
    pass
