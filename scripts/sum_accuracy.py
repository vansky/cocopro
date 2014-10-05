#sum_accuracy.py FILE FILE FILE...
# takes a list of files that each have a single accuracy formula in them and writes the sum to stdout

from __future__ import division
import re
import sys

reacc = re.compile('(\d*)/(\d*)=([01]\.\d*)$')

hits = 0  #total successful hits across all testsets
total = 0 #total potential hits across all testsets
weakest = ('-1',1.0) #testset with worst accuracy
best = ('-1',0.0) #testset with best accuracy
ave = 0.0  #average accuracy on each testset (as opposed to per test item)
avemod = 0 #modifier to make the average ignore testsets with 0 entities

for aix in range(1,len(sys.argv)):
  with open(sys.argv[aix], 'r') as f:
    line = reacc.search(f.readline().strip())
    hits += int(line.group(1))
    total += int(line.group(2))
    acc = float(line.group(3))

    if acc != 0.0:
      ave += acc
      if acc > best[1]:
        best = (sys.argv[aix],acc)
      if acc < weakest[1]:
        weakest = (sys.argv[aix],acc)
    else:
      avemod += 1
sys.stdout.write('Accuracy: '+str(hits)+'/'+str(total)+'='+str(hits/total)+'\n')
sys.stdout.write('Ave subset accuracy: '+str(ave / (len(sys.argv)-avemod))+'\n')
sys.stdout.write('Best subset: '+str(best[0])+' ['+str(best[1])+']\n')
sys.stdout.write('Worst subset: '+str(weakest[0])+' ['+str(weakest[1])+']\n')
