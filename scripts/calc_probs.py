#scripts/calc_probs.py {--in FILE} --output FILE
# input FILE is the pickled input dict containing counts
# output FILE is a list of associated probabilities

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
    if sys.argv[aix][2:] == 'in':
        input_names.append(sys.argv[aix][2:])
    else:
        OPTS[sys.argv[aix][2:]] = sys.argv[aix+1]

def combine_dicts(global_dict,local_dict):
    pass

def compute_probs(cond_prob,marginal_prob):
    pass

combined_full_joint_counts = {}
combined_marginal_counts = {}
combined_sent_counts = {}
combined_topic_counts = {}

COMPUTE_PRO = False
for fname in input_names:
    with open(fname, 'rb') as f:
        pcounts = pickle.load(f)

    full_joint_counts = pcounts['full_joint']
    combined_full_joint_counts = combine_dicts(combined_full_joint_counts,full_joint_counts)
    marginal_counts = pcounts['marginal']
    combined_marginal_counts = combine_dicts(combined_marginal_counts,marginal_counts)
    if COMPUTE_PRO or 'topic' in pcounts:
        COMPUTE_PRO = True
        sent_counts = pcounts['sent']
        combined_sent_counts = combine_dicts(combined_sent_counts,sent_counts)
        topic_counts = pcounts['topic']
        combined_topic_counts = combine_dicts(combined_topic_counts,topic_counts)

full_probs = compute_probs(combined_full_joint_counts,combined_marginal_counts)
if COMPUTE_PRO:
    sent_probs = compute_probs(combined_sent_counts, combined_topic_counts)
