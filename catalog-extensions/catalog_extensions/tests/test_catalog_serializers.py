from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import PropertyMock
from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist
from django.test import SimpleTestCase

from catalog_extensions.api.serializers.course import (
    CourseListSerializer,
    CourseRunSerializer,
)
from catalog_extensions.api.serializers.program import (
    ProgramSerializer,
)


class RelatedCollection:
    def __init__(self, *items):
        self.items = list(items)

    def all(self):
        return self.items

    def __iter__(self):
        return iter(self.items)


def category(key, active=True):
    return SimpleNamespace(
        key=key,
        is_active=active,
    )


def course_metadata(primary, *categories):
    return SimpleNamespace(
        primary_catalog_category=primary,
        catalog_categories=RelatedCollection(*categories),
        catalog_status="waitlist_open",
        catalog_visibility="public",
        access_scope="public",
        access_policy_key="",
        standalone_enrollment_allowed=True,
        duration_minutes=60,
        learning_outcomes=[],
        course_overview="",
        references=[],
    )


def course_run(metadata):
    return SimpleNamespace(
        uuid=uuid4(),
        key="course-v1:CBA+ORF101M01C01+2027",
        title="Know When Risk Becomes a Disruption",
        status="published",
        cba_catalog=metadata,
        start=None,
        end=None,
        enrollment_start=None,
        enrollment_end=None,
        pacing_type="self_paced",
        weeks_to_complete=1,
        seats=RelatedCollection(),
        cba_faculty_assignments=RelatedCollection(),
    )


def course(run):
    return SimpleNamespace(
        key="CBA+ORF101M01C01",
        uuid=uuid4(),
        number="ORF101M01C01",
        title="Know When Risk Becomes a Disruption",
        short_description="Short description",
        advertised_course_run=run,
        canonical_course_run=None,
        course_runs=RelatedCollection(run),
        image_url="",
        marketing_url="",
        authoring_organizations=RelatedCollection(),
        subjects=RelatedCollection(),
    )


def program_metadata(primary, *categories):
    return SimpleNamespace(
        primary_catalog_category=primary,
        catalog_categories=RelatedCollection(*categories),
        program_code="ORF",
        short_description="Short description",
        full_description="Full description",
        catalog_status="waitlist_open",
        catalog_visibility="public",
        access_scope="public",
        access_policy_key="",
        course_overview="Overview",
        syllabus="Syllabus",
        completion_requirements="Requirements",
        learning_outcomes=[],
        references=[],
        duration_minutes=600,
        price=Decimal("590.00"),
        currency="USD",
        pacing="self_paced",
    )


def program(metadata):
    return SimpleNamespace(
        uuid=uuid4(),
        title="Organizational Resilience Foundations",
        subtitle="Foundation certificate",
        marketing_slug="organizational-resilience-foundations",
        status="active",
        overview="Overview",
        marketing_url="",
        banner_image=None,
        card_image=None,
        cba_catalog=metadata,
        authoring_organizations=RelatedCollection(),
        subjects=RelatedCollection(),
        courses=RelatedCollection(),
        cba_course_requirements=RelatedCollection(),
        cba_faculty_assignments=RelatedCollection(),
    )


class MissingCatalogMetadata:
    cba_catalog = PropertyMock(
        side_effect=ObjectDoesNotExist,
    )


class CatalogCategorySerializerTests(SimpleTestCase):
    def setUp(self):
        self.primary = category(
            "organizational-resilience"
        )
        self.secondary = category(
            "business-continuity-and-crisis-management"
        )

    def test_course_run_response_contains_categories(self):
        metadata = course_metadata(
            self.primary,
            self.primary,
            self.secondary,
        )

        data = CourseRunSerializer(
            course_run(metadata)
        ).data

        self.assertEqual(
            data["primary_catalog_category"],
            "organizational-resilience",
        )
        self.assertEqual(
            data["catalog_categories"],
            [
                "organizational-resilience",
                "business-continuity-and-crisis-management",
            ],
        )

    def test_course_list_response_contains_categories(self):
        metadata = course_metadata(
            self.primary,
            self.primary,
            self.secondary,
        )
        run = course_run(metadata)

        data = CourseListSerializer(
            course(run)
        ).data

        self.assertEqual(
            data["primary_catalog_category"],
            "organizational-resilience",
        )
        self.assertEqual(
            data["catalog_categories"],
            [
                "organizational-resilience",
                "business-continuity-and-crisis-management",
            ],
        )

    def test_program_response_contains_categories(self):
        metadata = program_metadata(
            self.primary,
            self.primary,
            self.secondary,
        )

        data = ProgramSerializer(
            program(metadata)
        ).data

        self.assertEqual(
            data["primary_catalog_category"],
            "organizational-resilience",
        )
        self.assertEqual(
            data["catalog_categories"],
            [
                "organizational-resilience",
                "business-continuity-and-crisis-management",
            ],
        )

    def test_inactive_categories_are_suppressed(self):
        inactive = category(
            "enterprise-risk-management",
            active=False,
        )
        metadata = course_metadata(
            inactive,
            self.primary,
            inactive,
        )

        data = CourseRunSerializer(
            course_run(metadata)
        ).data

        self.assertEqual(
            data["primary_catalog_category"],
            "",
        )
        self.assertEqual(
            data["catalog_categories"],
            ["organizational-resilience"],
        )

    def test_missing_metadata_has_empty_category_values(self):
        missing = MissingCatalogMetadata()

        course_serializer = CourseRunSerializer()
        program_serializer = ProgramSerializer()

        self.assertEqual(
            course_serializer.get_primary_catalog_category(
                missing
            ),
            "",
        )
        self.assertEqual(
            course_serializer.get_catalog_categories(
                missing
            ),
            [],
        )
        self.assertEqual(
            program_serializer.get_primary_catalog_category(
                missing
            ),
            "",
        )
        self.assertEqual(
            program_serializer.get_catalog_categories(
                missing
            ),
            [],
        )
