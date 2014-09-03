#sum_probs.py FILE FILE FILE...
# takes a list of files that each have a single logprob in them and writes the sum to stdout

import sys

total = 0
for aix in range(1,len(sys.argv)):
  with open(sys.argv[aix], 'r') as f:
    total += float(f.readline().strip())
sys.stdout.write(str(total)+'\n')
