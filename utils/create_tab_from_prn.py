import re

def extract_unique_altitudes(prn_file):
    altitudes = set()  # Using a set to store unique values

    with open(prn_file, "r", encoding="utf-8") as file:
        for line in file:
            match = re.search(r"ALTITUDE\s*:\s*([-+]?\d*\.?\d+)", line)
            if match:
                altitude = float(match.group(1))  # Convert to float
                altitudes.add(altitude)  # Add to the set (avoids duplicates)

    return sorted(altitudes)  # Return sorted unique altitudes

def extract_unique_temperature(prn_file):
    temps = set()

    with open(prn_file, "r", encoding="utf-8") as file:
        for line in file:
            match = re.search(r"ISA\s*\s*([-+]?\s*\d*\.?\d+)", line)
            if match:
                temp= float(match.group(1).replace(" ", ""))
                temps.add(temp)

    return sorted(temps)


prn_file_path = "../reference_skyconseil/A330_example.prn"
unique_altitudes = extract_unique_altitudes(prn_file_path)
unique_temps= extract_unique_temperature(prn_file_path)
print("Extracted Unique Altitudes:", unique_altitudes)
print("Extracted Unique Temperatures:", unique_temps)
