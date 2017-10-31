import codecs


def purple(word):
    return "\033[35m%s\033[0m" % word


def read_file(file_path, alignments=False):
    with codecs.open(file_path, 'r', "utf-8") as fid:
        lines = [line.rstrip().split() for line in fid.readlines()]
    if alignments:
        alignments = []
        for sent in lines:
            alignments.append([
                tuple([int(side) if side else None for side in word.split('-')])
                for word in sent
            ])
        return alignments
    else:
        return lines
