
import argparse
import alignbrary3 as A
import os

# COLLECT USER INPUT (WHAT FILE TO READ AND WHAT TO NAME THE TIER (IF NOT "transcript"))
parser = argparse.ArgumentParser(description='Repair textgrids that have gaps and/or overlapping intervals')
parser.add_argument('--input', default='xxx', help='the path to read')
parser.add_argument('--output', default='xxx', help='the path to write')
args = parser.parse_args()

filenames = [i for i in os.listdir(args.input) if i.endswith('.TextGrid')]

# print(filenames)

for i in range(len(filenames)):

	tg = A.parseTextGrid(args.input+filenames[i])

	print(filenames[i])
	mintime = 999999999
	maxtime = -999999999
	for k in tg.keys():
		tg[k][1] = A.cleanTier(tg[k][1])
		# print(filenames[i], 'tier', k, tg[k][1][0][2], tg[k][1][-1][3])
		mintime = min(mintime, tg[k][1][0][2])
		maxtime = max(maxtime, tg[k][1][-1][3])

	for k in tg.keys():
		if tg[k][1][0][2] != mintime:
			print ('tier', k, 'does not match textgrid minimum time')
		if tg[k][1][-1][3] != maxtime:
			print ('tier', k, 'does not match textgrid maximum time')

	# print(mintime, maxtime)
	A.writeTextGrid(tg, args.output+filenames[i])