import glob

from scipy.optimize import minimize
import numpy as np
import pandas as pd
from utils.XML_Parser import XMLParser
from pyBADA.bada4 import PTD
from pyBADA.bada4 import Bada4Aircraft
from pyBADA.bada4 import Parser as Bada4Parser

def reinit_bada_xml():
    bada_version = "DUMMY"
    all_data = Bada4Parser.parseAll(badaVersion=bada_version, filePath="reference_dummy_extracted")
    # Create BADA Aircraft instance
    return Bada4Aircraft(
        badaVersion=bada_version,
        acName="Dummy-TWIN-plus",
        allData=all_data,
    )

def update_xml_coefficients(coefficients, tags, xml_parser):
    for tag in tags:
        xml_parser.modify_tag(tag, coefficients)

def rmse_cost_function(coefficients, tags, csv_files, xml_parser, optimise_for):
    # Update XML coefficients in XML file
    start_index = 0
    for tag in tags:
        num_elements = xml_parser.len_tags(tag)
        tag_coefficients = coefficients[start_index:start_index + num_elements]
        xml_parser.modify_tag(tag, tag_coefficients)
        start_index += num_elements

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
        drag = df["Drag_PRN"]
        isa = df["ISA"][0]
        altitude = df["Altitude"][0]

        if optimise_for == "drag":
            observed_values = df["Drag_PRN"]
            predicted_values = []
            for m, c in zip(mass, cas):
                try:
                    result = ptd.PTD_cruise_SKYCONSEIL([m], [altitude], c, isa)
                    predicted_values.append(result[0][0])
                except Exception as e:
                    print(f"Error calculating BADA drag for {file}: {e}")
                    continue  # skip to the next data point
        elif optimise_for == "fuel":
            observed_values = df["Fuel_PRN"]
            predicted_values = []
            for m, c in zip(mass, cas):
                try:
                    result = ptd.PTD_cruise_SKYCONSEIL([m], [altitude], c, isa)
                    predicted_values.append(result[1][0])
                except Exception as e:
                    print(f"Error calculating BADA fuel for {file}: {e}")
                    continue
        elif optimise_for == "joint":
            observed_drag = df["Drag_PRN"]
            observed_fuel = df["Fuel_PRN"]
            observed_thrust = df["Thrust_PRN"]
            observed_lift = df["Lift_PRN"]
            predicted_drag = []
            predicted_fuel = []
            for m, c in zip(mass, cas):
                try:
                    result = ptd.PTD_cruise_SKYCONSEIL([m], [altitude], c, isa)
                    predicted_drag.append(result[0][0])
                    predicted_fuel.append(result[1][0])
                except Exception as e:
                    print(f"Error calculating BADA values for {file}: {e}")
                    continue
            rmse_drag = np.sqrt(np.mean((np.array(predicted_drag) - np.array(observed_drag)) ** 2))
            rmse_fuel = np.sqrt(np.mean((np.array(predicted_fuel) - np.array(observed_fuel)) ** 2))
            rmse = rmse_drag + rmse_fuel
            all_rmse.append(rmse)
            continue
        elif optimise_for == "fuel_beam":
            observed_values = df["Fuel_PRN"]
            predicted_values = []
            for m, c, drag in zip(mass, cas, drag):
                try:
                    result = ptd.PTD_cruise_BEAM_SKYCONSEIL(m, altitude, c, isa, drag)
                    predicted_values.append(result)
                except Exception as e:
                    print(f"Error calculating BEAM fuel for {file}: {e}")
                    continue
        else:
            raise ValueError("Invalid mode. Choose 'drag', 'fuel', 'joint' or 'fuel_beam'.")

        rmse = np.sqrt(np.mean((np.array(predicted_values) - np.array(observed_values)) ** 2))
        all_rmse.append(rmse)

    overall_rmse = np.mean(all_rmse)  # Average RMSE across all files
    return overall_rmse  # Return the overall RMSE


def optimize_mode(optimise_for, xml_parser, csv_files):
    if optimise_for == "fuel":
        tags = ["CF/f"]
    elif optimise_for == "drag":
        tags = ["CD_clean/d"]
    elif optimise_for == "fuel_beam":
        tags = ["CF_BEAM/b"]
    else:
        raise ValueError("Invalid mode. Choose 'drag', 'fuel', or 'fuel_beam'.")

    initial_guess = xml_parser.find_tag_coefficients(tags[0])

    result = minimize(
        rmse_cost_function,
        x0=initial_guess,
        args=(tags, csv_files, xml_parser, optimise_for),
        method="BFGS",
        options={"maxiter": 200}
    )

    print(f"Mode: {optimise_for}")
    print("Optimal Coefficients:", result.x)
    print("Minimized RMSE:", result.fun)
    return result

def optimize_mode_joint(xml_parser, csv_files):
    tags = ["CD_clean/d", "CF/f"]
    initial_guess = np.concatenate([xml_parser.find_tag_coefficients(tag) for tag in tags])

    result = minimize(
        rmse_cost_function,
        x0=initial_guess,
        args=(tags, csv_files, xml_parser, "joint"),
        method="L-BFGS-B",
        options={"maxiter": 400}
    )

    print("Optimal Coefficients:")
    for i, tag in enumerate(tags):
        print(f"{tag}: {result.x[i]}")
    print("Minimized RMSE:", result.fun)
    return result

# XML Parser instance
xml_parser = XMLParser("reference_dummy_extracted/Dummy-TWIN-plus/Dummy-TWIN-plus.xml")
tags = ["CD_clean/d", "CF/f", "CF_BEAM/b"]
if True:
    csv_files = glob.glob("ptd_results/results_Altitude_*_ISA_*.csv")
    if not csv_files:
        raise FileNotFoundError("No CSV files found. Run ptd.py first.")
# else:
    # csv_files = glob.glob("ptd_results/results_Altitude_*.0_ISA_0.0.csv")

#result = optimize_mode_joint(xml_parser, csv_files)


#result_drag = optimize_mode("drag", xml_parser, csv_files)
result_fuel = optimize_mode("fuel", xml_parser, csv_files)
# result_drag = optimize_mode("drag", xml_parser, csv_files)
# result_fuel = optimize_mode("fuel", xml_parser, csv_files)
result_fuel_beam = optimize_mode("fuel_beam", xml_parser, csv_files)
