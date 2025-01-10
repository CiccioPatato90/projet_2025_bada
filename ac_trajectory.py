"""
Aircraft Trajectory Calculation
===============================

Example of BADA3 and BADA4 trajectory using TCL
"""

from dataclasses import dataclass
import matplotlib.pyplot as plt

from pyBADA import atmosphere as atm
from pyBADA import conversions as conv
from pyBADA import TCL as TCL
from pyBADA.flightTrajectory import FlightTrajectory as FT
from pyBADA.bada3 import Bada3Aircraft
from pyBADA.bada4 import Bada4Aircraft
from pyBADA.bada4 import Parser as Bada4Parser
from pyBADA.bada3 import Parser as Bada3Parser


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
allData = Bada4Parser.parseAll(badaVersion=badaVersion)
print(allData)

#AC = Bada3Aircraft(badaVersion=badaVersion, acName="J2H", allData=allData)
AC = Bada4Aircraft(
    badaVersion=badaVersion,
    acName="Dummy-TWIN-plus",
    allData=allData,
)



# Example loading models from files on disk
# AC = Bada4Aircraft(
#    badaVersion=badaVersion,
#    acName="A320-232",
#    filePath="/home/<USER>/ec/pybada-models/models/BADA4/4.3",
# )

# create a Flight Trajectory object to store the output from TCL segment calculations
ft = FT()

# default parameters
speedType = "CAS"  # {M, CAS, TAS}
wS = 60  # [kt] wind speed
ba = 0  # [deg] bank angle
DeltaTemp = 10  # [K] delta temperature from ISA

# Initial conditions
m_init = AC.OEW + 0.7 * (AC.MTOW - AC.OEW)  # [kg] initial mass
CAS_init = 170  # [kt] Initial CAS
Hp_RWY = 318.0  # [ft] CDG RWY26R elevation

# take-off conditions
[theta, delta, sigma] = atm.atmosphereProperties(
    h=conv.ft2m(Hp_RWY), DeltaTemp=DeltaTemp
)  # atmosphere properties at RWY altitude
[cas_cl1, speedUpdated] = AC.ARPM.climbSpeed(
    h=conv.ft2m(Hp_RWY),
    mass=m_init,
    theta=theta,
    delta=delta,
    DeltaTemp=DeltaTemp,
)  # [m/s] take-off CAS

flightTrajectory = TCL.constantSpeedRating(
    AC=AC,
    speedType="CAS",
    v=conv.ms2kt(cas_cl1),
    Hp_init=Hp_RWY,
    Hp_final=600,
    m_init=m_init,
    wS=wS,
    bankAngle=ba,
    DeltaTemp=DeltaTemp,
)
ft.append(AC, flightTrajectory)

[Vcr1, Vcr2, Mcr] = AC.flightEnvelope.getSpeedSchedule(
    phase="Cruise"
)  # BADA Cruise speed schedule

# CRUISE for 200 NM
# ------------------------------------------------
# current values
Hp, m_final = ft.getFinalValue(AC, ["Hp", "mass"])

flightTrajectory = TCL.constantSpeedLevel(
    AC=AC,
    lengthType="distance",
    length=200,
    speedType="M",
    v=Mcr,
    Hp_init=Hp,
    m_init=m_final,
    wS=wS,
    bankAngle=ba,
    DeltaTemp=DeltaTemp,
)
ft.append(AC, flightTrajectory)


# print and plot final trajectory
df = ft.getFT(AC=AC)
print(df)

# Plotting the graph Hp=f(dist)
plt.figure(1, figsize=(8, 6))
plt.plot(df["dist"], df["Hp"], linestyle="-", color="b")
plt.grid(True)
plt.xlabel("Distance [NM]")
plt.ylabel("Pressure Altitude [ft]")
plt.title("Pressure Altitude as a Function of Distance")

# Plot for Calibrated Airspeed (CAS)
plt.figure(2, figsize=(8, 6))
plt.plot(df["dist"], df["CAS"], linestyle="-", color="r")
plt.grid(True)
plt.xlabel("Distance [NM]")
plt.ylabel("CAS [kt]")
plt.title("Calibrated Airspeed (CAS) as a Function of Distance")

# Plot for Mass
plt.figure(3, figsize=(8, 6))
plt.plot(df["time"], df["mass"], linestyle="-", color="r")
plt.grid(True)
plt.xlabel("time [s]")
plt.ylabel("mass [kg]")
plt.title("Mass (kg) as a Function of Time")

# Plot for fuel consumed (kg)
plt.figure(4, figsize=(8, 6))
plt.plot(df["time"], df["FUELCONSUMED"], linestyle="-", color="r")
plt.grid(True)
plt.xlabel("time [s]")
plt.ylabel("fuel [kg]")
plt.title("fuel (kg) as a Function of time")
# Display the plot
plt.show()


# Plot for fuel flow (kg/s)
plt.figure(4, figsize=(8, 6))
plt.plot(df["time"], df["FUEL"], linestyle="-", color="r")
plt.grid(True)
plt.xlabel("time [s]")
plt.ylabel("fuel [kg]")
plt.title("fuel flow (kg/s)")
# Display the plot
plt.show()



# save the output to a CSV/XLSX file
# ------------------------------------------------
# ft.save2csv(os.path.join(grandParentDir, "flightTrajectory_export"), separator=",")
# ft.save2xlsx(os.path.join(grandParentDir, "flightTrajectory_export"))
