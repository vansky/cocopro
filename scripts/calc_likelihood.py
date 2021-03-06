#calc_likelihood.py --model FILE --input FILE --topics FILE --sentences FILE --output FILE
# uses a model to compute the likelihood of a corpus
#      model FILE is the probability model for computing the likelihood
#      input FILE is the corpus to compute the likelihood over
#      topics FILE is the topic model of the corpus of interest
#      sentences FILE is the list of sentence boundaries in the corpus of interest
#      output FILE designates where to write output

from __future__ import division
import math
import pickle
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

def get_topic(line):
  #returns the topic assignment from this line
  return line.strip().split()[-1]

def find_sent(inix, sentlist):
  old_six = 0
  for six,sent in enumerate(sentlist):
    if sent >= inix:
      return(old_six,sentlist[old_six])
    old_six = six
  return(len(sentlist)-1,sentlist[-1])

def get_prob(indict, keya, keyb):
  #returns conditional logprobs from dicts within dicts
  #defaults to '-1' if it can't find a given key
  if keya in indict:
    if keyb in indict[keya]:
      return(indict[keya][keyb])
    else:
      #the inner key is of an open class
      return(indict[keya]['-1'])
  else:
    #the outer key is of an open class
    return(indict['-1'][keyb])
  raise #Something went wrong... failure in a closed class!
  
with open(OPTS['model'], 'rb') as f:
  model = pickle.load(f)

with open(OPTS['input'], 'rb') as f:
  corpus = pickle.load(f)

with open(OPTS['topics'], 'r') as f:
  topics = f.readlines()

with open(OPTS['sentences'], 'r') as f:
  sentlist = [int(s) for s in f.readlines() if s.strip() != '']
  #sentlist = pickle.load(f)
  
PRONOUNS = ['he','she','they','we','I','you','them','that','those','it','one', 'who', 'which']

likelihood = 0

for e in corpus:
  #coco_corpus.dict_keys(['ANTECEDENT_SPAN', 'ENTITY_ID', 'SENTPOS', 'SPAN' : (277, 299), 'PRO', 'COHERENCE', 'CONTEXT', 'HEAD', 'ANTECEDENT_HEAD'])
  #NB: currently, ref is the sentence position of the antecedent, but we may want to make ref a *distribution over positions* which is sampled from to get the antecedent
  ref = str(e['ENTITY_ID'])
  coh = e['COHERENCE']
  
  #sentence context
  head_begin = e['HEAD'][0]
  head_end = e['HEAD'][1]
  next_sent = 0
  for si in sentlist:
    if si > head_begin:
      next_sent = si
      break

  #now:
      #head_begin - e['SENTPOS'] is the first word in this sentence
      # so range(head_begin - e['SENTPOS'],head_begin) is the preceding sentence_{-i}
      #next_sent - 1 is the final word in this sentence
      # so range(e['SPAN'][1],next_sent) is the remaining sentence_{-i}
  #NB: For now, we treat the first word of the sentence as s_{-i}, but that's a really crappy method of accounting
      #What would be better?
  sent_info = topics[head_begin - e['SENTPOS']].split()[0]
  sent_topic = topics[head_begin - e['SENTPOS']].split()[1]
  ref_topic = topics[head_begin].split()[1]

  ### DEBUG
#  output = []
#  thissent = find_sent(head_begin,sentlist)
#  for i in range(max(0,thissent[1]-3),sentlist[thissent[0]+1]):#head_begin - e['SENTPOS'],next_sent):
#      output.append(topics[i].split()[0])
#  sys.stderr.write(' '.join(output)+'\n')
  ### /DEBUG
  
  pro = str(topics[head_begin].split()[0] in PRONOUNS)
  try:
    likelihood += get_prob(model['pro_from_ref'], ref, pro)
    likelihood += get_prob(model['pro_from_coh'], coh, pro)
    likelihood += get_prob(model['pro_from_top'], ref_topic, pro)
    likelihood += get_prob(model['pro_from_sent'], sent_info, pro)

    likelihood += get_prob(model['ref_from_coh'], coh, ref)
    likelihood += get_prob(model['ref_from_top'], ref_topic, ref)

    likelihood += get_prob(model['s_from_top'], sent_topic, sent_info)

  except:
    sys.stderr.write('Likelihood key error! '+sys.argv[1]+' skipping datapoint\n')
#    continue
    ### DEBUG
#    thissent = find_sent(head_begin,sentlist)
#    sys.stderr.write(str(model['pro'][pro].keys())+'\n')
#    output = []
#    for i in range(thissent[1],sentlist[thissent[0]+1]): #head_begin - e['SENTPOS'],next_sent):
#      output.append(topics[i].split()[0])
#    sys.stderr.write(' '.join(output)+'\n')
    raise
    ###/DEBUG
  likelihood += model['coh'][coh]
  likelihood += model['topic'][ref_topic]
  likelihood += model['topic'][sent_topic]
  
with open(OPTS['output'], 'w') as f:
  f.write(str(likelihood)+'\n')
