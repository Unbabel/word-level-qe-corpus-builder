Redefine Word Quality Estimation
======

# Following tools are needed

## Install Fast Align

Download zip and uncompress it into the `./external_tools/` folder. In unix
systems this can be done with

    mkdir ./external_tools/
    cd ./external_tools/
    wget https://github.com/clab/fast_align/archive/master.zip
    unzip master.zip
    rm master.zip
    
Then follow 

    fast_align-master/README.md 
    
to install. Note that you will need some extra utilities described there.
Ubuntu friendly commands are given in the README.md. 

    ./external_tools/fast_align-master/build/fast_align  

## Install Tercom

Just dowload the tool and decompress it

    cd ./external_tools
    wget http://www.cs.umd.edu/~snover/tercom/tercom-<version>.tgz
    tar -xf tercom-<version>.tgz

If you are sucesful the following file should be available

    ./external_tools/tercom-<version>/tercom.<version>.jar

where `<version>` is the tercom version.

## Generating the first version of the tags 

You will need to train fast align from a sufficienlty big corpus. Current
example uses WMT2017 QE-task2 data which is unsufficient. Uncompress the
WMT2017 data on a `DATA` folder. This should look like

    DATA/task2_en-de_training/

Then train `fast_align` with

    cd corpus_generation/
    bash train_fast_align_wmt2017.sh

Once fast align is trained, call the following to generate the tags

    bash get_tags_wmt2017.sh 

Tags are currently stored under e.g.

    DATA/temporal_files/task2_en-de_training/

## Exploring the tags

Use the notebook in `notebooks`

    notebooks/Investigate-BAD-tag-approaches.ipynb
