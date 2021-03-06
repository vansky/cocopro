###############################################################################
##                                                                           ##
## This file is part of Cocopro. Copyright 2013, Cocopro developers.         ##
##                                                                           ##
##    Cocopro is free software: you can redistribute it and/or modify        ##
##    it under the terms of the GNU General Public License as published by   ##
##    the Free Software Foundation, either version 3 of the License, or      ##
##    (at your option) any later version.                                    ##
##                                                                           ##
##    Cocopro is distributed in the hope that it will be useful,             ##
##    but WITHOUT ANY WARRANTY; without even the implied warranty of         ##
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          ##
##    GNU General Public License for more details.                           ##
##                                                                           ##
##    You should have received a copy of the GNU General Public License      ##
##    along with Cocopro.  If not, see <http://www.gnu.org/licenses/>.       ##
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
DGBSECTS = $(shell seq 135)
DGBDEVSECTS = $(shell seq 100 115) #391 dev cases
DGBDEV2SECTS = $(shell seq 100 120) #525 training cases for rapid dev testing
DGBTESTSECTS= $(shell seq 100) $(shell seq 116 135) #2270 test cases

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

parse1: $(foreach sect,$(shell seq 1 15),genmodel/cocopro.dgb_data-20.1_$(sect).cats)
parse2: $(foreach sect,$(shell seq 16 30),genmodel/cocopro.dgb_data-20.1_$(sect).cats)
parse3: $(foreach sect,$(shell seq 31 45),genmodel/cocopro.dgb_data-20.1_$(sect).cats)
parse4: $(foreach sect,$(shell seq 46 60),genmodel/cocopro.dgb_data-20.1_$(sect).cats)
parse5: $(foreach sect,$(shell seq 61 75),genmodel/cocopro.dgb_data-20.1_$(sect).cats)
parse6: $(foreach sect,$(shell seq 76 90),genmodel/cocopro.dgb_data-20.1_$(sect).cats)
parse7: $(foreach sect,$(shell seq 91 105),genmodel/cocopro.dgb_data-20.1_$(sect).cats)
parse8: $(foreach sect,$(shell seq 106 120),genmodel/cocopro.dgb_data-20.1_$(sect).cats)
parse9: $(foreach sect,$(shell seq 121 135),genmodel/cocopro.dgb_data-20.1_$(sect).cats)

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
	echo '/home/corpora/original/english/discourse_graphbank' > $@
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

#### location of mallet
user-mallet-location.txt:
	echo '/home/compling/mallet-2.0.7' > $@
	@echo ''
	@echo 'ATTENTION: I had to create "$@" for you, which may be wrong'
	@echo 'edit it to point at your mallet repository, and re-run make to continue!'
	@echo ''

#### location of bnc
user-bnc-location.txt:
	echo '/home/corpora/original/english/bnc' > $@
	@echo ''
	@echo 'ATTENTION: I had to create "$@" for you, which may be wrong'
	@echo 'edit it to point at your bnc repository, and re-run make to continue!'
	@echo ''

#### location of glove
user-glove-location.txt:
	echo '/home/corpora/original/english/' > $@
	@echo ''
	@echo 'ATTENTION: I had to create "$@" for you, which may be wrong'
	@echo 'edit it to point at your bnc repository, and re-run make to continue!'
	@echo ''

#### location of tokenizer
user-tokenizer-location.txt:
	echo '/home/compling/extended_penn_tokenizer' > $@
	@echo ''
	@echo 'ATTENTION: I had to create "$@" for you, which may be wrong'
	@echo 'edit it to point at your tokenizer directory, and re-run make to continue!'
	@echo ''

#### location of sentence tokenizer
user-sentokenizer-location.txt:
	echo '/home/compling/simple_sentence_tokenizer' > $@
	@echo ''
	@echo 'ATTENTION: I had to create "$@" for you, which may be wrong'
	@echo 'edit it to point at your tokenizer directory, and re-run make to continue!'
	@echo ''

#### location of sentence tokenizer
user-modelblocks-location.txt:
	echo '../modelblocks-repository/dundee' > $@
	@echo ''
	@echo 'ATTENTION: I had to create "$@" for you, which may be wrong'
	@echo 'edit it to point at your modelblocks/dundee directory, and re-run make to continue!'
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
#  3. Cocopro items
#
################################################################################

#.PRECIOUS: genmodel/cocopro.%.counts
#genmodel/cocopro.%.counts: scripts/munge_c3.py $(shell cat user-dgb-location.txt)/data/annotator$$(word 1,$$(subst _, ,$$*))/$$(word 2,$$(subst _, ,$$*)) \
#				$(shell cat user-dgb-location.txt)/data/annotator$$(word 1,$$(subst _, ,$$*))/$$(word 2,$$(subst _, ,$$*))-annotation \
#				$(shell cat user-c3-location.txt)/$$(word 2,$$(subst _, ,$$*)).gann | genmodel
#	python3 $< $(word 2,$^) $(word 3,$^) $(word 4,$^) --output-compressed $@

.PRECIOUS: genmodel/cocopro.%.corpus
# genmodel/cocopro.1_100.corpus
genmodel/cocopro.%.corpus: scripts/munge_c3.py $(shell cat user-dgb-location.txt)/data/annotator$$(word 1,$$(subst _, ,$$*))/$$(word 2,$$(subst _, ,$$*)) \
				$(shell cat user-dgb-location.txt)/data/annotator$$(word 1,$$(subst _, ,$$*))/$$(word 2,$$(subst _, ,$$*))-annotation \
				$(shell cat user-c3-location.txt)/$$(word 2,$$(subst _, ,$$*)).gann \
				$$(basename $$@).sentids | genmodel
	python3 $< --text $(word 2,$^) --dgb-annotations $(word 3,$^) --c3-annotations $(word 4,$^) --sentences $(word 5,$^) --output-sentences $(basename $@).outsents --output $(basename $@).corpus

.PRECIOUS: genmodel/cocopro.%.sentids
genmodel/cocopro.%.sentids: user-sentokenizer-location.txt $(shell cat user-sentokenizer-location.txt)/simple_sentence_tokenizer.py $(shell cat user-dgb-location.txt)/data/annotator$$(word 1,$$(subst _, ,$$*))/$$(word 2,$$(subst _, ,$$*))
	python3 $(word 2,$^) --index --input $(word 3,$^) --output $@

.PRECIOUS: genmodel/cocopro.%.sents
# genmodel/cocopro.dgb_data.1_100.sents
genmodel/cocopro.%.sents: user-sentokenizer-location.txt $(shell cat user-sentokenizer-location.txt)/simple_sentence_tokenizer.py $(shell cat user-dgb-location.txt)/data/annotator$$(subst .,,$$(word 1,$$(subst _, ,$$(suffix $$*))))/$$(word 2,$$(subst _, ,$$(suffix $$*)))
	python3 $(word 2,$^) --input $(word 3,$^) --output $@

.PRECIOUS: genmodel/cocopro.%.parsed
# genmodel/cocopro.dgb_data.1_100.parsed
genmodel/cocopro.%.parsed: user-modelblocks-location.txt user-tokenizer-location.txt $(shell cat user-modelblocks-location.txt)/bin/parser-fullberk $(shell cat user-tokenizer-location.txt)/ptb_tokenizer.sed parsing_data/wsj02to21.gcg14.1671.5sm.fullberk.model genmodel/cocopro.$$*.sents
	cat $(word 6,$^) | $(word 4,$^) | $(word 3,$^) $(word 5,$^) | perl -pe 's/\+(?=[^\)]* )/\-/g'  |  perl -pe 's/-l[^ )]* / /g' > $@

#.PRECIOUS: genmodel/cocopro.%.cats
#genmodel/cocopro.%.cats: scripts/grab_leaves.sed scripts/align_parsed_text.py parsing_data/cocopro.notok.sents parsing_data/cocopro.wsj02to21-gcg14-1671-5sm.fullberk.parsed.nol.linetrees
#	$(word 1,$^) $(word 4,$^) | python3 $(word 2,$^) --parsed - --sentences $(word 3,$^) --output $@

.PRECIOUS: genmodel/cocopro.%.cats
# genmodel/cocopro.dgb_data.1_100.cats
genmodel/cocopro.%.cats: scripts/grab_leaves.sed scripts/align_parsed_text.py genmodel/cocopro.$$*.sents genmodel/cocopro.$$*.parsed
	$(word 1,$^) $(word 4,$^) | python3 $(word 2,$^) --parsed - --sentences $(word 3,$^) --output $@

#.PRECIOUS: genmodel/cocopro.%.corpus
# genmodel/cocopro.dgb_data-20.1_100.corpus
#genmodel/cocopro.%.corpus: scripts/munge_c3.py \
#				$(shell cat user-dgb-location.txt)/data/annotator$$(word 1,$$(subst _, ,$$(subst .,,$$(suffix $$*))))/$$(word 2,$$(subst _, ,$$(subst .,,$$(suffix $$*)))) \
#				$(shell cat user-dgb-location.txt)/data/annotator$$(word 1,$$(subst _, ,$$(subst .,,$$(suffix $$*))))/$$(word 2,$$(subst _, ,$$(subst .,,$$(suffix $$*))))-annotation \
#				$(shell cat user-c3-location.txt)/$$(word 2,$$(subst _, ,$$(subst .,,$$(suffix $$*)))).gann \
#				genmodel/cocopro.$$(basename $$*).$$(word 2,$$(subst _, ,$$(suffix $$*))).topics | genmodel
#	python3 $< --text $(word 2,$^) --dgb-annotations $(word 3,$^) --c3-annotations $(word 4,$^) --topics $(word 5,$^) --output-sentences genmodel/$(basename $$@).sentids --output $@

.PRECIOUS: genmodel/cocopro.%.topics
# genmodel/cocopro.dgb_data-20.100.topics
genmodel/cocopro.%.topics: user-mallet-location.txt $(shell cat user-mallet-location.txt)/bin/mallet genmodel/$$(word 1,$$(subst -, ,$$(basename $$*))).mallet genmodel/$$(basename $$*).topic_inferencer scripts/munge_doctopics.py
	mkdir tmpwork
	mkdir $(subst .,,$(suffix $*))
	#Need to remove carriage returns since the corpus was apparently created with Windows
	sed 's/\r//g' genmodel/$(word 1,$(subst -, ,$(basename $*)))/$(subst .,,$(suffix $*)).txt | csplit --prefix=$(subst .,,$(suffix $*))/ --quiet - '/^$$/' '{*}'
	$(word 2,$^) import-dir --input $(subst .,,$(suffix $*)) --output tmpwork/$(subst .,,$(suffix $*)).mallet --keep-sequence --remove-stopwords --use-pipe-from $(word 3,$^)
	$(word 2,$^) infer-topics --input tmpwork/$(subst .,,$(suffix $*)).mallet --inferencer $(word 4,$^) --output-doc-topics $(basename $@).doctopics
	python3 $(word 5,$^) --model $(basename $@).doctopics --text genmodel/$(word 1,$(subst -, ,$(basename $*)))/$(subst .,,$(suffix $*)).txt --output $@
	rm -rf tmpwork $(subst .,,$(suffix $*))

.PRECIOUS: genmodel/cocopro.%.vecs
# genmodel/cocopro.dgb_data.100.vecs
genmodel/cocopro.%.vecs: user-glove-location.txt $(shell cat user-glove-location.txt)/glove.6B.300d.txt scripts/build_vectoks.py \
												genmodel/$$(basename $$*)/$$(subst .,,$$(suffix $$*)).txt
	python3 $(word 3,$^) --vectors $(word 2,$^) --text $(word 4,$^) > $@

.PRECIOUS: genmodel/cocopro.%.pcounts
.PRECIOUS: genmodel/cocopro.%.regtable
# genmodel/cocopro.dgb_data-20.100.pcounts
genmodel/cocopro.%.pcounts genmodel/cocopro.%.regtable: scripts/calc_pcounts.py genmodel/cocopro.1_$$(subst .,,$$(suffix $$*)).corpus genmodel/cocopro.1_$$(subst .,,$$(suffix $$*)).sentids genmodel/cocopro.$$*.topics genmodel/cocopro.$$(word 1,$$(subst -, ,$$*))$$(suffix $$*).vecs genmodel/cocopro.$$(word 1,$$(subst -, ,$$*)).1_$$(subst .,,$$(suffix $$*)).cats
	python3 $< --coco-corpus $(word 2,$^) --topics $(word 4,$^) --regression genmodel/cocopro.$*.regtable --sentences $(word 3,$^) --vectors $(word 5,$^) --categories $(word 6,$^) --output genmodel/cocopro.$*.pcounts

.PRECIOUS: genmodel/cocopro.%.regtables
# genmodel/cocopro.dgb_data-20.regtables
genmodel/cocopro.%.regtables: scripts/find_feature_weights.py $(foreach sect,$(DGBDEVSECTS), genmodel/cocopro.$$*.$(sect).regtable)
	python $< $(foreach sect,$(DGBDEVSECTS), --input genmodel/cocopro.$*.$(sect).regtable) > $@

.PRECIOUS: genmodel/cocopro.%.regtables.acc
# genmodel/cocopro.dgb_data-20+100.regtables
genmodel/cocopro.%.regtables genmodel/cocopro.%.regtables.acc: scripts/find_feature_weights.py $(foreach sect,$(DGBSECTS), genmodel/cocopro.$$(word 1,$$(subst +, ,$$*)).$(sect).regtable)
	python $< $(foreach sect,$(DGBSECTS), --input genmodel/cocopro.$(word 1,$(subst +, ,$*)).$(sect).regtable) --hold-out genmodel/cocopro.$(word 1,$(subst +, ,$*)).$(word 2,$(subst +, ,$*)).regtable --acc genmodel/cocopro.$*.regtables.acc > genmodel/cocopro.$*.regtables

.PRECIOUS: genmodel/cocopro.%.latmodels
# genmodel/cocopro.dgb_data-20.latmodels
genmodel/cocopro.%.latmodels: scripts/infer_ref.py $(foreach sect,$(DGBDEVSECTS), genmodel/cocopro.$$*.$(sect).regtable)
	python $< $(foreach sect,$(DGBDEVSECTS), --input genmodel/cocopro.$*.$(sect).regtable) > $@

.PRECIOUS: genmodel/cocopro.%.latmodels.acc
# genmodel/cocopro.dgb_data-20+100.latmodels
genmodel/cocopro.%.latmodels genmodel/cocopro.%.latmodels.acc: scripts/infer_ref.py $(foreach sect,$(DGBSECTS), genmodel/cocopro.$$(word 1,$$(subst +, ,$$*)).$(sect).regtable)
	python $< $(foreach sect,$(DGBSECTS), --input genmodel/cocopro.$(word 1,$(subst +, ,$*)).$(sect).regtable) --hold-out genmodel/cocopro.$(word 1,$(subst +, ,$*)).$(word 2,$(subst +, ,$*)).regtable --acc genmodel/cocopro.$*.latmodels.acc > genmodel/cocopro.$*.latmodels

#.PRECIOUS: %.pcounts
## genmodel/cocopro.dgb_data-20.100.pcounts
#%.pcounts: scripts/calc_pcounts.py genmodel/cocopro.1_$$(subst .,,$$(suffix $$*)).corpus genmodel/cocopro.1_$$(subst .,,$$(suffix $$*)).sentids $$*.topics $$(word 1,$$(subst -, ,%))$$(suffix $$*).vecs
#	python3 $< --coco-corpus $(word 2,$^) --topics $(word 4,$^) --sentences $(word 3,$^) --vectors $(word 5,$^) --output $@

#.PRECIOUS: %.model
# basic model (trained on full corpus)
# genmodel/cocopro.dgb_data-20.model
#%.model: scripts/calc_logprobs.py $(foreach sect,$(DGBSECTS), %.$(sect).pcounts)
#	python3 $< $(foreach sect,$(DGBSECTS),--input $*.$(sect).pcounts) --output $@

.PRECIOUS: %.model
# jack knife model (trained on all but one subcorpus)
# genmodel/cocopro.dgb_data-20+100.model
%.model: scripts/calc_logprobs.py $(foreach sect,$(DGBSECTS), $$(word 1,$$(subst +, ,%)).$(sect).pcounts)
	python3 $< $(foreach sect,$(DGBSECTS),--input $(word 1,$(subst +, ,$*)).$(sect).pcounts) --hold-out $(word 2,$(subst +, ,$(suffix $*))) --output $@

.PRECIOUS: %.training_likelihood
# likelihood after training on all subcorpora
# genmodel/cocopro.dgb_data-20.100.training_likelihood
%.training_likelihood: scripts/calc_likelihood.py  $$(basename %).model $$(basename $$(basename %)).1_$$(subst .,,$$(suffix $$*)).corpus %.topics $$(basename $$(basename %)).1_$$(subst .,,$$(suffix $$*)).sentids
	python3 $< --model $(word 2,$^) --input $(word 3,$^) --topics $(word 4,$^) --sentences $(word 5,$^) --output $@

# genmodel/cocopro.dgb_data-20.training_likelihood
%.training_likelihood: scripts/sum_probs.py $(foreach sect,$(DGBSECTS),%.$(sect).training_likelihood)
	python3 $^ > $@

#.PRECIOUS: %.accuracy
# accuracy on a subcorpus after training on all subcorpora
# genmodel/cocopro.dgb_data-20.100.accuracy
#%.accuracy: scripts/predict.py  $$(basename %).model $$(basename $$(basename %)).1_$$(subst .,,$$(suffix $$*)).corpus %.topics $$(basename $$(basename %)).1_$$(subst .,,$$(suffix $$*)).sentids
#	python3 $< --model $(word 2,$^) --input $(word 3,$^) --topics $(word 4,$^) --sentences $(word 5,$^) --output $@

.PRECIOUS: %.accuracy
# accuracy on a subcorpus after training on all subcorpora *except* that subcorpus
# genmodel/cocopro.dgb_data-20.100.accuracy
%.accuracy: scripts/predict.py  $$(basename %)+$$(subst .,,$$(suffix $$*)).model $$(basename $$(basename %)).1_$$(subst .,,$$(suffix $$*)).corpus %.topics $$(basename $$(basename %)).1_$$(subst .,,$$(suffix $$*)).sentids $$(word 1,$$(subst -, ,$$(basename %)))$$(suffix $$*).vecs $$(word 1,$$(subst -, ,%)).1_$$(subst .,,$$(suffix $$*)).cats
	python3 $< --model $(word 2,$^) --input $(word 3,$^) --topics $(word 4,$^) --sentences $(word 5,$^) --vectors $(word 6,$^) --categories $(word 7,$^) --output $@

.PRECIOUS: %.totaccuracy
# overall accuracy
# genmodel/cocopro.dgb_data-20.accuracy
%.totaccuracy: scripts/sum_accuracy.py $(foreach sect, $(DGBSECTS),%.$(sect).accuracy)
	python3 $^ > $@

%.devaccuracy: scripts/sum_accuracy.py $(foreach sect, $(DGBDEVSECTS),%.$(sect).accuracy)
	python3 $^ > $@

%.testaccuracy: scripts/sum_accuracy.py $(foreach sect, $(DGBTESTSECTS),%.$(sect).accuracy)
	python3 $^ > $@

%.totclassaccuracy: scripts/sum_accuracy.py $(foreach sect, $(DGBSECTS),%+$(sect).regtables.acc)
	python3 $^ > $@

%.devclassaccuracy: scripts/sum_accuracy.py $(foreach sect, $(DGBDEVSECTS),%+$(sect).regtables.acc)
	python3 $^ > $@

%.testclassaccuracy: scripts/sum_accuracy.py $(foreach sect, $(DGBTESTSECTS),%+$(sect).regtables.acc)
	python3 $^ > $@

%.totlataccuracy: scripts/sum_accuracy.py $(foreach sect, $(DGBSECTS),%+$(sect).latmodels.acc)
	python3 $^ > $@

%.devlataccuracy: scripts/sum_accuracy.py $(foreach sect, $(DGBDEVSECTS),%+$(sect).latmodels.acc)
	python3 $^ > $@

%.testlataccuracy: scripts/sum_accuracy.py $(foreach sect, $(DGBTESTSECTS),%+$(sect).latmodels.acc)
	python3 $^ > $@

#.PRECIOUS: genmodel/cocopro.counts
#genmodel/cocopro.counts: $(foreach annotator,1 2,$(foreach sect,$(DGBSECTS),genmodel/cocopro.$(annotator)_$(sect).counts))
#genmodel/cocopro.counts: $(foreach sect,$(DGBSECTS),genmodel/cocopro.1_$(sect).counts)
#	#c3 only exists for annotator_1, so treat that as gold, and we can modify this with annotator_2 later
#	cat $^ > $@

genmodel/dgb_data: | genmodel
	# This creates a directory of dgb data for mallet to train up a topic model on
	mkdir genmodel/dgb_data
	for i in $(shell ls $(shell cat user-dgb-location.txt)/data/annotator1/* | sed 's/[^ ]* //g;' | grep -v "annotation"); do cp $$i genmodel/dgb_data/$$(basename $$i); done
	for i in genmodel/dgb_data/*; do sed 's/^--//g;' $$i > $$i.txt; rm -f $$i; done

.PRECIOUS: genmodel/%.mallet
#genmodel/dgb_data.mallet
genmodel/%.mallet: $(shell cat user-mallet-location.txt)/bin/mallet genmodel/$(basename $$*)
	# Although we're modeling stopwords, we don't want them in the topic model since they'll overpower all other cues
	$< import-dir --input $(word 2,$^) --output $@ --keep-sequence --remove-stopwords


.PRECIOUS: genmodel/%.topic_inferencer
#genmodel/dgb_data-20.topic_inferencer
genmodel/%.topic_inferencer: user-mallet-location.txt $(shell cat user-mallet-location.txt)/bin/mallet genmodel/$$(word 1,$$(subst -, ,$$*)).mallet
	# Takes a target like dgb_data-20.topic_model and trains up a topic model on dgb_data with 20 topics
	# NB: --output-topic-keys and --output-doc-topics are more for exploration than production, so remove them from the final makeflow
	$(word 2,$^) train-topics --input $(word 3,$^) --num-topics $(word 2,$(subst -, ,$*)) --optimize-interval $(word 2,$(subst -, ,$*)) --output-state genmodel/$*.topic_model.gz --inferencer-filename genmodel/$*.topic_inferencer  --random-seed 37 #--output-topic-keys $*_keys.txt --output-doc-topics $*_composition.txt