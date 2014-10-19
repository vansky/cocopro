#sum_accuracy.py FILE FILE FILE...
# takes a list of files that each have a single accuracy formula in them and writes the sum to stdout

from __future__ import division
import re
import sys

reacc = re.compile('^([A-Za-z]*): (\d*)/(\d*)$')

results = {}

for aix in range(1,len(sys.argv)):
  with open(sys.argv[aix], 'r') as f:
    for rawline in f.readlines():
      line = reacc.match(rawline.strip())
      if not line:
        #we must have found a comment line rather than an accuracy report, so try the next line
        continue
      label = line.group(1)
      if label not in results:
        results[label] = [0,0]
      results[label][0] += int(line.group(2))
      results[label][1] += int(line.group(3))

sys.stdout.write('Total Accuracy: '+str(results['Total'][0])+'/'+str(results['Total'][1])+'='+str(results['Total'][0]/results['Total'][1])+'\n')
for l in results:
  if l == "Total":
    #we output the total accuracy first
    continue
  if results[l][1] == 0:
    sys.stdout.write(l+' Accuracy: '+str(results[l][0])+'/'+str(results[l][1])+'='+str(0.0)+'\n')
  else:
    sys.stdout.write(l+' Accuracy: '+str(results[l][0])+'/'+str(results[l][1])+'='+str(results[l][0]/results[l][1])+'\n')
