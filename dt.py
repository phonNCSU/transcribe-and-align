

''' 

vosk and pyannote installation (see https://pypi.org/project/pyannote.audio/)

pip install vosk

conda create -n pyannote python=3.8
conda activate pyannote
conda install pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 -c pytorch

pip install pyannote.audio

# usage:

conda activate pyannote
python dt.py --input /phon/Raleigh/wav/ral3171d.wav

# this is similar to: 
python transcribe_wav.py --input /phon/Raleigh/wav/ral3171d.wav --limiter 1

#this script was updated 2024-02-21 to ensure that it uses the GPU

'''


# nvidia-smi
import torch
torch.cuda.empty_cache()

import alignbrary3lite as A
import datetime

# instantiate pretrained speaker diarization pipeline
from pyannote.audio import Pipeline

import sys
import os
import wave
import subprocess
import json
import contextlib
import argparse

#PARSE ARGUMENTS
parser = argparse.ArgumentParser(description='diarize and transcribe a sound file using vosk and pyannote, and optionally limit using sox and compand')
parser.add_argument('--input', default='', help='the path to the sound file')
# parser.add_argument('--transcriber', default = 'vosk', help='the transcription program to use (vosk or whisper)')
# parser.add_argument('--model', default='/phon/vosk/vosk-model-en-us-0.22', help='the language model to use for transcription')
# parser.add_argument('--limiter', default='1', help='whether to limit')
parser.add_argument('--transcriber', default = 'whisper', help='the transcription program to use (vosk or whisper)')
parser.add_argument('--model', default='medium.en', help='the language model to use for transcription')
parser.add_argument('--limiter', default='0', help='whether to limit')
parser.add_argument('--expand', default='1', help='expand speech intervals by 50 ms')
args = parser.parse_args()

if args.transcriber == 'vosk':
    from vosk import Model, KaldiRecognizer, SetLogLevel
elif args.transcriber == 'whisper':
    import whisper
    model = whisper.load_model(args.model)
else:
    print('please use --transcriber vosk or --transcriber whisper')


def diarize_to_textgrid(sound):

    diarization = pipeline(sound)

    speaker_tier = {}
    diarized_textgrid = {}

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
        if speaker in speaker_tier.keys():
            speaker_tier_name = speaker_tier[speaker]
        else:
            speaker_tier_name = str(len(speaker_tier.keys())+1)
            speaker_tier[speaker] = speaker_tier_name
            diarized_textgrid[speaker_tier_name] = [speaker, []]
        if diarized_textgrid[speaker_tier_name][1] == []:
            diarized_textgrid[speaker_tier_name][1].append(['', 1, 0, turn.start])
        else:
            diarized_textgrid[speaker_tier_name][1].append(['', 1, diarized_textgrid[speaker_tier_name][1][-1][3], turn.start])
        diarized_textgrid[speaker_tier_name][1].append([speaker, 1, turn.start, turn.end])

    return diarized_textgrid
    



def transcribe_vosk():
    results = []
    subs = []
    while True:
        # data = process.stdout.read(4000)
        data = wf.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(rec.Result())
    results.append(rec.FinalResult())

    last_word_xmax = 0
    last_phrase_xmax = 0
    phrase_intervals = []
    word_intervals = []
    confidence_intervals = []

    labels = []
    for i, res in enumerate(results):
        jres = json.loads(res)
        if not 'result' in jres:
           continue
        words = jres['result']
        for j in range(len(words)):
            line = words[j] 
            # print (line)
            xmin = line['start']
            xmax = line['end']
            label = line['word']
            confidence = str(line['conf'])

            if xmin > last_word_xmax:
                word_intervals.append(['',0,last_word_xmax,xmin])
                word_intervals.append([label,0,xmin,xmax])
                confidence_intervals.append(['',0,last_word_xmax,xmin])
                confidence_intervals.append([confidence,0,xmin,xmax])
            elif xmin == last_word_xmax:
                word_intervals.append([label,0,xmin,xmax])
                confidence_intervals.append([confidence,0,xmin,xmax])
            else:
                word_intervals[-1][0] += ' '+label
                word_intervals[-1][3] = xmax
                confidence_intervals[-1][0] += ' '+confidence
                confidence_intervals[-1][3] = xmax

            last_word_xmax = xmax
 

        line = words[0:]
        xmin = line[0]['start']
        xmax = line[-1]['end']
        label = " ".join([l['word'] for l in line])

        # added the if phrase_intervals == [] part 6/13/22 
        if phrase_intervals == [] or xmin > last_phrase_xmax:
            phrase_intervals.append(['',0,last_phrase_xmax,xmin])
            phrase_intervals.append([label,0,xmin,xmax])
        else:
            phrase_intervals[-1][0] += ' '+label
            phrase_intervals[-1][3] = xmax

        last_phrase_xmax = xmax
        labels.append(label)

    transcription = ' '.join(labels)

    return transcription

def transcribe_whisper():
    result = model.transcribe(temp_clip)
    # print(result['text'])
    return result['text']

def Sort(sub_li):
    return(sorted(sub_li, key = lambda x: -x[1]))    
  

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

print ("imported libraries...")

#####################################################################################
# interpret the user input and do preprocessing
#####################################################################################

wav_path = args.input
# tg_path = wav_path.split('/')[-1].replace('.wav','_dt.TextGrid').replace('.WAV','_dt.TextGrid')
tg_path = wav_path.split('/')[-1].replace('.wav','.TextGrid').replace('.WAV','.TextGrid')

temp_long_sound = 'temp_long.wav'

with contextlib.closing(wave.open(wav_path,'r')) as f:
    frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)

# resample and also apply limiter if requested.
if args.limiter == '1':
    sox_command = ' '.join(['sox', wav_path, '-b 16', temp_long_sound, 'rate 16000', 'remix 1', 'compand 0,0.3 0:-50,-10,-20,-10,-10,-3 -1 -6 0.3 gain -n -0.1'])
    print('resampling and compressing sound file...')
else:
    sox_command = ' '.join(['sox', wav_path, '-b 16', temp_long_sound, 'rate 16000', 'remix 1'])
    print('resampling sound file...')
# print(sox_command)
os.system(sox_command)

#####################################################################################
# diarization
#####################################################################################

print('starting diarization...')
started_diarization = datetime.datetime.now()

file_path = os.path.realpath(__file__)
file_dir = file_path.replace('dt.py','').replace('dtw.py','')
if os.path.exists(file_dir+'pyannote_token.txt'):

    with open(file_dir+'pyannote_token.txt') as f:
        lines=f.readlines()
        pyannote_token = lines[0].strip()
else:

    print ('##################################################################')
    print ('Could not find '+file_dir+'pyannote_token.txt')
    print ('This script requires a token obtained from the pyannote developer.')
    print ('Please obtain a token and paste it into the first line of a text\nfile called pyannote_token.txt and put that file in the same\nlocation as dt.py')
    print ('##################################################################')
    exit()

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
                                    use_auth_token=pyannote_token)
pipeline.to(torch.device("cuda"))

# apply pretrained pipeline
diarized_textgrid = diarize_to_textgrid(temp_long_sound)
# A.writeTextGrid(diarized_textgrid, 'diarized_only_'+tg_path)
# diarized_textgrid = A.parseTextGrid('diarized_only_'+tg_path)


finished_diarization = datetime.datetime.now()
diarization_time = finished_diarization - started_diarization
print('diarization took', round(diarization_time.total_seconds()), 'seconds')

#####################################################################################
# transcription
#####################################################################################

print('starting transcription...')
started_transcription = datetime.datetime.now()

# VOSK-SPECIFIC PREPARATION
model_name = args.model
if args.transcriber == 'vosk':
    SetLogLevel(-1)
    sample_rate=16000
    model = Model(model_name)
    print ('using model', model_name)
    rec = KaldiRecognizer(model, sample_rate)
    # print('aa')
    rec.SetWords(True)

words_by_speaker = {}

total_intervals = sum([len(tier[1]) for tier in diarized_textgrid.values()])

processed_intervals = 0

for tier_number in diarized_textgrid.keys():
    words_by_speaker[tier_number] = 0
    for i,turn in enumerate(diarized_textgrid[tier_number][1]):
        processed_intervals += 1

        if diarized_textgrid[tier_number][1][i][0] != '':

            temp_clip = 'a_t_temp.wav'

            os.system('sox '+temp_long_sound+' '+temp_clip+' trim '+str(turn[2])+' '+str(turn[3]-turn[2]))

            if args.transcriber == 'vosk':
                wf = open(temp_clip, "rb")
                wf.read(44) # skip header
                transcription = transcribe_vosk()
            elif args.transcriber == 'whisper':
                transcription = transcribe_whisper()
            else:
                print('please choose vosk or whisper')

            print('['+str(processed_intervals)+'/'+str(total_intervals)+']', diarized_textgrid[tier_number][0],
                  str(round(turn[2],3)), '-', str(round(turn[3],3)), ':', transcription)

            words_by_speaker[tier_number] += len(transcription.split(' '))
            diarized_textgrid[tier_number][1][i][0] = transcription

print ('###############################################################')

word_counts = []
for tier_number in words_by_speaker.keys():
    print(diarized_textgrid[tier_number][0], 'has', words_by_speaker[tier_number], 'words')
    word_counts.append([tier_number, words_by_speaker[tier_number]])
word_counts = Sort(word_counts)

sorted_textgrid = {}

# sort tiers and clean them up (removing boundaries between empty labels)
tg_max_time = 0
for s,x in enumerate(word_counts):
    # cleaned_up_tier = diarized_textgrid[x[0]]
    cleaned_up_tier = [diarized_textgrid[x[0]][0].replace('PEAKER_', ''), []]
    last_label = 'NA'
    for interval in diarized_textgrid[x[0]][1]:
        if last_label == '' and interval[0] == '':
            cleaned_up_tier[1][-1][3] = interval[3]
        else:
            cleaned_up_tier[1].append(interval)

        last_label = interval[0]

    sorted_textgrid[str(s)] = cleaned_up_tier

    tg_max_time = max(tg_max_time, cleaned_up_tier[1][-1][3])

if args.expand == '1':
    sorted_textgrid = expand_intervals(sorted_textgrid)

##############

wav_duration = 0
if os.path.isfile(wav_path):
    
    with contextlib.closing(wave.open(wav_path,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        wav_duration = frames / float(rate)

mintime = 0
maxtime = wav_duration

for k in sorted_textgrid.keys():
    sorted_textgrid[k][1] = A.cleanTier(sorted_textgrid[k][1])

for k in sorted_textgrid.keys():
    if sorted_textgrid[k][1][0][2] > mintime:
        if sorted_textgrid[k][1][0][0] == '':
            sorted_textgrid[k][1][0][2] = mintime
        else:
            sorted_textgrid[k][1] = [['',0,mintime,sorted_textgrid[k][1][0][2]]]+sorted_textgrid[k][1]
    if sorted_textgrid[k][1][-1][3] < maxtime:
        if sorted_textgrid[k][1][-1][0] == '':
            sorted_textgrid[k][1][-1][3] = maxtime
        else:
            sorted_textgrid[k][1] = sorted_textgrid[k][1]+[['',0,sorted_textgrid[k][1][-1][3],maxtime]]

##############

A.writeTextGrid(sorted_textgrid, tg_path)
print('wrote transcript with', len(word_counts),'speakers to', tg_path)
finished_transcription = datetime.datetime.now()
transcription_time = finished_transcription - started_transcription
with open('dt_log.txt', 'a') as f:
    f.write('\t'.join([started_diarization.strftime("%Y-%m-%d %H:%M:%S"), wav_path, args.transcriber+':'+model_name, tg_path, str(duration), str(len(word_counts)), str(round(diarization_time.total_seconds())), str(round(transcription_time.total_seconds()))])+'\n')

print('diarization took', round(diarization_time.total_seconds()), 'seconds')
print('transcription took', round(transcription_time.total_seconds()), 'seconds')
print ('###############################################################')
