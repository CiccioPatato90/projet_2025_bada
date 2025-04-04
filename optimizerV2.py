import glob
from scipy.optimize import minimize, differential_evolution
import numpy as np
import pandas as pd

from utils.XML_Parser import XMLParser
from pyBADA.bada4 import PTD, Bada4Aircraft, Parser as Bada4Parser

# Function Definitions
def reinit_bada_xml():
    """Reinitialize the BADA XML configuration."""
    bada_version = "DUMMY"
    all_data = Bada4Parser.parseAll(badaVersion=bada_version, filePath="reference_dummy_extracted")
    return Bada4Aircraft(
        badaVersion=bada_version,
        acName="Dummy-TWIN-plus",
        allData=all_data,
    )

def update_xml_coefficients(coefficients, tags, xml_parser):
    """Update multiple coefficients in the XML file."""
    start_index = 0
    for tag in tags:
        num_elements = xml_parser.len_tags(tag)
        tag_coefficients = coefficients[start_index:start_index + num_elements]
        xml_parser.modify_tag(tag, tag_coefficients)
        start_index += num_elements

def rmse_cost_function(coefficients, tags, csv_files, xml_parser, optimise_for):
    """Calculate the RMSE cost function based on updated XML coefficients."""
    update_xml_coefficients(coefficients, tags, xml_parser)
    ac = reinit_bada_xml()
    ptd = PTD(ac)

    all_rmse = []

    for file in csv_files:
        df = pd.read_csv(file)
        if df.empty:
            print(f"WARNING: DataFrame for {file} is empty!")
            continue

        mass, cas, roll, mach, drag = df["Mass"], df["CAS"], df["Roll"], df["Mach"], df["Drag_PRN"]
        # mass, cas, drag = df["Mass"], df["CAS"], df["Drag_PRN"]
        isa, altitude = df["ISA"][0], df["Altitude"][0]

        observed_values, predicted_values = [], []
        if optimise_for == "drag":
            observed_values = drag
            predicted_values = [
                ptd.PTD_cruise_SKYCONSEIL([m], [altitude], c, isa)[0][0] for m, c in zip(mass, cas)
            ]
        elif optimise_for == "fuel":
            observed_values = df["Fuel_PRN"]
            predicted_values = [
                ptd.PTD_cruise_SKYCONSEIL([m], [altitude], c, isa)[1][0] for m, c in zip(mass, cas)
            ]
        elif optimise_for == "fuel_beam":
            observed_values = df["Fuel_PRN"]
            predicted_values = [
                ptd.PTD_cruise_BEAM_SKYCONSEIL(m, altitude, c, isa, 0, roll, mach) for m, c in zip(mass, cas)
                # ptd.PTD_cruise_BEAM_SKYCONSEIL(m, altitude, c, isa, d) for m, c, d in zip(mass, cas, drag)
            ]
        else:
            raise ValueError("Invalid mode. Choose 'drag', 'fuel', or 'fuel_beam'.")

        rmse = np.sqrt(np.mean((np.array(predicted_values) - np.array(observed_values)) ** 2))
        all_rmse.append(rmse)

    return np.mean(all_rmse)

def optimize_mode(optimise_for, xml_parser, csv_files):
    """Optimize individual coefficients for a specific mode."""
    tags = {"fuel": ["CF/f"], "drag": ["CD_clean/d"], "fuel_beam": ["CF_BEAM/b"]}.get(optimise_for)
    if not tags:
        raise ValueError("Invalid mode. Choose 'drag', 'fuel', or 'fuel_beam'.")

    initial_guess = xml_parser.find_tag_coefficients(tags[0])

    result = minimize(
        rmse_cost_function,
        x0=initial_guess,
        args=(tags, csv_files, xml_parser, optimise_for),
        method="BFGS",
        options={"maxiter": 100}
    )

    print(f"Mode: {optimise_for}")
    print("Optimal Coefficients:", result.x)
    print("Minimized RMSE:", result.fun)
    return result

def optimize_mode_joint(optimise_for, xml_parser, csv_files):
    """Optimize multiple coefficients at the same time (joint optimization)."""
    tags = {
        "bada": ["CD_clean/d", "CF/f"],
        "fuel_beam": ["CF_BEAM/b", "CD_BEAM/d"]
    }.get(optimise_for)
    if not tags:
        raise ValueError("Invalid mode. Choose 'bada' or 'fuel_beam'.")

    initial_guess = np.concatenate([xml_parser.find_tag_coefficients(tag) for tag in tags])

    result = minimize(
        rmse_cost_function,
        x0=initial_guess,
        args=(tags, csv_files, xml_parser, optimise_for),
        method="BFGS",
        options={"maxiter": 100}
    )

    print("Optimal Coefficients:")
    start_index = 0
    for tag in tags:
        num_elements = xml_parser.len_tags(tag)
        print(f"{tag}: {result.x[start_index:start_index + num_elements]}")
        start_index += num_elements

    print("Minimized RMSE:", result.fun)
    return result

# Main Execution
xml_parser = XMLParser("reference_dummy_extracted/Dummy-TWIN-plus/Dummy-TWIN-plus.xml")
csv_files = glob.glob("ptd_results/*.csv")

if not csv_files:
    raise FileNotFoundError("No CSV files found. Run generate_ptd_inputs.py first.")

# Run optimizations
# result_drag = optimize_mode("drag", xml_parser, csv_files)
# result_fuel = optimize_mode("fuel", xml_parser, csv_files)
result_fuel_beam = optimize_mode("fuel_beam", xml_parser, csv_files)
# result_joint = optimize_mode_joint("fuel_beam", xml_parser, csv_files)
