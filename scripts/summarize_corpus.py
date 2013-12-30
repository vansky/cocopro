#python summarize_corpus.py
#reads lines from stdin and gives a summary of the corpus (made primarily to assess training corpus)
import sys

total = 0
for line in sys.stdin:
    total += int(line.strip().split()[-1])

sys.stdout.write('Number of instances: '+str(total)+'\n')
