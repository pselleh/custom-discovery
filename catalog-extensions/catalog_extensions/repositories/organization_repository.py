from course_discovery.apps.course_metadata.models import Organization


class OrganizationRepository:

    def list(self, limit=100):
        return (
            Organization.objects
            .all()
            .order_by("name")[:limit]
        )

    def get(self, key):
        return (
            Organization.objects
            .filter(key=key)
            .first()
        )
