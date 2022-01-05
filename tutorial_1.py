# Use Python 3.9 or 3.8; 3.10 does not work.

# Tutorial link: https://medium.com/towards-formula-1-analysis/how-i-analyze-formula-1-data-with-python-2021-italian-gp-dfb11db4b73

# Last edited: 1/4/22
# On "Next, what we need to do is loop through all the laps one by one."


# Importing all the necessary libraries

import fastf1 as ff1  # Pulls all the necessary data from the fastf1 api
from fastf1 import plotting
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import numpy as np
import pandas as pd

# DPI value for plotting
dpi_val = 500


# Setup plotting
plotting.setup_mpl()


# Enabling the cache to prevent long wait times
ff1.Cache.enable_cache('C:/Users/Josh Gregory/OneDrive - UCB-O365/Current Projects/F1 Analysis Python/tutorial_1_cache')

# Get rid of some pandas warnings that don't matter
pd.options.mode.chained_assignment = None

# Loading in the session data
race = ff1.get_session(2021, 'Monza', 'R')

# Load all laps with telemetry
laps = race.load_laps(with_telemetry=True)


# Select drivers of interest
laps_ric = laps.pick_driver('RIC')
laps_ver = laps.pick_driver('VER')


# Only select first sting since Ver and Ham crashed early

laps_ric = laps_ric.loc[laps_ric['Stint'] == 1]
laps_ver = laps_ver.loc[laps_ver['Stint'] == 1]


# Create a lap number that subtracts 1 lap due to the warm up lap

laps_ric['RaceLapNumber'] = laps_ric['LapNumber'] - 1
laps_ver['RaceLapNumber'] = laps_ver['LapNumber'] - 1

# Get idea of how close Ver was to Ric

# Look at ff1 telemetry data of distance to driver ahead

# Ver was behind Ric

# Two dataframes, one for distance between Ver and Ric at any moment during any lap, and one for the average
# distance (summarized) per lap.

full_distance_ver_ric = pd.DataFrame()
summarized_distance_ver_ric = pd.DataFrame()

# Now loop through all the laps one by one
# Want to reset the distance variable to zero for each lap
# If we don't, we will end up getting the entire length of the
# first stint


for lap in laps_ver.iterlaps():
    # Looping through all of Ver's laps one by one using iterlaps
    # telemetry loads car data, include the distance, and add the driver ahead
    # Adds a column DriverAhead and DistanceToDriverAhead to Ver's telemetry data
    telemetry = lap[1].get_car_data().add_distance().add_driver_ahead()

    # Only run this loop when driver ahead is RIC, otherwise we compare wrong distance gaps
    telemetry = telemetry.loc[telemetry['DriverAhead'] == "3"]

    # Make sure that the telemetry DF is not empty. If it is, there is a pitstop so we discard the data
    if len(telemetry) != 0:
        # Select columns we want for the full distance DF with the lap number.
        # Full distance
        lap_telemetry = telemetry[['Distance', 'DistanceToDriverAhead']]
        lap_telemetry.loc[:, 'Lap'] = lap[0] + 1

        # Only run this loop when driver ahead is Ric, num. 3, otherwise we compare wrong distance gaps
        full_distance_ver_ric = full_distance_ver_ric.append(lap_telemetry)

        # Average / median distance
        # na prefix ignores NaN entries (like during pitstops)
        distance_mean = np.nanmean(telemetry['DistanceToDriverAhead'])
        distance_median = np.nanmedian(telemetry['DistanceToDriverAhead'])

        summarized_distance_ver_ric = summarized_distance_ver_ric.append({
            'Lap': lap[0] + 1,
            'Mean': distance_mean,
            'Median': distance_median
        }, ignore_index=True)

# Plotting the Data

# Need to compare the lap times between RIC and VER and the average distance between them

# First subplot is lap times during the opening stint, second one is the average distance between RIC and VER
plt.rcParams['figure.figsize'] = [10, 6]

fig, ax = plt.subplots(2)
fig.suptitle("RIC vs. VER Opening Stint Comparison")

ax[0].plot(laps_ric["RaceLapNumber"], laps_ric["LapTime"], label="RIC")
ax[0].plot(laps_ver["RaceLapNumber"], laps_ver["LapTime"], label="VER")
ax[0].set(ylabel='Laptime', xlabel='Lap')
ax[0].legend(loc="upper center")

ax[1].plot(summarized_distance_ver_ric["Lap"], summarized_distance_ver_ric["Mean"], label='Mean', color='red')
ax[1].plot(summarized_distance_ver_ric["Lap"], summarized_distance_ver_ric["Median"], label='Median', color='grey')
ax[1].set(ylabel="Distance (meters)", xlabel="Lap")
ax[1].legend(loc="upper center")

# Hides x-labels and tick labels for top plots and y-ticks for right plots

for a in ax.flat:
    a.label_outer()


plt.show()
plt.savefig('ric_ver_stint1.png')
#, dpi=dpi_val)

# VER is close to RIC during lap 4, so let's analyze that

# Load in the telemetry for laps 3, 4, 5, and 6

lap_telemetry_ric = laps_ric.loc[laps_ric['RaceLapNumber'] == 4].get_car_data().add_distance()
lap_telemetry_ver = laps_ver.loc[laps_ver['RaceLapNumber'] == 4].get_car_data().add_distance()

distance_lap3 = full_distance_ver_ric.loc[full_distance_ver_ric['Lap'] == 3]
distance_lap4 = full_distance_ver_ric.loc[full_distance_ver_ric['Lap'] == 4]
distance_lap5 = full_distance_ver_ric.loc[full_distance_ver_ric['Lap'] == 5]
distance_lap6 = full_distance_ver_ric.loc[full_distance_ver_ric['Lap'] == 6]

### Plotting

# Make the plot bigger
plt.rcParams['figure.figsize'] = [15, 15]

fig, ax = plt.subplots(5)
fig.suptitle("Fastest Race Lap Telemetry Comparison")

ax[0].title.set_text("Distance to RIC (m)")
ax[0].plot(distance_lap3['Distance'], distance_lap3['DistanceToDriverAhead'], label='Lap 3', linestyle='dotted', color='grey')
ax[0].plot(distance_lap4['Distance'], distance_lap4['DistanceToDriverAhead'], label='Lap 4')
ax[0].plot(distance_lap5['Distance'], distance_lap5['DistanceToDriverAhead'], label='Lap 5', linestyle='dotted', color='white')
ax[0].plot(distance_lap6['Distance'], distance_lap6['DistanceToDriverAhead'], label='Lap 6', linestyle='dashed', color='lightgrey')
ax[0].legend(loc="lower right")

ax[1].title.set_text("Lap 4 Telemetry")
ax[1].plot(lap_telemetry_ric['Distance'], lap_telemetry_ric['Speed'], label='RIC')
ax[1].plot(lap_telemetry_ver['Distance'], lap_telemetry_ver['Speed'], label='VER')
ax[1].set(ylabel='Speed')
ax[1].legend(loc="lower right")

ax[2].plot(lap_telemetry_ric['Distance'], lap_telemetry_ric['Throttle'], label="RIC")
ax[2].plot(lap_telemetry_ver['Distance'], lap_telemetry_ver['Throttle'], label="VER")
ax[2].set(ylabel="Throttle")

ax[3].plot(lap_telemetry_ric['Distance'], lap_telemetry_ric['Brake'], label="RIC")
ax[3].plot(lap_telemetry_ver['Distance'], lap_telemetry_ver['Brake'], label="VER")
ax[3].set(ylabel="Brakes")

ax[4].plot(lap_telemetry_ric['Distance'], lap_telemetry_ric['DRS'], label="RIC")
ax[4].plot(lap_telemetry_ver['Distance'], lap_telemetry_ver['DRS'], label="VER")
ax[4].set(ylabel="DRS")

# Hide x-labels and tick labels for top plots and y-ticks for the right plots.

for a in ax.flat:
    a.label_outer()

plt.show()
plt.savefig('ric_ver_lap4')
#, dpi=dpi_val)

print("\n Program executed")
