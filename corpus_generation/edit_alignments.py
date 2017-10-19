import sys
import parse_pra_xml
assert len(sys.argv[:1]) == 1, "Expected one argument"
tercom_xml = sys.argv[1]
import ipdb;ipdb.set_trace(context=50)
parse_pra_xml.parse_file(tercom_xml)
