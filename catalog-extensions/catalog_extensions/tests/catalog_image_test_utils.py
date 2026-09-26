from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image


def prepare_catalog_images(test_case, command, payload):
    test_case.image_temp_directory = TemporaryDirectory()
    base_dir = Path(test_case.image_temp_directory.name)

    command.catalog_base_dir = base_dir

    image_paths = []

    for course in payload.get("microcourses", []):
        image_paths.append(course["course_image"])

    for program in payload.get("certificate_programs", []):
        image_paths.extend(
            [
                program["card_image"],
                program["banner_image"],
            ]
        )

    for relative_path in image_paths:
        image_path = base_dir / relative_path
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
            format="JPEG",
            quality=90,
        )

    return base_dir


def remove_catalog_images(test_case):
    test_case.image_temp_directory.cleanup()
