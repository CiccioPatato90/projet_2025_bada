import pandas as pd
import os
import numpy as np

output_dir = os.path.join(os.path.dirname(__file__), "../ptd_inputs")
os.makedirs(output_dir, exist_ok=True)

R = 287.05  # constant gas
rho0 = 1.225  # Air density at sea level (kg/m³)


def calculate_tas(mach, temperature):
    heat_ratio=1.4
    tas = mach* np.sqrt(R*heat_ratio*temperature)
    return tas


def calculate_isa_deviation(altitude_feet, temperature_real):
    T0 = 15.0
    T_ISA = T0 - (1.98* altitude_feet)/1000
    delta_T = temperature_real - T_ISA
    return delta_T


def calculate_Drag():
    return 0  # need to calculate


try:
    df = pd.read_csv('../reference_skyconseil/FDR-input.csv')
    df_name = df['Type'][1]
    df_cruise = df[df['Cruise'] == 1]

    df_filtered = df_cruise[df_cruise['Time_secs'] % 50 == 0]

    columns_needed = [
        'Computed_Airspeed', 'Mach', 'Pitch_Angle', 'Roll_Angle', 'Altitude',
        'Gross_Weight', 'T_Air_Temp', 'EGT_E1', 'EPR_E1', 'N1_E1',
        'Throttle_Angle1', 'Instant_Fuel'
    ]
    df_filtered = df_filtered[columns_needed]

    df_filtered['WGHT (KG)'] = df_filtered['Gross_Weight']
    df_filtered['MACH'] = df_filtered['Mach']
    df_filtered['CAS (KT)'] = df_filtered['Computed_Airspeed']

    df_filtered['TAS (KT)'] = df_filtered.apply(
        lambda row: calculate_tas(row['MACH'], row['T_Air_Temp'] + 273.15),
        axis=1
    )

    df_filtered['SR (NMKG)'] = 0
    df_filtered['WFE (KG/H)'] = df_filtered['Instant_Fuel']
    df_filtered['N1 (%)'] = df_filtered['N1_E1']
    df_filtered['EGT (DG.C)'] = df_filtered['EGT_E1']
    df_filtered['CL'] = 0
    df_filtered['CD'] = 0
    df_filtered['ALPH (DEG)'] = df_filtered['Pitch_Angle']
    df_filtered['ROLL (DEG)'] = df_filtered['Roll_Angle']
    df_filtered['PATH (DEG)'] = 0
    df_filtered['DRAG (DAN)'] = calculate_Drag()
    df_filtered['FN (DAN)'] = 0
    df_filtered['PCFN (%)'] = 0

    final_columns = [
        'WGHT (KG)', 'MACH', 'CAS (KT)', 'TAS (KT)', 'SR (NMKG)', 'WFE (KG/H)',
        'N1 (%)', 'EGT (DG.C)', 'CL', 'CD', 'ALPH (DEG)', 'ROLL (DEG)', 'PATH (DEG)', 'DRAG (DAN)', 'FN (DAN)', 'PCFN (%)'
    ]
    df_final = df_filtered[final_columns]

    # Save each row to a separate CSV file
    for i in range(len(df_final)):
        altitude = int(df_filtered['Altitude'].iloc[i])
        isa = round(calculate_isa_deviation(df_filtered['Altitude'].iloc[i], df_filtered['T_Air_Temp'].iloc[i]),2)
        df_final.iloc[i:i + 1].to_csv(os.path.join(output_dir, f'A319_Altitude_{altitude}_ISA_{isa}.csv'), index=False)

    # Save the entire filtered data to a CSV file
    df_final.to_csv(os.path.join(output_dir, f'filtered_cruise_data_{df_name}.csv'), index=False)

except Exception as e:
    print(f"An error occurred: {e}")