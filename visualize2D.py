import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd
import glob
import mpl_toolkits.mplot3d

# Merge all processed CSV files
isa_value = '*'
pattern = f"ptd_results/results_Altitude_*_ISA_{isa_value}.csv"
all_results_df = pd.concat([pd.read_csv(f) for f in glob.glob(pattern)], ignore_index=True)

def plot_rmse_vs_altitude(x, y, data, y_label, title, file_name):
    sns.lineplot(x=x, y=y, data=data, errorbar=None)
    plt.xlabel("Altitude (ft)")
    plt.ylabel(y_label)
    plt.title(title)
    plt.savefig(file_name)
    plt.show()

# # Now you can call this function for each plot
plot_rmse_vs_altitude(
    x="Altitude", y="RelativeError_Drag", data=all_results_df,
    y_label="RelativeError_Drag", title="DragRelativeError vs Altitude",
    file_name="res/DragRelativeError_vs_altitude.png"
)

plot_rmse_vs_altitude(
    x="Altitude", y="RelativeError_Fuel", data=all_results_df,
    y_label="RelativeError_Fuel", title="FuelRelativeError vs Altitude",
    file_name="res/FuelRelativeError_vs_altitude.png"
)

plot_rmse_vs_altitude(
    x="Altitude", y="RMSE_Fuel", data=all_results_df,
    y_label="RMSE_Fuel", title="RMSE_Fuel vs Altitude",
    file_name="res/RMSE_Fuel_vs_altitude.png"
)

plot_rmse_vs_altitude(
    x="Altitude", y="RelativeError_Fuel_BEAM", data=all_results_df,
    y_label="RelativeError_Fuel_BEAM", title="RelativeError_Fuel_BEAM vs Altitude",
    file_name="res/RelativeError_Fuel_BEAM_vs_altitude.png"
)

plot_rmse_vs_altitude(
    x="Altitude", y="RMSE_Fuel_BEAM", data=all_results_df,
    y_label="RMSE_Fuel_BEAM", title="RMSE_Fuel_BEAM vs Altitude",
    file_name="res/RMSE_Fuel_BEAM_vs_altitude.png"
)