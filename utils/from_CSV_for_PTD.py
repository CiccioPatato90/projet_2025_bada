import pandas as pd
import os
import numpy as np
from glob import glob
from pyBADA import atmosphere

output_dir = os.path.join(os.path.dirname(__file__), "../ptd_inputs")
os.makedirs(output_dir, exist_ok=True)

R = 287.05  # constant gas

def calculate_tas(mach, temperature):
    heat_ratio = 1.4
    tas = mach * np.sqrt(R * heat_ratio * temperature)
    return tas

# def calculate_isa_deviation(altitude_feet, temperature_real):
#     T0 = 15.0
#     T_ISA = T0 - (1.98 * altitude_feet) / 1000
#     delta_T = temperature_real - T_ISA
#     return delta_T

def calculate_isa_temperature(altitude_meters):
    # Constants
    sea_level_temperature_C = 15.0       # Celsius
    lapse_rate = 0.0065                  # K/m
    tropopause_altitude = 11000          # meters

    if altitude_meters < tropopause_altitude:
        isa_temperature = sea_level_temperature_C - lapse_rate * altitude_meters
    else:
        isa_temperature = sea_level_temperature_C - lapse_rate * tropopause_altitude
    return isa_temperature  # returns Celsius

def calculate_isa_deviation(altitude_feet, temperature_real):
    altitude_meters = altitude_feet * 0.3048
    isa_temp = calculate_isa_temperature(altitude_meters)
    return temperature_real - isa_temp  # both in °C

def process_file(file_path):
    try:
        df = pd.read_csv(file_path)
        df_cruise = df[df['Cruise'] == 1]
        df_filtered = df_cruise[df_cruise['Time_secs'] % 50 == 0]

        columns_needed = [
            'Computed_Airspeed', 'Mach', 'Pitch_Angle', 'Roll_Angle', 'Altitude',
            'Gross_Weight', 'Static_Temp', 'EGT_E1', 'N1_E1', 'Instant_Fuel'
        ]
        df_filtered = df_filtered[columns_needed]

        df_filtered['WGHT (KG)'] = df_filtered['Gross_Weight']
        df_filtered['MACH'] = df_filtered['Mach']
        df_filtered['CAS (KT)'] = df_filtered['Computed_Airspeed']
        df_filtered['TAS (KT)'] = df_filtered.apply(
            lambda row: calculate_tas(row['MACH'], row['Static_Temp'] + 273.15),
            axis=1
        )
        df_filtered['SR (NMKG)'] = 0
        df_filtered['WFE (KG/H)'] = df_filtered['Instant_Fuel'] * 2
        df_filtered['N1 (%)'] = df_filtered['N1_E1']
        df_filtered['EGT (DG.C)'] = df_filtered['EGT_E1']
        df_filtered['CL'] = 0
        df_filtered['CD'] = 0
        df_filtered['ALPH (DEG)'] = df_filtered['Pitch_Angle']
        df_filtered['ROLL (DEG)'] = df_filtered['Roll_Angle'].fillna(0.0)
        df_filtered['DRAG (DAN)'] = 0
        df_filtered['FN (DAN)'] = 0
        df_filtered['PCFN (%)'] = 0

        df_filtered['ISA TEMP (C)'] = df_filtered.apply(
            lambda row: calculate_isa_deviation(row['Altitude'], row['Static_Temp']),
            axis=1
        )

        final_columns = [
            'WGHT (KG)', 'MACH', 'CAS (KT)', 'TAS (KT)', 'SR (NMKG)', 'WFE (KG/H)',
            'N1 (%)', 'EGT (DG.C)', 'CL', 'CD', 'ALPH (DEG)', 'ROLL (DEG)', 'DRAG (DAN)', 'FN (DAN)', 'PCFN (%)',
            'Altitude', 'ISA TEMP (C)'
        ]
        df_final = df_filtered[final_columns]

        return df_final

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Main processing
try:
    csv_files = glob('../reference_skyconseil/A321/*.csv')

    if not csv_files:
        print("No CSV files found in the directory")
    else:
        combined_data = []

        for file in csv_files:
            df_processed = process_file(file)
            if df_processed is not None:
                combined_data.append(df_processed)

        if combined_data:
            final_df = pd.concat(combined_data, ignore_index=True)
            output_file = os.path.join(output_dir, 'combined_data.csv')
            final_df.to_csv(output_file, index=False)
            print(f"Successfully saved all data into {output_file}")

except Exception as e:
    print(f"An error occurred: {e}")