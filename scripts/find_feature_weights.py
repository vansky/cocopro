#python find_feature_weights.py [REG_TAB_FILE ...]
# outputs regression weights to sys.stdout

import math
import numpy
import pickle
import sklearn
from sklearn.feature_extraction import DictVectorizer
from sklearn import svm
import sys

DEP_VAL = "pro" #dependent variable to regress to when determining weights
OMIT_VALS = ["ref_id"] #features to omit when determining feature weights
RANDOM_SEED = 37 #None yields random initialization

#OPTS = {}
#for aix in range(1,len(sys.argv)):
#  if len(sys.argv[aix]) < 2 or sys.argv[aix][:2] != '--':
#    #filename or malformed arg
#    continue
#  elif aix < len(sys.argv) - 1 and len(sys.argv[aix+1]) > 2 and sys.argv[aix+1][:2] == '--':
#    #missing filename, so simple arg
#    OPTS[sys.argv[aix][2:]] = True
#  else:
#    OPTS[sys.argv[aix][2:]] = sys.argv[aix+1]

indict = []
for infile in sys.argv[1:]:
  with open(infile,'rb') as f:
    indict += pickle.load(f)

#since all categorial values are one hot, each vector associated w/ a feature is FEATURE=X, so ensure the entire feature name should be omitted
DEP_VAL = DEP_VAL + '='
for i,v in enumerate(OMIT_VALS):
  OMIT_VALS[i] = OMIT_VALS[i]+'='

#suck the input dict lists in, encode categorial variables as one-hot, and store as a scipy.sparse matrix of [obs][feature_vec_element]
myobs = DictVectorizer()
#myobs_scaled = sklearn.preprocessing.scale(myobs, with_mean=False) #memory-efficient, scales (but doesn't center) all features/columns
myobs_a = myobs.fit_transform(indict).toarray()
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
y = numpy.nonzero(y_raw)[1].astype("float") #grab the dimension that's one-hot for the dependent variable
y_scaled = sklearn.preprocessing.scale(y.reshape(-1,1)).ravel() #scale and center the dependent variable (then convert to a flattened array
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
