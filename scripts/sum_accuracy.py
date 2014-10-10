#sum_accuracy.py FILE FILE FILE...
# takes a list of files that each have a single accuracy formula in them and writes the sum to stdout

from __future__ import division
import re
import sys

reacc = re.compile('(\d*)/(\d*)=([01]\.\d*)$')

hits = 0  #total successful hits across all testsets
total = 0 #total potential hits across all testsets
ave = 0.0  #average accuracy on each testset (as opposed to per test item)
avemod = 0 #modifier to make the average ignore testsets with 0 entities
acclist = [] #a list of the accuracies for each test set #for coarse statistical testing

for aix in range(1,len(sys.argv)):
  with open(sys.argv[aix], 'r') as f:
    line = reacc.search(f.readline().strip())
    if not line:
      #we must have found a comment line rather than an accuracy report, so try the next line
      line = reacc.search(f.readline().strip())
    hits += int(line.group(1))
    total += int(line.group(2))
    acc = float(line.group(3))

    if acc != 0.0:
      acclist.append(acc)
      ave += acc
    else:
      avemod += 1
sys.stdout.write('Accuracy: '+str(hits)+'/'+str(total)+'='+str(hits/total)+'\n')
sys.stdout.write('Test set accuracies: '+str(acclist)+'\n')
