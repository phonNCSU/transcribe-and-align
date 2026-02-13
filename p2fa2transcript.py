
'''

python ~/scripts/phonNCSU/transcribe-and-align/p2fa2transcript.py --input Mylah_P2FA.TextGrid --output Mylah.TextGrid

'''



def expand_intervals(one_textgrid, expand_by=0.050):

    tg_keys = one_textgrid.keys()

    for k in tg_keys:
        one_tier = one_textgrid[k][1]
        # print (one_tier)
        for i in range(len(one_tier)):
            if one_tier[i][0] != '':
                if i > 0:
                    if one_tier[i-1][0] == '': # if the left context is silence
                        if one_tier[i-1][2]  < one_tier[i][2]-expand_by: # if it's longer than 50ms
                            earlier_start = one_tier[i][2]-expand_by # we will move the boundary by 50ms
                        else:                                   # if it's no more than 50ms
                            earlier_start = one_tier[i-1][2] # take the whole pause (it will be filtered out)
                        one_tier[i][2]   = earlier_start # start this interval earlier
                        one_tier[i-1][3] = earlier_start # end the left context earlier
                if i < len(one_tier)-1:
                    if one_tier[i+1][0] == '': # if the right context is silence
                        if one_tier[i+1][3]  > one_tier[i][3]+expand_by: # if it's longer than 50ms
                            later_end = one_tier[i][3]+expand_by # we will move the boundary by 50ms
                        else:                                   # if it's no more than 50ms
                            later_end = one_tier[i+1][3] # take the whole pause (it will be filtered out)
                        one_tier[i][3]   = later_end # end this interval later
                        one_tier[i+1][2] = later_end # start the right context later to match

        # print (len(one_tier), 'before filtering')
        one_tier = [interval for interval in one_tier if interval[2] < interval[3]] # filter out zero-length intervals
        # print (len(one_tier), 'after filtering')
        # print (one_tier)

        one_textgrid[k][1] = one_tier
    return one_textgrid

import alignbrary3lite as A

import argparse

# COLLECT USER INPUT (WHAT FILE TO READ AND WHAT TO NAME THE TIER (IF NOT "transcript"))
parser = argparse.ArgumentParser(description='Read a P2FA textgrid and make a transcript for realigning with MFA')
parser.add_argument('--input', default='xxx', help='the path to read')
parser.add_argument('--output', default='xxx', help='the path to write')
parser.add_argument('--min', default='0.2', help='the minimum pause duration')
args = parser.parse_args()

min_pause = float(args.min)
tg = A.parseTextGrid(args.input)

tiername = args.input.split('/')[-1].replace('_P2FA','').replace('.TextGrid','')
print (tiername)

wordtier = tg['2'][1]

chunktier = []
between_chunks = True

for [text, nothing, xmin, xmax] in wordtier:
	if text == 'sp':
		if xmax-xmin >= min_pause or len(chunktier)==0:
			chunktier.append(['', nothing, xmin, xmax])
			between_chunks = True
		else:
			chunktier[-1][3] = xmax

	elif between_chunks:
		chunktier.append([text.lower(), nothing, xmin, xmax])
		between_chunks = False
	else:
		chunktier[-1][0] = chunktier[-1][0]+' '+text.lower()
		chunktier[-1][3] = xmax

# print(chunktier)

new_tg = {'1':[tiername,chunktier]}
new_tg = expand_intervals(new_tg, expand_by=0.1)

pauses=[]
texts=[]

for w in new_tg['1'][1]:
	[text, nothing, xmin, xmax] = w
	duration = round(xmax-xmin,3)
	if text=='':
		#print(duration, 'pause')
		pauses.append(duration)
	else:
		#print(duration, 'text')
		texts.append(duration)

print (len(texts),'text chunks')
print ('longest chunk is',max(texts),'seconds')

A.writeTextGrid(new_tg, args.output)