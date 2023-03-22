#! /usr/bin/env python3

import mysql.connector
import subprocess
import xlrd
import os
import re

# constants
line = ""
landmarks = [
    "IN",
    "BR",
    "GL",
    "NA",
    "RH",
    "NS",
    "PR",
    "R_PR2",
    "R_PMS",
    "R_ZMI",
    "R_ZMU",
    "R_DA",
    "R_MTI",
    "R_MTS",
    "R_FMO",
    "R_FMT",
    "R_PO",
    "R_ZTS",
    "L_PR2",
    "L_PMS",
    "L_ZMI",
    "L_ZMU",
    "L_DA",
    "L_MTI",
    "L_MTS",
    "L_FMO",
    "L_FMT",
    "L_PO",
    "L_ZTS",
    "OP",
    "BA",
    "ST",
    "IV",
    "R_PG",
    "R_ZTI",
    "R_M3D",
    "R_M12",
    "R_MP3",
    "R_PMI",
    "L_PG",
    "L_ZTI",
    "L_M3D",
    "L_M12",
    "L_MP3",
    "L_PMI",
    "GLRH",
    "NOSE",
    "NASP-PR",
    "R-PM/MAX",
    "L-PM/MAX",
    "ROSTRUM",
    "SUPORB",
    "RORBIT",
    "LORBIT",
    "RTEMFOS",
    "LTEMFOS",
    "RZYGINF",
    "LZYGINF",
    "R-ALV",
    "L-ALV",
]
fileName = (
    "/Volumes/files/business/NYCEP/3D/first batch to process/to_resample/an1msc.prn"
)
session_id = 20001 # First session id, it iterates on each file.
data_id = 1 # I can start at 1 for now, because 3D is its own table.
"""
protocol_id == 1 for now; later I'll have to deal with this varying somehow, maybe
through input arguments. dunno. Variance in this variable will cause trouble,
because there will be more landmarks in those cases.
"""
protocol_id = 1
observer_id = 0 # This gets set based on the last two letters of the file name.
"""
observer_inits is the last two letters of the file name, or possibly comes from
a lookup table: %observers.
"""
observer_inits = 0
original_id = 1 # For now; this they'll attempt to change later.
dfltsess = "y" # This is default session.
iteratio = 1 # I should probably ask about this.
comments = "" # Has to be global because Spreadsheet::ParseExcel worksheet->get_cell() kept failing.
# $filename = '3D cranium'; # this gets replaced by the name of the prn file
group_id = 2

resample = {
    "GLRH": 16,
    "NOSE": 17,
    "NASP-PR": 4,
    "R-PM/MAX": 11,
    "L-PM/MAX": 11,
    "ROSTRUM": 23,
    "SUPORB": 20,
    "RORBIT": 13,
    "LORBIT": 13,
    "RTEMFOS": 10,
    "LTEMFOS": 10,
    "RZYGINF": 9,
    "LZYGINF": 9,
    "R-ALV": 10,
    "L-ALV": 10,
}  # these are the lengths of the lines

observers = {
    "stv": 1,
    "srf": 1,
    "z": 2,
    "pwl": 3,
    "mam": 4,
    "cms": 5,
    "ams": 6,
    "ajt": 7,
    "tosi": 7,
    "tos": 7,
    "wjw": 8,
    "bjw": 8,
    "dpr": 14,
    "wke": 16,
    "mgl": 20,
    "whs": 25,
    "kns": 50,
    "msc": 6,
}  # because some observers have multiple sets of initials

inDir = os.getcwd() + "/OWM_prn/Prnfiles/"
resampleControl = (
    os.getcwd() + "/resample_control.txt"
)  # lengths of resampled lines are in this file
excelDir = os.getcwd() + "/XLS--all/"
toResample = "/Users/eric/Desktop/to_resample/"
intermediateDir = "/Users/eric/Desktop/process_before_dvlr/"
toDVLR = "/Users/eric/Desktop/to_dvlr/"
DVLRed = "/Users/eric/Desktop/done/"
csvs = "/Users/eric/Desktop/csvs/"
path_to_catalog_no_lookup = os.getcwd() + "/Microscribe catalog.csv"
catalog_nos = {}
excel_files = {}

errorout = open(csvs + "errors.txt", "w")
warnout = open(csvs + "warnings.txt", "w")
sessout = open(csvs + "3Dsess.csv", "w")
print(
    (
        "id, observer_id, specimen_id, protocol_id, original_id, iteratio, dfltsess, "
        "comments, filename, group_id, created_by, created_at, updatedby, updated_at"
    ),
    file=sessout,
)

dataout = open(csvs + "3Ddata.csv", "w")
print(
    "id, session_id, variable_id, datindex, x, y, z, createby, created_at, updateby, updated_at",
    file=dataout,
)


infile = open(path_to_catalog_no_lookup, "r")
line = infile.readline()
for line in infile:
    input = line.split(",")
    input[11] = input[11].strip()  # $input[11] =~ s{\A\s*|\s*\z}{}gmsx;
    input[8] = input[8].strip()
    input[12] = input[12].strip()
    # print( input[16].lower() )
    """
    Following was originally 15 => 7, not 16 => 7. That was causing problems with prns
    that didn't have an associated xls. Now it's indexed by the prn name, which
    may or may not cause unforseen problems.
    """
    catalog_nos[input[16].lower()] = input[7]
    excel_files[input[16].lower()] = input[15]

infile.close()

for root, dirs, files in os.walk(inDir):
    for file in files:
        try:
            # Read first line of file to get institution, observer and
            # double-check file name.
            error = "unknown: " + file
            if file[0] == ".":
                continue
            file = file[:-4]  # to strip off suffix
            infile = open(inDir + file + ".prn", "r")
            line = infile.readline().rstrip()
            institution = line[:11].rstrip()
            # print( 'Institution: ' + institution + "\n" )
            origCatNo = line[11:22].rstrip()
            # print( 'Original Catalog number: ' + origCatNo + "\n")
            if len(line) < 24:
                raise Exception("prn file " + file + " missing excel file name")
            fileName = re.sub(r"(.*?)\..*", r"\1", line[22:])

            try:
                catNo = catalog_nos[fileName.lower()]
            except:
                catNo = None
                try:
                    catNo = catalog_nos[excel_files[fileName.lower()]]
                except:
                    try:
                        catNo = catalog_nos[file.lower()]
                    except:
                        try:
                            catNo = catalog_nos[excel_files[file.lower()]]
                        except:
                            try:
                                """
                                here I fall back to the number from the file.
                                I don't remember why I didn't do this originally,
                                so hopefully this won't cause a problem.
                                """
                                catNo = origCatNo
                            except:
                                raise Exception(
                                    "Reading from prn file "
                                    + file
                                    + ", Excel file "
                                    + fileName
                                    + " does not exist in Microscribe catalog.xls"
                                )
        except Exception as error:
            errorout.write(error + "\n")
        # print("computed file & catNo:", file, catNo )

        observer_inits = re.sub(r".*?\d+([a-zA-Z]*).*", r"\1", fileName.lower())
        if observer_inits == "":
            observer_inits = re.sub(r".*?\d+([a-zA-Z]*).*", r"\1", file.lower())
        # print( fileName, file, observer_inits )

        file = re.sub(r"(.*)\..*", r"\1", file)

        # warn if file names don't match
        if file.lower() != fileName.lower():
            warnout.write(
                "\tWarning: name found in file ("
                + fileName
                + ") doesn't match name of file ("
                + file
                + ")\n"
            )

        print(file)
        ### now get info needed from db ###
        config = {
            "user": "root",
            "password": "jg54wmv",
            "host": "127.0.0.1",
            "database": "nyceporg_primo2",
            "raise_on_warnings": True,
        }

        try:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()

            if catNo[0] == '"':
                catNo = catNo[1:-1]
            catNo = re.sub(r'"""', r'"', catNo)  # because of the way Excel exports
            catNo = re.sub(r'""', r'"', catNo)  # double quotes in csvs.
            # and finally, to get rid of quotes around entry, should they still exist
            catNo = re.sub(r'"', r"\"", catNo)  # now, escape quotes

            query = (
                'SELECT id, institut_id FROM `specimen` WHERE catlogno LIKE "'
                + str(catNo)
                + '"'
            )
            cursor.execute(query, (catNo))
            for (id1, id2) in cursor:
                specimen_id = id1
                inst_id = id2
            if len(observer_inits) != 2:
                observer_id = observers[observer_inits]
            else:
                query = (
                    "SELECT id FROM `observer` WHERE initials LIKE "
                    + '"'
                    + observer_inits
                    + '"'
                )
                cursor.execute(query, (observer_inits))
                for id1 in cursor:
                    observer_id = id1[0]
            # print( "got values", catNo, specimen_id, inst_id, observer_id )
            if observer_id == "" or catNo == "":
                raise Exception(
                    "File "
                    + file
                    + "\tObserver "
                    + observer_id
                    + " or catNo: "
                    + catNo
                    + " blank. Observer initials: "
                    + obsever_inits
                    + "Filename: "
                    + fileName
                )

            cursor.close()
            cnx.close()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exists")
            else:
                print(err)
        else:
            cnx.close()

        comments = ""

        """
        This next conditional because the file names don't necessarily match what's
        in the Microscribe catalog, or what it says in the prn, so I'm going to
        try both.
        """
        if fileName in excel_files:
            try:
                workbook = xlrd.open_workbook(excelDir + excel_files[fileName] + ".xls")
            except:
                print("Couldn't open " + excelDir + excel_files[fileName], file=warnout)
        elif fileName[-1:] == "c":
            fileName = fileName[:-1]
            try:
                workbook = xlrd.open_workbook(excelDir + excel_files[fileName] + ".xls")
            except:
                print("Couldn't open " + excelDir + fileName, file=warnout)
        else:
            try:
                workbook = xlrd.open_workbook(
                    excelDir + excel_files[file.lower()] + ".xls"
                )
            except:
                print(
                    "Couldn't open " + excelDir + excel_files[file.lower()],
                    file=warnout,
                )

        worksheet = workbook.sheet_by_index(0)
        try:
            comments += worksheet.cell(1, 9).value + " "
            comments += worksheet.cell(2, 9).value
        except:
            print(
                "Couldn't read comments in " + excel_files[file.lower()], file=warnout
            )

        if comments != "":
            comments = re.sub(r"`", r"\'", comments)
            comments = '"' + comments + '"'
            # print("Comment!!! " + comments)

        ### all info checks out, so start reading file to send to resample ###

        # note: \r\n after this, because resample needs Windows line returns
        outfile = open(toResample + file + "_out.prn", "w", newline="\r\n")
        print("#", institution, catNo, fileName, file=outfile, end="\r\n")
        for line in infile:
            line = line.rstrip()
            if line != "":
                """
                This next part, in case a 3D line is like 9999 9999 9999 LTEMFOS,
                I need at least two datapoints, or resample will treat it as a
                landmark. Since line starts with 9999 and will get removed, anyway,
                I'll just add a spurious point, so it's at least two points long.
                """
                name = re.split("\s+", line)

                """
                If there are more than 3 items in the line, then there's a name.
                If there's a name *and* it's 9999's *and* the name is in resample,
                then it's a line, not a point, and a second line of 9999's needs
                to be output. If the try fails, it's not in resample, and we can
                just move on.
                """
                if len(name) > 3 and line.find("9999") > -1:
                    try:
                        rr = resample[name[3]]
                        line = re.sub(" +", " ", line)
                        print(line, file=outfile, end="\r\n")
                        line = "9999 9999 9999"
                    except:
                        pass
                line = re.sub(" +", " ", line)
            print(line, file=outfile, end="\r\n")
        print("", file=outfile, end="\r\n")
        outfile.close()
        infile.close()
        """
        Note that the control file must be in the local directory when the command
        is called, and there cannot be a space between -c and the control file name.
        """
        code = subprocess.call(
            [
                "/Applications/resample/bin/resample",
                "-c" + resampleControl,
                "-d",
                toResample,
                "-e",
                "prn",
                "-o",
                intermediateDir,
                "-?",
                "9999",
            ]
        )
        if code != 0:
            subprocess.call(["rm", toResample + file + "_out.prn"])
            print("resampling failed on" + file)

        # Now reorder lines to prep for dvlr.
        landmarkslines = []
        infile = open(intermediateDir + file + "_out.prn", "r")
        outfile = open(toDVLR + file + ".prn", "w")
        for line in infile:
            if line.find(" IN ") > -1:
                print(line[:-1] + "up", file=outfile)
            elif line.find(" OP ") > -1:
                landmarkslines.append(line[:-1] + "down")
                for i in range(19):
                    line = infile.readline()
                    landmarkslines.append(line)
            elif line.find("RZYGINF") > -1:
                for i in landmarkslines:
                    print(i[:-1], file=outfile)
                print("", file=outfile)
                print(line[:-1], file=outfile)
            else:
                print(line[:-1], file=outfile)
        infile.close()
        outfile.close()

        ### run dvlr on file ###
        code = subprocess.call(
            [
                "/Volumes/files/business/NYCEP/3D/Dvlr/dvlr_eric.py",
                toDVLR + file + ".prn",
            ]
        )
        if code != 0:
            subprocess.call(["rm", toDVLR + file + ".prn"])
            print("dvlr failed on", file)

        # Read in dvlr's output, process to session out file and data out file.
        datindex = 0  # For landmarks; will be redefined later for lines.
        infile = open(DVLRed + file + ".dt2", "r")
        infile.readline()  # we don't need first line
        for i in range(1, 46):
            line = infile.readline()
            x, y, z = re.split("\s+", line)[:3]
            print(
                f"{data_id},{session_id},{i},{datindex},{x},{y},{z},,,,",
                file=dataout,
            )
            data_id += 1
        # print( '\nfinished landmarks\n' )

        # Now get lines.
        infile.readline()  # Get rid of blank before lines start.
        for i in range(46, 61):
            datindex = 1  # for lines
            for j in range(0, resample[landmarks[i - 1]]):
                line = infile.readline()
                # print( j, line, landmarks[i-1] )
                x, y, z = re.split("\s+", line)[:3]
                print(
                    f"{data_id},{session_id},{i},{datindex},{x},{y},{z},,,,",
                    file=dataout,
                )
                datindex += 1
                data_id += 1
            infile.readline()  # Remove blanks between lines.

        print(
            (
                f"{session_id},{observer_id},{specimen_id},{protocol_id},{original_id},"
                f'{iteratio},"{dfltsess}",{comments},"{file}",{group_id},,,,'
            ),
            file=sessout,
        )

        # Delete file from $toResample and $toDVLR
        subprocess.call(["rm", toResample + file + "_out.prn"])
        subprocess.call(["rm", toDVLR + file + ".prn"])
        session_id += 1


warnout.close()
errorout.close()
dataout.close()
