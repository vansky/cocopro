#scripts/calc_logprobs.py {--input FILE} --output FILE
#computes logprobs based on count data
# input FILE is a pickled input dict containing counts
# output FILE is a pickled dictionary of probabilities

from __future__ import division
import math
import pickle
import re
import sys

ADD_PSEUDO=True #Adds pseudo counts at this large, corpus-level stage
WEAKPRIOR=True #Strengthens/Weakens PRO priors

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

def normalize_probs(count_dict):
    #normalize a dictionary of counts into probabilities
    total = 0
    if type(count_dict[list(count_dict)[0]]) == type({}):
        #normalize subdicts (conditional probs)
        for k in count_dict:
            count_dict[k] = normalize_probs(count_dict[k])
    else:
        for k in count_dict:
            total += count_dict[k]
        for k in count_dict:
            count_dict[k] = math.log(count_dict[k] / total)
    return(count_dict)

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
      poss_keys = len(priordict) + 1
      indict['-1'] = priordict
      for k in priordict:
        indict['-1'][k] += 1/poss_keys
      indict['-1']['-1'] = 1/poss_keys
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
combined_pro_from_sent = {}
combined_pro_from_ant = {}
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
    combined_pro_from_sent = combine_dicts(combined_pro_from_sent, pcounts['pro_from_sent'])
    combined_pro_from_ant = combine_dicts(combined_pro_from_ant, pcounts['pro_from_ant'])

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

  for d in (combined_pro_from_ref, combined_pro_from_coh, combined_pro_from_top, combined_pro_from_sent, combined_pro_from_ant):
    d = add_pseudocounts(d, combined_pro_counts)

  for d in (combined_ref_from_coh, combined_ref_from_top):
    d = add_pseudocounts(d)
    
prob_dict = {}
prob_dict['pro_from_ref'] = normalize_probs(combined_pro_from_ref) #P(pro|ref)
prob_dict['pro_from_coh'] = normalize_probs(combined_pro_from_coh) #P(pro|coh)
prob_dict['pro_from_top'] = normalize_probs(combined_pro_from_top) #P(pro|top)
prob_dict['pro_from_sent'] = normalize_probs(combined_pro_from_sent) #P(pro|sent)
prob_dict['pro_from_ant'] = normalize_probs(combined_pro_from_ant) #P(pro|ant)
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
