from astroquery.jplhorizons import Horizons
from astropy.time import Time
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

# constants
GM = 2.95929739849e-4 # AU^3 / day^2

# initialize planet metadata
def InitializePlanets(planetids, colors):
  planets = []
  for i in range(len(planetids)):
    planet_hor = Horizons(id=planetids[i], location='@sun', epochs=start_time_jd).vectors()
    r = np.array([np.double(planet_hor[ri]) for ri in ['x', 'y', 'z']])
    v = np.array([np.double(planet_hor[vi]) for vi in ['vx', 'vy', 'vz']])
    planet = {
        'r'     : r,
        'v'     : v,
        'point' : ax.scatter(r[0], r[1], color=colors[i]),
        'xs'    : [],
        'ys'    : [] # xs and ys to keep track of for trail
    }
    planets.append(planet)
  return planets

# acceleration calculation
def a(planet):
  return (-GM * planet['r'] / (np.sum(planet['r']**2))**(3.0/2))

# timestep for each planet
def StepPlanet(planet, positions, trails, trail, dt):
  # update positions
  planet['v'] += a(planet) * dt
  planet['r'] += planet['v'] * dt
  planet['point'].set_offsets(planet['r'][:2])
  positions.append(planet['point'])

  # update trails
  planet['xs'].append(planet['r'][0])
  planet['ys'].append(planet['r'][1])
  trail.set_xdata(planet['xs'])
  trail.set_ydata(planet['ys'])
  trails.append(trail)

# timestep for the whole system
def StepSolarSystem(planets, time, dt, timestamp):
  planets_positions = []
  planets_trails = []
  for planet in planets:
    trail, = ax.plot([], [], color = 'white', linewidth=1.4)
    StepPlanet(planet, planets_positions, planets_trails, trail, dt)
  time += dt
  timestamp.set_text('Date: ' + Time(time, format='jd').iso)
  return (planets_positions + planets_trails + [timestamp], time)

# adjustable parameters
start_time_yyyy_mm_dd = '1960-01-01'
dt = 1.5
mode = 'all' # can either be 'terrestrial' or 'all' 

# converted parameters
start_time_jd = Time(start_time_yyyy_mm_dd).jd
time = start_time_jd
if (mode == 'terrestrial'):
  timeframe = (int)(2 * 365 / dt) # number of timesteps
  planetids = [199, 299, 399, 499]
  colors = ['red', 'orange', 'limegreen', 'chocolate']
  plot_limits = (-2,2)
  animate_interval = 20.0
elif (mode == 'all'):
  timeframe = (int)(200 * 365 / dt) # number of timesteps
  planetids = [199, 299, 399, 499, 599, 699, 799, 899]
  colors = ['red', 'orange', 'limegreen', 'chocolate', 'goldenrod', 'wheat', 'paleturquoise', 'deepskyblue']
  plot_limits = (-31,31)
  animate_interval = 1.0

# create plot
plt.style.use('dark_background')
fig = plt.figure(figsize=[6, 6])
ax = plt.axes([0., 0., 1., 1.], xlim=plot_limits, ylim=plot_limits)
ax.scatter(0, 0, color='white') # this is the Sun
timestamp = ax.text(.22, .95, 'Date: ', transform=ax.transAxes, fontsize='x-large')

# initialize planets
planets = InitializePlanets(planetids, colors)

# animate
def animate(i):
  global time
  if i % (timeframe//10) == 0:  # Print on every 10% of total timeframe
    print(f"Frame: {i+1}/{timeframe} ({100*(i+1)/timeframe:.0f}%)")
  elif i == timeframe-1:
    print("Simulation complete!")
  result, time = StepSolarSystem(planets, time, dt, timestamp)
  return result

ani = animation.FuncAnimation(fig, animate, repeat=False, frames=timeframe, blit=True, interval=animate_interval)
plt.show()