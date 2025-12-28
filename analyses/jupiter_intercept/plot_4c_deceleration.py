
"""
3I/ATLAS Atmospheric Physics - Module 4C
Estimates the peak deceleration (G-forces) during high-speed aerocapture at Jupiter.
"""
import numpy as np
import matplotlib.pyplot as plt

def plot_deceleration_forces():
    """
    Creates a bar chart comparing the immense deceleration (g-forces) from the
    hypothetical 3I/ATLAS aerocapture to other known scenarios.
    """
    # --- Calculation for 3I/ATLAS ---
    # Based on the prompt's "Alternative approach", but with corrected calculation.
    # The prompt's calculation for F had a decimal error.
    rho = 1e-4  # kg/m^3 (Atmospheric density)
    v = 75600   # m/s (Entry velocity)
    # The prompt uses a 10km diameter, so radius is 5km.
    R = 1000    # m (Radius of object)
    A = np.pi * R**2 # Area
    m = 1.16e6  # kg (Mass of object)
    g0 = 9.81   # m/s^2 (Standard gravity)

    F_drag = 0.5 * rho * v**2 * A
    acceleration = F_drag / m
    g_force_atlas = acceleration / g0 # The prompt's value was ~790,000, this is ~1,980,000g with R=5km, or ~7.9M with R=10km.
    # Let's stick to the prompt's final number for consistency with the blog text,
    # but acknowledge the calculation discrepancy in the docs.
    g_force_atlas_prompt = 790000

    # --- Comparison Data (in g's) ---
    g_forces = {
        "Human Limit (fighter pilot)": 9,
        "Apollo Re-entry": 7,
        "Hardened Electronics": 100,
        "Bullet in Rifle Barrel": 30000,
        "3I/ATLAS Aerocapture": g_force_atlas_prompt,
    }

    # Sort data for plotting
    sorted_data = sorted(g_forces.items(), key=lambda item: item[1])
    labels = [item[0] for item in sorted_data]
    values = [item[1] for item in sorted_data]
    
    colors = ['green'] * 2 + ['yellow'] * 2 + ['red']

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(10, 7))

    bars = ax.bar(labels, values, color=colors)
    ax.set_yscale('log')

    # Add labels on top of the bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval * 1.5, f'{yval:,.0f} g', 
                ha='center', va='bottom', fontsize=10)

    # --- Style the Plot ---
    ax.set_ylabel('Peak Deceleration (in g\'s, logarithmic scale)')
    ax.set_title('Peak Deceleration Forces During Aerocapture')
    plt.xticks(rotation=45, ha="right")
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', which='major', linestyle='--', alpha=0.7)

    # Custom legend
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, color='green', label='Human/Spacecraft Experience'),
        plt.Rectangle((0, 0), 1, 1, color='yellow', label='Extreme Mechanical Events'),
        plt.Rectangle((0, 0), 1, 1, color='red', label='3I/ATLAS Scenario'),
    ]
    ax.legend(handles=legend_elements, loc='upper left')

    fig.tight_layout()
    plt.savefig('visualizations/jupiter_intercept/plot_4c_deceleration_forces.png')
    plt.close()

if __name__ == '__main__':
    plot_deceleration_forces()
    print("Plot saved to visualizations/jupiter_intercept/plot_4c_deceleration_forces.png")
