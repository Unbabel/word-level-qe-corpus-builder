import simalign
from tqdm import tqdm

from simalign import SentenceAligner

def parse_file2lines(filename):
    lines=[]
    with open(filename) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines] 
    return lines

def align_simaligner(infile_src, infile_tgt, outfile, langs):

    moden = 'itermax'
    for lang in langs:
        if lang in ['de', 'cs']:
            moden = 'inter'
    #model options: bert | xlmr |
    tok_src_lines = parse_file2lines(infile_src)
    tok_tgt_lines = parse_file2lines(infile_tgt)

    simple_aligner = SentenceAligner(model="xlmr", token_type="bpe", matching_methods="mai")

    # The output is a dictionary with different matching methods.
    # Each method has a list of pairs indicating the indexes of aligned words (The alignments are zero-indexed).
    alignments=[]
    for src_sentence, trg_sentence in tqdm(zip(tok_src_lines, tok_tgt_lines)):
        alignments.append(simple_aligner.get_word_aligns(src_sentence, trg_sentence)[moden])

    writer = open(outfile, 'w')
    print('Writing alignments at: '+outfile)
    for alignment in alignments:
        line = ''
        for pair in alignment:
            p = str(pair[0])+'-'+str(pair[1])
            line += p+' '
        writer.write(line.strip()+'\n')
    writer.close()