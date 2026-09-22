import copy
import json
from pathlib import Path

from django.test import SimpleTestCase

from catalog_extensions.management.commands.import_cba_catalog import Command


EXAMPLE_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "api"
    / "cba_catalog_import.example.json"
)


class CatalogImportValidationTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def test_example_catalog_is_valid(self):
        self.assertEqual(Command()._validate(copy.deepcopy(self.payload)), [])

    def test_program_accepts_multiple_instructors(self):
        payload = copy.deepcopy(self.payload)
        payload["people"].append(
            {
                "person_id": "faculty-002",
                "given_name": "Second",
                "family_name": "Instructor",
            }
        )
        payload["certificate_programs"][0]["program_faculty"].append(
            {
                "person_id": "faculty-002",
                "role": "instructor",
                "display_order": 3,
            }
        )
        self.assertEqual(Command()._validate(payload), [])

    def test_course_key_components_must_match(self):
        payload = copy.deepcopy(self.payload)
        payload["microcourses"][0]["course_run"] = "2028"
        errors = Command()._validate(payload)
        self.assertTrue(any("course_key must equal" in error for error in errors))

    def test_program_requires_syllabus_and_completion_requirements(self):
        payload = copy.deepcopy(self.payload)
        payload["certificate_programs"][0].pop("syllabus")
        payload["certificate_programs"][0].pop("completion_requirements")
        errors = Command()._validate(payload)
        self.assertTrue(any(".syllabus is required" in error for error in errors))
        self.assertTrue(any(".completion_requirements is required" in error for error in errors))

    def test_hidden_listing_requires_nonpublic_access_scope(self):
        payload = copy.deepcopy(self.payload)
        payload["microcourses"][0]["catalog_visibility"] = "hidden"
        errors = Command()._validate(payload)
        self.assertTrue(any("hidden listings cannot use" in error for error in errors))

    def test_organization_code_access_requires_policy_key(self):
        payload = copy.deepcopy(self.payload)
        course = payload["microcourses"][0]
        course["catalog_visibility"] = "hidden"
        course["access_scope"] = "organization_code"
        course["access_policy_key"] = ""
        errors = Command()._validate(payload)
        self.assertTrue(any("access_policy_key is required" in error for error in errors))

    def test_hidden_organization_code_course_is_valid(self):
        payload = copy.deepcopy(self.payload)
        course = payload["microcourses"][0]
        course["catalog_visibility"] = "hidden"
        course["access_scope"] = "organization_code"
        course["access_policy_key"] = "cba-restricted-risk-2027"
        self.assertEqual(Command()._validate(payload), [])

    def test_program_only_course_cannot_be_standalone(self):
        payload = copy.deepcopy(self.payload)
        course = payload["microcourses"][0]
        course["catalog_visibility"] = "hidden"
        course["access_scope"] = "program_only"
        course["standalone_enrollment_allowed"] = True
        errors = Command()._validate(payload)
        self.assertTrue(any("must be false for program_only" in error for error in errors))
