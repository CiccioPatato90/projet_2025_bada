import os
import re
import csv

output_dir = os.path.join(os.path.dirname(__file__), "../ptd_inputs")
os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

# Open the PRN file for reading
with open("../reference_skyconseil/A330_example.prn", "r") as file:
    lines = file.readlines()

# Regular expressions to detect altitude, temperature, and data rows
alt_temp_pattern = re.compile( r"ALTITUDE\s*:\s*([\d.]+)\.FT\s+ISA\s*([+-]?\s*\d+\.\d+)\s+DG\.C\s+WIND\s*:\s*(0\.0)\s*KT")
data_pattern = "WGHT    MACH    CAS     TAS      SR     WFE      N1     EGT      CL      CD     ALPH    DRAG     FN     PCFN"

# Store extracted data
data_blocks = {}

current_key = None
for index, line in enumerate(lines):
    # Search for altitude and ISA temperature
    alt_temp_match = alt_temp_pattern.search(line)
    if alt_temp_match:
        print(line)
        altitude = float(alt_temp_match.group(1))
        temperature = float(alt_temp_match.group(2).replace(" ", ""))  # Clean spaces
        current_key = (str(altitude), str(temperature))
        data_blocks[current_key] = []
        continue

    # Capture table data
    if current_key and (data_pattern in line):
        current_line_index = index
        for j in range(2, 54):
            if current_line_index + j < len(lines):
                next_line = lines[current_line_index + j]

                # Stop appending if the second character is a letter
                if len(next_line) > 3 and next_line[3].isalpha():
                    #print(f"Stopping at: {current_key}")
                    break

                data_blocks[current_key].append(next_line)


# Save each altitude-temperature block into a CSV
for (altitude, temperature), rows in data_blocks.items():
    if altitude != '40000.0':
        filename = f"Altitude_{altitude}_ISA_{temperature}.csv"
        filepath = os.path.join(output_dir, filename)  # Save in ptd_inputs folder

        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["WGHT (KG)", "MACH", "CAS (KT)", "TAS (KT)", "SR (NMKG)", "WFE (KG/H)", "N1 (%)", "EGT (DG.C)", "CL", "CD", "ALPH (DEG)", "DRAG (DAN)", "FN (DAN)", "PCFN (%)"])
            for row in rows:
                row=list(map(float, row.split()))
                writer.writerow(row)
        print(f"Saved: {filename}")
