from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from PIL import Image

from catalog_extensions.management.commands.import_cba_catalog import (
    Command,
)


class CatalogImageValidationTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.temp_directory = TemporaryDirectory()
        self.base_dir = Path(self.temp_directory.name)
        self.command = Command()
        self.command.catalog_base_dir = self.base_dir

    def tearDown(self):
        self.temp_directory.cleanup()
        super().tearDown()

    def create_image(
        self,
        relative_path,
        image_format="JPEG",
    ):
        image_path = self.base_dir / relative_path
        image_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image = Image.new(
            "RGB",
            (1600, 900),
            color=(20, 72, 112),
        )
        image.save(
            image_path,
            format=image_format,
            quality=90,
        )

        return image_path

    def test_valid_native_course_image_is_accepted(self):
        relative_path = (
            "images/microcourses/RMP103/"
            "images_course_image.jpg"
        )
        self.create_image(relative_path)

        errors = []

        self.command._validate_image(
            "microcourses[1]",
            "course_image",
            relative_path,
            errors,
            required_filename="images_course_image.jpg",
            allowed_formats={"JPEG"},
        )

        self.assertEqual(errors, [])

    def test_course_image_requires_native_filename(self):
        relative_path = (
            "images/microcourses/RMP103/RMP103.jpg"
        )
        self.create_image(relative_path)

        errors = []

        self.command._validate_image(
            "microcourses[1]",
            "course_image",
            relative_path,
            errors,
            required_filename="images_course_image.jpg",
            allowed_formats={"JPEG"},
        )

        self.assertTrue(
            any(
                "must use the native filename" in error
                for error in errors
            )
        )

    def test_path_traversal_is_rejected(self):
        errors = []

        self.command._validate_image(
            "microcourses[1]",
            "course_image",
            "../outside/images_course_image.jpg",
            errors,
            required_filename="images_course_image.jpg",
            allowed_formats={"JPEG"},
        )

        self.assertTrue(
            any(
                "must remain inside the catalog package"
                in error
                for error in errors
            )
        )

    def test_absolute_path_is_rejected(self):
        errors = []

        self.command._validate_image(
            "certificate_programs[1]",
            "card_image",
            "/tmp/card_image.jpg",
            errors,
            allowed_formats={"JPEG"},
        )

        self.assertTrue(
            any(
                "must be package-relative" in error
                for error in errors
            )
        )

    def test_missing_image_is_rejected(self):
        errors = []

        self.command._validate_image(
            "certificate_programs[1]",
            "banner_image",
            "images/programs/RMP/banner_image.jpg",
            errors,
            allowed_formats={"JPEG"},
        )

        self.assertTrue(
            any(
                "does not exist" in error
                for error in errors
            )
        )

    def test_invalid_image_content_is_rejected(self):
        relative_path = (
            "images/programs/RMP/card_image.jpg"
        )
        image_path = self.base_dir / relative_path
        image_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        image_path.write_bytes(b"not an image")

        errors = []

        self.command._validate_image(
            "certificate_programs[1]",
            "card_image",
            relative_path,
            errors,
            allowed_formats={"JPEG"},
        )

        self.assertTrue(
            any(
                "is not a valid image" in error
                for error in errors
            )
        )

    def test_wrong_image_format_is_rejected(self):
        relative_path = (
            "images/microcourses/RMP103/"
            "images_course_image.jpg"
        )
        self.create_image(
            relative_path,
            image_format="PNG",
        )

        errors = []

        self.command._validate_image(
            "microcourses[1]",
            "course_image",
            relative_path,
            errors,
            required_filename="images_course_image.jpg",
            allowed_formats={"JPEG"},
        )

        self.assertTrue(
            any(
                "detected 'PNG'" in error
                for error in errors
            )
        )

    def test_program_image_is_passed_to_native_field(self):
        relative_path = (
            "images/programs/RMP/card_image.jpg"
        )
        expected_path = self.create_image(relative_path)

        captured = {}

        def capture_save(name, django_file, save):
            captured["name"] = name
            captured["content"] = django_file.read()
            captured["save"] = save

        native_field = MagicMock()
        native_field.save.side_effect = capture_save

        program = SimpleNamespace(
            card_image=native_field,
        )

        self.command._save_program_image(
            program,
            "card_image",
            relative_path,
        )

        self.assertEqual(
            captured["name"],
            "card_image.jpg",
        )
        self.assertEqual(
            captured["content"],
            expected_path.read_bytes(),
        )
        self.assertFalse(captured["save"])
        native_field.save.assert_called_once()

    @patch(
        "catalog_extensions.management.commands."
        "import_cba_catalog.transaction.on_commit"
    )
    def test_first_program_image_does_not_schedule_deletion(
        self,
        on_commit,
    ):
        relative_path = (
            "images/programs/RMP/card_image.jpg"
        )
        self.create_image(relative_path)

        native_field = MagicMock()
        native_field.name = ""
        native_field.storage = MagicMock()

        def save_image(name, django_file, save):
            native_field.name = (
                "programs/catalog/card_image.jpg"
            )

        native_field.save.side_effect = save_image

        program = SimpleNamespace(
            card_image=native_field,
        )

        self.command._save_program_image(
            program,
            "card_image",
            relative_path,
        )

        on_commit.assert_not_called()
        native_field.storage.delete.assert_not_called()

    @patch(
        "catalog_extensions.management.commands."
        "import_cba_catalog.transaction.on_commit"
    )
    def test_replaced_program_image_is_deleted_after_commit(
        self,
        on_commit,
    ):
        relative_path = (
            "images/programs/RMP/card_image.jpg"
        )
        self.create_image(relative_path)

        storage = MagicMock()
        native_field = MagicMock()
        native_field.name = (
            "programs/catalog/old-card-image.jpg"
        )
        native_field.storage = storage

        def save_image(name, django_file, save):
            native_field.name = (
                "programs/catalog/new-card-image.jpg"
            )

        native_field.save.side_effect = save_image

        program = SimpleNamespace(
            card_image=native_field,
        )

        self.command._save_program_image(
            program,
            "card_image",
            relative_path,
        )

        storage.delete.assert_not_called()
        on_commit.assert_called_once()

        cleanup = on_commit.call_args.args[0]
        cleanup()

        storage.delete.assert_called_once_with(
            "programs/catalog/old-card-image.jpg"
        )

    @patch(
        "catalog_extensions.management.commands."
        "import_cba_catalog.transaction.on_commit"
    )
    def test_unchanged_program_image_name_is_not_deleted(
        self,
        on_commit,
    ):
        relative_path = (
            "images/programs/RMP/banner_image.jpg"
        )
        self.create_image(relative_path)

        storage = MagicMock()
        native_field = MagicMock()
        native_field.name = (
            "programs/catalog/banner_image.jpg"
        )
        native_field.storage = storage

        program = SimpleNamespace(
            banner_image=native_field,
        )

        self.command._save_program_image(
            program,
            "banner_image",
            relative_path,
        )

        on_commit.assert_not_called()
        storage.delete.assert_not_called()
