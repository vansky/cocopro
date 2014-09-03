#scripts/calc_probs.py {--input FILE} --output FILE
# input FILE is a pickled input dict containing counts
# output FILE is a pickled dictionary of probabilities

from __future__ import division
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
        input_names.append(sys.argv[aix][2:])
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
            global_dict[topkey] = global_dict.get(topkey, 0) + local_dict[topkey][lowkey]
    return(global_dict)

def compute_probs(cond_counts,marginal_counts):
    #computes probabilities from conditional and marginal counts
    prob_dict = {}
    for key in cond_counts:
        if key not in prob_dict:
            prob_dict[key] = {}
        for cond in cond_counts[key]:
            prob_dict[key][cond] = cond_counts[key][cond] / marginal_counts[cond]
    return(prob_dict)

def normalize_probs(count_dict):
    #normalize a dictionary of counts into probabilities
    total = 0
    norm_dict = {}
    for k in count_dict:
        if k != '-1':
            total += count_dict[k]
    for k in count_dict:
        if k != '-1':
            norm_dict[k] = count_dict[k] / total
    return(norm_dict)

combined_jpro_counts = {} #C(pro,ref,coh,top,sent)
combined_mpro_counts = {} #C(ref,coh,top,sent)
combined_jref_counts = {} #C(ref,coh,topic)
combined_mref_counts = {} #C(coh,topic)
combined_sent_counts = {} #C(sent,topic)
combined_topic_counts = {} #C(topic)
combined_coh_counts = {} #C(coh)

for fname in input_names:
    with open(fname, 'rb') as f:
        pcounts = pickle.load(f)

    if 'topic' in pcounts:
        jpro_counts = pcounts['full_joint']
        combined_jpro_counts = combine_dicts(combined_jpro_counts,jpro_counts)
        mpro_counts = pcounts['marginal']
        combined_mpro_counts = combined_dicts(combined_mpro_counts,mpro_counts)
        
        sent_counts = pcounts['sent']
        combined_sent_counts = combine_dicts(combined_sent_counts,sent_counts)
        topic_counts = pcounts['topic']
        combined_topic_counts = combine_dicts(combined_topic_counts,topic_counts)
        coh_counts = pcounts['coh']
        combined_coh_counts = combine_dicts(combined_coh_counts,coh_counts)
    else:
        jref_counts = pcounts['full_joint']
        combined_jref_counts = combine_dicts(combined_jref_counts,jref_counts)
        mref_counts = pcounts['marginal']
        combined_mref_counts = combined_dicts(combined_mref_counts,mref_counts)

prob_dict = {}
prob_dict['pro'] = compute_probs(combined_jpro_counts,combined_mpro_counts) #P(pro|ref,coh,topic,sent)
prob_dict['ref'] = compute_probs(combined_jref_counts,combined_mref_counts) #P(ref|coh,topic)
prob_dict['sent'] = compute_probs(combined_sent_counts, combined_topic_counts) #P(sent|topic)
prob_dict['topic'] = normalize_probs(combined_topic_counts) #P(topic|\phi_2)
prob_dict['coh'] = normalize_probs(combined_coh_counts)     #P(coh|\phi_1)

with open(OPTS['output'],'wb') as f:
    pickle.dump(prob_dict, f)
