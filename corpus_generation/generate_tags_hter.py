import os
from sqlite3 import TimestampFromTicks
import subprocess
import sys
import argparse

sys.path.insert(0, 'tools')

from tools.alltokenisers import tokenize
from tools.preprocess import truecase
from tools.aligners import align_simaligner as align
from tools.generate_BAD_tags import generate_bad_ok_tags


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', help='Source', type=str)
    parser.add_argument('--mt', help='MT hypothesis (target)', type=str)
    parser.add_argument('--pe', help='Post edited translation', type=str)
    parser.add_argument('--src_lang', help='Source language abbreviation', type=str)
    parser.add_argument('--tgt_lang', help='Target language abbreviation', type=str)
    parser.add_argument('--src_tc', type=str, default='')
    parser.add_argument('--tgt_tc', type=str, default='')
    parser.add_argument('--token', dest='token', action='store_true')
    parser.add_argument('--truecase', dest='truecase', action='store_true')
    parser.add_argument('--gaps', dest='truecase', action='store_true')
    parser.set_defaults(token=True)
    parser.set_defaults(truecase=False)
    parser.set_defaults(gaps=False)
    return parser.parse_args()

def main(args):
    print(args)
    src = args.src 
    mt = args.mt   
    pe = args.pe  
    path = os.path.dirname(os.path.abspath(src))
    if args.token:
        tok_src = tokenize(args.src_lang, src)
        tok_mt = tokenize(args.tgt_lang, mt)
        tok_pe = tokenize(args.tgt_lang, pe)
    else:
        tok_src = src
        tok_mt = mt 
        tok_pe = pe 
    
    if args.truecase:
        truecase_script = "../external_tools/mosesdecoder/scripts/recaser/truecase.perl"
        tok_tc_src = truecase(truecase_script, args.src_tc, tok_src)
        tok_tc_mt = truecase(truecase_script, args.tgt_tc, tok_mt)
        tok_tc_pe = truecase(truecase_script, args.tgt_tc, tok_pe)
    else:
        tok_tc_src = tok_src
        tok_tc_mt = tok_mt
        tok_tc_pe = tok_pe
    
    src_mt_align = src.rsplit('.')[0]+'.src-mt.alignments'
    src_pe_align = src.rsplit('.')[0]+'.src-pe.alignments'
    mt_pe_align = src.rsplit('.')[0]+'.mt-pe.alignments'


    align(tok_src, tok_mt, src_mt_align, [args.src_lang, args.tgt_lang])
    align(tok_src, tok_pe, src_pe_align, [args.src_lang, args.tgt_lang])

    
    tercom = "temp/tercom/"
    
    params = ["bash ./tools/tercom.sh  " + tok_tc_mt + " " + tok_tc_pe +"  "+ tercom + "  " + mt_pe_align + "  false"]
    print(" ".join(params))
    p = subprocess.Popen(params, shell=True)
    p.wait() 
   
    src_tags = src.rsplit('.')[0]+'.source_tags'
    tgt_tags = src.rsplit('.')[0]+'.target_tags'
    hter = src.rsplit('.')[0]+'.hter'
    print("ALIGNED MT PE")

    if args.gaps:
        generate_bad_ok_tags(tok_tc_src, tok_tc_mt, tok_tc_pe, mt_pe_align, src_pe_align, 'normal', src_tags, tgt_tags)
    else:
        generate_bad_ok_tags(tok_tc_src, tok_tc_mt, tok_tc_pe, mt_pe_align, src_pe_align, 'normal', src_tags, tgt_tags, False)
    params = ["bash ./tools/tercom.sh " +  tok_tc_mt+ " " + tok_tc_pe + " " + tercom + " "+ mt_pe_align + " true"]
    p2 = subprocess.Popen(params, shell=True)
    p2.wait() 

    params = ["tail -n +3 temp/tercom/out_tercom_file.ter | awk '{if ($4 > 1) hter=1; else hter=$4; printf \"%.6f\\n\",hter}' > "+hter]
    p3 = subprocess.Popen(params, shell=True)
    p3.wait() 
    print('processed')
 
if __name__ == '__main__':
    args = parse_args()
    main(args)