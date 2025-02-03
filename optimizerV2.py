import glob

from scipy.optimize import minimize
import numpy as np
import pandas as pd
from utils.XML_Parser import XMLParser
from pyBADA.bada4 import PTD
from pyBADA.bada4 import Bada4Aircraft
from pyBADA.bada4 import Parser as Bada4Parser

# TODO:
# - STUDY SOLUTION SPACE:
#   - Normalize coefficients in fixed range and then convert them back
#   - Vary one coefficient at a time around its initial value to see how it affects RMSE
#   - Same as above but 2 coefficients at a time
#   - Study potential correlation between coefficients
#   - Try to understand the physics behind it and rethink cost function
#   - (VAL1 - VAL2) / VAL1 --> ADD AS OUTPUT METRIC
#   - Try to show min/max error, change CF


def reinit_bada_xml():
    badaVersion = "DUMMY"
    allData = Bada4Parser.parseAll(badaVersion=badaVersion, filePath="reference_dummy_extracted")
    # Create BADA Aircraft instance
    return Bada4Aircraft(
        badaVersion=badaVersion,
        acName="Dummy-TWIN-plus",
        allData=allData,
    )

def update_xml_coefficients(coefficients, tags, xml_parser):
    #dict_of_values = {tags[i]: [coefficients[i]] * xml_parser.len_tags(tags[i]) for i in range(len(tags))}
    for tag in tags:
        xml_parser.modify_tag(tag, coefficients)

def rmse_cost_function(coefficients, tags, csv_files, xml_parser):
    # Update XML coefficients in XML file
    update_xml_coefficients(coefficients, tags, xml_parser)

    # Reload the BADA model with updated coefficients
    ac = reinit_bada_xml()
    ptd = PTD(ac)

    all_rmse = []  # To store RMSE for each table

    for file in csv_files:  # Loop through CSV files
        df = pd.read_csv(file)
        if df.empty:
            print(f"WARNING: DataFrame for {file} is empty!")
            continue  # skip to the next file

        mass = df["Mass"].to_numpy()
        cas = df["CAS"].to_numpy()
        drag_prn = df["Drag_PRN"].to_numpy()

        drag_bada_updated = []
        for m, c in zip(mass, cas):
            try:
                result = ptd.PTD_cruise_SKYCONSEIL([m], [30000], c, 0)
                drag_bada_updated.append(result[0][0])
            except Exception as e:
                print(f"Error calculating BADA drag for {file}: {e}")
                continue  # skip to the next data point

        rmse = np.sqrt(np.mean((np.array(drag_bada_updated) - np.array(drag_prn)) ** 2))
        all_rmse.append(rmse)

    overall_rmse = np.mean(all_rmse)  # Average RMSE across all files
    return overall_rmse  # Return the overall RMSE

# We start by heuristics only on CD coefficients
# XML Parser instance
xml_parser = XMLParser("reference_dummy_extracted/Dummy-TWIN-plus/Dummy-TWIN-plus.xml")
tags = ["CD_clean/d"]
initial_guess = xml_parser.find_tag_coefficients(tags[0])

csv_files = glob.glob("ptd_results/results_Altitude_*_ISA_*.csv")
if not csv_files:
    raise FileNotFoundError("No CSV files found. Run tmp.py first.")

# Minimize RMSE
if True:
    result = minimize(
        rmse_cost_function,
        x0=initial_guess,
        args=(tags, csv_files, xml_parser),  # Pass csv_files
        method="BFGS",
        options={"maxiter": 10000}
    )
else:
    from scipy.optimize import basinhopping
    result = basinhopping(
        rmse_cost_function,
        x0=initial_guess,
        minimizer_kwargs={
            "args": (tags, csv_files, xml_parser),  # Pass csv_files
            "method": "BFGS"
        },
        niter=100
    )

# Extract optimal coefficients
optimal_coefficients = result.x
print("Optimal Coefficients:", optimal_coefficients)

# Print minimized RMSE
print("Minimized RMSE:", result.fun)