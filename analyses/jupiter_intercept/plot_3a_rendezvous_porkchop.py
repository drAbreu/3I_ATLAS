"""
3I/ATLAS Mission Design - Module 3A (Porkchop Plot)
Scans 2,000+ launch and arrival windows to find the optimal energy window for a
rendezvous mission (stopping at Jupiter) using high-precision Lambert solvers.
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
# Obliquity of the Ecliptic (J2000)
EPS = np.deg2rad(23.4392911)
# Rotation matrix from Equatorial (ICRF) to Ecliptic J2000
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
    """Returns Jupiter's state in Heliocentric Ecliptic J2000."""
    t_sf = TS.tt(jd=t_astropy.jd)
    # Get Equatorial state
    state = (JUPITER_SF - SUN_SF).at(t_sf)
    r_eq = state.position.au
    v_eq = state.velocity.au_per_d
    
    # Rotate to Ecliptic
    r_ecl = R_EQ_TO_ECL @ r_eq
    v_ecl = R_EQ_TO_ECL @ v_eq
    
    return r_ecl * u.AU, v_ecl * (u.AU / u.d)

def get_atlas_state_ecliptic(t_astropy):
    """Returns ATLAS state in Heliocentric Ecliptic J2000."""
    # Verified Paper Elements
    atlas_ref = Orbit.from_classical(
        Sun,
        a=-0.263836 * u.AU,
        ecc=6.139658 * u.one,
        inc=175.1129 * u.deg,
        raan=322.1549 * u.deg,
        argp=128.0072 * u.deg,
        nu=0 * u.deg,
        epoch=Time(2460977.9827, format='jd', scale='tdb')
    )
    ss = atlas_ref.propagate(t_astropy - atlas_ref.epoch)
    return ss.r, ss.v

def calculate_rendezvous_grid():
    # Grid search parameters
    dep_dates = Time(np.linspace(Time("2025-05-01").jd, Time("2026-02-01").jd, 45), format='jd')
    tofs = np.linspace(50, 350, 45) * u.d
    
    dv_grid = np.full((len(tofs), len(dep_dates)), np.nan)

    print("Calculating Rendezvous Porkchop Grid (High Precision Ecliptic)...")
    for j, dep_date in enumerate(dep_dates):
        if j % 10 == 0: print(f"Processing maneuver date {dep_date.iso[:10]}...")
        r1, v1_atlas = get_atlas_state_ecliptic(dep_date)

        for i, tof in enumerate(tofs):
            arr_date = dep_date + tof
            r2, v2_jupiter = get_jupiter_state_ecliptic(arr_date)

            try:
                # Solve Lambert for the transfer trajectory
                (v1_trans, v2_trans), = lambert(Sun.k, r1, r2, tof)
                
                # Burn 1: Departure from ATLAS trajectory
                dv1 = np.linalg.norm(v1_trans - v1_atlas)
                
                # Burn 2: Jupiter Capture (Oberth Effect)
                # Calculate delta-V to enter a parabolic/highly-eccentric orbit
                # at 1.05 Jupiter radii (as per paper's 0.05 altitude)
                v_rel_inf = np.linalg.norm(v2_trans - v2_jupiter)
                mu_jup = 1.26686e8 * u.km**3 / u.s**2
                r_p = 1.05 * 71492 * u.km
                v_esc = np.sqrt(2 * mu_jup / r_p)
                v_hyp = np.sqrt(v_rel_inf**2 + v_esc**2)
                
                # Burn to reach escape velocity (capture)
                dv2 = v_hyp - v_esc
                
                dv_grid[i, j] = (dv1 + dv2).to(u.km/u.s).value
            except:
                continue
                
    return dep_dates, tofs, dv_grid

def plot_porkchop(dep_dates, tofs, dv_grid):
    fig, ax = plt.subplots(figsize=(13, 10))
    
    X, Y = np.meshgrid(dep_dates.datetime, tofs.value)
    
    # Contour levels reflecting the paper's rendezvous costs (~20 km/s)
    levels = [15, 20, 25, 30, 40, 50, 60, 80, 100]
    cp = ax.contourf(X, Y, dv_grid, levels=levels, cmap='magma', extend='both')
    cbar = fig.colorbar(cp)
    cbar.set_label('Total Rendezvous ΔV (Departure + Arrival) [km/s]', fontsize=12, weight='bold')

    # Add labels to contour lines
    cs = ax.contour(X, Y, dv_grid, levels=levels, colors='white', alpha=0.4, linewidths=0.8)
    ax.clabel(cs, inline=True, fontsize=9, fmt='%.0f')

    # Global Optimal Point
    min_dv = np.nanmin(dv_grid)
    min_idx = np.unravel_index(np.nanargmin(dv_grid), dv_grid.shape)
    min_dep = dep_dates[min_idx[1]].datetime
    min_tof = tofs[min_idx[0]].value
    
    ax.plot(min_dep, min_tof, 'r*', markersize=15, label=f'Global Minimum: {min_dv:.1f} km/s')

    # Styling
    ax.set_title('3I/ATLAS Rendezvous Porkchop Plot (High Precision)', fontsize=16, pad=25)
    ax.set_xlabel('Maneuver Date (Discovery to Perijove)', fontsize=12)
    ax.set_ylabel('Time of Flight (Days)', fontsize=12)
    ax.grid(True, alpha=0.15)
    ax.legend(loc='upper right', frameon=True, facecolor='white')
    
    # Reference markers
    discovery = Time('2025-07-01').datetime
    ax.axvline(discovery, color='cyan', linestyle=':', alpha=0.8)
    ax.text(discovery, ax.get_ylim()[1]*0.9, ' Discovery (July 1)', rotation=90, color='cyan', fontsize=10)

    plt.tight_layout()
    output_path = 'visualizations/jupiter_intercept/plot_3a_rendezvous_porkchop.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    print(f"Rendezvous porkchop plot saved to {output_path}")

if __name__ == '__main__':
    dep, tof, grid = calculate_rendezvous_grid()
    plot_porkchop(dep, tof, grid)
