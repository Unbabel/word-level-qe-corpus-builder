import sys
from xml.sax.saxutils import escape
assert len(sys.argv[:1]) == 1, "Expected one argument"
in_file = sys.argv[1]
with open(in_file, 'r') as fid:
    for index, line in enumerate(fid.readlines()):
        # Note that HTML compatible scaping is needed
        line = escape(line)
        print("%s\t(%.12d)" % (line.rstrip(), index))
