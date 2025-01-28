import re
import csv


# Open the PRN file for reading
with open("../Data/A330_example(1).prn", "r") as file:
    lines = file.readlines()

# Regular expressions to detect altitude, temperature, and data rows
alt_temp_pattern = re.compile(r"ALTITUDE\s*:\s*([\d.]+)\.FT\s+ISA\s*([+-]?\s*\d+\.\d+)")
data_pattern = "WGHT    MACH    CAS     TAS      SR     WFE      N1     EGT      CL      CD     ALPH    DRAG     FN     PCFN"

# Store extracted data
data_blocks = {}

current_key = None
for index, line in enumerate(lines):
    # Search for altitude and ISA temperature
    alt_temp_match = alt_temp_pattern.search(line)
    if alt_temp_match:
        altitude = float(alt_temp_match.group(1))
        temperature = float(alt_temp_match.group(2).replace(" ", ""))  # Clean spaces
        current_key = (str(altitude), str(temperature))
        data_blocks[current_key] = []
        continue

    # Capture table data
    if current_key and (data_pattern in line):
        current_line_index = index
        data_blocks[current_key].append(lines[current_line_index + 2 : current_line_index + 54])

# Save each altitude-temperature block into a CSV
for (altitude, temperature), rows in data_blocks.items():
        filename = f"Altitude_{altitude}_ISA_{temperature}.csv"
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["WGHT (KG)", "MACH", "CAS (KT)", "TAS (KT)", "SR (NMKG)", "WFE (KG/H)", "N1 (%)", "EGT (DG.C)", "CL", "CD", "ALPH (DEG)", "DRAG (DAN)", "FN (DAN)", "PCFN (%)"])
            for row in rows:
                for r in row:
                    r=list(map(float, r.split()))
                    print(r)
                    writer.writerow(r)
        print(f"Saved: {filename}")
