# TODO: Proper instaler for the tools
import argparse
from collections import defaultdict
import sys
sys.path.append('..')
from qe_tools.io import read_file, purple


GAP_ERRORS = True
SOURCE_ERRORS = True

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
            raise Exception(
                "Tercom alignments and original tokens do not match."
                "Likely an enconding problem"
            )


def parse_arguments(sys_argv):

    parser = argparse.ArgumentParser(
        prog='New word-level tags version 0.0.1'
    )
    # Arguments defining a time slice
    parser.add_argument(
        '--in-source-segments',
        help='One sentence per line',
        required=True,
        type=str
    )
    parser.add_argument(
        '--in-mt-segments',
        help='One sentence per line',
        required=True,
        type=str
    )
    parser.add_argument(
        '--in-pe-segments',
        help='One sentence per line',
        required=True,
        type=str
    )
    parser.add_argument(
        '--in-source-pe-alignments',
        help='Fast align format',
        required=True,
        type=str
    )
    parser.add_argument(
        '--in-pe-mt-alignments',
        help='Fast align format, deletions insertions as empty index',
        required=True,
        type=str
    )

    # OUTPUTS
    parser.add_argument(
        '--out-source-tags',
        help='Source OK/BAD tags per sentence',
        type=str
    )
    parser.add_argument(
        '--out-target-tags',
        help='Target OK/BAD tags per sentence',
        required=True,
        type=str
    )
    args = parser.parse_args(sys_argv)

    if SOURCE_ERRORS:
        assert args.out_source_tags, "--out-source-tags required"

    return args


def read_data(args):

    source_tokens = read_file(args.in_source_segments)
    mt_tokens = read_file(args.in_mt_segments)
    pe_tokens = read_file(args.in_pe_segments)
    src_pe_alignments = read_file(args.in_source_pe_alignments, alignments=True)
    pe_mt_alignments = read_file(args.in_pe_mt_alignments, alignments=True)

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
    pe2source = []
    for sent in src_pe_alignments:
        pe2source_sent = defaultdict(list)
        for src_idx, pe_idx in sent:
            pe2source_sent[pe_idx].append(src_idx)
        pe2source.append(pe2source_sent)

    return (
        source_tokens, mt_tokens, pe_tokens, pe2source, pe_mt_alignments
    )


def get_quality_tags(mt_tokens, pe_tokens, pe_mt_alignments, pe2source):

    # Word + Gap Tags
    target_tags = []
    source_tags = []
    for sentence_index in range(len(mt_tokens)):

        # Variables for this sentence
        sent_tags = []
        sent_deletion_indices = []
        source_sentence_bad_indices = set()
        mt_position = 0

        for pe_idx, mt_idx in pe_mt_alignments[sentence_index]:

            if mt_idx is None:

                # Deleted word error (need to store for later)
                sent_deletion_indices.append(mt_position-1)

                if SOURCE_ERRORS:
                    # Aligned words in the source are BAD
                    source_sentence_bad_indices |= \
                        set(pe2source[sentence_index][pe_idx])

            elif pe_idx is None:

                # Insertion error
                sent_tags.append('BAD')
                mt_position += 1

            elif (
                mt_tokens[sentence_index][mt_idx] !=
                pe_tokens[sentence_index][pe_idx]
            ):

                # Substitution error
                sent_tags.append('BAD')
                mt_position += 1

                if SOURCE_ERRORS:
                    # Aligned words in the source are BAD
                    source_sentence_bad_indices |= \
                        set(pe2source[sentence_index][pe_idx])

            else:

                # OK
                sent_tags.append('OK')
                mt_position += 1

        # Insert deletion errors as gaps
        if GAP_ERRORS:
            word_and_gaps_tags = []
            for index, tag in enumerate(sent_tags):
                if index in sent_deletion_indices:
                    word_and_gaps_tags.extend([tag, 'BAD'])
                else:
                    word_and_gaps_tags.extend([tag, 'OK'])
            target_tags.append(word_and_gaps_tags)
        else:
            target_tags.append(sent_tags)

        if SOURCE_ERRORS:
            # Convert BAD source indices into indices
            source_sentence_bad_tags = \
                ['OK'] * len(source_tokens[sentence_index])
            for index in list(source_sentence_bad_indices):
                source_sentence_bad_tags[index] = 'BAD'
            source_tags.append(source_sentence_bad_tags)

    # Basic sanity checks
    assert all(
        [len(aa)*2 == len(bb) for aa, bb in zip(mt_tokens, target_tags)]
    ), "tag creation failed"
    assert all(
        [len(aa) == len(bb) for aa, bb in zip(source_tokens, source_tags)]
    ), "tag creation failed"

    return source_tags, target_tags


def write_tags(output_file, tags):
    with open(output_file, 'w') as fid:
        for sent_tags in tags:
            tags_line = " ".join(sent_tags)
            fid.write("%s\n" % tags_line)


if __name__ == '__main__':

    # ARGUMENT HANDLING
    args = parse_arguments(sys.argv[1:])

    # READ DATA AND CHECK INTEGRITY
    (
        source_tokens,
        mt_tokens,
        pe_tokens,
        pe2source,
        pe_mt_alignments
    ) = read_data(args)


    # GET TAGS FOR SOURCE AND TARGET
    source_tags, target_tags = get_quality_tags(
        mt_tokens,
        pe_tokens,
        pe_mt_alignments,
        pe2source
    )

    # WRITE DATA
    if SOURCE_ERRORS:
        write_tags(args.out_source_tags, source_tags)
    write_tags(args.out_target_tags, target_tags)
