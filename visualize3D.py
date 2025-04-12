import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd
import glob
import mpl_toolkits.mplot3d
import numpy as np
from scipy.interpolate import griddata

# Merge all processed CSV files
pattern = f"ptd_results/*.csv"
all_results_df = pd.concat([pd.read_csv(f) for f in glob.glob(pattern)], ignore_index=True)

# Define a threshold for high relative error drag
high_error_threshold = 0  # Adjust this value as needed
high_error_mask = all_results_df['RelativeError_Fuel'] > high_error_threshold
if high_error_mask.any():
    print("Warning: High relative error fuel detected!")
    # Extract the altitude and mass for high relative error drag
    high_error_data = all_results_df[high_error_mask][['Altitude', 'Mass', 'RelativeError_Fuel']]
    print("Altitude and Mass for high relative error fuel:")
    print(high_error_data)
else:
    print("No high relative error fuel detected.")

# Plotting the 3D scatter plot for RelativeError_Drag
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter(all_results_df['RelativeError_Drag'], all_results_df['Altitude'], all_results_df['Mass'],
                c=all_results_df['RelativeError_Drag'], cmap='viridis')
ax.set_xlabel('RelativeError_Drag')
ax.set_ylabel('Mass')
ax.set_zlabel('Altitude')
ax.set_title('Relative Error Drag')  # Add title
plt.colorbar(sc, label='RelativeError_Drag')
plt.show()

# Plotting the 3D scatter plot for RelativeError_Fuel
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter(all_results_df['RelativeError_Fuel'], all_results_df['Altitude'], all_results_df['Mass'],
                c=all_results_df['RelativeError_Fuel'], cmap='viridis')
ax.set_xlabel('RelativeError_Fuel')
ax.set_ylabel('Mass')
ax.set_zlabel('Altitude')
ax.set_title('Relative Error Fuel')  # Add title
plt.colorbar(sc, label='RelativeError_Fuel')
plt.show()

# Interpolating and plotting the surface for RMSE_Drag
x = all_results_df['Altitude'].values
y = all_results_df['Mass'].values
z = all_results_df['RMSE_Drag'].values

xi = np.linspace(x.min(), x.max(), 100)
yi = np.linspace(y.min(), y.max(), 100)
xi, yi = np.meshgrid(xi, yi)
zi = griddata((x, y), z, (xi, yi), method='cubic')

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(xi, yi, zi, cmap='viridis')
ax.set_xlabel('Altitude')
ax.set_ylabel('Mass')
ax.set_zlabel('RelativeError_Drag')
ax.set_title('Surface Plot of RMSE Drag')  # Add title
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()

# Interpolating and plotting the surface for RMSE_Fuel
z_fuel = all_results_df['RMSE_Fuel'].values
zi_fuel = griddata((x, y), z_fuel, (xi, yi), method='cubic')

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(xi, yi, zi_fuel, cmap='viridis')
ax.set_xlabel('Altitude')
ax.set_ylabel('Mass')
ax.set_zlabel('RMSE_Fuel')
ax.set_title('Surface Plot of RMSE Fuel')  # Add title
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()