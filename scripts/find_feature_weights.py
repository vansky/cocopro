#python find_feature_weights.py {--input REG_TAB_FILE ...} [--hold-out FILE] [--acc FILE]
# outputs regression weights to sys.stdout
# tests on hold-out file to determine accuracy
# accuracy is output to the FILE specified by --acc or defaults to stderr

import math
import numpy
import pickle
import sklearn
from sklearn.feature_extraction import DictVectorizer
from sklearn import svm
import sys

DEP_VAL = "pro" #dependent variable to regress to when determining weights
# Full model
OMIT_VALS = ["ref_id"] #features to omit when determining feature weights
# Best binary model
#OMIT_VALS = ["ref_id","sentpos","coh","ant_syncat","ant_info","ref_topic"] #features to omit when determining feature weights
RANDOM_SEED = 37 #None yields random initialization

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

fullindict = []
indict = []
for infile in inputlist:
  if 'hold-out' in OPTS and infile == OPTS['hold-out']: #don't train on held-out data
    with open(infile,'rb') as f:
      fullindict += pickle.load(f)
    continue
  with open(infile,'rb') as f:
    newfile = pickle.load(f)
    indict += newfile
    fullindict += newfile

#since all categorial values are one hot, each vector associated w/ a feature is FEATURE=X, so ensure the entire feature name should be omitted
DEP_VAL = DEP_VAL + '='
for i,v in enumerate(OMIT_VALS):
  if v not in ['sentpos']: #don't worry about non-categorial variables
    OMIT_VALS[i] = OMIT_VALS[i]+'='

#suck the input dict lists in, encode categorial variables as one-hot, and store as a scipy.sparse matrix of [obs][feature_vec_element]
myobs = DictVectorizer()
myobs.fit(fullindict) #allow the classifier to know of the existence of all the data (for testing purposes)
#myobs_scaled = sklearn.preprocessing.scale(myobs, with_mean=False) #memory-efficient, scales (but doesn't center) all features/columns
myobs_a = myobs.transform(indict).toarray()
myobs_scaled = sklearn.preprocessing.scale(myobs_a) #less memory efficient, but centers and scales all features/columns

#Regress an SVM classifier to distinguish between the classes and output the weights
dep_ix = []
omit_ix = []
feature_names = myobs.get_feature_names()
for i,k in enumerate(feature_names):
  if k[:len(DEP_VAL)] == DEP_VAL:
    dep_ix.append(i)
    omit_ix.append(i)
    continue
  for v in OMIT_VALS:
    if k[:len(v)] == v:
      omit_ix.append(i)
if dep_ix == []:
  raise #Invalid DEP_VAR keys
#y = myobs_scaled.getcol(dep_ix) #pull out the dependent var
y_raw = myobs_a[:,dep_ix[0]].reshape(-1,1) #pull out the dependent var columns
for i in dep_ix[1:]:
  y_raw = numpy.append(y_raw,myobs_a[:,i].reshape(-1,1),1)  #Need to append columns to one another!
y = numpy.nonzero(y_raw)[1]#.astype("float") #grab the dimension that's one-hot for the dependent variable
#the following is only necessary w/ continuous variables
#y_scaled = sklearn.preprocessing.scale(y.reshape(-1,1)).ravel() #scale and center the dependent variable (then convert to a flattened array)
y_scaled = y
X = myobs_scaled[:,:omit_ix[0]]
for i in range(len(omit_ix[1:-1])):
  X = numpy.append(X,myobs_scaled[:,omit_ix[i-1]:omit_ix[i]],1) #append any intervening columns... might never happen due to OneHot
X = numpy.append(X,myobs_scaled[:,omit_ix[-1]:],1) #append the rest of myobs_scaled

#sys.stderr.write(str(y_scaled.shape)+'~'+str(X.shape)+'\n')
#use SVR
#svm_classifier = sklearn.svm.SVR(kernel="linear",random_state=RANDOM_SEED) #find linear regression weights

#use LinearSVC #optimized for linear kernels
svm_classifier = svm.LinearSVC(random_state=RANDOM_SEED) #find linear classification coefs

svm_classifier.fit(X,y_scaled)

#with open('tmp.svm_class','wb') as f:
#  pickle.dump(svm_classifier,f)

clean_coefs = {} #convert out of the onehot encoding for categorial features

fixmod = 0
for fix in range(len(feature_names)):
  if fix in omit_ix:
    #need to skip the (now-missing) omitted variable columns
    fixmod -= 1
    continue
  clean_name = feature_names[fix].split('=')[0]
  clean_coefs[clean_name] = clean_coefs.get(clean_name, 0) + svm_classifier.coef_[0][fix+fixmod]**2 #find the length of the categorial coef vector
total = sum(math.sqrt(c) for c in clean_coefs.values())
newtotal = 0
for coef in clean_coefs:
  sys.stdout.write(str(coef)+': '+str(math.sqrt(clean_coefs[coef])/total)+'\n') #output normalized weights
  #sys.stdout.write(str(coef)+': '+str(math.sqrt(clean_coefs[coef]))+'\n') #output raw coefficients

if 'hold-out' in OPTS:
  with open(OPTS['hold-out'],'rb') as f:
    testdata = pickle.load(f)
  newobs_a = myobs.transform(testdata).toarray()
  newobs_scaled = sklearn.preprocessing.scale(newobs_a) #less memory efficient, but centers and scales all features/columns

#  dep_ix = []
#  omit_ix = []
#  feature_names = newobs.get_feature_names()
#  for i,k in enumerate(feature_names):
#    if k[:len(DEP_VAL)] == DEP_VAL:
#      dep_ix.append(i)
#      omit_ix.append(i)
#      continue
#    for v in OMIT_VALS:
#      if k[:len(v)] == v:
#        omit_ix.append(i)

  y_raw = newobs_a[:,dep_ix[0]].reshape(-1,1) #pull out the dependent var columns
  for i in dep_ix[1:]:
    y_raw = numpy.append(y_raw,newobs_a[:,i].reshape(-1,1),1)  #Need to append columns to one another!
  X = newobs_scaled[:,:omit_ix[0]]
  for i in range(len(omit_ix[1:-1])):
    X = numpy.append(X,newobs_scaled[:,omit_ix[i-1]:omit_ix[i]],1) #append any intervening columns... might never happen due to OneHot
  X = numpy.append(X,newobs_scaled[:,omit_ix[-1]:],1) #append the rest of newobs_scaled

#if there is no held-out data, report the accuracy on the training data
y_toscore = numpy.nonzero(y_raw)[1] #grab the dimension that's one-hot for the dependent variable
#sys.stderr.write(str(y_toscore.shape)+'~'+str(X.shape)+'\n')
#sys.stderr.write(str(y_toscore)+'\n\n')

#predict = svm_classifier.predict(X)
#sys.stderr.write(str(predict.shape)+': '+str(predict)+'\n')
score = svm_classifier.score(X,y_toscore)
cases = len(y_toscore)
if 'acc' in OPTS:
  with open(OPTS['acc'],'w') as f:
    f.write('Total: '+str(int(score*cases))+'/'+str(cases)+'='+str(score)+'\n')
else:
  sys.stderr.write('Total: '+str(int(score*cases))+'/'+str(cases)+'='+str(score)+'\n')
