import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd
import glob
import mpl_toolkits.mplot3d

# Merge all processed CSV files
isa_value = '*'
pattern = f"ptd_results/results_Altitude_*_ISA_{isa_value}.csv"
all_results_df = pd.concat([pd.read_csv(f) for f in glob.glob(pattern)], ignore_index=True)


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter(all_results_df['RelativeError_Drag'],all_results_df['Altitude'], all_results_df['Mass'],
                c=all_results_df['RelativeError_Drag'], cmap='viridis')
ax.set_xlabel('RelativeError_Drag')
ax.set_ylabel('Mass')
ax.set_zlabel('Altitude')
plt.colorbar(sc, label='RelativeError_Drag')
plt.show()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter( all_results_df['RelativeError_Fuel'], all_results_df['Altitude'], all_results_df['Mass'],
                c=all_results_df['RelativeError_Fuel'], cmap='viridis')
ax.set_xlabel('RelativeError_Fuel')
ax.set_ylabel('Mass')
ax.set_zlabel('Altitude')
plt.colorbar(sc, label='RelativeError_Fuel')
plt.show()


from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
import numpy as np

x = all_results_df['Altitude'].values
y = all_results_df['Mass'].values
z = all_results_df['RMSE_Drag'].values

xi = np.linspace(x.min(), x.max(), 100)
yi = np.linspace(y.min(), y.max(), 100)
xi, yi = np.meshgrid(xi, yi)
zi = griddata((x, y), z, (xi, yi), method='cubic')

# Plot the surface
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(xi, yi, zi, cmap='viridis')
ax.set_xlabel('Altitude')
ax.set_ylabel('Mass')
ax.set_zlabel('RelativeError_Drag')
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()


z_fuel = all_results_df['RMSE_Fuel'].values

zi_fuel = griddata((x, y), z_fuel, (xi, yi), method='cubic')

# Plot the surface
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(xi, yi, zi_fuel, cmap='viridis')
ax.set_xlabel('Altitude')
ax.set_ylabel('Mass')
ax.set_zlabel('RMSE_Fuel')
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()