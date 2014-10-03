#scripts/calc_logprobs.py {--input FILE} --output FILE
#computes logprobs based on count data
# input FILE is a pickled input dict containing counts
# output FILE is a pickled dictionary of probabilities

from __future__ import division
import math
import pickle
import re
import sys

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
    norm_dict = {}
    if type(count_dict[count_dict.keys()[0]]) == type({}):
        #normalize subdicts (conditional probs)
        for k in count_dict:
            count_dict[k] = normalize_probs(count_dict[k])
    else:
        for k in count_dict:
            total += count_dict[k]
        for k in count_dict:
            norm_dict[k] = math.log(count_dict[k] / total)
    return(norm_dict)

combined_pro_from_ref = {}
combined_pro_from_coh = {}
combined_pro_from_top = {}
combined_pro_from_sent = {}
combined_ref_from_coh = {}
combined_ref_from_top = {}
combined_s_from_top = {}
combined_sent_counts = {}
combined_topic_counts = {}
combined_coh_counts = {}

for fname in input_names:
    with open(fname, 'rb') as f:
        pcounts = pickle.load(f)

    combined_pro_from_ref = combine_dicts(combined_pro_from_ref, pcounts['pro_from_ref'])
    combined_pro_from_coh = combine_dicts(combined_pro_from_coh, pcounts['pro_from_coh'])
    combined_pro_from_top = combine_dicts(combined_pro_from_top, pcounts['pro_from_top'])
    combined_pro_from_sent = combine_dicts(combined_pro_from_sent, pcounts['pro_from_sent'])

    combined_ref_from_coh = combine_dicts(combined_ref_from_coh, pcounts['ref_from_coh'])
    combined_ref_from_top = combine_dicts(combined_ref_from_top, pcounts['ref_from_top'])

    combined_s_from_top = combine_dicts(combined_s_from_top, pcounts['s_from_top'])
    
    sent_counts = pcounts['sent']
    combined_sent_counts = combine_dicts(combined_sent_counts,sent_counts)
    topic_counts = pcounts['topic']
    combined_topic_counts = combine_dicts(combined_topic_counts,topic_counts)
    coh_counts = pcounts['coh']
    combined_coh_counts = combine_dicts(combined_coh_counts,coh_counts)
    
prob_dict = {}
prob_dict['pro_from_ref'] = normalize_probs(combined_pro_from_ref) #P(pro|ref)
prob_dict['pro_from_coh'] = normalize_probs(combined_pro_from_coh) #P(pro|coh)
prob_dict['pro_from_top'] = normalize_probs(combined_pro_from_top) #P(pro|top)
prob_dict['pro_from_sent'] = normalize_probs(combined_pro_from_sent) #P(pro|sent)
prob_dict['ref_from_coh'] = normalize_probs(combined_ref_from_coh) #P(ref|coh)
prob_dict['ref_from_top'] = normalize_probs(combined_ref_from_top) #P(ref|topic)
prob_dict['s_from_top'] = normalize_probs(combined_s_from_top) #P(sent|topic)

#prob_dict['sent'] = normalize_probs(combined_sent_counts)
prob_dict['topic'] = normalize_probs(combined_topic_counts) #P(topic|\phi_2)
prob_dict['coh'] = normalize_probs(combined_coh_counts)     #P(coh|\phi_1)

with open(OPTS['output'],'wb') as f:
    pickle.dump(prob_dict, f)
