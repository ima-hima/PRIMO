#!/usr/bin/perl -w
#################################################################
#
# Perl script to build the scalar & session tables from Eric's skull table
# By: Katherine St. John
# Date: April 2007
#
# Modified from teee2scalar.pl (written April 2007).
#
# Session table: from the skull table, grab the hyponum (column B)
# and the observer (E), and make a list (without duplicates).
# Then, print out the session table:
#
#	uniqueid,observer,specimen,5,original_id,1,y,,skull,group_id,9
#
# where observer and specimen are B and E from above,
# the uniqueid is generated on the fly when printing out the table, and
# the following values are hard-coded:
# 			protocol_id 	5
#			iteratio		1
#			dfltsess		y
#			comments		<empty>
#			filename		skull
#			createby		9
#
#
# Process each row from the file:
# 1.  Find the session's uniqueid (from column E & B, and session
#     table above).
# 2.  For each non-empty entry, find the variable's name (from type in
#     column A and lookup table) to associate with the value.
# 3.  Creating a uniqueid and printing out for the scalar table:
#		uniqueid,sessionid,variableName,value
#
# Unlike the teeth table, the variable names are just the column headings
# and don't change, depending on initial entries in the file.  Also, there
# are no comments in the file.
#
#
# Usage:
#
#	skull2scalar inputFile outSession outScalar
#
# where the inputFile is a CSV skull excel database and
# the output files are CSV file to be read into the primo
# database
#
################################################################

#Options from the command line:
if($#ARGV != 2)
{
    die "Usage: skull2session infile outSession outScalar: create session & scalar table from skull data\n";
}

$infile = shift;		#input file, CSV data
$sessionfile = shift;	#name of session output file
$scalarfile = shift;	#name of scalar output file
%entries = ();			#clear out the entry table, to be safe
%session = ();			#clear out the session table, to be safe
%comments = ();			#clear out the comments, to be safe
$uniqueid = 10001;		#assign to each entry a unique ID, starting with
						#10001 for session table

#Options that can be changed:
$verbose = 1;		#non-zero ==> lots of messages
#local $/ = "\r"; #for csvs created on a Mac. Comment out if the file came from a PC


#Open files for reading and writing
open(INFILE, "$infile") or die "Couldn't open infile: $infile";
open(SESSION, ">$sessionfile") or die "Couldn't create session file: $sessionfile";

# Not necessary for skulls
# Throw away six lines (they're the ones with the header info):
#	Will want to comment these lines out for input files without a header lines
#for ($i = 0; $i < 7; $i++) {
#	$_ = <INFILE>;
#}
#Instead, keep track of column heads from first two lines to set up the variable
#ID and names:
# $header = <INFILE>;
# @columnName = split(",", $header);

$header = <INFILE>;
@columnID = split(",", $header);


# Read in each line, storing in a dictionary:
while ( $_ = <INFILE> )
{
	chomp $_;
	@words = split(',', $_);

    if ( $verbose > 2 )
	{
        	print "line: $_\n";
        	print "\t $words[2], $words[0]\n";

    }
    $idString = "$words[2],$words[0]";
    $idString =~ s/\n//;
   # print $newString . "\n";
    $entries{ $idString}++;
    $groups{ $idString } = $words[4];
    $original{ $idString } = $words[5];
    if ( $words[121] ) {
    	if ( $words[122] ) {
			#There was a comma in the comment, so, reparse input to make sure you have it all:
			@doubleCheck = split ('\"', $_);
			( $comments{ $idString } = $doubleCheck[1] ) =~ s/,/;/g;
		}
		else {
			$comments{ $idString } = $words[121];
		}
		if( $verbose > 0 ) {
			print "$comments{ $idString }\n";
		}
	}

}

#set date
$month = (localtime)[4] + 1;
$date = (localtime)[3];
$year = (localtime)[5] + 1900;

print SESSION 'id, observer_id, specimen_id, protocol_id, original_id, iteratio, dlftsess, comments, filename, group_id, created_by, created_at, updatedby, updated_at' . "\n";

#Print out (one occurence of each "hyponum,observer") info to OUTFILE:
foreach $key (sort keys %entries) {
	if ( $verbose > 2 )
	{
     	print "\"$key\" occurs $entries{$key} times and is assigned the uniqueid $uniqueid.\n";
    }

    #Set up a hash for the session data, to be used to build the scalar table:
    $session{ $key } = $uniqueid;

    #If the exist, print comments:
    if ( $comments{ $key } ) {
    	print SESSION "$uniqueid,$key,5,$original{$key},1,y,$comments{$key},skull,$groups{$key},9,,,$month/$date/$year\n" ;
    }
    else {
    	print SESSION "$uniqueid,$key,5,$original{$key},1,y,,skull,$groups{$key},9,,,$month/$date/$year\n" ;
    }
    $uniqueid++;
}

# Clean up:
close(INFILE);
close(SESSION);



#Read the infile again, this time, creating entries for the scalar table
#	for each of the variables entered (multiple per line):

#Open files for reading and writing
open(INFILE, "$infile");
open(SCALAR, ">$scalarfile");

print SCALAR 'id, session_id, variable_id, value' . "\n";

# Throw away six lines (they're the ones with the header info):
#	Will want to comment these lines out for input files without a header lines
#for ($i = 0; $i <6; $i++) {
#	$_ = <INFILE>;
#}
#Throw away first two line:
# <INFILE>;
<INFILE>;

# Read in each line, split into values, and print to the session table (proceeded
#	by a uniqueid, starting with 200000 for scalar table:
$uniqueid = 200000;
while ( $_ = <INFILE> )
{
 	chomp $_;
	@words = split(',', $_);

	#Not needed for skulls:
    #$specimenType = $words[0];

    #Look up the uniqueid for this "hyponum,observer":
    $idString = "$words[2],$words[0]";
    $idString =~ s/\n//;
    $sessionid = $session{ $idString };


    if ( $verbose > 2 )
	{
        	print "line: $_\n";
        	#print "the specimen type is $specimenType\n";
        	print "\t\"$words[2], $words[0]\" has sessionid $sessionid\n";
    }


    #Process the list of values:
    #	first data occurs column 6 or later
    for ($i = 6 ; $i < 121 ; $i++ )
    {
    	#For each non-zero entry, look up the variable name:
    	if ( exists($words[$i]) && $words[$i] ne '' )
    	{
    		#$vName = $columnName[$i];
    		$vID = $columnID[$i];
#     		if ( $vName ne "MALF")
#     		{
    			#Print the variable ID and value, with a uniqueid to the scalar table:

    			print SCALAR "$uniqueid,$sessionid,$vID,$words[$i]\n";
#    		}
    		#else {
    		#	print "Warning: data entry with no variable name:\t";
    		#	print "\tline: $_\t";
    		#	print "\tentry $i: $words[$i]\n";
    		#}

    		if ( $verbose > 1 )
    		{
    			print "\tword $i is $words[$i]\n";
    			if ( $vName ne "MALF")
    			{
    				print "\t\tthe variable name and ID is $vName and $vID\n";
    			}
    			#else {
    			#	print "\tnot defined!\n";
    			#}
    		}

    		#Update uniqueid:
    		$uniqueid++;
    	}
    }
}
# Clean up:
close(INFILE);
close(SCALAR);

