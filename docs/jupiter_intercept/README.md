# Module 2: Jupiter Intercept & Proximity Analysis

This module contains the scientific analysis of 3I/ATLAS's encounter with Jupiter in March 2026. We explore the trajectory, the energy required to intercept it, and the statistical likelihood of its close approach.

## 📁 Directory Structure

- `analyses/`: Python scripts using `poliastro`, `skyfield`, and `astropy`.
- `visualizations/`: High-resolution plots.
- `docs/`: Detailed methodology for each plot.

## 📊 Core Analyses

### 1. Proximity & Probability
- **[Plot 1A: Meaningful Radii](plot_1a_radii_chart.md)** - Visualizing Jupiter's gravitational boundaries.
- **[Plot 1C: Approach Distribution](plot_1c_monte_carlo.md)** - Analyzing 10,000 near-Jupiter visitors.
- **[Plot 1D: Radii Penetration](plot_1d_monte_carlo.md)** - The 50/50 likelihood of entering the Hill Radius.

### 2. The Intercept Mission
- **[Plot 2A: Paper Reproduction](plot_2a_paper_reproduction.md)** - Verifying the 5 km/s "nudge" claim.
- **[Plot 2A: Reality Check](plot_2a_current_reality.md)** - Why the real cost is 27+ km/s.
- **[Plot 2B: Tech Comparison](plot_2b_technology_comparison.md)** - Humans vs. Interstellar technology.

### 3. Rendezvous & Propulsion
- **[Plot 3A: Porkchop Plot](plot_3a_rendezvous_porkchop.md)** - The scan of all possible mission windows.
- **[Plot 3B: Energy Budget](plot_3b_energy_budget.md)** - Characteristic Energy ($C_3$) requirements.
- **[Plot 3C: Rocket Equation](plot_3c_rocket_equation.md)** - Translating $\Delta V$ into fuel mass.

### 4. Extreme Reentry (Aerocapture)
- **[Plot 4A: Stagnation Heating](plot_4a_aerocapture_heating.md)** - 40,000x hotter than Apollo.
- **[Plot 4B: Energy Dissipation](plot_4b_energy_dissipation.md)** - Kinetic energy release.
- **[Plot 4C: Deceleration G-Forces](plot_4c_deceleration.md)** - The mechanical limits of the spacecraft.

### 5. Uncertainty
- **[Plot 5A: Orbital Evolution](plot_5a_orbital_uncertainty.md)** - How our knowledge of the path converges over time.

---

**Note:** All scripts use the **Heliocentric Ecliptic J2000** frame to ensure perfect synchronization between ephemeris data and orbital mechanics solvers.

