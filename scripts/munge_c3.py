#munge_c3.py textFile dgbFile c3File
# PRE: textFile is the discourse segmented text found in Discourse GraphBank
#      dgbFile contains the DGB annotation for the segments in textFile
#      c3File contains the C3 annotation for the segments in textFile
# collates C3 and DGB annotations
# output format: TBD

import re

metadata = re.compile('^<\?')
entity = re.compile('^<entity')
mention = re.compile('^<mention')
comment = re.compile('<!--.*-->')

def is_entity(line):
  #indicates if the line describes an entity or not
  if entity.match(line):
    return True
  return False

def is_mention(line):
  #indicates if the line describes a mention or not
  if mention.match(line):
    return True
  return False

def remove_comment(line):
  #removes html-style comments
  return comment.sub("",line)

def munge_c3_line(line):
  #generates a dict based on a line of c3 xml
  outdict = {}
  sline = line.strip('<>/').split()
  for p in sline[1:]:
    #iterate over key-value pairs and build a dict
    pair = p.split('=')
    outdict[pair[0]] = pair[1].strip('"')
  return outdict

def munge_c3(c3handle):
  #munges c3 annotations into a dictionary (from its native gann xml)
  c3annot = {}
  entity = {}
  with open(c3handle,'r') as c3File:
    for line in c3File.readlines():
      sline = line.strip()
      if metadata.match(sline):
        #ignore lines with metadata
        continue
      elif '<gann>' == sline:
        #ignore the header line
        continue
      elif '</gann>' == sline:
        #ignore the footer line
        continue
      elif is_mention(sline):
        #create a new mention; add mention to the current entity
        entity['mentions'].append(munge_c3_line(remove_comment(sline).strip()))
      elif is_entity(sline):
        #create a new entity
        entity = munge_c3_line(sline)
        entity['mentions'] = []
      else:
        #end of this entity
        #update the annotation with the current entity
        c3annot[entity['id']] = entity  #NB: Do we really want this to be indexed by entity id? What about by span?
