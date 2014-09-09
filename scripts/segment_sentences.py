#segment_sentences.py --text textFile --output FILE [OPTS]
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
reperiodinword = re.compile('[A-Za-z]\.[A-Za-z]') #find word-internal punc (e.g. acronyms)
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

sentbounds = [0]

NUMLINES = len(text)
for lix,line in enumerate(text):
  sline = line.strip().split()
  if sline == []:
    sentbounds.append(overix)
    
  for wix,word in enumerate(sline):
    #if there's non-period punctuation at the end of word (and we're not at the end of the file) OR
      #the word ends with a period AND the word isn't an exception AND the word begins with a capital AND the word has no internal periods
      # we assume sentences can't end with acronyms, which isn't true, but it's what we're assuming for now
    if (repuncendword.search(word) and (lix < NUMLINES or wix < len(sline) )) or \
          ( reperiodendword.search(word) and word not in exceptions and wix < len(sline)-1 and recap.match(sline[wix+1]) and not reperiodinword.search(word) ):
      sentbounds.append(overix + wix + 1) #if this is the end of a sentence, the NEXT ix is the beginning of a sentence
  overix += len(sline)

with open(OPTS['output'],'wb') as f:
  pickle.dump(sentbounds,f)
