import re

def extract_altitude_and_isa(filename):
    match = re.search(r"Altitude_(-?\d+(?:\.\d+)?)_ISA_(-?\d+(?:\.\d+)?).csv", filename)
    if match:
        return float(match.group(1)), float(match.group(2))
    else:
        print(f"Could not extract altitude or ISA from filename: {filename}")

# Example usage:
filename = "Altitude_30000.0_ISA_-20.0.csv"
print(extract_altitude_and_isa(filename))