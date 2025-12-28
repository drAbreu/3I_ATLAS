"""
3I/ATLAS Energy Analysis - Module 3B (C3 Energy)
Calculates the characteristic energy (C3) required for intercept and rendezvous
scenarios as a function of the maneuver date.
"""
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
from astropy import units as u
from poliastro.bodies import Sun
from poliastro.twobody import Orbit
from poliastro.iod.izzo import lambert
from skyfield.api import load
import os

# --- High Precision Ecliptic Transformation ---
EPS = np.deg2rad(23.4392911)
R_EQ_TO_ECL = np.array([
    [1, 0, 0],
    [0, np.cos(EPS), np.sin(EPS)],
    [0, -np.sin(EPS), np.cos(EPS)]
])

EPH = load('de421.bsp')
TS = load.timescale()
SUN_SF = EPH['sun']
JUPITER_SF = EPH['jupiter_barycenter']

def get_jupiter_state_ecliptic(t_astropy):
    t_sf = TS.tt(jd=t_astropy.jd)
    state = (JUPITER_SF - SUN_SF).at(t_sf)
    r_ecl = R_EQ_TO_ECL @ state.position.au
    v_ecl = R_EQ_TO_ECL @ state.velocity.au_per_d
    return r_ecl * u.AU, v_ecl * (u.AU / u.d)

def get_atlas_state_ecliptic(t_astropy):
    atlas_ref = Orbit.from_classical(
        Sun, a=-0.263836 * u.AU, ecc=6.139658 * u.one, inc=175.1129 * u.deg,
        raan=322.1549 * u.deg, argp=128.0072 * u.deg, nu=0 * u.deg,
        epoch=Time(2460977.9827, format='jd', scale='tdb')
    )
    ss = atlas_ref.propagate(t_astropy - atlas_ref.epoch)
    return ss.r, ss.v

def calculate_energy_budget():
    # Scanning a range of departure dates
    maneuver_dates = Time(np.linspace(Time("2025-05-01").jd, Time("2026-02-01").jd, 100), format='jd')
    
    c3_intercept = []
    c3_rendezvous = []
    
    # Target: Jupiter at its closest approach (approximate for scanning)
    target_date = Time("2026-03-16")
    r_target, v_target = get_jupiter_state_ecliptic(target_date)

    print("Calculating Energy Budget (C3)...")
    for date in maneuver_dates:
        r1, v1_atlas = get_atlas_state_ecliptic(date)
        tof = target_date - date
        
        try:
            (v1_trans, v2_trans), = lambert(Sun.k, r1, r_target, tof)
            
            # Intercept: Burn to change trajectory
            dv_intercept = np.linalg.norm(v1_trans - v1_atlas).to(u.km/u.s).value
            c3_intercept.append(dv_intercept**2)
            
            # Rendezvous: Burn at departure + Capture burn at Jupiter
            v_rel_inf = np.linalg.norm(v2_trans - v_target)
            mu_jup = 1.26686e8 * u.km**3 / u.s**2
            r_p = 1.05 * 71492 * u.km
            v_esc = np.sqrt(2 * mu_jup / r_p)
            v_hyp = np.sqrt(v_rel_inf**2 + v_esc**2)
            dv_capture = (v_hyp - v_esc).to(u.km/u.s).value
            
            dv_total_rend = dv_intercept + dv_capture
            c3_rendezvous.append(dv_total_rend**2)
            
        except:
            c3_intercept.append(np.nan)
            c3_rendezvous.append(np.nan)

    return maneuver_dates, c3_intercept, c3_rendezvous

def plot_energy_budget(dates, c3_int, c3_rend):
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.plot(dates.datetime, c3_int, 'C0-', linewidth=2, label='Intercept Scenario (C3)')
    ax.plot(dates.datetime, c3_rend, 'C1-', linewidth=2, label='Rendezvous Scenario (C3)')
    
    ax.set_title('Energy Budget (Characteristic Energy $C_3$) vs. Maneuver Date', fontsize=16)
    ax.set_xlabel('Date of Maneuver', fontsize=12)
    ax.set_ylabel('$C_3$ ($km^2/s^2$)', fontsize=12)
    ax.grid(True, alpha=0.2)
    ax.legend()
    
    # Annotate Discovery
    discovery = Time('2025-07-01').datetime
    ax.axvline(discovery, color='red', linestyle='--', alpha=0.5)
    ax.text(discovery, ax.get_ylim()[1]*0.8, ' Discovery', rotation=90, color='red')

    plt.tight_layout()
    output_path = 'visualizations/jupiter_intercept/plot_3b_energy_budget.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    print(f"Energy budget plot saved to {output_path}")

if __name__ == '__main__':
    d, ci, cr = calculate_energy_budget()
    plot_energy_budget(d, ci, cr)
