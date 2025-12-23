
# Monte Carlo Orbit Simulation for 3I/ATLAS

This document outlines the process and results of a Monte Carlo simulation performed to analyze the trajectory of the interstellar object 3I/ATLAS and its close approaches to the planets in our Solar System.

## 1. Purpose

The primary goal of this analysis is to determine the statistical likelihood of 3I/ATLAS passing close to planets in our Solar System. By simulating a large number of scenarios with randomized initial conditions, we can estimate the probability of observing the close approaches that have been recorded. This helps us to understand if the trajectory of 3I/ATLAS is statistically remarkable or within the range of expected outcomes for an object with its orbital parameters.

## 2. Tools Used

The simulation and analysis were conducted using a Python script, leveraging the following open-source libraries:

-   **NumPy**: For numerical operations and array handling.
-   **Pandas**: for data manipulation and storage in CSV format.
-   **Matplotlib**: For generating plots and histograms.
-   **Skyfield**: For high-precision planetary position calculations using the DE421 ephemeris.

## 3. Methodology

### 3.1. Simulation Setup

The simulation is based on the orbital elements of 3I/ATLAS, which have been obtained from the JPL Small-Body Database. The core of the simulation is a Python script located at `analyses/montecarlo_orbit_simulation/simulation.py`.

The simulation performs 10,000 trials. In each trial, the orbital parameters of 3I/ATLAS are kept constant, but the time of its perihelion passage is randomized over a 130-year period (from 1910 to 2040). This effectively creates 10,000 different scenarios of the Solar System's planetary configuration at the time of the object's passage.

### 3.2. Trajectory Propagation

For each of the 10,000 trials, the trajectory of 3I/ATLAS is propagated for a period of 4000 days (approximately 11 years) centered around its perihelion. The positions of the planets are calculated at each step of the propagation using the Skyfield library.

### 3.3. Hit Calculation

A "hit" is defined as a close approach of 3I/ATLAS to a planet within a certain distance. The simulation checks for hits at the following distances: 25, 50, 75, 100, 125, and 150 million kilometers.

The minimum distance between 3I/ATLAS and each of the eight planets is calculated for each simulation. If this distance is less than or equal to any of the predefined hit distances, it is recorded as a hit. For the "Hits per Planet" visualization, distributions for all these thresholds are shown.

## 4. How to Run the Simulation

The simulation can be run by executing the following command from the root directory of the project:

```bash
python analyses/montecarlo_orbit_simulation/simulation.py
```

The script will run for a significant amount of time due to the large number of simulations. Once completed, it will generate the data and plot files described below.

## 5. Expected Output

The simulation generates the following output files:

-   `data/montecarlo_orbit_simulation/montecarlo_simulation_min_distances.csv`: A CSV file containing the minimum distance (in AU) between 3I/ATLAS and each planet for each of the 10,000 simulations.
-   `data/montecarlo_orbit_simulation/montecarlo_orbit_simulation_hits.csv`: A CSV file containing detailed information about each recorded hit, including the simulation ID, the planet, the minimum distance, and the hit distance.
-   `visualizations/montecarlo_orbit_simulation/hits_per_planet.png`: A histogram showing the number of simulations that resulted in a hit for each planet.
-   `visualizations/montecarlo_orbit_simulation/hits_per_simulation.png`: A histogram showing the distribution of the number of planets hit per simulation.

## 6. Results

After running the simulation, the generated plots will be available in the `visualizations/montecarlo_orbit_simulation/` directory.

### 6.1. Hits per Planet

This histogram shows how many simulations resulted in at least one close approach for each planet, categorized by distance thresholds (25, 50, 75, 100, 125, 150 MKM). Planets are ordered by their distance from the Sun.

![Hits per Planet](../visualizations/montecarlo_orbit_simulation/hits_per_planet.png)

### 6.2. Hits per Simulation

This histogram shows the distribution of the number of planets hit in a single simulation at the maximum distance threshold (150 MKM). It includes the count for zero hits.

![Hits per Simulation](../visualizations/montecarlo_orbit_simulation/hits_per_simulation.png)

### 6.3. P-value Calculation

The simulation calculates the p-value for the observed close approaches of 3I/ATLAS to Venus, Mars, and Jupiter. 

A joint p-value is also calculated to represent the fraction of simulations where all three close approaches occurred simultaneously. This accounts for the inherent dependencies in the orbital configuration, providing a more accurate assessment than simply multiplying individual p-values.

Detailed results and the calculated joint p-value can be found in the [Results Report](../results/montecarlo_orbit_simulation/README.md).
