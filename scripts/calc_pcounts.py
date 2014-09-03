#align_topics_coref.py --coco-corpus FILE --topics FILE [--sentences FILE] --output FILE
# aligns topics, coref, and coherence data for probability computations
#      coco-corpus FILE is the (pickled) aligned dgb/c3 corpus
#      topics FILE contains words from the DGB with associated topic assignments
#      sentences FILE contains a list of the sentence boundary indices from dgb
#      output FILE designates where to write output; '-' designates stdin

from collections import OrderedDict
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
    continue
  OPTS[sys.argv[aix][2:]] = sys.argv[aix+1]

def get_topic(line):
  #returns the topic assignment from this line
  return line.split()[-1]

with open(OPTS['coco-corpus'], 'rb') as f:
  coco_corpus = pickle.load(f)

with open(OPTS['topics'], 'r') as f:
  topics = f.readlines()

USE_SENTS = False
if 'sentences' in OPTS:
  USE_SENTS = True
  with open(OPTS['sentences'], 'rb') as f:
    sentlist = pickle.load(f)

full_joint_counts = {} # { [item] : { [conditional/marginal] : [counts] } }
marginal_counts = {} # { [conditional/marginal] : [counts] }

#if USE_SENTS: P(ref | coh, top)
#else: P(pro | ref, coh, top, s_i)

#sys.stderr.write('topics: '+str(topics[0])+'\n\n')
#sys.stderr.write('sentences: '+str(sentlist[0])+'\n\n')
#sys.stderr.write('coco keys: '+str(coco_corpus[0]['SPAN'])+'\n\n')

for e in coco_corpus:
  #coco_corpus.dict_keys(['ANTECEDENT_SPAN', 'ENTITY_ID', 'SENTPOS', 'SPAN' : (277, 299), 'PRO', 'COHERENCE', 'CONTEXT'])
  ref = e['ENTITY_ID']
  topic_list = {}
  for tix in range(e['SPAN'][0],e['SPAN'][1]):
    my_topic = get_topic(topics[tix])
    topic_list[my_topic] = topic_list.get(my_topic, 0) + 1
  #NB: for now, we'll have the topics vote first past the post, but we may want to allow proportional topic assignments in the future
  best_topic = ['-1',0]
  for t in topic_list:
    if t != '-1' and topic_list[t] > best_topic[1]:
      best_topic = [t,topic_list[t]]
  coh = e['COHERENCE']
  if USE_SENTS:
    #sentence portion will go here
    pass
  if ref not in full_joint_counts:
    full_joint_counts[ref] = {}
  full_joint_counts[ref][coh,best_topic[0]] = full_joint_counts[ref].get((coh,best_topic[0]), 0) + 1
  marginal_counts[coh,best_topic[0]] = marginal_counts.get((coh,best_topic[0]), 0) + 1

pcounts = {'full_joint': full_joint_counts, 'marginal': marginal_counts}
with open(OPTS['output'], 'wb') as f:
  pickle.dump(pcounts, f)
