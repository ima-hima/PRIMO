import tempfile
from contextlib import contextmanager
from typing import Generator

from django.db import connection
from django.test import SimpleTestCase, TestCase

from web.views import (  # type: ignore[attr-defined]
    _find_missing_specimens,
    _format_db_error,
    _preview_specimen_counts,
    _preview_teeth_counts,
    _upsert_specimen_data,
    _upsert_teeth_data,
)

SESSION_HEADER = (
    "id,observer_id,group_id,specimen_id,original_id,protocol_id,comments,filename\n"
)
SCALAR_HEADER = "id,session_id,variable_id,value\n"


def _sess_csv(*rows: str) -> str:
    return SESSION_HEADER + "\n".join(rows) + "\n"


def _scalar_csv(*rows: str) -> str:
    return SCALAR_HEADER + "\n".join(rows) + "\n"


class UpsertTeethDataTest(TestCase):
    def setUp(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=0")
            c.execute(
                "INSERT IGNORE INTO specimen (id, taxonomic_type_id, updated_at)"
                " VALUES (100, 1, NOW()),"
                "        (101, 1, NOW())"
            )

    def tearDown(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=1")

    def _run(
        self, sess_content: str, scalar_content: str
    ) -> tuple[list[str], dict[str, int]]:
        with (
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".sess.csv", delete=False
            ) as sf,
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".scalar.csv", delete=False
            ) as scf,
        ):
            sf.write(sess_content)
            scf.write(scalar_content)
            sess_path = sf.name
            scalar_path = scf.name
        return _upsert_teeth_data(sess_path, scalar_path, set())

    def _session_row(self, id: int) -> dict | None:
        with connection.cursor() as c:
            c.execute("SELECT * FROM session WHERE id=%s", [id])
            cols = [d[0] for d in c.description]
            row = c.fetchone()
            return dict(zip(cols, row)) if row else None

    def _scalar_rows(self, session_id: int) -> list[dict]:
        with connection.cursor() as c:
            c.execute(
                "SELECT * FROM data_scalar WHERE session_id=%s ORDER BY id",
                [session_id],
            )
            cols = [d[0] for d in c.description]
            return [dict(zip(cols, r)) for r in c.fetchall()]

    def test_inserts_new_session_and_scalar(self) -> None:
        errors, counts = self._run(
            _sess_csv("1,9,2,100,1,5,test comment,teeth"),
            _scalar_csv("100,1,225,12.3"),
        )
        self.assertEqual(errors, [])
        self.assertEqual(counts["sessions_inserted"], 1)
        self.assertEqual(counts["scalars_inserted"], 1)
        sess = self._session_row(1)
        self.assertIsNotNone(sess)
        assert sess is not None
        self.assertEqual(sess["specimen_id"], 100)
        self.assertEqual(sess["comments"], "test comment")
        scalars = self._scalar_rows(1)
        self.assertEqual(len(scalars), 1)
        self.assertEqual(scalars[0]["value"], "12.3")

    def test_updates_existing_session_on_duplicate(self) -> None:
        self._run(
            _sess_csv("1,9,2,100,1,5,original comment,teeth"),
            _scalar_csv("100,1,225,12.3"),
        )
        errors, counts = self._run(
            _sess_csv("1,9,2,100,1,5,updated comment,teeth"),
            _scalar_csv("100,1,225,9.9"),
        )
        self.assertEqual(errors, [])
        self.assertEqual(counts["sessions_updated"], 1)
        self.assertEqual(counts["scalars_updated"], 1)
        sess = self._session_row(1)
        assert sess is not None
        self.assertEqual(sess["comments"], "updated comment")
        scalars = self._scalar_rows(1)
        self.assertEqual(scalars[0]["value"], "9.9")

    def test_inserts_multiple_sessions_and_scalars(self) -> None:
        errors, counts = self._run(
            _sess_csv(
                "1,9,2,100,1,5,,teeth",
                "2,9,2,101,1,5,,teeth",
            ),
            _scalar_csv(
                "100,1,225,1.1",
                "101,2,225,2.2",
            ),
        )
        self.assertEqual(errors, [])
        self.assertEqual(counts["sessions_inserted"], 2)
        self.assertEqual(counts["scalars_inserted"], 2)
        self.assertIsNotNone(self._session_row(1))
        self.assertIsNotNone(self._session_row(2))
        self.assertEqual(len(self._scalar_rows(1)), 1)
        self.assertEqual(len(self._scalar_rows(2)), 1)

    def test_bad_session_row_logged_and_continues(self) -> None:
        # variable_id 999999 doesn't exist but FK checks are off;
        # use an invalid specimen_id type to force an error instead
        # by passing a non-numeric value
        errors, _ = self._run(
            _sess_csv("BADID,9,2,100,1,5,,teeth"),
            _scalar_csv("100,1,225,1.0"),
        )
        self.assertTrue(len(errors) > 0)
        self.assertIn("Failed to insert session", errors[0])
        # scalar still inserted despite session error
        with connection.cursor() as c:
            c.execute("SELECT COUNT(*) FROM data_scalar WHERE session_id=1")
            self.assertEqual(c.fetchone()[0], 1)

    def test_empty_csvs_produce_no_errors(self) -> None:
        errors, counts = self._run(SESSION_HEADER, SCALAR_HEADER)
        self.assertEqual(errors, [])
        self.assertEqual(counts["sessions_inserted"], 0)
        self.assertEqual(counts["scalars_inserted"], 0)

    def test_skipped_session_ids_excluded(self) -> None:
        # Session 1 is in the skipped set; its scalar should also be skipped.
        errors, counts = self._run(
            _sess_csv("1,9,2,100,1,5,,teeth", "2,9,2,101,1,5,,teeth"),
            _scalar_csv("10,1,225,1.1", "11,2,225,2.2"),
        )
        # Re-run with session 1 in skipped set
        with (
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".sess.csv", delete=False
            ) as sf,
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".scalar.csv", delete=False
            ) as scf,
        ):
            sf.write(_sess_csv("1,9,2,100,1,5,,teeth", "2,9,2,101,1,5,,teeth"))
            scf.write(_scalar_csv("10,1,225,1.1", "11,2,225,2.2"))
            sess_path = sf.name
            scalar_path = scf.name
        with connection.cursor() as c:
            c.execute("DELETE FROM data_scalar")
            c.execute("DELETE FROM session")
        errors2, counts2 = _upsert_teeth_data(sess_path, scalar_path, {"1"})
        self.assertEqual(errors2, [])
        self.assertEqual(counts2["sessions_inserted"], 1)
        self.assertEqual(counts2["scalars_inserted"], 1)
        with connection.cursor() as c:
            c.execute("SELECT id FROM session")
            ids = [r[0] for r in c.fetchall()]
        self.assertNotIn(1, ids)
        self.assertIn(2, ids)


SPECIMEN_HEADER = (
    "id,hypocode,taxon_id,institute_id,catalog_number,"
    "mass,locality_id,sex_id,fossil_id,captive_id,taxonomic_type_id,comments\n"
)


def _spec_csv(*rows: str) -> str:
    return SPECIMEN_HEADER + "\n".join(rows) + "\n"


def _spec_row(
    id: str = "200",
    hypo: str = "XYZ001",
    taxon: str = "1",
    inst: str = "1",
    catnum: str = "C1",
    mass: str = "500",
    loc: str = "1",
    sex: str = "1",
    fossil: str = "2",
    captive: str = "2",
    typ: str = "1",
    comments: str = "",
) -> str:
    return (
        f"{id},{hypo},{taxon},{inst},{catnum},{mass},"
        f"{loc},{sex},{fossil},{captive},{typ},{comments}"
    )


@contextmanager
def _fk_off() -> Generator[None, None, None]:
    with connection.cursor() as c:
        c.execute("SET FOREIGN_KEY_CHECKS=0")
    try:
        yield
    finally:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=1")


class PreviewTeethCountsTest(TestCase):
    def setUp(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=0")
            c.execute(
                "INSERT IGNORE INTO specimen (id, taxonomic_type_id, updated_at)"
                " VALUES (100, 1, NOW()), (101, 1, NOW())"
            )

    def tearDown(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=1")

    def _make_csvs(self, sess_content: str, scalar_content: str) -> tuple[str, str]:
        sf = tempfile.NamedTemporaryFile(mode="w", suffix=".sess.csv", delete=False)
        scf = tempfile.NamedTemporaryFile(mode="w", suffix=".scalar.csv", delete=False)
        sf.write(sess_content)
        scf.write(scalar_content)
        sf.close()
        scf.close()
        return sf.name, scf.name

    def test_all_new_counted_as_inserts(self) -> None:
        sess_path, scalar_path = self._make_csvs(
            _sess_csv("1,9,2,100,1,5,,teeth"),
            _scalar_csv("10,1,225,1.1"),
        )
        counts, missing, skipped = _preview_teeth_counts(sess_path, scalar_path)
        self.assertEqual(counts["sessions_insert"], 1)
        self.assertEqual(counts["sessions_update"], 0)
        self.assertEqual(counts["scalars_insert"], 1)
        self.assertEqual(counts["scalars_update"], 0)
        self.assertEqual(missing, [])

    def test_existing_rows_counted_as_updates(self) -> None:
        # Insert first so the preview sees them as existing.
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=0")
            c.execute(
                "INSERT INTO session (id, observer_id, group_id, specimen_id,"
                " original_id, protocol_id, comments, filename, updated_at)"
                " VALUES (1, 9, 2, 100, 1, 5, '', 'teeth', NOW())"
            )
            c.execute(
                "INSERT INTO data_scalar (id, session_id, variable_id,"
                " value, updated_at)"
                " VALUES (10, 1, 225, '1.1', NOW())"
            )
        sess_path, scalar_path = self._make_csvs(
            _sess_csv("1,9,2,100,1,5,,teeth"),
            _scalar_csv("10,1,225,9.9"),
        )
        counts, missing, skipped = _preview_teeth_counts(sess_path, scalar_path)
        self.assertEqual(counts["sessions_insert"], 0)
        self.assertEqual(counts["sessions_update"], 1)
        self.assertEqual(counts["scalars_insert"], 0)
        self.assertEqual(counts["scalars_update"], 1)

    def test_missing_specimen_reported_and_session_skipped(self) -> None:
        sess_path, scalar_path = self._make_csvs(
            _sess_csv("1,9,2,99999,1,5,,teeth"),  # specimen 99999 not in DB
            _scalar_csv("10,1,225,1.1"),
        )
        counts, missing, skipped = _preview_teeth_counts(sess_path, scalar_path)
        self.assertIn("99999", missing)
        self.assertIn("1", skipped)
        self.assertEqual(counts["sessions_insert"], 0)
        self.assertEqual(counts["scalars_insert"], 0)

    def test_empty_csvs_all_zeros(self) -> None:
        sess_path, scalar_path = self._make_csvs(SESSION_HEADER, SCALAR_HEADER)
        counts, missing, skipped = _preview_teeth_counts(sess_path, scalar_path)
        self.assertEqual(
            counts,
            {
                "sessions_insert": 0,
                "sessions_update": 0,
                "scalars_insert": 0,
                "scalars_update": 0,
            },
        )
        self.assertEqual(missing, [])

    def test_mixed_insert_and_update(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=0")
            c.execute(
                "INSERT INTO session (id, observer_id, group_id, specimen_id,"
                " original_id, protocol_id, comments, filename, updated_at)"
                " VALUES (1, 9, 2, 100, 1, 5, 'old comment', 'teeth', NOW())"
            )
        # CSV has a changed comment for session 1 and a new session 2
        sess_path, scalar_path = self._make_csvs(
            _sess_csv("1,9,2,100,1,5,new comment,teeth", "2,9,2,101,1,5,,teeth"),
            _scalar_csv("10,1,225,1.1", "11,2,225,2.2"),
        )
        counts, missing, _ = _preview_teeth_counts(sess_path, scalar_path)
        self.assertEqual(counts["sessions_insert"], 1)
        self.assertEqual(counts["sessions_update"], 1)


class FindMissingSpecimensTest(TestCase):
    def setUp(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=0")
            c.execute(
                "INSERT IGNORE INTO specimen (id, taxonomic_type_id, updated_at)"
                " VALUES (100, 1, NOW())"
            )

    def tearDown(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=1")

    def test_no_missing_when_all_present(self) -> None:
        rows = [{"id": "1", "specimen_id": "100"}]
        with connection.cursor() as cursor:
            missing, skipped = _find_missing_specimens(cursor, rows)
        self.assertEqual(missing, [])
        self.assertEqual(skipped, set())

    def test_missing_specimen_identified(self) -> None:
        rows = [{"id": "1", "specimen_id": "99999"}]
        with connection.cursor() as cursor:
            missing, skipped = _find_missing_specimens(cursor, rows)
        self.assertIn("99999", missing)
        self.assertIn("1", skipped)

    def test_empty_rows(self) -> None:
        with connection.cursor() as cursor:
            missing, skipped = _find_missing_specimens(cursor, [])
        self.assertEqual(missing, [])
        self.assertEqual(skipped, set())

    def test_partial_missing(self) -> None:
        rows = [
            {"id": "1", "specimen_id": "100"},
            {"id": "2", "specimen_id": "99999"},
        ]
        with connection.cursor() as cursor:
            missing, skipped = _find_missing_specimens(cursor, rows)
        self.assertEqual(missing, ["99999"])
        self.assertEqual(skipped, {"2"})


class UpsertSpecimenDataTest(TestCase):
    def setUp(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=0")

    def tearDown(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=1")

    def _run(self, content: str) -> tuple[list[str], dict[str, int]]:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".specimen.csv", delete=False
        ) as f:
            f.write(content)
            path = f.name
        return _upsert_specimen_data(path)

    def test_inserts_new_specimen(self) -> None:
        errors, counts = self._run(_spec_csv(_spec_row(id="200")))
        self.assertEqual(errors, [])
        self.assertEqual(counts["specimens_inserted"], 1)
        self.assertEqual(counts["specimens_updated"], 0)

    def test_updates_existing_specimen(self) -> None:
        self._run(_spec_csv(_spec_row(id="200", mass="100")))
        errors, counts = self._run(_spec_csv(_spec_row(id="200", mass="200")))
        self.assertEqual(errors, [])
        self.assertEqual(counts["specimens_inserted"], 0)
        self.assertEqual(counts["specimens_updated"], 1)
        with connection.cursor() as c:
            c.execute("SELECT mass FROM specimen WHERE id=200")
            self.assertEqual(str(c.fetchone()[0]), "200")

    def test_inserts_multiple(self) -> None:
        errors, counts = self._run(
            _spec_csv(_spec_row(id="200"), _spec_row(id="201", hypo="XYZ002"))
        )
        self.assertEqual(errors, [])
        self.assertEqual(counts["specimens_inserted"], 2)

    def test_empty_csv_produces_no_errors(self) -> None:
        errors, counts = self._run(SPECIMEN_HEADER)
        self.assertEqual(errors, [])
        self.assertEqual(counts["specimens_inserted"], 0)
        self.assertEqual(counts["specimens_updated"], 0)


class PreviewSpecimenCountsTest(TestCase):
    def setUp(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=0")

    def tearDown(self) -> None:
        with connection.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=1")

    def _make_csv(self, content: str) -> str:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".specimen.csv", delete=False
        ) as f:
            f.write(content)
            return f.name

    def test_all_new_counted_as_inserts(self) -> None:
        path = self._make_csv(_spec_csv(_spec_row(id="300")))
        counts = _preview_specimen_counts(path)
        self.assertEqual(counts["specimens_insert"], 1)
        self.assertEqual(counts["specimens_update"], 0)

    def test_existing_counted_as_update(self) -> None:
        with connection.cursor() as c:
            c.execute(
                "INSERT IGNORE INTO specimen (id, taxonomic_type_id, updated_at)"
                " VALUES (300, 1, NOW())"
            )
        path = self._make_csv(_spec_csv(_spec_row(id="300")))
        counts = _preview_specimen_counts(path)
        self.assertEqual(counts["specimens_insert"], 0)
        self.assertEqual(counts["specimens_update"], 1)

    def test_mixed_insert_and_update(self) -> None:
        with connection.cursor() as c:
            c.execute(
                "INSERT IGNORE INTO specimen (id, taxonomic_type_id, updated_at)"
                " VALUES (300, 1, NOW())"
            )
        path = self._make_csv(
            _spec_csv(_spec_row(id="300"), _spec_row(id="301", hypo="XYZ002"))
        )
        counts = _preview_specimen_counts(path)
        self.assertEqual(counts["specimens_insert"], 1)
        self.assertEqual(counts["specimens_update"], 1)

    def test_empty_csv_all_zeros(self) -> None:
        path = self._make_csv(SPECIMEN_HEADER)
        counts = _preview_specimen_counts(path)
        self.assertEqual(counts, {"specimens_insert": 0, "specimens_update": 0})


class FormatDbErrorTest(SimpleTestCase):
    def _fk_error(self, col: str, ref_table: str) -> Exception:
        return Exception(
            f"(1452, 'Cannot add or update a child row: a foreign key constraint "
            f"fails (`db`.`specimen`, CONSTRAINT `specimen_{col}_fk` "
            f"FOREIGN KEY (`{col}`) REFERENCES `{ref_table}` (`id`))')"
        )

    def test_fk_error_produces_clean_message(self) -> None:
        row = {"id": "53097", "institute_id": "42"}
        msg = _format_db_error(self._fk_error("institute_id", "institute"), row)
        self.assertEqual(msg, "No institute with id 42 exists.")

    def test_fk_error_different_column(self) -> None:
        row = {"id": "100", "taxon_id": "999"}
        msg = _format_db_error(self._fk_error("taxon_id", "taxon"), row)
        self.assertEqual(msg, "No taxon with id 999 exists.")

    def test_non_fk_error_returns_raw_message(self) -> None:
        row = {"id": "1"}
        msg = _format_db_error(Exception("some unexpected error"), row)
        self.assertEqual(msg, "some unexpected error")

    def test_missing_col_value_shows_question_mark(self) -> None:
        row = {"id": "1"}  # institute_id not present
        msg = _format_db_error(self._fk_error("institute_id", "institute"), row)
        self.assertEqual(msg, "No institute with id ? exists.")
