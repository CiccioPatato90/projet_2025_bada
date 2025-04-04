import os
import re
import csv

output_dir = os.path.join(os.path.dirname(__file__), "../ptd_inputs")
os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

output_filepath = os.path.join(output_dir, "combined_output.csv")

# Open the PRN file for reading
with open("../reference_skyconseil/A330_example.prn", "r") as file:
    lines = file.readlines()

# Regular expressions to detect altitude, temperature, and data rows
alt_temp_pattern = re.compile(
    r"ALTITUDE\s*:\s*([\d.]+)\.FT\s+ISA\s*([+-]?\s*\d+\.\d+)\s+DG\.C\s+WIND\s*:\s*(0\.0)\s*KT"
)
data_pattern = "WGHT    MACH    CAS     TAS      SR     WFE      N1     EGT      CL      CD     ALPH    DRAG     FN     PCFN"

# Store extracted data
data_rows = []

current_altitude = None
current_temperature = None

for index, line in enumerate(lines):
    # Search for altitude and ISA temperature
    alt_temp_match = alt_temp_pattern.search(line)
    if alt_temp_match:
        current_altitude = float(alt_temp_match.group(1))
        current_temperature = float(alt_temp_match.group(2).replace(" ", ""))  # Clean spaces
        continue

    # Capture table data
    if current_altitude and (data_pattern in line):
        current_line_index = index
        for j in range(2, 54):
            if current_line_index + j < len(lines):
                next_line = lines[current_line_index + j]

                # Stop appending if the second character is a letter
                if len(next_line) > 3 and next_line[3].isalpha():
                    break


                row_values = next_line.split()

                if len(row_values) >= 14:
                    row_values = list(map(float, row_values))
                    data_rows.append([current_altitude, current_temperature] + row_values)

# Write all collected data into a single CSV file
with open(output_filepath, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Header with added Altitude and ISA Temperature columns
    writer.writerow(["ALTITUDE (FT)", "ISA TEMP (C)", "WGHT (KG)", "MACH", "CAS (KT)", "TAS (KT)",
                     "SR (NMKG)", "WFE (KG/H)", "N1 (%)", "EGT (DG.C)", "CL", "CD",
                     "ALPH (DEG)", "DRAG (DAN)", "FN (DAN)", "PCFN (%)"])

    # Write data rows
    writer.writerows(data_rows)

print(f"Saved all data to: {output_filepath}")