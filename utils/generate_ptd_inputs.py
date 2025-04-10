import os
import re
import csv

# Set up output directory
output_dir = os.path.join(os.path.dirname(__file__), "../ptd_inputs")
os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

# Open the PRN file for reading
with open("../reference_skyconseil/A330_example.prn", "r") as file:
    lines = file.readlines()

# Regular expressions to detect altitude, temperature, and data rows
alt_temp_pattern = re.compile(
    r"ALTITUDE\s*:\s*([\d.]+)\.FT\s+ISA\s*([+-]?\s*\d+\.\d+)\s+DG\.C\s+WIND\s*:\s*(0\.0)\s*KT"
)
data_pattern = "WGHT    MACH    CAS     TAS      SR     WFE      N1     EGT      CL      CD     ALPH    DRAG     FN     PCFN"

current_altitude = None
current_temperature = None

for index, line in enumerate(lines):
    # Match altitude and ISA temperature
    alt_temp_match = alt_temp_pattern.search(line)
    if alt_temp_match:
        current_altitude = float(alt_temp_match.group(1))
        current_temperature = float(alt_temp_match.group(2).replace(" ", ""))  # Clean spaces
        continue

    # Match start of data block
    if current_altitude is not None and (data_pattern in line):
        current_line_index = index
        data_rows = []

        for j in range(2, 54):  # Scan forward to collect rows
            if current_line_index + j < len(lines):
                next_line = lines[current_line_index + j]

                # Stop if not a data row (based on 4th character being alpha)
                if len(next_line) > 3 and next_line[3].isalpha():
                    break

                row_values = next_line.split()

                if len(row_values) >= 14:
                    row_values = list(map(float, row_values))
                    data_rows.append([current_altitude, current_temperature] + row_values)

        # Define output filename based on altitude and temp
        output_filename = f"ALT_{int(current_altitude)}_ISA_{current_temperature:+.1f}.csv"
        output_filepath = os.path.join(output_dir, output_filename.replace("+", "P").replace("-", "M"))

        # Write data for this block
        with open(output_filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ALTITUDE (FT)", "ISA TEMP (C)", "WGHT (KG)", "MACH", "CAS (KT)", "TAS (KT)",
                             "SR (NMKG)", "WFE (KG/H)", "N1 (%)", "EGT (DG.C)", "CL", "CD",
                             "ALPH (DEG)", "DRAG (DAN)", "FN (DAN)", "PCFN (%)"])
            writer.writerows(data_rows)

        print(f"Saved data to: {output_filepath}")
