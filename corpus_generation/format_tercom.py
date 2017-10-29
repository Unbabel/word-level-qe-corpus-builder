import sys
from xml.sax.saxutils import escape
import codecs
assert len(sys.argv[1:]) == 2, "Expected one argument"
in_file, out_file = sys.argv[1:]

# Read
lines = []
#with open(in_file, 'r') as fid:
with codecs.open(in_file, 'r', "utf-8") as fid:
    for line in fid.readlines():
        # Note that HTML compatible scaping is needed
        lines.append(line.rstrip())

# Write
#with open(out_file, 'w') as fid:
with codecs.open(out_file, 'w', "utf-8") as fid:
    for index, line in enumerate(lines):
        # Note that HTML compatible scaping is needed
        line = escape(line)
        # We also need to scape double quotes
        line = line.replace('"','\\"')
        fid.write("%s\t(%.12d)\n" % (line, index))
