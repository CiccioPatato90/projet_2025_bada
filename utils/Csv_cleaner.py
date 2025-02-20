import os
import glob

# Define the directory where the CSV files are located
directory = "../ptd_results"  # Modify this if your files are in a different directory

# Find all CSV files that match the pattern
csv_files = glob.glob(os.path.join(directory, "Altitude_*_ISA_*.csv"))

# Delete each CSV file found
for file in csv_files:
    try:
        os.remove(file)
        print(f"Deleted: {file}")
    except Exception as e:
        print(f"Error deleting {file}: {e}")
