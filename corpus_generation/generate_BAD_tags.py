# TODO: Proper instaler for the tools
from collections import defaultdict
import sys
sys.path.append('..')
from tools.io import read_file, purple


def check_out_of_bounds(tokens, alignments, source=True):
    """
    Checks if alignment indices our out of bounds to respect to tokens. This can
    happend as we generated the alignments with tercom but use the original raw
    files (encoding problems may lead to tokens disspearing)
    """
    assert len(tokens) == len(alignments), "Number of sentences does not macth"
    for sent_index in range(len(tokens)):

        length = len(tokens[sent_index])
        if source:
            max_index = max([x[0] for x in alignments[sent_index]])
        else:
            max_index = max([x[1] for x in alignments[sent_index]])
        if max_index >= length:
            import ipdb;ipdb.set_trace(context=50)
            raise Exception(
                "Tercom alignments and original tokens do not match."
                "Likely an enconding problem"
            )


if __name__ == '__main__':

    # Data
    src_file, mt_file, pe_file, src_pe_align_file, mt_pe_align_file = \
        sys.argv[1:]

    # Read data
    source_tokens = read_file(src_file)
    mt_tokens = read_file(mt_file)
    pe_tokens = read_file(pe_file)
    src_pe_alignments = read_file(src_pe_align_file, alignments=True)
    pe_mt_alignments = read_file(mt_pe_align_file, alignments=True)

    # Sanity Checks
    # Number of sentences matches
    num_sentences = len(source_tokens)
    assert len(mt_tokens) == num_sentences, "Number of sentences does not match"
    assert len(pe_tokens) == num_sentences, "Number of sentences does not match"
    assert len(src_pe_alignments) == num_sentences, \
        "Number of sentences does not match"
    assert len(pe_mt_alignments) == num_sentences, \
        "Number of sentences does not match"
    # fast_align alignments out-of-bounds
    check_out_of_bounds(source_tokens, src_pe_alignments, source=True)
    check_out_of_bounds(pe_tokens, src_pe_alignments, source=False)
    # tercom alignments out-of-bounds
    check_out_of_bounds(mt_tokens, pe_mt_alignments, source=False)
    check_out_of_bounds(pe_tokens, pe_mt_alignments, source=True)

    # Reorganize source-target alignments as a dict
    target2source = []
    for sent in src_pe_alignments:
        target2source_sent = defaultdict(list)
        for src_idx, pe_idx in sent:
            target2source_sent[pe_idx].append(src_idx)
        target2source.append(target2source)

    # Word + Gap Tags
    target_sentence_tags = []
    for sentence_index in range(num_sentences):
        word_tags = []
        word_deletion_indices = []
        mt_position = 0
        for pe_idx, mt_idx in pe_mt_alignments[sentence_index]:

            # Insertion / Substitution errors
            if mt_idx is None:

                # Deleted word (need to store for later)
                word_deletion_indices.append(mt_position-1)
                pass

            elif pe_idx is None:

                # Insertion error
                word_tags.append('BAD')
                mt_position += 1

            elif (
                mt_tokens[sentence_index][mt_idx] !=
                pe_tokens[sentence_index][pe_idx]
            ):

                # Substitution error
                word_tags.append('BAD')
                mt_position += 1

            else:

                # OK
                word_tags.append('OK')
                mt_position += 1

        # Insert deletion errors as gaps
        word_and_gaps_tags = []
        for index in enumerate(word_tags):
            if index in word_deletion_indices:
                word_and_gaps_tags.extend([word_tags[index], 'BAD'])
            else:
                word_and_gaps_tags.extend([word_tags[index], 'OK'])

        target_sentence_tags.append(word_and_gaps_tags)
