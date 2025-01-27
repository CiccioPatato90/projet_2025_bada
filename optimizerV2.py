from scipy.optimize import minimize
import numpy as np
import pandas as pd
from utils.prn_parser import PRNFileParser
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

def rmse_cost_function(coefficients, tags, mass, cas_list, drag_prn, xml_parser):
    # Update XML coefficients in XML file
    update_xml_coefficients(coefficients, tags, xml_parser)

    # Reload the BADA model with updated coefficients
    ac = reinit_bada_xml()
    ptd = PTD(ac)

    drag_bada_updated = []
    for m, c in zip(mass, cas):
        # Recalculate Drag_BADA using the updated coefficients
        result = ptd.PTD_cruise_SKYCONSEIL([m], [30000], c, 0)  # Example usage
        drag_bada_updated.append(result[0][0])

    # Calculate RMSE
    rmse = np.sqrt(np.mean((np.array(drag_bada_updated) - np.array(drag_prn))**2))
    return rmse

# We start by heuristics only on CD coefficients
# XML Parser instance
xml_parser = XMLParser("reference_dummy_extracted/Dummy-TWIN-plus/Dummy-TWIN-plus.xml")
tags = ["CD_clean/d"]
initial_guess = xml_parser.find_tag_coefficients(tags[0])

results_df = pd.read_csv("results.csv")
# Prepare data (replace with actual data from your application)
mass_list = results_df["Mass"].to_numpy()
cas = results_df["CAS"].to_numpy()
drag_prn = results_df["Drag_PRN"].to_numpy()

# Minimize RMSE
if True:
    result = minimize(
        rmse_cost_function,
        x0=initial_guess,
        args=(tags, mass_list, cas, drag_prn, xml_parser),
        method="BFGS",
        options={"maxiter": 10000}  # Maximum iterations
    )
else:
    from scipy.optimize import basinhopping
    result = basinhopping(
        rmse_cost_function,
        x0=initial_guess,
        minimizer_kwargs={
            "args": (tags, mass_list, cas, drag_prn, xml_parser),
            "method": "BFGS"
        },
        niter=100  # Number of random jumps
    )

# Extract optimal coefficients
optimal_coefficients = result.x
print("Optimal Coefficients:", optimal_coefficients)

# Print minimized RMSE
print("Minimized RMSE:", result.fun)