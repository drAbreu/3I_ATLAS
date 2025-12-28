
"""
3I/ATLAS Orbit Determination - Module 5A
Simulates the convergence of the perijove distance estimate as more observations
are collected, demonstrating the collapse of uncertainty onto the true physical encounter.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

def plot_orbital_uncertainty_evolution():
    """
    Creates a plot showing a plausible evolution of the orbital uncertainty for
    3I/ATLAS's perijove distance over time. This uses synthetic data to
    illustrate the scientific process of orbital determination.
    """
    # --- Generate Synthetic Data ---
    discovery_date = datetime(2025, 7, 1)
    days = np.arange(1, 201)
    plot_dates = [discovery_date + timedelta(days=int(d)) for d in days]

    # "True" final value
    true_perijove = 53.6  # million km

    # Initial estimated value
    initial_perijove = 53.445 # million km
    
    # Simulate the best-fit value converging to the true value
    # We use a function that starts at initial_perijove and slowly moves to true_perijove
    convergence_speed = 0.02
    best_fit_perijove = true_perijove + (initial_perijove - true_perijove) * np.exp(-convergence_speed * days)

    # Simulate the uncertainty shrinking over time (proportional to 1/sqrt(N))
    initial_uncertainty = 2.0 # million km
    uncertainty = initial_uncertainty / np.sqrt(days)
    # Ensure uncertainty doesn't start ridiculously large on day 1
    uncertainty[0] = initial_uncertainty / np.sqrt(1.5) 
    # Let's add some noise to make it look more realistic
    noise = np.random.normal(0, 0.05, len(days))
    best_fit_perijove += uncertainty * noise

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the shaded uncertainty region (1-sigma)
    ax.fill_between(plot_dates, best_fit_perijove - uncertainty, best_fit_perijove + uncertainty,
                    color='lightblue', alpha=0.6, label='1-σ Uncertainty')
    
    # Plot the best-fit line
    ax.plot(plot_dates, best_fit_perijove, color='blue', label='Best-Fit Perijove Distance')

    # Plot the Hill Radius and the final "true" value
    hill_radius = 53.5
    ax.axhline(hill_radius, color='red', linestyle='--', label=f"Jupiter Hill Radius ({hill_radius}M km)")
    ax.axhline(true_perijove, color='green', linestyle=':', label=f"Final Converged Value ({true_perijove}M km)")

    # --- Style and Annotations ---
    ax.set_title('Evolution of 3I/ATLAS Perijove Distance Estimate Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Closest Approach to Jupiter (million km)')
    
    # Format the x-axis for dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()

    # Mark key dates
    key_dates = {
        "Discovery": discovery_date,
        "Perihelion": datetime(2025, 10, 29),
    }
    for label, date in key_dates.items():
        if date < plot_dates[-1]:
            ax.axvline(date, color='black', linestyle='-.', alpha=0.5)
            ax.text(date + timedelta(days=2), ax.get_ylim()[1]*0.95, label, 
                    rotation=90, verticalalignment='top', fontsize=9)

    ax.legend(loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Set y-axis limits to focus on the convergence
    final_plus_minus = uncertainty[-1] * 2
    ax.set_ylim(true_perijove - (initial_perijove-true_perijove)*2 - final_plus_minus, 
                true_perijove + (initial_perijove-true_perijove)*2 + initial_uncertainty*0.5)


    fig.tight_layout()
    plt.savefig('visualizations/jupiter_intercept/plot_5a_orbital_uncertainty.png')
    plt.close()


if __name__ == '__main__':
    plot_orbital_uncertainty_evolution()
    print("Plot saved to visualizations/jupiter_intercept/plot_5a_orbital_uncertainty.png")
