import glob
import os
import csv
from matplotlib import pyplot as plt
from pyBADA.bada4 import Bada4Aircraft
from pyBADA.bada4 import Parser as Bada4Parser
from pyBADA.bada4 import PTD
import seaborn as sns

import numpy as np
import pandas as pd

badaVersion = "DUMMY"
allData = Bada4Parser.parseAll(badaVersion=badaVersion, filePath="../reference_dummy_extracted")

# Create BADA Aircraft instance
AC = Bada4Aircraft(
    badaVersion=badaVersion,
    acName="Dummy-TWIN-plus",
    allData=allData,
)
mass_list=[180000.0,181000.0,182000.0,
183000.0,
184000.0,
185000.0,
186000.0,
187000.0,
188000.0,
189000.0,
190000.0,
191000.0,
192000.0,
193000.0,
194000.0,
195000.0,
196000.0,
197000.0,
198000.0,
199000.0,
200000.0,
201000.0,
202000.0,203000.0,204000.0,205000.0,206000.0,207000.0,208000.0,209000.0,210000.0,211000.0,212000.0,213000.0,214000.0,215000.0,216000.0,217000.0,218000.0,219000.0,220000.0,221000.0,222000.0,223000.0,224000.0,225000.0,226000.0,227000.0,228000.0,229000.0,230000.0]
AltitudeList = [30000]*len(mass_list)

ptd = PTD(AC)
result = ptd.PTD_cruise(180000, [30000], -10)
#ptd.create_only_cruise(0,mass_list,AltitudeList,"../Data")
tab1=[ "FL " ,  "T" ,      "p" ,     "rho ",   " a ",  "TAS" , "CAS",  "M" , "mass","Thrust", "Drag",  "Fuel", "ESF", "ROCD","gamma" ,"Conf","Lim"]
ta2=["[-] " , "[K]" , "[Pa]",  "[kg/m3]", "[m/s]",   "[kt]",    "[kt]",   "[-]", "[kg]",  "[N]",  "[N]",  "[kgm]", "[-]","[fpm]","[deg]","[-]"]
results = []
for i in range(len(result)):
    results.append(result[i][0])
flat_result = [x[0] if isinstance(x, list) else x for x in result]

# Créer le DataFrame avec une seule ligne
results_df = pd.DataFrame([flat_result], columns=tab1)

base_name = "PTD.csv"
output_file_path = os.path.join("../Neural_Network", f"results_{base_name}")
results_df.to_csv(output_file_path, index=False)
print(f"Results saved to: {output_file_path}")