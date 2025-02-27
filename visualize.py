import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd
import glob


# Merge all processed CSV files
isa_value = -20.0
pattern = f"ptd_results/results_Altitude_*_ISA_{isa_value}.csv"
all_results_df = pd.concat([pd.read_csv(f) for f in glob.glob(pattern)], ignore_index=True)
#all_results_df = pd.concat([pd.read_csv(f) for f in glob.glob("ptd_results/*.csv")], ignore_index=True)

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

# sns.lineplot(x="Mass", y="RelativeError", data=all_results_df)
# plt.xlabel("Mass (ft)")
# plt.ylabel("RelativeError")
# plt.title("RelativeError vs Mass")
# plt.savefig("res/RelativeError_vs_mass.png")
# plt.show()