"""
Process a specimen CSV and write a cleaned CSV ready for DB import.

Input CSV columns (case-sensitive):
  UNIQUEID, HYPOCODE, taxon ID, inst ID, CATNUM, MASS,
  LOC ID, sex, Fossil, captive, TYPE, COMMENTS

Output CSV columns (matching specimen table):
  id, hypocode, taxon_id, institute_id, catalog_number, mass,
  locality_id, sex_id, fossil_id, captive_id, taxonomic_type_id, comments

Usage:
  python process_specimen_csv.py --in specimen.csv --out specimen_import.csv
"""

import argparse
from csv import DictReader, DictWriter
from typing import TextIO

_TYPE_LOOKUP = {
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "H": "1",
    "L": "2",
    "S": "3",
    "N": "4",
    "FN": "5",
    "FL": "6",
}
_CAPTIVE_LOOKUP = {"C": "1", "W": "2", "P": "3", "C?": "3", "U": "9"}
_VALID_SEX = {"1", "2", "3", "4", "5", "6", "9"}
_OUT_FIELDS = [
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
]


def process_specimens(in_path: str, out: TextIO, error_out: TextIO) -> int:
    """
    Read specimen CSV at in_path, write cleaned rows to out.
    Returns the number of specimens written.
    """
    seen: set[tuple[str, str]] = set()
    writer = DictWriter(out, fieldnames=_OUT_FIELDS)
    writer.writeheader()
    count = 0

    with open(in_path, encoding="utf-8-sig") as f:
        for row in DictReader(f):
            uid = row["UNIQUEID"]
            hypo = row["HYPOCODE"]
            key = (hypo, uid)
            if key in seen:
                error_out.write(f"Repeated specimen: {uid}\n")
                continue
            seen.add(key)

            fossil = row["Fossil"]
            if fossil == "F":
                fossil = "1"
            elif fossil == "E":
                fossil = "2"
            elif fossil == "":
                fossil = "9"
            else:
                error_out.write(f"Specimen {uid} has incorrect fossil type: {fossil}\n")
                fossil = "9"

            sex = row["sex"]
            if sex not in _VALID_SEX:
                if sex == "":
                    error_out.write(f"Specimen {uid} missing sex\n")
                else:
                    error_out.write(f"Specimen {uid} has incorrect sex: {sex}\n")

            mass = row["MASS"] or "0"

            taxonomic_type = row["TYPE"].strip().upper()
            if taxonomic_type and taxonomic_type not in _TYPE_LOOKUP:
                error_out.write(
                    f"Specimen {uid} has incorrect taxonomic type: "
                    f"{taxonomic_type}\n"
                )
                taxonomic_type = ""
            elif taxonomic_type:
                taxonomic_type = _TYPE_LOOKUP[taxonomic_type]

            locality_id = row["LOC ID"] or "10000"

            captive = row["captive"].upper()
            if captive in _CAPTIVE_LOOKUP:
                captive = _CAPTIVE_LOOKUP[captive]
            elif captive == "":
                captive = "9"
            else:
                error_out.write(
                    f"Specimen {uid} has incorrect captive value: " f"{captive}\n"
                )
                captive = "9"

            comments = row["COMMENTS"].replace('"', '""')

            writer.writerow(
                {
                    "id": uid,
                    "hypocode": hypo,
                    "taxon_id": row["taxon ID"],
                    "institute_id": row["inst ID"],
                    "catalog_number": row["CATNUM"],
                    "mass": mass,
                    "locality_id": locality_id,
                    "sex_id": sex,
                    "fossil_id": fossil,
                    "captive_id": captive,
                    "taxonomic_type_id": taxonomic_type or "7",
                    "comments": comments,
                }
            )
            count += 1

    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean a specimen CSV for DB import.")
    parser.add_argument("--in", dest="infile", required=True, help="input specimen CSV")
    parser.add_argument(
        "--out", dest="outfile", required=True, help="output specimen CSV"
    )
    args = parser.parse_args()

    import sys

    with open(args.outfile, "w", newline="") as out:
        count = process_specimens(args.infile, out, sys.stderr)
    print(f"{count} specimens written to {args.outfile}")


if __name__ == "__main__":
    main()
