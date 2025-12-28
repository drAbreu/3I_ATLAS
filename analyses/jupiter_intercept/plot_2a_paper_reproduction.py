"""
3I/ATLAS Intercept Analysis - Module 2A (Paper Reproduction)
Reproduces Figure 4 from Hibberd, Crowl, & Loeb (2025).
Uses the initial orbital elements published in mid-2025 to verify the
original claim of a ~5 km/s "nudge" intercept window.
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
    t_sf = TS.tt(jd=t_astropy.jd)
    pos = (JUPITER_SF - SUN_SF).at(t_sf).ecliptic_position().au
    return pos * u.AU

def get_atlas_paper_state(t_astropy):
    """Returns 3I/ATLAS state using ORIGINAL elements from Hibberd et al. (2025)."""
    atlas_paper = Orbit.from_classical(
        Sun,
        a=-0.263836 * u.AU,
        ecc=6.139658 * u.one,
        inc=175.1129 * u.deg,
        raan=322.1549 * u.deg,
        argp=128.0072 * u.deg,
        nu=0 * u.deg,
        epoch=Time(2460977.9827, format='jd', scale='tdb')
    )
    ss = atlas_paper.propagate(t_astropy - atlas_paper.epoch)
    return ss.r, ss.v

def find_min_dv_intercept(t_maneuver):
    r1, v1_atlas = get_atlas_paper_state(t_maneuver)
    
    def objective(t_jd):
        t_arr = Time(t_jd[0], format='jd')
        tof = (t_arr - t_maneuver).to(u.d)
        if tof.value <= 1.0 or tof.value > 600:
            return 1e6
        r2 = get_jupiter_ecliptic(t_arr)
        try:
            (v1_trans, _), = lambert(Sun.k, r1, r2, tof)
            dv = np.linalg.norm(v1_trans - v1_atlas).to(u.km/u.s).value
            return dv
        except:
            return 1e6
    
    # Initial guess: Natural approach date
    guess_jd = Time('2026-03-16').jd
    
    # Optimize with a much wider range of arrival times
    result = minimize(
        objective, 
        [guess_jd],
        method='Powell',
        options={'ftol': 1e-6, 'maxiter': 200}
    )
    return result.fun if result.fun < 1e5 else np.nan

def create_paper_analysis():
    print("Reproducing paper analysis with original orbital elements...")
    # Date range: Mid-2025 to late 2025
    maneuver_dates = Time(np.linspace(Time("2025-05-01").jd, Time("2025-11-01").jd, 30), format='jd')
    dv_values = []
    opt_arrivals = []
    
    for i, t_dep in enumerate(maneuver_dates):
        if i % 10 == 0: print(f"Processing {i+1}/{len(maneuver_dates)}: {t_dep.iso[:10]}...")
        # Find optimal arrival
        def obj(t_jd):
            t_arr = Time(t_jd[0], format='jd')
            tof = (t_arr - t_dep).to(u.d)
            if tof.value <= 1.0 or tof.value > 600: return 1e6
            r1, v1_atlas = get_atlas_paper_state(t_dep)
            r2 = get_jupiter_ecliptic(t_arr)
            try:
                (v1_t, _), = lambert(Sun.k, r1, r2, tof)
                return np.linalg.norm(v1_t - v1_atlas).to(u.km/u.s).value
            except: return 1e6
        
        res = minimize(obj, [Time('2026-03-16').jd], method='Powell')
        dv_values.append(res.fun)
        opt_arrivals.append(Time(res.x[0], format='jd'))
    
    fig, ax = plt.subplots(figsize=(12, 7))
    dep_days = [d.datetime for d in maneuver_dates]
    
    color_red = '#d62728'
    ax.plot(dep_days, dv_values, '-', color=color_red, linewidth=3, label='Required ΔV (Paper Elements)')
    ax.set_ylabel('Required ΔV (km/s)', color=color_red, fontsize=12, fontweight='bold')
    ax.set_ylim(0, 20)
    ax.grid(True, alpha=0.3)

    min_dv = np.nanmin(dv_values)
    ax.axhline(5.0, color='darkblue', linestyle='--', linewidth=1.5, label='Approximate Paper Minimum (~5 km/s)')

    plt.title('3I/ATLAS Intercept Requirements: Reproduction of Hibberd et al. (2025)\nOriginal Orbital Elements (High-Speed Head-on Intercept)', fontsize=14, pad=25)
    ax.set_xlabel('Date of ΔV Application (Trajectory Nudge)', fontsize=12)
    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.95)

    plt.tight_layout()
    output_path = 'visualizations/jupiter_intercept/plot_2a_paper_reproduction.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Paper reproduction plot saved to {output_path}")
    min_idx = np.nanargmin(dv_values)
    print(f"Minimum ΔV found (Paper): {dv_values[min_idx]:.2f} km/s at maneuver {maneuver_dates[min_idx].iso[:10]} arriving {opt_arrivals[min_idx].iso[:10]}")

if __name__ == '__main__':
    create_paper_analysis()
