"""Bulk-create or update CBA Studio course shells on Open edX Verawood.

Run this file through ``./manage.py cms shell``. Configuration is supplied by
environment variables so no credentials or server-specific paths are stored in
the repository.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db.models import Q
from opaque_keys.edx.keys import CourseKey

from cms.djangoapps.contentstore.views.course import create_new_course
from xmodule.modulestore.django import modulestore


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


catalog_path = Path(os.environ.get("CBA_CATALOG_FILE", "/tmp/cba_catalog.json"))
studio_user = os.environ.get("CBA_STUDIO_USER", "").strip()
validate_only = env_bool("CBA_VALIDATE_ONLY")
update_existing = env_bool("CBA_UPDATE_EXISTING")

errors = []
if not studio_user:
    errors.append("CBA_STUDIO_USER is required (username or email).")

try:
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    errors.append(f"Cannot read valid catalog JSON from {catalog_path}: {exc}")
    payload = {}

records = payload.get("microcourses", [])
if not isinstance(records, list) or not records:
    errors.append("The catalog must contain a non-empty microcourses array.")

seen = set()
for index, record in enumerate(records, start=1):
    prefix = f"microcourses[{index}]"
    for field in (
        "course_key", "organization", "course_number", "course_run", "title",
        "pacing", "catalog_status", "catalog_visibility", "access_scope",
    ):
        if not record.get(field):
            errors.append(f"{prefix}.{field} is required.")
    expected = (
        f"course-v1:{record.get('organization')}+"
        f"{record.get('course_number')}+{record.get('course_run')}"
    )
    if record.get("course_key") != expected:
        errors.append(f"{prefix}.course_key must equal {expected!r}.")
    if record.get("course_key") in seen:
        errors.append(f"{prefix}.course_key must be unique.")
    seen.add(record.get("course_key"))
    if record.get("pacing") != "self_paced":
        errors.append(f"{prefix}.pacing must be 'self_paced'.")
    if record.get("access_scope") == "organization_code" and not record.get("access_policy_key"):
        errors.append(f"{prefix}.access_policy_key is required for organization_code access.")

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)

User = get_user_model()
try:
    user = User.objects.get(Q(username=studio_user) | Q(email=studio_user))
except User.DoesNotExist as exc:
    raise SystemExit(f"ERROR: Studio user {studio_user!r} was not found.") from exc
except User.MultipleObjectsReturned as exc:
    raise SystemExit(
        f"ERROR: Studio user {studio_user!r} matched more than one account; use the exact username."
    ) from exc

store = modulestore()
summary = {
    "validated": len(records),
    "would_create": [],
    "would_update": [],
    "created": [],
    "updated": [],
    "existing": [],
    "errors": [],
}

for record in records:
    key = CourseKey.from_string(record["course_key"])
    fields = {
        "display_name": record["title"],
        "self_paced": True,
        # CBA's public catalog is Wagtail, so never expose these shells in the LMS catalog/about page.
        "catalog_visibility": "none",
        # Prevent direct enrollment while waitlisted and for every restricted product.
        "invitation_only": (
            record["catalog_status"] != "enrollment_open"
            or record["access_scope"] != "public"
        ),
        "start": datetime(int(record["course_run"]), 1, 1, tzinfo=timezone.utc),
    }
    try:
        exists = store.has_course(key, ignore_case=True)
        if validate_only:
            if exists:
                summary["would_update" if update_existing else "existing"].append(str(key))
            else:
                summary["would_create"].append(str(key))
            continue
        if exists:
            if not update_existing:
                summary["existing"].append(str(key))
                continue
            course = store.get_course(key)
            for field, value in fields.items():
                setattr(course, field, value)
            store.update_item(course, user.id)
            summary["updated"].append(str(key))
            continue
        create_new_course(
            user,
            record["organization"],
            record["course_number"],
            record["course_run"],
            fields,
        )
        summary["created"].append(str(key))
    except Exception as exc:  # noqa: BLE001 - report every failed row before exiting
        summary["errors"].append({"course_key": str(key), "error": str(exc)})

print(json.dumps(summary, indent=2, sort_keys=True))
if summary["errors"]:
    raise SystemExit(1)
