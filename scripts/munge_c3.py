#munge_c3.py textFile dgbFile c3File
# PRE: textFile is the discourse segmented text found in Discourse GraphBank
#      dgbFile contains the DGB annotation for the segments in textFile
#      c3File contains the C3 annotation for the segments in textFile
# collates C3 and DGB annotations
# output format: ENTITY_ID CONTEXT COHERENCE PRO : 3

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
        mention = munge_c3_line(remove_comment(sline).strip())
        if ',' not in mention['head']: #NB: disregard grouped coref for now; not sure how to deal with it (omits 222 mentions ~ 1% of the data)
          entity['mentions'].append(mention)
      elif is_entity(sline):
        #create a new entity
        entity = munge_c3_line(sline)
        entity['mentions'] = []
      else:
        #end of this entity
        #update the annotation with the current entity
        if entity['mentions'] != []: #NB: if all mentions were grouped, disregard entity
          c3annot.append(entity) #[entity['entity_id']] = entity
  return(c3annot)

def munge_dgb(dgbhandle):
  #munges dgb into a dictionary (from its native, line-delimited format)
  indexed_dgb = {} #[segmentid] : (startix,['This','is','the','text.'])
  dgb_sentixes = [0]
  dgb_charix_to_wordix = OrderedDict() #{charix: wordix}
  dgb = []
  ix = 0 #index of discourse segment
  dgb_wordlen = 0 #current length of dgb (words)
  dgb_charlen = 0 #current length of dgb (chars)
  with open(dgbhandle,'r') as dgbFile:
    for line in dgbFile.readlines():
      sline = line.strip()
      if sline == '':
        #if we find an empty line, skip it (end of sentence)
        dgb_sentixes.append(dgb_wordlen)
        continue
      #otherwise, add the new text to dgb, and index it
      addend = sline.split()
      for wix,word in enumerate(addend):
        dgb_charix_to_wordix[dgb_charlen] = dgb_wordlen + wix
        dgb_charlen += len(word)+1 #add the word and the following space to the charlen
      dgb += addend
      indexed_dgb[ix] = (dgb_wordlen, addend)
      dgb_wordlen += len(addend)
      ix += 1
  return(dgb,indexed_dgb,dgb_sentixes,dgb_charix_to_wordix)

def char_to_word(charix,ctwdict):
  #returns the word associated with the given char index
  prevkey = 0
  for c in ctwdict.keys():
    if c > charix: #we just passed the correct word
      return ctwdict[prevkey]
    prevkey = c
  return ctwdict[prevkey] #must be the final word

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
  dgb,indexed_dgb,dgb_sentixes,ctwdict = munge_dgb(dgbhandle) #['This','is','the','text.'] , [segmentid] : (startix,['This','is','the','text.'])
  dgbannot = munge_dgb_annot(dgb_annothandle) # [startstartgrp,endstartgrp][startendgrp,endendgrp] : coherence_relation
  c3annot = munge_c3(c3handle) #[startspan,endspan] : coref_entity_info

#  sys.stderr.write('indexed_dgb: '+str(indexed_dgb)+'\n')
  
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
    dgb_spanlookup.append( (aspanstart,aspanend) )
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
      dgb_spanlookup.append( (bspanstart,bspanend) )
      #enable reverse lookups from endspans to startspans
#      if (bspanstart,bspanend) in dgb_spanlookup.keys():
#        dgb_spanlookup[bspanstart,bspanend].append( (aspanstart,aspanend) )
#      else:
#        dgb_spanlookup[bspanstart,bspanend] = [(aspanstart,aspanend)]

#  sys.stderr.write('c3annot: '+str(c3annot)+'\n')
#  sys.stderr.write('dgbannotspans: '+str(dgbannotspans)+'\n')
  dgb_spanlookup = list(OrderedDict.fromkeys(sorted(dgb_spanlookup))) #sorts all spans and removes duplicates
#  sys.stderr.write('dgb_spanlookup: '+str(dgb_spanlookup)+'\n')
  
  #create output form
  output_corpus = []
  prev_spanix = -1
  for entity in c3annot:
    entity_output = [] #collect all mentions' context, etc here; then iterate over those to find which ones have coherence relations with each other
    for mention in entity['mentions']:
      output_elem = {}

      head_span = char_to_word(int(mention['head'].split('..')[0]),ctwdict) #only care about the first index to the head_span
#      head_span = (int(head_span[0]),int(head_span[1]))
      
      if mention['type'] in ('PRO','WHQ'):
        output_elem['PRO'] = int(True)
      else:
        output_elem['PRO'] = int(False)
      for ix,span in enumerate(dgb_spanlookup):
        if span[0] > head_span: #just passed target
          #sys.stderr.write(str(dgb_spanlookup[ix-1][0])+'/'+str(len(dgb))+' :: ')
          #sys.stderr.write('head_span: '+str(head_span)+' :: span: '+str(dgb_spanlookup[ix-1])+'\n')
          output_elem['CONTEXT'] = dgb[dgb_spanlookup[ix-1][0]] #snag first word of referring segment as context
          output_elem['SPAN'] = dgb_spanlookup[ix-1]
          break
        if ix == len(dgb_spanlookup)-1:
          #must be in the last span
          #sys.stderr.write(str(dgb_spanlookup[ix][0])+'/'+str(len(dgb))+' :: ')
          #sys.stderr.write('head_span: '+str(head_span)+' :: span: '+str(dgb_spanlookup[ix])+'\n')
          output_elem['CONTEXT'] = dgb[dgb_spanlookup[ix][0]] #snag first word of referring segment as context
          output_elem['SPAN'] = dgb_spanlookup[ix]
          break
          
      prevsentix = 0
      for sentix in dgb_sentixes:
        if sentix > head_span:
          output_elem['SENTPOS'] = head_span - prevsentix
          break
        prevsentix = sentix
      entity_output.append(output_elem)
    
    for i,mention_a in enumerate(entity_output):
      for j,mention_b in enumerate(entity_output):
        if i == j: #no self relations, so skip
          continue
        #find all coherence relations between mentions of this entity and list them as a separate instance
        if mention_a['SPAN'] in dgbannotspans.keys() and mention_b['SPAN'] in dgbannotspans[mention_a['SPAN']].keys():
          #there is a coherence relation between mention_a and mention_b, so use mention_b as previous mention (it's a cross-product, so order won't really matter)
          #previous mention's sentence position used as 'entity_id'
          output_corpus.append(dict(list(mention_a.items()) + list({'COHERENCE': dgbannotspans[mention_a['SPAN']][mention_b['SPAN']], \
                                                                      'ENTITY_ID': mention_b['SENTPOS']}.items())))
  return(output_corpus)

def build_corpus(dgbhandle,dgb_annothandle,c3handle):
  #builds corpus from co-occurrence counts
  counts = {}
  corpus = collate_annotations(dgbhandle,dgb_annothandle,c3handle)
  for e in corpus:
    counts[e['ENTITY_ID'],e['CONTEXT'],e['COHERENCE'],e['PRO']] = counts.get((e['ENTITY_ID'],e['CONTEXT'],e['COHERENCE'],e['PRO']), 0) + 1
  for c in counts.keys():
    sys.stdout.write(str(c[0])+' '+str(c[1])+' '+str(c[2])+' '+str(c[3])+' : '+str(counts[c])+'\n')

build_corpus(dgbhandle,dgb_annothandle,c3handle)
