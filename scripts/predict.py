#predict.py --model FILE --input FILE --topics FILE --sentences FILE --vectors FILE --categories FILE --output FILE
# uses a model to predict pronominalization in a test corpus
#      model FILE is the probability model for computing the likelihood
#      input FILE is the corpus to compute the likelihood over
#      topics FILE is the topic model of the corpus of interest
#      sentences FILE is the list of sentence boundaries in the corpus of interest
#      vectors FILE contains a list (word/line) of dgb words and their distributed reps
#      categories FILE contains a list (word/line) of dgb words and their associated syntactic categories
#      output FILE designates where to write output

from __future__ import division
import math
import pickle
import re
import sys

#TEST variable dictates the type of model used
#  TEST = 'TEST' means we provide a valid test for a trained model
#  TEST = [Other] means we assume every reference is maximum likelihood estimator (technically, a maximum a posteriori estimator, but our prior is uniform)
TEST = 'TEST'
VERBOSE = False
DEBUG = False

# Tells what features to use during test time; At least one must be set to True
USE_COH = 1 #coherence relation
USE_TOP = 1 #topic assignment
USE_TOPCHANGE = 1 #topic assignment changed?
USE_ANT = 1 #antecedent token
USE_ANT_SYNCAT = 1 #antecedent syntactic category
USE_SENT = 1 #first token of sentence
USE_SENTPOS = 1 #sentence position of PRO
USE_BI = 1 #preceding (bigram prefix) token
USE_SYNCAT = 1 #syntactic (GCG14) category

# Tells how to collapse PRO (0 means uncollapsed)
COLLAPSE_PRO = 2

# Tells the model to use regression weights (obtained from genmodel/*regtables)
USE_WEIGHTS = 0
###
#10-class
###
#Full Model
WEIGHTS = {'ref_topic': 0.00666626210126,
           'ant_syncat': 0.0200567706199,
           'sentpos': 0.00122216836002,
           'ref_syncat': 0.740686157874,
           'sent_info': 0.0228712082297,
           'bi_info': 0.0294790422769,
           'ant_info': 0.16291055631,
           'coh': 0.0161078342276 }
#WEIGHTS = { 'ref_syncat': 0.0986255020389,
#            'sent_info': 0.0992567905501,
#            'bi_info': 0.802117707411 }

###
#BINARY
###
#Full Model
#WEIGHTS = {'ref_topic': 0.0496257879026,
#           'ant_syncat': 0.0340216454766,
#           'sentpos': 0.0045892626512,
#           'ref_syncat': 0.373785189945,
#           'sent_info': 0.126916850703,
#           'bi_info': 0.20357637105,
#           'ant_info': 0.139158061098,
#           'coh': 0.068326831174 }
#WEIGHTS = {'ref_syncat': 0.142033138804,
#           'sent_info': 0.389173236236,
#           'bi_info': 0.46879362496 }


# Tells which features should exist in vector space during test time; All can be False
ANT_VECTORS = False
SENT_VECTORS = False
BI_VECTORS = False

#Storage for results
proresults = {} #how well can we predict PROtype?

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

def find_best_key(indict):
  #returns the key with the largest associated int value
  bestkey = 0
  bestval = 0
  for k,v in indict.items():
    if int(v) > bestval:
      bestkey = k
      bestval = int(v)
  return(bestkey)

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
    if keyb in indict['-1']:
      #the outer key is of an open class
      return(indict['-1'][keyb])
    else:
      #both keys are of an open class
      return(indict['-1']['-1'])

def combine_dicts(global_dict,local_dict,weight_key):
  #combines logprobs from a local_dict with those in a global_dict
  for topkey in local_dict:
    if type(local_dict[topkey]) == type({}):
      if topkey not in global_dict:
        global_dict[topkey] = {}
      for lowkey in local_dict[topkey]:
        if USE_WEIGHTS:
          global_dict[topkey][lowkey] = global_dict[topkey].get(lowkey, 0) + (1-WEIGHTS[weight_key])*local_dict[topkey][lowkey]+.5*local_dict[topkey][lowkey]
        else:
          global_dict[topkey][lowkey] = global_dict[topkey].get(lowkey, 0) + local_dict[topkey][lowkey]
    else:
      if USE_WEIGHTS:
        global_dict[topkey] = global_dict.get(topkey, 0) + (1-WEIGHTS[weight_key])*local_dict[topkey]+local_dict[topkey]
      else:
        global_dict[topkey] = global_dict.get(topkey, 0) + .5*local_dict[topkey]
  return(global_dict)

def marginalize_dict(indict):
  #return leaf values marginalized over all conditionals
  return_vals = {}
  for topkey in indict:
    for inkey in indict[topkey]:
      return_vals[inkey] = return_vals.get(inkey,0) + math.e**indict[topkey][inkey]
  for k in return_vals:
    return_vals[k] = math.log(return_vals[k])
  return(return_vals)

def marginalize_centroid_dict(indict,invec):
  #return leaf values marginalized over all conditionals scaled by how well invec matches each topkey
  return_vals = {}
  for topkey in indict:
    for inkey in indict[topkey]:
      return_vals[inkey] = return_vals.get(inkey,0) + math.e**indict[topkey][inkey]*abs(cosim(invec,topkey))
  for k in return_vals:
    return_vals[k] = math.log(return_vals[k])
  return(return_vals)

def cosim(vec1,vec2):
    #given two lists of string representations of vectors, output the cosine similarity
    vec1 = [float(f) for f in vec1.split()]
    vec2 = [float(f) for f in vec2.split()]
    vec1mag = math.sqrt(sum(f**2 for f in vec1))
    vec2mag = math.sqrt(sum(f**2 for f in vec2))
    return( sum(vec1[i]*vec2[i] for i in range(len(vec1)))/(vec1mag*vec2mag) )

def predict(indict, keya):
  #returns the conditional probability of all keyb's on keya
  if keya in indict:
    return(indict[keya])
  return(indict['-1'])

with open(OPTS['model'], 'rb') as f:
  model = pickle.load(f)

with open(OPTS['input'], 'rb') as f:
  corpus = pickle.load(f)

with open(OPTS['topics'], 'r') as f:
  topics = f.readlines()

with open(OPTS['vectors'], 'r') as f:
  vectors = [l.strip() for l in f.readlines()]

with open(OPTS['categories'], 'r') as f:
  syncats = f.readlines()
  
with open(OPTS['sentences'], 'r') as f:
  sentlist = [int(s) for s in f.readlines() if s.strip() != '']
  #sentlist = pickle.load(f)
  
PRONOUNS = ['he','she','they','we','I','you','them','that','those','it','one', 'who', 'which']

total = 0
hits = 0

for e in corpus:
  #coco_corpus.dict_keys(['ANTECEDENT_SPAN', 'ENTITY_ID', 'SENTPOS', 'SPAN' : (277, 299), 'PRO', 'COHERENCE', 'CONTEXT', 'HEAD', 'ANTECEDENT_HEAD'])
  #NB: currently, ref is the sentence position of the antecedent, but we may want to make ref a *distribution over positions* which is sampled from to get the antecedent
  ref = str(e['ENTITY_ID'])
  coh = e['COHERENCE']
  
  #sentence context
  head_begin = e['HEAD'][0]
  head_end = e['HEAD'][1]
  next_sent = 0
  prevsent = -1
  for six,si in enumerate(sentlist):
    if si > head_begin:
      prevsent = sentlist[max(0,six-2)]
      next_sent = si
      break

  #now:
      #head_begin - e['SENTPOS'] is the first word in this sentence
      # so range(head_begin - e['SENTPOS'],head_begin) is the preceding sentence_{-i}
      #next_sent - 1 is the final word in this sentence
      # so range(e['SPAN'][1],next_sent) is the remaining sentence_{-i}
  #NB: For now, we treat the first word of the sentence as s_{-i}, but that's a really crappy method of accounting
      #What would be better?
  if SENT_VECTORS:
    sent_info = ' '.join(vectors[head_begin - e['SENTPOS']].split()[1:])
  else:
    sent_info = topics[head_begin - e['SENTPOS']].split()[0]
  sent_topic = topics[head_begin - e['SENTPOS']].split()[1]
  posstops = {} #{topic: count}
  for wix in range(prevsent,head_begin - e['SENTPOS']):
    thistop = topics[wix].split()[1]
    posstops[thistop] = posstops.get(thistop,0) + 1
  if posstops == {}:
    prevsent_topic = '-1'
  else:
    prevsent_topic = find_best_key(posstops) 

  sentpos = e['SENTPOS']
  ref_topic = topics[head_begin].split()[1]
  ref_syncat = syncats[head_begin].split()[1]
  ant_syncat = syncats[e['ANTECEDENT_HEAD'][0]].split()[1]
  if ANT_VECTORS:
    ant_info = ' '.join(vectors[e['ANTECEDENT_HEAD'][0]].split()[1:])
  else:
    ant_info = topics[e['ANTECEDENT_HEAD'][0]].split()[0]
  if BI_VECTORS:
    bi_info = ' '.join(vectors[head_begin - 1].split()[1:])
  else:
    bi_info = topics[head_begin - 1].split()[0]

  if COLLAPSE_PRO == 0:
    pro = e['TYPE']
  elif COLLAPSE_PRO == 2:
    if e['TYPE'] in ['WHQ','PRO']:
      pro = 'PRO'
    else:
      pro = 'OTHER'
  else:
    raise #undefined collapse specification

  likelihood = 0

  likelihood += predict(model['coh'], coh)
  likelihood += predict(model['topic'], ref_topic)
  likelihood += predict(model['topic'], sent_topic)

#  likelihood += get_prob(model['s_from_top'], sent_topic, sent_info)

  likelihood += get_prob(model['ref_from_coh'], coh, ref)
  likelihood += get_prob(model['ref_from_top'], ref_topic, ref)

  if TEST == 'TEST':
    options = {}
    #options = combine_dicts(options, predict(model['pro_from_ref'], ref))
    if USE_COH:
      options = combine_dicts(options, predict(model['pro_from_coh'], coh), 'coh')
    if USE_TOP:
      options = combine_dicts(options, predict(model['pro_from_top'], ref_topic), 'ref_topic')
    #options = combine_dicts(options, predict(model['pro_from_sent'], sent_info))
    if USE_TOPCHANGE:
      TOPCHANGE = ref_topic == prevsent_topic
      options = combine_dicts(options, predict(model['pro_from_topchange'], TOPCHANGE), 'topchange')

    if USE_SYNCAT:
      options = combine_dicts(options, predict(model['pro_from_ref_syncat'], ref_syncat), 'ref_syncat')
    if USE_ANT_SYNCAT:
      options = combine_dicts(options, predict(model['pro_from_ant_syncat'], ant_syncat), 'ant_syncat')

    if USE_SENT:
      if SENT_VECTORS:
        options = combine_dicts(options, marginalize_centroid_dict(model['pro_from_sent'], sent_info), 'sent_info')
      else:
        options = combine_dicts(options, predict(model['pro_from_sent'], sent_info), 'sent_info')
    if USE_SENTPOS:
      options = combine_dicts(options, predict(model['pro_from_sentpos'], sentpos), 'sentpos')
    if USE_ANT:
      if ANT_VECTORS:
        options = combine_dicts(options, marginalize_centroid_dict(model['pro_from_ant'], ant_info), 'ant_info')
      else:
        options = combine_dicts(options, predict(model['pro_from_ant'], ant_info), 'ant_info')
      
    if DEBUG:
      sys.stderr.write('Before: '+str(options)+'\n')
    if USE_BI:
      if BI_VECTORS:
        options = combine_dicts(options, marginalize_centroid_dict(model['pro_from_bi'], bi_info), 'bi_info')
      else:
        options = combine_dicts(options, predict(model['pro_from_bi'], bi_info), 'bi_info')
    if DEBUG:
      sys.stderr.write('After: '+str(options)+'\n')
      
    best = max(options.keys(), key=(lambda key: options[key])) # returns best key
    if DEBUG:
      sys.stderr.write('Guess: '+best+ ' Answer: '+pro+'\n\n')
    if VERBOSE:
      sys.stderr.write('Best answer: '+str(best)+'\n')
  else:
    options = marginalize_dict(model['pro_from_ref'])
    #Don't need other dicts because we're marginalizing over all eventualities
    #options = combine_dicts(options, predict(model['pro_from_coh'], coh))
    #options = combine_dicts(options, predict(model['pro_from_top'], ref_topic))
    #options = combine_dicts(options, predict(model['pro_from_sent'], sent_info))
    best = max(options.keys(), key=(lambda key: options[key])) # returns best key
    if VERBOSE:
      sys.stderr.write('Best answer: '+str(best)+'\n')

  total += 1
  if pro not in proresults:
    proresults[pro] = [0,0]
  proresults[pro][1] += 1
  if best == pro:
    hits += 1
    proresults[pro][0] += 1

if VERBOSE:
  sys.stderr.write(str(hits)+'/'+str(total)+'\n')
with open(OPTS['output'], 'w') as f:
  if TEST == 'TEST':
    f.write('Testing actual model predictions\n')
  else:
    f.write('Forcing baseline model to answer with most likely answer\n')
  f.write('Total: '+str(hits)+'/'+str(total)+'\n')
  for pro in proresults:
    f.write(pro+': '+str(proresults[pro][0])+'/'+str(proresults[pro][1])+'\n')
