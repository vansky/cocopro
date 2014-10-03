#calc_pcounts.py --coco-corpus FILE --topics FILE --sentences FILE --use-sents --output FILE
# outputs counts from topics, coref, and coherence data for probability computations
#      coco-corpus FILE is the (pickled) aligned dgb/c3 corpus
#      topics FILE contains words from the DGB with associated topic assignments
#      sentences FILE contains a list of the sentence boundary indices from dgb
#      output FILE designates where to write output; '-' designates stdin

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
    

with open(OPTS['coco-corpus'], 'rb') as f:
  coco_corpus = pickle.load(f)

with open(OPTS['topics'], 'r') as f:
  topics = f.readlines()

#USE_SENTS = False
#if 'use-sents' in OPTS:
#  USE_SENTS = True
with open(OPTS['sentences'], 'rb') as f:
  sentlist = pickle.load(f)

PRONOUNS = ['he','she','they','we','I','you','them','that','those','it','one']
prob_counts = {} # { [item] : { [conditional/marginal] : [counts] } }
marginal_counts = {} # { [conditional/marginal] : [counts] }
sent_counts = {} # { [word] : { [topic] : [counts] } }
coh_counts = {} # { [coh] : [counts] }

#if USE_SENTS: P(ref | coh, top)
#else: P(pro | ref, coh, top, s_i)

#sys.stderr.write('topics: '+str(topics[0])+'\n\n')
#sys.stderr.write('sentences: '+str(sentlist[0])+'\n\n')
#sys.stderr.write('coco keys: '+str(coco_corpus[0]['SPAN'])+'\n\n')

for e in coco_corpus:
  #coco_corpus.dict_keys(['ANTECEDENT_SPAN', 'ENTITY_ID', 'SENTPOS', 'SPAN' : (277, 299), 'PRO', 'COHERENCE', 'CONTEXT'])
  #NB: currently, ref is the sentence position of the antecedent, but we may want to make ref a *distribution over positions* which is sampled from to get the antecedent
  ref = e['ENTITY_ID']
#  topic_list = {}
#  for tix in range(e['SPAN'][0],e['SPAN'][1]):
#    #determine the topic of the head
#    #NB: for now, we'll have the topics vote first past the post, but we may want to allow proportional topic assignments in the future
#    if tix >=len(topics):
#      #NB: total hack to get by an issue where section 95 of c3 indexes beyond the end of the file... (possibly introduced during munging c3?)
#      sys.stderr.write('span: '+str(e['SPAN'][0])+':'+str(e['SPAN'][1])+ 'in'+ str(len(topics))+'\n')
#      break
#    my_topic = get_topic(topics[tix])
#    topic_list[my_topic] = topic_list.get(my_topic, 0) + 1
  coh = e['COHERENCE']
  coh_counts[coh] = coh_counts.get(coh, 0) + 1
  
  #sentence portion
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

    ### DEBUG
#    output = []
#    for i in range(head_begin - e['SENTPOS'],next_sent):
#      output.append(topics[i].split()[0])
#    sys.stderr.write(' '.join(output)+'\n')
    ### /DEBUG

#  ctr = 1
#  while sent_topic == '-1':
#    # If the sentence/context has a generic topic (i.e. could have been generated by any topic),
#    #    find the next topic to appear and assume that one generated the preceding context
#    # Also assume that topic-associated word is a better cue to context than the preceding words
#    sent_info = topics[head_begin - e['SENTPOS'] + ctr].split()[0]
#    sent_topic = topics[head_begin - e['SENTPOS'] + ctr].split()[1]
#    ctr += 1

#  best_topic = ['-1',0]
#  for t in topic_list:
#    if t != '-1' and topic_list[t] > best_topic[1]:
#      best_topic = [t,topic_list[t]]
#  if best_topic[0] == '-1':
#    #NB: None of the words in the head had a topic (they were all stop words and so could have been generated by any topic)
#    #    So find the closest preceding topic and assign the head to that topic
#    for tix in range(head_begin,head_begin - e['SENTPOS'],-1):
#      #search preceding context for a valid topic
#      if get_topic(topics[tix]) != '-1':
#        best_topic = [get_topic(topics[tix]),head_begin - tix]
#        break
#    for tix in range(e['SPAN'][1],next_sent):
#      #make sure there's no closer topic succeeding the head
#      if best_topic[0] != '-1' and tix - e['SPAN'][1] >= best_topic[1]: #we already found a closer topic
#        break
#      if get_topic(topics[tix]) != '-1':
#        best_topic = [get_topic(topics[tix]),-1]
#  if best_topic[0] == '-1':
#    #if there's no valid topic in this sentence, then I'm not sure we have much to go on; throw out this datapoint;
#    sys.stderr.write("Couldn't find a valid topic assignment... skipping datapoint.\n")
#    continue

  #binary pro
  pro = str(topics[head_begin].split()[0] in PRONOUNS) #possible: 'True', 'False'
  if ref not in pro_from_ref:
    pro_from_ref[ref] = {'True':0.5, 'False':0.5}
  pro_from_ref[ref][pro] += 1
  if coh not in pro_from_coh:
    pro_from_coh[coh] = {'True':0.5, 'False':0.5}
  pro_from_coh[coh][pro] += 1
  if top not in pro_from_top:
    pro_from_top[top] = {'True':0.5, 'False':0.5}
  pro_from_top[top][pro] += 1
  if sent not in pro_from_sent:
    pro_from_sent[sent] = {'True':0.5, 'False':0.5}
  pro_from_sent[sent][pro] += 1

  #NB: for now, ref is an observed variable (ref sentpos), but I really think it'd be better if it was a latent variable that generated the observed ref sentpos
  POSS_REFS = 20
  if coh not in ref_from_coh: #NB: possible...? say range(20)?
    ref_from_coh[coh] = {}
    for i in range(POSS_REFS):
      ref_from_coh[coh][i] = 1.0/POSS_REFS #i might need to be cast as string
  ref_from_coh[coh][ref] += 1
  if top not in ref_from_top:
    ref_from_top[top] = {}
    for i in range(POSS_REFS):
      ref_from_top[top][i] = 1.0/POSS_REFS #i might need to be cast as string
  ref_from_top[top][ref] += 1

  sent_info_prior = 1.0/1000
  if sent_topic not in s_from_top: #NB: possible...? no idea, so let's say 1/1000?
    s_from_top[sent_topic] = {'-1': sent_info_prior}
  #NB: For now, sentences are generated from just topics (not coherence)
  s_from_top[sent_topic][sent_info] = s_from_top[sent_topic].get(sent_info, sent_info_prior) + 1
  
  if sent_info not in sent_counts:
    sent_counts[sent_info] = {}
  sent_counts[sent_info] = sent_counts.get(sent_info, sent_info_prior) + 1
  ###    
  #flat multinomial pro
  #for pro in PRONOUNS+['other']:
  ###
  #hierarchic multinomial pro
  #for class in PROCLASSES.keys():
  #  for pro in PROCLASSES['class']:
  #  #pro='other' case
    
pcounts = {'pro_from_ref': pro_from_ref, 'pro_from_coh':pro_from_coh, 'pro_from_top':pro_from_top, 'pro_from_sent':pro_from_sent,\
             'ref_from_coh':ref_from_coh, 'ref_from_top':ref_from_top,\
             's_from_top':s_from_top}
topic_counts = {}
for t in topics:
  mytopic = get_topic(t)
  topic_counts[mytopic] = topic_counts.get(mytopic, 0) + 1
pcounts.update({'sent': sent_counts, 'topic': topic_counts, 'coh': coh_counts})
with open(OPTS['output'], 'wb') as f:
  # pro_from_ref, pro_from_coh, pro_from_top, pro_from_sent,
  # ref_from_coh, ref_from_top, s_from_top,
  # sent, topic, coh
  pickle.dump(pcounts, f)
