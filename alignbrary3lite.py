
# 2024-05-17 updated cleanTier() so that it works again

import os, sys
import decimal

def cleanTier(oldtier, speaker='', tiername=''):

    ''' correct ill-formed intervals in a textgrid tier prior to writing it to a file '''
    omitted = 0
    inserted = 0
    merged = 0
    extended = 0
    shortened = 0
    newtier = []

    for i,interval in enumerate(oldtier):
        oldtier[i][2] = round(interval[2],6)
        oldtier[i][3] = round(interval[3],6)

    for i,interval in enumerate(oldtier):
        # if i in [0,len(oldtier)-1]:
        if i == 0:
            # print(interval)
            newtier.append(interval)
        else:
            # sixtimes = oldtier[i-1][2:4] + interval[2:4] + oldtier[i+1][2:4]
            # positive_duration = interval[2] < interval[3]
            # matching_edges = oldtier[i-1][3] == interval[2], interval[3] == oldtier[i+1][2]

            if interval[2] < interval[3]:
                # if matching_edges == [True, True]:
                    # newtier.append(interval)
                if newtier[-1][3] == interval[2]:
                    newtier.append(interval) #the edges already match
                else:
                    # does the last interval end before the start of this interval?
                    if newtier[-1][3] < interval[2]:
                        if newtier[-1][0] == '':
                            newtier[-1][3] = interval[2] #extend a blank interval to fill the gap
                            newtier.append(interval) 
                            extended += 1
                        elif interval[0] == '':
                            interval[2] = newtier[-1][3] #extend a blank interval to fill the gap
                            newtier.append(interval) 
                            extended += 1
                        else:
                            newtier.append(['', 0, newtier[-1][3], interval[2]]) #insert a blank interval to fill the gap
                            newtier.append(interval) 
                            inserted += 1
                    # does this interval end before the start of the next interval?
                    # elif interval[3] < oldtier[i+1][2]:
                    #     if interval[0] == '':
                    #         newtier.append(interval) 
                    #         newtier[-1][3] = interval[2] #extend a blank interval to fill the gap
                    #         extended += 1
                    #     else:
                    #         newtier.append(interval) 
                    #         newtier.append(['', 0, interval[3], oldtier[i+1][2]]) #insert a blank interval to fill the gap
                    #         inserted += 1

                    # does the last interval end after the start of this interval?
                    elif newtier[-1][3] > interval[2] and newtier[-1][3] < interval[3]:
                        # newtier.append([interval[0], newtier[-1][2]]+interval[2:]) #shorten interval to avoid overlap
                        # newtier.append([interval[0], interval[1], newtier[-1][3]], interval[3]) #shorten interval to avoid overlap
                        if newtier[-1][0] == '':
                            newtier[-1][3] = interval[2] #shorten interval to avoid overlap
                            newtier.append(interval) 
                            shortened += 1
                        elif interval[0] == '':
                            interval[2] = newtier[-1][3] #shorten interval to avoid overlap
                            newtier.append(interval) 
                            shortened += 1
                        else:
                            newtier[-1][3] = round(statistics.mean([interval[2],newtier[-1][3]]),6) #shorten both intervals to avoid overlap
                            interval[2] = round(statistics.mean([interval[2],newtier[-1][3]]),6) #shorten both intervals to avoid overlap
                            newtier.append(interval) 
                            shortened += 1
                        #print (' ...cleanTier() shortened an interval by', newtier[-1][2]-interval[1], ':', interval[2] < interval[3], matching_edges, sixtimes)
                        # print (' ...cleanTier() shortened an interval by', newtier[-1][2]-interval[1], ':', newtier[-1])
                    else:    
                        print (' WARNING: edges still do not match: tell Jeff...', i, len(oldtier), speaker, tiername, interval[2] < interval[3], matching_edges, oldtier[i-1][2:4] + interval[2:4] + oldtier[i+1][2:4])
                        newtier.append(interval)
            else:
                if newtier[-1][3] == oldtier[i+1][2]:  #omit intervals that wouldn't even leave a gap
                    omitted += 1
                elif abs(newtier[-1][3]-oldtier[i+1][2])<0.00001:  #omit interval that will require a small adjustment to prevent a gap
                    omitted += 1

                elif matching_edges == [True, True]:
                    print (' WARNING: nonpositive duration but edges match: tell Jeff', interval[2] < interval[3], matching_edges, oldtier[i-1][2:4] + interval[2:4] + oldtier[i+1][2:4])
                    newtier.append(interval)
                else:
                    print (' WARNING: nonpositive duration but cannot just remove interval: tell Jeff', interval[2] < interval[3], matching_edges, oldtier[i-1][2:4] + interval[2:4] + oldtier[i+1][2:4])
                    newtier.append(interval)
        # if len(newtier) > 1 and newtier[-2][0]+newtier[-1][0] == '':
        #     # print(newtier[-2])
        #     newtier[-2][2] = newtier[-1][2]
        #     newtier.pop()
        #     merged += 1

    print (' '+speaker,tiername+': CleanTier()','omitted',omitted,'extended',extended,'inserted',inserted,'merged',merged,'shortened',shortened)

    return newtier

def writeTextGrid(textgrid, path_to_write):

    ''' write a textgrid that has been previously read and possibly changed using this library '''

    # tiers_to_write = []

    tiernumbers = list(textgrid.keys())
    tiernumbers.sort()

    tierlines = []
    all_xs = []
    for tiernumber in tiernumbers:

        intervals = textgrid[tiernumber][1]
        tier_xs = []
        intervallines = []
        for i,interval in enumerate(intervals):
            intervallines += ['        intervals ['+str(i+1)+']:',
                              '            xmin = '+str(interval[2])+" ", 
                              '            xmax = '+str(interval[3])+" ", 
                              '            text = "'+interval[0]+'" '] 
            tier_xs += interval[2:4]

        tierlines.append('    item ['+tiernumber+']:')
        tierlines.append('        class = "IntervalTier" ')
        tierlines.append('        name = "'+textgrid[tiernumber][0]+'" ')
        tierlines.append('        xmin = '+str(min(tier_xs))+" ") 
        tierlines.append('        xmax = '+str(max(tier_xs))+" ") 
        tierlines.append('        intervals: size = '+str(len(intervals))+" ")
 
        tierlines += intervallines
        all_xs += tier_xs

    output = ['File type = "ooTextFile"',
              'Object class = "TextGrid"',
              '',
              'xmin = '+str(min(all_xs))+" ",
              'xmax = '+str(max(all_xs))+" ",
              'tiers? <exists> ',
              'size = '+str(len(textgrid.keys()))+" ",
              'item []: '
              ] + tierlines

    with open(path_to_write, 'w') as f:
        for o in output:
            f.write(o+'\n')

def parseTextGrid(path_to_textgrid, slope=1, intercept=0):

    ''' read the textgrid file and produce a dictionary with an entry for each tier.  
        Each entry consists of the tier name, followed by a list of intervals, 
        where each interval is represented by its label, the repetition number 
        for that label, and its start and end times, like this:

        {'1': ['segment', [
                           ['seg', 1, 101.24574935642588, 101.78244178091559], 
                           ['seg', 2, 101.78244178091559, 105.15990272813534]

                          ]
              ], 

         '2': ['word',    [
                           ['word', 1, 101.24574935642588, 105.15990272813534]
                          ]
              ]
        }
    '''

    textgrid = open(path_to_textgrid).readlines()

    textgrid_d = {}
    tier_number = '-1'
    tier_name = '-1'

    #print ([t.strip() for t in textgrid][:10])
    #if 'ooTextFile short' in textgrid[0] or 'File type = "ooTextFile"' in textgrid[0]:

    if 'F\x00i\x00l\x00e\x00' in textgrid[0]:
        print ('TextGrid is writen in UTF-16.\nPlease re-save your textgrid as UTF-8\n(see Praat... Preferences... Text writing preferences).')
        sys.exit()

    elif 'Praat chronological TextGrid text file' in textgrid[0]:
        #IT'S A CHRONOLOGICAL TEXTGRID FILE
        print ('TextGrid is in chronological text file format.\nPlease re-save your textgrid as a text file or short text file.')
        sys.exit()

    elif not 'item []:' in [t.strip() for t in textgrid]: 
        #IT'S A SHORT TEXTGRID FILE
        #print (path_to_textgrid, 'IS SHORT')
        tier_counter = 1
        for i in range(3, len(textgrid)):
            if textgrid[i-1].startswith('\"IntervalTier\"'):
                tier_number = str(tier_counter)
                tier_counter += 1
                tier_name = textgrid[i].split('\"')[1]
                textgrid_d[tier_number] = [tier_name, []]
                intervals = textgrid_d[tier_number][1]
                #labels_and_numbers = []

            elif textgrid[i].count('\"') == 2 and not '\"IntervalTier\"' in textgrid[i]:
                label = textgrid[i].split('\"')[1]
                xmin = decimal.Decimal(textgrid[i-2].strip())
                xmax = decimal.Decimal(textgrid[i-1].strip())
                #JM added 3/1/20
                xmin = float(xmin)
                xmax = float(xmax)
                intervals.append([label, 0, xmin, xmax])

    else:
        #IT'S A LONG TEXTGRID FILE        
        #print (path_to_textgrid, 'IS LONG')
        for i in range(3, len(textgrid)):
            if 'IntervalTier' in textgrid[i]:
                tier_number = textgrid[i-1].split('[')[1].split(']')[0]
                tier_name = textgrid[i+1].split('\"')[1]
                textgrid_d[tier_number] = [tier_name, []]
                intervals = textgrid_d[tier_number][1]
                #labels_and_numbers = []

            elif 'text =' in textgrid[i]:
                # label = removeNonAscii(textgrid[i].split('\"')[1])
                # JM changed this 12/13/19 to handle quotes in textgrid labels
                label =textgrid[i][textgrid[i].find('"')+1:textgrid[i].rfind('"')]

                xmin = decimal.Decimal(textgrid[i-2].split('=')[1].strip())
                xmax = decimal.Decimal(textgrid[i-1].split('=')[1].strip())
                #JM added 3/1/20
                xmin = float(xmin)
                xmax = float(xmax)
                intervals.append([label, 0, xmin, xmax])

    return textgrid_d
