#python find_feature_weights.py [REG_TAB_FILE ...]
# outputs regression weights to sys.stdout

import math
import numpy
import pickle
import sklearn
from sklearn.feature_extraction import DictVectorizer
from sklearn import svm
import sys

DEP_VAL = "pro"
OMIT_VALS = ["ref_id"]
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

DEP_VAL = DEP_VAL + '='
for i,v in enumerate(OMIT_VALS):
  OMIT_VALS[i] = OMIT_VALS[i]+'='

#suck the input dict lists in, encode categorial variables as one-hot, and store as a scipy.sparse matrix of [obs][feature_vec_element]
myobs = DictVectorizer()
#myobs.fit_transform(indict)
#myobs_scaled = sklearn.preprocessing.scale(myobs, with_mean=False) #memory-efficient, scales (but doesn't center) all features/columns
myobs_a = myobs.fit_transform(indict).toarray()
myobs_scaled = sklearn.preprocessing.scale(myobs_a) #less memory efficient, but centers and scales all features/columns

#Regress an SVM classifier to distinguish between the classes and output the weights
#sys.stderr.write(str(myobs.get_feature_names())+'\n')
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
  #sys.stderr.write(str(y_raw.shape)+'\n')
y = numpy.nonzero(y_raw)[1].astype("float") #grab the dimension that's one-hot for the dependent variable
#y = [float(i) for i in y]
#sys.stderr.write(str(y_raw[:100,:])+'\n')
#sys.stderr.write(str(y[:100])+'\n')
y_scaled = sklearn.preprocessing.scale(y.reshape(-1,1)).ravel()
X = myobs_scaled[:,:omit_ix[0]]
for i in range(len(omit_ix[1:-1])):
  X = numpy.append(X,myobs_scaled[:,omit_ix[i-1]:omit_ix[i]],1) #append any intervening columns... might never happen due to OneHot
#X = numpy.delete(myobs_scaled,omit_ix,1) #created a matrix of independent vars that doesn't include the dependent var
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
    #need to skip the (now-missing) dependent variable column name
    fixmod -= 1
    continue
    #sys.stdout.write(str(feature_names[fix+1])+': '+str(svm_classifier.coef_[0][fix])+'\n')
  else:
    pass
    #sys.stdout.write(str(feature_names[fix])+': '+str(svm_classifier.coef_[0][fix])+'\n')
  #sys.stderr.write(str(feature_names[fix])+'\n')
  clean_name = feature_names[fix].split('=')[0]
  clean_coefs[clean_name] = clean_coefs.get(clean_name, 0) + svm_classifier.coef_[0][fix+fixmod]**2 #find the length of the categorial coef vector
for coef in clean_coefs:
  sys.stdout.write(str(coef)+': '+str(math.sqrt(clean_coefs[coef]))+'\n')
