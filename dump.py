#! python3
# dump.py - Dumps contents of shelf into csv.
# Usage: python dump.py > dump.csv

import os
import glob
import shelve

data_path = os.path.join(os.getcwd(), 'data', '*.dat')
files = []
for file in glob.glob(data_path):
	files.append(os.path.basename(file[:-4]))
	db = shelve.open(os.path.join(os.getcwd(), 'data', file[:-4]))
	print(str(os.path.basename(file[:-4])))
	if os.path.basename(file[:-4]) in ['daily', 'dailysilvercar', 'sixttransition']:
		for k,v in sorted(db.items()):
			print(k  + ',' + v[1] + ',' + v[2] + ',' + v[3])
	else:
		for k, v in sorted(db.items()):
			print(k + ',' + str(v))
	print()
	db.close()