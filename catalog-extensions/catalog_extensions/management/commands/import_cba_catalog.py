import json
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from course_discovery.apps.core.models import Currency, Partner
from course_discovery.apps.course_metadata.models import (
    CourseRun,
    Organization,
    Person,
    Program,
    ProgramType,
    Seat,
    SeatType,
)

from catalog_extensions.models.category import CatalogCategory
from catalog_extensions.models.course import (
    AccessScope,
    CatalogStatus,
    CatalogVisibility,
    CourseRunFacultyAssignment,
    FacultyRole,
    MicrocourseCatalogMetadata,
)
from catalog_extensions.models.program import (
    CertificateProgramCatalogMetadata,
    ProgramCourseRequirement,
    ProgramFacultyAssignment,
)


VALID_STATUSES = {value for value, _label in CatalogStatus.choices}
VALID_VISIBILITIES = {value for value, _label in CatalogVisibility.choices}
VALID_ACCESS_SCOPES = {value for value, _label in AccessScope.choices}
VALID_ROLES = {value for value, _label in FacultyRole.choices}

VALID_CATALOG_CATEGORIES = {
    "organizational-resilience",
    "enterprise-risk-management",
    "risk-analysis-and-assessment",
    "risk-intelligence-and-emerging-risk",
    "business-continuity-and-crisis-management",
    "leadership-governance-and-oversight",
    "audit-assurance-and-forensics",
    "sector-specific-enterprise-risk-management",
    "strategic-environmental-and-threat-analysis",
    "quality-and-integrated-management-systems",
}


class Command(BaseCommand):
    help = "Validate or import CBA microcourse and certificate-program catalog JSON."

    def add_arguments(self, parser):
        parser.add_argument("catalog_file", type=Path)
        parser.add_argument("--partner", required=True, help="Discovery Partner.short_code")
        parser.add_argument("--validate-only", action="store_true")

    def handle(self, *args, **options):
        path = options["catalog_file"]
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f"Cannot read valid JSON from {path}: {exc}") from exc

        errors = self._validate(payload)
        if errors:
            raise CommandError("Catalog validation failed:\n- " + "\n- ".join(errors))

        if options["validate_only"]:
            self.stdout.write(self.style.SUCCESS("Catalog JSON is valid."))
            return

        try:
            partner = Partner.objects.get(short_code=options["partner"])
        except Partner.DoesNotExist as exc:
            raise CommandError(f"Discovery partner {options['partner']!r} does not exist.") from exc

        requested_category_keys = set()

        for section in (
            "microcourses",
            "certificate_programs",
        ):
            for record in payload.get(section, []):
                requested_category_keys.update(
                    record["catalog_categories"]
                )

        category_lookup = {
            category.key: category
            for category in CatalogCategory.objects.filter(
                key__in=requested_category_keys,
                is_active=True,
            )
        }

        missing_category_keys = sorted(
            requested_category_keys
            - set(category_lookup)
        )

        if missing_category_keys:
            raise CommandError(
                "Active catalog-category records are "
                "missing from Discovery: "
                + ", ".join(missing_category_keys)
            )

        with transaction.atomic():
            people = self._import_people(
                payload.get("people", []),
                partner,
            )
            course_runs = self._import_microcourses(
                payload.get("microcourses", []),
                people,
                category_lookup,
            )
            self._import_programs(
                payload.get("certificate_programs", []),
                partner,
                people,
                course_runs,
                category_lookup,
            )

        self.stdout.write(self.style.SUCCESS("CBA catalog import completed."))

    def _validate(self, payload):
        errors = []
        if not isinstance(payload, dict):
            return ["The top-level JSON value must be an object."]

        people_ids = set()
        for index, person in enumerate(payload.get("people", []), start=1):
            prefix = f"people[{index}]"
            for field in ("person_id", "given_name"):
                if not person.get(field):
                    errors.append(f"{prefix}.{field} is required.")
            if person.get("person_id") in people_ids:
                errors.append(f"{prefix}.person_id must be unique.")
            people_ids.add(person.get("person_id"))

        course_keys = set()
        required_course_fields = (
            "course_key", "organization", "course_number", "course_run", "title",
            "pacing", "duration_minutes", "price", "currency", "catalog_status",
            "catalog_visibility", "access_scope", "access_policy_key",
            "primary_catalog_category", "catalog_categories",
            "standalone_enrollment_allowed",
            "short_description", "full_description", "learning_outcomes",
            "course_overview", "syllabus", "references",
        )
        for index, course in enumerate(payload.get("microcourses", []), start=1):
            prefix = f"microcourses[{index}]"
            for field in required_course_fields:
                if field not in course or (
                    field != "access_policy_key" and course[field] in (None, "")
                ):
                    errors.append(f"{prefix}.{field} is required.")
            key = course.get("course_key")
            expected = f"course-v1:{course.get('organization')}+{course.get('course_number')}+{course.get('course_run')}"
            if key and key != expected:
                errors.append(f"{prefix}.course_key must equal {expected!r}.")
            if key in course_keys:
                errors.append(f"{prefix}.course_key must be unique.")
            course_keys.add(key)
            self._validate_common(prefix, course, errors)
            self._validate_faculty(prefix, course.get("faculty", []), people_ids, errors)

        program_codes = set()
        required_program_fields = (
            "program_code", "title", "short_description", "full_description",
            "catalog_status", "duration_minutes", "price", "currency",
            "pacing", "catalog_visibility", "access_scope", "access_policy_key",
            "primary_catalog_category", "catalog_categories",
            "learning_outcomes", "course_overview", "syllabus",
            "completion_requirements", "references", "microcourses",
        )
        for index, program in enumerate(payload.get("certificate_programs", []), start=1):
            prefix = f"certificate_programs[{index}]"
            for field in required_program_fields:
                if field not in program or (
                    field != "access_policy_key" and program[field] in (None, "")
                ):
                    errors.append(f"{prefix}.{field} is required.")
            code = program.get("program_code")
            if code in program_codes:
                errors.append(f"{prefix}.program_code must be unique.")
            program_codes.add(code)
            self._validate_common(prefix, program, errors)
            if program.get("access_scope") == AccessScope.PROGRAM_ONLY:
                errors.append(f"{prefix}.access_scope cannot be program_only for a certificate program.")
            self._validate_faculty(prefix, program.get("program_faculty", []), people_ids, errors)
            sequences = set()
            for item_index, item in enumerate(program.get("microcourses", []), start=1):
                item_prefix = f"{prefix}.microcourses[{item_index}]"
                if item.get("course_key") not in course_keys:
                    errors.append(f"{item_prefix}.course_key is not defined in microcourses.")
                if not isinstance(item.get("sequence"), int) or item["sequence"] < 1:
                    errors.append(f"{item_prefix}.sequence must be a positive integer.")
                elif item["sequence"] in sequences:
                    errors.append(f"{item_prefix}.sequence must be unique within the program.")
                sequences.add(item.get("sequence"))
        return errors

    def _validate_common(self, prefix, item, errors):
        status = item.get("catalog_status")
        if status and status not in VALID_STATUSES:
            errors.append(f"{prefix}.catalog_status must be one of {sorted(VALID_STATUSES)}.")
        visibility = item.get("catalog_visibility")
        access_scope = item.get("access_scope")
        policy_key = item.get("access_policy_key", "")
        if visibility and visibility not in VALID_VISIBILITIES:
            errors.append(
                f"{prefix}.catalog_visibility must be one of {sorted(VALID_VISIBILITIES)}."
            )
        if access_scope and access_scope not in VALID_ACCESS_SCOPES:
            errors.append(f"{prefix}.access_scope must be one of {sorted(VALID_ACCESS_SCOPES)}.")
        if visibility == CatalogVisibility.PUBLIC and access_scope != AccessScope.PUBLIC:
            errors.append(f"{prefix}: public listings must use access_scope='public'.")
        if visibility == CatalogVisibility.HIDDEN and access_scope == AccessScope.PUBLIC:
            errors.append(f"{prefix}: hidden listings cannot use access_scope='public'.")
        if access_scope == AccessScope.ORGANIZATION_CODE and not policy_key:
            errors.append(
                f"{prefix}.access_policy_key is required for organization_code access."
            )
        if access_scope != AccessScope.ORGANIZATION_CODE and policy_key:
            errors.append(
                f"{prefix}.access_policy_key must be empty unless access_scope is organization_code."
            )
        primary_category = item.get(
            "primary_catalog_category"
        )
        category_values = item.get(
            "catalog_categories"
        )

        if (
            not isinstance(primary_category, str)
            or not primary_category
        ):
            errors.append(
                f"{prefix}.primary_catalog_category "
                "must be a nonempty string."
            )

        if (
            not isinstance(category_values, list)
            or not category_values
        ):
            errors.append(
                f"{prefix}.catalog_categories "
                "must be a nonempty array."
            )
        else:
            string_categories = [
                category
                for category in category_values
                if isinstance(category, str)
                and category
            ]

            if len(string_categories) != len(
                category_values
            ):
                errors.append(
                    f"{prefix}.catalog_categories values "
                    "must be nonempty strings."
                )

            if len(string_categories) != len(
                set(string_categories)
            ):
                errors.append(
                    f"{prefix}.catalog_categories "
                    "must not contain duplicates."
                )

            if (
                isinstance(primary_category, str)
                and primary_category
                and primary_category
                not in string_categories
            ):
                errors.append(
                    f"{prefix}.primary_catalog_category "
                    "must also occur in catalog_categories."
                )

            unknown_categories = sorted(
                set(string_categories)
                - VALID_CATALOG_CATEGORIES
            )

            if unknown_categories:
                errors.append(
                    f"{prefix}.catalog_categories contains "
                    "unknown values: "
                    + ", ".join(unknown_categories)
                    + "."
                )

        if "standalone_enrollment_allowed" in item:
            standalone = item["standalone_enrollment_allowed"]
            if not isinstance(standalone, bool):
                errors.append(f"{prefix}.standalone_enrollment_allowed must be a boolean.")
            elif access_scope == AccessScope.PROGRAM_ONLY and standalone:
                errors.append(
                    f"{prefix}.standalone_enrollment_allowed must be false for program_only access."
                )
        if "duration_minutes" in item and (
            not isinstance(item["duration_minutes"], int) or item["duration_minutes"] < 1
        ):
            errors.append(f"{prefix}.duration_minutes must be a positive integer.")
        try:
            if "price" in item and Decimal(str(item["price"])) < 0:
                errors.append(f"{prefix}.price cannot be negative.")
        except Exception:
            errors.append(f"{prefix}.price must be a decimal value.")
        if item.get("currency") and len(item["currency"]) != 3:
            errors.append(f"{prefix}.currency must be a three-letter code.")
        for list_field in ("learning_outcomes", "references"):
            if list_field in item and not isinstance(item[list_field], list):
                errors.append(f"{prefix}.{list_field} must be an array.")

    def _validate_faculty(self, prefix, assignments, people_ids, errors):
        for index, assignment in enumerate(assignments, start=1):
            item_prefix = f"{prefix}.faculty[{index}]"
            if assignment.get("person_id") not in people_ids:
                errors.append(f"{item_prefix}.person_id is not defined in people.")
            if assignment.get("role") not in VALID_ROLES:
                errors.append(f"{item_prefix}.role must be one of {sorted(VALID_ROLES)}.")

    def _import_people(self, records, partner):
        result = {}
        for record in records:
            email = record.get("email") or None
            lookup = {"partner": partner, "email": email} if email else {
                "partner": partner,
                "given_name": record["given_name"],
                "family_name": record.get("family_name", ""),
            }
            person, _created = Person.objects.update_or_create(
                **lookup,
                defaults={
                    "given_name": record["given_name"],
                    "family_name": record.get("family_name", ""),
                    "bio": record.get("bio", ""),
                    "published": record.get("published", True),
                },
            )
            result[record["person_id"]] = person
        return result

    def _import_microcourses(
        self,
        records,
        people,
        category_lookup,
    ):
        result = {}
        for record in records:
            try:
                course_run = CourseRun.objects.select_related("course").get(key=record["course_key"])
            except CourseRun.DoesNotExist as exc:
                raise CommandError(
                    f"{record['course_key']} does not exist in Discovery. Create the Studio course shell and "
                    "refresh its metadata before running this catalog import."
                ) from exc

            course = course_run.course
            course.title = record["title"]
            course.number = record["course_number"]
            course.short_description = record["short_description"]
            course.full_description = record["full_description"]
            course.syllabus_raw = record["syllabus"]
            course.save()

            course_run.pacing_type = record["pacing"]
            course_run.save()
            metadata, _created = (
                MicrocourseCatalogMetadata.objects.update_or_create(
                    course_run=course_run,
                    defaults={
                        "primary_catalog_category": category_lookup[
                            record["primary_catalog_category"]
                        ],
                        "duration_minutes": record["duration_minutes"],
                        "catalog_status": record["catalog_status"],
                        "catalog_visibility": record["catalog_visibility"],
                        "access_scope": record["access_scope"],
                        "access_policy_key": record["access_policy_key"],
                        "standalone_enrollment_allowed": record["standalone_enrollment_allowed"],
                        "course_overview": record["course_overview"],
                        "learning_outcomes": record["learning_outcomes"],
                        "references": record["references"],
                    },
                )
            )

            metadata.catalog_categories.set(
                [
                    category_lookup[key]
                    for key in record["catalog_categories"]
                ]
            )

            self._upsert_seat(
                course_run,
                record["price"],
                record["currency"],
            )
            self._replace_course_faculty(course_run, record.get("faculty", []), people)
            result[record["course_key"]] = course_run
        return result

    def _upsert_seat(self, course_run, price, currency_code):
        currency = Currency.objects.get(code=currency_code.upper())
        seat_type, _created = SeatType.objects.get_or_create(name="Professional")
        Seat.objects.update_or_create(
            course_run=course_run,
            type=seat_type,
            currency=currency,
            credit_provider=None,
            defaults={"price": Decimal(str(price))},
        )

    def _replace_course_faculty(self, course_run, assignments, people):
        CourseRunFacultyAssignment.objects.filter(course_run=course_run).delete()
        course_run.staff.clear()
        for index, item in enumerate(assignments):
            person = people[item["person_id"]]
            course_run.staff.add(person)
            CourseRunFacultyAssignment.objects.create(
                course_run=course_run,
                person=person,
                role=item["role"],
                credentials=item.get("credentials", ""),
                display_order=item.get("display_order", index),
            )

    def _import_programs(
        self,
        records,
        partner,
        people,
        course_runs,
        category_lookup,
    ):
        organization_cache = {}
        for record in records:
            metadata = CertificateProgramCatalogMetadata.objects.filter(
                program_code=record["program_code"]
            ).select_related("program").first()
            if metadata:
                program = metadata.program
            else:
                program_type = ProgramType.objects.get(slug=record.get("program_type", "certificate"))
                program = Program.objects.create(
                    partner=partner,
                    type=program_type,
                    title=record["title"],
                    subtitle=record.get("subtitle", ""),
                    marketing_slug=record.get("marketing_slug", record["program_code"].lower()),
                    overview=record["course_overview"],
                )
            program.title = record["title"]
            program.subtitle = record.get("subtitle", "")
            program.overview = record["course_overview"]
            program.total_hours_of_effort = max(1, (record["duration_minutes"] + 59) // 60)
            program.save()

            organization_key = record.get("organization", "CBA")
            if organization_key not in organization_cache:
                organization_cache[organization_key] = Organization.objects.get(
                    partner=partner,
                    key=organization_key,
                )
            program.authoring_organizations.set([organization_cache[organization_key]])

            metadata, _created = (
                CertificateProgramCatalogMetadata.objects.update_or_create(
                    program=program,
                    defaults={
                        "primary_catalog_category": category_lookup[
                            record["primary_catalog_category"]
                        ],
                        "program_code": record["program_code"],
                        "short_description": record["short_description"],
                        "full_description": record["full_description"],
                        "catalog_status": record["catalog_status"],
                        "catalog_visibility": record["catalog_visibility"],
                        "access_scope": record["access_scope"],
                        "access_policy_key": record["access_policy_key"],
                        "duration_minutes": record["duration_minutes"],
                        "price": Decimal(str(record["price"])),
                        "currency": record["currency"].upper(),
                        "pacing": record["pacing"],
                        "course_overview": record["course_overview"],
                        "syllabus": record["syllabus"],
                        "completion_requirements": record["completion_requirements"],
                        "learning_outcomes": record["learning_outcomes"],
                        "references": record["references"],
                    },
                )
            )

            metadata.catalog_categories.set(
                [
                    category_lookup[key]
                    for key in record["catalog_categories"]
                ]
            )

            ProgramCourseRequirement.objects.filter(
                program=program
            ).delete()
            ordered_courses = []
            for item in sorted(record["microcourses"], key=lambda value: value["sequence"]):
                course_run = course_runs[item["course_key"]]
                ordered_courses.append(course_run.course)
                ProgramCourseRequirement.objects.create(
                    program=program,
                    course_run=course_run,
                    sequence=item["sequence"],
                    required=item.get("required", True),
                )
            program.courses.set(ordered_courses)
            self._replace_program_faculty(program, record.get("program_faculty", []), people)

    def _replace_program_faculty(self, program, assignments, people):
        ProgramFacultyAssignment.objects.filter(program=program).delete()
        program.instructor_ordering.clear()
        for index, item in enumerate(assignments):
            person = people[item["person_id"]]
            program.instructor_ordering.add(person)
            ProgramFacultyAssignment.objects.create(
                program=program,
                person=person,
                role=item["role"],
                credentials=item.get("credentials", ""),
                display_order=item.get("display_order", index),
                is_primary=item.get("is_primary", False),
            )
