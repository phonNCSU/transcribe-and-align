

# make a dt batch file for all wav files in a directory

import os

wav_files = [fn for fn in os.listdir() if fn.endswith('.wav')]

wav_files.sort()

with open('batch_file', 'w') as f:
    f.write('#!/bin/bash\n')
    for fn in wav_files:
        f.write('python /phon/vosk/dt.py --input '+fn+'\n')

print ('created batch_file. Please rename it and make it executable:')
print ('mv batch_file jeffs_batch_file')
print ('chmod +x jeffs_batch_file')
