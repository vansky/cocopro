#segment_sentences.py --text textFile [OPTS] [--output FILE]
# PRE: textFile is the discourse segmented text found in Discourse GraphBank
# outputs a list of sentence boundaries
# OPTS: --output FILE
#         Saves the list of sentence boundary indicies to FILE (gives index of word including sentence final punctuation)
#         output format: BOUNDARY\nBOUNDARY\n...

import pickle
import re
import sys

OPTS = {}
for aix in range(1,len(sys.argv)):
  if len(sys.argv[aix]) < 2 or sys.argv[aix][:2] != '--':
    #filename or malformed arg
    continue
  elif aix < len(sys.argv) - 1 and len(sys.argv[aix+1]) > 2 and sys.argv[aix+1][:2] == '--':
    #missing filename
    OPTS[sys.argv[aix][2:1]] = True
  else:
    OPTS[sys.argv[aix][2:]] = sys.argv[aix+1]
  

reperiodendword = re.compile('[A-Za-z]\.[\'"]*') #find word-final periods
repuncinword = re.compile('[A-Za-z]\.[A-Za-z]') #find word-internal punc (e.g. acronyms)
repuncendword = re.compile('[A-Za-z][\?!][\'"]*') #find word-final punc
recap = re.compile('[A-Z]') #find caps

exceptions = ['mr','mrs','ms','eg','ie','etc'] #these and all words with word-internal periods

with open(OPTS['text'], 'r') as f:
  text = f.readlines()

def hasInternalPunc(word):
  if repuncword.search(word) or word in exceptions:
    return(True)
  else:
    return(False)

overix = 0 #ctr to track overall position in text

sentbounds = []

for line in text:
  sline = line.strip().split()
  if sline == []:
    sentbounds.append(overix)
    
  for wix,word in enumerate(sline):
    #if there's punc at the end of word and:
      #the next word begins with a capital letter OR
      #not (the current word has internal punc or the current word is an exception)
    if repuncendword.search(word) or \
          reperiodendword and word not in exceptions and ( ( wix < len(sline)-1 and recap.match(sline[wix+1]) in repuncinword ) or \
                                                              not repuncword.search(word) ):
      sentbounds.append(overix + wix)
  overix += len(sline)

with open(OPTS['output'],'wb') as f:
  pickle.dump(sentbounds,f)
