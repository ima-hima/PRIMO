import tempfile

from django.db import connection
from django.test import SimpleTestCase, TestCase

from web.views import (  # type: ignore[attr-defined]
    _preview_institute_counts,
    _upsert_institute_data,
    _validate_institute_csv,
)

INSTITUTE_HEADER = "id,instabbr,instname,instdept,locality_id,comments\n"


def _inst_csv(*rows: str) -> str:
    return INSTITUTE_HEADER + "\n".join(rows) + "\n"


def _inst_row(
    id: str = "10",
    abbr: str = "UNK",
    name: str = "Unknown Museum",
    dept: str = "",
    locality_id: str = "10000",
    comments: str = "",
) -> str:
    return f"{id},{abbr},{name},{dept},{locality_id},{comments}"


def _inst_path(content: str) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        return f.name


class ValidateInstituteCsvTest(SimpleTestCase):
    def _validate(self, content: str) -> list[str]:
        return _validate_institute_csv(_inst_path(content))

    def test_valid_rows_produce_no_errors(self) -> None:
        errors = self._validate(_inst_csv(_inst_row(), _inst_row(id="11", abbr="AMN")))
        self.assertEqual(errors, [])

    def test_missing_id_reported(self) -> None:
        errors = self._validate(_inst_csv(",UNK,Unknown Museum,,,"))
        self.assertTrue(any("missing id" in e for e in errors))

    def test_missing_name_reported(self) -> None:
        errors = self._validate(_inst_csv(_inst_row(id="10", name="")))
        self.assertTrue(any("missing institute name" in e for e in errors))

    def test_duplicate_id_reported_once(self) -> None:
        errors = self._validate(
            _inst_csv(_inst_row(id="10"), _inst_row(id="10"), _inst_row(id="10"))
        )
        dup_errors = [e for e in errors if "Repeated institute id: 10" in e]
        self.assertEqual(len(dup_errors), 1)

    def test_no_duplicate_no_error(self) -> None:
        errors = self._validate(
            _inst_csv(_inst_row(id="10"), _inst_row(id="11"), _inst_row(id="12"))
        )
        self.assertEqual(errors, [])

    def test_missing_id_and_name_both_reported(self) -> None:
        errors = self._validate(_inst_csv(",,,,,"))
        self.assertTrue(any("missing id" in e for e in errors))
        # missing name is not reported when id is also missing (row is skipped after id check)
        self.assertEqual(len([e for e in errors if "missing id" in e]), 1)

    def test_bom_stripped(self) -> None:
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as f:
            f.write(("﻿" + _inst_csv(_inst_row())).encode("utf-8"))
            path = f.name
        self.assertEqual(_validate_institute_csv(path), [])


class UpsertInstituteDataTest(TestCase):
    def setUp(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=0")

    def tearDown(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=1")

    def _run(self, content: str) -> tuple[list[str], dict[str, int]]:
        return _upsert_institute_data(_inst_path(content))

    def test_inserts_new_institute(self) -> None:
        errors, counts = self._run(_inst_csv(_inst_row(id="500")))
        self.assertEqual(errors, [])
        self.assertEqual(counts["institutes_inserted"], 1)
        self.assertEqual(counts["institutes_updated"], 0)

    def test_updates_existing_institute(self) -> None:
        self._run(_inst_csv(_inst_row(id="500", name="Old Name")))
        errors, counts = self._run(_inst_csv(_inst_row(id="500", name="New Name")))
        self.assertEqual(errors, [])
        self.assertEqual(counts["institutes_inserted"], 0)
        self.assertEqual(counts["institutes_updated"], 1)
        with connection.cursor() as c:
            c.execute("SELECT institute_name FROM institute WHERE id=500")
            self.assertEqual(c.fetchone()[0], "New Name")

    def test_noop_counts_as_neither(self) -> None:
        self._run(_inst_csv(_inst_row(id="500")))
        errors, counts = self._run(_inst_csv(_inst_row(id="500")))
        self.assertEqual(errors, [])
        self.assertEqual(counts["institutes_inserted"], 0)
        self.assertEqual(counts["institutes_updated"], 0)

    def test_inserts_multiple(self) -> None:
        errors, counts = self._run(
            _inst_csv(_inst_row(id="500"), _inst_row(id="501", abbr="AMN"))
        )
        self.assertEqual(errors, [])
        self.assertEqual(counts["institutes_inserted"], 2)

    def test_empty_csv_produces_no_errors(self) -> None:
        errors, counts = self._run(INSTITUTE_HEADER)
        self.assertEqual(errors, [])
        self.assertEqual(counts["institutes_inserted"], 0)
        self.assertEqual(counts["institutes_updated"], 0)

    def test_blank_id_row_silently_skipped(self) -> None:
        errors, counts = self._run(_inst_csv(_inst_row(id="500"), ",UNK,X,,,"))
        self.assertEqual(errors, [])
        self.assertEqual(counts["institutes_inserted"], 1)

    def test_fk_violation_reported_as_error(self) -> None:
        # Re-enable FK checks so locality_id=99999 triggers a real FK error.
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=1")
        errors, counts = self._run(
            _inst_csv(_inst_row(id="500", locality_id="99999"))
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("locality", errors[0])
        self.assertEqual(counts["institutes_inserted"], 0)


class PreviewInstituteCountsTest(TestCase):
    def setUp(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=0")

    def tearDown(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=1")

    def test_all_new_counted_as_inserts(self) -> None:
        counts = _preview_institute_counts(_inst_path(_inst_csv(_inst_row(id="600"))))
        self.assertEqual(counts["institutes_insert"], 1)
        self.assertEqual(counts["institutes_update"], 0)

    def test_existing_counted_as_update(self) -> None:
        with connection.cursor() as c:
            c.execute(
                "INSERT IGNORE INTO institute (id, institute_name) VALUES (600, 'X')"
            )
        counts = _preview_institute_counts(_inst_path(_inst_csv(_inst_row(id="600"))))
        self.assertEqual(counts["institutes_insert"], 0)
        self.assertEqual(counts["institutes_update"], 1)

    def test_empty_csv_all_zeros(self) -> None:
        counts = _preview_institute_counts(_inst_path(INSTITUTE_HEADER))
        self.assertEqual(counts, {"institutes_insert": 0, "institutes_update": 0})
