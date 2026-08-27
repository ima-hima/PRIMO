import io
import sys
import tempfile
from csv import DictReader
from pathlib import Path

from django.test import SimpleTestCase

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from process_specimen_csv import process_specimens  # noqa: E402

_HEADER = (
    "UNIQUEID,HYPOCODE,taxon ID,inst ID,CATNUM,MASS,LOC ID,sex,"
    "Fossil,captive,TYPE,COMMENTS"
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
        f"{uid},{hypo},{taxon},{inst},{catnum},{mass},{loc},{sex},"
        f"{fossil},{captive},{typ},{comments}"
    )


def _run(csv_content: str) -> tuple[list[dict], str]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        tmp = f.name
    out = io.StringIO()
    err = io.StringIO()
    process_specimens(tmp, out, err)
    out.seek(0)
    rows = list(DictReader(out))
    return rows, err.getvalue()


class ProcessSpecimenCsvTest(SimpleTestCase):
    def test_valid_row_written(self) -> None:
        rows, errors = _run(_make_csv(_blank_row()))
        self.assertEqual(len(rows), 1)
        self.assertEqual(errors, "")

    def test_output_header_fields(self) -> None:
        rows, _ = _run(_make_csv(_blank_row()))
        self.assertEqual(
            set(rows[0].keys()),
            {
                "id",
                "hypocode",
                "taxon_id",
                "institute_id",
                "catalog_number",
                "mass",
                "locality_id",
                "sex_id",
                "fossil_id",
                "captive_id",
                "taxonomic_type_id",
                "comments",
            },
        )

    def test_fossil_f_maps_to_1(self) -> None:
        rows, errors = _run(_make_csv(_blank_row(fossil="F")))
        self.assertEqual(rows[0]["fossil_id"], "1")
        self.assertEqual(errors, "")

    def test_fossil_e_maps_to_2(self) -> None:
        rows, errors = _run(_make_csv(_blank_row(fossil="E")))
        self.assertEqual(rows[0]["fossil_id"], "2")
        self.assertEqual(errors, "")

    def test_fossil_blank_maps_to_9(self) -> None:
        rows, errors = _run(_make_csv(_blank_row(fossil="")))
        self.assertEqual(rows[0]["fossil_id"], "9")
        self.assertEqual(errors, "")

    def test_fossil_invalid_writes_error_and_defaults_to_9(self) -> None:
        rows, errors = _run(_make_csv(_blank_row(fossil="X")))
        self.assertEqual(rows[0]["fossil_id"], "9")
        self.assertIn("incorrect fossil type", errors)

    def test_captive_letter_codes_mapped(self) -> None:
        for code, expected in [
            ("C", "1"),
            ("W", "2"),
            ("P", "3"),
            ("C?", "3"),
            ("U", "9"),
        ]:
            rows, errors = _run(_make_csv(_blank_row(captive=code)))
            self.assertEqual(rows[0]["captive_id"], expected, f"captive={code}")
            self.assertEqual(errors, "")

    def test_captive_blank_defaults_to_9(self) -> None:
        rows, errors = _run(_make_csv(_blank_row(captive="")))
        self.assertEqual(rows[0]["captive_id"], "9")
        self.assertEqual(errors, "")

    def test_captive_invalid_writes_error_and_defaults_to_9(self) -> None:
        rows, errors = _run(_make_csv(_blank_row(captive="Z")))
        self.assertEqual(rows[0]["captive_id"], "9")
        self.assertIn("incorrect captive value", errors)

    def test_taxonomic_type_letter_codes_mapped(self) -> None:
        for code, expected in [
            ("H", "1"),
            ("L", "2"),
            ("S", "3"),
            ("N", "4"),
            ("FN", "5"),
            ("FL", "6"),
            ("1", "1"),
            ("6", "6"),
        ]:
            rows, errors = _run(_make_csv(_blank_row(typ=code)))
            self.assertEqual(rows[0]["taxonomic_type_id"], expected, f"type={code}")
            self.assertEqual(errors, "")

    def test_taxonomic_type_blank_defaults_to_7(self) -> None:
        rows, _ = _run(_make_csv(_blank_row(typ="")))
        self.assertEqual(rows[0]["taxonomic_type_id"], "7")

    def test_taxonomic_type_invalid_writes_error_and_defaults_to_7(self) -> None:
        rows, errors = _run(_make_csv(_blank_row(typ="ZZZ")))
        self.assertEqual(rows[0]["taxonomic_type_id"], "7")
        self.assertIn("incorrect taxonomic type", errors)

    def test_mass_blank_defaults_to_0(self) -> None:
        rows, _ = _run(_make_csv(_blank_row(mass="")))
        self.assertEqual(rows[0]["mass"], "0")

    def test_locality_blank_defaults_to_10000(self) -> None:
        rows, _ = _run(_make_csv(_blank_row(loc="")))
        self.assertEqual(rows[0]["locality_id"], "10000")

    def test_sex_invalid_writes_error_but_row_still_written(self) -> None:
        rows, errors = _run(_make_csv(_blank_row(sex="X")))
        self.assertEqual(len(rows), 1)
        self.assertIn("incorrect sex", errors)

    def test_sex_blank_writes_error_but_row_still_written(self) -> None:
        rows, errors = _run(_make_csv(_blank_row(sex="")))
        self.assertEqual(len(rows), 1)
        self.assertIn("missing sex", errors)

    def test_duplicate_hypo_uid_skipped_with_error(self) -> None:
        rows, errors = _run(
            _make_csv(
                _blank_row(uid="1001", hypo="ABC001"),
                _blank_row(uid="1001", hypo="ABC001"),
            )
        )
        self.assertEqual(len(rows), 1)
        self.assertIn("Repeated specimen", errors)

    def test_same_uid_different_hypo_both_written(self) -> None:
        rows, errors = _run(
            _make_csv(
                _blank_row(uid="1001", hypo="ABC001"),
                _blank_row(uid="1001", hypo="XYZ999"),
            )
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(errors, "")

    def test_multiple_valid_rows(self) -> None:
        rows, errors = _run(_make_csv(_blank_row(uid="1001"), _blank_row(uid="1002")))
        self.assertEqual(len(rows), 2)
        self.assertEqual(errors, "")

    def test_returns_count(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(_make_csv(_blank_row(uid="1001"), _blank_row(uid="1002")))
            tmp = f.name
        count = process_specimens(tmp, io.StringIO(), io.StringIO())
        self.assertEqual(count, 2)

    def test_comments_quotes_escaped(self) -> None:
        rows, _ = _run(_make_csv(_blank_row(comments='say "hello"')))
        self.assertIn('""hello""', rows[0]["comments"])

    def test_bom_stripped(self) -> None:
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as f:
            f.write(("﻿" + _make_csv(_blank_row())).encode("utf-8"))
            tmp = f.name
        out = io.StringIO()
        err = io.StringIO()
        process_specimens(tmp, out, err)
        out.seek(0)
        rows = list(DictReader(out))
        self.assertEqual(len(rows), 1)
        self.assertEqual(err.getvalue(), "")
