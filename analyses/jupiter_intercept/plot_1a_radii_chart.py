"""
3I/ATLAS Proximity Analysis - Module 1A
Visualizes Jupiter's gravitationally significant radii, including Lagrange points (L1-L5).
Demonstrates that the Hill radius is part of a complex system of equilibrium points.
"""
import numpy as np
import matplotlib.pyplot as plt

def plot_radii_chart():
    """
    Generates a radar chart of Jupiter's meaningful radii including Lagrange points.
    """
    # Data for the meaningful radii in million km
    radii = {
        'Roche limit': 0.18,
        'Io orbit': 0.42,
        'Europa orbit': 0.67,
        'Ganymede orbit': 1.07,
        'Callisto orbit': 1.88,
        'L1 (Sun-Jup)': 52.0,
        'Hill radius': 53.5,
        'L2 (Sun-Jup)': 54.0,
        'L4/L5 (Trojans)': 778.0,
        'L3 (Opposite)': 1560.0
    }
    
    sorted_radii = sorted(radii.items(), key=lambda item: item[1])
    
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={'projection': 'polar'})
    ax.set_rscale('log')
    
    # Plot concentric circles
    for label, radius in sorted_radii:
        ax.plot(np.linspace(0, 2 * np.pi, 100), [radius] * 100, label=f'{label}: {radius:,.0f}M km')

    # 3I/ATLAS trajectory
    perijove_dist = 53.6
    eccentricity = 1281 # High speed flyby
    p = perijove_dist * (1 + eccentricity)
    
    cos_nu_limit = ((p / 2000) - 1) / eccentricity # Increased r_max to 2000
    nu_limit = np.arccos(np.clip(cos_nu_limit, -1, 1))
    nu = np.linspace(-nu_limit, nu_limit, 800)
    r = p / (1 + eccentricity * np.cos(nu))
    
    rotation_angle = np.deg2rad(35)
    ax.plot(nu + rotation_angle, r, color='red', linestyle='--', linewidth=2, label="3I/ATLAS Trajectory (Flyby)")
    ax.plot([rotation_angle], [perijove_dist], 'rx', markersize=10, markeredgewidth=2, label=f"3I/ATLAS Perijove: {perijove_dist}M km")
    
    ax.set_facecolor('#fdfdfd')
    ax.set_rmax(2000)
    ax.set_rticks([0.1, 1, 10, 100, 1000])
    ax.set_rlabel_position(22.5)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5)
    ax.set_title("Jupiter's Gravitationally Meaningful Radii (including Lagrange points)", fontsize=16, pad=30)
    
    ax.legend(loc='upper left', bbox_to_anchor=(1.1, 1.1), fontsize=10)
    
    output_path = 'visualizations/jupiter_intercept/plot_1a_radii_chart.png'
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    print(f"Updated radii chart saved to {output_path}")
    plt.close()

if __name__ == '__main__':
    plot_radii_chart()
