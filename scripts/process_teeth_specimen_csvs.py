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
import subprocess
from collections import defaultdict
from csv import DictReader
from io import TextIOBase
from pathlib import Path
from typing import Any

import variables as v


def process_specimens(
    specimen_inname: str, specimen_outname: str, error_out: TextIOBase
) -> dict:

    type_lookup = {
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
    captive_lookup = {"C": "1", "W": "2", "P": "3", "C?": "3", "U": "9"}
    sex_lookup = {"1", "2", "3", "4", "5", "6", "9"}

    specimen_id = 0
    try:
        os.mkdir(data_path)
    except FileExistsError:
        pass
    with open(specimen_inname, mode="r", encoding="utf-8-sig") as infile, open(
        specimen_outname, "w"
    ) as outfile:
        count = 0
        rows = DictReader(infile, delimiter=",", quotechar='"')
        outfile.write(
            "id,hypocode,taxon_id,institute_id,catalog_number,mass,locality_id,sex_id,"
            "age_class_id,fossil_id,captive_id,taxonomic_type_id,comments\n"
        )
        specimen_list = dict()
        for row in rows:
            # Write error and skip if specimen is dupe.
            if (row["HYPOCODE"], row["UNIQUEID"]) in specimen_list:
                error_out.write(f"Repeated specimen: {row['UNIQUEID']}\n")
                continue
            count += 1
            specimen_list[(row["HYPOCODE"], row["UNIQUEID"])] = specimen_id
            specimen_id += 1

            # Now, do lookup and replacements
            if row["Fossil"] == "F":
                row["Fossil"] = 1
            elif row["Fossil"] == "E":
                row["Fossil"] = 2
            elif row["Fossil"] == "":
                row["Fossil"] = 9
            else:
                error_out.write(
                    f"Specimen {row['UNIQUEID']} has incorrect fossil type: "
                    f"{row['Fossil']}\n"
                )

            if row["sex"] not in sex_lookup:
                if row["sex"] == "":
                    error_out.write(f"Specimen {row['UNIQUEID']} missing sex\n")
                else:
                    error_out.write(
                        f"Specimen {row['UNIQUEID']} has incorrect sex: {row['sex']}\n"
                    )

            if row["MASS"] == "":
                row["MASS"] = 0
            # if row["TYPE"] != "":
            #     print("before", row["TYPE"])
            row["TYPE"] = row["TYPE"].strip().upper()
            # if row["TYPE"] != "":
            #     print("after", row["TYPE"], type_lookup[row["TYPE"]])
            if (
                row["TYPE"] not in type_lookup and row["TYPE"] != ""
            ):  # Note that blank is the default.
                error_out.write(
                    f"Specimen {row['UNIQUEID']} has incorrect taxonomic type: "
                    f"{row['TYPE']}\n"
                )
            elif row["TYPE"] != "":
                row["TYPE"] = type_lookup[row["TYPE"]]
            if row["TYPE"] != "":
                print("after", row["TYPE"], type_lookup[row["TYPE"]])
            if row["LOC ID"] == "":
                row["LOC ID"] = "10000"
            row["captive"] = row["captive"].upper()
            if row["captive"] not in captive_lookup:
                if row["captive"] != "":
                    error_out.write(
                        f"Specimen {row['UNIQUEID']} has incorrect captive value: "
                        f"{row['captive']}\n"
                    )
                else:
                    row["captive"] = "9"
            else:
                row["captive"] = captive_lookup[row["captive"]]
            row["COMMENTS"] = row["COMMENTS"].replace('"', '""')
            print(
                f"{row['UNIQUEID']},"
                f"{row['HYPOCODE']},"
                f"{row['taxon ID']},"
                f"{row['inst ID']},"
                f"{row['CATNUM']},"
                f"{row['MASS']},"
                f"{row['LOC ID']},"
                f"{row['sex']},"
                f"{row['Fossil']},"
                f"{row['captive']},"
                f"{row['TYPE']},"
                f"\"{row['COMMENTS']}\""
                "\n"
            )
            outfile.write(
                f"{row['UNIQUEID']},"
                f"{row['HYPOCODE']},"
                f"{row['taxon ID']},"
                f"{row['inst ID']},"
                f"{row['MASS']},"
                f"{row['LOC ID']},"
                f"{row['sex']},"
                f"{row['Fossil']},"
                f"{row['captive']},"
                f"{row['TYPE']},"
                f"\"{row['COMMENTS']}\""
                "\n"
            )

        print(f"{count} specimens were processed.")

        return specimen_list


def process_teeth(
    specimen_list: dict, teethfile: str, sessionfile: str, scalarfile: str
) -> None:
    entries: defaultdict[Any, Any] = defaultdict(dict)
    comments: defaultdict[Any, str] = defaultdict(str)
    missing_specimens: set = set()

    # Open files for reading and writing.
    with open(teethfile, "r") as f, open(sessionfile, "w") as session_out, open(
        scalarfile, "w"
    ) as scalar_out:
        # Throw away six lines (they're the ones with the header info).
        # Will want to comment these lines out for input files without a header lines.
        rows = DictReader(f, fieldnames=v.field_names, delimiter=",", quotechar='"')

        scalar_out.write("id,session_id,variable_id,value\n")
        for i in range(7):
            row = next(rows)
        session_id = 0
        prev_session_id = 0
        cur_uid: Any = -1
        cur_observer: Any = -1
        duplicate_teeth = set()
        for row in rows:
            if args["verbose"] > 3:
                print(f"line: {row}")
                print(f"\t {row['group_id']}, {row['hypocode']}")
            unique_id = row["uid"]
            lookup_tuple = (row["hypocode"], row["uid"])
            if lookup_tuple not in specimen_list and (row["hypocode"], row["uid"]):
                if lookup_tuple not in missing_specimens:
                    error_out.write(
                        f"The hypocode/unique ID pair ({row['hypocode']}:{row['uid']})"
                        " does not exist in the specimen file.\n"
                    )
                    missing_specimens.add(lookup_tuple)
                continue

            if not unique_id:
                if not row["hypocode"] and not row["tooth"]:
                    # This is mostly stupid Excel adding blank rows at the end.
                    # Assume if hypocode, unique id and tooth all missing that
                    # it's MS. Otherwise, output an error.
                    continue
                error_out.write(f"unique_id missing: {row}\n")
            if unique_id != cur_uid:
                # Every time there's a new specimen there's also a new session.
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
            # We made need to concat multiple comments for the same specimen/session.
            if "comments" not in entries[unique_id]:
                entries[unique_id]["comments"] = ""
            if row["comments"]:
                entries[unique_id]["comments"] += row["comments"]
            if row["cast"] == "cast":
                # Casts are 2 and originals are 1.
                entries[unique_id]["original"] = 2
            else:
                entries[unique_id]["original"] = 1
            if "values" not in entries[unique_id]:
                entries[unique_id]["values"] = {}
            tooth_name = row["tooth"].strip()
            # Note that teeth with unknown positions end in X, e.g. UMX, UPX.
            if tooth_name.endswith("X"):
                unknown_teeth(tooth_name, unique_id, row, entries, error_out)
            for num in range(1, 22):
                value = f"m{num}"
                if row[value]:
                    try:
                        variable_name = v.variable_names[tooth_name][num]
                    except Exception as e:
                        error_out.write(
                            f"Incorrect tooth name? unique_id: {row['uid']} "
                            f"hypocode: {row['hypocode']} tooth: {e}\n"
                        )
                        break
                    if variable_name:
                        # Look up variable ID.
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
            error_out.write(
                f"Error: the {len(duplicate_teeth)} following teeth have "
                "duplicate lines:\n"
            )
            for tooth in sorted(duplicate_teeth):
                error_out.write(f" {tooth}\n")
        # Print out (one occurrence of each "hyponum,observer") info to session file:
        session_out.write(
            "id,observer_id,group_id,specimen_id,original_id,protocol_id,"
            "comments,filename\n"
        )
        # scalar_out.write("id,session_id,variable_id,value\n")
        for uid in sorted(entries.keys()):
            if args["verbose"] > 2:
                try:
                    print(
                        f"{entries[uid]['hypocode']} group {entries[uid]['group_id']} "
                        f"has {len(entries[uid]['values'])} measurements and is "
                        f"assigned the uniqueid {uid}."
                    )
                except Exception as e:
                    print(f"{e}, {uid}\n")
            # Set up a hash for the session data, to be used to build the scalar table.
            # session[uid] = uid
            session_out.write(
                f"{entries[uid]['session']},"
                f"{entries[uid]['observer']},"
                f"{entries[uid]['group_id']},"
                f"{uid},"  # specimen id
                f"{entries[uid]['original']},"
                "5,"  # protocol id
                f"{comments[uid]},"
                f"teeth"  # file name
                # f"{entries[uid]['group_id']}\n"
                "\n"
            )
            for variable_name in entries[uid]["values"]:
                scalar_out.write(
                    f"{uid},"
                    f"{entries[uid]['session']},"
                    f"{v.variable_ids[variable_name]},"
                    f"{entries[uid]['values'][variable_name]}"  # value
                    "\n"
                )


def unknown_teeth(
    tooth_name: str, unique_id: str, row: dict, entries: dict, error_out: TextIOBase
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
            if args["verbose"] > 2:
                print(
                    f"Added comment to {unique_id}: " f'"{v.UMXTOOTH[row["xtooth"]]}"'
                )
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
            if args["verbose"] > 2:
                print(
                    f"Added comment to {unique_id}: " f'"{v.UPXTOOTH[row["xtooth"]]}"'
                )
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
            if args["verbose"] > 2:
                print(
                    f"Added comment to {unique_id}: " f'"{v.LMXTOOTH[row["xtooth"]]}"'
                )
        except Exception as e:
            if str(e) != "''" and str(e) != "'0'":
                error_out.write(
                    f"Warning: LMXTOOTH with incorrect value, {e}, "
                    f"in XTOOTH column. unique id: {unique_id}. "
                    'A value of "lower molar position uncertain" was output.\n'
                )
            entries[unique_id]["comments"] += f" {v.LMXTOOTH['9']}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Produce specimen, session, and scalar csv files "
            "from specimen and tooth csvs."
        )
    )
    parser.add_argument(
        "--teeth",
        metavar="teeth-in-file",
        type=str,
        help="the name of the input file",
        required=True,
    )
    parser.add_argument(
        "--sess",
        metavar="session-out-file",
        type=str,
        help="the name of the session output file",
        required=True,
    )
    parser.add_argument(
        "--scalar",
        metavar="scalar-out-file",
        type=str,
        help="the name of the scalar output file",
        required=True,
    )
    parser.add_argument(
        "--specimen_in",
        metavar="specimen_infile",
        type=str,
        help="the name of the specimen input file",
        required=True,
    )
    parser.add_argument(
        "--specimen_out",
        metavar="specimen_outfile",
        type=str,
        help="the name of the speciment output file",
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
    data_path = Path("csvs")
    try:
        os.mkdir(data_path)
    except FileExistsError:
        pass
    specimen_outname = data_path / args["specimen_out"]
    teethfile = data_path / args["teeth"]
    sessionfile = data_path / args["sess"]
    scalarfile = data_path / args["scalar"]
    errorfilename = data_path / "errors.txt"
    with open(errorfilename, "w") as error_out:
        specimen_list = process_specimens(
            args["specimen_in"], specimen_outname, error_out
        )
        process_teeth(specimen_list, teethfile, sessionfile, scalarfile)
    subprocess.run(["open", errorfilename], check=True)
