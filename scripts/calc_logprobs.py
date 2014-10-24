#scripts/calc_logprobs.py {--input FILE} [--hold-out FILE] --output FILE
#computes logprobs based on count data
# input FILE is a pickled input dict containing counts
# hold-out FILE is a file that is held-out for testing purposes
# output FILE is a pickled dictionary of probabilities

from __future__ import division
import math
import pickle
import re
import sys

ADD_PSEUDO=True #Adds pseudo counts at this large, corpus-level stage
WEAKPRIOR=True #Strengthens/Weakens PRO priors
ANT_VECTORS=False #Uses distributed representation of antecedents
SENT_VECTORS=False #Uses distributed representation of sentence
BI_VECTORS=False #Uses distributed representation of bigram context

OPTS = {}
input_names = []
for aix in range(1,len(sys.argv)):
  if len(sys.argv[aix]) < 2 or sys.argv[aix][:2] != '--':
    #filename or malformed arg
    continue
  elif aix < len(sys.argv) - 1 and len(sys.argv[aix+1]) > 2 and sys.argv[aix+1][:2] == '--':
    #missing filename
    continue
  if sys.argv[aix][2:] == 'input':
    input_names.append(sys.argv[aix+1])
  else:
    OPTS[sys.argv[aix][2:]] = sys.argv[aix+1]

def combine_dicts(global_dict,local_dict):
  #adds counts from a local_dict to those in a global_dict
  for topkey in local_dict:
    if type(local_dict[topkey]) == type({}):
      if topkey not in global_dict:
        global_dict[topkey] = {}
      for lowkey in local_dict[topkey]:
        global_dict[topkey][lowkey] = global_dict[topkey].get(lowkey, 0) + local_dict[topkey][lowkey]
    else:
      global_dict[topkey] = global_dict.get(topkey, 0) + local_dict[topkey]
  return(global_dict)

def normalize_probs(count_dict,LOG=True):
  #normalize a dictionary of counts into log-probabilities
  total = 0
  if type(count_dict[list(count_dict)[0]]) == type({}):
    #normalize subdicts (conditional probs)
    for k in count_dict:
      count_dict[k] = normalize_probs(count_dict[k])
  else:
    for k in count_dict:
      total += count_dict[k]
    for k in count_dict:
      if LOG:
        count_dict[k] = math.log(count_dict[k] / total)
      else:
        count_dict[k] /= total
  return(count_dict)

def find_centroid(veclist):
  #given a list of strings representations of vectors, output the centroid
  if veclist == []:
    return(veclist)
  if len(veclist) == 1:
    return(veclist[0])
  centroid = [float(f) for f in veclist[0].split()]
  for v in veclist[1:]:
    for i,d in enumerate(float(f) for f in v.split()):
      centroid[i] += d
  mylen = len(veclist)
  for i in range(len(centroid)):
    centroid[i] /= mylen
  return(' '.join(list(str(f) for f in centroid)))

def cosim(vec1,vec2):
  #given two lists of string representations of vectors, output the cosine similarity
  vec1 = [float(f) for f in vec1.split()]
  vec2 = [float(f) for f in vec2.split()]
  vec1mag = math.sqrt(sum(f**2 for f in vec1))
  vec2mag = math.sqrt(sum(f**2 for f in vec2))
  return( sum(vec1[i]*vec2[i] for i in range(len(vec1)))/(vec1mag*vec2mag) )

def reframe_with_centroids(indict):
  #replace conditional probability dict parents with centroids
  inverteddict = {}
  for value in set(k2 for k in indict for k2 in indict[k].keys()):
    #for each leaf key type
    inverteddict[value] = []
    for k in indict:
      #make a dict to find all possible parents that can generate leaf key type
      if value in indict[k]:
        inverteddict[value].append(k)
  outdict = {}
  for k in inverteddict:
    #for each possible manifestation (PRO)
    #find the centroid
    newcentroid = find_centroid(inverteddict[k])
    outdict[newcentroid] = {}
    for parent in indict:
      for child in indict[parent]:
        #update the probabilities based on |cos(Parent_x,centroid)|*P(Parent_x->x)
        outdict[newcentroid][child] = outdict[newcentroid].get(child,0) + abs(cosim(newcentroid,parent)) * indict[parent][child]
  for child in outdict[newcentroid]:
    #normalize each child by the number of vectors that composed it
    outdict[newcentroid][child] = outdict[newcentroid][child] / len(inverteddict[child])
  # P(a|A') = ( sim(A_1|A')*P(a|A_1) + sim(A_2|A')*P(a|A_2) ) / 2
  return(outdict)
    
def add_pseudocounts(indict,priordict=None):
  if len(indict) == 0:
    return(indict)
  #adds 1 pseudo observation to all conditions (divided among marginals+unk)
  if type(indict[list(indict)[0]]) == type({}):
    #conditional probability dict
    for k in indict:
      indict[k] = add_pseudocounts(indict[k],priordict)
    if not priordict:
      #add one pseudo count for unseen conditions that can split to all observed marginals
      poss_keys = set([m for k in indict for m in indict[k]])
      indict['-1'] = dict([(k, 1/len(poss_keys)) for k in poss_keys])
    else:
      #add pseudo counts for unseen conditions that can split based on prior expectations
      numkeys = len(priordict) + 1
      indict['-1'] = priordict
      for k in priordict:
        indict['-1'][k] += 1/numkeys
      indict['-1']['-1'] = 1/numkeys
  else:
    if not priordict:
      #marginal probability dist
      numkeys = len(indict)+1
      for k in indict:
        indict[k] += 1/numkeys
      indict['-1'] = 1/numkeys
    else:
      #include prior expectation pseudo counts
      poss_keys = len(priordict) + 1
      for k in priordict:
        indict[k] = indict.get(k,0)+priordict[k] + 1/poss_keys
      indict['-1'] = 1/poss_keys
  return(indict)


combined_pro_from_ref = {}
combined_pro_from_coh = {}
combined_pro_from_top = {}
combined_pro_from_topchange = {}
combined_pro_from_sent = {}
combined_pro_from_sentpos = {}
combined_pro_from_ant = {}
combined_pro_from_ant_syncat = {}
combined_pro_from_bi = {}
combined_pro_from_ref_syncat = {}
combined_ref_from_coh = {}
combined_ref_from_top = {}
combined_s_from_top = {}
combined_sent_counts = {}
combined_topic_counts = {}
combined_coh_counts = {}
combined_pro_counts = {}

for fname in input_names:
  if 'hold-out' in OPTS and fname.split('.')[-2] == OPTS['hold-out']:
    #skip held-out subcorpus
    continue
#    sys.stderr.write(str(fname.split('.')[-2])+'?='+OPTS['hold-out']+'\n')
  with open(fname, 'rb') as f:
    pcounts = pickle.load(f)

  combined_pro_from_ref = combine_dicts(combined_pro_from_ref, pcounts['pro_from_ref'])
  combined_pro_from_coh = combine_dicts(combined_pro_from_coh, pcounts['pro_from_coh'])
  combined_pro_from_top = combine_dicts(combined_pro_from_top, pcounts['pro_from_top'])
  combined_pro_from_topchange = combine_dicts(combined_pro_from_topchange, pcounts['pro_from_topchange'])
  combined_pro_from_sent = combine_dicts(combined_pro_from_sent, pcounts['pro_from_sent'])
  combined_pro_from_sentpos = combine_dicts(combined_pro_from_sentpos, pcounts['pro_from_sentpos'])
  combined_pro_from_ant = combine_dicts(combined_pro_from_ant, pcounts['pro_from_ant'])
  combined_pro_from_ant_syncat = combine_dicts(combined_pro_from_ant_syncat, pcounts['pro_from_ant_syncat'])
  combined_pro_from_bi = combine_dicts(combined_pro_from_bi, pcounts['pro_from_bi'])
  combined_pro_from_ref_syncat = combine_dicts(combined_pro_from_ref_syncat, pcounts['pro_from_ref_syncat'])

  combined_ref_from_coh = combine_dicts(combined_ref_from_coh, pcounts['ref_from_coh'])
  combined_ref_from_top = combine_dicts(combined_ref_from_top, pcounts['ref_from_top'])

  combined_s_from_top = combine_dicts(combined_s_from_top, pcounts['s_from_top'])
    
#    sent_counts = pcounts['sent']
#    combined_sent_counts = combine_dicts(combined_sent_counts,sent_counts)
  topic_counts = pcounts['topic']
  combined_topic_counts = combine_dicts(combined_topic_counts,topic_counts)
  coh_counts = pcounts['coh']
  combined_coh_counts = combine_dicts(combined_coh_counts,coh_counts)
  pro_counts = pcounts['pro']
  combined_pro_counts = combine_dicts(combined_pro_counts,pro_counts)

if ADD_PSEUDO:
  if WEAKPRIOR:
    #normalize to largest thing to weaken prior counts (and only see 1/100 of an pseudo-obs for added weakness)
    bigkey = max(combined_pro_counts.values())*100
    for p in combined_pro_counts:
      combined_pro_counts[p] = combined_pro_counts[p] / bigkey
  else:
    #normalize to smallest thing to strengthen prior counts
    smallkey = min(combined_pro_counts.values())
    for p in combined_pro_counts:
      combined_pro_counts[p] = combined_pro_counts[p] / smallkey

  if ANT_VECTORS:
    combined_pro_from_ant = reframe_with_centroids(normalize_probs(combined_pro_from_ant, LOG=False))
  else:
    combined_pro_from_ant = add_pseudocounts(combined_pro_from_ant, combined_pro_counts)

  if BI_VECTORS:
    combined_pro_from_bi = reframe_with_centroids(normalize_probs(combined_pro_from_bi, LOG=False))
  else:
    combined_pro_from_bi = add_pseudocounts(combined_pro_from_bi, combined_pro_counts)

  if SENT_VECTORS:
    combined_pro_from_sent = reframe_with_centroids(normalize_probs(combined_pro_from_sent, LOG=False))
  else:
    combined_pro_from_sent = add_pseudocounts(combined_pro_from_sent, combined_pro_counts)

  for d in (combined_pro_from_ref, combined_pro_from_coh, combined_pro_from_top, combined_pro_from_topchange, combined_pro_from_ref_syncat, combined_pro_from_sentpos, combined_pro_from_ant_syncat):
    d = add_pseudocounts(d, combined_pro_counts)
  for d in (combined_ref_from_coh, combined_ref_from_top):
    d = add_pseudocounts(d)
    
prob_dict = {}
prob_dict['pro_from_ref'] = normalize_probs(combined_pro_from_ref) #P(pro|ref)
prob_dict['pro_from_coh'] = normalize_probs(combined_pro_from_coh) #P(pro|coh)
prob_dict['pro_from_top'] = normalize_probs(combined_pro_from_top) #P(pro|top)
prob_dict['pro_from_topchange'] = normalize_probs(combined_pro_from_topchange) #P(pro|topchange)
prob_dict['pro_from_sent'] = normalize_probs(combined_pro_from_sent) #P(pro|sent)
prob_dict['pro_from_sentpos'] = normalize_probs(combined_pro_from_sentpos) #P(pro|sentpos)
prob_dict['pro_from_ant'] = normalize_probs(combined_pro_from_ant) #P(pro|ant)
prob_dict['pro_from_ant_syncat'] = normalize_probs(combined_pro_from_ant_syncat) #P(pro|ant_syncat)
prob_dict['pro_from_bi'] = normalize_probs(combined_pro_from_bi) #P(pro|bi)
prob_dict['pro_from_ref_syncat'] = normalize_probs(combined_pro_from_ref_syncat) #P(pro|ref_syncat)
prob_dict['ref_from_coh'] = normalize_probs(combined_ref_from_coh) #P(ref|coh)
prob_dict['ref_from_top'] = normalize_probs(combined_ref_from_top) #P(ref|topic)
prob_dict['s_from_top'] = normalize_probs(combined_s_from_top) #P(sent|topic)

#prob_dict['sent'] = normalize_probs(combined_sent_counts)
# add a pseudo-observed unk topic
numtopics = len(combined_topic_counts) + 1
for k in combined_topic_counts:
  combined_topic_counts[k] += 1 / numtopics
combined_coh_counts['-1'] = 1 / numtopics
prob_dict['topic'] = normalize_probs(combined_topic_counts) #P(topic|\phi_2)
# add a pseudo-observed unk coherence relation
numcoh = len(combined_coh_counts) + 1
for k in combined_coh_counts:
  combined_coh_counts[k] += 1 / numcoh
combined_coh_counts['-1'] = 1 / numcoh
prob_dict['coh'] = normalize_probs(combined_coh_counts)     #P(coh|\phi_1)

with open(OPTS['output'],'wb') as f:
  pickle.dump(prob_dict, f)
