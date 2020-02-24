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

Download zip and uncompress it into the `./external_tools/` folder. In Unix
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

Download the latest version of the tool and decompress it. For the WMT2018
corpus creation we used

    cd ./external_tools
    wget http://www.cs.umd.edu/~snover/tercom/tercom-0.7.25.tgz
    tar -xf tercom-0.7.25.tgz

If you are sucesful the following file should be available

    ./external_tools/tercom-0.7.25/tercom.7.25.jar

## Training Fast Align 

To train fast align in any new corpus, call directly the script `train_fast_align.sh`
inside `tools`:

    bash tools/train_fast_align.sh source.txt target.txt temp-dir/ models/src-tgt/
    
The files `source.txt` and `target.txt` must be large text files with aligned sentences, 
one per line. This script will create the input to fast align in the temporary directory 
and save the trained model in the given models directory.

## Preprocessing

Before generating alignment tags, make sure to tokenize and truecase source, mt and post-edited files. The moses tokenizer is a common choice. Double check to use the correct language option.

    perl /path/to/moses/scripts/tokenizer/tokenize.pl -l (en|de|...) -no-escape < text.source > text.tok.source
    
The `-no-escape` option prevents automatic conversion of HTML entities such as `'` to `&apos;`.

Then, truecasing. This needs to have a truecaser model; a new one can be trained with `train-truecaser.perl` under moses.

    perl /path/to/moses/scripts/recaser/truecase.perl --model truecaser.model < text.tok.source > text.tok.tc.src


## Generating alignment tags

Once fast align is trained and inputs tokenized, use the script `get_tags.sh` to generate word alignment tags 
on the QE data:

    bash tools/get_tags.sh text.tok.tc.src text.tok.tc.mt text.tok.tc.pe models/src-tgt temp-dir
    output-dir normal

The command above will generate alignment files in the `output` directory.

## Exploring the tags

You can explore the created tags using the notebook in `notebooks`. For this 
you will have to install the `jupyter` Python module

    jupyter-notebook notebooks/Investigate-BAD-tag-approaches.ipynb
