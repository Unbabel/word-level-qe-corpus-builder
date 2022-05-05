import os
import codecs
import argparse
from collections import defaultdict
from itertools import chain
from collections import Counter
from operator import itemgetter
import json
import sys


GAP_ERRORS = True
SOURCE_ERRORS = True


def read_file(file_path, alignments=False):
    with codecs.open(file_path, 'r', "utf-8") as fid:
        lines = [line.rstrip().split() for line in fid.readlines()]
    if alignments:
        alignments = []
        for sent in lines:
            alignments.append([
                tuple([
                    int(side) if side else None for side in word.split('-')
                ])
                for word in sent
            ])
        return alignments
    else:
        return lines


def check_out_of_bounds(tokens, alignments, source=True):
    """
    Checks if alignment indices our out of bounds to respect to tokens. This
    can happend as we generated the alignments with tercom but use the original
    raw files (encoding problems may lead to tokens disspearing)
    """
    assert len(tokens) == len(alignments), "Number of sentences does not macth"
    for sent_index in range(len(tokens)):
        
        length = len(tokens[sent_index])
        #try:
     
        if source: 
            max_index = max([-1 if x[0] is None else x[0] for x in  alignments[sent_index]])
        else:
            max_index = max([-1 if x[1] is None else x[1] for x in  alignments[sent_index]])
        #except:
        #    print(alignments[sent_index])
            
        if max_index >= length:
            print("Sentence Index: %d" % sent_index)
            print(tokens[sent_index])
            print(alignments[sent_index])
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
        '--in-source-tokens',
        help='One sentence per line',
        required=True,
        type=str
    )
    parser.add_argument(
        '--in-mt-tokens',
        help='One sentence per line',
        required=True,
        type=str
    )
    parser.add_argument(
        '--in-pe-tokens',
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
        required=True,
        type=str
    )
    parser.add_argument(
        '--out-target-tags',
        help='Target OK/BAD tags per sentence',
        required=True,
        type=str
    )
    parser.add_argument(
        '--fluency-rule',
        help='Rules used to determine source tags',
        choices=['ignore-shift-set', 'normal', 'missing-only'],
        type=str
    )
    args = parser.parse_args(sys_argv)

    return args


def read_data(args):

    source_tokens = read_file(args['src_tokens'])
    mt_tokens = read_file(args['mt_tokens'])
    pe_tokens = read_file(args['pe_tokens'])
    src_pe_alignments = read_file(args['pe2source'], alignments=True)
    pe_mt_alignments = read_file(args['pe_mt_alignments'], alignments=True)

    # Sanity Checks
    # Number of sentences matches
    num_sentences = len(source_tokens)
    assert len(mt_tokens) == num_sentences, \
        "Number of sentences does not match"
    assert len(pe_tokens) == num_sentences, \
        "Number of sentences does not match"
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

def get_quality_tags(source_tokens, mt_tokens, pe_tokens, pe_mt_alignments, pe2source,
                     fluency_rule=None, gaps=True):
    
    if not gaps:
        GAP_ERRORS = False

    # Word + Gap Tags
    target_tags = []
    source_tags = []
    error_detail = []
    for sentence_index in range(len(mt_tokens)):

        # Variables for this sentence
        sent_tags = []
        sent_deletion_indices = []
        source_sentence_bad_indices = set()
        error_detail_sent = []
        mt_position = 0

        # Loop over alignments. This has the length of the edit-distance aligned
        # sequences.
        for pe_idx, mt_idx in pe_mt_alignments[sentence_index]:

            if mt_idx is None:

                # Deleted word error (need to store for later)
                sent_deletion_indices.append(mt_position-1)

                if fluency_rule == 'normal' or fluency_rule == "missing-only":

                    source_positions = pe2source[sentence_index][pe_idx]
                    source_sentence_bad_indices |= set(source_positions)
                    error_type = 'deletion'

                elif fluency_rule == 'ignore-shift-set':

                    # RULE: If word exists elsewhere in the sentence do not
                    # propagate error to the source.
                    if (
                        pe_tokens[sentence_index][pe_idx] not in
                        mt_tokens[sentence_index]
                    ):
                        source_positions = pe2source[sentence_index][pe_idx]
                        source_sentence_bad_indices |= set(source_positions)
                        error_type = 'deletion'
                    else:
                        source_positions = None
                        error_type = 'deletion (shift)'

                else:
                    raise Exception("Uknown rule %s" % fluency_rule)

                # Store error detail
                error_detail_sent.append({
                    'type': error_type,
                    'gap_position': mt_position-1,
                    'target_position': mt_idx,
                    'source_positions': source_positions,
                })

            elif pe_idx is None:

                # Insertion error
                sent_tags.append('BAD')
                mt_position += 1

                # Store error detail
                error_detail_sent.append({
                    'type': 'insertion',
                    'target_position': mt_idx,
                    'source_positions': None,
                })

            elif (
                mt_tokens[sentence_index][mt_idx] !=
                pe_tokens[sentence_index][pe_idx]
            ):

                # Substitution error
                sent_tags.append('BAD')
                mt_position += 1

                source_positions = None

                # Aligned words in the source are BAD
                # RULE: If word exists elsewhere in the sentence do not
                # propagate error to the source.
                if fluency_rule == 'normal':

                    source_positions = pe2source[sentence_index][pe_idx]
                    source_sentence_bad_indices |= set(source_positions)
                    error_type = 'substitution'

                elif fluency_rule == 'ignore-shift-set':

                    # RULE: If word exists elsewhere in the sentence do not
                    # propagate error to the source.
                    if (
                        pe_tokens[sentence_index][pe_idx] not in
                        mt_tokens[sentence_index]
                    ):
                        source_positions = pe2source[sentence_index][pe_idx]
                        source_sentence_bad_indices |= set(source_positions)
                        error_type = 'substitution'
                    else:
                        source_positions = None
                        error_type = 'substitution (shift)'

                elif fluency_rule == 'missing-only':

                    source_positions = None
                    error_type = 'substitution'

                else:
                    raise Exception("Uknown rule %s" % fluency_rule)



                # Store error detail
                error_detail_sent.append({
                    'type': error_type,
                    'target_position': mt_idx,
                    'source_positions': source_positions,
                })

            else:

                # OK
                sent_tags.append('OK')
                mt_position += 1

        # Insert deletion errors as gaps
        if GAP_ERRORS:
            word_and_gaps_tags = []

            # Add starting OK/BAD
            if -1 in sent_deletion_indices:
                word_and_gaps_tags.append('BAD')
            else:
                word_and_gaps_tags.append('OK')

            # Add rest of OK/BADs
            for index, tag in enumerate(sent_tags):
                if index in sent_deletion_indices:
                    word_and_gaps_tags.extend([tag, 'BAD'])
                else:
                    word_and_gaps_tags.extend([tag, 'OK'])
            target_tags.append(word_and_gaps_tags)
        else:
            target_tags.append(sent_tags)

        # Convert BAD source indices into indices
        source_sentence_bad_tags = \
            ['OK'] * len(source_tokens[sentence_index])
        for index in list(source_sentence_bad_indices):
            source_sentence_bad_tags[index] = 'BAD'
        source_tags.append(source_sentence_bad_tags)

        #
        error_detail.append(error_detail_sent)
    print(mt_tokens[1])
    print(target_tags[1])
    print(len(mt_tokens[1]))
    print(len(target_tags[1]))
    # Basic sanity checks
    if GAP_ERRORS:
        assert all(
            [len(aa)*2 + 1 == len(bb) for aa, bb in zip(mt_tokens, target_tags)]
        ), "tag creation failed"
        assert all(
            [len(aa) == len(bb) for aa, bb in zip(source_tokens, source_tags)]
        ), "tag creation failed"
    else:
        assert all(
            [len(aa) == len(bb) for aa, bb in zip(mt_tokens, target_tags)]
        ), "tag creation failed"
        assert all(
            [len(aa) == len(bb) for aa, bb in zip(source_tokens, source_tags)]
        ), "tag creation failed"

    return source_tags, target_tags, error_detail


def write_tags(output_file, tags):
    with open(output_file, 'w') as fid:
        for sent_tags in tags:
            tags_line = " ".join(sent_tags)
            fid.write("%s\n" % tags_line)


def write_error_detail(output_file, error_detail):
    with open(output_file, 'w') as fid:
        for error_sent in error_detail:
            fid.write("%s\n" % json.dumps(error_sent))


def generate_bad_ok_tags(fsrc_tokens, fmt_tokens, fpe_tokens, fpe_mt_alignments, fpe2source, fluency_rule, out_source_tags, out_target_tags, gaps):
   # GET TAGS FOR SOURCE AND TARGET
    sargs= {}
    sargs['src_tokens']=fsrc_tokens
    sargs['mt_tokens']=fmt_tokens
    sargs['pe_tokens']=fpe_tokens
    sargs['pe_mt_alignments']=fpe_mt_alignments
    sargs['pe2source']=fpe2source
    sargs['fluency_rule']=fluency_rule
    sargs['gaps']=gaps

    (
        source_tokens,
        mt_tokens,
        pe_tokens,
        pe2source,
        pe_mt_alignments
    ) = read_data(sargs)
    print('data parsed properly')
    
    source_tags, target_tags, error_detail = get_quality_tags(
        source_tokens,
        mt_tokens,
        pe_tokens,
        pe_mt_alignments,
        pe2source,
        fluency_rule=fluency_rule,
        gaps=gaps
    )

    # Store a more details summary of errors
    error_detail_flat = list(chain.from_iterable(error_detail))
    print(Counter(map(itemgetter('type'), error_detail_flat)))
    dirname = os.path.dirname(out_source_tags)
    basename = os.path.basename(out_source_tags).split('.')[0]
    error_detail_json = "%s/%s.json" % (dirname, basename)
    write_error_detail(error_detail_json, error_detail)
    print("Wrote %s" % error_detail_json)

    # WRITE DATA
    write_tags(out_source_tags, source_tags)
    print("Wrote %s" % out_source_tags)
    write_tags(out_target_tags, target_tags)
    print("Wrote %s" % out_target_tags)

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
    print('data parsed properly')

    # GET TAGS FOR SOURCE AND TARGET
    source_tags, target_tags, error_detail = get_quality_tags(
        source_tokens,
        mt_tokens,
        pe_tokens,
        pe_mt_alignments,
        pe2source,
        fluency_rule=args.fluency_rule
    )

    # Store a more details summary of errors
    error_detail_flat = list(chain.from_iterable(error_detail))
    print(Counter(map(itemgetter('type'), error_detail_flat)))
    dirname = os.path.dirname(args.out_source_tags)
    basename = os.path.basename(args.out_source_tags).split('.')[0]
    error_detail_json = "%s/%s.json" % (dirname, basename)
    write_error_detail(error_detail_json, error_detail)
    print("Wrote %s" % error_detail_json)

    # WRITE DATA
    write_tags(args.out_source_tags, source_tags)
    print("Wrote %s" % args.out_source_tags)
    write_tags(args.out_target_tags, target_tags)
    print("Wrote %s" % args.out_target_tags)
