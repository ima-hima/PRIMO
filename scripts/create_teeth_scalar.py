"""
Script to build the scalar & session tables from Eric's teeth table
By: Katherine St. John
Date: July 2006

Modified April 2007 to include standard fields for the session table.

Edited and ported to Python by Eric Ford January 2023

Session table: from the teeth table, grab the hyponum (column C)
and the observer (F), and make a list (without duplicates).
Then, print out the session table:

uniqueid,observer,specimen,5,1,y,,teeth,9

where observer and specimen are C and F from above,
the uniqueid is generated on the fly when printing out the table, and
the following values are hard-coded:
  protocol_id 5
  iteratio 1
  dfltsess y
  comments <empty>
  filename teeth
  createby 9

Scalar table: first generate a lookup table with the name of the
variables based on the type of tooth. For example,
if the tooth is 02UPR, then the J column holds the variable UP4WG,
if the tooth is 03UM1, then the J column holds the variable UM1WS.

Next, process each row from the file:
1. Find the type of tooth (column A).
2. Find the session's uniqueid (from column F & C, and session
   table above).
3. For each non-empty entry, find the variable's name (from type in
   column A and lookup table) to associate with the value.
4. Creating a uniqueid and printing out for the scalar table:
   uniqueid,sessionid,variableName,value


Usage:

   teeth2scalar inputFile outSessionFile outScalarFile

where the inputFile is a CSV teeth excel database and
the output files are CSV file to be read into the primo
database.
"""

import argparse
import os
from collections import defaultdict
from csv import DictReader
from pathlib import Path
from typing import Any, TextIO

import variables as v


def process_teeth(
    teeth_path: str,
    session_out: TextIO,
    scalar_out: TextIO,
    error_out: TextIO,
    verbose: int = 0,
) -> None:
    """Read a teeth CSV and write session and scalar output CSVs."""
    entries: defaultdict[Any, Any] = defaultdict(dict)
    comments: defaultdict[Any, str] = defaultdict(str)

    with open(teeth_path, "r") as f:
        rows = DictReader(f, fieldnames=v.field_names, delimiter=",", quotechar='"')

        scalar_out.write("id,session_id,variable_id,value\n")
        for i in range(7):
            next(rows)
        session_id = 0
        prev_session_id = 0
        cur_uid: Any = -1
        cur_observer: Any = -1
        duplicate_teeth: set = set()
        for row in rows:
            if verbose > 3:
                print(f"line: {row}")
                print(f"\t {row['group_id']}, {row['hypocode']}")
            unique_id = row["uid"]
            if not unique_id:
                if not row["hypocode"] and not row["tooth"]:
                    # Mostly Excel adding blank rows at the end.
                    continue
                error_out.write(f"unique_id missing: {row}\n")
            if unique_id != cur_uid:
                cur_uid = unique_id
                prev_session_id = session_id
                session_id += 1
                entries[unique_id]["session"] = session_id
            elif prev_session_id == session_id and cur_observer != row["observer"]:
                error_out.write(
                    "Warning: observer changed but session didn't: "
                    f"unique_id: {row['uid']} hypocode: {row['hypocode']}\n"
                )
            cur_observer = row["observer"]
            entries[unique_id]["hypocode"] = row["hypocode"]
            entries[unique_id]["group_id"] = row["group_id"]
            entries[unique_id]["observer"] = row["observer"]
            if "comments" not in entries[unique_id]:
                entries[unique_id]["comments"] = ""
            if row["comments"]:
                entries[unique_id]["comments"] += row["comments"]
            if row["cast"] == "cast":
                entries[unique_id]["original"] = 2
            else:
                entries[unique_id]["original"] = 1
            if "values" not in entries[unique_id]:
                entries[unique_id]["values"] = {}
            tooth_name = row["tooth"].strip()
            if tooth_name.endswith("X"):
                unknown_teeth(tooth_name, unique_id, row, entries, error_out)
            for num in range(1, 22):
                value = f"m{num}"
                if row[value]:
                    try:
                        variable_name = v.variable_names[tooth_name][num]
                    except Exception as e:
                        error_out.write(
                            f"Incorrect tooth name? unique_id: {unique_id} "
                            f"hypocode: {row['hypocode']} tooth: {e}\n"
                        )
                        break
                    if variable_name:
                        var_id = v.variable_ids[variable_name]
                        if variable_name in entries[unique_id]["values"]:
                            duplicate_teeth.add(unique_id)
                        scalar_out.write(
                            f"{unique_id},{session_id},{var_id},{row[value]}\n"
                        )
                        entries[unique_id]["values"][variable_name] = row[value]
                    else:
                        error_out.write(
                            "Warning: data entry with a value where "
                            "there shouldn't be one.\n"
                            f"    unique_id: {row['uid']} hypocode: {row['hypocode']} "
                            f"tooth: {row['tooth']}"
                            f"    value: {row[value]}\n"
                        )
        if duplicate_teeth:
            count = len(duplicate_teeth)
            error_out.write(
                f"Error: the {count} following teeth have duplicate lines:\n"
            )
            for tooth in sorted(duplicate_teeth):
                error_out.write(f" {tooth}\n")

    session_out.write(
        "id,observer_id,group_id,specimen_id,"
        "original_id,protocol_id,comments,filename\n"
    )
    for uid in sorted(entries.keys()):
        if verbose > 2:
            try:
                print(
                    f"{entries[uid]['hypocode']} group {entries[uid]['group_id']} "
                    f"has {len(entries[uid]['values'])} measurements and is "
                    f"assigned the uniqueid {uid}."
                )
            except Exception as e:
                print(f"{e}, {uid}\n")
        session_out.write(
            f"{entries[uid]['session']},"
            f"{entries[uid]['observer']},"
            f"{entries[uid]['group_id']},"
            f"{uid},"
            f"{entries[uid]['original']},"
            "5,"
            f"{comments[uid]},"
            "teeth\n"
        )
        for variable_name in entries[uid]["values"]:
            scalar_out.write(
                f"{uid},"
                f"{entries[uid]['session']},"
                f"{v.variable_ids[variable_name]},"
                f"{entries[uid]['values'][variable_name]}\n"
            )


def unknown_teeth(
    tooth_name: str, unique_id: str, row: dict, entries: dict, error_out: TextIO
) -> None:
    """
    Deal with teeth whose position is unknown, but have good guesses.
    Errors with missing values are considered the same as "position
    uncertain," as are 0s, which we assume are mistyped.
    Other values we code as "position uncertain" but kick out an error.
    """
    if tooth_name.endswith("UMX"):
        try:
            entries[unique_id]["comments"] += f" {v.UMXTOOTH[row['xtooth']]}"
        except Exception as e:
            if str(e) != "''" and str(e) != "'0'":
                error_out.write(
                    f"Warning: UMXTOOTH with incorrect value, {e}, "
                    f"in XTOOTH column. unique id: {unique_id}. "
                    'A value of "upper molar position uncertain" was output.\n'
                )
            entries[unique_id]["comments"] += f" {v.UMXTOOTH['9']}"
    elif tooth_name.endswith("UPX"):
        try:
            entries[unique_id]["comments"] += f" {v.UPXTOOTH[row['xtooth']]}"
        except Exception as e:
            if str(e) != "''" and str(e) != "'0'":
                error_out.write(
                    f"Warning: UPXTOOTH with incorrect value, {e}, "
                    f"in XTOOTH column. unique id: {unique_id}. "
                    'A value of "upper premolar position uncertain" was output.\n'
                )
            entries[unique_id]["comments"] += f" {v.UPXTOOTH['9']}"
    elif tooth_name.endswith("LMX"):
        try:
            entries[unique_id]["comments"] += f" {v.LMXTOOTH[row['xtooth']]}"
        except Exception as e:
            if str(e) != "''" and str(e) != "'0'":
                error_out.write(
                    f"Warning: LMXTOOTH with incorrect value, {e}, "
                    f"in XTOOTH column. unique id: {unique_id}. "
                    'A value of "lower molar position uncertain" was output.\n'
                )
            entries[unique_id]["comments"] += f" {v.LMXTOOTH['9']}"


def main() -> None:
    data_path = Path("csvs")
    try:
        os.mkdir(data_path)
    except FileExistsError:
        pass
    with open(data_path / args["sess"], "w") as session_out, open(
        data_path / args["scalar"], "w"
    ) as scalar_out, open(data_path / "teeth_scalar_errors.txt", "w") as error_out:
        process_teeth(
            args["teeth"], session_out, scalar_out, error_out, args["verbose"]
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Produce session and scalar csv files from teeth csv."
    )
    parser.add_argument(
        "--teeth",
        metavar="teeth_input_file",
        type=str,
        help="the name of the input file",
        required=True,
    )
    parser.add_argument(
        "--sess",
        metavar="session_output_file",
        type=str,
        help="the name of the session output file",
        required=True,
    )
    parser.add_argument(
        "--scalar",
        metavar="scalar_output_file",
        type=str,
        help="the name of the scalar output file",
        required=True,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="Repeat up to 3 v's. More v's -> more verbose output",
        action="count",
        default=0,
    )

    args = vars(parser.parse_args())
    main()
