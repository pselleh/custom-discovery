from catalog_extensions.repositories.course_repository import CourseRepository


class CourseService:
    """Business logic for catalog courses."""

    def __init__(self):
        self.repository = CourseRepository()

    def list_courses(self, limit=100):
        return self.repository.list_courses(limit)

    def get_course(self, course_key):
        return self.repository.get_by_key(course_key)
