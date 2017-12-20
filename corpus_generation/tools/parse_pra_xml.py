from __future__ import generators
from xml.dom.minidom import parse, parseString
import argparse
import re

"""
parse ter xml output
"""

class Edit:
    def __init__(self, before, after, operation):
        #xml switches hyps and refs
        self.h = after
        self.r = before
        self.o = switch_ops(operation)

    def __str__(self):
        return "%s/%s/%s" % (self.h, self.r, self.o)

def switch_ops(op):
    switch_dict = {"C":"C", "D":"I", "I":"D", "S":"S"}
    return switch_dict[op]

def KnuthMorrisPratt(text, pattern):

    '''Yields all starting positions of copies of the pattern in the text.
Calling conventions are similar to string.find, but its arguments can be
lists or iterators, not just strings, it returns all matches, not just
the first one, and it does not need the whole text in memory at once.
Whenever it yields, it will have read the text exactly up to and including
the match that caused the yield.'''
    # Knuth-Morris-Pratt string matching
    # David Eppstein, UC Irvine, 1 Mar 2002

    # allow indexing into pattern and protect against change during yield
    pattern = list(pattern)

    # build table of shift amounts
    shifts = [1] * (len(pattern) + 1)
    shift = 1
    for pos in range(len(pattern)):
        while shift <= pos and pattern[pos] != pattern[pos-shift]:
            shift += shifts[pos-shift]
        shifts[pos+1] = shift

    # do the actual search
    startPos = 0
    matchLen = 0
    for c in text:
        while matchLen == len(pattern) or \
              matchLen >= 0 and pattern[matchLen] != c:
            startPos += shifts[matchLen]
            matchLen -= shifts[matchLen]
        matchLen += 1
        if matchLen == len(pattern):
            yield startPos

def mark_matches(list, seq, matches, sep_start, sep_end):
    offset = 0
    for m in matches: #start index of match
        start = offset+m
        list.insert(start, sep_start)
        end = start+len(seq)+1
        list.insert(end, sep_end)
        offset += 2
    return list

def edits2str(edits):
    """
    get a printable representation for a list of edits
    """
    output_str = [edit.__str__() for edit in edits]
    return output_str

def parse_file(filepath):
    """
    parse the xml tree, extracting hypotheses, their references and their edits
    """

    dom = parse(filepath)
    hyp_elems = dom.getElementsByTagName("hyp")
    hyps = list() #list of list of tokens
    refs = list() #list of list of tokens
    hyps_edits = list() #list of list of edits
    hters = list() #list of HTER scores
    for hyp_edits in hyp_elems:
        hyp = list()
        ref = list()
        h_edits = list()
        hter = float(hyp_edits.attributes["num_errs"].value)/float(hyp_edits.attributes["wrd_cnt"].value)
        for edits in hyp_edits.childNodes:
            edit_list = edits.data.split()
            for edit in edit_list:
                trimmed_edit = edit.strip()
                m = re.findall(r'^(".*"),(".*"),(.*),(.*)$', trimmed_edit)
                assert len(m) == 1 and len(m[0]) == 4
                splitted = list(m[0])
                word_ref = splitted[0].strip('"')
                word_hyp = splitted[1].strip('"')
                error_type = splitted[2]
                # print word_hyp, word_ref, error_type
                hyp.append(word_hyp)
                ref.append(word_ref)
                h_edits.append(Edit(word_hyp, word_ref, error_type))
        assert len(hyp) == len(ref)
        hyps.append(hyp)
        refs.append(ref)
        hyps_edits.append(h_edits)
        hters.append(hter)
    return hyps, refs, hyps_edits, hters

def get_tags(hyps_edits, tags_map, keep_inserts):
    """
    from the edits, generate the sequence of tags
    """
    tags = list()
    for hyp_edit in hyps_edits:
        operation = hyp_edit.o
        if operation=="I":
            if not keep_inserts:
                continue
            else:
                tag = tags_map[operation]
                tags.append(tag)
        else:
            tag = tags_map[operation]
            tags.append(tag)
    return tags

def dict2table(freq, freq_dist):
    table_str = ""
    sep = "|"
    table_str += "%s %s %s %s %s\n" % ("k", sep, "matches", sep, "distinct sents.")
    table_str += "-"*20+"\n"
    for k in freq.keys():
        table_str += "%d %s %d %s %d\n" % (k, sep, freq[k], sep, freq_dist[k])
    return table_str

def get_unks(hyps_edits):
    """
    replace the words in the pe that have been inserted as new lexical items
    """
    #FIXME: first just all inserts, without checking if they occur else-where
    pe_unks = list()
    for hyp_edit in hyps_edits:
        if hyp_edit.o == "I":
            pe_unks.append("UNK")
        else:
            pe_unks.append(hyp_edit.r)
    return pe_unks

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-tercom_file', type=str, required=True)
    parser.add_argument('-fine_grained', action='store_true')
    parser.add_argument('-keep_inserts', action='store_true')
    parser.add_argument('-k', type=int)
    parser.add_argument('-j', type=int)
    args = vars(parser.parse_args())
    filepath = args['tercom_file']
    fine_grained = args['fine_grained']
    keep_inserts = args['keep_inserts']
    k = args['k']
    jj = args['j']
    if jj is None:
        jj = 1
    print "fine grained?", fine_grained
    print "keep inserts?", keep_inserts
    if fine_grained:
        tags_map = {'C': 'OK', 'S': 'BAD_SUB', 'I': 'BAD_INS', 'D': 'BAD_DEL'}
    else:
        tags_map = {'C': 'OK', 'S': 'BAD', 'I': 'BAD', 'D': 'BAD'}
    hyps, refs, hyps_edits, hters = parse_file(filepath)

    print "analysis for up to k=%d" % k

    j_freq = {}
    j_dist_freq = {}
    num_examples = 1
    for j in xrange(1,k+1):
        print "j=%d" % jj
        k_seq = j*["BAD_SUB"]
        j_seq = jj*["BAD_INS"]
        seq = ["OK"]+j_seq+k_seq+["OK"]
        sep_start = "["
        sep_end = "]"
        i = 0
        mc = 0
        matches_sum = 0
        matches_sents_sum = 0 #count distinct sentences
        for i in xrange(len(hyps)):
            hyp = hyps[i]
            #print " ".join(hyp)
            ref = refs[i]
            #print " ".join(ref)
            edits = edits2str(hyps_edits[i])
            #print " ".join(edits)
            tags = get_tags(hyps_edits[i], tags_map, keep_inserts)
            #print " ".join(tags)
            tags_unks = get_unks(hyps_edits[i])
            #print " ".join(tags_unks)
            matches = [m for m in KnuthMorrisPratt(tags, seq)]
            if len(matches) >= 1:
                matches_sum += len(matches)
                matches_sents_sum +=1
                if mc < num_examples: #only print this many examples
                    print "\n\t%d" % i
                    hyp_marked = mark_matches(hyp, seq, matches, sep_start, sep_end) 
                    ref_marked = mark_matches(ref, seq, matches, sep_start, sep_end)
                    tags_marked = mark_matches(tags, seq, matches, sep_start, sep_end)   
                    print "\t", " ".join(hyp_marked)
                    print "\t", " ".join(ref_marked)
                    print "\t", " ".join(tags_marked)
                    mc+=1
            i+=1
        print "%d cases of pattern for k=%d, j=%d matches in %d distinct sentences %s" % (matches_sum, j, jj, matches_sents_sum, str(seq))
        j_freq[j] = matches_sum
        j_dist_freq[j] = matches_sents_sum

        print "modified words: %d" % (j+jj)
    print dict2table(j_freq, j_dist_freq)

