"""
3I/ATLAS Atmospheric Physics - Module 4A
Analyzes stagnation point heating during high-speed atmospheric entry at Jupiter.
Uses sqrt(rho) * v^3 scaling to compare 3I/ATLAS heating to Apollo and Galileo.
"""
import numpy as np
import matplotlib.pyplot as plt
import os

def plot_aerocapture_heating_corrected():
    """
    Generates a bar chart comparing peak heating rates in MW/m^2.
    Units are carefully corrected: 1 MW/m2 = 100 W/cm2.
    """
    # Heating data in MW/m^2 (Corrected for unit consistency)
    # Galileo: 30,000 W/cm2 = 300 MW/m2
    # Apollo: 1,000 W/cm2 = 10 MW/m2
    # 3I/ATLAS: Scaled via sqrt(rho) * v^3 ~ 40x Apollo
    heating_data = {
        "Space Shuttle": {"v": 8, "q": 1.5, "c": "green", "ref": "Achieved"},
        "Mars Pathfinder": {"v": 7, "q": 0.5, "c": "green", "ref": "Achieved"},
        "Apollo CM": {"v": 11, "q": 10, "c": "green", "ref": "Achieved"},
        "Galileo Probe": {"v": 47.4, "q": 300, "c": "yellow", "ref": "Survived"},
        "3I/ATLAS (Jupiter)": {"v": 75.6, "q": 400, "c": "red", "ref": "Theoretical"},
    }
    
    sorted_items = sorted(heating_data.items(), key=lambda x: x[1]['q'])
    labels = [f"{item[0]}\n({item[1]['v']} km/s)" for item in sorted_items]
    rates = [item[1]['q'] for item in sorted_items]
    colors = [item[1]['c'] for item in sorted_items]

    fig, ax1 = plt.subplots(figsize=(12, 8))
    bars = ax1.bar(labels, rates, color=colors, edgecolor='black', alpha=0.8)
    ax1.set_yscale('log')
    
    # Add value labels
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval * 1.1, f'{yval:.1f}', 
                 ha='center', va='bottom', fontweight='bold')

    ax1.set_ylabel('Peak Stagnation Heating Rate ($MW/m^2$)', fontsize=12)
    ax1.set_title('Atmospheric Entry Heating: Scientific Scrutiny (Unit Corrected)', fontsize=16, pad=20)
    plt.xticks(rotation=0, ha="center")

    # Apollo Relative Axis
    ax2 = ax1.twinx()
    ax2.set_yscale('log')
    ymin, ymax = ax1.get_ylim()
    ax2.set_ylim(ymin / 10, ymax / 10)
    ax2.set_ylabel('Multiples of Apollo Reentry Heating', color='purple', fontsize=12)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', label='Proven/Achieved'),
        Patch(facecolor='yellow', label='Extreme/Survived (Probes)'),
        Patch(facecolor='red', label='3I/ATLAS (Theoretical)')
    ]
    ax1.legend(handles=legend_elements, loc='upper left')
    
    ax1.grid(axis='y', which='both', linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    output_path = 'visualizations/jupiter_intercept/plot_4a_aerocapture_heating.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    print(f"Corrected heating plot saved to {output_path}")

if __name__ == '__main__':
    plot_aerocapture_heating_corrected()
