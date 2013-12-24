##############################################################################
##                                                                           ##
## This file is part of Coco. Copyright 2013, Coco developers.               ##
##                                                                           ##
##    Coco is free software: you can redistribute it and/or modify           ##
##    it under the terms of the GNU General Public License as published by   ##
##    the Free Software Foundation, either version 3 of the License, or      ##
##    (at your option) any later version.                                    ##
##                                                                           ##
##    Coco is distributed in the hope that it will be useful,                ##
##    but WITHOUT ANY WARRANTY; without even the implied warranty of         ##
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          ##
##    GNU General Public License for more details.                           ##
##                                                                           ##
##    You should have received a copy of the GNU General Public License      ##
##    along with Coco.  If not, see <http://www.gnu.org/licenses/>.          ##
##                                                                           ##
###############################################################################

################################################################################
#
#  i. Macros & variables
#
################################################################################
.SECONDARY:

SHELL = /bin/bash
INCLUDES = 
CFLAGS = $(INCLUDES) -Wall `cat user-cflags.txt` -g #-DNDEBUG -O3 #-DNOWARNINGS #-g #
CC = g++ 
LD = g++
PYTHON = python3
X_MXSTUFF = -Xmx12g

comma = ,
space = $(subst s, ,s)

PROPTXT       = /project/nlp/data/propbank/propbank-1.0/prop.txt
READINGDATA   = /project/nlp/data/readingtimes

SWBDTRAINSECTS = 2 3
DUNDEESECTS = 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20
DUNDEESUBJS = sa sb sc sd se sf sg sh si sj
WSJMAPTRAINSECTS  = 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21  ##EOS
WSJTRAINSECTS  = 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21  ##EOS
WSJTRAINSECTS02  = 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21  ##EOS
WSJHELDOUTSECTS  = 00
BROWNTRAINSECTS = cf cg ck cl cm cn cp cr
BNCTRAINDIRS = A B C D E F G H J
LRSECTS = oerr oer ofr oq rnr se ser

include $(wildcard */*.d)      ## don't comment out, it breaks make!

.SUFFIXES:
.SECONDEXPANSION:


################################################################################
#
#  ii. Demo
#
################################################################################

##################
## RELEASE TARGETS
## Please add targets used in publications here to make creation of a minimal release version easier
tbd: genmodel/quantext-train.gcg13.scopematch
vanschijndeletal12: wsj23.wsj02to21-1671-5sm-bd.x-fabp.-b2000_parsed.nosm.syneval
nguyenetal12: lrtest.wsj02to21-gcg12-1671-3sm.berk.parsed.gapeval
vanschijndelschuler13naacl: dundee.wsj02to21-1671-5sm-bd.x-fabp.-c_-b2000_parsed.-nlLgRw.-A.arg.dundeeeval
#This will be wrapped into Cognition article, but it takes a REALLY long time to run
#vanschijndelschuler13aclshort: dundee.wsj02to21-1671-5sm-bd.x-fabp.-c_-b2000_parsed.-nlLgRw.-dA.arg.dundeeeval
vanschijndeletal13cmcl: dundee.wsj02to21-gcg12-fg-1671-3sm-bd.x-efabp.-c_-b2000_parsed.-nlLgrRwB.canonsubset.-cmcl2013.arg.dundeeeval \
				dundee.wsj02to21-gcg12-fg-1671-3sm-bd.x-efabp.-c_-b2000_parsed.-nlLgrRwB.noncanonsubset.-cmcl2013.arg.dundeeeval \
				dundee.wsj02to21-gcg12-fg-1671-3sm-bd.x-efabp.-c_-b2000_parsed.-nlLgRw.baselinecomparison
##################

################################################################################
#
#  iii. User-specific parameter files (not shared; created by default with default values)
#
#  These parameter files differ from user to user, and should not be checked in.
#  This script just establishes 'official' default values for these parameters.
#
################################################################################

#### c++ compile flags
user-cflags.txt:   ## -g
	echo '-DNDEBUG -O3' > $@
	@echo ''
	@echo 'ATTENTION: I had to create "$@" for you, which may not be to your liking'
	@echo 'edit it to tell C++ whether to compile in debug mode or optimize, and re-run make to continue!'
	@echo ''

#### java compile flags
user-javaflags.txt:
	echo '-Xmx4g' > $@
	@echo ''
	@echo 'ATTENTION: I had to create "$@" for you, which may not be to your liking'
	@echo 'edit it to give java as much memory as you want to, and re-run make to continue!'
	@echo ''

#### location of Discourse GraphBank
user-dgb-location.txt:
	echo '/home/corpora/original/english/discourse_graphbank/' > $@
	@echo ''
	@echo 'ATTENTION: I had to create "$@" for you, which may be wrong'
	@echo 'edit it to point at your discourse graphbank repository, and re-run make to continue!'
	@echo ''

#### location of c-3 corpus
user-c3-location.txt:
	echo '/home/corpora/original/english/c-3-v1.0' > $@
	@echo ''
	@echo 'ATTENTION: I had to create "$@" for you, which may be wrong'
	@echo 'edit it to point at your c3 repository, and re-run make to continue!'
	@echo ''

#### location of bnc
user-bnc-location.txt:
	echo '/home/corpora/original/english/bnc' > $@
	@echo ''
	@echo 'ATTENTION: I had to create "$@" for you, which may be wrong'
	@echo 'edit it to point at your bnc repository, and re-run make to continue!'
	@echo ''

################################################################################
#
#  iv. Code compilation items
#
################################################################################

#### bin directory (ignored by git b/c empty)
bin:
	if [ ! -d $@ ]; then mkdir $@; fi

#### cython executables
%.c: %.py
	cython --embed $< -o $@
bin/%: scripts/%.c
	gcc  -lpython2.5 -I /Library/Frameworks/Python.framework/Versions/2.6/include/python2.6/ $< -o $@
#### java executable objects
.PRECIOUS: %.class
%.class: %.java #$$(addsuffix .class,$$(subst .,/,$$(subst import ,,$$(shell grep -o 'import edu[.a-zA-Z0-9]*' $$(subst .class,.java,$$@)))))
	javac $<

#### R packages
rpkgs:
	mkdir rpkgs
	scripts/installR.r
	echo 'R_LIBS="rpkgs"' > .Renviron

################################################################################
#
#  2. Surface syntax formatting items
#
#  to construct the following file types:
#    <x>.linetrees    : treebank-tagset phase structure trees, one sentence per line, bracketed by parens
#
################################################################################

#### genmodel directory (ignored by git b/c empty)
genmodel:
	if [ ! -d $@ ]; then mkdir $@; fi

define BNCDIRMACRO
.PRECIOUS: genmodel/bnc$(1).sents
genmodel/bnc$(1).sents: $$(shell cat user-bnc-location.txt)/Texts/$(1)/*/*
	cat $$^ | sed 's|<teiHeader.*</teiHeader>||g;s|<[^<>]*>||g;s|^\s*\n||g;/^$$$$/d;s|  *| |g;' > $$@
endef

$(foreach dir,$(BNCTRAINDIRS),$(eval $(call BNCDIRMACRO,$(dir))))

.PRECIOUS: genmodel/bncTRAIN.sents
genmodel/bncTRAIN.sents: $(foreach sect,$(BNCTRAINDIRS),genmodel/bnc$(sect).sents)
	cat $^ > $@

################################################################################
#
#  3. Deep syntax (incl unbounded) dependency items
#
################################################################################

%.scopes: srcmodel/$$*.scopes
	cp $^ $@
%.linetrees:  srcmodel/$$*.linetrees
	cp $^ $@
%.linetrees:  %.editabletrees  scripts/editabletrees2linetrees.pl
	cat $<  |  perl $(word 2,$^)  >  $@
%.gcgsyndeps:  %.linetrees  scripts/gcgtrees2syndeps.py
	cat $<  |  python3 $(word 2,$^)  >  $@
%.gcgsemdeps:  %.gcgsyndeps  scripts/gcgsyndeps2semdeps.pl
	cat $<  |  perl $(word 2,$^)  >  $@
%.gcgscopedeps: %.gcgsemdeps  scripts/gcgsemdeps2scope.py
	cat $<  |  python3 $(word 2,$^)  >  $@
%deps.tex:  %deps  scripts/deps2tex.py
	cat $<  |  python3 $(word 2,$^)  >  $@
%deps.pdf:  %deps.tex
	pdflatex --output-directory $(dir $@) $^
%.scopematch:  scripts/compareScopes.py  genmodel/$$(word 1,$$(subst ., ,$$*)).scopes  %.gcgscopedeps
	python3 $(word 1,$^) $(word 2,$^) $(word 3,$^)  >  $@


## for unbounded dependency corpus
.PRECIOUS: genmodel/lr%.sents
.PRECIOUS: genmodel/lr%.ans
#
#genmodel/lr%.sents: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/lr%.sents scripts/editabletrees2linetrees.pl
#	cat $(word 2,$^)/*.mrg | perl scripts/tbtrees2linetrees.pl > $@
#
genmodel/lr%oerr.sents: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_extract_red_rel/%.raw.obj_extract_red_rel | genmodel
	cat $(word 2,$^) | perl -pe "s/\(/-LRB-/g;s/\)/-RRB-/g;" > $@
genmodel/lr%oerr.ans: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_extract_red_rel/%.obj_extract_red_rel | genmodel
	cp $(word 2,$^) $@
genmodel/lr%oer.sents: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_extract_rel_clause/%.raw.obj_extract_rel_clause | genmodel
	cat $(word 2,$^) | perl -pe "s/\(/-LRB-/g;s/\)/-RRB-/g;" > $@
genmodel/lr%oer.ans: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_extract_rel_clause/%.obj_extract_rel_clause | genmodel
	cp $(word 2,$^) $@
genmodel/lr%ofr.sents: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_free_rels/%.raw.obj_free_rels | genmodel
	cat $(word 2,$^) | perl -pe "s/\(/-LRB-/g;s/\)/-RRB-/g;" > $@
genmodel/lr%ofr.ans: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_free_rels/%.obj_free_rels | genmodel
	cp $(word 2,$^) $@
genmodel/lr%oq.sents: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_qus/%.raw.obj_qus | genmodel
	cat $(word 2,$^) | perl -pe "s/\(/-LRB-/g;s/\)/-RRB-/g;" > $@
genmodel/lr%oq.ans: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_qus/%.obj_qus | genmodel
	cp $(word 2,$^) $@
genmodel/lr%rnr.sents: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/right_node_raising/%.raw.right_node_raising | genmodel
	cat $(word 2,$^) | perl -pe "s/\(/-LRB-/g;s/\)/-RRB-/g;" > $@
genmodel/lr%rnr.ans: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/right_node_raising/%.right_node_raising | genmodel
	cp $(word 2,$^) $@
genmodel/lr%se.sents: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/sbj_embedded/%.raw.sbj_embedded | genmodel
	cat $(word 2,$^) | perl -pe "s/\(/-LRB-/g;s/\)/-RRB-/g;" > $@
genmodel/lr%se.ans: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/sbj_embedded/%.sbj_embedded | genmodel
	cp $(word 2,$^) $@
genmodel/lr%ser.sents: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/sbj_extract_rel_clause/%.raw.sbj_extract_rel_clause | genmodel
	cat $(word 2,$^) | perl -pe "s/\(/-LRB-/g;s/\)/-RRB-/g;" > $@
genmodel/lr%ser.ans: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/sbj_extract_rel_clause/%.sbj_extract_rel_clause | genmodel
	cp $(word 2,$^) $@

lrdev.%:  lrdevoerr.%  lrdevoer.%  lrdevofr.%  lrdevoq.%  lrdevrnr.%  lrdevse.%  lrdevser.%
	more $^  >  $@
lrtest.%gapeval: lrtestoerr.%gapeval lrtestoer.%gapeval lrtestofr.%gapeval lrtestoq.%gapeval lrtestrnr.%gapeval lrtestse.%gapeval lrtestser.%gapeval
	more $^  >  $@
#
# candc parse and try duplicating Rimmel's result on the longrange corpus
#
lrcc.test.%: lrcc.test.oerr.% lrcc.test.oer.% lrcc.test.ofr.% lrcc.test.oq.% lrcc.test.rnr.% lrcc.test.se.% lrcc.test.ser.%
	more $^  >  $@
lrcc.%.oerr.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_extract_red_rel/%.obj_extract_red_rel lrcc.%.oerr.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 > $@
lrcc.%.oerr.r.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_extract_red_rel/%.obj_extract_red_rel lrcc.%.oerr.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 -r1 > $@
lrcc.%.oerr.gapeval.output: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_extract_red_rel/%.raw.obj_extract_red_rel $$(shell cat user-candc-exe-location.txt) $$(shell cat user-candc-models-location.txt)
	cat $(word 2,$^) | $(word 3,$^) --models $(word 4,$^) > $@

lrcc.%.oer.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_extract_rel_clause/%.obj_extract_rel_clause lrcc.%.oer.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 > $@
lrcc.%.oer.r.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_extract_rel_clause/%.obj_extract_rel_clause lrcc.%.oer.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 -r1 > $@
lrcc.%.oer.gapeval.output: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_extract_rel_clause/%.raw.obj_extract_rel_clause $$(shell cat user-candc-exe-location.txt) $$(shell cat user-candc-models-location.txt)
	cat $(word 2,$^) | $(word 3,$^) --models $(word 4,$^) > $@

lrcc.%.ofr.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_free_rels/%.obj_free_rels lrcc.%.ofr.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 > $@
lrcc.%.ofr.r.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_free_rels/%.obj_free_rels lrcc.%.ofr.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 -r1 > $@
lrcc.%.ofr.gapeval.output: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_free_rels/%.raw.obj_free_rels $$(shell cat user-candc-exe-location.txt) $$(shell cat user-candc-models-location.txt)
	cat $(word 2,$^) | $(word 3,$^) --models $(word 4,$^) > $@

lrcc.%.oq.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_qus/%.obj_qus lrcc.%.oq.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 > $@
lrcc.%.oq.r.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_qus/%.obj_qus lrcc.%.oq.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 -r1 > $@
lrcc.%.oq.gapeval.output: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/obj_qus/%.raw.obj_qus $$(shell cat user-candc-exe-location.txt) $$(shell cat user-candc-models-location.txt)
	cat $(word 2,$^) | $(word 3,$^) --models $(word 4,$^) > $@

lrcc.%.rnr.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/right_node_raising/%.right_node_raising lrcc.%.rnr.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 > $@
lrcc.%.rnr.r.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/right_node_raising/%.right_node_raising lrcc.%.rnr.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 -r1 > $@
lrcc.%.rnr.gapeval.output: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/right_node_raising/%.raw.right_node_raising $$(shell cat user-candc-exe-location.txt) $$(shell cat user-candc-models-location.txt)
	cat $(word 2,$^) | $(word 3,$^) --models $(word 4,$^) > $@

lrcc.%.se.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/sbj_embedded/%.sbj_embedded lrcc.%.se.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 > $@
lrcc.%.se.r.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/sbj_embedded/%.sbj_embedded lrcc.%.se.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 -r1 > $@
lrcc.%.se.gapeval.output: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/sbj_embedded/%.raw.sbj_embedded $$(shell cat user-candc-exe-location.txt) $$(shell cat user-candc-models-location.txt)
	cat $(word 2,$^) | $(word 3,$^) --models $(word 4,$^) > $@

lrcc.%.ser.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/sbj_extract_rel_clause/%.sbj_extract_rel_clause lrcc.%.ser.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 > $@
lrcc.%.ser.r.gapeval: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/sbj_extract_rel_clause/%.sbj_extract_rel_clause lrcc.%.ser.gapeval.output scripts/candcRimmelEval.py
	$(PYTHON) $(word 4,$^) -p $(word 3,$^) -g $(word 2,$^) -d1 -r1 > $@
lrcc.%.ser.gapeval.output: user-lrbank-location.txt $$(shell cat user-lrbank-location.txt)/sbj_extract_rel_clause/%.raw.sbj_extract_rel_clause $$(shell cat user-candc-exe-location.txt) $$(shell cat user-candc-models-location.txt)
	cat $(word 2,$^) | $(word 3,$^) --models $(word 4,$^) > $@


################################################################################
#
#  4. Propositional content formatting items
#
#  to construct the following file types:
#    <x>.sentrelns : sentence-indexed relations, one per line, with role-specific propositions delimited by spaces
#    <x>.pbconts   : propbank-tagset sentence contents, one sentence per line, with role-specific propositions delimited by spaces
#    <x>.melconts  : melcuk-tagset sentence contents, one sentence per line, with role-specific propositions delimited by spaces
#
################################################################################

#### obtain relation-aligned sentence-indexed propositions for each sentence, including empty lines for `proposition-free' sentences
genmodel/wsj%.sentrelns:  user-treebank-location.txt  $$(shell cat user-treebank-location.txt)/parsed/mrg/wsj/%  user-propbank-location.txt  $$(shell cat user-propbank-location.txt)/prop.txt 
	grep '^(' $(word 2,$^)/*.mrg  |  sed 's/.*parsed\/mrg\///;s/:.*//'  |  perl -pe 'if($$prev ne $$_){$$prev=$$_;$$ct=0;} s/$$/ $$ct/; $$ct++;'  >  $@
	cat $(word 4,$^)  |  grep '^wsj.$*'  >>  $@
#### obtain relation-aligned sentence-indexed propositions for entire training set, including empty lines for `proposition-free' sentences
genmodel/wsj00to21.sentrelns: $(foreach sect,$(WSJMAPTRAINSECTS),genmodel/wsj$(sect).sentrelns) ##genmodel/wsjEOS$*trees  ##genmodel/eos.linetrees
	cat $^ > $@
genmodel/wsj01to21.sentrelns: $(foreach sect,$(WSJTRAINSECTS),genmodel/wsj$(sect).sentrelns) ##genmodel/wsjEOS$*trees  ##genmodel/eos.linetrees
	cat $^ > $@
genmodel/wsj02to21.sentrelns: $(foreach sect,$(WSJTRAINSECTS02),genmodel/wsj$(sect).sentrelns) ##genmodel/wsjEOS$*trees  ##genmodel/eos.linetrees
	cat $^ > $@
genmodel/wsjTRAIN.sentrelns: $(foreach sect,$(WSJTRAINSECTS),genmodel/wsj$(sect).sentrelns) ##genmodel/wsjEOS$*trees  ##genmodel/eos.linetrees
	cat $^ > $@


#### obtain sentence-aligned space-delimited propbank-domain propositions
.PRECIOUS: %.pbconts
%.pbconts: %.sentrelns  scripts/sentrelns2pbconts.py  %.linetrees
	cat $<  |  perl -pe 'while(s/([^ ]*)\*([^-]*)-([^ \n]*)/\1-\3 \2-\3/g){}; while(s/([^ ]*),([^-]*)-([^ \n]*)/\1-\3 \2-\3/g){}'  |  $(PYTHON) $(word 2,$^) $(word 3,$^)  >  $@
#### use only first N trees
%.pbconts: $$(wordlist 2,$$(words $$(subst -first, ,$$@)),- $$(subst -first, ,$$@)).pbconts
	head -$(word 2,$(subst -first, ,$*)) $< > $@
%first.pbconts: $$(subst $$(space),-,$$(wordlist 2,$$(words $$(subst -, ,$$@)),- $$(subst -, ,$$@))).pbconts
	head -$(lastword $(subst -, ,$*)) $< > $@


#### obtain sentence-aligned space-delimited text-based(number)-domain propositions
.PRECIOUS: %.tbconts
#%.tbconts:  %.linetrees  scripts/trees2melconts.py
#	$(PYTHON) $(word 2,$^) -t $< -p -r >  $@
%berk.parsed.tbconts:  %berk.parsed.linetrees scripts/trees2melconts.py
	cat $< | sed 's/(\(\))/\[\)/g;' | perl -pe 's/(\([^ ]+) +\)/\1 \]/g;' > $@.tmp
	$(PYTHON) $(word 2,$^) -t $@.tmp -p -r -c > $@
	rm -f $@.tmp

%_parsed.tbconts:  %_parsed.output scripts/output2tbconts.py scripts/output2commonconts.py
	$(PYTHON) $(word 2,$^) $<  >  $@
%.ans.tbconts:  %.ans  scripts/convertGoldUnbound.py
	$(PYTHON) $(word 2,$^) -f $< >  $@


#### obtain sentence-aligned space-delimited melcuk(number)-domain propositions
.PRECIOUS: %.melconts
## someone changed to %psg.melconts, but doesn't work for depeval!
#%.ccg.melconts:  %.ccg.linetrees  scripts/ccgtrees2dsyndeps.py
#	$(PYTHON) $(word 2,$^) $<  >  $@
%.melconts:  %.linetrees  scripts/trees2melconts.py scripts/ccgtrees2dsyndeps.py
	if [ "$(word 2,$(subst ., ,$<))" != "ccg" ] && [ "$(word 3,$(subst ., ,$<))" != "ccg" ] && [ "$(word 4,$(subst ., ,$<))" != "ccg" ] && [ "$(word 2,$(subst -, ,$(word 2,$(subst ., ,$<))))" != "ccg" ] ; then $(PYTHON) $(word 2,$^) -t $< -p -r >  $@; else $(PYTHON) $(word 3,$^) $< >  $@; fi
#	if [ "$(word 2,$(subst ., ,$<))" = "ccg" ]; then $(PYTHON) $(word 3,$^) $< >  $@; fi
#	$(PYTHON) $(word 2,$^) -t $< -p -r >  $@
%.ans.melconts:  %.ans  scripts/convertGoldUnbound.py
	$(PYTHON) $(word 2,$^) -f $< >  $@
%nosm.melconts:  %nosm.linetrees  scripts/trees2melconts.py
	$(PYTHON) $(word 2,$^) -t $< -p >  $@
#%parsed.melconts:  %parsed.output scripts/output2melconts.py scripts/output2commonconts.py
#	$(PYTHON) $(word 2,$^) $<  >  $@
%.enju.melconts:  %.enju.output scripts/enju2melconts.py
	$(PYTHON) $(word 2,$^) $<  >  $@

##old pre-psg version needed role labels to be added
#%.melconts:  %-mb-rl.linetrees  scripts/trees2melconts.py
#	$(PYTHON) $(word 2,$^)  -t $< >  $@
%.melrels:  %.melconts
	cat $<  |  grep -n ''  |  perl -pe 's/^([0-9]+):/-----\1-----\n/;s/ (?!$$)/\n/g'  >  $@

################################################################################
#
#  5. Syntax model building items
#
#  to construct the following file types:
#
#    <m>.<x>-<y>.counts : raw counts of model patterns in <m>, using observed <x> and hidden <y> random variables:
#
#                         if <x> = pw   : Pc   (pos given category --- generative)
#                                         Pw   (pos given word --- discriminative)
#                                         P    (prior prob of pos --- used in bayes flip)
#                                         W    (prior prob of word --- used to define oov words)
#
#                                = pwdt : Pc,Pw,P,W (as above)
#                                         PwDT (decis tree for pos given word, if not in Pw)
#
#                                = x    : X    (likelihood of word given terminal category)
#
#                         if <y> = cc   : Cr   (root prior probabilities)
#                                         CC   (joint left and right child given parent)
#
#                                = ccu  : Cr,CC (as above)
#                                         Cu   (unary child given parent --- not used in cnf parsing)
#
#                                = cfp  : Ce   (expansion probability)
#                                         Ctaa (active component of active transition)
#                                         Ctaw (awaited component of active transition)
#                                         Ctww (awaited component of awaited transition)
#                                         F    (final state flag)
#
#    <m>.<x>-<y>.model : probability model, based on counts
#
################################################################################

#### pw-cc counts
.PRECIOUS: %.pw-cc.counts
%.pw-cc.counts: %.linetrees  scripts/trees2rules.pl  scripts/relfreq.pl
	cat $<  |  perl $(word 2,$^) -p  |  perl $(word 3,$^) -f  >  $@
#### x-cc counts
.PRECIOUS: %.x-cc.counts
%.x-cc.counts: %.linetrees  scripts/trees2rules.pl  scripts/relfreq.pl
	cat $<  |  perl $(word 2,$^)  |  perl $(word 3,$^) -f  >  $@

##### pcfg counts, not depth-specific
#.PRECIOUS: %-nobd.pw-cc.counts
#%-nobd.pw-cc.counts: %.linetrees  scripts/trees2rules.pl  scripts/relfreq.pl
#	cat $<  |  perl $(word 2,$^)  |  perl $(word 3,$^) -f  >  $@
####
#.PRECIOUS: %-mdepth.pw-cc.counts
#%-mdepth.pw-cc.counts: %.pw-cc.counts  scripts/pcfg2bdpcfg.py
#	cat $<  |  $(PYTHON) $(word 2,$^)  >  $@
#
####
.PRECIOUS: %.x.model
%.model:  %.counts  scripts/relfreq.pl
	cat $<  |  perl $(word 2,$^)  >  $@


#### decision tree observation model (part of speech model)
.PRECIOUS: %.dt.model
%.dt.model:  %.pw-cc.counts  bin/postrainer  ##scripts/relfreq.pl
	cat $<  |  sed 's/\.0*$$//g'  |  grep '^Pw .* = [1-5]$$'  |  sed 's/^Pw/PwDT/'  |  $(word 2,$^)  >  $@


#### pwdt-cc (pcfg) model
.PRECIOUS: %.pwdt-cc.model
%.pwdt-cc.model:  %.pw-cc.counts  scripts/relfreq.pl  %.dt.model
	cat $<  |  grep -v '^Pw .* = [0]$$'  |  perl $(word 2,$^)  >  $@
	cat $(word 3,$^)  >>  $@


#### pwdt-cfp (hhmm) model
.PRECIOUS: %.pwdt-cfp.model
%.pwdt-cfp.model:  %.pw-cc.counts  scripts/calc-cfp-hhmm.py  scripts/sortbyprob.pl  %.dt.model
	cat $<  |  grep -v '^Pw .* = [0]$$'  |  $(PYTHON) $(word 2,$^)  |  perl $(word 3,$^)  >  $@
	cat $(word 4,$^)  >>  $@

#genmodel/wsjBERKTUNE.extraparen.linetrees: genmodel/wsj21.linetrees
#	cat $< | sed 's/^\((.*\)$$/(\1)/g' > $@

#.PRECIOUS: genmodel/wsjTRAINberk-%sm-fromlinetrees.gr
#genmodel/wsjTRAINberk-%sm-fromlinetrees.gr: edu/berkeley/nlp/PCFGLA/GrammarTrainer.class genmodel/wsjBERKTRAIN.extraparen.linetrees genmodel/wsjBERKTUNE.extraparen.linetrees
#	java $(X_MXSTUFF) edu.berkeley.nlp.PCFGLA.GrammarTrainer -SMcycles $* -path $(word 2,$^) -validation $(word 3,$^) -treebank SINGLEFILE -out $@
#	rm -f $@_*

#.PRECIOUS: genmodel/wsjTRAIN-%sm-fromgaptrees.gr
#genmodel/wsjTRAIN-%sm-fromgaptrees.gr:  edu/berkeley/nlp/PCFGLA/GrammarTrainer.class genmodel/wsjTRAIN.extrapar.gaptrees genmodel/wsj21.extrapar.gaptrees
#	java $(X_MXSTUFF) edu.berkeley.nlp.PCFGLA.GrammarTrainer -SMcycles $* -path $(word 2,$^) -validation $(word 3,$^) -treebank SINGLEFILE -out $@
#	rm -f $@_*
#.PRECIOUS: genmodel/wsjTRAINpsg-%sm-fromgaptrees.gr
#genmodel/wsjTRAINpsg-%sm-fromgaptrees.gr:  edu/berkeley/nlp/PCFGLA/GrammarTrainer.class genmodel/wsjTRAINpsg.extrapar.gaptrees genmodel/wsj21psg.extrapar.gaptrees
#	java $(X_MXSTUFF) edu.berkeley.nlp.PCFGLA.GrammarTrainer -SMcycles $* -path $(word 2,$^) -validation $(word 3,$^) -treebank SINGLEFILE -out $@
#	rm -f $@_*

##### berkeley model -- obtain model database
#.PRECIOUS: genmodel/wsjTRAINberk-%sm.gr
#genmodel/wsjTRAINberk-%sm.gr: berkeley-parser/berkeleyParser.jar user-treebank-location.txt $$(shell cat user-treebank-location.txt)/parsed/mrg/wsj
#	java $(X_MXSTUFF) -cp $< edu.berkeley.nlp.PCFGLA.GrammarTrainer -SMcycles $* -path $(word 3,$^) -out $@
#	rm -f $@_*
#### berkeley model -- obtain grammar and lexicon (text files)
#.PRECIOUS: genmodel/wsjTRAINberk-%sm.grammar genmodel/wsjTRAINberk-%sm.lexicon
#genmodel/wsjTRAINberk-%sm.grammar genmodel/wsjTRAINberk-%sm.lexicon: berkeley-parser/berkeleyParser.jar genmodel/wsjTRAINberk-%sm.gr
#	java -cp $< edu/berkeley/nlp/PCFGLA/WriteGrammarToTextFile $(word 2,$^) $(basename $@)
.PRECIOUS: %.splits %.grammar %.lexicon
%.splits %.grammar %.lexicon:  berkeley-parser/berkeleyParser.jar  %.gr  user-javaflags.txt
	java  $(shell cat $(word 3,$^))  -cp $<  edu/berkeley/nlp/PCFGLA/WriteGrammarToTextFile  $(word 2,$^)  $(basename $@)
.PRECIOUS: %.x-ccu.model
#### berkeley model -- obtain x-cc model (with unaries)
%.x-ccu.model:  %.grammar  %.lexicon  scripts/berkgrammar2ckygr.py  scripts/berklexicon2ckylex.py
	cat $(word 1,$^)  |  python3 $(word 3,$^)  >   $@
	cat $(word 2,$^)  |  python3 $(word 4,$^)  >>  $@


#### NEWSTYLE
.PRECIOUS: %sm.gr
%sm.gr:  edu/berkeley/nlp/PCFGLA/GrammarTrainer.class  $$(basename $$(basename %)).extrpar.linetrees  $$(basename %)last.extrpar.linetrees  user-javaflags.txt
	java  $(shell cat $(word 4,$^))  $(subst /,.,$(basename $<))  -SMcycles $(subst .,,$(suffix $*))  -path $(word 2,$^)  -validation $(word 3,$^)  -treebank SINGLEFILE  -out $@

%sm.gr:  edu/berkeley/nlp/PCFGLA/GrammarTrainer.class  $$(basename $$(basename %)).extrpar.linetrees  $$(basename %)last.extrpar.linetrees  user-javaflags.txt
	java  $(shell cat $(word 4,$^))  $(subst /,.,$(basename $<))  -SMcycles $(subst .,,$(suffix $*))  -path $(word 2,$^)  -validation $(word 3,$^)  -treebank SINGLEFILE  -out $@


#### silly shortcut for berkeley parser
%.berk.model: %.gr
	ln -sf $(notdir $<) $@
%.fullberk.model: %.gr
	ln -sf $(notdir $<) $@

#### obtain strict cc model (no unaries)
.PRECIOUS: %.x-cc.model
%.x-cc.model: %.x-ccu.model  scripts/ccu2cc.py
	cat $<  |  $(PYTHON) $(word 2,$^)  >  $@


##### obtain model-based depth-bounded model (which is also strict cc model (no unaries)
#.PRECIOUS: %-mdepth.x-cc.model
#%-mdepth.x-cc.model: %.x-cc.model  scripts/pcfg2bdpcfg.py
#	cat $<  |  $(PYTHON) $(word 2,$^)  >  $@


###### obtain model-based depth-bounded model that isn't 10x larger than it should be
#.PRECIOUS: %-mdepth.x-ccp.model
#%-mdepth.x-ccp.model: %.x-cc.model  scripts/pcfg2pxmodel.py
#	cat $<  |  $(PYTHON) $(word 2,$^)  >  $@


#### NEWSTYLE
# obtain model-based depth-bounded model that isn't 10x larger than it should be
.PRECIOUS: %.bd.x-ccp.model
%.bd.x-ccp.model:  %.x-cc.model  scripts/pcfg2pxmodel.py
	cat $<  |  $(PYTHON) $(word 2,$^)  >  $@

.PRECIOUS: %.bogusbd.x-ccp.model
%.bogusbd.x-ccp.model:  %.x-cc.model  scripts/pcfg2pxmodel.py
	cat $<  |  sed 's/-eb/-bb/g;s/-ei/-bi/g;s/-ee/-be/g'  |  $(PYTHON) $(word 2,$^)  >  $@

#### x-cfp (hhmm) model
.PRECIOUS: %.x-cfp.model
#%.x-cfp.model:  %.x-ccp.model  bin/calc-cfp-hhmm  scripts/sortbyprob.pl
%.x-cfp.model:  %.x-ccp.model  scripts/calc-cfp-hhmm.py  scripts/sortbyprob.pl
	cat $<  |  egrep    '^(CC|Cr)'  | $(PYTHON) $(word 2,$^)  |  perl $(word 3,$^)  >  $@
	cat $<  |  egrep -v '^(PX|CC|Cr)' >>  $@
	# ^^^ this line just passes the X model straight through
#	cat $<  |  egrep -v '^(CC|Cr)'  |  grep -v '\^R,. '  |  grep -v '\^.,[2-5]'  |  sed 's/\^.,. / /'  >>  $@
	# ^^^ this line takes the X lines and strips off branch and depth bounds.

##### x-rte (hhmm) model
#.PRECIOUS: %.x-rte.model
#%.x-rte.model:  %.x-ccp.model  scripts/calc-rte-model.py  scripts/sortbyprob.pl
#	cat $<  |  grep -v '^PX '  |  python3 $(word 2,$^)  |  perl $(word 3,$^)  >  $@
#.PRECIOUS: %.pw-rte.model
#%.pw-rte.model:  %.pw-cc.counts  scripts/calc-rte-model.py  scripts/sortbyprob.pl
#	cat $<  |  python3 $(word 2,$^)  |  perl $(word 3,$^)  >  $@
.PRECIOUS: %.x-rtue.model
#%.x-rtue.model:  %.x-ccp.model  scripts/calc-rtue-model.py  scripts/sortbyprob.pl
#	cat $<  |  grep -v '^PX '  |  python3 $(word 2,$^)  |  perl $(word 3,$^)  >  $@
%.x-rtue.model:  %.x-ccp.model  bin/calc-rtue-model  scripts/sortbyprob.pl
	cat $<  |  grep -v '^PX '  | sed 's/^Cr : \(.*\^[Ll],1\) =/CC REST^R,0 : \1 REST^R,0 =/;s/ - - / -\^.,. -\^.,. /' \
		|  sed 's/CC \(.*\)\^\(.\),\(.\) : \(.*\)\^.,. \(.*\)\^.,. = \(.*\)/CC \2 \3 \1 : \4 \5 = \6/' |  $(word 2,$^)  |  perl $(word 3,$^)  >  $@
.PRECIOUS: %.x-fawp.model
%.x-fawp.model:  %.x-ccp.model  bin/calc-fawp-model  scripts/sortbyprob.pl
	cat $<  |  grep -v '^PX '  | sed 's/^Cr : \(.*\^[Ll],1\) =/CC REST^R,0 : \1 REST^R,0 =/;s/ - - / -\^.,. -\^.,. /' \
		|  sed 's/CC \(.*\)\^\(.\),\(.\) : \(.*\)\^.,. \(.*\)\^.,. = \(.*\)/CC \2 \3 \1 : \4 \5 = \6/' |  $(word 2,$^)  |  perl $(word 3,$^)  >  $@
.PRECIOUS: %.x-fabp.probmodel
%.x-fabp.probmodel:  %.x-ccp.model  bin/calc-fabp-model
	cat $<  |  grep -v '^PX '  | sed 's/^Cr : \(.*\^[Ll],1\) =/CC REST^R,0 : \1 REST^R,0 =/;s/ - - / -\^.,. -\^.,. /' \
		|  sed 's/CC \(.*\)\^\(.\),\(.\) : \(.*\)\^.,. \(.*\)\^.,. = \(.*\)/CC \2 \3 \1 : \4 \5 = \6/' |  $(word 2,$^)  >  $@
.PRECIOUS: %.x-srfabp.model
# should maybe take out edited at some point here... maybe during/after ccu2cc-save-edited?
%.x-srfabp.model: %.x-ccu.model scripts/ccu2cc-save-edited.py scripts/pcfg2pxmodel.py bin/calc-srfabp-model scripts/sortbyprob.pl
	cat $< | $(PYTHON) $(word 2,$^) | $(PYTHON) $(word 3,$^) | grep -v '^PX ' \
		| sed 's/^Cr : \(.*\^[Ll],1\) =/CC REST^R,0 : \1 REST^R,0 =/;s/ - - / -\^.,. -\^.,. /' \
	|  sed 's/CC \(.*\)\^\(.\),\(.\) : \(.*\)\^.,. \(.*\)\^.,. = \(.*\)/CC \2 \3 \1 : \4 \5 = \6/' \
	|  sed 's/UNF[^ ]*/UNF/g' | $(word 4,$^) | perl $(word 5,$^) > $@
.PRECIOUS: %.x-wp-fabp.model #with weight pushing for speediness
%.x-wp-fabp.model:  %.x-fabp.probmodel  scripts/push-fabp-weights.py  scripts/sortbyprob.pl
	cat $<  |  python3 $(word 2,$^)  |  perl $(word 3,$^)  >  $@
.PRECIOUS: %.x-fabp.model
%.x-fabp.model:  %.x-fabp.probmodel  scripts/sortbyprob.pl
	cat $<  |  perl $(word 2,$^)  >  $@
.PRECIOUS: %.x-efawp.model
%.x-efawp.model:  %.x-fawp.model
	ln -sf $(notdir $<) $@
.PRECIOUS: %.x-wp-efabp.model
%.x-wp-efabp.model:  %.x-wp-fabp.model
	ln -sf $(notdir $<) $@
.PRECIOUS: %.x-efabp.model
%.x-efabp.model:  %.x-fabp.model
	ln -sf $(notdir $<) $@

.PRECIOUS: %.x-ctf-fawp.model
%.x-ctf-fawp.model:  $$(subst .bd,,%).splits scripts/calc-grammar-splits.py %.x-fawp.model scripts/calc-ctf-fawp-model.py scripts/sortbyprob.pl
	cat $(word 3,$^) > $(subst fawp,fawp-prectf,$(word 3,$^))
	cat $(word 1,$^) | $(PYTHON) $(word 2,$^) >> $(subst fawp,fawp-prectf,$(word 3,$^))
	cat $(subst fawp,fawp-prectf,$(word 3,$^)) | $(PYTHON) $(word 4,$^) | perl $(word 5,$^) > $@

.PRECIOUS: %.x-ctf-fabp.model
%.x-ctf-fabp.model:  $$(subst .bd,,%).splits scripts/calc-grammar-splits.py %.x-fabp.model scripts/calc-ctf-fabp-model.py scripts/sortbyprob.pl
	cat $(word 3,$^) > $(subst fabp,fabp-prectf,$(word 3,$^))
	cat $(word 1,$^) | $(PYTHON) $(word 2,$^) >> $(subst fabp,fabp-prectf,$(word 3,$^))
	cat $(subst fabp,fabp-prectf,$(word 3,$^)) | $(PYTHON) $(word 4,$^) | perl $(word 5,$^) > $@

.PRECIOUS: %.x-ctfw-fawp.model
%.x-ctfw-fawp.model:  $$(subst .bd,,%).splits scripts/calc-grammar-splits.py %.x-fawp.model scripts/calc-ctf-fawp-model.py scripts/sortbyprob.pl
	cat $(word 3,$^) > $(subst fawp,fawp-prectf,$(word 3,$^))
	cat $(word 1,$^) | $(PYTHON) $(word 2,$^) >> $(subst fawp,fawp-prectf,$(word 3,$^))
	cat $(subst fawp,fawp-prectf,$(word 3,$^)) | $(PYTHON) $(word 4,$^) | perl $(word 5,$^) > $@

.PRECIOUS: %.x-awp.model
%.x-awp.model:  %.x-ccp.model  bin/calc-rtue-model  scripts/sortbyprob.pl
	cat $<  |  grep -v '^PX '  | sed 's/^Cr : \(.*\^[Ll],1\) =/CC REST^R,0 : \1 REST^R,0 =/;s/ - - / -\^.,. -\^.,. /' \
		|  sed 's/CC \(.*\)\^\(.\),\(.\) : \(.*\)\^.,. \(.*\)\^.,. = \(.*\)/CC \2 \3 \1 : \4 \5 = \6/' |  $(word 2,$^)  |  perl $(word 3,$^)  >  $@

#.PRECIOUS: %-forcedaligned-t2m.x-rtue.model
#%-forcedaligned-t2m.x-rtue.model:  %-forcedaligned.linetrees  %-fromgaptrees.x-cc.model  scripts/linetrees2rtuemodel.py  scripts/relfreq.pl  scripts/sortbyprob.pl
#	cat $<  |  python3 $(word 3,$^)  |  grep -v '^X'  |  perl $(word 4,$^)  |  perl $(word 5,$^)  >  $@
#	cat $(word 2,$^)  |  grep '^X '  |  sed 's/\_\([0-9]\)/-\1/g'  >>  $@

#### NEWSTYLE
%.t2m.x-rtue.model:  %.linetrees scripts/linetrees2rtuemodel.py  scripts/relfreq.pl  scripts/sortbyprob.pl
	cat $<  |  python3 $(word 2,$^)  |  perl $(word 3,$^)  |  perl $(word 4,$^)  >  $@

%.t2m.x-fawp.model:  %.linetrees scripts/linetrees2rtuemodel.py  scripts/relfreq.pl  scripts/sortbyprob.pl
	cat $<  |  python3 $(word 2,$^)  |  perl $(word 3,$^)  |  perl $(word 4,$^)  >  $@

################################################################################
#
#  7. Parsing items
#
#  to construct the following file types:
#    <x>.sents                       : sentences, one per line, consisting of only tokenized words, delimited by spaces
#    <w>.<x>_<y>_<z>_parsed.linetrees : .linetrees file resulting from applying parser-<z>, using parameter <y>, and model <x>.<z>.model, to <w>.sents file
#    <x>.nosm.linetrees              : remove latent variable annotation (berkeley split-merge grammar)
#    <x>.syneval : evaluation report for parsing
#    <x>.depeval : evaluation report for syntactic dependencies
#    <x>.gapeval : evaluation report for long-distance dependencies
#
#  e.g.: make wsj22-10first.wsjTRAINberk-2sm_unked.wsjTRAINberk-2sm-mdepth_-b500,-xa_x-cfp_parsed.syneval
#				 make wsj22-393first.wsjTRAINberk-6sm_,_berk_parsed.syneval
#
################################################################################

#### obtain input sentences from linetrees
.PRECIOUS: %.sents
%.sents: %.linetrees
	cat $<  |  sed 's/(-NONE-[^)]*)//g'  \
		|  sed 's/([^ ]* //g;s/)//g'  |  sed 's/  */ /g;s/^ *//;s/ *$$//;'  \
		| sed 's/!unf! *//g' >  $@

#### NEWSTYLE
#### obtain input sentences
.PRECIOUS: %.sents
%.sents: genmodel/$$(subst -,.,$$*).sents
	cp $< $@
%.noquote.linetrees: %.linetrees
	cat $<  |  grep -v \`  |  grep -v \'  >  $@  #` #(need this extra backtick comment to stop stupid auto-formatting)
#	cat $<  |  perl -pe "s/\`\` *//g;s/ *\'\'//g;s/(?<!\w)\`(?!\w) *//g;s/ *(?<!\w)\'(?!\w)//g;s/^ *//;s/ *$$//"  >  $@
%.fromccg.sents: genmodel/$$(subst -,.,$$*).ccg.linetrees
	cat $<  |  sed 's/([^ ]* //g;s/)//g'  |  sed 's/  */ /g;s/^ *//;s/ *$$//;'  >  $@

.PRECIOUS: %.hysents
%.hysents: %.sents
	cat $< | perl -pe 'while ( s/(\w+)(\-)(\w+)/\1 \2 \3/g ){}; while ( s/([^ \d]+)\\(\/)([^ \d]+)/\1 \2 \3/g ){};' > $@

##### obtain input sentences with modelblocks tag (needed to fix output??)
#%-mb.sents: %-mb.linetrees
#	cat $< | sed 's/([^ ]* //g;s/)//g;s/[^ \/]*\#//g' > $@

## replace rare words with UNKs from Berkeley set
#%_unked.sents: genmodel/$$(basename $$*).sents  genmodel/$$(word 2,$$(subst ., ,$$*)).x-ccu.model scripts/unkreplace.py
#	cat $<  |  $(PYTHON) $(word 3,$^) $(word 2,$^)  >  $@


#### NEWSTYLE
# replace rare words with UNKs from Berkeley set
%.unked.sents:  $$(basename %).sents  genmodel/$$(subst -,.,$$(subst .,,$$(suffix $$*))).x-ccu.model  scripts/unkreplace.py
	cat $<  |  python3  $(word 3,$^)  $(word 2,$^)  >  $@


##### obtain model-specific parser output by running sentences through parser given flags and model:
##### <testset>.<trainset>.<model>.(<params>_)streamed  ---->  genmodel/<testset>.sents  bin/streamparser-<model>  genmodel/<trainset>.<model>.model
.PRECIOUS: %streamed.output
%streamed.output: $$(basename $$(basename $$(basename %))).$$(findstring hy,$$*)sents \
		bin/streamparser-$$(subst .,,$$(suffix $$(basename $$*))) \
		genmodel/$$(subst -,.,$$(subst .,,$$(suffix $$(basename $$(basename $$*))))).$$(subst .,,$$(suffix $$(basename $$*))).model
	@echo "WARNING: long build for '$@'!  Press CTRL-C to abort!"
	@sleep 5
	cat $<  |  $(word 2,$^)  $(subst _, ,$(subst .,,$(suffix $*)))  $(word 3,$^)  >  $@

.PRECIOUS: %streamed.errlog
%streamed.errlog: $$(basename $$(basename $$(basename %))).sents \
		bin/streamparser-$$(subst .,,$$(suffix $$(basename $$*))) \
		genmodel/$$(subst -,.,$$(subst .,,$$(suffix $$(basename $$(basename $$*))))).$$(subst .,,$$(suffix $$(basename $$*))).model
	make $(basename $@).output 2> $@


##### obtain model-specific parser output by running sentences through parser given flags and model:
##### <testset>.<trainset>.<model>.(<params>_)parsed  ---->  genmodel/<testset>.sents  bin/parser-<model>  genmodel/<trainset>.<model>.model
# $$(basename $$(basename $$(basename %))).$$(findstring hy,$$*)sents
.PRECIOUS: %parsed.output
%parsed.output: $$(word 1,$$(subst ., ,%)).$$(findstring hy,$$*)sents \
		bin/parser-$$(subst .,,$$(suffix $$(basename $$*))) \
		genmodel/$$(subst -,.,$$(subst .,,$$(suffix $$(basename $$(basename $$*))))).$$(subst .,,$$(suffix $$(basename $$*))).model
	@echo "WARNING: long build for '$@'!  Press CTRL-C to abort!"
	@sleep 5
	cat $<  |  $(word 2,$^)  $(subst _, ,$(subst .,,$(suffix $*)))  $(word 3,$^)  >  $@

.PRECIOUS: %parsed.errlog
%parsed.errlog: $$(basename $$(basename $$(basename %))).sents \
		bin/parser-$$(subst .,,$$(suffix $$(basename $$*))) \
		genmodel/$$(subst -,.,$$(subst .,,$$(suffix $$(basename $$(basename $$*))))).$$(subst .,,$$(suffix $$(basename $$*))).model
	make $(basename $@).output 2> $@

.PRECIOUS: %enju.output
%enju.output: $$(basename $$(basename %)).sents ../enju-2.4.2/enju
	@echo "WARNING: long build for '$@'!  Press CTRL-C to abort!"
	@sleep 5
	$(word 2,$^) < $<  >  $@

##### obtain linetrees by converting output using script:
#%-cfp_parsed.linetrees:  %-cfp_parsed.output  scripts/cfpout2linetrees.py scripts/unkrestore.py genmodel/$$(basename $$(basename $$*)).sents
#	cat $<  |  $(PYTHON) $(word 2,$^)  |  sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g;s/@//g' | $(PYTHON) $(word 3,$^) $(word 4,$^) >  $@
#%-rte_parsed.linetrees:  %-rte_parsed.output  scripts/rteout2linetrees.py scripts/unkrestore.py genmodel/$$(basename $$(basename $$*)).sents
#	cat $<  |  $(PYTHON) $(word 2,$^)  |  sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g;s/@//g' | $(PYTHON) $(word 3,$^) $(word 4,$^) >  $@
#%-rtue_parsed.linetrees:  %-rtue_parsed.output  scripts/rteout2linetrees.py scripts/unkrestore.py genmodel/$$(basename $$(basename $$*)).sents
#	cat $<  |  $(PYTHON) $(word 2,$^)  |  sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g;s/@//g' | $(PYTHON) $(word 3,$^) $(word 4,$^) >  $@
##%-cky_parsed.linetrees:  %-cky_parsed.output
#%-cc_parsed.linetrees:  %-cc_parsed.output
#	cat $<  |  sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g;s/@//g'  >  $@
##	cat $<  |  sed 's/\^.,.//g'  >  $@


#### NEWSTYLE
#### obtain linetrees by converting output using script:
%parsed.linetrees: %parsed.output scripts/$$(lastword $$(subst -, ,$$(basename $$*)))out2linetrees.py
	cat $<  |  python3 $(word 2,$^)  | sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g'  >  $@

#### POSSIBLE PROBLEM POINT: The below %parsed.linetrees was used until repo move...now above is...?
#%parsed.linetrees: %parsed.output \
#		  scripts/$$(lastword $$(subst -, ,$$(basename $$*)))out2linetrees.py \
#		  scripts/unkrestore.py \
#		  genmodel/$$(basename $$(basename $$(basename $$*))).sents
#	cat $<  |  python3 $(word 2,$^)  |  python3 $(word 3,$^) $(word 4,$^) |  sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g'  >  $@
#^ rteout2linetrees.py | unkrestore.py sents | sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g;s/@//g'
# Consolidation results in moving shared berk/fawp preprocessing to nosm.linetrees
#    This means @ and '-' tags are still in %parsed.linetrees

#%-cfp.parsed.linetrees:  %-cfp.parsed.output  scripts/cfpout2linetrees.py scripts/unkrestore.py genmodel/$$(basename $$(basename $$*)).sents
#	cat $<  |  $(PYTHON) $(word 2,$^)  |  sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g;s/@//g' | $(PYTHON) $(word 3,$^) $(word 4,$^) >  $@
#%-rte.parsed.linetrees:  %-rte.parsed.output  scripts/rteout2linetrees.py scripts/unkrestore.py genmodel/$$(basename $$(basename $$*)).sents
#	cat $<  |  $(PYTHON) $(word 2,$^)  |  sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g;s/@//g' | $(PYTHON) $(word 3,$^) $(word 4,$^) >  $@
#%-rtue.parsed.linetrees:  %-rtue.parsed.output  scripts/rteout2linetrees.py scripts/unkrestore.py genmodel/$$(basename $$(basename $$*)).sents
#	cat $<  |  $(PYTHON) $(word 2,$^)  |  sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g;s/@//g' | $(PYTHON) $(word 3,$^) $(word 4,$^) >  $@
#%-fawp.parsed.linetrees:  %-fawp.parsed.output  scripts/rteout2linetrees.py scripts/unkrestore.py genmodel/$$(basename $$(basename $$*)).sents
#	cat $<  |  $(PYTHON) $(word 2,$^)  |  sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g;s/@//g' | $(PYTHON) $(word 3,$^) $(word 4,$^) >  $@
#%-cky.parsed.linetrees:  %-cky.parsed.output

%-cc.parsed.linetrees:  %-cc.parsed.output
	cat $<  |  sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g;s/@//g'  >  $@
#	cat $<  |  sed 's/\^.,.//g'  >  $@

## sed magic fixes numbers... (CD 20 million) converted to (CD 20) (CD million)
#.PRECIOUS: %_berk_parsed.linetrees
#%_berk_parsed.linetrees:  %_berk_parsed.output
#	cat $<  |  perl -pe 's/\&(?=[^\)]* )/\-/g'  |  sed 's/CD\([^A-Z ]*\) \([0-9]*\) /CD\1 \2) (CD\1 /g'  |  perl -pe 's/^ *\( *//;s/ *\) *$$//;'  \
#		>  $@    ## |  sed 's/-[0-9][0-9]*//g;s/\^g//g'  >  $@    ## |  sed 's/-\([0-9][0-9]*\)/_\1/g'
## EXAMPLE: make wsj22-10first.sm2-berk_unked.sm2-berk_,_x-cc_parsed.syneval wsj22-10first.sm2-berk_berkparsed.syneval 

## NEWSTYLE
# sed magic fixes numbers... (CD 20 million) converted to (CD 20) (CD million)
# also convert things like (NP-lA-9 69 1\/4) to (NP-lA-9 (NP-lI-9 69) (NP-lA-9 1\/4))
#.PRECIOUS: %berk.parsed.linetrees
#%berk.parsed.linetrees:  %berk.parsed.output scripts/killUnaries.pl
#	cat $<  |  perl -pe 's/\&(?=[^\)]* )/\-/g'  |  sed 's/CD\([^A-Z ]*\) \([0-9]*\) /CD\1 \2) (CD\1 /g' |  perl -pe 's/^ *\( *//;s/ *\) *$$//;' |  perl $(word 2,$^) | perl -pe 's/\(([^ \)\(]+)(\-l[A-Z])(\-[0-9]+) ([^ \)\(]+) ([^ \)\(]+)\)/(\1\2\3 (\1-lI\3 \4) (\1-lA\3 \5))/g' >  $@
#.PRECIOUS: %berk.parsed.nounary.linetrees
#%berk.parsed.nounary.linetrees:  %berk.parsed.output  scripts/killUnaries.pl
#	cat $<  |  perl -pe 's/\&(?=[^\)]* )/\-/g'  |  sed 's/CD\([^A-Z ]*\) \([0-9]*\) /CD\1 \2) (CD\1 /g'  |  perl -pe 's/^ *\( *//;s/ *\) *$$//;'  |  perl $(word 2,$^)  >  $@
.PRECIOUS: %berk.parsed.linetrees
%berk.parsed.linetrees:  %berk.parsed.output
	cat $<  |  perl -pe 's/\&(?=[^\)]* )/\-/g'  |  perl -pe 's/^ *\( *//;s/ *\) *$$//;s/-\d+ / /g'  >  $@
#.PRECIOUS: %berk.parsed.ccg.linetrees
#%berk.parsed.ccg.linetrees:  %berk.parsed.output
#	cat $<  |  perl -pe 's/\&(?=[^\)]* )/\-/g'  |  perl -pe 's/^ *\( *//;s/ *\) *$$//;'  >  $@
# EXAMPLE: make wsj22-10first.sm2-berk_unked.sm2-berk_,_x-cc_parsed.syneval wsj22-10first.sm2-berk_berkparsed.syneval 
# perl -pe 's/\&(?=[^\)]* )/\-/g' | sed 's/CD\([^A-Z ]*\) \([0-9]*\) /CD\1 \2) (CD\1 /g' | perl -pe 's/^ *\( *//;s/ *\) *$$//;' | killUnaries.pl

# if we're going to nosm format, that means that we're going to eval this. Also need to 
# alter the REPAIR/EDITED stuff in swbd
#.PRECIOUS: swbd%.nosm.linetrees
#swbd%.nosm.linetrees: %.linetrees scripts/removeAt.py scripts/repairToEdited.rb
#	cat $<  |  perl -pe 's/\(([^ ]+)-[0-9]+ /\(\1 /g;s/\_[0-9]+//g;s/\^g//g;s/[ ]+/ /g;s/\) \)/\)\)/g'  |  python $(word 2,$^) | ruby $(word 3,$^) >  $@
#
# argh, insertion of swbd-only scripts didn't work. I'm going to throw in my REPAIR/EDIT fix to every 
# nosm.linetrees build... this hopefully won't be a huge mess
.PRECIOUS: %.nosm.linetrees
%.nosm.linetrees: %.linetrees scripts/removeAt.py scripts/repairToEdited.rb
#	cat $<  |  perl -pe 's/\(([A-Z]+)-[0-9a-zA-Z\-]+/\(\1/g;s/-[0-9]+//g;s/\_[0-9]+//g;s/\^g//g;s/[ ]+/ /g;s/\) \)/\)\)/g'  |  python $(word 2,$^)  >  $@
	cat $<  |  perl -pe 's/\(([^ ]+)-[0-9]+ /\(\1 /g;s/\_[0-9]+//g;s/\^g//g;s/[ ]+/ /g;s/\) \)/\)\)/g'  |  python $(word 2,$^) | ruby $(word 3,$^) >  $@
#	cat $<  |  perl -pe 's/-[0-9]+//g;s/\_[0-9]+//g;s/\^g//g'  |  python $(word 2,$^)  >  $@

# input is like: wsj23.wsj01to21-psg-nol-1671-5sm.berk.parsed.nosm.linetrees
.PRECIOUS: %.addl.linetrees
%.addl.linetrees: %.linetrees scripts/gen-l-feats.py scripts/annotateL.py 
	$(PYTHON) $(word 2,$^) -t genmodel/wsj01to21.psg.linetrees > genmodel/wsj01to21.psg.linetrees.lfeats
	../maxent-20061005/src/opt/maxent -v -i3000 -g100 genmodel/wsj01to21.psg.linetrees.lfeats --model genmodel/wsj01to21.psg.linetrees.lmodel
	$(PYTHON) $(word 3,$^) -w genmodel/wsj01to21.psg.linetrees.lmodel -n $< > $@ 
#	$(PYTHON) $(word 2,$^) -w genmodel/wsj01to21.psg.linetrees.lmodel -n genmodel/wsj23.psg.nol.linetrees -g genmodel/wsj23.psg.linetrees > genmodel/wsj23.psg.l.linetrees

# eliminates all '-' tags (incl. nosm),cosmetic space reduction
# perl -pe 's/\(([A-Z]+)-[0-9a-zA-Z\-]+/\($1/g;s/\_[0-9]+//g;s/\^g//g;s/[ ]+/ /g;s/\) \)/\)\)/g'

#### turn linetrees into more standard, flatter parse format
#.PRECIOUS: %.evalform
#%.evalform: %.linetrees scripts/unbinarize.pl
#	cat $< | sed 's/[^ \/]*\#//g' | sed 's/[^\(\) ]*://g;s/\.e[0-9]//g' | perl $(word 2,$^) | perl -p -e 's/(\([A-Z\$$\.\,\!\`\'\'']+)[-a-z\$$]+[-a-zA-Z0-9\$$]*/\1/g' > $@
##' # need this to view rest of make correctly following single-quote trickery above

#### obtain eval by running evaluator on gold and hypoth trees
%.nounary.unlabeled.syneval:  user-subproject-includes.txt  bin/evalb  srcmodel/new.prm  genmodel/$$(subst -,.,$$(basename $$(basename $$(basename $$(notdir $$*))))).nounary.unlabeled.linetrees  %.nounary.unlabeled.linetrees
	$(word 2,$^) -p $(word 3,$^) $(word 4,$^) $(word 5,$^) > $@
%.nounary.onlyval.syneval:  user-subproject-includes.txt  bin/evalb  srcmodel/new.prm  genmodel/$$(subst -,.,$$(basename $$(basename $$(basename $$(notdir $$*))))).nounary.onlyval.linetrees  %.nounary.onlyval.linetrees
	$(word 2,$^) -p $(word 3,$^) $(word 4,$^) $(word 5,$^) > $@
%.nounary.syneval:  user-subproject-includes.txt  bin/evalb  srcmodel/new.prm  genmodel/$$(subst -,.,$$(basename $$(basename $$(basename $$(notdir $$*))))).nounary.plusops.linetrees  %.nounary.plusops.linetrees
	$(word 2,$^) -p $(word 3,$^) $(word 4,$^) $(word 5,$^) > $@
%.syneval:  user-subproject-includes.txt  bin/evalb  srcmodel/new.prm  genmodel/$$(subst -,.,$$(basename $$(basename $$(basename $$(notdir $$*))))).plusops.linetrees  %.plusops.linetrees
	$(word 2,$^) -p $(word 3,$^) $(word 4,$^) $(word 5,$^) > $@

%_depeval: user-subproject-includes.txt scripts/depeval.py genmodel/$$(subst -,.,$$(word 1,$$(subst ., ,$$(notdir $$*))))$$(suffix $$*).nounary.melconts $$(basename %).nounary.melconts
	$(PYTHON) $(word 2,$^) $(word 3,$^) $(word 4,$^) > $@

%_syneval:  user-subproject-includes.txt  bin/evalb  srcmodel/new.prm  genmodel/$$(subst -,.,$$(word 1,$$(subst ., ,$$(notdir $$*))))$$(suffix $$*).nounary.linetrees  $$(basename $$@).nounary.linetrees genmodel/$$(subst -,.,$$(word 1,$$(subst ., ,$$(notdir $$*))))$$(suffix $$*).onlyval.nounary.linetrees genmodel/$$(subst -,.,$$(word 1,$$(subst ., ,$$(notdir $$*))))$$(suffix $$*).unlabeled.nounary.linetrees
#	if [ "$(suffix $(basename $@))" == ".onlyval" ]; then $(word 2,$^) -p $(word 3,$^) $(word 6,$^) $(word 5,$^) > $@; else $(word 2,$^) -p $(word 3,$^) $(word 4,$^) $(word 5,$^) > $@; fi
	if [ "$(suffix $(basename $@))" == ".onlyval" ]; then $(word 2,$^) -p $(word 3,$^) $(word 6,$^) $(word 5,$^) > $@; fi 
	if [ "$(suffix $(basename $@))" == ".unlabeled" ]; then $(word 2,$^) -p $(word 3,$^) $(word 7,$^) $(word 5,$^) > $@; else $(word 2,$^) -p $(word 3,$^) $(word 4,$^) $(word 5,$^) > $@; fi

#%.psgsyneval:  user-subproject-includes.txt  bin/evalb  srcmodel/new.prm  genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).psg.nounary.linetrees  %.nounary.linetrees
#	$(word 2,$^) -p $(word 3,$^) $(word 4,$^) $(word 5,$^) > $@


#%_synmatch.corr:  genmodel/$$(word 1,$$(subst ., ,$$(notdir $$*)))$$(suffix $$*).nounary.linetrees  $$(basename %).output  scripts/killUnaries.pl
#	echo 'dat'  >  $@
#	cat $(word 2,$^)  |  sed 's/^$$/NONE/'  |  perl -pe 's/^ *\( *//;s/ *\) *$$//;'  |  perl -pe 's/-[0-9]+ / /g'  |  perl $(word 3,$^)  |  sdiff -d $(word 1,$^) -  |  grep -v '<'  |  perl -pe 's/.*[|>].*/0/;s/.* .*/1/'  >>  $@
#%_synmatch.corr:  genmodel/$$(word 1,$$(subst ., ,$$(notdir $$*)))$$(suffix $$*).nounary.onlyop.linetrees  $$(basename %).nounary.onlyop.linetrees
#	echo 'dat'  >  $@
#	cat $(word 2,$^)  |  sed 's/^$$/NONE/'  |  sdiff -d $(word 1,$^) -  |  grep -v '<'  |  perl -pe 's/.*[|>].*/0/;s/.* .*/1/'  >>  $@
#%_synmatch.unlabeled.corr:  genmodel/$$(word 1,$$(subst ., ,$$(notdir $$*)))$$(suffix $$*).nounary.unlabeled.linetrees  $$(basename %).nounary.unlabeled.linetrees
#	echo 'dat'  >  $@
#	cat $(word 2,$^)  |  sed 's/^$$/NONE/'  |  sdiff -d $(word 1,$^) -  |  grep -v '<'  |  perl -pe 's/.*[|>].*/0/;s/.* .*/1/'  >>  $@
#%_synmatch.unlabeled.corr:  genmodel/$$(word 1,$$(subst ., ,$$(notdir $$*)))$$(suffix $$*).nounary.unlabeled.linetrees  $$(basename %).nounary.unlabeled.linetrees
#	echo 'dat'  >  $@
#	cat $(word 2,$^)  |  sed 's/^$$/NONE/'  |  sdiff -d $(word 1,$^) -  |  grep -v '<'  |  perl -pe 's/.*[|>].*/0/;s/.* .*/1/'  >>  $@
#%_synmatch.onlyval.corr:  genmodel/$$(word 1,$$(subst ., ,$$(notdir $$*)))$$(suffix $$*).nounary.onlyval.linetrees  $$(basename %).nounary.onlyval.linetrees
#	echo 'dat'  >  $@
#	cat $(word 2,$^)  |  sed 's/^$$/NONE/'  |  sdiff -d $(word 1,$^) -  |  grep -v '<'  |  perl -pe 's/.*[|>].*/0/;s/.* .*/1/'  >>  $@
#%_synmatch.onlyval.corr:  genmodel/$$(word 1,$$(subst ., ,$$(notdir $$*)))$$(suffix $$*).nounary.onlyval.linetrees  $$(basename %).nounary.onlyval.linetrees
#	echo 'dat'  >  $@
#	cat $(word 2,$^)  |  sed 's/^$$/NONE/'  |  sdiff -d $(word 1,$^) -  |  grep -v '<'  |  perl -pe 's/.*[|>].*/0/;s/.* .*/1/'  >>  $@
%_depeval.corr:  %_depeval
	echo 'dat'  >  $@
	cat $< | awk -F '\(|/|\)' '{if($$3!=0) print $$2/$$3; else print 0}'  >>  $@
%.syneval.corr:  %.syneval
	echo 'dat'  >  $@
	cat $<  |  egrep '^ *[0-9]+ +[0-9]+'  |  perl -pe 's/ *[0-9]+ +[0-9]+ +[0-9]+ +([^ ]*).*/\1/'  >>  $@
#	cat $<  |  egrep '^ *[0-9]+ +[0-9]+'  |  sed 's/.*0  *100.00  *100.00.*/1/;s/.* .*/0/'  >>  $@
%.synmatch.unlabeled.corr:  genmodel/$$(subst -,.,$$(basename $$(basename $$(basename $$(notdir $$*))))).nounary.unlabeled.linetrees  %.nounary.unlabeled.linetrees
	echo 'dat'  >  $@
	cat $(word 2,$^)  |  sed 's/^$$/NONE/'  |  sdiff -d $(word 1,$^) -  |  grep -v '<'  |  perl -pe 's/.*[|>].*/0/;s/.* .*/1/'  >>  $@
%.synmatch.onlyval.corr:  genmodel/$$(subst -,.,$$(basename $$(basename $$(basename $$(notdir $$*))))).nounary.onlyval.linetrees  %.nounary.onlyval.linetrees
	echo 'dat'  >  $@
	cat $(word 2,$^)  |  sed 's/^$$/NONE/'  |  sdiff -d $(word 1,$^) -  |  grep -v '<'  |  perl -pe 's/.*[|>].*/0/;s/.* .*/1/'  >>  $@
#%.synmatch.corr:  genmodel/$$(word 1,$$(subst ., ,$$(notdir $$*))).nounary.linetrees  $$(basename %).nounary.linetrees
%.synmatch.corr:  genmodel/$$(subst -,.,$$(basename $$(basename $$(basename $$(notdir $$*))))).nounary.linetrees  %.nounary.linetrees
	echo 'dat'  >  $@
	cat $(word 2,$^)  |  sed 's/^$$/NONE/'  |  sdiff -d $(word 1,$^) -  |  grep -v '<'  |  perl -pe 's/.*[|>].*/0/;s/.* .*/1/'  >>  $@
%.depmatch.corr:  genmodel/$$(subst -,.,$$(basename $$(basename $$(basename $$(notdir $$*))))).nounary.melconts  %.nounary.melconts
	echo 'dat'  >  $@
	cat $(word 2,$^)  |  sed 's/^$$/NONE/'  |  sdiff -d $(word 1,$^) -  |  grep -v '<'  |  perl -pe 's/.*[|>].*/0/;s/^[^0].*/1/'  >>  $@
%.gapeval.corr:  %.gapeval
	echo 'dat'  >  $@
	cat $<  |  egrep ': \('  |  perl -pe 's/[0-9] \[/\n\[/' | perl -pe 's/.*\[ \].*/0/;s/.*\[.*/1/;s/.* .*//'  >>  $@
%signif: scripts/mcnemar.r \
         $$(word 1,$$(subst .., ,%)).$$(word 2,$$(subst .., ,$$*)).$$(word 4,$$(subst .., ,$$*))corr \
         $$(word 1,$$(subst .., ,%)).$$(word 3,$$(subst .., ,$$*)).$$(word 4,$$(subst .., ,$$*))corr
	$(word 1,$^) $(word 2,$^) $(word 3,$^)  >  $@
%ttestsignif: scripts/ttest.r \
         $$(word 1,$$(subst .., ,%)).$$(word 2,$$(subst .., ,$$*)).$$(word 4,$$(subst .., ,$$*))corr \
         $$(word 1,$$(subst .., ,%)).$$(word 3,$$(subst .., ,$$*)).$$(word 4,$$(subst .., ,$$*))corr
	$(word 1,$^) $(word 2,$^) $(word 3,$^)  >  $@

%.bootstrapsignif: scripts/compare.pl \
         $$(word 1,$$(subst .., ,%)).$$(word 2,$$(subst .., ,$$*)).$$(word 4,$$(subst .., ,$$*)) \
         $$(word 1,$$(subst .., ,%)).$$(word 3,$$(subst .., ,$$*)).$$(word 4,$$(subst .., ,$$*))
	perl $(word 1,$^) $(word 2,$^) $(word 3,$^)  >  $@

%.fbootstrapsignif: scripts/compare.pl \
         $$(word 1,$$(subst .., ,%)).$$(word 2,$$(subst .., ,$$*)).$$(word 4,$$(subst .., ,$$*)) \
         $$(word 1,$$(subst .., ,%)).$$(word 3,$$(subst .., ,$$*)).$$(word 4,$$(subst .., ,$$*))
	perl -f $(word 1,$^) $(word 2,$^) $(word 3,$^)  >  $@

%.editeval: scripts/markRepair.rb scripts/evalEdit.rb genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).nounary.linetrees  %.linetrees
	cat $(word 3,$^) | ruby $(word 1,$^) > eraseme1
	cat $(word 4,$^) | ruby $(word 1,$^) > eraseme2
	ruby $(word 2,$^) eraseme1 eraseme2 > $@

# wsj22-10first.sm2-berk_unked.sm2-berk_,_x-cc_parsed.syneval

%.failures:  $$(basename $$(basename %)).linetrees  scripts/getfailures.py  genmodel/$$(subst .,,$$(suffix $$(basename $$*))).$$(subst .,,$$(suffix $$*)).model
	cat $<  |  $(PYTHON) $(word 2,$^) $(word 3,$^)  >  $@

#### obtain syntactic dependency eval on enju parser
%.enju.depeval:  scripts/depeval.py  genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).psg.melconts  %.enju.melconts
	$(PYTHON) $< -l $(word 2,$^) $(word 3,$^)  |  grep -n ''  >  $@

#### obtain syntactic dependency eval
#%.depeval:  scripts/depeval.py  genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).ccg.melconts  %.ccg.melconts
#	$(PYTHON) $< $(word 2,$^) $(word 3,$^)  |  grep -n ''  >  $@

#%.depeval:  scripts/depeval.py  genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).melconts  %.melconts
%.depeval:  scripts/depeval.py  genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).$$(word  2,$$(subst -, ,$$(notdir $$(word 2,$$(subst ., ,$$@))))).melconts  %.melconts
	$(PYTHON) $< $(word 2,$^) $(word 3,$^)  |  grep -n ''  >  $@

#### obtain syntactic dependency eval
%.hydepeval:  scripts/depeval.py  genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).psg.hy.melconts  %.melconts
	$(PYTHON) $< $(word 2,$^) $(word 3,$^)  |  grep -n ''  >  $@

#### obtain long-distance dependency eval
%.gapeval:  scripts/lrdepeval.py  genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).ans.tbconts  %.tbconts
	$(PYTHON) $< $(word 2,$^) $(word 3,$^)  |  grep -n ''  >  $@
%.lrview:  scripts/lrviewer.py  %.gapeval %.output %.tbconts
	$(PYTHON) $<  $(word 2,$^) $(word 3,$^) $(word 4,$^)  |  grep -n ''  >  $@


### scores
%.scores: %.syneval
	cat $< | grep -v '^2 or' | grep -v '^    ' | grep '^[ 0-9]' | perl -na -e 'if ($$F[1]<=40) {print "$$F[0] $$F[3]\n";}' > $@


################################################################################
#
#  8. Propositional content extraction (semantic role labeling) items
#
#  to construct the following file types:
#    <x>.lmodel             : a learned mapping from melconts to pbconts
#    <x>.<y>_mapped.pbconts : .pbconts file resulting from applying <y>.lmodel to <x>.melconts file
#    <x>.propeval           : evaluation report for proposition extraction
#
#  e.g.: from gold trees: make genmodel/wsj22.wsjTRAIN_mapped.propeval
#        from live parse: make wsj22-first10.wsjTRAIN_-b500_pwdt-cfp_parsed.wsjTRAIN_mapped.propeval
#
################################################################################

#### THIS IS A TOTAL HACK TO MAKE PROPEVAL RUN WITH PSG --- SHOULD BE REMOVED!!!!
%.psg.pbconts: %.pbconts
	cat $< > $@

##### obtain model of pb label given mel label, words, and cats
#.PRECIOUS: %.lmodel
#%.lmodel:  scripts/calc-l-model.py  %.melconts  %.pbconts
#	$(PYTHON) $< $(word 2,$^) $(word 3,$^)  >  $@

#.PRECIOUS: %.lmodelme
#%.lmodelme:  scripts/calc-l-model-maxent.py  %.melconts  %.pbconts
#	$(PYTHON) $< $(word 2,$^) $(word 3,$^) srcmodel/pbrolesMap >  $@

##### obtain pbconts from melconts
#.PRECIOUS: %_mapped.pbconts
#%_mapped.pbconts: $$(basename %).melconts  scripts/melconts2pbconts.py  genmodel/$$(subst .,,$$(suffix $$*)).lmodel
#	$(PYTHON) $(word 2,$^) $(word 3,$^) $< >  $@


#### obtain proposition eval
%.propeval:  scripts/propeval.py  genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).pbconts  %.pbconts
	$(PYTHON) $< -h $(word 2,$^) $(word 3,$^)  | grep -n ''  >  $@
	tail -n3 $@ 
	@echo "Constituent-based evaluation: exact boundaries match"
	$(PYTHON) $< -c $(word 2,$^) $(word 3,$^)  | grep -n ''  >  $@.consti.exactmatch
	tail -n3 $@.consti.exactmatch 
	@echo "Constituent-based evaluation: hypoth nested in gold"
	$(PYTHON) $< -l $(word 2,$^) $(word 3,$^)  | grep -n ''  >  $@.consti.h.nestedin.g
	tail -n3 $@.consti.h.nestedin.g 
	@echo "Constituent-based evaluation: hypoth covered gold"
	$(PYTHON) $< -g $(word 2,$^) $(word 3,$^)  | grep -n ''  >  $@.consti.h.covered.g
	tail -n3 $@.consti.h.covered.g ; date
	@echo "Same evaluations above but consolidating adjacent propbank args"
	$(PYTHON) $< -s -h $(word 2,$^) $(word 3,$^)  | grep -n ''  >  $@.pbargs.consolidated
	tail -n3 $@.pbargs.consolidated 
	@echo "Constituent-based evaluation: exact boundaries match"
	$(PYTHON) $< -s -c $(word 2,$^) $(word 3,$^)  | grep -n ''  >  $@.consti.exactmatch.pbargs.consolidated
	tail -n3 $@.consti.exactmatch.pbargs.consolidated 
	@echo "Constituent-based evaluation: hypoth nested in gold"
	$(PYTHON) $< -s -l $(word 2,$^) $(word 3,$^)  | grep -n ''  >  $@.consti.h.nestedin.g.pbargs.consolidated
	tail -n3 $@.consti.h.nestedin.g.pbargs.consolidated 
	@echo "Constituent-based evaluation: hypoth covered gold"
	$(PYTHON) $< -s -g $(word 2,$^) $(word 3,$^)  | grep -n ''  >  $@.consti.h.covered.g.pbargs.consolidated
	tail -n3 $@.consti.h.covered.g.pbargs.consolidated ; date

%.conll: scripts/formatConll.py $$(basename $$(basename $$(basename %))).melconts genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).sents %.pbconts
	$(PYTHON) $< -m $(word 2,$^) -s $(word 3,$^) -p $(word 4,$^) > $@
%.conll: scripts/formatConll.py $$(basename $$(basename %)).linetrees genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).sents %.pbconts
	$(PYTHON) $< -c $(word 2,$^) -s $(word 3,$^) -p $(word 4,$^) > $@
#%.conll: scripts/formatConll.py genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).sents %.pbconts
#	$(PYTHON) $< -s $(word 2,$^) -p $(word 3,$^)  > $@


### we can't do this
#genmodel/test.wsj.props: ../conll05st-release/conll05st-tests/test.wsj/props/test.wsj.props.gz
#	gunzip -c $< > $@

%.conlleval: scripts/SRL/srl-eval.pl genmodel/test.wsj.props %.conll 
	perl -Iscripts $< $(word 2,$^) $(word 3,$^) > $@


##### obtain proposition eval with params tacked on end
#%.zpropeval:  scripts/propeval.py  genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).pbconts %.pbconts$(ME_PARAMS)
#	$(PYTHON) $< $(word 2,$^) $(word 3,$^)  | grep -n ''  >  $@$(ME_PARAMS)
#	tail -n3 $@$(ME_PARAMS) ; date

#%.z2spropeval:  scripts/propeval.py  genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).pbconts %.pbconts$(ME_PARAMS)
#	$(PYTHON) $< $(word 2,$^) $(word 3,$^)  | grep -n ''  >  $@$(ME_PARAMS)
#	tail -n3 $@$(ME_PARAMS) ; date

#%.propevalme:  megam_0.92/megam.opt genmodel/$$(notdir $$(word 2,$$(subst ., ,$$@))).lmodelme  genmodel/$$(notdir $$(word 1,$$(subst ., ,$$@))).lmodelme
#	$< -lambda 0 -maxi 1000 multiclass $(word 2,$^) > $(word 2,$^).weight
#	$< -predict $(word 2,$^).weight multiclass $(word 3,$^) &>  $@


#### obtrain decision tree features (ordinary model format)
.PRECIOUS: %.l.cptfeats
%.l.cptfeats:  scripts/calc-l-cptfeats.py  %.melconts  %.pbconts
	$(PYTHON) $< $(word 2,$^) $(word 3,$^)  >  $@

#### obtain binary decision tree model
#### line format: <modelid> <root attrib position in condition> <root attrib 1 value> ... <leaf attrib position in condition> <leaf attrib value> : <modeled value> = <prob>
%.l.bdtmodel:  %.l.cptfeats  scripts/bdtreetrainer.py  scripts/sortbyprob.pl
	cat $<  |  $(PYTHON) $(word 2,$^)  |  perl $(word 3,$^)  >  $@

#### obtain binary-decision-tree mapped propositional content in propbank form
%_bdtmapped.pbconts:  $$(basename %).melconts  scripts/bdtreemapper.py  genmodel/$$(subst .,,$$(suffix $$*)).l.bdtmodel
	$(PYTHON) $(word 2,$^) $(word 3,$^) $<  >  $@

##### e.g. wsjTRAIN_-a3,-i0,-o0,-s0-c1.l.megfeats 
##### obtrain maxent features (include dev (wsj00) and test (wsj22) )
#.PRECIOUS: %.l.megfeats
#%.l.megfeats:  scripts/calc-feats.py  $$(word 1,$$(subst _, ,%)).melconts  $$(word 1,$$(subst _, ,%)).pbconts  srcmodel/pbrolesMap  genmodel/wsj00.melconts  genmodel/wsj00.pbconts scripts/mecommon.py
#	$(PYTHON) $< -m $(word 2,$^) -p $(word 3,$^) -r $(word 4,$^) $(subst $(comma), ,$(word 2,$(subst _, ,$(lastword $(subst ., ,$*))))) -f $*.cutoffFile >  $@
#	@echo "use wsj00 as dev set"
#	echo "DEV" >> $@  #tuning set
#	$(PYTHON) scripts/calc-feats-fordevtest.py -m $(word 5,$^) -p $(word 6,$^) -r $(word 4,$^) $(subst $(comma), ,$(word 2,$(subst _, ,$(lastword $(subst ., ,$*))))) -f $*.cutoffFile  >> $@
##	# i deleted this b/c we don't use it anymore (right?)
##	@echo "use wsj22 as test set. This looks at gold standard to measure the effectiveness of maxent learning alone"
##	echo "TEST" >> $@  #eval set
##	$(PYTHON) scripts/calc-feats-fordevtest.py -m genmodel/wsj22.melconts -p genmodel/wsj22.pbconts -r srcmodel/pbrolesMap -a3 -i0 -o0 -f $*.cutoffFile -s1 >> $@

#### e.g. wsjTRAIN_-a3,-i0,-o0,-k0-c0.l.zmefeats 
#### obtrain maxent features (include dev (wsj00) and test (wsj22) )
#.PRECIOUS: %.l.mefeats
#%.l.mefeats:  scripts/calc-feats.py  $$(word 1,$$(subst _, ,%)).melconts  $$(word 1,$$(subst -, ,$$(subst _, ,%))).pbconts  srcmodel/pbrolesMap scripts/splitTrain-Heldout.sh   scripts/mecommon.py
#	$(word 5,$^) $(word 2,$^) $(word 3,$^)
#	$(PYTHON) $< -g1 -m $(word 2,$^).train -p $(word 3,$^).train -r $(word 4,$^) $(subst $(comma), ,$(word 2,$(subst _, ,$(lastword $(subst ., ,$*)))))  >  $@
#	$(PYTHON) $< -g1 -m $(word 2,$^).heldout -p $(word 3,$^).heldout -r $(word 4,$^) $(subst $(comma), ,$(word 2,$(subst _, ,$(lastword $(subst ., ,$*)))))  > $@.heldout
##	$(PYTHON) scripts/calc-feats-fordevtest.py -m $(word 2,$^).heldout -p $(word 3,$^).heldout -r $(word 4,$^) $(subst $(comma), ,$(word 2,$(subst _, ,$(lastword $(subst ., ,$*)))))  > $@.heldout

#### NEWSTYLE
#.PRECIOUS: %l.mefeats
#%l.mefeats:	scripts/splitTrain-Heldout.sh \
#		$$(basename %).melconts \
#		$$(basename %).pbconts \
#		scripts/calc-feats.py \
#		srcmodel/pbrolesMap \
#		scripts/mecommon.py
#	$(word 1,$^)  $(word 2,$^)  $(word 3,$^)
#	python3  $(word 4,$^)  -g1  -m $(word 2,$^).train    -p $(word 3,$^).train    -r $(word 5,$^)  -a3 -i0 -o0 -k0 $(subst _, ,$(subst .,,$(suffix $*)))  >  $@.train
#	python3  $(word 4,$^)  -g1  -m $(word 2,$^).heldout  -p $(word 3,$^).heldout  -r $(word 5,$^)  -a3 -i0 -o0 -k0 $(subst _, ,$(subst .,,$(suffix $*)))  >  $@.heldout

%.train.melconts %.train.pbconts %.heldout.melconts %.heldout.pbconts:  scripts/splitTrain-Heldout.sh  %.melconts  %.pbconts
	$(word 1,$^)  $(basename $(word 2,$^))  $(basename $(word 3,$^))

.PRECIOUS: %l.mefeats
%l.mefeats:	scripts/calc-feats.py \
		$$(basename %).melconts \
		$$(basename %).pbconts \
		srcmodel/pbrolesMap \
		scripts/mecommon.py
	python3  $(word 1,$^)  -g1  -m $(word 2,$^)  -p $(word 3,$^)  -r $(word 4,$^)  -a3 -i0 -o0 -k0 $(subst _, ,$(subst .,,$(suffix $*)))  >  $@


##### e.g. wsjTRAIN_-a3,-i0,-o0,-k0-c0.l.z2smefeats wsjTRAIN_-a3,-i0,-o0,-k0-c0.l.z2smefeats.heldout wsjTRAIN_-a3,-i0,-o0,-k0-c0.l.z2smefeats.binary wsjTRAIN_-a3,-i0,-o0,-k0-c0.l.z2smefeats.binary.heldout 
##### obtrain maxent features (include dev (wsj00) and test (wsj22) )
#.PRECIOUS: %.l.z2smefeats
#%.l.z2smefeats:  scripts/calc-feats.py  $$(word 1,$$(subst _, ,%)).melconts  $$(word 1,$$(subst _, ,%)).pbconts  srcmodel/pbrolesMap scripts/splitTrain-Heldout.sh
#	$(word 5,$^) $(word 2,$^) $(word 3,$^)
#	$(PYTHON) $< -m $(word 2,$^).train -p $(word 3,$^).train -r $(word 4,$^) $(subst $(comma), ,$(word 2,$(subst _, ,$(lastword $(subst ., ,$*))))) >  $@.z2s
#	$(PYTHON) scripts/calc-feats-fordevtest.py -m $(word 2,$^).heldout -p $(word 3,$^).heldout -r $(word 4,$^) $(subst $(comma), ,$(word 2,$(subst _, ,$(lastword $(subst ., ,$*)))))  > $@.z2s.heldout
#	@echo "generate binary feats"
#	cat $@.z2s | grep "^20 " | sed 's/:[0-9\.]* /:1 /g' > $@.binary
#	cat $@.z2s | grep -v "^20 " | sed 's/^[0-9]* /200 /g' | sed 's/:[0-9\.]* /:2 /g' >> $@.binary
#	@echo "generate binary feats heldout"
#	cat $@.z2s.heldout | grep "^20 " | sed 's/:[0-9\.]* / /g' > $@.binary.heldout
#	cat $@.z2s.heldout | grep -v "^20 " | sed 's/^[0-9]* /200 /g;s/:[0-9\.]* / /g' >> $@.binary.heldout
#	@echo "generate non-NIL only feats"
#	cat $@.z2s | grep -v "^20 " > $@
#	@echo "generate non-NIL only feats heldout"
#	cat $@.z2s.heldout | grep -v "^20 " > $@.heldout

##### obtain maxent model using Hal Daume's megam
##### line format: <modelid> <root attrib position in condition> <root attrib 1 value> ... <leaf attrib position in condition> <leaf attrib value> : <modeled value> = <prob>
#.PRECIOUS: %.l.megmodel
#%.l.megmodel:  %.l.megfeats ./megam_0.92/megam.opt
#	echo "Traing with bias=$(findstring -nobias,$<)"
##	$(word 2,$^) $(findstring -nobias,$<)  -lambda 0 -maxi 10000 -tune -dpp 0.00000000001 multiclass $< > $@ 
#	$(word 2,$^) $(findstring -nobias,$<) -lambda 0.0000001 -maxi 10000 -tune -dpp 0.00000000001 multiclass $< > $@ 
##	$(word 2,$^) -nobias -lambda 0.0000001 -maxi 10000 -tune -dpp 0.00000000001 multiclass $< > $@ 


#### obtain maxent model using Zhang's maxent
#### line format: <modelid> <root attrib position in condition> <root attrib 1 value> ... <leaf attrib position in condition> <leaf attrib value> : <modeled value> = <prob>
.PRECIOUS: %l.memodel
%l.memodel:  ../maxent-20061005/src/opt/maxent  $$(basename %).train$$(suffix $$*)l.mefeats  $$(basename %).heldout$$(suffix $$*)l.mefeats
	$(word 1,$^)  -v -i1000 -g0.5  $(word 2,$^)  --heldout $(word 3,$^)  --model $@ 


#.PRECIOUS: %.l.z2smemodel$(ME_PARAMS)
#%.l.z2smemodel$(ME_PARAMS):  %.l.z2smefeats ../maxent-20061005/src/opt/maxent 
#	echo "Training the binary feats (NIL or non-NIL) for arg identification"
#	$(word 2,$^) -v $(subst $(comma), ,$(ME_PARAMS)) $<.binary --heldout $<.binary.heldout --model $@.binary 
#	echo "Training the non-NIL feats for arg classification"
#	$(word 2,$^) -v $(subst $(comma), ,$(ME_PARAMS)) $< --heldout $<.heldout --model $@ 

##### obtain maxent mapped propositional content in propbank form using Hal Daume's megam
#.PRECIOUS: %_megmapped.pbconts
#%_megmapped.pbconts:  $$(basename %).melconts  scripts/mel2pb.py  genmodel/$$(subst .,,$$(suffix $$*)).l.megmodel scripts/mecommon.py
#	$(PYTHON) $(word 2,$^) -w $(word 3,$^) -r srcmodel/pbrolesMap $(subst $(comma), ,$(word 2,$(subst _, ,$(lastword $(subst ., ,$*))))) -m $< -f genmodel/$(subst .,,$(suffix $*)).cutoffFile >  $@

#### obtain maxent mapped propositional content in propbank form using Zhang's maxent
.PRECIOUS: %mapped.pbconts
%mapped.pbconts: scripts/mel2pb-zhang.py \
		 $$(basename $$(basename %)).melconts \
		 genmodel/$$(subst -,.,$$(subst .,,$$(suffix $$(basename $$*)))).$$(subst .,,$$(suffix $$*))l.memodel \
		 srcmodel/pbrolesMap \
		 $$(basename $$(basename %)).linetrees \
		 scripts/mecommon.py
	python3  $<  -m $(word 2,$^)  -g1 -w  $(word 3,$^)  -r $(word 4,$^) -c $(word 5,$^)  -a3 -i0 -o0 -k0 $(subst _, ,$(subst .,,$(suffix $*)))  >  $@

.PRECIOUS: %mapped.i.pbconts
%mapped.i.pbconts: scripts/mel2pb-zhang.py \
		 $$(basename $$(basename %)).melconts \
		 genmodel/$$(subst -,.,$$(subst .,,$$(suffix $$(basename $$*)))).$$(subst .,,$$(suffix $$*))l.memodel \
		 srcmodel/pbrolesMap \
		 scripts/mecommon.py
	python3  $<  -m $(word 2,$^)  -g1 -w  $(word 3,$^)  -r $(word 4,$^) -a3 -i0 -o0 -k0 $(subst _, ,$(subst .,,$(suffix $*)))  >  $@

#.PRECIOUS: %_z2smemapped.pbconts$(ME_PARAMS)
#%_z2smemapped.pbconts$(ME_PARAMS):  $$(basename %).melconts  scripts/mel2pb-zhang.py  genmodel/$$(subst .,,$$(suffix $$*)).l.z2smemodel$(ME_PARAMS) scripts/mecommon.py
#	$(PYTHON) $(word 2,$^) -w $(word 3,$^) -r srcmodel/pbrolesMap $(subst $(comma), ,$(word 2,$(subst _, ,$(lastword $(subst ., ,$*))))) -m $< >  $@

################################################################################
#
#  9. Eyetracking
#
#  to construct the following file types:
#    <x>.eyemodel           : a model of eyetracking behavior
#    <x>.eyemodels          : a model of eyetracking behavior from a variety of subjects
#    <x>.ngrams             : unigram and bigram models
#    <x>.srilmngrams        : unigram and forward and backward bigram models calculated using SRILM, smoothed with Kneser-Ney
#    <x>.dundeeeval         : A linear mixed effects model fitting the datapoints of <x>.eyemodels (typically from the Dundee Corpus)
#
################################################################################

.PRECIOUS: %.complex
%.complex: %.errlog
	cp $< $@

.PRECIOUS: %.unfiltered.ccomplex
%.unfiltered.ccomplex: scripts/analyzeComplexity.py $$(basename %).complex \
	$$(basename $$(basename $$(basename $$(basename %)))).sents \
	genmodel/broadcoveragetraining.srilmngrams genmodel/wsj02to21.wordcounts
	$(PYTHON) $< $(basename $(subst .,,$(suffix $*))) $(word 2,$^) $(word 3,$^) $(word 4,$^) $(word 5,$^) > $@

%.unfiltered.ccomplex: scripts/analyzeComplexity.py %.complex \
	$$(basename $$(basename $$(basename %))).sents \
	genmodel/broadcoveragetraining.srilmngrams genmodel/wsj02to21.wordcounts
	$(PYTHON) $< $(word 2,$^) $(word 3,$^) $(word 4,$^) $(word 5,$^) > $@

.PRECIOUS: %.ccomplex
%.ccomplex: scripts/filterComplex.py %.unfiltered.ccomplex
	$(PYTHON) $< $(word 2,$^) > $@

.PRECIOUS: dundee.canonsubset
## Requires gcg output from fabp, so: dundee.wsj02to21-gcg-1671-3sm-bd.x-fabp.-c_-b2000_parsed.output
## The sed bit at the beginning removes the null sentence from the output because it messes with the scripts
dundee.canonsubset : dundee.wsj02to21-gcg12-1671-3sm-bd.x-fabp.-c_-b2000_parsed.output scripts/convert_latin-1.py scripts/fabpout2linetrees.py scripts/annotateDepth.py scripts/findCenterEmbeddings.pl
	$(PYTHON) $(word 2,$^) $< | tac | sed -e '/line=1926/{n;N;d}' | tac | \
	$(PYTHON) $(word 3,$^)| sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g' | \
	$(PYTHON) $(word 4,$^) | perl $(word 5,$^) | grep -n '' | grep 'FOUNDCANON' | grep -v 'FOUNDMOD' | \
	sed 's/^\([0-9]\+\):.*$$/\1/' > $@

.PRECIOUS: %dundee.canonsubset
## Requires gcg output from fabp, so: dundee.wsj02to21-gcg-1671-3sm-bd.x-fabp.-c_-b2000_parsed.output
%dundee.canonsubset : %dundee.wsj02to21-gcg12-1671-3sm-bd.x-fabp.-c_-b2000_parsed.output scripts/convert_latin-1.py scripts/fabpout2linetrees.py scripts/annotateDepth.py scripts/findCenterEmbeddings.pl
	$(PYTHON) $(word 2,$^) $< | tac | sed -e '/line=1926/{n;N;d}' | tac | \
	$(PYTHON) $(word 3,$^)| sed 's/\^.,.//g;s/\^g//g;s/\_[0-9]*//g' | \
	$(PYTHON) $(word 4,$^) | perl $(word 5,$^) | grep -n '' | grep 'FOUNDCANON' | grep -v 'FOUNDMOD' | \
	sed 's/^\([0-9]\+\):.*$$/\1/' > $@

.PRECIOUS: %.baselinecomparison
%.baselinecomparison: $$(dirname %)dundee.wsj02to21-gcg12-1671-3sm-bd.x-efabp.-c_-b2000_parsed.$$(subst .,,$$(suffix $$*)).eyemodels $$(dirname %)dundee.wsj02to21-gcg12-fg-1671-3sm-bd.x-efabp.-c_-b2000_parsed.$$(subst .,,$$(suffix $$*)).eyemodels scripts/dundeeLME.compare.r
	$(word 3,$^) $< $(word 2,$^) > $@

genmodel/broadcoveragetraining.sents: genmodel/brownTRAIN.sents genmodel/wsj02to21.sents genmodel/bncTRAIN.sents genmodel/dundee.sents extraScripts/ptb_tokenizer.sed
	cat $(word 3,$^) | sed "s/&bquo;/\'/g;s/&equo;/\'/g;s/&hellip;/.../g;s/&percnt;/%/g;s/&ndash;/-/g;s/&amp;/\&/g;s/&mdash;/--/g;" | \
	./$(word 5,$^) > genmodel/tmp.bnc
	./$(word 5,$^) $(word 4,$^) > genmodel/tmp.dundee
	cat $(word 1,$^) $(word 2,$^) genmodel/tmp.bnc genmodel/tmp.dundee | grep -v '\*x\*' | sed 's/  */ /g;' > $@
	rm -f genmodel/tmp.bnc genmodel/tmp.dundee

genmodel/broadcoveragetraining.revsents: genmodel/broadcoveragetraining.sents
	cat $^ | sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/ <LINEBREAK> /g' > $@.tmp #the idiocy of BSD sed (e.g. on OSX) requires the dumb formulation of this sed command
	tac -s ' ' $@.tmp | sed 's/ <LINEBREAK> /\n/g;s/  */ /g;' > $@
	rm -f $@.tmp

.PRECIOUS: %.ngrams
%.ngrams: %.sents scripts/calc-unigrams.py scripts/calc-bigrams.py
	#cat $< | sed 's/\([^A-Za-z0-9]\)/ \1 /g;s/  */ /g;' > $@.tmp 
	$(PYTHON) $(word 2,$^) -kn $< > $@.uni
	$(PYTHON) $(word 3,$^) -kn $< $@.uni > $@.bi
	cat $@.uni $@.bi > $@
	#rm -f $@.tmp $@.uni $@.bi
	rm -f $@.uni $@.bi

.PRECIOUS: %.srilmngrams
%.srilmngrams: %.sents %.revsents scripts/convert_srilm.py user-srilm-location.txt
	#cat $< | sed 's/\([^A-Za-z0-9]\)/ \1 /g;s/  */ /g;' > $@.fwtmp
	#cat $(word 2, $^) | sed 's/\([^A-Za-z0-9]\)/ \1 /g;s/  */ /g;' > $@.bwtmp
	$(SRILM)/$(SRILMSUB)/ngram-count -order 1 -kndiscount -text $< -lm $@.uprobs
	$(SRILM)/$(SRILMSUB)/ngram-count -order 2 -kndiscount -interpolate -text $< -lm $@.fwprobs
	$(SRILM)/$(SRILMSUB)/ngram-count -order 2 -kndiscount -interpolate -text $(word 2, $^) -lm $@.bwprobs
	$(PYTHON) $(word 3,$^) $@.uprobs -U > $@
	$(PYTHON) $(word 3,$^) $@.fwprobs -BF >> $@
	$(PYTHON) $(word 3,$^) $@.bwprobs -BB >> $@
	rm -f $@.{uprobs,fwtmp,fwprobs,bwtmp,bwprobs}

.PRECIOUS: %.eyemodel
%.eyemodel: scripts/analyzeComplexity.py $$(basename %).complex \
	genmodel/$$(notdir $$(basename $$(basename $$(basename $$(basename $$*))))).$$(subst .,,$$(suffix $$(subst _,.,$$*))).textdata \
	genmodel/$$(notdir $$(basename $$(basename $$(basename $$(basename $$*))))).$$(subst .,,$$(suffix $$(subst _,.,$$*))).eyedata \
	genmodel/$$(notdir $$(basename $$(basename $$(basename $$(basename $$*))))).$$(subst .,,$$(suffix $$(subst _,.,$$*))).eventdata \
	genmodel/broadcoveragetraining.srilmngrams genmodel/wsj02to21.wordcounts
	$(PYTHON) $< $(basename $(subst _,.,$(subst .,,$(suffix $*)))) $(word 2,$^) $(word 3,$^) $(word 4,$^) $(word 5,$^) $(word 6,$^) $(word 7,$^) > $@

.PRECIOUS: %.unfiltered.eyemodels
%.unfiltered.eyemodels: $(foreach subj,$(DUNDEESUBJS),%_$(subj).eyemodel)
	head -1 $< > $@
	cat $^ | grep -v '^subject word' >> $@

#.PRECIOUS: %.eyemodels
#%.eyemodels: scripts/filterComplex.py %.unfiltered.eyemodels
#	$(PYTHON) $< $(word 2,$^) > $@

.PRECIOUS: %.canonsubset.eyemodels
%.canonsubset.eyemodels: $$(dirname %)dundee.canonsubset %.unfiltered.eyemodels scripts/filterComplexSubset.py
	$(PYTHON) $(word 3,$^) $< $(word 2,$^) > $@

.PRECIOUS: %.noncanonsubset.eyemodels
%.noncanonsubset.eyemodels: $$(dirname %)dundee.canonsubset %.unfiltered.eyemodels scripts/filterComplexSubset.py
	$(PYTHON) $(word 3,$^) -v $< $(word 2,$^) > $@

.PRECIOUS: %.dundeeeval
%.arg.dundeeeval: $$(basename %).eyemodels scripts/dundeeLME.r rpkgs
	$(word 2,$^) $< $(subst _,$(space),$(subst .,,$(suffix $*))) > $@

%.dundeeeval: %.eyemodels scripts/dundeeLME.r rpkgs
	$(word 2,$^) $< - > $@

################################################################################
#
#  Misc utilities
#
################################################################################

grep.%:
	grep $(subst '.',' ',$*) src/*.cpp include/*.h ../rvtl/include/*.h -n

%.memprof: run-%
	valgrind --tool=massif --time-unit=i --max-snapshots=500 --massif-out-file=$@ -v $<
#	ms_print $@ | less

%.procprof: 
	cat user-cflags.txt > user-cflags.tmp.txt
	echo '-DNDEBUG -O3 -pg' > user-cflags.txt
	make $* -B
	gprof $* > $@
	cat user-cflags.tmp.txt > user-cflags.txt

dist-clean:
	@echo 'Do you really want to destroy all models in genmodel?  If not, CTRL-C and copy it from somewhere!'
	@sleep 5
	-rm bin/* genmodel/* */*.o ./*~ ./*~ */*.a */*.cmx */*.d ./semantic.cache pkgmodel/*
clean:
	@echo 'Do you really want to destroy all models in genmodel?  If not, CTRL-C and copy it from somewhere!'
	@sleep 5
	-rm bin/* genmodel/* */*.o ./*~ ./*~ */*.a */*.cmx */*.d ./semantic.cache
tidy:
	-rm bin/*            */*.o ./*~ ./*~ */*.a */*.cmx */*.d ./semantic.cache

#depend:
#	makedepend -Iinclude -I../rvtl/include -I../slush/include src/*.cpp -Y
# #	g++ -MM -Iinclude -I../rvtl/include -I../slush/include src/*.cpp ### but then do what with this?

