"""
3I/ATLAS Propulsion Engineering - Module 3C
Applies the Tsiolkovsky rocket equation to various propulsion systems (Chemical,
Nuclear, Fusion) to visualize the mass ratio required for 3I/ATLAS maneuvers.
"""
import numpy as np
import matplotlib.pyplot as plt
import os

def rocket_equation(dv, isp):
    """
    Tsiolkovsky rocket equation: m_initial / m_final = exp(dv / (isp * g0))
    """
    g0 = 9.80665  # m/s^2
    return np.exp((dv * 1000) / (isp * g0))

def plot_rocket_equation():
    # Delta-V range in km/s (from Intercept 5km/s to Rendezvous 45km/s)
    dv_range = np.linspace(0, 60, 200)
    
    # ISP values for different technologies (typical values)
    techs = {
        'Chemical (LOX/LH2)': 450,
        'Nuclear Thermal (NTR)': 900,
        'Electric (Hall/Ion)': 3000,
        'Fusion (Theoretical)': 10000
    }
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    for name, isp in techs.items():
        mass_ratios = rocket_equation(dv_range, isp)
        ax.plot(dv_range, mass_ratios, label=f'{name} (Isp={isp}s)', linewidth=2)
        
    # Mark the key mission requirements
    intercept_dv = 5.0
    rendezvous_dv = 43.8 # From our high-precision porkchop min
    
    ax.axvline(intercept_dv, color='green', linestyle=':', alpha=0.7)
    ax.text(intercept_dv + 1, 10**1, f'Intercept Requirement (~{intercept_dv} km/s)', color='green', fontweight='bold')
    
    ax.axvline(rendezvous_dv, color='red', linestyle=':', alpha=0.7)
    ax.text(rendezvous_dv - 15, 10**6, f'Rendezvous Requirement (~{rendezvous_dv:.1f} km/s)', color='red', fontweight='bold')

    # Formatting
    ax.set_yscale('log')
    ax.set_title('Propulsion Requirements: Mass Ratio vs. Mission ΔV', fontsize=16, pad=20)
    ax.set_xlabel('Mission ΔV (km/s)', fontsize=12)
    ax.set_ylabel('Mass Ratio ($m_{initial} / m_{final}$)', fontsize=12)
    ax.set_ylim(1, 1e10)
    ax.set_xlim(0, 60)
    ax.grid(True, which="both", ls="-", alpha=0.2)
    ax.legend(loc='upper left', frameon=True, facecolor='white')

    # Background shading for "Human Technology" vs "Speculative"
    ax.axvspan(0, 15, color='gray', alpha=0.1)
    ax.text(2, 1e9, 'Currently Feasible\n(Intercept Window)', fontsize=10, color='gray')
    
    ax.axvspan(15, 60, color='orange', alpha=0.05)
    ax.text(35, 1e9, 'Extremely Challenging\n(Rendezvous Window)', fontsize=10, color='orange')

    plt.tight_layout()
    output_path = 'visualizations/jupiter_intercept/plot_3c_rocket_equation.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    print(f"Rocket equation plot saved to {output_path}")

if __name__ == '__main__':
    plot_rocket_equation()
