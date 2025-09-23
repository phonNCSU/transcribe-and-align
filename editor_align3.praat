
##############################################################################
# editor_align3.praat                                    Mar 7, 2024
# Jeff Mielke
#
# realigns the currently selected words to part of the sound
# requires P2FA or MFA
##############################################################################

#
# TO DO:
# handle MFA input tier order
# try on Windows and Mac OS
# maybe fix oddities involving sp etc.

##############################################################################
# settings
##############################################################################
mfa = 1

working_directory$ = "~/scripts/"
p2fa_command$ = "python2 ~/p2fa/align.py"

# mfa_input$ = working_directory$+"editor_align_temp_input/"
# mfa_output$ = working_directory$+"editor_align_temp_output/"
# documents_mfa$ = "~/Documents/MFA/editor_align_temp_input/"
# mfa_command$ = "~/montreal-forced-aligner/bin/mfa_align"
# mfa_dict$ = "~/teaching/ENG536_2021/lab6/slaap_dict2"
# mfa_language$ = "english"
mfa_input_dir$ = working_directory$+"editor_align_temp_input/"
mfa_wav_input$ = mfa_input_dir$+"temp_for_editor_align.wav"
mfa_tg_input$ = mfa_input_dir$+"temp_for_editor_align.TextGrid"
mfa_input$ = mfa_wav_input$+" "+mfa_tg_input$
mfa_output$ = working_directory$+"editor_align_temp_output/temp_for_editor_align.TextGrid"
documents_mfa$ = "~/Documents/MFA/editor_align_temp_input/"
mfa_command$ = "mfa align_one"
mfa_dict$ = "english_us_arpa"
mfa_language$ = "english_us_arpa"
    


uppercase = 0

delete_temp_files = 1
word_tier_is_2 = 0
word_tier_is_not_1 = 1
##############################################################################

call collectInfo
old_start = Get start of selection
old_end = Get end of selection

if mfa == 1
    call readWordsMFA
else
    call readWords
endif

beginPause ("Please select the sound to align these words to")
    boolean ("realign", 1)
endPause ("OK", 1)

start = Get start of selection
end = Get end of selection
call clearTextGrid

if realign
    Extract selected sound (time from 0)
    if mfa == 1
        call reAlignMFA
    else
        call reAlign
    endif
    call readAlignedTextGrid
endif

##############################################################################
# procedures
##############################################################################

procedure collectInfo
    edi$ = Editor info
    tgi$ = TextGrid info
    textgrid$ = extractWord$ (tgi$, "Object name:")
    sndi$ = TextGrid info
    sound$ = extractWord$ (sndi$, "Object name:")

    if mfa == 1
        if word_tier_is_2
            word_tier = 1
        else
            word_tier = extractNumber (edi$, "Selected tier:")
            if word_tier_is_not_1 and word_tier=1
                word_tier = 1
            endif
        endif
        phone_tier = word_tier + 1
    else
        if word_tier_is_2
            word_tier = 2
        else
            word_tier = extractNumber (edi$, "Selected tier:")
            if word_tier_is_not_1 and word_tier=1
                word_tier = 2
            endif
        endif
        phone_tier = word_tier - 1
    endif




endproc


procedure readWordsMFA
    endeditor

    #### MFA ####

    if not fileReadable(mfa_input_dir$)
        system mkdir 'mfa_input_dir$'
    endif
    #if not fileReadable(mfa_output$)
    #    system mkdir 'mfa_output$'
    #endif    
    #### MFA ####

    select TextGrid 'textgrid$'
    start_interval = Get interval at time... 'word_tier' 'old_start'
    end_interval = Get interval at time... 'word_tier' 'old_end'
    start_phone_interval = Get interval at time... 'phone_tier' 'old_start'
    end_phone_interval = Get interval at time... 'phone_tier' 'old_end'
    mfa_transcript$ = "'mfa_input$'temp_for_editor_align.TextGrid"

    #filedelete 'mfa_transcript$'
    #select TextGrid 'textgrid$'
    transcript_text$ = ""
    for interval from start_interval to end_interval
        word$ = Get label of interval... 'word_tier' 'interval'
        if word$ != "sp"
            transcript_text$ = transcript_text$+" "+word$
        endif
    endfor

    editor
endproc



procedure readWords
    endeditor
    select TextGrid 'textgrid$'
    start_interval = Get interval at time... 'word_tier' 'old_start'
    end_interval = Get interval at time... 'word_tier' 'old_end'
    start_phone_interval = Get interval at time... 'phone_tier' 'old_start'
    end_phone_interval = Get interval at time... 'phone_tier' 'old_end'
    transcript$ = "'working_directory$'temp_'textgrid$'_'old_start'_'old_end'.txt"
    filedelete 'transcript$'
    select TextGrid 'textgrid$'
    for interval from start_interval to end_interval
        word$ = Get label of interval... 'word_tier' 'interval'
        if word$ != "sp"
            fileappend 'transcript$' 'word$''newline$'
        endif
    endfor

    editor
endproc

procedure clearTextGrid
    endeditor
    select TextGrid 'textgrid$'
    for interval from start_interval to end_interval-1
        Remove right boundary... 'word_tier' 'start_interval'
    endfor
    Set interval text... 'word_tier' 'start_interval' sp

    for interval from start_phone_interval to end_phone_interval-1
        Remove right boundary... 'phone_tier' 'start_phone_interval'
    endfor
    Set interval text... 'phone_tier' 'start_phone_interval' sp
    editor
endproc

procedure reAlignMFA
    endeditor
    filename$ = "temp_'textgrid$'_'start'_'end'"
    temp_wav$ = "'working_directory$''filename$'.wav"
    # mfa_temp_wav$ = "'mfa_input$'temp_for_editor_align.wav"
    # temp_textgrid$ = "'working_directory$''filename$'.TextGrid"
    select Sound untitled
    # Write to WAV file... 'mfa_temp_wav$'
    Write to WAV file... 'mfa_wav_input$'
    # Resample... 11025 25
    # Write to WAV file... 'temp_wav$'

    #MFA
    excerpt_duration = Get total duration
    printline 'excerpt_duration'
    Create TextGrid: 0, excerpt_duration, "transcript", ""
    Set interval text: 1, 1, transcript_text$

    # Save as text file: mfa_transcript$
    Save as text file: mfa_tg_input$
    #MFA

    plus Sound untitled
    #plus Sound untitled_11025
    Remove

    # if fileReadable(documents_mfa$)
    #     system rm -rf 'documents_mfa$'
    # endif

    # ~/montreal-forced-aligner/bin/mfa_align ~/scripts/editor_align_temp_input/ ~/teaching/ENG536_2021/lab6/slaap_dict2 english ~/scripts/editor_align_temp_output/
    # mfa align_one ~/scripts/editor_align_temp_input/temp_for_editor_align.wav ~/scripts/editor_align_temp_input/temp_for_editor_align.TextGrid english_us_arpa english_us_arpa ~/scripts/editor_align_temp_output/temp_for_editor_align.TextGrid

    full_mfa_command$ = "'mfa_command$' 'mfa_input$' 'mfa_dict$' 'mfa_language$' 'mfa_output$'"
    #system conda activate aligner
    printline 'full_mfa_command$'
    system 'full_mfa_command$'



# mfa align ~/scripts/editor_align_temp_input/ english_us_arpa english_us_arpa ~/scripts/editor_align_temp_output/

endproc



procedure reAlign
    endeditor
    filename$ = "temp_'textgrid$'_'start'_'end'"
    temp_wav$ = "'working_directory$''filename$'.wav"
    temp_textgrid$ = "'working_directory$''filename$'.TextGrid"
    select Sound untitled
    Resample... 11025 25
    Write to WAV file... 'temp_wav$'
    plus Sound untitled
    Remove

    system 'p2fa_command$' 'temp_wav$' 'transcript$' 'temp_textgrid$'
endproc

procedure readAlignedTextGrid
    # flip order and capitalization
    if mfa == 1
        # Read from file... 'mfa_output$'temp_for_editor_align.TextGrid
        Read from file... 'mfa_output$'
        output_phone_tier = 2
        output_word_tier = 1
    else
        Read from file... 'temp_textgrid$'
        output_phone_tier = 1
        output_word_tier = 2
    endif

    Rename... temp
    Shift times by... 'start'
    phone_intervals = Get number of intervals... output_phone_tier
    word_intervals = Get number of intervals... output_word_tier

    for interval from 1 to word_intervals
        select TextGrid temp
        start_time = Get start point... 'output_word_tier' 'interval'
        end_time = Get end point... 'output_word_tier' 'interval'
        mid_time = (start_time+end_time)/2
        label$ = Get label of interval... 'output_word_tier' 'interval'

        if uppercase == 1 and label$ != "sp"
            label$ = replace_regex$ (label$, ".", "\U&", 0)
        endif

        if label$ == "<eps>"
            label$ = ""
        endif

        select TextGrid 'textgrid$'
        if interval = 1
            Insert boundary... 'word_tier' 'start_time'
        endif
        if interval < word_intervals or label$ != "sp"
            Insert boundary... 'word_tier' 'end_time'
            new_interval = Get interval at time... 'word_tier' 'mid_time'
            Set interval text... 'word_tier' 'new_interval' 'label$'
        else
            new_interval = 1
        endif
    endfor

    next_pause = new_interval+1
    select TextGrid 'textgrid$'
    Set interval text... 'word_tier' 'next_pause' sp

    for interval from 1 to phone_intervals
        select TextGrid temp
        start_time = Get start point... 'output_phone_tier' 'interval'
        end_time = Get end point... 'output_phone_tier' 'interval'
        mid_time = (start_time+end_time)/2
        label$ = Get label of interval... 'output_phone_tier' 'interval'
        
        label$ = replace$(label$, "_S", "", 1)
        label$ = replace$(label$, "_B", "", 1)
        label$ = replace$(label$, "_I", "", 1)
        label$ = replace$(label$, "_E", "", 1)

        if label$ == "sil"
            label$ = ""
        endif
        
        select TextGrid 'textgrid$'
        if interval = 1
            Insert boundary... 'phone_tier' 'start_time'
        endif
        if interval < phone_intervals or label$ != "sp"
            Insert boundary... 'phone_tier' 'end_time'
            new_interval = Get interval at time... 'phone_tier' 'mid_time'
            Set interval text... 'phone_tier' 'new_interval' 'label$'
        endif
    endfor

    next_pause = new_interval+1
    select TextGrid 'textgrid$'
    Set interval text... 'phone_tier' 'next_pause' sp

    select TextGrid temp
    Remove

    if delete_temp_files
        filedelete 'temp_wav$'
        filedelete 'transcript$'
        filedelete 'temp_textgrid$'
    endif
    editor
endproc



