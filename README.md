Word Quality Estimation for NMT
======

This is an updated version of the WMT word-level quality estimation task (Bojar
et al 2017) that takes into account both fluency and adequacy issues. It
requires not only the detection of wrong words but also insertion errors. It
also requires as well detecting words in the source that can be related to
errors on the target side.  

The tags are determined using the tools in previous WMT editions (fast_align,
tercom) with minor changes. Namely alignments are used to determine source
words that can be related to target side errors and one or more consecutive
insertions after tercom alignment are indicated as a single gap (insertion)
error.

# Following tools are needed

## Install Fast Align

Download zip and uncompress it into the `./external_tools/` folder. In unix
systems this can be done with

    mkdir ./external_tools/
    cd ./external_tools/
    wget https://github.com/clab/fast_align/archive/master.zip
    unzip master.zip
    rm master.zip
    
Then 

    cd fast_align-master/

check the `README.md` in that folder as there may be extra libraries needed.
Ubuntu friendly commands are provided to instal these. With the needed
libraries just do

    mkdir build
    build
    cmake ..
    make

as indicated in the `fast_align-master/README.md`. If everything goes right,
this should create

    ./external_tools/fast_align-master/build/fast_align  

## Install Tercom

Just go to

    http://www.cs.umd.edu/~snover/tercom/

dowload the latest version of the tool and decompress it. For the WMT2018
corpus creation we used

    cd ./external_tools
    wget http://www.cs.umd.edu/~snover/tercom/tercom-0.7.25.tgz
    tar -xf tercom-0.7.25.tgz

If you are sucesful the following file should be available

    ./external_tools/tercom-0.7.25/tercom.7.25.jar

## Generating the first version of the tags 

This is a simple example using WMT2017. In reality you will need to train fast
align from a sufficienlty big corpus. 

Uncompress the WMT2017 data on a `DATA` folder. This should look like

    mkdir DATA
    DATA/WMT2017/task2_de-en_training
    DATA/WMT2017/task2_de-en_training-dev
    DATA/WMT2017/task2_de-en_dev         
    DATA/WMT2017/task2_en-de_dev  
    DATA/WMT2017/task2_en-de_training
    DATA/WMT2017/task2_de-en_test
    DATA/WMT2017/task2_en-de_test  

Then train `fast_align` with

    cd corpus_generation/
    bash train_fast_align_wmt2017.sh

Once fast align is trained, call the following to generate the tags

    bash get_tags_wmt2017.sh 

Tags are currently stored under e.g.

    DATA/WMT2017/temporal_files/task2_en-de_training/

## Exploring the tags

Use the notebook in `notebooks`. For this you will have to install the
`jupyter` Python module

    jupyter-notebook notebooks/Investigate-BAD-tag-approaches.ipynb
