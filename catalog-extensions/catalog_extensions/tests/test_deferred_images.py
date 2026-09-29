import copy
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from catalog_extensions.management.commands.import_cba_catalog import Command


MODULE = "catalog_extensions.management.commands.import_cba_catalog"


class DeferredImagesTests(SimpleTestCase):
    def setUp(self):
        self.command = Command()
        self.command.defer_images = True
        example = Path(__file__).resolve().parents[2] / "docs/api/cba_catalog_import.example.json"
        self.payload = json.loads(example.read_text())
        for record in self.payload["microcourses"]:
            record.pop("course_image", None)
            record.pop("image_alt", None)
        for record in self.payload["certificate_programs"]:
            for field in ("card_image", "banner_image", "image_alt"):
                record.pop(field, None)

    def test_metadata_without_images_is_valid_only_when_deferred(self):
        self.assertEqual(self.command._validate(self.payload), [])
        self.command.defer_images = False
        errors = self.command._validate(self.payload)
        self.assertTrue(any("course_image is required" in e for e in errors))
        self.assertTrue(any("card_image is required" in e for e in errors))

    def test_defer_does_not_relax_program_requirements(self):
        payload = copy.deepcopy(self.payload)
        payload["certificate_programs"][0].pop("completion_requirements")
        errors = self.command._validate(payload)
        self.assertTrue(any("completion_requirements is required" in e for e in errors))

    def test_course_update_preserves_alt_text(self):
        record = self.payload["microcourses"][0]
        with patch(f"{MODULE}.CourseRun") as runs, patch(f"{MODULE}.MicrocourseCatalogMetadata") as metadata:
            metadata.objects.update_or_create.return_value = (MagicMock(), False)
            self.command._upsert_seat = MagicMock()
            self.command._replace_course_faculty = MagicMock()
            self.command._import_microcourses([record], {}, {
                key: MagicMock() for key in record["catalog_categories"]
            })
            defaults = metadata.objects.update_or_create.call_args.kwargs["defaults"]
            self.assertNotIn("image_alt", defaults)

    def test_program_update_preserves_native_images_and_alt(self):
        record = self.payload["certificate_programs"][0]
        with patch(f"{MODULE}.CertificateProgramCatalogMetadata") as metadata, patch(f"{MODULE}.Organization"), patch(f"{MODULE}.ProgramCourseRequirement"):
            metadata.objects.update_or_create.return_value = (MagicMock(), False)
            self.command._save_program_image = MagicMock()
            self.command._replace_program_faculty = MagicMock()
            self.command._import_programs([record], MagicMock(), {}, {
                item["course_key"]: MagicMock() for item in record["microcourses"]
            }, {key: MagicMock() for key in record["catalog_categories"]})
            self.command._save_program_image.assert_not_called()
            defaults = metadata.objects.update_or_create.call_args.kwargs["defaults"]
            self.assertNotIn("image_alt", defaults)
