import glob

from scipy.optimize import minimize
import numpy as np
import pandas as pd
from utils.XML_Parser import XMLParser
from pyBADA.bada4 import PTD
from pyBADA.bada4 import Bada4Aircraft
from pyBADA.bada4 import Parser as Bada4Parser

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

        mass = df["Mass"]
        cas = df["CAS"]
        drag_prn = df["Drag_PRN"]
        isa = df["ISA"][0]
        altitude = df["Altitude"][0]

        drag_bada_updated = []

        for m, c in zip(mass, cas):
            try:
                result = ptd.PTD_cruise_SKYCONSEIL([m], [altitude], c, isa)
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
if True:
    csv_files = glob.glob("ptd_results/results_Altitude_*_ISA_*.csv")
    if not csv_files:
        raise FileNotFoundError("No CSV files found. Run generate_ptd_inputs.py first.")
else:
    csv_files = glob.glob("ptd_results/results_Altitude_*.0_ISA_0.0.csv")

# Minimize RMSE
result = minimize(
    rmse_cost_function,
    x0=initial_guess,
    args=(tags, csv_files, xml_parser),
    method="BFGS",
    options={"maxiter": 100}
)

# Extract optimal coefficients
optimal_coefficients = result.x
print("Optimal Coefficients:", optimal_coefficients)

# Print minimized RMSE
print("Minimized RMSE:", result.fun)