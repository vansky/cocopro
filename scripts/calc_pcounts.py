#calc_pcounts.py --coco-corpus FILE --topics FILE --sentences FILE --vectors FILE --categories FILE --regression FILE --output FILE
# outputs counts from topics, coref, and coherence data for probability computations
#      coco-corpus FILE is the (pickled) aligned dgb/c3 corpus
#      topics FILE contains words from the DGB with associated topic assignments
#      sentences FILE contains a list of the sentence boundary indices from dgb
#      vectors FILE contains a list (word/line) of dgb words and their distributed reps
#      categories FILE contains a list (word/line) of dgb words and their associated syntactic categories
#      regression FILE contains a list of all obs attributes for use in regression
#      output FILE designates where to write output; '-' designates stdin

from __future__ import division
import pickle
import re
import sys

VERBOSE=False #Exposes a couple bugs we'll likely need to address later as they make the data sloppy (might be inherent in c3)
WEAKPRIOR=True #Weakens/Strengthens prior PRO expectations
ADD_PSEUDO=False #Adds pseudo counts at this document-level stage
ANT_VECTORS = False #uses distributed representation of antecedent
SENT_VECTORS = False #uses distributed representation of sentence
BI_VECTORS = False #uses distributed representation of bigram context

COLLAPSE_PRO = 2 # how should pro values be collapsed (0 = uncollapsed)

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
  return(line.strip().split()[-1])

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

with open(OPTS['coco-corpus'], 'rb') as f:
  coco_corpus = pickle.load(f)

with open(OPTS['topics'], 'r') as f:
  topics = f.readlines()

with open(OPTS['sentences'], 'r') as f:
  sentlist = [int(s) for s in f.readlines() if s.strip() != '']

with open(OPTS['vectors'], 'r') as f:
  vectors = [l.strip() for l in f.readlines()]

with open(OPTS['categories'], 'r') as f:
  syncats = f.readlines()
  
PRONOUNS = ['he','she','they','we','I','you','them','that','those','it','one']
#sent_counts = {'-1': {}} # { [word] : { [topic] : [counts] } }
coh_counts = {} # { [coh] : [counts] }
pro_counts = {} # { [pro] : [counts] }

#binary
pro_from_ref = {} # { [ref] : { [pro] : [counts] } }
pro_from_coh = {} # { [coh] : { [pro] : [counts] } }
pro_from_top = {} # { [topic] : { [pro] : [counts] } }
pro_from_sent = {} # { [sent] : { [pro] : [counts] } }
pro_from_sentpos = {} # { [sentpos] : { [pro] : [counts] } }
pro_from_ant = {} # { [ant] : { [pro] : [counts] } }
pro_from_ant_syncat = {} # { [ant_syncat] : { [pro] : [counts] } }
pro_from_bi = {} # { [bi] : { [pro] : [counts] } }
pro_from_ref_syncat = {} # { [syncat] : { [pro] : [counts] } }

ref_from_coh = {} # { [coh] : { [ref] : [counts] } }
ref_from_top = {} # { [topic] : { [ref] : [counts] } }

s_from_top = {} # { [topic] : { [word] : [counts] } }

regtab = [] #an output table to regress feature weights to

# regtab.append('pro coh ref_id sentpos sent_info ref_topic ant_info bi_info ref_syncat ant_syncat'+'\n')
# pro = str
# coh = str
# ref_id = str
# sentpos = int
# sent_info = str
# ref_topic = str
# ant_info = str
# bi_info = str
# x_syncat = str
for e in coco_corpus:
  #coco_corpus.dict_keys(['ANTECEDENT_SPAN', 'ENTITY_ID', 'SENTPOS', 'SPAN' : (277, 299), 'PRO', 'COHERENCE', 'CONTEXT', 'HEAD', 'ANTECEDENT_HEAD'])
  #NB: currently, ref is the sentence position of the antecedent, but we may want to make ref a *distribution over positions* which is sampled from to get the antecedent
  ref_id = str(e['ENTITY_ID'])
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
  head_begin = e['HEAD'][0]
  head_end = e['HEAD'][1]
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
  if SENT_VECTORS:
    sent_info = ' '.join(vectors[head_begin - e['SENTPOS']].split()[1:])
  else:
    sent_info = topics[head_begin - e['SENTPOS']].split()[0]
  sent_topic = topics[head_begin - e['SENTPOS']].split()[1]
  sentpos = e['SENTPOS']
  ref_topic = topics[head_begin].split()[1]
  if ANT_VECTORS:
    ant_info = ' '.join(vectors[e['ANTECEDENT_HEAD'][0]].split()[1:]) #must be string since lists aren't hashable
  else:
    ant_info = topics[e['ANTECEDENT_HEAD'][0]].split()[0]
  if BI_VECTORS:
    bi_info = ' '.join(vectors[head_begin - 1].split()[1:])
  else:
    bi_info = topics[head_begin - 1].split()[0]

  ref_syncat = syncats[head_begin].split()[1]
  ant_syncat = syncats[e['ANTECEDENT_HEAD'][0]].split()[1]
  
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
#  pro = str(topics[head_begin].split()[0].lower() in PRONOUNS) #possible: 'True', 'False'
  if COLLAPSE_PRO == 0:
    pro = e['TYPE'] #mention type
  elif COLLAPSE_PRO == 2:
    if e['TYPE'] in ['WHQ','PRO']:
      pro = 'PRO'
    else:
      pro = 'OTHER'
  else:
    raise #undefined collapse value
  pro_counts[pro] = pro_counts.get(pro,0) + 1
  
  if ref_id not in pro_from_ref:
    pro_from_ref[ref_id] = {}
  pro_from_ref[ref_id][pro] = pro_from_ref[ref_id].get(pro,0) + 1
  if sentpos not in pro_from_sentpos:
    pro_from_sentpos[sentpos] = {}
  pro_from_sentpos[sentpos][pro] = pro_from_sentpos[sentpos].get(pro,0) + 1
  if coh not in pro_from_coh:
    pro_from_coh[coh] = {}
  pro_from_coh[coh][pro] = pro_from_coh[coh].get(pro,0) + 1
  if ref_topic not in pro_from_top:
    pro_from_top[ref_topic] = {}
  pro_from_top[ref_topic][pro] = pro_from_top[ref_topic].get(pro,0) + 1
  if sent_info not in pro_from_sent:
    pro_from_sent[sent_info] = {}
  pro_from_sent[sent_info][pro] = pro_from_sent[sent_info].get(pro,0) + 1
  if ant_info not in pro_from_ant:
    pro_from_ant[ant_info] = {}
  pro_from_ant[ant_info][pro] = pro_from_ant[ant_info].get(pro,0) + 1
  if bi_info not in pro_from_bi:
    pro_from_bi[bi_info] = {}
  pro_from_bi[bi_info][pro] = pro_from_bi[bi_info].get(pro,0) + 1
  if ref_syncat not in pro_from_ref_syncat:
    pro_from_ref_syncat[ref_syncat] = {}
  pro_from_ref_syncat[ref_syncat][pro] = pro_from_ref_syncat[ref_syncat].get(pro,0) + 1
  if ant_syncat not in pro_from_ant_syncat:
    pro_from_ant_syncat[ant_syncat] = {}
  pro_from_ant_syncat[ant_syncat][pro] = pro_from_ant_syncat[ant_syncat].get(pro,0) + 1

  #update regression table to determine feature weights
  regtab.append({'pro':pro,
                 'coh':coh,
                 'ref_id':ref_id,
                 'sentpos':int(sentpos),
                 'sent_info':sent_info,
                 'ref_topic':ref_topic,
                 'ant_info':ant_info,
                 'bi_info':bi_info,
                 'ref_syncat':ref_syncat,
                 'ant_syncat':ant_syncat })
  

  #NB: for now, ref is an observed variable (ref sentpos), but I really think it'd be better if it was a latent variable that generated the observed ref sentpos
  POSS_REFS = 100
  if coh not in ref_from_coh: #NB: possible...? say range(100)?
    ref_from_coh[coh] = {}
    for i in range(POSS_REFS):
      ref_from_coh[coh][str(i)] = 1.0/POSS_REFS #i might need to be cast as string
  ref_from_coh[coh][ref_id] += 1
  #### DEBUG
  if VERBOSE:
    if int(ref_id) <= 35:
      output = [ref_id+': ']
      for i in range(head_begin - e['SENTPOS'],head_begin):
        output.append(topics[i].split()[0])
      output.append('[')
      for i in range(head_begin,head_end+1):
        output.append(topics[i].split()[0])
      output.append(']')
      for i in range(head_end+1,next_sent):
        output.append(topics[i].split()[0])
      sys.stderr.write(' '.join(output)+'\n')
  #### /DEBUG
  if ref_topic not in ref_from_top:
    ref_from_top[ref_topic] = {}
    for i in range(POSS_REFS):
      ref_from_top[ref_topic][str(i)] = 1.0/POSS_REFS #i might need to be cast as string
  ref_from_top[ref_topic][ref_id] += 1

  sent_info_prior = 1.0/1000
  if sent_topic not in s_from_top: #NB: possible...? no idea, so let's say 1/1000?
    s_from_top[sent_topic] = {'-1': sent_info_prior}
  #NB: For now, sentences are generated from just topics (not coherence)
  s_from_top[sent_topic][sent_info] = s_from_top[sent_topic].get(sent_info, sent_info_prior) + 1
  
#  sent_counts[sent_info] = sent_counts.get(sent_info, 0) + 1
  ###    
  #flat multinomial pro
  #for pro in PRONOUNS+['other']:
  ###
  #hierarchic multinomial pro
  #for class in PROCLASSES.keys():
  #  for pro in PROCLASSES['class']:
  #  #pro='other' case

###DEBUG
## Use scripts/find_pros.py to collect the output from the following
#posskeys = []
#for r in pro_from_ref:
#  posskeys += list(pro_from_ref[r])
#posskeys = list(set(posskeys)) #remove duplicates before re-listing possible keys
#if posskeys != []:
#  with open(OPTS['output']+'.prolist','w') as f:
#    f.write(' '.join(posskeys)+'\n')
#  ###/DEBUG

###DEBUG
## Use scripts/find_pros.py to collect the output from the following
#posskeys = list(pro_from_coh)
#if posskeys != []:
#  with open(OPTS['output']+'.cohlist','w') as f:
#    f.write(' '.join(posskeys)+'\n')
#  ###/DEBUG


#Possible values for PRO:
#  10: ['PRE', 'NOM', 'BAR', 'PRO', 'HLS', 'NAM', 'ARC', 'WHQ', 'PTV', 'APP']
#posspros = ['PRE', 'NOM', 'BAR', 'PRO', 'HLS', 'NAM', 'ARC', 'WHQ', 'PTV', 'APP']
#prior = 1 / len(posspros)
#for d in [pro_from_ref, pro_from_coh, pro_from_top, pro_from_sent]:
#  #assign uniform priors over the set of possible PRO values
#  for outer in d:
#    for pro in posspros:
#      d[outer][pro] = d[outer].get(pro,0) + prior

if ADD_PSEUDO:
  if pro_counts != {}:
    if WEAKPRIOR:
      #normalize to largest thing to weaken prior counts
      bigkey = max(pro_counts.values())
      for p in pro_counts:
        pro_counts[p] = pro_counts[p] / bigkey
    else:
      #normalize to smallest thing to strengthen prior counts
      smallkey = min(pro_counts.values())
      for p in pro_counts:
        pro_counts[p] = pro_counts[p] / smallkey

  for d in (pro_from_ref, pro_from_coh, pro_from_top, pro_from_sent, pro_from_ant, pro_from_bi):
    d = add_pseudocounts(d,pro_counts)

  for d in (ref_from_coh, ref_from_top):
    d = add_pseudocounts(d)
#Possible values for COH:
#  127: ['elab-det-time-org-num', 'elab-num-pers-det', 'elab-loc', 'elab-det-num-pers-org', 'elab-det-loc-org-time', 'elab-loc-pers', 'elab', 'elab-time-pers-loc', 'elab-det-org-num-time', 'elab-pers-time-loc', 'elab-det-pers', 'elab-det-time-org', 'elab-pers-det', 'elab-pers-org-det', 'elab-pers-det-org-time-num', 'elab-num-time', 'elab-det-num-time', 'elab-det-time-pers', 'elab-det-loc-num-org', 'elab-det-num-pers-org-loc-time', 'elab-pers-loc', 'gen', 'elab-pers-det-time-num', 'attr', 'elab-time', 'elab-time-num', 'elab-det-num-loc-time', '-1', 'elab-det-pers-time-org', 'elab-pers-org', 'elab-det-time-org-pers', 'elab-org-pers-det', 'elab-loc-det', 'elab-pers-num', 'elab-det-org-pers', 'elab-det-num', 'elab-det-time-loc', 'elab-time-det-num', 'elab-det-num-pers', 'elab-pers-time', 'elab-det-pers-time', 'elab-det-pers-org-time-num', 'elab-det-pers-loc-org', 'contrast', 'elab-num-pers', 'elab-det-org-loc', 'elab-org', 'elab-det-num-loc', 'elab-det-num-pers-time', 'elab-org-num', 'elab-det-pers-loc', 'elab-det-org-num', 'elab-det-pers-org-time', 'elab-org-time', 'elab-pers-loc-num', 'elab-loc-org-num', 'elab-det-time-num-org-loc-pers', 'elab-pers-loc-time', 'contr', 'elab-time-org', 'elab-det', 'elab-det-pers-org-num', 'elab-loc-time-det', 'elab-det-org-time-num-pers', 'elab-det-pers-time-loc', 'ce', 'elab-pers-det-loc', 'elab-det-pers-num-org', 'elab-dec-loc-pers', 'elab-det-num-org-loc', 'elab-per', 'elab-det-time', 'elab-det-pers-org', 'elab-detg', 'elab-org-det', 'elab-det-loc-num', 'elab-det-pers-org-loc', 'elab-time-loc', 'elab-det-loc-org-num', 'elab-time-num-det', 'elab-org-pers', 'elab-time-det-loc', 'elab-det-loc-org', 'elab-num-time-det', 'elab-det-pers-org-num-loc', 'elab-num-loc-org-pers', 'elab-pers-time-org', 'elab-loc-org', 'elab-det-org-loc-pers', 'temp', 'expv', 'elab-det-time-num-org', 'elab-det-pers-loc-org-num-time', 'elab-det-pers-loc-time-org', 'elab-det-loc-pers-time', 'elab-time-det', 'elab-pers-org-loc', 'elab-det-time-loc-org', 'elab-loc-det-pers', 'elab-num', 'cond', 'elab-det-pers-num', 'elab-num-loc-det', 'elab-time-det-org-pers', 'elab-pers-det-time', 'par', 'elab-loc-org-pers-det', 'same', 'elab-det-pers-time-num', 'examp', 'elab-det-loc-time', 'elab-det-loc', 'elab-det-loc-pers', 'elab-num-org-time', 'elab-pers', 'elab-det-org', 'elab-det-org-time-loc-num-pers', 'elab-det-pers-loc-time', 'elab-det-num-org', 'parallel', 'elab-num-loc-pers-det', 'elab-det-time-pers-num', 'elab-det-num-time-loc', 'elab-num-det-pers', 'elab-det-num-pers-loc', 'elab-num-loc-det-pers', 'elab-det-time-num']
pcounts = {'pro_from_ref': pro_from_ref, 'pro_from_coh':pro_from_coh, 'pro_from_top':pro_from_top, 'pro_from_sent':pro_from_sent, 'pro_from_ant':pro_from_ant,\
             'pro_from_bi':pro_from_bi, 'pro_from_ref_syncat':pro_from_ref_syncat, 'pro_from_ant_syncat':pro_from_ant_syncat, 'pro_from_sentpos':pro_from_sentpos, \
             'ref_from_coh':ref_from_coh, 'ref_from_top':ref_from_top,\
             's_from_top':s_from_top}
topic_counts = {}
for t in topics:
  mytopic = get_topic(t)
  topic_counts[mytopic] = topic_counts.get(mytopic, 0) + 1
#pcounts.update({'sent': sent_counts, 'topic': topic_counts, 'coh': coh_counts})
pcounts.update({'topic': topic_counts, 'coh': coh_counts, 'pro': pro_counts})
with open(OPTS['regression'], 'wb') as f:
  pickle.dump(regtab,f)
with open(OPTS['output'], 'wb') as f:
  # pro_from_ref, pro_from_coh, pro_from_top, pro_from_sent,
  # ref_from_coh, ref_from_top, s_from_top,
  # sent, topic, coh, pro
  pickle.dump(pcounts, f)
