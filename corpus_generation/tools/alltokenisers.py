import os
from tqdm.notebook import tqdm
import jieba
import janome.tokenizer 
import re
import subprocess 
import fugashi
import fileinput
import sys
import indicnlp


def parse_file2lines(filename):
    lines=[]
    with open(filename) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines] 
    return lines

def janome_tokenize(infile, outfile):
    print('Using Janome tokenizer')
    tokenizer = janome.tokenizer.Tokenizer()
    lines = parse_file2lines(infile)
    wf = open(outfile,'w')
    for line in lines:
        tokens = [tok.surface for tok in tokenizer.tokenize(line.strip())]
        out = ' '.join(tokens)
        out = re.sub('\s+', ' ', out)
        wf.write(out+'\n')
    wf.close()

def jieba_tokenize(infile, outfile):
    print('Using jieba tokenizer')
    lines = parse_file2lines(infile)
    wf = open(outfile,'w')
    for line in lines:
        tokens = [tok.surface for tok in jieba.tokenize(line.strip())]
        out = ' '.join(tokens)
        out = re.sub('\s+', ' ', out)
        wf.write(out+'\n')
    wf.close()

def moses_tokenize(lang, infile, outfile):    
    print('Using Moses tokenizer')
    tokeniser_script = "../external_tools/mosesdecoder/scripts/tokenizer/tokenizer.perl"
    perl_params = [tokeniser_script, '-l',lang, '-no-escape']
    with open(outfile, 'wb', 0) as fileout:
        with open(infile, 'r') as filein:
            subprocess.call(perl_params, stdin=filein, stdout=fileout)

def fugashi_tokenize(infile,outfile):
    print('Using FUGASHI tokenizer')
    tokenizer = fugashi.Tagger()
    lines = parse_file2lines(infile)
    wf = open(outfile,'w')
    for line in lines:
        tokens = [word.surface for word in tokenizer(line.strip())]
        out = ' '.join(tokens)
        out = re.sub('\s+', ' ', out)
        wf.write(out+'\n')
    wf.close()

def flores_tokenize(language, infile, outfile):
    print('Using flores tokenizer')
    indic_nlp_path='../external_tools/indic_nlp_resources'
    try:
        sys.path.extend([
            indic_nlp_path,
            os.path.join(indic_nlp_path, "src"),
        ])
        from indicnlp.tokenize import indic_tokenize
        from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
    except:
        raise Exception(
            "Cannot load Indic NLP Library, make sure --indic-nlp-path is correct"
        )
    # create normalizer
    factory = IndicNormalizerFactory()
    normalizer = factory.get_normalizer(
        language, remove_nuktas=False,
    )
    factory = IndicNormalizerFactory()
    normalizer = factory.get_normalizer(
        language, remove_nuktas=False,
    )
    lines = parse_file2lines(infile)
    wf = open(outfile, 'w')
    # normalize and tokenize
    for line in lines:
        line = normalizer.normalize(line)
        line = " ".join(indic_tokenize.trivial_tokenize(line, language))
        wf.write(line.strip() + '\n')
    wf.close()


def tokenize(lang, infile):
    outfile = infile.rsplit('.')[0]+'.tok.'+infile.rsplit('.')[1]
    print("tokenizing file "+infile+" for lang "+lang)
    if lang=='zh':
        jieba_tokenize(infile, outfile)
    elif lang=='ja':
        fugashi_tokenize(infile, outfile)
    elif lang=='ne'or lang=='si' or lang=='ma' or lang=='mr':
        flores_tokenize(lang, infile, outfile)
    else:
        moses_tokenize(lang, infile, outfile)
    return outfile