#python3 build_vectoks.py --vectors VECTOR_FILE --text TEXTFILE
#
# VECTOR_FILE is a file with [word dimension_a dimension_b ...\n]
# TEXTFILE is a raw dgb file
# outputs a version of dgb with a single word/dimension set per line

import sys

OPTS = {}
for aix in range(1,len(sys.argv)):
  if len(sys.argv[aix]) < 2 or sys.argv[aix][:2] != '--':
    #filename or malformed arg
    continue
  elif aix < len(sys.argv) - 1 and len(sys.argv[aix+1]) > 2 and sys.argv[aix+1][:2] == '--':
    #missing filename, so simple arg
    OPTS[sys.argv[aix][2:]] = True
  else:
    OPTS[sys.argv[aix][2:]] = sys.argv[aix+1]

def parse_vectors(inlines):
  output = {}
  for l in inlines:
    sl = l.strip().split()
    if sl == []:
      continue
    output[sl[0]] = [w for w in sl[1:]]
  return(output)

def simplify_terms(instr):
  if len(instr) == 1 and instr in [".","?",",","!","-"]:
    return(instr)
  elif len(instr) == 2 and instr in ["--"]:
    return(instr)
  simple = instr.strip("-!?'\"`,\.;:(){}").lower()
  if '$' == simple[0]:
    return('$')
  elif "%" == simple[-1]:
    return("%")
  elif simple[-2:] in ["'s","'m","'d"]:
    return(simple[:-2])
  elif simple == "can't":
    return("cannot")
  elif len(instr) > 3 and simple[-3:] in ["'ll","'re","n't","'ve"]:
    return(simple[:-3])
  else:
    return(simple)
  
#read in the vectors
with open(OPTS['vectors'], 'r') as f:
  vectors = parse_vectors(f.readlines())

#read in the text
with open(OPTS['text'],'r') as f:
  text = [w for l in f.readlines() for w in l.strip().split()]

numdims = len(vectors[list(vectors.keys())[0]])
for word in text:
  try:
    sys.stdout.write(word+' '+' '.join(vectors[simplify_terms(word)])+'\n')
  except:
    sys.stdout.write(word+' '+' 0.00001'*numdims+'\n')
    sys.stderr.write('Problem! '+word+' not found\n')
