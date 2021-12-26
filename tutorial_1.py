# Tutorial link: https://medium.com/towards-formula-1-analysis/how-i-analyze-formula-1-data-with-python-2021-italian-gp-dfb11db4b73

# Last edited: 12/19/21
# On "Next, what we need to do is loop through all the laps one by one."


# Importing all the necessary libraries

import fastf1 as ff1 # Pulls all the necessary data from the fastf1 api
from fastf1 import plotting
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import numpy as np
import pandas as pd


# Setup plotting

plotting.setup.mpl()


# Enabling the cache to prevent long wait times

ff1.Cache.enable_cache('../cache')

# Get rid of some pandas warnings that don't matter

pd.options.mode.chaines_assignment = None

# Loading in the session data

race = ff1.get_session(2021, 'Monza', 'R')

# Load all laps with telemetry

laps = race.load_laps(with_telemetry=True)


# Select drivers of interest

laps_ric = laps.pick_driver('RIC')
laps_ver = laps.pick_driver('VER')


# Only select first sting since Ver and Ham crashed early

laps_ric = laps_ric.loc[laps_ric['Stint']==1]
laps_ver = laps_ver.loc[laps_ric['Stint']==1]


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



