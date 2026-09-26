"""Bulk-create or update CBA Studio course shells on Open edX Verawood.

Run this file through ``python manage.py cms shell``. Configuration is supplied
by environment variables so credentials and server-specific paths are not
stored in the repository.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db.models import Q
from opaque_keys.edx.keys import CourseKey
from PIL import Image, UnidentifiedImageError

from cms.djangoapps.contentstore.views.course import create_new_course
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore
from xmodule.modulestore.django import modulestore


NATIVE_COURSE_IMAGE = "images_course_image.jpg"


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def package_path(base_directory, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("must be a nonempty package-relative path")

    relative_path = Path(value)

    if relative_path.is_absolute():
        raise ValueError("must be package-relative")

    resolved_path = (base_directory / relative_path).resolve()

    try:
        resolved_path.relative_to(base_directory)
    except ValueError as exc:
        raise ValueError(
            "must remain inside the catalog package"
        ) from exc

    return resolved_path


def validate_course_image(base_directory, value):
    image_path = package_path(base_directory, value)

    if image_path.name != NATIVE_COURSE_IMAGE:
        raise ValueError(
            "must use the native filename "
            f"{NATIVE_COURSE_IMAGE!r}"
        )

    if not image_path.is_file():
        raise ValueError(
            f"does not exist or is not a regular file: {value!r}"
        )

    try:
        with Image.open(image_path) as image:
            detected_format = image.format
            image.verify()
    except (
        OSError,
        UnidentifiedImageError,
    ) as exc:
        raise ValueError(
            f"is not a valid image: {value!r}"
        ) from exc

    if detected_format != "JPEG":
        raise ValueError(
            "must contain a JPEG image; "
            f"detected {detected_format!r}"
        )

    return image_path


def save_course_image(course, image_path):
    asset_key = StaticContent.compute_location(
        course.id,
        NATIVE_COURSE_IMAGE,
    )

    with image_path.open("rb") as source_file:
        content = StaticContent(
            asset_key,
            NATIVE_COURSE_IMAGE,
            "image/jpeg",
            source_file,
        )
        contentstore().save(content)


catalog_path = Path(
    os.environ.get(
        "CBA_CATALOG_FILE",
        "/tmp/cba_catalog.json",
    )
)
catalog_base_directory = catalog_path.resolve().parent
studio_user = os.environ.get(
    "CBA_STUDIO_USER",
    "",
).strip()
validate_only = env_bool("CBA_VALIDATE_ONLY")
update_existing = env_bool("CBA_UPDATE_EXISTING")

errors = []

if not studio_user:
    errors.append(
        "CBA_STUDIO_USER is required (username or email)."
    )

try:
    payload = json.loads(
        catalog_path.read_text(encoding="utf-8")
    )
except (OSError, json.JSONDecodeError) as exc:
    errors.append(
        "Cannot read valid catalog JSON from "
        f"{catalog_path}: {exc}"
    )
    payload = {}

records = payload.get("microcourses", [])

if not isinstance(records, list) or not records:
    errors.append(
        "The catalog must contain a non-empty "
        "microcourses array."
    )
    records = []

seen = set()
validated_image_paths = {}

for index, record in enumerate(records, start=1):
    prefix = f"microcourses[{index}]"

    if not isinstance(record, dict):
        errors.append(f"{prefix} must be an object.")
        continue

    for field in (
        "course_key",
        "organization",
        "course_number",
        "course_run",
        "title",
        "pacing",
        "catalog_status",
        "catalog_visibility",
        "access_scope",
        "course_image",
        "image_alt",
    ):
        if not record.get(field):
            errors.append(f"{prefix}.{field} is required.")

    expected = (
        f"course-v1:{record.get('organization')}+"
        f"{record.get('course_number')}+"
        f"{record.get('course_run')}"
    )

    if record.get("course_key") != expected:
        errors.append(
            f"{prefix}.course_key must equal {expected!r}."
        )

    if record.get("course_key") in seen:
        errors.append(
            f"{prefix}.course_key must be unique."
        )

    seen.add(record.get("course_key"))

    if record.get("pacing") != "self_paced":
        errors.append(
            f"{prefix}.pacing must be 'self_paced'."
        )

    if (
        record.get("access_scope") == "organization_code"
        and not record.get("access_policy_key")
    ):
        errors.append(
            f"{prefix}.access_policy_key is required "
            "for organization_code access."
        )

    image_alt = record.get("image_alt")

    if (
        isinstance(image_alt, str)
        and len(image_alt.strip()) > 255
    ):
        errors.append(
            f"{prefix}.image_alt cannot exceed "
            "255 characters."
        )

    if record.get("course_image"):
        try:
            validated_image_paths[
                record.get("course_key")
            ] = validate_course_image(
                catalog_base_directory,
                record["course_image"],
            )
        except ValueError as exc:
            errors.append(
                f"{prefix}.course_image {exc}."
            )

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)

User = get_user_model()

try:
    user = User.objects.get(
        Q(username=studio_user) |
        Q(email=studio_user)
    )
except User.DoesNotExist as exc:
    raise SystemExit(
        f"ERROR: Studio user {studio_user!r} "
        "was not found."
    ) from exc
except User.MultipleObjectsReturned as exc:
    raise SystemExit(
        f"ERROR: Studio user {studio_user!r} matched "
        "more than one account; use the exact username."
    ) from exc

store = modulestore()

summary = {
    "validated": len(records),
    "validated_images": len(validated_image_paths),
    "would_create": [],
    "would_update": [],
    "would_upload_images": [],
    "created": [],
    "updated": [],
    "uploaded_images": [],
    "existing": [],
    "errors": [],
}

for record in records:
    key = CourseKey.from_string(record["course_key"])
    image_path = validated_image_paths[record["course_key"]]

    fields = {
        "display_name": record["title"],
        "self_paced": True,
        "course_image": NATIVE_COURSE_IMAGE,
        # Wagtail is the public catalog. Do not expose these
        # shells in the LMS catalog or course-about page.
        "catalog_visibility": "none",
        # Prevent direct enrollment while waitlisted and for
        # every restricted product.
        "invitation_only": (
            record["catalog_status"] != "enrollment_open"
            or record["access_scope"] != "public"
        ),
        "start": datetime(
            int(record["course_run"]),
            1,
            1,
            tzinfo=timezone.utc,
        ),
    }

    try:
        exists = store.has_course(
            key,
            ignore_case=True,
        )

        if validate_only:
            if exists:
                destination = (
                    "would_update"
                    if update_existing
                    else "existing"
                )
                summary[destination].append(str(key))

                if update_existing:
                    summary[
                        "would_upload_images"
                    ].append(str(key))
            else:
                summary["would_create"].append(str(key))
                summary[
                    "would_upload_images"
                ].append(str(key))

            continue

        if exists:
            if not update_existing:
                summary["existing"].append(str(key))
                continue

            course = store.get_course(key)

            for field, value in fields.items():
                setattr(course, field, value)

            store.update_item(course, user.id)
            save_course_image(course, image_path)

            summary["updated"].append(str(key))
            summary["uploaded_images"].append(str(key))
            continue

        create_new_course(
            user,
            record["organization"],
            record["course_number"],
            record["course_run"],
            fields,
        )

        course = store.get_course(key)
        save_course_image(course, image_path)

        summary["created"].append(str(key))
        summary["uploaded_images"].append(str(key))

    except Exception as exc:  # noqa: BLE001
        summary["errors"].append(
            {
                "course_key": str(key),
                "error": str(exc),
            }
        )

print(
    json.dumps(
        summary,
        indent=2,
        sort_keys=True,
    )
)

if summary["errors"]:
    raise SystemExit(1)
