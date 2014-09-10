#calc_likelihood.py --model FILE --input FILE --topics FILE --sentences FILE --output FILE
# uses a model to compute the likelihood of a corpus
#      model FILE is the probability model for computing the likelihood
#      input FILE is the corpus to compute the likelihood over
#      topics FILE is the topic model of the corpus of interest
#      sentences FILE is the list of sentence boundaries in the corpus of interest
#      output FILE designates where to write output

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

def find_sent(inix, sentlist):
  old_six = 0
  for six,sent in enumerate(sentlist):
    if sent >= inix:
      return(old_six,sentlist[old_six])
    old_six = six
  return(len(sentlist)-1,sentlist[-1])

with open(OPTS['model'], 'rb') as f:
  model = pickle.load(f)

with open(OPTS['input'], 'rb') as f:
  corpus = pickle.load(f)

with open(OPTS['topics'], 'r') as f:
  topics = f.readlines()

with open(OPTS['sentences'], 'rb') as f:
  sentlist = pickle.load(f)
  
PRONOUNS = ['he','she','they','we','I','you','them','that','those','it','one', 'who', 'which']

#sys.stderr.write('topics: '+str(topics[0])+'\n\n')
#sys.stderr.write('sentences: '+str(sentlist[0])+'\n\n')
#sys.stderr.write('coco keys: '+str(coco_corpus[0]['SPAN'])+'\n\n')

likelihood = 0

for e in corpus:
  #coco_corpus.dict_keys(['ANTECEDENT_SPAN', 'ENTITY_ID', 'SENTPOS', 'SPAN' : (277, 299), 'PRO', 'COHERENCE', 'CONTEXT'])
  #NB: currently, ref is the sentence position of the antecedent, but we may want to make ref a *distribution over positions* which is sampled from to get the antecedent
  ref = e['ENTITY_ID']
  topic_list = {}
  for tix in range(e['SPAN'][0],e['SPAN'][1]):
    my_topic = get_topic(topics[tix])
    topic_list[my_topic] = topic_list.get(my_topic, 0) + 1
  #NB: for now, we'll have the topics vote first past the post, but we may want to allow proportional topic assignments in the future
  #sentence context
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
  output = []
  thissent = find_sent(head_begin,sentlist)
  for i in range(max(0,thissent[1]-3),sentlist[thissent[0]+1]):#head_begin - e['SENTPOS'],next_sent):
      output.append(topics[i].split()[0])
  sys.stderr.write(' '.join(output)+'\n')
  ### /DEBUG

  ctr = 1
  while sent_topic == '-1':
    # If the sentence/context has a generic topic (i.e. could have been generated by any topic),
    #    find the next topic to appear and assume that one generated the preceding context
    # Also assume that topic-associated word is a better cue to context than the preceding words
    sent_info = topics[head_begin - e['SENTPOS'] + ctr].split()[0]
    sent_topic = topics[head_begin - e['SENTPOS'] + ctr].split()[1]
    ctr += 1
  best_topic = ['-1',0]
  for t in topic_list:
    if t != '-1' and topic_list[t] > best_topic[1]:
      best_topic = [t,topic_list[t]]
  if best_topic[0] == '-1':
    #NB: None of the words in the head had a topic (they were all stop words and so could have been generated by any topic)
    #    So find the closest preceding topic and assign the head to that topic
    for tix in range(head_begin,head_begin - e['SENTPOS'],-1):
      #search preceding context for a valid topic
      if get_topic(topics[tix]) != '-1':
        best_topic = [get_topic(topics[tix]),head_begin - tix]
        break
    for tix in range(e['SPAN'][1],next_sent):
      #make sure there's no closer topic succeeding the head
      if best_topic[0] != '-1' and tix - e['SPAN'][1] >= best_topic[1]: #we already found a closer topic
        break
      if get_topic(topics[tix]) != '-1':
        best_topic = [get_topic(topics[tix]),-1]
  if best_topic[0] == '-1':
    #if there's no valid topic in this sentence, then I'm not sure we have much to go on; throw out this datapoint;
    sys.stderr.write("Couldn't find a valid topic assignment... skipping datapoint.\n")
    continue
      
  coh = e['COHERENCE']
  
  pro = topics[head_begin].split()[0] in PRONOUNS
  try:
    likelihood += model['pro'][pro][ref,coh,best_topic[0],sent_info]
  except:
    output = []
    for i in range(thissent[1],sentlist[thissent[0]+1]): #head_begin - e['SENTPOS'],next_sent):
      output.append(topics[i].split()[0])
    sys.stderr.write(' '.join(output)+'\n')
    raise
  likelihood += model['ref'][ref][coh,best_topic[0]]
  likelihood += model['coh'][coh]
  likelihood += model['topic'][best_topic[0]]
  likelihood += model['sent'][sent_info][sent_topic]
  likelihood += model['topic'][sent_topic]
  
with open(OPTS['output'], 'w') as f:
  f.write(str(likelihood)+'\n')
