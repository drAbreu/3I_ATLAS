"""
3I/ATLAS Technology Comparison - Module 2B
Compares the Delta-V of current human propulsion systems (Apollo, Dawn)
against the extreme requirements of an interstellar intercept or rendezvous mission.
"""
import numpy as np
import matplotlib.pyplot as plt
import os

def plot_mission_energy_comparison():
    """
    Generates a comparison of mission energy requirements (C3) and spacecraft capabilities.
    Distinguishes between launch vehicle energy and spacecraft propulsion.
    """
    
    # Data organized by category
    data = {
        # Spacecraft on-board propulsion systems (what they can do AFTER launch)
        "Spacecraft Propulsion": {
            "Apollo CSM": {"value": 2.8, "color": "green", "ref": "NASA Apollo specs"},
            "Dawn (Ion Drive)": {"value": 11.5, "color": "green", "ref": "NASA JPL"},
            "Deep Space 1 (Ion)": {"value": 4.5, "color": "green", "ref": "NASA DS1"},
        },
        
        # Launch vehicle capabilities (what rockets can achieve)
        "Launch Vehicle Capability": {
            "New Horizons Launch C3": {"value": 16.5, "color": "blue", "ref": "NASA New Horizons"},
            "Parker Launch C3": {"value": 19.5, "color": "blue", "ref": "NASA Parker"},
        },
        
        # Theoretical limits
        "Theoretical/Future": {
            "Advanced Ion Drive": {"value": 45.0, "color": "yellow", "ref": "Isp~10,000s limit"},
        },
        
        # 3I/ATLAS requirements
        "3I/ATLAS Requirements": {
            "Intercept (Hibberd et al. 2025)": {"value": 5.0, "color": "orange", "ref": "Hibberd et al. 2025"},
            "Intercept (This post)": {"value": 27.0, "color": "red", "ref": "Independent calc"},
            "Rendezvous (Minimum)": {"value": 43.8, "color": "darkred", "ref": "Lambert analysis"},
        },
    }
    
    # Flatten for plotting
    labels = []
    values = []
    colors = []
    references = []
    
    for category, items in data.items():
        for name, info in items.items():
            labels.append(name)
            values.append(info["value"])
            colors.append(info["color"])
            references.append(info["ref"])
    
    # Sort by value
    sorted_indices = np.argsort(values)
    labels = [labels[i] for i in sorted_indices]
    values = [values[i] for i in sorted_indices]
    colors = [colors[i] for i in sorted_indices]
    references = [references[i] for i in sorted_indices]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 9))
    
    bars = ax.barh(labels, values, color=colors, edgecolor='black', alpha=0.8, linewidth=1.5)
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                f'{width:.1f} km/s', 
                ha='left', va='center', fontweight='bold', fontsize=10)
    
    # Style
    ax.set_xlabel('Velocity Capability or Requirement (km/s)', fontsize=14, fontweight='bold')
    ax.set_title('Interstellar Intercept Energy Requirements\nvs. Achieved Spacecraft Capabilities', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(right=max(values) * 1.15)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', edgecolor='black', label='Achieved (Spacecraft Propulsion)'),
        Patch(facecolor='blue', edgecolor='black', label='Achieved (Launch Vehicle)'),
        Patch(facecolor='yellow', edgecolor='black', label='Theoretical Future Tech'),
        Patch(facecolor='orange', edgecolor='black', label='3I/ATLAS Intercept (Hibberd et al. 2025)'),
        Patch(facecolor='red', edgecolor='black', label='3I/ATLAS Intercept (This post)'),
        Patch(facecolor='darkred', edgecolor='black', label='3I/ATLAS Rendezvous (Minimum)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11, framealpha=0.95)
    
    # Add reference annotations
    plt.figtext(0.5, 0.02, 
                'Note: Launch vehicle values (C₃ energy) represent what rockets achieved at launch.\n' +
                'Spacecraft values represent onboard propulsion capability after launch separation.\n' +
                '3I/ATLAS values show velocity change needed for trajectory modification.',
                ha='center', fontsize=9, style='italic',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    
    # Save
    output_path = 'visualizations/jupiter_intercept/plot_2b_energy_comparison_corrected.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Corrected plot saved to {output_path}")
    plt.close()
    
    # Print sources
    print("\nSOURCES FOR VERIFICATION:")
    print("="*80)
    for label, ref in zip(labels, references):
        print(f"{label:40s} → {ref}")

if __name__ == '__main__':
    plot_mission_energy_comparison()