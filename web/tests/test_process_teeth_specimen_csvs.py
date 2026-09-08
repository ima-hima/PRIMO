import io
import sys
import tempfile
from csv import DictReader
from pathlib import Path

from django.test import SimpleTestCase

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from process_teeth_specimen_csvs import process_specimens  # noqa: E402

_HEADER = (
    "UNIQUEID,HYPOCODE,taxon ID,inst ID,CATNUM,MASS,LOC ID,sex,Fossil,"
    "captive,TYPE,COMMENTS"
)


def _make_csv(*rows: str) -> str:
    return _HEADER + "\n" + "\n".join(rows) + "\n"


def _blank_row(
    uid: str = "1001",
    hypo: str = "ABC001",
    taxon: str = "10",
    inst: str = "5",
    catnum: str = "CAT1",
    mass: str = "500",
    loc: str = "200",
    sex: str = "1",
    fossil: str = "E",
    captive: str = "W",
    typ: str = "H",
    comments: str = "",
) -> str:
    return (
        f"{uid},{hypo},{taxon},{inst},{catnum},{mass},{loc},"
        f"{sex},{fossil},{captive},{typ},{comments}"
    )


def _run(csv_content: str) -> tuple[list[dict], str]:
    err = io.StringIO()
    with (
        tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as fin,
        tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as fout,
    ):
        fin.write(csv_content)
        in_path = fin.name
        out_path = fout.name
    process_specimens(in_path, out_path, err)
    with open(out_path) as f:
        rows = list(DictReader(f))
    return rows, err.getvalue()


class ProcessTeethSpecimenCsvTest(SimpleTestCase):
    def test_no_duplicate_ids_no_error(self) -> None:
        rows, errors = _run(
            _make_csv(
                _blank_row(uid="1001"),
                _blank_row(uid="1002"),
                _blank_row(uid="1003"),
            )
        )
        self.assertEqual(len(rows), 3)
        self.assertNotIn("Repeated", errors)

    def test_duplicate_id_same_hypo_skipped_with_error(self) -> None:
        rows, errors = _run(
            _make_csv(
                _blank_row(uid="1001", hypo="ABC001"),
                _blank_row(uid="1001", hypo="ABC001"),
            )
        )
        self.assertEqual(len(rows), 1)
        self.assertIn("Repeated specimen id: 1001", errors)

    def test_duplicate_id_different_hypo_skipped_with_error(self) -> None:
        rows, errors = _run(
            _make_csv(
                _blank_row(uid="1001", hypo="ABC001"),
                _blank_row(uid="1001", hypo="XYZ999"),
            )
        )
        self.assertEqual(len(rows), 1)
        self.assertIn("Repeated specimen id: 1001", errors)

    def test_duplicate_id_reported_only_once(self) -> None:
        rows, errors = _run(
            _make_csv(
                _blank_row(uid="1001"),
                _blank_row(uid="1001"),
                _blank_row(uid="1001"),
            )
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(errors.count("1001"), 1)
