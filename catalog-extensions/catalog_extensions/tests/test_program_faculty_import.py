from unittest.mock import MagicMock, call, patch

from django.test import SimpleTestCase

from catalog_extensions.management.commands.import_cba_catalog import (
    Command,
)


ASSIGNMENT_MODEL = (
    "catalog_extensions.management.commands."
    "import_cba_catalog.ProgramFacultyAssignment"
)


class ProgramFacultyImportTests(SimpleTestCase):
    @patch(ASSIGNMENT_MODEL)
    def test_faculty_uses_one_sorted_m2m_set(
        self,
        assignment_model,
    ):
        program = MagicMock()
        first_person = MagicMock(name="first_person")
        second_person = MagicMock(name="second_person")

        first_person.pk = 101
        second_person.pk = 102

        people = {
            "faculty-1": first_person,
            "faculty-2": second_person,
        }

        assignments = [
            {
                "person_id": "faculty-1",
                "role": "Lead Instructor",
                "credentials": "CRM",
                "display_order": 10,
                "is_primary": True,
            },
            {
                "person_id": "faculty-2",
                "role": "Instructor",
                "credentials": "CBCP",
                "display_order": 20,
                "is_primary": False,
            },
        ]

        Command()._replace_program_faculty(
            program,
            assignments,
            people,
        )

        assignment_model.objects.filter.assert_called_once_with(
            program=program,
        )

        (
            assignment_model.objects
            .filter.return_value
            .delete.assert_called_once_with()
        )

        program.instructor_ordering.set.assert_called_once_with(
            [
                first_person,
                second_person,
            ]
        )

        assert assignment_model.objects.create.call_args_list == [
            call(
                program=program,
                person=first_person,
                role="Lead Instructor",
                credentials="CRM",
                display_order=10,
                is_primary=True,
            ),
            call(
                program=program,
                person=second_person,
                role="Instructor",
                credentials="CBCP",
                display_order=20,
                is_primary=False,
            ),
        ]

    @patch(ASSIGNMENT_MODEL)
    def test_empty_faculty_sets_empty_ordering(
        self,
        assignment_model,
    ):
        program = MagicMock()

        Command()._replace_program_faculty(
            program,
            [],
            {},
        )

        program.instructor_ordering.set.assert_called_once_with(
            []
        )

        assignment_model.objects.create.assert_not_called()

    @patch(ASSIGNMENT_MODEL)
    def test_duplicate_person_roles_use_one_ordering_entry(
        self,
        assignment_model,
    ):
        program = MagicMock()
        person = MagicMock(name="faculty_person")
        person.pk = 201

        people = {
            "faculty-001": person,
        }

        assignments = [
            {
                "person_id": "faculty-001",
                "role": "program_director",
                "credentials": "Professional credentials",
                "display_order": 1,
                "is_primary": True,
            },
            {
                "person_id": "faculty-001",
                "role": "instructor",
                "credentials": "Professional credentials",
                "display_order": 2,
                "is_primary": False,
            },
        ]

        Command()._replace_program_faculty(
            program,
            assignments,
            people,
        )

        program.instructor_ordering.set.assert_called_once_with(
            [person]
        )

        assert assignment_model.objects.create.call_args_list == [
            call(
                program=program,
                person=person,
                role="program_director",
                credentials="Professional credentials",
                display_order=1,
                is_primary=True,
            ),
            call(
                program=program,
                person=person,
                role="instructor",
                credentials="Professional credentials",
                display_order=2,
                is_primary=False,
            ),
        ]
