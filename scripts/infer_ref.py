#python infer_ref.py {--input REG_TAB_FILE ...} [--hold-out FILE] [--acc FILE]
# infer a latent referent variable
# tests on hold-out file to determine accuracy
# accuracy is output to the FILE specified by --acc or defaults to stderr

import math
import numpy
import operator
import pickle
import random
#import sklearn
#from sklearn.feature_extraction import DictVectorizer
#from sklearn import svm
import sys

DEP_VAL = "pro" #dependent variable to regress to when determining weights
# Full model
OMIT_VALS = ["ref_id"] #features to omit when determining feature weights
# Best binary model
#OMIT_VALS = ["ref_id","sentpos","coh","ant_syncat","ant_info","ref_topic"] #features to omit when determining feature weights
RANDOM_SEED = 37 #None yields random initialization

submodels = [('coh','ref'),('ref','pro')] #the dicts in model will be keyed on (cond,x)
NUMREFS = 20 #the initial number of possible referents

random.seed(RANDOM_SEED)

def initialize_corpus(corpus,keyname,startkeys):
  #initializes corpus (in place) with random draws from startkeys
  for obs in range(len(corpus)):
    corpus[obs][keyname] = random.choice(startkeys)

def normalize(model):
  #normalize the input model
  if type(model[model.keys()[0]]) == type({}):
    #we're in a conditional dictionary
    for k in model:
      normalize(model[k])
  else:
    total = 0
    for k in model:
      total += model[k]
    for k in model:
      model[k] /= total
  #model is modified in place *and* is returned
  return( model )

def pseudo_normalize(model,pseudocount = 0.5):
  #add pseudo counts to unobserved events
  #then normalize the input model
  if type(model[model.keys()[0]]) == type({}):
    #we're in a conditional dictionary
    #add a pseudo condition
    model['-1'] = dict((v,1) for k in model for v in model[k])
    for k in model:
      pseudo_normalize(model[k], pseudocount)
  else:
    total = 0
    for k in model:
      total += model[k]
    total += pseudocount
    model['-1'] = pseudocount
    for k in model:
      model[k] /= total
  #model is modified in place *and* is returned
  return( model )

def combine_dicts(global_dict,local_dict,prior = None):
  #combines probs from a local_dict with those in a global_dict
  for topkey in local_dict:
    if type(local_dict[topkey]) == type({}):
      if topkey not in global_dict:
        global_dict[topkey] = {}
      for lowkey in local_dict[topkey]:
        if prior:
          #use a latent prior distribution
          global_dict[topkey][lowkey] = global_dict[topkey].get(lowkey, 0) + local_dict[topkey][lowkey]*prior[topkey]
        else:
          global_dict[topkey][lowkey] = global_dict[topkey].get(lowkey, 0) + local_dict[topkey][lowkey]
    else:
      global_dict[topkey] = global_dict.get(topkey, 0) + local_dict[topkey]
  return(global_dict)

def marginalize_dicts(global_dict,local_dict):
  #marginalize over all conditions
  for topkey in local_dict:
    if type(local_dict[topkey]) == type({}):
      for lowkey in local_dict[topkey]:          
        global_dict[lowkey] = global_dict.get(lowkey, 0) + local_dict[topkey][lowkey]
    else:
      global_dict[topkey] = global_dict.get(topkey, 0) + local_dict[topkey]
  return(normalize(global_dict))

def fully_generate(global_dict,local_dict,prior = None):
  #calculate likelihood from using each setting of latent cond
  for topkey in local_dict:
    if type(local_dict[topkey]) == type({}):
      for lowkey in local_dict[topkey]:
        if prior:
          #use a latent prior distribution
          global_dict[topkey] = global_dict.get(topkey, 0) + local_dict[topkey][lowkey]*prior[topkey]
        else:
          global_dict[topkey] = global_dict.get(topkey, 0) + local_dict[topkey][lowkey]
    else:
      global_dict[topkey] = global_dict.get(topkey, 0) + local_dict[topkey]
  return(normalize(global_dict))

def E(corpus,modelkeys):
  #updates model expectations based on corpus
  #initialize new model
  model = {}
  for key in modelkeys:
    model[key] = {}
  #walk through corpus and count co-occurrences
  for obs in corpus:
    for submodel in model:
      if obs[submodel[0]] not in model[submodel]:
        #we haven't seen this cond before
        model[submodel][obs[submodel[0]]] = {}
      model[submodel][obs[submodel[0]]][obs[submodel[1]]] = model[submodel][obs[submodel[0]]].get(obs[submodel[1]],0) + 1
  for submodel in model:
    #add pseudo counts to unobserved events and normalize
    pseudo_normalize(model[submodel])
  return(model)

def M(corpus,model,latent_var):
  #maximize the likelihood of the corpus given the model
  #updating 'latent_var' for each obs to maximize the probability
  #then return the resulting likelihood
  likelihood = 0.0
  latconds = [s for s in model if latent_var == s[0]]
  if latconds != []:
    possconds = model[latconds[0]].keys()
  latevents = [s for s in model if latent_var == s[1]]
  #sys.stderr.write('latconds: '+str(latconds)+'\n')
  #sys.stderr.write('latevents: '+str(latevents)+'\n')
  for ix,obs in enumerate(corpus):
    if ix %100 == 0:
      sys.stderr.write(str(ix)+ '\n')
    if latevents != []:
      #there are ways to generate this latent var
      prior = {}
      for obs in corpus:
        for submodel in latevents:
          #sum over all ways of generating latevent
          prior = marginalize_dicts(prior,model[submodel][obs[submodel[0]]])
        if latconds != []:
          #there are observed events conditioned on this latent var
          lik = {}
          for submodel in latconds:
            #calc likelihood of generating all downstream vars
            for val in prior:
              lik = fully_generate(lik,model[submodel][val],prior)
    else:
      lik = {}
      if latconds != []:
        #there are observed events conditioned on this latent var
          for submodel in latconds:
            #calc likelihood of generating all downstream vars
            for val in possconds:
              lik = full_generate(lik,model[submodel][val])
      else:
        raise #The latent variable doesn't exist in the model!
    #update the obs with new value for latent variable
    if lik != {}:
      #latent var generated something(s) (all values are also include prob of being generated, themselves)
      #each var is associated with its corpus likelihood
      best = max(lik.items(), key=operator.itemgetter(1)) #Pick the best label
      #NB: In future, maybe we should choose the label randomly according to the probabilities
      obs[latent_var] = best[0]
      likelihood += math.log(best[1])
    else:
      #latent var was generated (but didn't generate anything)
      best = max(prior.items(), key=operator.itemgetter(1)) #Pick the best label
      #NB: In future, maybe we should choose the label randomly according to the probabilities
      obs[latent_var] = best[0]
      likelihood += math.log(best[1])
  return(likelihood)

def choose_best(obs,model,collapse,predict_key,genchain):
  #determines the best assignment for predict_key
  #collapses across all the 'collapse' variables, which are latent
  #genchain is used to determine the order of model traversal NB: could be made A) more efficient and B) more general
  liklist = []
  for modi,submodel in enumerate(genchain):
    lik = {}
    if submodel[0] in collapse: #the condition var is latent
      if submodel[1] in collapse: #the generated var is also latent
        pass #we'll deal with this case when it arises
      else: #generated var is observed
        if modi == 0: #this is the first generation of the model
          pass
        else: #we've previously generated things from the model
          for val in liklist[modi-1]:
            #for each condition that could have been generated,
            #generate all of its child events
            lik = fully_generate(lik,model[submodel][val],liklist[modi-1])
          liklist.append(lik)
    elif submodel[1] in collapse: #the generated var is latent
      if obs[submodel[0]] not in model[submodel]:
        #we haven't seen this condition before
        liklist.append(model[submodel]['-1'])
      else:
        liklist.append(model[submodel][obs[submodel[0]]])
      #now lik is a dict of [ref]:[prob]
    else:
      #no latent variables in this submodel, so why do we care?
      pass
  return( max(liklist[-1].items(), key=operator.itemgetter(1)) ) #Report best label and its prob

inputlist = []
OPTS = {}
for aix in range(1,len(sys.argv)):
  if len(sys.argv[aix]) < 2 or sys.argv[aix][:2] != '--':
    #filename or malformed arg
    continue
  elif aix < len(sys.argv) - 1 and len(sys.argv[aix+1]) > 2 and sys.argv[aix+1][:2] == '--':
    #missing filename, so simple arg
    OPTS[sys.argv[aix][2:]] = True
  elif sys.argv[aix][2:] == 'input':
    inputlist.append(sys.argv[aix+1])
  else:
    OPTS[sys.argv[aix][2:]] = sys.argv[aix+1]

corpus = []
for infile in inputlist:
  if 'hold-out' in OPTS and infile == OPTS['hold-out']: #don't train on held-out data
    continue
  with open(infile,'rb') as f:
    newfile = pickle.load(f)
    corpus += newfile

##since all categorial values are one hot, each vector associated w/ a feature is FEATURE=X, so ensure the entire feature name should be omitted
#DEP_VAL = DEP_VAL + '='
#for i,v in enumerate(OMIT_VALS):
#  if v not in ['sentpos']: #don't worry about non-categorial variables
#    OMIT_VALS[i] = OMIT_VALS[i]+'='

model = {}
for submodel in submodels:
  model[submodel] = {}
  
#initialize corpus with latent refs
initrefs = range(NUMREFS) #[numpy.random.randint(1000, size=NUMREFS)
initialize_corpus(corpus,'ref',initrefs)

oldlik = 0
lik = 100
threshold = 1.0 #assume convergence if we reach this point

#EM phase
while abs(lik - oldlik) > threshold:
  oldlik = lik
  model = E(corpus,model.keys())
#  if FIRST:
#    sys.stderr.write('Expectation done\n')
#    sys.stderr.write('\n'.join([str(s)+': '+str(model[s]) for s in model])+'\n')
  lik = M(corpus,model,'ref')
#  if FIRST:
#    FIRST = False
#    sys.stderr.write('Maximization done\n')
#    sys.stderr.write('\n'.join([str(s)+': '+str(model[s]) for s in model])+'\n')
  sys.stderr.write('Likelihood: '+str(lik)+'\n')

#Scoring phase
if 'hold-out' in OPTS:
  with open(OPTS['hold-out'],'rb') as f:
    testdata = pickle.load(f)
else:
  testdata = corpus
  
total = 0
correct = 0
for obs in testdata:
  guess,guessprob = choose_best(obs,model,collapse=['ref'],predict_key=DEP_VAL,genchain=[('coh','ref'),('ref','pro')])
  total += 1
  if guess == obs[DEP_VAL]:
    correct += 1
if total != 0:
  score = correct / total
else:
  score = 0.0
if 'acc' in OPTS:
  with open(OPTS['acc'],'w') as f:
    f.write('Total: '+str(correct)+'/'+str(total)+'='+str(score)+'\n')
else:
  sys.stderr.write('Total: '+str(correct)+'/'+str(total)+'='+str(score)+'\n')
