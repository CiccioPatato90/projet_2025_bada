import glob
import os
import re
import pandas as pd

# Function to extract altitude and ISA from filename
def extract_altitude_and_isa(filename):
    match = re.search(r"Altitude_(\d+(\.\d+)?)_ISA_([+-]?\d+(\.\d+)?)", filename)
    if match:
        altitude = float(match.group(1))
        isa = float(match.group(3))
        return altitude, isa
    else:
        raise ValueError(f"Altitude or ISA not found in filename: {filename}")

# Get list of CSV files
csv_files = glob.glob("../ptd_inputs/Altitude_*_ISA_*.csv")

# Dictionary to store unique (Altitude, ISA) with one Mass and one WFE
unique_entries = {}

for file_path in csv_files:
    print(f"Processing: {file_path}")
    try:
        df = pd.read_csv(file_path)

        # Extract altitude and ISA from filename
        altitude, isa = extract_altitude_and_isa(file_path)

        # Rename columns if needed
        df.rename(columns={"WGHT (KG)": "Mass", "WFE (KG/H)": "WFE"}, inplace=True)

        # Select one value for Mass and WFE (e.g., first available row)
        if not df.empty:
            mass = df["Mass"].iloc[0]  # First Mass found
            wfe = df["WFE"].iloc[0]  # First WFE found
            unique_entries[(altitude, isa)] = (mass, wfe)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Convert dictionary to DataFrame
final_df = pd.DataFrame(
    [{"Mass": mass, "WFE": wfe, "Altitude": alt, "ISA": isa}
     for (alt, isa), (mass, wfe) in unique_entries.items()]
)

# Save the final results to a CSV file
output_file = "../Data/combined_results.csv"
final_df.to_csv(output_file, index=False)
print(f"Final results saved to: {output_file}")
