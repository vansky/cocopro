import sys

for line in sys.stdin.readlines():
    sline = line.lower().strip().split()
    for word in sline:
        sys.stdout.write(word+'\n')
