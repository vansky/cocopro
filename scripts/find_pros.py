import sys

options = []
for arg in sys.argv[1:]:
    with open(arg,'r') as f:
        options += f.readline().strip().split()
options = list(set(options))
sys.stderr.write('Types of values for pro:\n'+str(len(options))+': '+str(options)+'\n')
