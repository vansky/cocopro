#python munge_doctopics.py --model FILE --text FILE --output FILE
# munges Mallet output-doc-topics file into a space-delimited file with one word/topic pair per line
# --model FILE is an inferred topic model using mallet's  pre-trained topic model
# --text FILE is a file of raw text to sync the topic assignments with
# --output FILE is the file to output the completed topic list

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

model = {}
with open(OPTS['model'], 'r') as f:
   for line in f.readlines():
       if line[0] == '#':
           #comment
           continue
       sline = line.strip().split()
       key = int(sline[1].split('/')[1]) #key is the discourse chunk of textFile
       model[ key ] = []
       for i in range(2,len(sline),2):
           model[key].append( (sline[i], float(sline[i+1])) ) #[ (topic,wt) , ... ]
    
output = []
discourse_ix = 0
with open(OPTS['text'], 'r') as f:
    for line in f.readlines(): #' '.join(f.readlines()).lower().split()
        sline = line.strip().split()
        if sline == []:
            #end of a discourse segment, so start the next
            discourse_ix += 1
            continue
        for word in sline:
            output.append( (word, model[discourse_ix]) )


with open(OPTS['output'], 'w') as f:
    for w in output:
        #currently assumes the *best* topic is the *only* topic
        #NB: Later, we may want to see what happens if we use proportional representation
        #w = (word, [(topic, wt), (topic, wt), ...])
        f.write(w[0]+' '+w[1][0][0]+'\n')
