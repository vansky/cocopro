#python find_feature_weights.py [REG_TAB_FILE ...]
# outputs regression weights to sys.stdout

import numpy
import pickle
import sklearn
import sys

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

#suck the input dict lists in, encode categorial variables as one-hot, and store as a scipy.sparse matrix of [obs][feature_vec_element]
myobs = sklearn.feature_extraction.DictVectorizer()
myobs.fit_transform(indict) 

