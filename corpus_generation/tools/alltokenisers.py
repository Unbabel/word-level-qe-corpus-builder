import os
from tqdm import tqdm
import jieba
import janome.tokenizer 
import re
import subprocess 

def parse_file2lines(filename):
    lines=[]
    with open(filename) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines] 
    return lines

def janome_tokenize(infile, outfile):
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
  
    lines = parse_file2lines(infile)
    wf = open(outfile,'w')
    for line in lines:
        tokens = [tok.surface for tok in jieba.tokenize(line.strip())]
        out = ' '.join(tokens)
        out = re.sub('\s+', ' ', out)
        wf.write(out+'\n')
    wf.close()

def moses_tokenize(lang, infile, outfile):    
    tokeniser_script = "/home/chryssa/QE-ST/qe-corpus-builder/external_tools/mosesdecoder/scripts/tokenizer/tokenizer.perl"
    #os.system("perl " + tokeniser_script + " -l "+lang+" -no-escape < " + infile + " > " + outfile)

    perl_params = [tokeniser_script, '-l',lang, '-no-escape']
    #perl_script = subprocess.Popen(perl_params, stdin=infile, stdout=outfile)
    #perl_script.communicate()

    with open(outfile, 'wb', 0) as fileout:
        with open(infile, 'r') as filein:
            subprocess.call(perl_params, stdin=filein, stdout=fileout)


def tokenize(lang, infile):
    outfile = infile.rsplit('.')[0]+'.tok.'+infile.rsplit('.')[1]
    if lang=='zh':
        jieba_tokenize(infile, outfile)
    elif lang=='ja':
        janome_tokenize(infile, outfile)
    else:
        moses_tokenize(lang, infile, outfile)
    return outfile
