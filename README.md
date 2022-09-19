Quality Estimation for NMT
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

# Preprocessing tools

## Tokenization
Before generating alignment tags, it is necessary to tokenize and truecase source, mt and post-edited files. The __moses__ tokenizer is the default choice for most languages, but different tokenisers might be optimal for some languages.

 We provide below a breakdown of the proposed tokeniser per language (the indicated tokenisers are used by default for the generation of the MLQE-PE 2021 data).  

| Language  | Code | Tokenizer  |
|-----------|------|------------|
| Chinese   |  zh  | jieba      |
| Czech     |  cs  | moses      |
| English   |  en  | moses      |
| Esthonian |  et  | moses      |
| German    |  de  | moses      |
| Japanese  |  ja  | fugashi    |
| Khmer     |  km  | nltk-khmer |
| Marathi   |  mr  | indic_nlp  |
| Nepalese  |  ne  | indic_nlp  |
| Pashto    |  ps  | moses      |
| Romanian  |  ro  | moses      |
| Russian   |  ru  | moses      |
| Sinhala   |  si  | indic_nlp  |

We provide installation and versioning information below for each of the proposed tokenizers:

### Moses Installation
There are various wrappers for moses tokenizer with small output discrepancies among them. For the WMT2021 QE shared task we use the perl script mosestokenizer, made avalable in the scripts of the mosesdecoder [github repo](https://github.com/moses-smt/mosesdecoder). 

__Usage:__ Apart from specifying the specific language extention (en|de|cs etc), we also use the `--no-escape` option. The `--no-escape` option prevents automatic conversion of HTML entities such as `'` to `&apos;`.

### Jieba Installation
The jieba tokeniser can be installed easily with:

    pip install jieba

For the  WMT2021 QE shared task the jieba version used is the jieba 0.42.1 

fugashi-1.1.1

###

### Indic-NLP
Requires the installation of the indic-nlp-library (for WMT21 the version used was indic-nlp-library-0.81) with: 

    pip install indic-nlp-library

After installation it is necessary to create a directory for  Indic NLP Resources and then export the path. The default setup is to have the directory in the external_tools:

    export INDIC_RESOURCES_PATH='qe-corpus-builder/external_tools/indic_nlp_resources'


## True-casing

True-casing needs to preceed the MT-PE alignments and HTER calculation. Moses was used to train and apply true-casing for all language pairs. New models can be trained with the perl script made available in the `modes-decoder` repo.

    perl /path/to/moses/scripts/recaser/truecase.perl --model truecaser.model < text.tok.source > text.tok.tc.src


## Alignment
To obtain HTER scores and word tags, we need to align source-MT, source-PE and MT-PE.

To extract the source-MT/PE alignments we use __Simalign__.

### Simalign Installation
Install Simalign from the source ([github repo](https://github.com/cisnlp/simalign)) or install by pip:

    pip install --upgrade git+https://github.com/cisnlp/simalign.git#egg=simalign


### Usage
 We use the multilingual XLM-Roberta (base) model as encoder, and follow the SimAlign paper to decide the matching mode based on the language pairs [[1]](#1).

__Notes__:
Previous versions of the corpus_builder used fast-align to get the alignments. See [the previous github version](https://github.com/deep-spin/qe-corpus-builder) for more details.

### TerCOM Installation
Tercom can be downloaded from:

    http://www.cs.umd.edu/~snover/tercom/

Download the latest version of the tool and decompress it. For the WMT2018
corpus creation we used

    cd ./external_tools
    wget http://www.cs.umd.edu/~snover/tercom/tercom-0.7.25.tgz
    tar -xf tercom-0.7.25.tgz

If you are sucesful the following file should be available

    ./external_tools/tercom-0.7.25/tercom.7.25.jar

# Steps

The corpus can be generated by calling `generate_tags_hter.py` from the `corpus_generation` folder. An example of running for an en-de language pair follows:  

    python3 generate_tags_hter.py --src /path/to/data/folder/and/src/file/dev.src --mt /path/to/data/folder/and/src/file/dev.mt --pe /path/to/data/folder/and/src/file/dev.pe --src_lang en --tgt_lang de --src_tc /path/to/trained/truecase/src/model/truecase.all.en.ms.model --tgt_tc /path/to/trained/truecase/tgt/model/truecase.all.de.ms.model --token --truecase --align 



To run processing steps individually:



# References
<a id="1">[1]</a>  Sabet, Masoud Jalili, et al. "SimAlign: High Quality Word Alignments Without Parallel Training Data Using Static and Contextualized Embeddings." Findings of the Association for Computational Linguistics: EMNLP 2020. 2020.
