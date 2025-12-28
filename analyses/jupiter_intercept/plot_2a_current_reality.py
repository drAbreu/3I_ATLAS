"""
3I/ATLAS Intercept Analysis - Module 2A (Reality Check)
Calculates the Delta-V requirements for a Jupiter intercept mission using
the most recent best-fit orbital elements (as of late 2024/2025 refinement).
Demonstrates how refined data increases mission difficulty from 5 km/s to ~27-30 km/s.
"""
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
from astropy import units as u
from poliastro.bodies import Sun
from poliastro.twobody import Orbit
from poliastro.iod.izzo import lambert
from skyfield.api import load
from scipy.optimize import minimize
import os

# --- Setup ---
EPH = load('de421.bsp')
TS = load.timescale()
SUN_SF = EPH['sun']
JUPITER_SF = EPH['jupiter_barycenter']

def get_jupiter_ecliptic(t_astropy):
    """Returns Jupiter's Heliocentric Ecliptic J2000 position."""
    # Ensure we use TT for skyfield consistency
    t_sf = TS.tt(jd=t_astropy.jd)
    pos = (JUPITER_SF - SUN_SF).at(t_sf).ecliptic_position().au
    return pos * u.AU

def get_atlas_current_state(t_astropy):
    """Returns 3I/ATLAS state using CURRENT best-fit orbital elements."""
    atlas_current = Orbit.from_classical(
        Sun,
        a=-0.280 * u.AU,
        ecc=6.200 * u.one,
        inc=175.50 * u.deg,
        raan=322.20 * u.deg,
        argp=128.10 * u.deg,
        nu=0 * u.deg,
        epoch=Time(2460977.98, format='jd', scale='tdb')
    )
    ss = atlas_current.propagate(t_astropy - atlas_current.epoch)
    return ss.r, ss.v

def find_min_dv_intercept(t_maneuver):
    r1, v1_atlas = get_atlas_current_state(t_maneuver)
    
    def objective(t_jd):
        t_arr = Time(t_jd[0], format='jd')
        tof = (t_arr - t_maneuver).to(u.d)
        if tof.value <= 1.0 or tof.value > 400:
            return 1e6
        r2 = get_jupiter_ecliptic(t_arr)
        try:
            (v1_trans, _), = lambert(Sun.k, r1, r2, tof)
            dv = np.linalg.norm(v1_trans - v1_atlas).to(u.km/u.s).value
            return dv
        except:
            return 1e6
    
    guess_jd = Time('2026-03-16').jd
    result = minimize(objective, [guess_jd], method='Powell', options={'ftol': 1e-4, 'maxiter': 100})
    return result.fun if result.fun < 1e5 else np.nan

def create_current_analysis():
    print("Creating updated analysis with current orbital elements...")
    maneuver_dates = Time(np.linspace(Time("2025-07-01").jd, Time("2026-02-01").jd, 30), format='jd')
    arrival_dates = []
    dv_values = []
    
    for i, t_dep in enumerate(maneuver_dates):
        if i % 10 == 0: print(f"Processing {i+1}/{len(maneuver_dates)}: {t_dep.iso[:10]}...")
        dv = find_min_dv_intercept(t_dep)
        dv_values.append(dv)
        
        # Optimal arrival search
        r1, v1_atlas = get_atlas_current_state(t_dep)
        def find_arrival(t_jd):
            t_arr = Time(t_jd[0], format='jd')
            tof = (t_arr - t_dep).to(u.d)
            if tof.value <= 1: return 1e6
            r2 = get_jupiter_ecliptic(t_arr)
            try:
                (v1_trans, _), = lambert(Sun.k, r1, r2, tof)
                return np.linalg.norm(v1_trans - v1_atlas).to(u.km/u.s).value
            except: return 1e6
        res = minimize(find_arrival, [Time('2026-03-16').jd], method='Powell')
        arrival_dates.append(Time(res.x[0], format='jd'))
    
    fig, ax1 = plt.subplots(figsize=(12, 7))
    dep_days = [d.datetime for d in maneuver_dates]
    arr_days = [d.datetime for d in arrival_dates]
    
    color_blue = '#1f77b4'
    ax1.plot(dep_days, arr_days, color=color_blue, linewidth=3, label='Optimal Arrival Date at Jupiter')
    ax1.set_ylabel('Arrival Date at Jupiter', color=color_blue, fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color_blue)
    ax1.grid(True, alpha=0.3)
    
    ax2 = ax1.twinx()
    color_red = '#d62728'
    ax2.plot(dep_days, dv_values, '-', color=color_red, linewidth=3, label='Required ΔV (Current Elements)')
    ax2.set_ylabel('Required ΔV (km/s)', color=color_red, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color_red)
    ax2.set_ylim(0, 60)

    min_dv = np.nanmin(dv_values)
    ax2.axhline(16.5, color='green', linestyle='--', alpha=0.6, label='New Horizons Capability (16.5 km/s)')
    ax2.axhline(45, color='orange', linestyle='--', alpha=0.6, label='Theoretical Ion Drive Limit (~45 km/s)')

    discovery = Time('2025-07-01').datetime
    perihelion = Time('2025-10-29').datetime
    for date, label in [(discovery, 'Expected Discovery'), (perihelion, 'Perihelion')]:
        ax1.axvline(date, color='black', alpha=0.2, lw=1.5)
        ax1.text(date, ax1.get_ylim()[1], f' {label}', rotation=90, va='top', fontsize=10, alpha=0.8)

    ax2.axhspan(0, 20, alpha=0.05, color='green', label='Currently Achievable')
    ax2.axhspan(20, 60, alpha=0.05, color='red')

    plt.title('3I/ATLAS Intercept Requirements with Updated Orbital Elements\nReality Check: Current Best-Fit Trajectory Data', fontsize=14, pad=25)
    ax1.set_xlabel('Date of ΔV Application (Trajectory Nudge)', fontsize=12)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, facecolor='white', framealpha=0.95, fontsize=9)

    ax2.text(0.98, 0.35, f'Improved orbital elements\nshow significantly higher\nintercept requirements\n(~{min_dv/5:.1f}x paper estimate)',
             transform=ax2.transAxes, fontsize=10, va='top', ha='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    output_path = 'visualizations/jupiter_intercept/plot_2a_current_reality.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to {output_path}")
    print(f"Minimum ΔV found: {min_dv:.2f} km/s")
    print(f"\nKey insight: Updated elements require ~{min_dv/5:.1f}× more ΔV than paper estimate!")
    plt.close()

if __name__ == '__main__':
    create_current_analysis()
