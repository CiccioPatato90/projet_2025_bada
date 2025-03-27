import pandas as pd
import os
import numpy as np
from glob import glob

output_dir = os.path.join(os.path.dirname(__file__), "../ptd_inputs")
os.makedirs(output_dir, exist_ok=True)

R = 287.05  # constant gas
rho0 = 1.225  # Air density at sea level


def calculate_tas(mach, temperature):
    heat_ratio = 1.4
    tas = mach * np.sqrt(R * heat_ratio * temperature)
    return tas


def calculate_isa_deviation(altitude_feet, temperature_real):
    T0 = 15.0
    T_ISA = T0 - (1.98 * altitude_feet) / 1000
    delta_T = temperature_real - T_ISA
    return delta_T


def calculate_drag():
    return 0  # need to calculate


def process_file(file_path):
    try:
        df = pd.read_csv(file_path)
        df_name = os.path.splitext(os.path.basename(file_path))[0]

        df_cruise = df[df['Cruise'] == 1]
        df_filtered = df_cruise[df_cruise['Time_secs'] % 50 == 0]

        columns_needed = [
            'Computed_Airspeed', 'Mach', 'Pitch_Angle', 'Altitude',
            'Gross_Weight', 'T_Air_Temp', 'EGT_E1', 'N1_E1', 'Instant_Fuel','Roll_Angle'
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
        df_filtered['DRAG (DAN)'] = calculate_drag()
        df_filtered['FN (DAN)'] = 0
        df_filtered['PCFN (%)'] = 0
        df_filtered['ROLL (DEG)'] = df_filtered['Roll_Angle']
        df_filtered['PATH (DEG)'] = 0 #since cruise

        df_filtered['ISA_DEV'] = df_filtered.apply(
            lambda row: calculate_isa_deviation(row['Altitude'], row['T_Air_Temp']),
            axis=1
        )

        final_columns = [
            'WGHT (KG)', 'MACH', 'CAS (KT)', 'TAS (KT)', 'SR (NMKG)', 'WFE (KG/H)',
            'ROLL (DEG)','PATH (DEG)','N1 (%)', 'EGT (DG.C)', 'CL', 'CD', 'ALPH (DEG)', 'DRAG (DAN)', 'FN (DAN)', 'PCFN (%)',
            'Altitude', 'ISA_DEV'
        ]
        df_final = df_filtered[final_columns]

        df_final = df_final.sort_values(by=['Altitude', 'ISA_DEV'])

        altitude_threshold = 1000
        isa_threshold = 7

        group = []
        previous_altitude = None
        previous_isa = None
        file_counter = 1

        for i, row in df_final.iterrows():
            altitude = row['Altitude']
            isa = row['ISA_DEV']

            if (previous_altitude is None or previous_isa is None or
                    abs(altitude - previous_altitude) > altitude_threshold or
                    abs(isa - previous_isa) > isa_threshold):
                if group:
                    group_df = pd.DataFrame(group)
                    avg_altitude = round(np.mean([r['Altitude'] for r in group]), 0)
                    avg_isa = round(np.mean([r['ISA_DEV'] for r in group]), 2)
                    filename = os.path.join(output_dir, f'Altitude_{avg_altitude}_ISA_{avg_isa}.csv')
                    group_df.drop(columns=['Altitude', 'ISA_DEV'], inplace=True)
                    group_df.to_csv(filename, index=False)
                    file_counter += 1

                group = []

            group.append(row)
            previous_altitude = altitude
            previous_isa = isa

        if group:
            group_df = pd.DataFrame(group)
            avg_altitude = round(np.mean([r['Altitude'] for r in group]), 0)
            avg_isa = round(np.mean([r['ISA_DEV'] for r in group]), 2)
            filename = os.path.join(output_dir, f'Altitude_{avg_altitude}_ISA_{avg_isa}.csv')
            group_df.drop(columns=['Altitude', 'ISA_DEV'], inplace=True)  # Nettoyage avant sauvegarde
            group_df.to_csv(filename, index=False)

        print(f"Successfully processed {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")


# Main processing
try:
    csv_files = glob('../reference_skyconseil/A321/*.csv')

    if not csv_files:
        print("No CSV files found in the directory")
    else:
        for file in csv_files:
            process_file(file)

except Exception as e:
    print(f"An error occurred: {e}")
