###################################################################################################
# insert_scripted_text.praat               Jeff Mielke                       2024-05-29
#
# clears out selected textgrid intervals and optionally replaces them with new text from a csv file
#
# The script expects scripted_speech_for_praat.csv to be in a subfolder of  
# your home directory named scripts (e.g., /Users/username/scripts)
#
# Run this from the editor. If you add more scripts to the csv file, add them as options in the script
# (see the "option:" lines below). If you change the csv file while using Praat, make sure to delete the Table
# from your objects list so that it gets read again.
###################################################################################################

# PREPARE OBJECTS AND INFORMATION

@openCSVfile

edi$ = Editor info
tgi$ = TextGrid info
# sndi$ = TextGrid info
selected_tier = extractNumber (edi$, "Selected tier:")
textgrid$ = extractWord$ (tgi$, "Object name:")

# EXAMINE SELECTED INTERVAL

selection_start = Get start of selection
selection_end = Get end of selection
selection_duration = selection_end - selection_start

endeditor
	selectObject: "TextGrid "+textgrid$
	start_interval = Get interval at time: selected_tier, selection_start
	end_interval = Get interval at time: selected_tier, selection_end
editor

beginPause: "Please select the scripted text to use"
    choice: "selected script", 1
    	option: "None (leave blank)"
	option: "Hmong part B passage"
	option: "test script"
endPause ("OK", 1)

printline scripted text 'selected_script$'

# CLEAR THE SELECTION
    
@clearSelected

# INSERT THE SCRIPTED TEXT

if selected_script$ != "None (leave blank)"

	@ find_script_in_table

	if script_first_row == 999999
		printline did not find script 'selected_script$' in Table 'script_filename$'
	else
		@ insertText
	endif

endif

####################################################################################
# PROCEDURES
####################################################################################

procedure openCSVfile
	endeditor
		readpath$ = homeDirectory$+"/scripts/"
		script_filename$ = "scripted_speech_for_praat"
	
		nocheck selectObject: "Table "+script_filename$
		if numberOfSelected ("Table") == 0
			Read Table from comma-separated file: readpath$+script_filename$+".csv"
			printline opened 'script_filename$'
		else
			printline 'script_filename$' is already open
		endif
	editor
endproc

procedure clearSelected
	endeditor
		select TextGrid 'textgrid$'
		for interval from start_interval to end_interval-1
			Remove right boundary: selected_tier, start_interval
		endfor
		Set interval text: selected_tier, start_interval, ""
	editor
endproc

procedure find_script_in_table
	total_speech_duration = 0
	total_pause_duration = 0
	endeditor
		selectObject: "Table "+script_filename$
		table_rows = Get number of rows
		script_first_row = 999999
		script_last_row = 0
		for r from 1 to table_rows
			script_name$ = Get value: r, "Script"
			if script_name$ == selected_script$
				row_speech_duration = Get value: r, "Speech_duration"
				row_pause_duration = Get value: r, "Pause_duration"
				script_first_row = min(script_first_row, r)
				script_last_row = max(script_last_row, r)
				total_speech_duration = total_speech_duration + row_speech_duration
				total_pause_duration = total_pause_duration + row_pause_duration
			endif
		endfor
		total_script_duration = total_speech_duration + total_pause_duration
	editor
endproc

procedure insertText
	pasting_progress = 0
	current_interval = start_interval

	for r from script_first_row to script_last_row
		endeditor
			selectObject: "Table "+script_filename$
			row_text$ = Get value: r, "Text"
			row_speech_duration = Get value: r, "Speech_duration"
			row_pause_duration = Get value: r, "Pause_duration"
		
			new_interval_start = selection_start + pasting_progress*selection_duration
			new_interval_end = new_interval_start + row_speech_duration*selection_duration/total_script_duration
			new_pause_end = new_interval_end + row_pause_duration*selection_duration/total_script_duration
			pasting_progress = pasting_progress + (new_pause_end - new_interval_start)/selection_duration
	
			selectObject: "TextGrid "+textgrid$
			Insert boundary: selected_tier, new_interval_start
			current_interval = current_interval + 1
			Set interval text: selected_tier, current_interval, row_text$
			Insert boundary: selected_tier, new_interval_end
			current_interval = current_interval + 1
		editor
	endfor
endproc

