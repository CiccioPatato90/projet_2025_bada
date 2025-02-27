
from dataclasses import dataclass
import matplotlib.pyplot as plt
import pandas as pd

from pyBADA import TCL as TCL
from pyBADA.bada4 import Bada4Aircraft
from pyBADA.bada4 import Parser as Bada4Parser


@dataclass
class target:
    ROCDtarget: float = None
    slopetarget: float = None
    acctarget: float = None
    ESFtarget: float = None


# initialization of BADA3/4
# uncomment for testing different BADA family if available

badaVersion = "DUMMY"

# allData = Bada3Parser.parseAll(badaVersion=badaVersion)
allData = Bada4Parser.parseAll(badaVersion=badaVersion,filePath="reference_dummy_extracted")
print(allData)

#AC = Bada3Aircraft(badaVersion=badaVersion, acName="J2H", allData=allData)
AC = Bada4Aircraft(
    badaVersion=badaVersion,
    acName="Dummy-TWIN-plus",
    allData=allData,
)

# default parameters
speedType = "CAS"  # {M, CAS, TAS}
wS = 0  # [kt] wind speed
ba = 0  # [deg] bank angle
DeltaTemp = 0  # [K] delta temperature from ISA

# Initial conditions
#m_init = AC.OEW + 0.7 * (AC.MTOW - AC.OEW)  # [kg] initial mass
m_init = 180000
CAS_init = 309.1  # [kt] Initial CAS
Altitude = 31000 # [ft] CDG RWY26R elevation

df = TCL.constantSpeedLevel(
    # plane to sim
    AC=AC,
    # length of the flight segment type
    lengthType='time',
    # simulation length
    length=3600,
    # CAS, TAS or - for Mach
    speedType=speedType,
    # wind speed (positive for headwind, negative for tailwind)
    wS=wS,
    # target speed, for cruise is maintained
    v=CAS_init,
    # initial pressure
    Hp_init=Altitude,
    # initial mass
    m_init=m_init,
    # deviation from standard ISA [kelvin]
    DeltaTemp=DeltaTemp,
    # optional: Specify the flight phase
    flightPhase='Cruise'
)


print(df)

# Plot for Mass
plt.figure(3, figsize=(8, 6))
plt.plot(df["time"], df["mass"], linestyle="-", color="r")
plt.grid(True)
plt.xlabel("Distance [NM]")
plt.ylabel("mass [kg]")
plt.title("Mass (kg) as a Function of Distance")

# Plot for fuel quantity
plt.figure(4, figsize=(8, 6))
plt.plot(df["time"], df["FUELCONSUMED"], linestyle="-", color="r")
plt.grid(True)
plt.xlabel("time [s]")
plt.ylabel("fuel [kg]")
plt.title("fuel consumed (kg) as a Function of Time")
# Display the plot
plt.show()

# Plot for fuel quantity
plt.figure(4, figsize=(8, 6))
plt.plot(df["time"], df["FUEL"]*3600, linestyle="-", color="r")
plt.grid(True)
plt.xlabel("distance [kt]")
plt.ylabel("fuel [kg]")
plt.title("fuel consumption rate (kg/s) as a Function of time")
# Display the plot
plt.show()


# Calculate Specific Range (SR) in NM/kg
df_sr = df["dist"] / (df["FUEL"]*3600) # makes sense bc (kg/s)*s = kg --> NM/k

# Plot SR as a function of time
plt.figure(4, figsize=(8, 6))
plt.plot(df["dist"], df_sr, linestyle="-", color="r")
plt.grid(True)
plt.xlabel("Time [s]")
plt.ylabel("Specific Range [NM/kg]")
plt.title("Specific Range (NM/kg) as a Function of Time")
plt.show()
