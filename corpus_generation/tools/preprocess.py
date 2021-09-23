import os

import subprocess
import sys
import argparse

#truecase_script = "/home/chryssa/QE-ST/qe-corpus-builder/external_tools/mosesdecoder/scripts/recaser/truecase.perl"
#truecase_model = "truecase.all."+lang+".ms.model"
#os.system("perl "+ truecase_script + " --model "+truecase_model+ "  < " + file_prefix + ".reord.tok.src > "+ file_prefix + ".reord.tok.tc.src"


def truecase(truecase_script, truecase_model, infile):
    #perl_params = [truecase_script, '--model',truecase_model, '<', infile, '>', outfile]
    perl_params = [truecase_script, '--model',truecase_model]
    #perl_script = subprocess.Popen(perl_params, stdin=infile, stdout=outfile)
    #perl_script.communicate()
    outfile = infile.rsplit('.')[0]+'.'+infile.rsplit('.')[1]+'.tc.'+infile.rsplit('.')[2]
    print(outfile)
    if len(truecase_model)>0:
        with open(outfile, 'wb', 0) as fileout:
            with open(infile, 'r') as filein:
                subprocess.call(perl_params, stdin=filein, stdout=fileout)
    return outfile

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tc_model_src', help='tc model', type=str)
    parser.add_argument('--tc_model_tgt', help='tc model', type=str)
    parser.add_argument('--infile', help='Gaps predictions', type=str)
    parser.add_argument('--outfile', help='Path to output', type=str) 
    parser.add_argument('--infile', help='Gaps predictions', type=str)
    parser.add_argument('--outfile', help='Path to output', type=str)
    return parser.parse_args()

def main(args):
    truecase_script = "/home/chryssa/QE-ST/qe-corpus-builder/external_tools/mosesdecoder/scripts/recaser/truecase.perl"
    
    truecase(truecase_script, args.model, args.infile)

if __name__ == '__main__':
    args = parse_args()
    main(args)