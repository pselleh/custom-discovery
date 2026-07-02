from catalog_extensions.repositories.course_repository import CourseRepository


class CourseService:
    """Service layer for Discovery Courses."""

    def __init__(self):
        self.repository = CourseRepository()

    def list_courses(self, filters=None, limit=100):
        return self.repository.list_courses(
            filters=filters,
            limit=limit,
        )

    def get_course(self, course_key):
        return self.repository.get_by_key(course_key)
