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
  return line.strip().split()[-1]

with open(OPTS['coco-corpus'], 'rb') as f:
  coco_corpus = pickle.load(f)

with open(OPTS['topics'], 'r') as f:
  topics = f.readlines()

USE_SENTS = False
if 'sentences' in OPTS:
  USE_SENTS = True
  with open(OPTS['sentences'], 'rb') as f:
    sentlist = pickle.load(f)

PRONOUNS = ['he','she','they','we','I','you','them','that','those','it','one']
full_joint_counts = {} # { [item] : { [conditional/marginal] : [counts] } }
marginal_counts = {} # { [conditional/marginal] : [counts] }
sent_counts = {} # { [word] : { [topic] : [counts] } }

#if USE_SENTS: P(ref | coh, top)
#else: P(pro | ref, coh, top, s_i)

#sys.stderr.write('topics: '+str(topics[0])+'\n\n')
#sys.stderr.write('sentences: '+str(sentlist[0])+'\n\n')
#sys.stderr.write('coco keys: '+str(coco_corpus[0]['SPAN'])+'\n\n')

for e in coco_corpus:
  #coco_corpus.dict_keys(['ANTECEDENT_SPAN', 'ENTITY_ID', 'SENTPOS', 'SPAN' : (277, 299), 'PRO', 'COHERENCE', 'CONTEXT'])
  #NB: currently, ref is the sentence position of the antecedent, but we may want to make ref a *distribution over positions* which is sampled from to get the antecedent
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
    head_begin = e['SPAN'][0]
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
    pro = topics[head_begin].split()[0] in PRONOUNS
    if pro not in full_joint_counts:
      full_joint_counts[pro] = {}
    full_joint_counts[pro][ref,coh,best_topic[0],sent_info] = full_joint_counts[pro].get((ref,coh,best_topic[0],sent_info), 0) + 1
    marginal_counts[ref,coh,best_topic[0],sent_info] = marginal_counts.get((ref,coh,best_topic[0],sent_info), 0) + 1
    if sent_info not in sent_counts:
      sent_counts[sent_info] = {}
    #NB: For now, sentences are generated from just topics (not coherence)
    sent_counts[sent_info][sent_topic] = sent_counts[sent_info].get(sent_topic, 0) + 1
  else:
    if ref not in full_joint_counts:
      full_joint_counts[ref] = {}
    full_joint_counts[ref][coh,best_topic[0]] = full_joint_counts[ref].get((coh,best_topic[0]), 0) + 1
    marginal_counts[coh,best_topic[0]] = marginal_counts.get((coh,best_topic[0]), 0) + 1

pcounts = {'full_joint': full_joint_counts, 'marginal': marginal_counts}
if USE_SENTS:
  topic_counts = {}
  for t in topics:
    mytopic = get_topic(t)
    topic_counts[mytopic] = topic_counts.get(mytopic, 0) + 1
  pcounts.update({'sent': sent_counts, 'topic': topic_counts})
with open(OPTS['output'], 'wb') as f:
  pickle.dump(pcounts, f)
