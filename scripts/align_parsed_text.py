# python align_parsed_text.py --parsed FILE --sentences FILE --output FILE
# aligns/untokenizes parsed text and outputs syntactic categories for each word; each output line contains WORD CAT
# assumes the parsed text contains the same line-delimiting as the sentences file, but tokenization can differ
#      parsed FILE contains space-delimited leaves from a syntactic parse; '-' designates stdin
#      sentences FILE contains the non-ptb-tokenized text; '-' designates stdin
#      output FILE designates where to write output; '-' designates stdout

import re
import sys

DEBUG = False

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

def clean_target(inword):
  # ptb tokenizer converts all quotes to directional, so do the same here
  output = inword
  if output[0] == '"':
    output = '``'+output[1:]
  output = output.replace('"',"''")
#  if output[-1] == '"':
#    output = output[:-1]+"''"
  return(output)
    
if 'parsed' in OPTS and OPTS['parsed'] != '-':
  with open(OPTS['parsed'], 'r') as f:
    parsed = f.readlines()
else:
  parsed = sys.stdin.readlines()

if 'sentences' in OPTS and OPTS['sentences'] != '-':
  with open(OPTS['sentences'], 'r') as f:
    sentences = f.readlines()
else:
  sentences = sys.stdin.readlines()

output = []
bestlen = 0
bestcat = ''
currword = ''
for pix,pline in enumerate(parsed):
  pos = 0
  mysent = sentences[pix].split()
  mytarget = clean_target(mysent[pos])
  myline = pline.strip(' \n()').split(') (')
  linelen = len(myline)
  if myline == ['']:
    #parse failure, so output the words without syntactic categories (just going to have to eat this loss)
    for word in mysent:
      output.append( (word, 'NULL') )
  else:
    for wix,word in enumerate(myline):
      mycat,myword = word.split()
      if myword == '-LRB-':
        myword = '('
      elif myword == '-RRB-':
        myword = ')'
      elif myword == '-LCB-':
        myword = '{'
      elif myword == '-RCB-':
        myword = '}'
      elif myword == '-LSB-':
        myword = '['
      elif myword == '-RSB-':
        myword = ']'
      
      mylen = len(myword)
      currword = currword + myword
      if mylen > bestlen:
        #use longest word fragment as representative for choosing syntactic category
        bestlen = mylen
        bestcat = mycat
      if currword == mytarget:
        #if we've successfully found the entire word, offload it and move on
        output.append( (mysent[pos],bestcat) )
        currword = ''
        bestcat = ''
        bestlen = 0
        if wix < linelen -1:
          pos += 1
          mytarget = clean_target(mysent[pos])
      elif DEBUG:
        sys.stderr.write(str(currword)+' ?= '+str(mytarget)+'\n')

if 'output' in OPTS and OPTS['output'] != '-':
  with open(OPTS['output'], 'w') as f:
    f.write('\n'.join(' '.join(w) for w in output)+'\n')
else:
  sys.stdout.write('\n'.join(' '.join(w) for w in output)+'\n')
