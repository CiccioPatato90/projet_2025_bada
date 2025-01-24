from matplotlib import pyplot as plt
from matplotlib.testing.compare import calculate_rms
from pyBADA.bada4 import Bada4Aircraft
from pyBADA.bada4 import Parser as Bada4Parser
from pyBADA.bada4 import PTD
from utils.prn_parser import PRNFileParser
import seaborn as sns
from matplotlib.colors import Normalize

import numpy as np
import pandas as pd

SIGNIFICANT_DIGITS = 2

# Function to calculate RMSE between two values
def calculate_rmse_row(row):
    return np.sqrt((row["Drag_BADA"] - row["Drag_PRN"])**2)

badaVersion = "DUMMY"
allData = Bada4Parser.parseAll(badaVersion=badaVersion, filePath="reference_dummy_extracted")
print(allData)

# Create BADA Aircraft instance
AC = Bada4Aircraft(
    badaVersion=badaVersion,
    acName="Dummy-TWIN-plus",
    allData=allData,
)

file_path = "table.txt"
parser = PRNFileParser(file_path)
parser.parse_file()

# Access dataframe
print("\nData Table DRAG:")
drag_prn = parser.get_column_as_array("DRAG")
print(drag_prn)
print("\nMetadata:")
print(parser.get_metadata())

ptd = PTD(AC)
results = []
drag_bada_values = []

# Loop through parsed data to calculate drag using BADA and compare with PRN drag
for altitude, cas, drag_prn_val in zip(
    parser.get_column_as_array("WGHT"),
    parser.get_column_as_array("CAS"),
    drag_prn
):
    result = ptd.PTD_cruise_SKYCONSEIL([altitude], [30000], cas, 0)
    drag_bada_val = result[0][0]  # Extracting the value from result
    drag_bada_values.append(drag_bada_val)
    results.append((altitude, cas, drag_bada_val, drag_prn_val*10))

# Calculate and print RMSE between BADA and PRN drag values
#rmse = calculate_rmse(drag_bada_values, drag_prn)

results_df = pd.DataFrame(results, columns=["Mass", "CAS", "Drag_BADA", "Drag_PRN"])

# Apply the RMSE calculation for each row
results_df["RMSE"] = results_df.apply(calculate_rmse_row, axis=1)

results_df["Drag_BADA"] = results_df["Drag_BADA"].round(SIGNIFICANT_DIGITS)
results_df["Drag_PRN"] = results_df["Drag_PRN"].round(SIGNIFICANT_DIGITS)
results_df["RMSE"] = results_df["RMSE"].round(SIGNIFICANT_DIGITS)

results_df.to_csv("results.csv")
