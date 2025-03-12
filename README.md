Basically we have three scripts in the library.
OptimizerV2, PTD and Visualize
The sequence to carry out the evaluation is the following:

PTD -> takes current XML coefficients, calculates RMSE+RelativeError
and outputs a csv structure in ptd_results/ the PRN value is copied from the ptd_inputs/


Optimizer -> it has a RMSE based cost function to optimize for fuel and drag
using scipy.optimizer.minimize

Visualize -> plots graphs fro RMSE and RelativeError over Altitude
for Drag and Fuel