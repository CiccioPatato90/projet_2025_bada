from pyBADA.bada4 import Bada4Aircraft
from pyBADA.bada4 import Parser as Bada4Parser
from pyBADA.bada4 import PTD
from utils.prn_parser import PRNFileParser

badaVersion = "DUMMY"
allData = Bada4Parser.parseAll(badaVersion=badaVersion)
# still using Dummy XML
AC = Bada4Aircraft(
    badaVersion=badaVersion,
    acName="Dummy-TWIN-plus",
    allData=allData,
)

file_path = "table.txt"
parser = PRNFileParser(file_path)
parser.parse_file()

# Access dataframe
print("\nData Table:")
print(parser.get_column_as_array("WGHT"))
print(parser.get_column_as_array("CAS"))
print("\nMetadata:")
print(parser.get_metadata())


ptd = PTD(AC)
# rewrite this method with the custom annotations.
# 1st step: try to extract the table from .pnr file --> OK
# 2nd step: change altitudeList to massList and keep altitude fixed
#result = ptd.PTD_cruise_SKYCONSEIL(parser.get_column_as_array("WGHT"), [30000], 0)
results = {}
for altitude, cas in zip(parser.get_column_as_array("WGHT"), parser.get_column_as_array("CAS")):
    result = ptd.PTD_cruise_SKYCONSEIL([altitude], [30000], cas, 0)
    results[(altitude, cas)] = result
print(results)