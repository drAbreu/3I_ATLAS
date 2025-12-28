"""
3I/ATLAS Monte Carlo Analysis - Module 1D
Likelihood analysis of penetrating Jupiter's significant gravitational radii.
This script uses the results from 1C to calculate the percentage of passing
trajectories that enter the Hill sphere, Lagrange points, and moon orbits.
"""
import numpy as np
import matplotlib.pyplot as plt
import os

# --- Constants ---
AU_KM = 149597870.7

SIGNIFICANT_RADII = {
    'L3 (Opposite)': 1560.0,
    'L4 (Greeks)': 778.0,
    'L5 (Trojans)': 778.0,
    'L2 Point': 54.0,
    'Hill Radius': 53.5,
    'L1 Point': 52.0,
    'Callisto Orbit': 1.88,
    'Ganymede Orbit': 1.07,
    'Europa Orbit': 0.67,
    'Io Orbit': 0.42,
    'Jupiter Surface': 0.071
}

BASELINE_THRESHOLD_MKM = 100.0

def plot_1d_results():
    input_path = 'data/jupiter_intercept/monte_carlo_1c_results.csv'
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Run plot_1c_monte_carlo.py first.")
        return

    distances_au = np.loadtxt(input_path, delimiter=',')
    distances_mkm = distances_au * AU_KM / 1e6
    n_cases = len(distances_mkm)

    hit_counts = {}
    for name, radius in SIGNIFICANT_RADII.items():
        count = np.sum(distances_mkm <= radius)
        hit_counts[name] = count
    
    sorted_hits = sorted(hit_counts.items(), key=lambda x: SIGNIFICANT_RADII[x[0]], reverse=True)
    names = [x[0] for x in sorted_hits]
    counts = [x[1] for x in sorted_hits]
    percentages = [c / n_cases * 100 for c in counts]

    plt.figure(figsize=(12, 10))
    bars = plt.barh(names, percentages, color='salmon', edgecolor='black', alpha=0.8)
    
    plt.xlabel(f'Percentage of Passing Trajectories (%)', fontsize=12)
    plt.title(f'Monte Carlo 1D: Likelihood of Penetrating Jupiter\'s Significant Radii\n(Baseline: Trajectories within {BASELINE_THRESHOLD_MKM}M km of Jupiter)', fontsize=14)
    plt.xlim(0, 100)
    
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{width:.2f}%', va='center', fontsize=10, fontweight='bold')
    
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    
    output_path = 'visualizations/jupiter_intercept/plot_1d_significant_radii.png'
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    print(f"Bar plot 1D saved to {output_path}")

if __name__ == "__main__":
    plot_1d_results()

