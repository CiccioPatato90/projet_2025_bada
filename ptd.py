import glob
import os

from matplotlib import pyplot as plt
from pyBADA.bada4 import Bada4Aircraft
from pyBADA.bada4 import Parser as Bada4Parser
from pyBADA.bada4 import PTD
import seaborn as sns

import numpy as np
import pandas as pd

SIGNIFICANT_DIGITS = 2

# Function to calculate RMSE between two values
def calculate_rmse_row(row):
    return np.sqrt((row["Drag_BADA"] - row["Drag_PRN"])**2)

# Function to calculate Relative Error Percentage between two values (VAL1 - VAL2) / VAL1 --> ADD AS OUTPUT METRIC
def calculate_relative_error_row(row):
    relative_error = ((row["Drag_BADA"] - row["Drag_PRN"]) / row["Drag_BADA"]) * 100
    return round(relative_error, 2 - len(str(int(abs(relative_error)))))

badaVersion = "DUMMY"
allData = Bada4Parser.parseAll(badaVersion=badaVersion, filePath="reference_dummy_extracted")
print(allData)

# Create BADA Aircraft instance
AC = Bada4Aircraft(
    badaVersion=badaVersion,
    acName="Dummy-TWIN-plus",
    allData=allData,
)

csv_files = glob.glob("ptd_inputs/Altitude_*_ISA_*.csv")
all_results_df = pd.DataFrame()  # To store results from all files
output_dir = "ptd_results"
os.makedirs(output_dir, exist_ok=True)

ptd = PTD(AC)

for file_path in csv_files:
    print(f"Processing: {file_path}")
    try:
        df = pd.read_csv(file_path)

        results = []
        for _, row in df.iterrows():
            altitude = row["WGHT (KG)"]
            cas = row["CAS (KT)"]
            drag_prn_val = row["DRAG (DAN)"]
            try:
                result = ptd.PTD_cruise_SKYCONSEIL([altitude], [30000], cas, 0)
                drag_bada_val = result[0][0]
                results.append([altitude, cas, drag_bada_val, drag_prn_val * 10])
            except Exception as e:
                print(f"PTD Error: {e} for altitude={altitude}, cas={cas} in {file_path}")
                continue

        results_df = pd.DataFrame(results, columns=["Mass", "CAS", "Drag_BADA", "Drag_PRN"])
        results_df["RMSE"] = results_df.apply(calculate_rmse_row, axis=1)
        results_df["RelativeError"] = results_df.apply(calculate_relative_error_row, axis=1)
        base_name = os.path.basename(file_path)
        output_file_path = os.path.join(output_dir, f"results_{base_name}")
        results_df.to_csv(output_file_path, index=False)
        print(f"Results saved to: {output_file_path}")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except pd.errors.EmptyDataError:
        print(f"File is empty: {file_path}")
    except Exception as e:  # Catch other potential errors
        print(f"Error processing {file_path}: {e}")

all_results_df = pd.concat([pd.read_csv(f) for f in glob.glob("ptd_results/*.csv")], ignore_index=True)