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
Ubuntu friendly commands are given in the README.md. If you are sucesful the
following binary should be available

    ./external_tools/fast_align-master/build/fast_align  

## Install Tercom

Just dowload the tool and decompress it

    cd ./external_tools
    wget http://www.cs.umd.edu/~snover/tercom/tercom-<version>.tgz
    tar -xf tercom-<version>.tgz

If you are sucesful the following file should be available

    ./external_tools/tercom-<version>/tercom.<version>.jar

where `<version>` is the tercom version.

## Generate alignments

## Generate Tags from Tercom



## Training models for your own Corpus 

See 

    corpus_generation/README.md
