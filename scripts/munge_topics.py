#python munge_topics.py --model FILE --text FILE --filenum NUM --output FILE
# munges Mallet topic-states into a space-delimited file with one word/topic pair per line
# Note: atopical stopwords are assigned a topic of -1
#
# --model FILE is a pre-trained topic model
# --text FILE is a file of raw text to sync the topic assignments with
# --filenum NUM is the id of the file associated with the topics of interest
# --output FILE is the file to output the completed topic list

import re
import sys

OPTS = {}
for aix in range(1,len(sys.argv)):
    if len(sys.argv[aix]) < 2 or sys.argv[aix][:2] != '--':
        #filename or malformed arg
        continue
    elif aix < len(sys.argv) - 1 and len(sys.argv[aix+1]) > 2 and sys.argv[aix+1][:2] == '--':
        #missing filename
        continue
    OPTS[sys.argv[aix][2:]] = sys.argv[aix+1]

modelfile = []
with open(OPTS['model'], 'r') as f:
    modelfile = f.readlines()

textfile = []

with open(OPTS['text'], 'r') as f:
    textfile = ' '.join(f.readlines()).lower().split()

#model format: 0 dgb_data/122.txt 0 0 competition 10
renums = re.compile('[0-9]+')

output = []
FOUNDFILE = False
textix = 0
HYPHENATED = False
for line in modelfile:
    if line[0] == '#': #ignore comment lines
        continue
    msline = line.strip().split()
    if not FOUNDFILE:
        #haven't found the correct section of the topic model yet
        if renums.search(msline[1]).group(0) == OPTS['filenum']:
            #now we have!
            FOUNDFILE = True
    if FOUNDFILE:
        #we've found the correct section of the topic model
        if renums.search(msline[1]).group(0) != OPTS['filenum']:
            #...aaaand we've left it behind
            FOUNDFILE = False
            break
        while msline[4] not in ' '.join(re.split('\.|\?|!| |,|-|\'|\d|:|;',textfile[textix])).split():
            #sys.stderr.write(str(msline[4]) + ' ?= ' + str(' '.join(re.split('\.|\?|!| |,|-|\'|\d|:|;',textfile[textix])).split())+'\n')
            if not HYPHENATED:
                output.append(textfile[textix] + ' -1')
            textix += 1
            HYPHENATED = False
        if not HYPHENATED:
            #if the raw word is hyphenated, we only keep the first piece (arbitrary)
            # otherwise we'll have duplicate words and the topic file will get out of sync with the coherence file
            output.append(textfile[textix] + ' ' + msline[5])
        if '-' in textfile[textix]:
            #if the raw word is hyphenated, we only keep the first piece (arbitrary)
            # otherwise we'll have duplicate words and the topic file will get out of sync with the coherence file
            HYPHENATED = True
            continue
        textix += 1
        

if OPTS['output'] == '-':
    sys.stdout.write('\n'.join(output))
else:
    with open(OPTS['output'], 'w') as f:
        f.write('\n'.join(output))
