
"""
3I/ATLAS Atmospheric Physics - Module 4B
Calculates the specific kinetic energy dissipation required for aerocapture at Jupiter.
"""
import numpy as np
import matplotlib.pyplot as plt

def plot_energy_infographic():
    """
    Creates an infographic-style plot to visualize the immense kinetic energy
    that would need to be dissipated during a hypothetical 3I/ATLAS aerocapture.
    """
    # --- Calculations ---
    # Kinetic Energy
    mass_atlas = 1.16e6  # kg (1,160 tonnes)
    vel_atlas = 75.6e3   # m/s (75.6 km/s)
    ke_atlas = 0.5 * mass_atlas * vel_atlas**2  # Joules

    # Comparison energies (in Joules)
    energies = {
        "Apollo Re-entry": 1.5e10,
        "Space Shuttle Re-entry": 1.4e11,
        "Hiroshima Bomb": 6.3e13,
        "Tsar Bomba (Largest H-Bomb)": 2.1e17,
    }

    # Power
    aerocapture_time = 45  # seconds
    power_atlas = ke_atlas / aerocapture_time  # Watts
    us_power_capacity = 1.2e12  # Watts (1.2 TW)

    # --- Visualization ---
    fig = plt.figure(figsize=(12, 8))
    
    # Use GridSpec for layout
    gs = fig.add_gridspec(2, 2, height_ratios=[2, 1])
    ax_energy = fig.add_subplot(gs[0, :])
    ax_power_label = fig.add_subplot(gs[1, 0])
    ax_power_value = fig.add_subplot(gs[1, 1])
    
    # --- Energy Comparison Plot (Top) ---
    ax_energy.set_title('Kinetic Energy to Dissipate During Aerocapture', fontsize=16, pad=20)

    # Convert everything to Hiroshima bomb equivalents for plotting
    hiroshima_eq = ke_atlas / energies["Hiroshima Bomb"]
    other_eq = {name: val / energies["Hiroshima Bomb"] for name, val in energies.items()}

    bar_labels = [f"3I/ATLAS Aerocapture\n({hiroshima_eq:.0f}x Hiroshima)"]
    bar_values = [hiroshima_eq]
    
    ax_energy.barh(bar_labels, bar_values, color='red', height=0.6)
    
    # Add text explaining the other comparisons
    text_y = -0.6
    for name, val in energies.items():
        factor = ke_atlas / val
        ax_energy.text(0, text_y, f'Equivalent to ~{factor:,.0f} x {name} events', 
                       ha='left', va='center', fontsize=12)
        text_y -= 0.2

    ax_energy.set_xscale('log')
    ax_energy.set_xlabel('Energy Equivalent (in multiples of Hiroshima bomb yield)')
    ax_energy.grid(axis='x', linestyle='--', alpha=0.7)
    ax_energy.spines['top'].set_visible(False)
    ax_energy.spines['right'].set_visible(False)
    ax_energy.spines['left'].set_visible(False)
    ax_energy.get_yaxis().set_visible(False)
    ax_energy.set_ylim(-1.5, 0.5)

    # --- Power Comparison Plot (Bottom) ---
    for ax in [ax_power_label, ax_power_value]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

    # Bottom left for the label
    ax_power_label.set_ylim(0,1)
    ax_power_label.set_xlim(0,1)
    ax_power_label.text(0.95, 0.5, 'Average Power\nDissipation\n(in < 1 minute)', 
                      ha='right', va='center', fontsize=14, weight='bold')

    # Bottom right for the value
    power_factor = power_atlas / us_power_capacity
    ax_power_value.set_ylim(0,1)
    ax_power_value.set_xlim(0,1)
    ax_power_value.text(0.05, 0.5, f'~{power_atlas/1e12:.0f} Terawatts\n~{power_factor:.0f}x Total US Power Capacity',
                        ha='left', va='center', fontsize=14, color='red')

    fig.suptitle('The Immense Energy of the 3I/ATLAS Aerocapture Scenario', fontsize=20, weight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    
    plt.savefig('visualizations/jupiter_intercept/plot_4b_energy_dissipation.png')
    plt.close()

if __name__ == '__main__':
    plot_energy_infographic()
    print("Plot saved to visualizations/jupiter_intercept/plot_4b_energy_dissipation.png")
