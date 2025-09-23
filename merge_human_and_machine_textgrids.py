
import alignbrary3 as A

donor_filepath = '/home/jimielke/nc_transcription/w_hck0140d_224_824.TextGrid'
recipient_filepath = '/home/jimielke/nc_transcription/hck0140d_dt.TextGrid'
new_filepath = '/home/jimielke/nc_transcription/hck0140d_dt_merged.TextGrid'

donor_textgrid = A.parseTextGrid(donor_filepath)
recipient_textgrid = A.parseTextGrid(recipient_filepath)


def merge_textgrids(tg1, tg2, tiername1, tiername2):


	for k in tg1.keys():
		if tg1[k][0] == tiername1:
			tiernumber1 = k

	for k in tg2.keys():
		if tg2[k][0] == tiername2:
			tiernumber2 = k

	print(tiername1, 'is tier number', tiernumber1, 'time range', tg1[tiernumber1][1][0][2], 'to', tg1[tiernumber1][1][-1][3])
	print(tiername2, 'is tier number', tiernumber2, 'time range', tg2[tiernumber2][1][0][2], 'to', tg2[tiernumber2][1][-1][3])

	last_pre = -1
	first_post = -1
	for i in range(len(tg2[tiernumber2][1])):
		if tg2[tiernumber2][1][i][3] < tg1[tiernumber1][1][0][2]:
			last_pre = i
		elif tg2[tiernumber2][1][i][2] > tg1[tiernumber1][1][-1][3]:
			first_post = i
			break
	print(last_pre, first_post)
	tg2[tiernumber2][1] = tg2[tiernumber2][1][:last_pre+1] + tg1[tiernumber1][1] + tg2[tiernumber2][1][first_post:]

	return tg2

recipient_textgrid = merge_textgrids(donor_textgrid, recipient_textgrid, 'ME', 'S01')
recipient_textgrid = merge_textgrids(donor_textgrid, recipient_textgrid, 'DC', 'S03')
recipient_textgrid = merge_textgrids(donor_textgrid, recipient_textgrid, 'CD', 'S00')

for k in recipient_textgrid.keys():
	recipient_textgrid[k][1] = A.cleanTier(recipient_textgrid[k][1])

A.writeTextGrid(recipient_textgrid, new_filepath)