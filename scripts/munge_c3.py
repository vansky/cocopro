#munge_c3.py textFile dgbFile c3File
# PRE: textFile is the discourse segmented text found in Discourse GraphBank
#      dgbFile contains the DGB annotation for the segments in textFile
#      c3File contains the C3 annotation for the segments in textFile
# collates C3 and DGB annotations
# output format: TBD

from collections import OrderedDict
import re
import sys

metadata = re.compile('^<\?')
entity = re.compile('^<entity')
mention = re.compile('^<mention')
comment = re.compile('<!--.*-->')

dgbhandle = sys.argv[1]
dgb_annothandle = sys.argv[2]
c3handle = sys.argv[3]

def is_entity(line):
  #indicates if the line describes an entity or not
  if entity.match(line):
    return(True)
  return(False)

def is_mention(line):
  #indicates if the line describes a mention or not
  if mention.match(line):
    return(True)
  return(False)

def remove_comment(line):
  #removes html-style comments
  return(comment.sub("",line))

def munge_c3_line(line):
  #generates a dict based on a line of c3 xml
  outdict = {}
  sline = line.strip('<>/').split()
  for p in sline[1:]:
    #iterate over key-value pairs and build a dict
    pair = p.split('=')
    if pair[0] == 'id':
      outdict[sline[0]+'_'+pair[0]] = pair[1].strip('"') #differentiate entity_id from mention_id
    else:
      outdict[pair[0]] = pair[1].strip('"')
  return(outdict)

def munge_c3(c3handle):
  #munges c3 annotations into a dictionary (from its native gann xml)
  c3annot = [] #{}
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
        c3annot.append(entity) #[entity['entity_id']] = entity
        #OPT1: Index entity by head span
#        a,b = entity['head'].split('..') #spans only exist for mentions
        #OPT2: Index entity by span
        #a,b = entity['span'].split('..') #spans only exist for mentions
#        c3annot[int(a),int(b)] = entity
  return(c3annot)

def munge_dgb(dgbhandle):
  #munges dgb into a dictionary (from its native, line-delimited format)
  indexed_dgb = {} #[segmentid] : (startix,['This','is','the','text.'])
  dgb_sentixes = [0]
  dgb = []
  ix = 0 #index of discourse segment
  dgblen = 0 #current length of dgb
  with open(dgbhandle,'r') as dgbFile:
    for line in dgbFile.readlines():
      sline = line.strip()
      if sline == '':
        #if we find an empty line, skip it (end of sentence)
        dgb_sentixes.append(dgblen)
        continue
      #otherwise, add the new text to dgb, and index it
      addend = sline.split()
      dgb.append(addend)
      indexed_dgb[ix] = (dgblen, addend)
      dgblen += len(addend)
      ix += 1
  return(dgb,indexed_dgb,dgb_sentixes)

def munge_dgb_annot(dgb_annothandle):
  #munges dgb annotation into a dictionary (from its native, line-delimited format)
  dgbannot = {} # [startstartgrp,endstartgrp][startendgrp,endendgrp] : coherence_relation
  with open(dgb_annothandle,'r') as dgbannotFile:
    for line in dgbannotFile.readlines():
      sline = line.strip().split()
      if (int(sline[0]),int(sline[1])) in dgbannot.keys():
        dgbannot[(int(sline[0]),int(sline[1]))][(int(sline[2]),int(sline[3]))] = sline[4]
      else:
        dgbannot[(int(sline[0]),int(sline[1]))] = {(int(sline[2]),int(sline[3])): sline[4]}
  return(dgbannot)

def collate_annotations(dgbhandle,dgb_annothandle,c3handle):
  #aligns the dgb with the dgb and c3 annotations using word spans to index the annotations
  dgb,indexed_dgb,dgb_sentixes = munge_dgb(dgbhandle) #['This','is','the','text.'] , [segmentid] : (startix,['This','is','the','text.'])
  dgbannot = munge_dgb_annot(dgb_annothandle) # [startstartgrp,endstartgrp][startendgrp,endendgrp] : coherence_relation
  c3annot = munge_c3(c3handle) #[startspan,endspan] : coref_entity_info

  #create a dgbannot dict indexed by spans rather than discourse segment ids
  dgbannotspans = {} # [startstartspan,endstartspan][startendspan,endendspan] : coherence_relation
  dgb_spanlookup = []
  for source in dgbannot.keys():
    #find the span of the source segments
    aspanstart = indexed_dgb[source[0]][0]
    if source[0] == source[1]:
      #if the start group is the only group, then end the span after this group
      aspanend = aspanstart + len(indexed_dgb[source[0]][1])
    else:
      #otherwise, find the end of the group that ends the span
      aspanend = indexed_dgb[source[1]][0] + len(indexed_dgb[source[1]][1])
#    dgb_spanlookup.append( (aspanstart,aspanend) ) #only occurs for cataphora; ignore for now
#    if (aspanstart,aspanend) in dgb_spanlookup.keys():
#      if 'START' not in dgb_spanlookup[aspanstart,aspanend]:
#        dgb_spanlookup[aspanstart,aspanend].append('START')
#    else:
#      dgb_spanlookup[aspanstart,aspanend] = ['START']
    for dest in dgbannot[source].keys():
      bspanstart = indexed_dgb[dest[0]][0]
      if dest[0] == dest[1]:
        #if the start group is the only group, then end the span after this group
        bspanend = bspanstart + len(indexed_dgb[dest[0]][1])
      else:
        #otherwise, find the end of the group that ends the span
        bspanend = indexed_dgb[dest[1]][0] + len(indexed_dgb[dest[1]][1])
      #create a new dict indexed by spans rather than segment ids
      if (aspanstart,aspanend) in dgbannotspans.keys():
        dgbannotspans[aspanstart,aspanend][bspanstart,bspanend] = dgbannot[source][dest]
      else:
        dgbannotspans[aspanstart,aspanend] = {(bspanstart,bspanend) : dgbannot[source][dest]}
      dgb_spanlookup.append( (bspanstart,bspanend,dgbannot[source][dest]) )
      #enable reverse lookups from endspans to startspans
#      if (bspanstart,bspanend) in dgb_spanlookup.keys():
#        dgb_spanlookup[bspanstart,bspanend].append( (aspanstart,aspanend) )
#      else:
#        dgb_spanlookup[bspanstart,bspanend] = [(aspanstart,aspanend)]

  dgb_spanlookup = list(OrderedDict.fromkeys(sorted(dgb_spanlookup))) #sorts all spans and removes duplicates
  
  #create output form
  output_corpus = []
  prev_spanix = -1
  for entity in c3annot:
    for mix,mention in enumerate(entity['mentions']):
      if mix == 0: #first mention, so no non-cataphoric pronominalization possible; skip it
        continue
      output_elem = {}
      
      head_span = mention['head'].split('..')
      head_span = (int(head_span[0]),int(head_span[1]))
      #reftext = dgb[head_span[0]]
      if mention['type'] in ('PRO','WHQ'):
        output_elem['PRO'] = int(True)
      else:
        output_elem['PRO'] = int(False)
      for ix,span in enumerate(dgb_spanlookup):
        if span[0] > head_span[0]: #just passed target
          output_elem['CONTEXT'] = dgb[dgb_spanlookup[ix-1][0]] #snag first word of referring segment as context
          output_elem['COHERENCE'] = dgb_spanlookup[ix-1][2] #record the coherence relation from dgb_annot
          break
      prevsentix = 0
      referent_ix = int(entity['mentions'][mix-1]['head'].split('..')[0]) #previous mention's sentence position used as 'referent_id'
      for sentix in dgb_sentixes:
        if sentix > referent_ix:
          output_elem['ENTITY_ID'] = referent_ix - prevsentix
          break
        prevsentix = sentix
      output_corpus.append(output_elem)

  return(output_corpus)

def build_corpus(dgbhandle,dgb_annothandle,c3handle):
  #builds corpus from co-occurrence counts
  counts = {}
  corpus = collate_annotations(dgbhandle,dgb_annothandle,c3handle)
  for e in corpus:
    counts[e['ENTITY_ID'],e['CONTEXT'],e['COHERENCE'],e['PRO']] = counts.get((e['ENTITY_ID'],e['CONTEXT'],e['COHERENCE'],e['PRO']), 0) + 1
  for c in counts.keys():
    sys.stdout.write(str(c[0])+' '+c[1]+' '+c[2]+' '+c[3]+' : '+counts[c]+'\n')

build_corpus(dgbhandle,dgb_annothandle,c3handle)
