import sys
assert len(sys.argv[:1]) == 1, "Expected one argument"
in_file = sys.argv[1]
with open(in_file, 'r') as fid:
    for index, line in enumerate(fid.readlines()):
        print("%s\t(%.12d)" % (line.rstrip(), index))
