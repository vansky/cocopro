# python align_parsed_text.py --parsed FILE --sentences FILE --output FILE
# aligns/untokenizes parsed text and outputs syntactic categories for each word; each output line contains WORD CAT
# assumes the parsed text contains the same line-delimiting as the sentences file, but tokenization can differ
#      parsed FILE contains space-delimited leaves from a syntactic parse
#      sentences FILE contains the non-ptb-tokenized text
#      output FILE designates where to write output; '-' designates stdin

import re
import sys

OPTS = {}
for aix in range(1,len(sys.argv)):
  if len(sys.argv[aix]) < 2 or sys.argv[aix][:2] != '--':
    #filename or malformed arg
    continue
  elif aix < len(sys.argv) - 1 and len(sys.argv[aix+1]) > 2 and sys.argv[aix+1][:2] == '--':
    #missing filename, so simple arg
    OPTS[sys.argv[aix][2:]] = True
  else:
    OPTS[sys.argv[aix][2:]] = sys.argv[aix+1]

with open(OPTS['parsed'], 'r') as f:
  parsed = f.readlines()

with open(OPTS['sentences'], 'r') as f:
  sentences = [w for s in f.readlines() if s.strip() != '' for w in s.split()]

output = []
bestlen = 0
bestcat = ''
currword = ''
for pix,pline in enumerate(parsed):
  pos = 0
  for wix,word in enumerate(pline.strip(' \n()').split(') (')):
    myword,mycat = word.split()
    mylen = len(myword)
    currword = currword + sword[0]
    if mylen > bestlen:
      #use longest word fragment as representative for choosing syntactic category
      bestlen = mylen
      bestcat = mycat
    if currword == sentences[pix][pos]:
      #if we've successfully found the entire word, offload it and move on
      output.append( (currword,bestcat) )
      currword = ''
      bestcat = ''
      bestlen = 0
      pos += 1

if 'output' in OPTS and OPTS['output'] != '-':
  with open(OPTS['output'], 'w') as f:
    f.write('\n'.join(' '.join(w) for w in output)+'\n')
else:
  sys.stdout.write('\n'.join(' '.join(w) for w in output)+'\n')
