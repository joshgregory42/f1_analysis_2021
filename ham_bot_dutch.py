import fastf1 as ff1
from fastf1 import plotting

from matplotlib import pyplot as plt
from matplotlib.pyplot import figure

# DPI value for plotting
dpi_val = 1500

# Set up plotting
plotting.setup_mpl()

# Enable the cache
ff1.Cache.enable_cache('C:/Users/Josh Gregory/OneDrive - UCB-O365/Current Projects/F1 Analysis '
                       'Python/ham_bot_dutch/ham_bot_dutch_cache')

# Loading the session data
race = ff1.get_session(2021, 'Zandvoort', 'R')

# Collecting all race laps with telemetry
laps = race.load_laps(with_telemetry=True)

# Getting the laps of BOT and HAM
laps_bot = laps.pick_driver('BOT')
laps_ham = laps.pick_driver('HAM')


# Get the fastest laps without telemetry
fastest_bot = laps_bot.pick_fastest()
fastest_ham = laps_ham.pick_fastest()

# Get telemetry from fastest laps
telemetry_bot = fastest_bot.get_car_data().add_distance()
telemetry_ham = fastest_ham.get_car_data().add_distance()

# Plotting the data using subplots; one for speed, throttle, and brake
fig, ax = plt.subplots(3)
fig.suptitle("BOT vs. HAM Fastest Race Lap Telemetry Comparison")

# Create subplots for each driver

ax[0].plot(telemetry_bot['Distance'], telemetry_bot['Speed'], label='BOT')
ax[0].plot(telemetry_ham['Distance'], telemetry_ham['Speed'], label='HAM')
ax[0].set(ylabel='Speed')
ax[0].legend(loc='lower right')

ax[1].plot(telemetry_bot['Distance'], telemetry_bot['Throttle'], label='BOT')
ax[1].plot(telemetry_ham['Distance'], telemetry_ham['Throttle'], label='HAM')
ax[1].set(ylabel='Throttle')

ax[2].plot(telemetry_bot['Distance'], telemetry_bot['Brake'], label='BOT')
ax[2].plot(telemetry_ham['Distance'], telemetry_ham['Brake'], label='HAM')
ax[2].set(ylabel='Brakes')


# Hide x-labels and tick labels for top plots and y ticks for right plots.
for a in ax.flat:
    a.label_outer()


plt.savefig("ham_vs_bot_dutch_image.png", dpi=dpi_val)
plt.show()


print("\n Program Executed")
