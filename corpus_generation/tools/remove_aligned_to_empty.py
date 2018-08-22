import codecs
import sys
import subprocess


def file_len(fname):
    """
    From https://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python#1019572
    """
    p = subprocess.Popen(
        ['wc', '-l', fname],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])


if __name__ == '__main__':

    in_source_file, in_target_file, out_paralel_corpus = sys.argv[1:]

    nr_lines = file_len(in_source_file)
    nr_lines2 = file_len(in_target_file)
    assert nr_lines == nr_lines2, \
        "Number of lines in %s and %s do not match" % (
            in_source_file,
            in_target_file
        )

    with codecs.open(in_source_file, 'r', 'utf-8') as source_fid:
        with codecs.open(in_target_file, 'r', 'utf-8') as target_fid:
            with codecs.open(out_paralel_corpus, 'w', 'utf-8') as paralel_fid:
                faulty_lines = 0
                for line_n in xrange(nr_lines2):

                    source_line = source_fid.readline().strip()
                    target_line = target_fid.readline().strip()

                    if len(source_line) and len(target_line):
                        paralel_fid.write(
                            " ||| ".join([source_line, target_line])
                            + "\n"
                        )
                    else:
                        faulty_lines += 1

    print("%d faulty lines" % faulty_lines)
