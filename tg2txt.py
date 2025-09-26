import alignbrary3lite as A
import argparse
import datetime

#PARSE ARGUMENTS
parser = argparse.ArgumentParser(description='convert a textgrid transcript to a more human-readable format')
parser.add_argument('--input', default='', help='the path to the textgrid file')
parser.add_argument('--concatenate', default='1', help='concatenate consecutive speaker turns')
parser.add_argument('--omit_phone', default='1', help='omit tiers with phone in the tier name')
args = parser.parse_args()

output_filepath = args.input.replace('.TextGrid','.txt')
print(output_filepath)
textgrid = A.parseTextGrid(args.input)

all_turns = []

for k in textgrid.keys():
	speaker = textgrid[k][0]
	# print(speaker)
	if args.omit_phone=='1' and ' - phones' in speaker:
		pass
	else:
		if args.omit_phone=='1':
			speaker = speaker.replace(' - words', '')
		print(speaker)
		for interval in textgrid[k][1]:
			if interval[0] != '':
				all_turns.append([interval[2],interval[3],speaker,interval[0]])

all_turns.sort()

formatted_turns = []
last_speaker = ''

for turn in all_turns:
	formatted_time = '['+str(datetime.timedelta(seconds=round(turn[0])))+'-'+str(datetime.timedelta(seconds=round(turn[1])))+']'
	speaker = turn[2]
	text = turn[3]

	if args.concatenate=='1' and speaker==last_speaker:
		formatted_turns[-1][0] = formatted_turns[-1][0].split('-')[0]+'-'+formatted_time.split('-')[1]
		formatted_turns[-1][2] = formatted_turns[-1][2] + ' ' + text
	else:
		formatted_turns.append([formatted_time, speaker, text])

	last_speaker = speaker

with open(output_filepath, 'w') as f:
	for turn in formatted_turns:
		f.write(turn[0]+'\n')
		f.write(turn[1]+': '+turn[2]+'\n')
		f.write('\n')

print('wrote', len(formatted_turns), 'turns to', output_filepath)
