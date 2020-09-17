#!/usr/bin/perl -w
#################################################################
#
# Perl script to build the scalar & session tables from Eric's teeth table
# By: Katherine St. John
# Date: July 2006
#
# Modified April 2007 to include standard fields for the session table.
#
# Session table: from the teeth table, grab the hyponum (column C) 
# and the observer (F), and make a list (without duplicates).
# Then, print out the session table:
#
#	uniqueid,observer,specimen,5,1,y,,teeth,9	
#
# where observer and specimen are C and F from above, 
# the uniqueid is generated on the fly when printing out the table, and
# the following values are hard-coded:
# 			protocol_id 	5	
#			iteratio		1
#			dfltsess		y
#			comments		<empty>
#			filename		teeth
#			createby		9
#
# Scalar table:  first generate a lookup table with the name of the 
# variables based on the type of tooth.  For example, 
# if the tooth is 02UPR, then the J column holds the variable UP4WG, 
# if the tooth is 03UM1, then the J column holds the variable UM1WS
#
# Next, process each row from the file:
# 1.  Find the type of tooth (column A).
# 2.  Find the session's uniqueid (from column F & C, and session
#     table above).
# 3.  For each non-empty entry, find the variable's name (from type in
#     column A and lookup table) to associate with the value.
# 4.  Creating a uniqueid and printing out for the scalar table:
#		uniqueid,sessionid,variableName,value
#
#
# Usage:
#
#	teeth2scalar inputFile outSession outScalar
#
# where the inputFile is a CSV teeth excel database and 
# the output files are CSV file to be read into the primo
# database
#
################################################################

#Options from the command line:
if($#ARGV != 2)
{
    die "Usage: teeth2scalar infile outSession outScalar: create session & scalar table from teeth data\n";
}

$infile = shift;		#input file, CSV data
$sessionfile = shift;	#name of session output file
$scalarfile = shift;	#name of scalar output file
%entries = ();			#clear out the entry table, to be safe
%session = ();			#clear out the session table, to be safe
%comments = ();			#clear out the comments, to be safe
$uniqueid = 1;			#assign to each entry a unique ID

#Options that can be changed:
$verbose = 0;		#non-zero ==> lots of messages
local $/ = "\r"; #for csvs created on a Mac. Comment out if the file came from a PC

#Call the subroutine that sets up the look-up table of variable names and 
#variable ID:
$refVNames = setUpVariableNames();
%variableNames = %$refVNames;
$refVIDs = setUpVariableID();
%variableID = %$refVIDs;

#Open files for reading and writing
open(INFILE, "$infile");
open(SESSION, ">$sessionfile");

# Throw away six lines (they're the ones with the header info):
#	Will want to comment these lines out for input files without a header lines
for ($i = 0; $i < 7; $i++) {
	$_ = <INFILE>;
}


# Read in each line, storing in a dictionary:
while ( $_ = <INFILE> )
{
 	chomp $_;
	@words = split(',', $_);
	
    if ( $verbose > 2 ) 
	{ 
        	print "line: $_\n";
        	print "\t $words[5], $words[2]\n";
        
    }
    #check for comments, and save by type:
    if ( $words[30] ) {
		#There was a comma in the comment, so, reparse input to make sure you have it all:
		@doubleCheck = split ('\"', $_);
		$comments{ "$words[5],$words[2]" } .= "$words[0]: $doubleCheck[1]; ";
    }
    elsif ( $words[29] ) {
    	$comments{ "$words[5],$words[2]" } .= "$words[0]: $words[29]; ";
    }
    
    $entries{ "$words[5],$words[2]"}++;         
}


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
    	print SESSION "$uniqueid,$key,5,1,y,\"$comments{$key}\",teeth,9\n" ;
    }
    else {
    	print SESSION "$uniqueid,$key,5,1,y,,teeth,9\n" ;    
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

# Throw away six lines (they're the ones with the header info):
#	Will want to comment these lines out for input files without a header lines
for ($i = 0; $i <6; $i++) {
	$_ = <INFILE>;
}	

# Read in each line, split into values, and print to the session table (proceeded
#	by a uniqueid:
$uniqueid = 1;
while ( $_ = <INFILE> )
{
 	chomp $_;
	@words = split(',', $_);
    $specimenType = $words[0];
    #Look up the uniqueid for this "hyponum,observer":
    $sessionid = $session{ "$words[5],$words[2]"};

	
    if ( $verbose > 2 ) 
	{ 
        	print "line: $_\n";
        	print "the specimen type is $specimenType\n";
        	print "\t\"$words[5], $words[2]\" has sessionid $sessionid\n";
    }
    
    
    #Process the list of values:
    #	first data occurs column 7 or later; only comments after column 29

    for ($i = 7 ; $i < 29 ; $i++ )
    {
    	#For each non-empty entry, look up the variable name:
     	if ( exists($words[$i]) && $words[$i] ne '' )
     	{		
    		$vName = $variableNames{$specimenType}[$i];
    		if ( $vName )
    		{
    			#Look up variable ID:
    			$varID = $variableID { $vName };
    			#Print the variable name and value, with a uniqueid to the scalar table:
    			print SCALAR "$uniqueid,$sessionid,$varID,$words[$i]\n";
    			#print "$uniqueid,$sessionid,$varID,$words[$i]\n";
    		}
    		else {
    			print "Warning: data entry with no variable name:\t";
    			print "\tline: $_\t";
    			print "\tentry $i: $words[$i]\n";
    		}
    		
    		if ( $verbose > 1 )
    		{
    			print "\tword $i is $words[$i]\t";
    			if ( $vName )
    			{
    				print "\tthe variable name is $vName\t";
    				$varID = $variableID { $vName };
    				print "with ID $varID\n";
    			}
    			else {
    				print "\tnot defined!\n";
    			}
    		}
    	
    		#Update uniqueid:
    		$uniqueid++;
    	}
    }
}
# Clean up:
close(INFILE);
close(SCALAR);




##################################################################
# Subroutine that sets up the lookup table of variable names, 
#	based on tooth type.
#
# The initial table is based on the teeth.xls file of Eric Delson,
# where the type of specimen (column A) determines the names of the
# variables provided.  For example, if the specimen is of type 
# '01UIC', then the variable in column M is 'UI1W'.  But if it's of 
# type '02UPR', then the variable in column M is 'UP3W'.
#
# This section is hand-edited and delicate-- be careful changing it!
##################################################################

sub setUpVariableNames {
	#The first 7 columns match the metadata from the teeth.xls.
	#Column 8 and greater are the variable names.  If blank, no 
	#data exists in that column for that specimen type.
	my %variableNames = (
		'01UIC' => ['01UIC','CGU 001',1001,1,ED,9,1,"","","","","",UI1W,UI1LA,UI1L,UI1H,UI1RH,UI1TH,UI2W,UI2LA,UI2L,UI2H,UI2RH,UI2TH,UCW,UCL,UCH,UCRH,UCTH,"","",""],
		'02UPR' => ['02UPR','CGU 001',1001,1,ED,9,1,"",UP3WG,UP4WG,UP3WS,UP4WS,UP3W,UP3L,UP3IC,UP3H,UP3FH,UP3AL,UP3PL,UP4W,UP4L,UP4IC,UP4H,UP4FH,UP4AL,UP4PL,"","","","","",""],
		'03UM1' => ['03UM1','CGU 001',1001,1,ED,9,1,"",UM1WG,UM1WS,"","",UM1AW,UM1AWN,UM1PW,UM1PWN,UM1L,UM1ICA,UM1ICP,UM1ICB,UM1ICL,UM1NH,UM1H,UM1AL,UM1PL,"","","","",'UM1AW est 7',"",""],
		'04UM2' => ['04UM2','CGU 001',1001,1,ED,9,1,"",UM2WG,UM2WS,"","",UM2AW,UM2AWN,UM2PW,UM2PWN,UM2L,UM2ICA,UM2ICP,UM2ICB,UM2ICL,UM2NH,UM2H,UM2AL,UM2PL,"","","","","","",""],
		'05UM3' => ['05UM3','CGU 001',1001,1,ED,9,1,"",UM3WG,UM3WS,"","",UM3AW,UM3AWN,UM3PW,UM3PWN,UM3L,UM3ICA,UM3ICP,UM3ICB,UM3ICL,UM3NH,UM3H,UM3AL,UM3PL,"","","","",'tooth green',"",""],
		'06LIC' => ['06LIC','CGU 001',1001,1,ED,9,1,"","","",LI1W,LI1LA,LI1L,LI1H,LI1RH,LI1TH,LI2W,LI2LA,LI2L,LI2H,LI2RH,LI2TH,LCW,LCL,LCH,LCRH,LCTH,"","","","",""],
		'07LPR' => ['07LPR','CGU 001',1001,1,ED,9,1,"",LP4WG,LP4WS,LP3W,LP3LA,LP3L,LP3FL,LP3H,LP3PL,LP3HX,LP4W,LP4L,LP4IC,LP4NH,LP4MH,LP4FH,LP4ALN,LP4PLN,LP4ALM,LP4PLM,"","",'tooth broken    LP4ALN est 4',"",""],
		'08LM1' => ['08LM1','CGU 001',1001,1,ED,9,1,"",LM1WG,LM1WS,LM1AW,LM1AWN,LM1PW,LM1PWN,LM1L,LM1ICA,LM1ICP,LM1ICB,LM1ICL,LM1NH,LM1H,LM1AL,LM1PL,"","","","","","","","",""],
		'09LM2' => ['09LM2','CGU 001',1001,1,ED,9,1,"",LM2WG,LM2WS,LM2AW,LM2AWN,LM2PW,LM2PWN,LM2L,LM2ICA,LM2ICP,LM2ICB,LM2ICL,LM2NH,LM2H,LM2AL,LM2PL,"","","","","","","","",""],
		'10LM3' => ['10LM3','CGU 001',1001,1,ED,9,1,"",LM3WG,LM3WS,LM3AW,LM3AWN,LM3PW,LM3PWN,LM3L,LM3ICA,LM3ICP,LM3ICB,LM3ICL,LM3NH,LM3H,LM3AL,LM3PL,LM3HW,LM3HW2,LM3IHB,LM3IHL,LM3AL2,LM3HYL,"","",""],
		'11UCD' => ['11UCD','CGU 108',1108,1,EC,10,2,"","","","","",UDI1W,UDI1LA,UDI1L,UDI1H,UDI1RH,UDI1TH,UDI2W,UDI2LA,UDI2L,UDI2H,UDI2RH,UDI2TH,UDCW,UDCL,UDCH,UDCRH,UDCTH,"","",""],
#Common typo, so, add a line to deal with it:
		'11UDC' => ['11UCD','CGU 108',1108,1,EC,10,2,"","","","","",UDI1W,UDI1LA,UDI1L,UDI1H,UDI1RH,UDI1TH,UDI2W,UDI2LA,UDI2L,UDI2H,UDI2RH,UDI2TH,UDCW,UDCL,UDCH,UDCRH,UDCTH,"","",""],
		'12UD3' => ['12UD3','CGU 108',1108,1,EC,10,2,"",UD3WG,UD3WS,"","",UD3AW,UD3AWN,UD3PW,UD3PWN,UD3L,UD3ICA,UD3ICP,UD3ICB,UD3ICL,UD3NH,UD3H,UD3AL,UD3PL,"","","","","","",""],
		'13UD4' => ['13UD4','CGU 108',1108,1,EC,10,2,"",UD4WG,UD4WS,"","",UD4AW,UD4AWN,UD4PW,UD4PWN,UD4L,UD4ICA,UD4ICP,UD4ICB,UD4ICL,UD4NH,UD4H,UD4AL,UD4PL,"","","","","","",""],
#Common typo, so, add a line to deal with it:	
		'13LDC' => ['14LDC','CBB 004',4004,4,EC,10,2,"","","",LDI1W,LDI1LA,LDI1L,LDI1H,LDI1RH,LDI1TH,LDI2W,LDI2LA,LDI2L,LDI2H,LDI2RH,LDI2TH,LDCW,LDCL,LDCH,LDCRH,LDCTH,"","","","",""],
		'14LDC' => ['14LDC','CBB 004',4004,4,EC,10,2,"","","",LDI1W,LDI1LA,LDI1L,LDI1H,LDI1RH,LDI1TH,LDI2W,LDI2LA,LDI2L,LDI2H,LDI2RH,LDI2TH,LDCW,LDCL,LDCH,LDCRH,LDCTH,"","","","",""],
#Common typo, so, add a line to deal with it:
		'14LCD' => ['14LDC','CBB 004',4004,4,EC,10,2,"","","",LDI1W,LDI1LA,LDI1L,LDI1H,LDI1RH,LDI1TH,LDI2W,LDI2LA,LDI2L,LDI2H,LDI2RH,LDI2TH,LDCW,LDCL,LDCH,LDCRH,LDCTH,"","","","",""],
		'15LD3' => ['15LD3','CBB 004',4004,4,EC,10,2,"",LD3WG,LD3WS,LD3AW,LD3AWN,LD3PW,LD3PWN,LD3L,LD3ICA,LD3ICP,LD3ICB,LD3ICL,LD3NH,LD3H,LD3AL,LD3PL,"","","","","","","","",""],
		'16LD4' => ['16LD4','CBB 004',4004,4,EC,10,2,"",LD4WG,LD4WS,LD4AW,LD4AWN,LD4PW,LD4PWN,LD4L,LD4ICA,LD4ICP,LD4ICB,LD4ICL,LD4NH,LD4H,LD4AL,LD4PL,"","","","","","","","",""],
		'17UMX' => ['17UMX','KUX1112',6112,6,ED,9,0,UMXTOOTH,UMXWG,UMXWS,"","",UMXAW,UMXAWN,UMXPW,UMXPWN,UMXL,UMXICA,UMXICP,UMXICB,UMXICL,UMXNH,UMXH,UMXAL,UMXPL,"","","","","","",""],
#Common typo, so, add a line to deal with it:
		'18UPX' => ['19UPX','MAFW705',62705,62,JF,17,0,"",UPX3WG,UPX4WG,UPX3WS,UPX4WS,UPX3W,UPX3L,UPX3IC,UPX3H,UPX3FH,UPX3AL,UPX3PL,UPX4W,UPX4L,UPX4IC,UPX4H,UPX4FH,UPX4AL,UPX4PL,"","","","","",""],
		'19UPX' => ['19UPX','MAFW705',62705,62,JF,17,0,"",UPX3WG,UPX4WG,UPX3WS,UPX4WS,UPX3W,UPX3L,UPX3IC,UPX3H,UPX3FH,UPX3AL,UPX3PL,UPX4W,UPX4L,UPX4IC,UPX4H,UPX4FH,UPX4AL,UPX4PL,"","","","","",""],
		'20LMX' => ['20LMX','KUA1031',6031,6,ED,9,0,LMXTOOTH,LMXWG,LMXWS,LMXAW,LMXAWN,LMXPW,LMXPWN,LMXL,LMXICA,LMXICP,LMXICB,LMXICL,LMXNH,LMXH,LMXAL,LMXPL,"","","","","","","","",""],
	);
	return \%variableNames;
}


##################################################################
# Subroutine that sets up the lookup table of variable ids, 
#	given the variable name.
#
# This section is hand-edited and delicate-- be careful changing it!
##################################################################

sub setUpVariableID {
	my %varID = (
	'UI1W' =>	225	,
 	'UI1LA' =>	226	,
 	'UI1L' =>	227	,
 	'UI1H' =>	228	,
	'UI1RH' =>	229	,
	'UI1TH' =>	230	,
	'UI2W' =>	231	,
	'UI2LA' =>	232	,
	'UI2L' =>	233	,
	'UI2H' =>	234	,
	'UI2RH' =>	235	,
	'UI2TH' =>	236	,
	'UCW' =>	237	,
	'UCL' =>	238	,
	'UCH' =>	239	,
	'UCRH' =>	240	,
	'UCTH' =>	241	,
	'UP3WG' =>	242	,
	'UP3WS' =>	243	,
	'UP3W' =>	244	,
	'UP3L' =>	245	,
	'UP3IC' =>	246	,
	'UP3H' =>	247	,
	'UP3FH' =>	248	,
	'UP3AL' =>	249	,
	'UP3PL' =>	250	,
	'UP4WG' =>	251	,
	'UP4WS' =>	252	,
	'UP4W' =>	253	,
	'UP4L' =>	254	,
	'UP4IC' =>	255	,
	'UP4H' =>	256	,
	'UP4FH' =>	257	,
	'UP4AL' =>	258	,
	'UP4PL' =>	259	,
	'UM1WG' =>	260	,
	'UM1WS' =>	261	,
	'UM1AW' =>	262	,
	'UM1AWN' =>	263	,
	'UM1PW' =>	264	,
	'UM1PWN' =>	265	,
	'UM1L' =>	266	,
	'UM1ICA' =>	267	,
	'UM1ICP' =>	268	,
	'UM1ICB' =>	269	,
	'UM1ICL' =>	270	,
	'UM1NH' =>	271	,
	'UM1H' =>	272	,
	'UM1AL' =>	273	,
	'UM1PL' =>	274	,
	'UM2WG' =>	275	,
	'UM2WS' =>	276	,
	'UM2AW' =>	277	,
	'UM2AWN' =>	278	,
	'UM2PW' =>	279	,
	'UM2PWN' =>	280	,
	'UM2L' =>	281	,
	'UM2ICA' =>	282	,
	'UM2ICP' =>	283	,
	'UM2ICB' =>	284	,
	'UM2ICL' =>	285	,
	'UM2NH' =>	286	,
	'UM2H' =>	287	,
	'UM2AL' =>	288	,
	'UM2PL' =>	289	,
	'UM3WG' =>	290	,
	'UM3WS' =>	291	,
	'UM3AW' =>	292	,
	'UM3AWN' =>	293	,
	'UM3PW' =>	294	,
	'UM3PWN' =>	295	,
	'UM3L' =>	296	,
	'UM3ICA' =>	297	,
	'UM3ICP' =>	298	,
	'UM3ICB' =>	299	,
	'UM3ICL' =>	300	,
	'UM3NH' =>	301	,
	'UM3H' =>	302	,
	'UM3AL' =>	303	,
	'UM3PL' =>	304	,
	'UDI1W' =>	305	,
	'UDI1LA' =>	306	,
	'UDI1L' =>	307	,
	 'UDI1H' =>	308	,
	 'UDI1RH' =>	309	,
	 'UDI1TH' =>	310	,
	 'UDI2W' =>	311	,
	 'UDI2LA' =>	312	,
	 'UDI2L' =>	313	,
	 'UDI2H' =>	314	,
	 'UDI2RH' =>	315	,
	 'UDI2TH' =>	316	,
	 'UDCW' =>	317	,
	 'UDCL' =>	318	,
	 'UDCH' =>	319	,
	 'UDCRH' =>	320	,
	 'UDCTH' =>	321	,
	 'UD3WG' =>	322	,
	 'UD3WS' =>	323	,
	 'UD3AW' =>	324	,
	 'UD3AWN' =>	325	,
	 'UD3PW' =>	326	,
	 'UD3PWN' =>	327	,
	 'UD3L' =>	328	,
	 'UD3ICA' =>	329	,
	 'UD3ICP' =>	330	,
	 'UD3ICB' =>	331	,
	 'UD3ICL' =>	332	,
	 'UD3NH' =>	333	,
	 'UD3H' =>	334	,
	 'UD3AL' =>	335	,
	 'UD3PL' =>	336	,
	 'UD4WG' =>	337	,
	 'UD4WS' =>	338	,
	 'UD4AW' =>	339	,
	 'UD4AWN' =>	340	,
	 'UD4PW' =>	341	,
	 'UD4PWN' =>	342	,
	 'UD4L' =>	343	,
	 'UD4ICA' =>	344	,
	 'UD4ICP' =>	345	,
	 'UD4ICB' =>	346	,
	 'UD4ICL' =>	347	,
	 'UD4NH' =>	348	,
	 'UD4H' =>	349	,
	 'UD4AL' =>	350	,
	 'UD4PL' =>	351	,
	 'UPX3WG' =>	352	,
	 'UPX3WS' =>	353	,
	 'UPX3W' =>	354	,
	 'UPX3L' =>	355	,
	 'UPX3IC' =>	356	,
	 'UPX3H' =>	357	,
	 'UPX3FH' =>	358	,
	 'UPX3AL' =>	359	,
	 'UPX3PL' =>	360	,
	 'UPX4WG' =>	361	,
	 'UPX4WS' =>	362	,
	 'UPX4W' =>	363	,
	 'UPX4L' =>	364	,
	 'UPX4IC' =>	365	,
	 'UPX4H' =>	366	,
	 'UPX4FH' =>	367	,
	 'UPX4AL' =>	368	,
	 'UPX4PL' =>	369	,
	 'UMXTOOTH' =>	370	,
	 'UMXWG' =>	371	,
	 'UMXWS' =>	372	,
	 'UMXAW' =>	373	,
	 'UMXAWN' =>	374	,
	 'UMXPW' =>	375	,
	 'UMXPWN' =>	376	,
	 'UMXL' =>	377	,
	 'UMXICA' =>	378	,
	 'UMXICP' =>	379	,
	 'UMXICB' =>	380	,
	 'UMXICL' =>	381	,
	 'UMXNH' =>	382	,
	 'UMXH' =>	383	,
	 'UMXAL' =>	384	,
	 'UMXPL' =>	385	,
	 'LI1W' =>	386	,
	 'LI1LA' =>	387	,
	 'LI1L' =>	388	,
	 'LI1H' =>	389	,
	 'LI1RH' =>	390	,
	 'LI1TH' =>	391	,
	 'LI2W' =>	392	,
	 'LI2LA' =>	393	,
	 'LI2L' =>	394	,
	 'LI2H' =>	395	,
	 'LI2RH' =>	396	,
	 'LI2TH' =>	397	,
	 'LCW' =>	398	,
	 'LCL' =>	399	,
	 'LCH' =>	400	,
	 'LCRH' =>	401	,
	 'LCTH' =>	402	,
	 'LP3W' =>	403	,
	 'LP3LA' =>	404	,
	 'LP3L' =>	405	,
	 'LP3FL' =>	406	,
	 'LP3H' =>	407	,
	 'LP3PL' =>	408	,
	 'LP3HX' =>	409	,
	 'LP4WG' =>	410	,
	 'LP4WS' =>	411	,
	 'LP4W' =>	412	,
	 'LP4L' =>	413	,
	 'LP4IC' =>	414	,
	 'LP4NH' =>	415	,
	 'LP4MH' =>	416	,
	 'LP4FH' =>	417	,
	 'LP4ALN' =>	418	,
	 'LP4PLN' =>	419	,
	 'LP4ALM' =>	420	, #was LP4AL
	 'LP4PLM' =>	421	, #was LP$PL
	 'LM1WG' =>	422	,
	 'LM1WS' =>	423	,
	 'LM1AW' =>	424	,
	 'LM1AWN' =>	425	,
	 'LM1PW' =>	426	,
	 'LM1PWN' =>	427	,
	 'LM1L' =>	428	,
	 'LM1ICA' =>	429	,
	 'LM1ICP' =>	430	,
	 'LM1ICB' =>	431	,
	 'LM1ICL' =>	432	,
	 'LM1NH' =>	433	,
	 'LM1H' =>	434	,
	 'LM1AL' =>	435	,
	 'LM1PL' =>	436	,
	 'LM2WG' =>	437	,
	 'LM2WS' =>	438	,
	 'LM2AW' =>	439	,
	 'LM2AWN' =>	440	,
	 'LM2PW' =>	441	,
	 'LM2PWN' =>	442	,
	 'LM2L' =>	443	,
	 'LM2ICA' =>	444	,
	 'LM2ICP' =>	445	,
	 'LM2ICB' =>	446	,
	 'LM2ICL' =>	447	,
	 'LM2NH' =>	448	,
	 'LM2H' =>	449	,
	 'LM2AL' =>	450	,
	 'LM2PL' =>	451	,
	 'LM3WG' =>	452	,
	 'LM3WS' =>	453	,
	 'LM3AW' =>	454	,
	 'LM3AWN' =>	455	,
	 'LM3PW' =>	456	,
	 'LM3PWN' =>	457	,
	 'LM3L' =>	458	,
	 'LM3ICA' =>	459	,
	 'LM3ICP' =>	460	,
	 'LM3ICB' =>	461	,
	 'LM3ICL' =>	462	,
	 'LM3NH' =>	463	,
	 'LM3H' =>	464	,
	 'LM3AL' =>	465	,
	 'LM3PL' =>	466	,
	 'LM3HW' =>	467	,
	 'LM3HW2' =>	468	,
	 'LM3IHB' =>	469	,
	 'LM3IHL' =>	470	,
	 'LM3AL2' =>	471	,
	 'LM3HYL' =>	472	,
	 'LDI1W' =>	473	,
	 'LDI1LA' =>	474	,
	 'LDI1L' =>	475	,
	 'LDI1H' =>	476	,
	 'LDI1RH' =>	477	,
	 'LDI1TH' =>	478	,
	 'LDI2W' =>	479	,
	 'LDI2LA' =>	480	,
	 'LDI2L' =>	481	,
	 'LDI2H' =>	482	,
	 'LDI2RH' =>	483	,
	 'LDI2TH' =>	484	,
	 'LDCW' =>	485	,
	 'LDCL' =>	486	,
	 'LDCH' =>	487	,
	 'LDCRH' =>	488	,
	 'LDCTH' =>	489	,
	 'LD3WG' =>	490	,
	 'LD3WS' =>	491	,
	 'LD3AW' =>	492	,
	 'LD3AWN' =>	493	,
	 'LD3PW' =>	494	,
	 'LD3PWN' =>	495	,
	 'LD3L' =>	496	,
	 'LD3ICA' =>	497	,
	 'LD3ICP' =>	498	,
	 'LD3ICB' =>	499	,
	 'LD3ICL' =>	500	,
	 'LD3NH' =>	501	,
	 'LD3H' =>	502	,
	 'LD3AL' =>	503	,
	 'LD3PL' =>	504	,
	 'LD4WG' =>	505	,
	 'LD4WS' =>	506	,
	 'LD4AW' =>	507	,
	 'LD4AWN' =>	508	,
	 'LD4PW' =>	509	,
	 'LD4PWN' =>	510	,
	 'LD4L' =>	511	,
	 'LD4ICA' =>	512	,
	 'LD4ICP' =>	513	,
	 'LD4ICB' =>	514	,
	 'LD4ICL' =>	515	,
	 'LD4NH' =>	516	,
	 'LD4H' =>	517	,
	 'LD4AL' =>	518	,
	 'LD4PL' =>	519	,
	 'LMXTOOTH' =>	520	,
	 'LMXWG' =>	521	,
	 'LMXWS' =>	522	,
	 'LMXAW' =>	523	,
	 'LMXAWN' =>	524	,
	 'LMXPW' =>	525	,
	 'LMXPWN' =>	526	,
	 'LMXL' =>	527	,
	 'LMXICA' =>	528	,
	 'LMXICP' =>	529	,
	 'LMXICB' =>	530	,
	 'LMXICL' =>	531	,
	 'LMXNH' =>	532	,
	 'LMXH' =>	533	,
	 'LMXAL' =>	534	,
	 'LMXPL' =>	535	,
	 'UPXTOOTH' =>	536	,

	);
	return \%varID;
}
