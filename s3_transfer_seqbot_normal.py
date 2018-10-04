#////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////
# script: s3_transfer_ashley_cells.py
# author: Lincoln Harris & James Webber
# date: 5.19
#
# Script for transfering cells from one s3 bucket to another (or a 
# group of query s3 buckets), according to a list of cells of interest. 
#
# 6.27: This has been optimized for parallel processing with GNU parallel. 
# Assuming you have GNU parallel installed, run like so:
#
#		parallel python3 s3_tranfer_ashley_cells.py ::: prefixList.csv
#
# where prefixList.csv is a file containing all of the s3 prefixes
# you want to search through
#
# s3_util library was written by James (THANK YOU)
#////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////
import s3_util
import os
import csv
import sys

#////////////////////////////////////////////////////////////////////
# getTCellFile()
#	args: myPath -> raw os path to tCell local file of interest (.csv)
#	returns: fPath -> python path to file of interest
#
# 	Just letting python know where our tCellFile is found
#////////////////////////////////////////////////////////////////////
def getTCellFile(myPath):
    # the actual file name
	fName = os.path.basename(myPath) 
    # the short path to that file
	sPath = os.path.dirname(myPath)
    # get full path to file
	fPath = os.path.join(sPath,fName)
    
	return fPath

#////////////////////////////////////////////////////////////////////
# getTCellSet()
#	args: myFile -> complete path to a local file (.csv) containing all
#					of the tCells we're interested in grabbing. 
#	returns: tSet -> a set (like a list, but hashed) of all the items
#				     in the input file
#	
#	Defining a set of all our tCells. 
#////////////////////////////////////////////////////////////////////
def getTCellSet(myFile):
	with open(myFile) as f:
		rdr = csv.reader(f)
		tSet = set()
		for item in rdr:
			tSet.add(item[0])
	return tSet

#////////////////////////////////////////////////////////////////////
# engine()
#	args: myPrefix -> query bucket prefix (s3) to get all subdirs within
#		  myTCellSet -> set of tCells to search for
#		  myBucket -> name of the s3 parent bucket to search through 
#	returns: 
#		  f_to_move -> list of files in query bucket prefix to be moved
#		  res_files -> list of names of destination files...where we 
#					   want our new files to be stored
# 
#	Searches through s3 buckets for files contained w/in a list
#////////////////////////////////////////////////////////////////////
def engine(myPrefix, myTCellSet, myBucket):
	f_to_move = []
	res_files = []
	for query_dir in s3_util.get_files(bucket=myBucket, prefix=myPrefix):
		dir_split = query_dir.split("/")
		#print(dir_split)
		query_cell_extra = dir_split[3]
		query_cell_extra_split = query_cell_extra.split("_")
		query_cell = query_cell_extra_split[0] + '_' + query_cell_extra_split[1]
		#print(query_cell)
		if query_cell in myTCellSet:
			f_to_move.append(query_dir)
			myStr = dest_bucket + query_cell + '/' + dir_split[4]
			res_files.append(myStr)
    
	return f_to_move, res_files

#////////////////////////////////////////////////////////////////////
# moveFiles()
#	args: mv -> list of file names to move (source)
#		  rs -> list of files to move to (destination)
#		  source_prefix -> s3 bucket to move files from
#	returns: NONE
#
#	Peforms the actual move, from one s3 bucket to another
#////////////////////////////////////////////////////////////////////
def moveFiles(mv, rs, source_prefix):
	s3_util.copy_files(mv, rs, source_prefix, 'darmanis-group', n_proc=16)

#////////////////////////////////////////////////////////////////////
# driverLoop()
#	args: pList -> list of prefixes w/in a parent s3 bucket
#		  tcSet -> set of tCells to search for
#		  cBucket -> parent s3 bucket
#	returns: NONE	
# 
#	Main logic here. Calls engine() to find files to move within query
#	bucket, then calls moveFiles() to do the move. 
#////////////////////////////////////////////////////////////////////
def driverLoop(pList, tcSet, cBucket):
	for i in range(len(pList)):
		currPre = pList[i]
		driver_out = engine(currPre, tcSet, cBucket)
		files_to_move = driver_out[0]
		results_files = driver_out[1]
		print(len(files_to_move))
		print("moving...")
		moveFiles(files_to_move, results_files, cBucket)
	return

#////////////////////////////////////////////////////////////////////
# main()
# 
#	scaffold for initiating lists & loops. Calls getTCellFile() and 
# 	getTCellSet() to define list of tCells to search for, then defines 
# 	lists of s3 prefixes to search our three parent s3 buckets for. 
# 	Then calls driverLoop to do all of the actual work. 
#
#////////////////////////////////////////////////////////////////////
  
global dest_bucket

tCellFile = getTCellFile("/home/ubuntu/expansionVol1/03-tCellGrab_redux/immune_tcells.csv")
tCellSet = getTCellSet(tCellFile)
dest_bucket = 'singlecell_lungadeno/seqbot_tCells/'

inputFile = sys.argv[1]

prefixList = []
with open(inputFile) as f:
	input_rdr = csv.reader(f)
	for item in input_rdr:
		prefixList.append(item[0])

print(" ")
print("STARTING")
driverLoop(prefixList, tCellSet, 'czbiohub-seqbot')
print("done!")

#////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////
