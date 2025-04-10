import glob
import os

import numpy as np
import pandas as pd

from pyBADA.bada4 import Bada4Aircraft, Parser as Bada4Parser, PTD
from utils.regex_parser import extract_altitude_and_isa

# Constants
SIGNIFICANT_DIGITS = 2
BADA_VERSION = "DUMMY"
INPUT_DIR = "ptd_inputs"
OUTPUT_DIR = "ptd_results"

# Functions
def calculate_rmse(value1, value2):
    """Calculate RMSE between two values."""
    return round(np.sqrt((value1 - value2)**2), SIGNIFICANT_DIGITS)

def calculate_relative_error(value1, value2):
    """Calculate relative error between two values."""
    relative_error = abs(((value1 - value2) / value1) * 100)
    return round(relative_error, 2 - len(str(int(abs(relative_error)))))

# Initialize BADA Aircraft
allData = Bada4Parser.parseAll(badaVersion=BADA_VERSION, filePath="reference_dummy_extracted")
AC = Bada4Aircraft(badaVersion=BADA_VERSION, acName="Dummy-TWIN-plus", allData=allData)

# Prepare for output
os.makedirs(OUTPUT_DIR, exist_ok=True)
csv_files = glob.glob(f"{INPUT_DIR}/*.csv")
ptd = PTD(AC)

# Processing CSV files
for file_path in csv_files:
    print(f"Processing: {file_path}")
    try:
        df = pd.read_csv(file_path)
        results = []

        for _, row in df.iterrows():
            mass = row["WGHT (KG)"]
            altitude = row["Altitude"]
            isa = row["ISA TEMP (C)"]
            cas = row["CAS (KT)"]
            roll = row["ALPH (DEG)"]
            mach = row["MACH"]
            drag_prn_val = row["DRAG (DAN)"]
            fuel_prn_val = row["WFE (KG/H)"]

            try:
                result = ptd.PTD_cruise_SKYCONSEIL([mass], [altitude], cas, isa)
                result_BEAM = ptd.PTD_cruise_BEAM_SKYCONSEIL(mass, altitude, cas, isa, 0, 0, mach)
                drag_bada_val = result[0][0]
                fuel_bada_val = result[1][0]
                fuel_beam_val = result_BEAM

                results.append([
                    altitude, isa, mass, cas, mach, 0,
                    drag_bada_val, drag_prn_val * 10, fuel_bada_val, fuel_beam_val, fuel_prn_val
                ])

            except Exception as e:
                print(f"PTD Error: {e} for mass={mass}, cas={cas} in {file_path}")
                continue

        # Create results DataFrame
        results_df = pd.DataFrame(results, columns=[
            "Altitude", "ISA", "Mass", "CAS", "Mach", "Roll",
            "Drag_BADA", "Drag_PRN", "Fuel_BADA", "Fuel_BEAM", "Fuel_PRN"
        ])

        # Calculate RMSE and Relative Errors
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
        output_file_path = os.path.join(OUTPUT_DIR, f"results_{base_name}")
        results_df.to_csv(output_file_path, index=False)
        print(f"Results saved to: {output_file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
