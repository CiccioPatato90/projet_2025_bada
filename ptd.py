import glob
import os

from pyBADA.bada4 import Bada4Aircraft
from pyBADA.bada4 import Parser as Bada4Parser
from pyBADA.bada4 import PTD


import numpy as np
import pandas as pd

from utils.regex_parser import extract_altitude_and_isa

SIGNIFICANT_DIGITS = 2

# Function to calculate RMSE between two values
def calculate_rmse_row(row, value1, value2):
    return np.sqrt((row[value1] - row[value2])**2)

def calculate_rmse(value1, value2):
    return round(np.sqrt((value1 - value2)**2), SIGNIFICANT_DIGITS)

# Function to calculate Relative Error Percentage between two values (value1 - value2) / value1 --> ADD AS OUTPUT METRIC
def calculate_relative_error_row(row, value1, value2):
    relative_error = ((row[value1] - row[value2]) / row[value1]) * 100
    return round(relative_error, 2 - len(str(int(abs(relative_error)))))

def calculate_relative_error(value1, value2):
    relative_error = abs(((value1 - value2) / value1) * 100)
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
        # here we use the regex since it's the only reference we have from input file
        altitude_extracted, isa_extracted = extract_altitude_and_isa(file_path)

        for _, row in df.iterrows():
            mass = row["WGHT (KG)"]
            cas = row["CAS (KT)"]
            drag_prn_val = row["DRAG (DAN)"]
            fuel_prn_val = row["WFE (KG/H)"]

            try:
                result = ptd.PTD_cruise_SKYCONSEIL([mass], [altitude_extracted], cas, isa_extracted)
                result_BEAM = ptd.PTD_cruise_BEAM_SKYCONSEIL(mass, altitude_extracted, cas, isa_extracted, drag_prn_val * 10)
                fuel_beam_val = result_BEAM

                drag_bada_val = result[0][0]
                fuel_bada_val = result[1][0]
                results.append([altitude_extracted, isa_extracted, mass, cas, drag_bada_val, drag_prn_val * 10, fuel_bada_val, fuel_beam_val, fuel_prn_val])
            except Exception as e:
                print(f"PTD Error: {e} for mass={mass}, cas={cas} in {file_path}")
                continue
        # from now on hte ISA is accessible from the ptd_results.csv file
        results_df = pd.DataFrame(results, columns=["Altitude", "ISA","Mass", "CAS", "Drag_BADA", "Drag_PRN", "Fuel_BADA", "Fuel_BEAM", "Fuel_PRN"])

        results_df["RMSE_Drag"] = results_df.apply(
            lambda row: calculate_rmse(row["Drag_BADA"], row["Drag_PRN"]), axis=1
        )

        results_df["RelativeError_Drag"] = results_df.apply(
            lambda row: calculate_relative_error(row["Drag_BADA"], row["Drag_PRN"]), axis=1
        )
        results_df["RMSE_Fuel"] = results_df.apply(
            lambda row: calculate_rmse(row["Fuel_BADA"], row["Fuel_PRN"]), axis=1
        )

        results_df["RelativeError_Fuel"] = results_df.apply(
            lambda row: calculate_relative_error(row["Fuel_BADA"], row["Fuel_PRN"]), axis=1
        )

        results_df["RMSE_Fuel_BEAM"] = results_df.apply(
            lambda row: calculate_rmse(row["Fuel_BEAM"], row["Fuel_PRN"]), axis=1
        )

        results_df["RelativeError_Fuel_BEAM"] = results_df.apply(
            lambda row: calculate_relative_error(row["Fuel_BEAM"], row["Fuel_PRN"]), axis=1
        )

        # Save results
        base_name = os.path.basename(file_path)
        output_file_path = os.path.join(output_dir, f"results_{base_name}")
        results_df.to_csv(output_file_path, index=False)
        print(f"Results saved to: {output_file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")