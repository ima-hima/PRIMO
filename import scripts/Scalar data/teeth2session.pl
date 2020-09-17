#!/usr/bin/perl -w
#################################################################
#
# Perl script to build the session table from Eric's teeth table
# By: Katherine St. John
# Date: July 2006
#
# From the teeth table, grab the hyponum (column C) and
# the observer (F), and make a list (without duplicates).
# Then, print out the session table:
#
#	uniqueid	observer	specimen
#
# where observer and specimen are C and F from above, and
# the uniqueid is generated on the fly.
#
#
# Usage:
#
#	teeth2session inputFile outputFile
#
# where the inputFile is a CSV teeth excel database and 
# the outputFile is a CSV file to be read into the primo
# database
#
################################################################

#Options from the command line:
if($#ARGV != 1)
{
    die "Usage: teeth2session infile outfile: create session table from teeth data\n";
}

$infile = shift;		#input file, CSV data
$outfile = shift;		#name of output file
%entries = ();			#clear out the entry table, to be safe
$uniqueid = 1;			#assign to each entry a unique ID

#Options that can be changed:
$verbose = 0;		#non-zero ==> lots of messages


#Open files for reading and writing
open(INFILE, "$infile") or die $!;
open(OUTFILE, ">$outfile") or die $!;

# Throw away first line (it's the one with the header):
#	Will want to comment this line out for input files without a header line
$_ = <INFILE>;

# Read in each line, storing in a dictionary:
while ( $_ = <INFILE> )
{
 	chomp $_;
	@words = split(',', $_);
	
    if ( $verbose > 1 ) 
	{ 
        	print "line: $_\n";
    }
    $entries{ "$words[0],$words[3]"}++;         
}
close(INFILE);

#Print out (one occurence of each "hyponum,observer") info to OUTFILE:
foreach $key (sort keys %entries) {
	if ( $verbose > 0 )
	{
     	print "$uniqueid,$key occurs $entries{$key}\n";
    }
    
    print OUTFILE "$uniqueid,$key\n" ;
    $uniqueid++;
}
close(OUTFILE);   
	



