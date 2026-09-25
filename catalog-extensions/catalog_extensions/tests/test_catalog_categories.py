import copy
import json
from pathlib import Path

from django.test import SimpleTestCase

from catalog_extensions.management.commands.import_cba_catalog import (
    Command,
)


EXAMPLE_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "api"
    / "cba_catalog_import.example.json"
)


class CatalogCategoryValidationTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payload = json.loads(
            EXAMPLE_PATH.read_text(encoding="utf-8")
        )

    def test_example_categories_are_valid(self):
        errors = Command()._validate(
            copy.deepcopy(self.payload)
        )

        self.assertEqual(errors, [])

    def test_primary_category_is_required(self):
        payload = copy.deepcopy(self.payload)
        course = payload["microcourses"][0]

        course.pop("primary_catalog_category")

        errors = Command()._validate(payload)

        self.assertTrue(
            any(
                "primary_catalog_category" in error
                and "required" in error
                for error in errors
            )
        )

    def test_category_list_is_required(self):
        payload = copy.deepcopy(self.payload)
        course = payload["microcourses"][0]

        course.pop("catalog_categories")

        errors = Command()._validate(payload)

        self.assertTrue(
            any(
                "catalog_categories" in error
                and "required" in error
                for error in errors
            )
        )

    def test_primary_category_must_be_in_category_list(
        self,
    ):
        payload = copy.deepcopy(self.payload)
        course = payload["microcourses"][0]

        course["primary_catalog_category"] = (
            "enterprise-risk-management"
        )
        course["catalog_categories"] = [
            "organizational-resilience"
        ]

        errors = Command()._validate(payload)

        self.assertTrue(
            any(
                "must also occur in catalog_categories"
                in error
                for error in errors
            )
        )

    def test_unknown_course_category_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        course = payload["microcourses"][0]

        course["primary_catalog_category"] = (
            "not-a-real-category"
        )
        course["catalog_categories"] = [
            "not-a-real-category"
        ]

        errors = Command()._validate(payload)

        self.assertTrue(
            any(
                "unknown values" in error
                for error in errors
            )
        )

    def test_duplicate_categories_are_rejected(self):
        payload = copy.deepcopy(self.payload)
        course = payload["microcourses"][0]

        category = course[
            "primary_catalog_category"
        ]
        course["catalog_categories"] = [
            category,
            category,
        ]

        errors = Command()._validate(payload)

        self.assertTrue(
            any(
                "must not contain duplicates" in error
                for error in errors
            )
        )

    def test_unknown_program_category_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        program = payload["certificate_programs"][0]

        program["primary_catalog_category"] = (
            "not-a-real-category"
        )
        program["catalog_categories"] = [
            "not-a-real-category"
        ]

        errors = Command()._validate(payload)

        self.assertTrue(
            any(
                "unknown values" in error
                for error in errors
            )
        )
