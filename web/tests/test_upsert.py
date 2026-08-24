import tempfile

from django.db import connection
from django.test import TestCase

from web.views import _upsert_teeth_data

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
        return _upsert_teeth_data(sess_path, scalar_path)

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
        self.assertIn("Session insert failed", errors[0])
        # scalar still inserted despite session error
        with connection.cursor() as c:
            c.execute("SELECT COUNT(*) FROM data_scalar WHERE session_id=1")
            self.assertEqual(c.fetchone()[0], 1)

    def test_empty_csvs_produce_no_errors(self) -> None:
        errors, counts = self._run(SESSION_HEADER, SCALAR_HEADER)
        self.assertEqual(errors, [])
        self.assertEqual(counts["sessions_inserted"], 0)
        self.assertEqual(counts["scalars_inserted"], 0)
