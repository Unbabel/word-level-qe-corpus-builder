import sys
sys.path.append('.')
from tools.io import read_file, purple

# Data
source_file = 'DATA/task2_en-de_training/train.src'
mt_file = 'DATA/task2_en-de_training/train.mt'
pe_file = 'DATA/task2_en-de_training/train.pe'
src_pe_align_file = 'DATA/temporal_files/train.src-pe.alignments'
mt_pe_align_file = 'DATA/temporal_files/train.mt-pe.edit_alignments'
pe_mt_edits_file = 'DATA/temporal_files/train.mt-pe.edits'

source_tokens = read_file(source_file)
mt_tokens = read_file(mt_file)
pe_tokens = read_file(pe_file)
src_pe_alignments = read_file(src_pe_align_file, alignments=True)
mt_pe_alignments = read_file(mt_pe_align_file, alignments=True)
pe_mt_edits = read_file(pe_mt_edits_file)

# Sanity Checks
num_sentences = len(source_tokens)
assert len(mt_tokens) == num_sentences, "Number of sentences does not match"
assert len(pe_tokens) == num_sentences, "Number of sentences does not match"
assert len(src_pe_alignments) == num_sentences, \
    "Number of sentences does not match"
assert len(mt_pe_alignments) == num_sentences, \
    "Number of sentences does not match"
assert len(pe_mt_edits) == num_sentences, "Number of sentences does not match"
# Check the alignments are correct
assert all([
    length-1 >= max_index
    for length, max_index in zip(
        map(len, source_tokens),
        [max([x[0] for x in sent]) for sent in src_pe_alignments]
    )
]), "Index out of bounds for source in alignments"
assert all([
    length-1 >= max_index
    for length, max_index in zip(
        map(len, pe_tokens),
        [max([x[1] for x in sent]) for sent in src_pe_alignments]
    )
]), "Index out of bounds for pe in alignments"

# Organize into a dictionary ala mongo
sentences = []
for src, mt, pe, src_pe, mt_pe, edits in zip(
    source_tokens,
    mt_tokens,
    pe_tokens,
    src_pe_alignments,
    mt_pe_alignments,
    pe_mt_edits
):
    sentences.append({
        'source': src,
        'mt': mt,
        'pe': pe,
        'src-pe_alignments': src_pe,
        'mt-pe_alignments': mt_pe,
        'edits': edits
    })

# Display in vertical
for sentence in sentences:
    print("")

    # Pad source and target
    mt_indices, pe_indices = zip(*sentence['mt-pe_alignments'])

    import ipdb;ipdb.set_trace(context=50)

    # Find words deleted on mt
    pe_indices = map(lambda x: x[1], sentence['mt-pe_alignments'])
    missing_pe_indices = [
        x for x in range(len(sentence['pe']))
        if x not in pe_indices
    ]

    if missing_pe_indices:
        import ipdb;ipdb.set_trace(context=50)
        print("")


    for mt_index in range(len(sentence['mt'])):

        # Find aligned reference words
        pe_index = [
            x[0] for x in sentence['mt-pe_alignments'] if x[1] == mt_index
        ]
        pe_tokens = " ".join([sentence['pe'][i] for i in pe_index])


        # PRINT MT PT AND SOURCE

        # Find source words aligned to reference
        if pe_index:
            src_index = [
                x[0] for x in sentence['src-pe_alignments']
                if x[1] == pe_index[0]
            ]
            src_tokens = ", ".join([sentence['source'][i] for i in src_index])
        else:
            src_tokens = " "

        # PE aligned to mt
        display_str = "%-20s %-20s %-20s" % (
            sentence['mt'][mt_index],
            pe_tokens,
            src_tokens
        )
        if sentence['mt'][mt_index] == pe_tokens:
            print(display_str)
        else:
            print(purple(display_str))
