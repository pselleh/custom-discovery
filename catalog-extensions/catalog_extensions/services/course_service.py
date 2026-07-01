from catalog_extensions.repositories.course_repository import CourseRepository


class CourseService:
    def __init__(self):
        self.repository = CourseRepository()

    def list_courses(self, limit=100):
        return self.repository.list_courses(limit=limit)

    def get_course(self, course_key):
        return self.repository.get_by_key(course_key)

    def serialize_course(self, course):
        return {
            "key": str(course.key),
            "uuid": str(getattr(course, "uuid", "") or ""),
            "title": course.title or "",
            "short_description": course.short_description or "",
            "full_description": getattr(course, "full_description", "") or "",
            "marketing_url": course.marketing_url or "",
            "image_url": self.get_image_url(course),
            "course_runs": [
                {
                    "key": str(run.key),
                    "title": run.title or "",
                    "start": run.start,
                    "end": run.end,
                    "enrollment_start": run.enrollment_start,
                    "enrollment_end": run.enrollment_end,
                    "pacing_type": getattr(run, "pacing_type", "") or "",
                    "status": getattr(run, "status", "") or "",
                }
                for run in course.course_runs.all()
            ],
        }

    def get_image_url(self, course):
        for attr in ("card_image_url", "image_url"):
            value = getattr(course, attr, None)
            if value:
                return value
        image = getattr(course, "image", None)
        if image:
            return str(image)
        return ""
