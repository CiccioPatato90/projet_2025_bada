import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd
import glob
import mpl_toolkits.mplot3d

# Merge all processed CSV files
isa_value = '*'
pattern = f"ptd_results/results_Altitude_*_ISA_{isa_value}.csv"
all_results_df = pd.concat([pd.read_csv(f) for f in glob.glob(pattern)], ignore_index=True)

# Plot RMSE vs Altitude
sns.lineplot(x="Altitude", y="RelativeError_Drag", data=all_results_df)
plt.xlabel("Altitude (ft)")
plt.ylabel("RelativeError_Drag")
plt.title("DragRelativeError vs Altitude")
plt.savefig("res/DragRelativeError_vs_altitude.png")
plt.show()

sns.lineplot(x="Altitude", y="RelativeError_Fuel", data=all_results_df)
plt.xlabel("Altitude (ft)")
plt.ylabel("RelativeError_Fuel")
plt.title("FuelRelativeError vs Altitude")
plt.savefig("res/FuelRelativeError_vs_altitude.png")
plt.show()

sns.lineplot(x="Altitude", y="RelativeError_Fuel_BEAM", data=all_results_df)
plt.xlabel("Altitude (ft)")
plt.ylabel("RelativeError_Fuel_BEAM")
plt.title("RelativeError_Fuel_BEAM vs Altitude")
plt.savefig("res/RelativeError_Fuel_BEAM_vs_altitude.png")
plt.show()

sns.lineplot(x="Altitude", y="RMSE_Drag", data=all_results_df)
plt.xlabel("Altitude (ft)")
plt.ylabel("RMSE_Drag")
plt.title("RMSE_Drag vs Altitude")
plt.savefig("res/RMSE_Drag_vs_altitude.png")
plt.show()

sns.lineplot(x="Altitude", y="RMSE_Fuel_BEAM", data=all_results_df)
plt.xlabel("Altitude (ft)")
plt.ylabel("RMSE_Fuel_BEAM")
plt.title("RMSE_Fuel_BEAM vs Altitude")
plt.savefig("res/RMSE_Fuel_BEAM_vs_altitude.png")
plt.show()

sns.lineplot(x="Altitude", y="RMSE_Fuel", data=all_results_df)
plt.xlabel("Altitude (ft)")
plt.ylabel("RMSE_Fuel")
plt.title("RMSE_Fuel vs Altitude")
plt.savefig("res/RMSE_Fuel_vs_altitude.png")
plt.show()
