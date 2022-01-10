# Importing everything
import fastf1 as ff1
from fastf1 import plotting
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.collections import LineCollection
from matplotlib import cm
import numpy as np
import pandas as pd

# Set up plotting
plotting.setup_mpl()

# Enabling cache
ff1.Cache.enable_cache(
    '../path_to_cache')
# Get rid of some pandas warnings that are not relevant
pd.options.mode.chained_assignment = None

# Loading session data
race = ff1.get_session(2021, 'Russia', 'R')

# Get laps
laps = race.load_laps(with_telemetry=True)

# Rain started falling on lap 45, so get laps from when the rain started onwards
laps['RaceLapNumber'] = laps['LapNumber'] - 1

# Starting from lap 45 it started raining
laps = laps.loc[laps['RaceLapNumber'] >= 45]

# To get a lap-by-lap comparison, we need lap-by-lap telemetry. Fastf1 only gives us telemetry per driver, so we need
# to do a few loops to get the data in the correct format.

# Get all drivers
drivers = pd.unique(laps['Driver'])

telemetry = pd.DataFrame()

# Telemetry can only be retrieved driver-by-driver

# First looping through all of the drivers, then select each of the laps that belong to that driver.
# Then loop through all of the laps for that driver with telemetry using iterlaps.
# Iterlaps is similar to Pandas's iterrows().
for driver in drivers:
    driver_laps = laps.pick_driver(driver)

    # Since we want to compare distances, we need to collect telemetry lap-by-lap to reset the distance
    for lap in driver_laps.iterlaps():
        driver_telemetry = lap[1].get_telemetry().add_distance()
        driver_telemetry['Driver'] = driver
        driver_telemetry['Lap'] = lap[1]['RaceLapNumber']
        driver_telemetry['Compound'] = lap[1]['Compound']

        telemetry = telemetry.append(driver_telemetry)

# Only keep the required columns and change all of the hard, medium, and soft compounds to say "slick"

telemetry = telemetry[['Lap', 'Distance', 'Compound', 'Speed', 'X', 'Y']]

# Everything that's not intermediate will be "slick"
telemetry['Compound'].loc[telemetry['Compound'] != 'INTERMEDIATE'] = 'SLICK'

## Creating the mini-sectors and calculate the fastest compounds
# Split the lap into 25 equally-sized mini sectors
# Assign every row in the telemetry data with the mini-sector it currently is in based on the lap distance
# Group by lap, mini-sector, and compound and calculate the average speed to see which compound is
# faster at what point during the lap


# Create the mini-sectors

# Want 25 mini-sectors
num_minisectors = 25

# Finding the total distance of a lap
total_distance = max(telemetry['Distance'])

# Generate equally sized mini-sectors
minisector_length = total_distance / num_minisectors

minisectors = [0]

for i in range(0, (num_minisectors - 1)):
    minisectors.append(minisector_length * (i + 1))

# Assign mini-sector to every row in the telemetry data

# Create a column Minisector in the Telemetry dataframe, which runs a calculation based on what is stored in
# the column Distance

# Based on the distance, we can see to what index the minisector list the distance actually belongs.
# The index number is the mini-sector number.
telemetry['Minisector'] = telemetry['Distance'].apply(
    lambda z: (
            minisectors.index(
                min(minisectors, key=lambda x: abs(x - z))) + 1
    )
)

# Calculating the average speed per mini-sector.
# Group by lap, mini-sector, and compound, then calculate the average speed.
average_speed = telemetry.groupby(['Lap', 'Minisector', 'Compound'])['Speed'].mean().reset_index()

# Use idmax() function to find the ID of the row with the highest speed per lap per minisector.

# Select the compound with the highest average speed
fastest_compounds = average_speed.loc[average_speed.groupby(['Lap', 'Minisector'])['Speed'].idxmax()]

# Get rid of the speed column and rename the Compound column
fastest_compounds = fastest_compounds[['Lap', 'Minisector', 'Compound']].rename(
    columns={'Compound': 'Fastest_compound'})

## Merge the telemetry data with the fastest compound per sector, order the telemetry data by distance to make the plot
# fine, and assign an integer value to the tire compound, since Matplotlib can only take integer values here.

# Join the fastest compound per minisector with the full telemetry
telemetry = telemetry.merge(fastest_compounds, on=['Lap', 'Minisector'])

# Order the data by distance to make matplotlib not freak out
telemetry = telemetry.sort_values(by=['Distance'])

# Assign integer value to the compound because that's what Matplotlib takes
telemetry.loc[telemetry['Fastest_compound'] == 'INTERMEDIATE', 'Fastest_compound_int'] = 1
telemetry.loc[telemetry['Fastest_compound'] == 'SLICK', 'Fastest_compound_int'] = 2


## Plotting the data


# Want to generate separate plots per lap, so put the code into a method to make things easier

def generate_minisector_plot(lap, save=False, details=True):
    # Get telemetry of specific lap
    single_lap = telemetry.loc[telemetry['Lap'] == lap]

    # Coordinates of the car on the track at that point in time. Draws the circuit in the plot
    x = np.array(single_lap['X'].values)
    y = np.array(single_lap['Y'].values)

    # Combine the x and y coordinates together to become points to form segments. Then convert this compound variable
    # to a nympy variable
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    compound = single_lap['Fastest_compound_int'].to_numpy().astype(float)

    # cmap is ColorMap and defines the colors of the plot
    # LineCollection combines the previously-created segments into a line, which forms the shape of the circuit
    cmap = cm.get_cmap('ocean', 2)
    lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N + 1), cmap=cmap)
    lc_comp.set_array(compound)
    lc_comp.set_linewidth(2)

    plt.rcParams['figure.figsize'] = [12, 5]

    if details:
        title = plt.suptitle(
            f"2021 Russian GP \n Lap {lap} - Slicks vs. Inters"
        )

    plt.gca().add_collection(lc_comp)
    plt.axis('equal')
    plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    if details:
        cbar = plt.colorbar(mappable=lc_comp, boundaries=np.arange(1, 4))
        cbar.set_ticks(np.arange(1.5, 9.5))
        cbar.set_ticklabels(['Inters', 'Slicks'])

    if save:
        plt.savefig("../path_to_images/minisectors_lap_{lap}.png", dpi=300)

    plt.show()


# Calling the function
generate_minisector_plot(46, save=True, details=False)

print("\nProgram executed")
