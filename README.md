Redefine Word Quality Estimation
======

# Following tools are needed

## Install Fast Align

Download zip and uncompress it into the `corpus_generation/external_tools/`
folder. In unix systems this can be done with

    mkdir ./external_tools/
    cd ./external_tools/
    wget https://github.com/clab/fast_align/archive/master.zip
    unzip master.zip
    
Then follow `fast_align-master/README.md` to install. 

## Install Tercom

TODO

# Creating your own Corpus 

This is exemplified usingv the WMT2017 data-set. If you want to reproduce this 
get it and store it inside `DATA/`, it should look like

	DATA/task2_en-de_training/
	etc

## Train fast_align models

    bash  corpus_generation/train_fast_align.sh DATA/task2_en-de_training/train.src DATA/task2_en-de_training/train.pe DATA/fast_align_models/en_de/

## Generate Tags from Tercom
