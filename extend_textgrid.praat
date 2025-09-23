##################################################################
# extend_textgrid.praat
#
# Add time to the start and/or end of a TextGrid to match a Sound
# Select your Sound and TextGrid objects and select Run.
# If the TextGrid starts later or ends earlier than the Sound, 
# it will be extended.
##################################################################

# count the selected objects and make sure there is one of each
numberOfSelectedTextGrids = numberOfSelected ("TextGrid")
numberOfSelectedSounds = numberOfSelected ("Sound")

if numberOfSelectedTextGrids != 1 or numberOfSelectedTextGrids != 1
	printline Please select exactly one Sound and one TextGrid
else

	# collect the names of the objects in order to refer to them
	textgrid_name$ = selected$ ("TextGrid", 1)
	sound_name$ = selected$ ("Sound", 1)

	# find the start and end time of the Sound
	selectObject: "Sound "+sound_name$
	sound_start = Get start time
	sound_end = Get end time
	printline Sound time range: 'sound_start'-'sound_end'
	
	# find the start and end time of the TextGrid
	selectObject: "TextGrid "+textgrid_name$
	textgrid_start = Get start time
	textgrid_end = Get end time
	printline TextGrid time range: 'textgrid_start'-'textgrid_end'
	
	# compare the TextGrid and Sound
	textgrid_start_difference = textgrid_start - sound_start
	textgrid_end_difference = sound_end - textgrid_end
	
	# extend the start if necessary
	if textgrid_start_difference > 0
		Extend time: textgrid_start_difference, "start"
		printline extended TextGrid start by 'textgrid_start_difference'
	endif

	# extend the end if necessary
	if textgrid_end_difference > 0
		Extend time: textgrid_end_difference, "end"
		printline extended TextGrid end by 'textgrid_end_difference'
	endif

endif




