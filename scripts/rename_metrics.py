#! /usr/bin/python

# rename_metrics
# Renames the following metrics and files (if present) from one or more Polyworld "run" directories:
#	brain
#	   Recent
#		  0 ... #
#			 metric_*.*
#		  AvrMetric*.plt

import os
import sys
import getopt
from os.path import join
import glob
import datalib

DEFAULT_DIRECTORY = ''

FILES_TO_ALTER = ['AvrMetric*.plt']
FILES_TO_RENAME = ['metric_*.plt']
METRICS_TO_RENAME = {'CC':'cc_a_bu', 'SP':'nsp_a_bu', 'CP':'cpl_a_bu', 'NM_wd':'nm_a_wd',
					 'SW':'swi_nsp_a_bu', 'SC':'swi_cpl_a_bu', 'HF':'hf'}


test = False


def usage():
	print 'Usage:  rename_metrics.py [-t] <directory>'
	print '  <directory> may be a run directory or a collection of run directories'
	print '  -t will print out the files that would have been affected, but nothing will be changed'


def parse_args():
	global test
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], 't', ['test'] )
	except getopt.GetoptError, err:
		print str(err) # will print something like "option -a not recognized"
		usage()
		exit(2)

	if len(args) == 1:
		directory = args[0].rstrip('/')
	elif len(args) > 1:
		print "Error: too many arguments"
		usage()
		exit(2)
	elif DEFAULT_DIRECTORY:
		directory = DEFAULT_DIRECTORY
	else:
		usage()
		exit(0)
	
	for o, a in opts:
		if o in ('-t', '--test'):
			test = True
		else:
			print 'Unknown option:', o
			usage()
			exit(2)
	
	return directory


def rename_metrics_in_file(file):
	global test
	tables = datalib.parse(file)
	not_renamed = []
	renamed = []
	for table in tables.values():
		if table.name in METRICS_TO_RENAME:
			renamed.append((table.name, METRICS_TO_RENAME[table.name]))
			table.name = METRICS_TO_RENAME[table.name]
		else:
			not_renamed.append(table.name)
	if renamed:
		if test:
			print 'renaming', renamed, 'in', file
		else:
			datalib.write(file, tables)
	if not_renamed:
		print 'could not rename', not_renamed, 'in', file

def rename_metric_file(file):
	global test
	root, name = os.path.split(file)  # get just the filename from the full path
	name = name[:-4]  # remove .plt
	if 'Random' in file:
		append = '_random'
		name = name[:-7]  # remove _Random
	else:
		append = ''
	metric = name[7:]  # get just the metric type
	if metric in METRICS_TO_RENAME:
		new_metric = METRICS_TO_RENAME[metric]
		new_file = 'metric_' + new_metric + append + '.plt'
		if root:
			new_file = join(root, new_file)
		if test:
			print '  renaming', file, 'to', new_file
		else:
			os.rename(file, new_file)
	else:
		print '  unknown metric:', metric, '; not renaming', file

def rename_metrics_in_dir(directory):
	print 'renaming metrics in', directory
	recent_dir = join(join(directory, 'brain'), 'Recent')

	# Rename the metrics in the AvrMetric* files
	files_to_alter = []
	for expression in FILES_TO_ALTER:
		files_to_alter += glob.glob(join(recent_dir, expression))
	for file in files_to_alter:
		rename_metrics_in_file(file)
	
	# Rename the metric_* files in the epochs
	for root, dirs, files in os.walk(recent_dir):
		break
	for dir in dirs:
		time_dir = join(recent_dir, dir)
		files_to_rename = []
		for expression in FILES_TO_RENAME:
			files_to_rename += glob.glob(join(time_dir, expression))
		for file in files_to_rename:
			rename_metric_file(file)


def main():
	directory = parse_args()
	
	for root, dirs, files in os.walk(directory):
		break
	
	if 'worldfile' not in files and len(dirs) < 1:
		print 'No worldfile and no directories, so nothing to do'
		usage()
		exit(1)
	
	if 'worldfile' in files:
		# this is a single run directory,
		# so just rename the files therein
		rename_metrics(directory)
	else:
		# this is a directory of run directories,
		# so recreate the run directories inside it,
		# and copy the desired pieces into each new run directory
		for run_dir in dirs:
			rename_metrics_in_dir(join(directory, run_dir))


main()
