"""
3I/ATLAS Monte Carlo Analysis - Module 1C
Isolated population analysis of interstellar objects passing within 100M km of Jupiter.
This script generates a high-fidelity sample of 10,000 Jupiter-passing visitors to
analyze the statistical distribution of close approaches.
"""
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
from skyfield.api import load
import os

# --- Constants & Setup ---
AU_KM = 149597870.7
K = 0.01720209895
GM_SUN = K**2 # in AU^3 / day^2

# Threshold for "passing close to Jupiter" baseline
BASELINE_THRESHOLD_MKM = 100.0 
BASELINE_THRESHOLD_AU = BASELINE_THRESHOLD_MKM * 1e6 / AU_KM

SIGNIFICANT_RADII = {
    'L3 (Opposite)': 1560.0,
    'L4/L5 (Trojans)': 778.0,
    'Hill Radius': 53.5,
    'L2 Point': 54.0,
    'L1 Point': 52.0,
    'Callisto Orbit': 1.88,
    'Ganymede Orbit': 1.07,
    'Jupiter Surface': 0.071
}

# --- Kepler Solver (Vectorized) ---
def solve_hyperbolic_kepler(M, e, tol=1e-8, max_iter=100):
    H = M / (e - 1)
    for _ in range(max_iter):
        f = e * np.sinh(H) - H - M
        df = e * np.cosh(H) - 1
        dH = f / df
        H = H - dH
        if np.all(np.abs(dH) < tol):
            break
    return H

def orbital_elements_to_pos(a, e, i_deg, node_deg, peri_deg, T_p, t):
    a = np.asarray(a).reshape(-1, 1)
    e = np.asarray(e).reshape(-1, 1)
    i, node, peri = np.deg2rad(i_deg).reshape(-1, 1), np.deg2rad(node_deg).reshape(-1, 1), np.deg2rad(peri_deg).reshape(-1, 1)
    T_p, t = np.asarray(T_p).reshape(-1, 1), np.asarray(t)

    n = np.sqrt(GM_SUN / np.abs(a)**3)
    M = n * (t - T_p)
    H = solve_hyperbolic_kepler(M, e)
    
    cosh_H, sinh_H = np.cosh(H), np.sinh(H)
    x_orb, y_orb = a * (cosh_H - e), -a * np.sqrt(e**2 - 1) * sinh_H
    
    cp, sp = np.cos(peri), np.sin(peri)
    x1, y1 = x_orb * cp - y_orb * sp, x_orb * sp + y_orb * cp
    ci, si = np.cos(i), np.sin(i)
    y2, z2 = y1 * ci, y1 * si
    cn, sn = np.cos(node), np.sin(node)
    x3, y3 = x1 * cn - y2 * sn, x1 * sn + y2 * cn
    
    return np.stack([x3, y3, z2], axis=-1)

def run_simulation(n_trials=400000):
    print(f"Running Monte Carlo Simulation 1C (Target 10k passing)...")
    ts, eph = load.timescale(), load('de421.bsp')
    sun_sf, jupiter_sf = eph['sun'], eph['jupiter_barycenter']

    start_jd, end_jd = ts.utc(2020, 1, 1).tt, ts.utc(2032, 1, 1).tt
    batch_size = 5000
    num_batches = n_trials // batch_size
    jupiter_passing_distances = []
    dt_steps = np.linspace(-100, 100, 50)

    for b in range(num_batches):
        v_inf_kms = np.random.uniform(20, 80, batch_size)
        v_inf_au_d = v_inf_kms * 86400 / AU_KM
        a = -GM_SUN / v_inf_au_d**2
        q = np.random.uniform(0.1, 10.0, batch_size)
        e = 1 - q/a
        is_retro = np.random.choice([True, False], batch_size)
        inc = np.where(is_retro, np.random.uniform(170, 180, batch_size), np.random.uniform(0, 10, batch_size))
        node, peri = np.random.uniform(0, 360, batch_size), np.random.uniform(0, 360, batch_size)
        Tp = np.random.uniform(start_jd, end_jd, batch_size)
        
        comet_pos = orbital_elements_to_pos(a, e, inc, node, peri, Tp, Tp.reshape(-1, 1) + dt_steps.reshape(1, -1))
        t_eval_jd = (Tp.reshape(-1, 1) + dt_steps.reshape(1, -1)).flatten()
        jupiter_pos = (jupiter_sf - sun_sf).at(ts.tt(jd=t_eval_jd)).ecliptic_position().au.T.reshape(batch_size, len(dt_steps), 3)
        
        min_dists = np.min(np.linalg.norm(comet_pos - jupiter_pos, axis=2), axis=1)
        passing = min_dists[min_dists <= BASELINE_THRESHOLD_AU]
        jupiter_passing_distances.extend(passing)
        
        if len(jupiter_passing_distances) >= 10000: break

    return np.array(jupiter_passing_distances)

def plot_1c_results(distances_au):
    distances_mkm = distances_au * AU_KM / 1e6
    n_cases = len(distances_mkm)
    
    plt.figure(figsize=(12, 8))
    bins = np.logspace(np.log10(0.01), np.log10(BASELINE_THRESHOLD_MKM), 50)
    plt.hist(distances_mkm, bins=bins, density=False, color='skyblue', edgecolor='black', alpha=0.7)
    
    plt.xscale('log')
    plt.axvline(SIGNIFICANT_RADII['Hill Radius'], color='red', linestyle='--', label='Jupiter Hill Radius')
    plt.axvline(53.6, color='green', linestyle=':', label='3I/ATLAS Perijove')
    plt.axvline(SIGNIFICANT_RADII['L1 Point'], color='orange', linestyle='--', alpha=0.6, label='L1 Point')
    plt.axvline(SIGNIFICANT_RADII['L2 Point'], color='purple', linestyle='--', alpha=0.6, label='L2 Point')
    
    plt.title(f'Monte Carlo 1C: Distribution of Close Approaches\n(Baseline: {n_cases} trajectories passing < {BASELINE_THRESHOLD_MKM}M km)', fontsize=14)
    plt.xlabel('Closest Approach to Jupiter (million km)', fontsize=12)
    plt.ylabel('Number of Cases', fontsize=12)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend()
    
    output_path = 'visualizations/jupiter_intercept/plot_1c_histogram.png'
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    print(f"Histogram saved to {output_path}")

if __name__ == "__main__":
    results = run_simulation(n_trials=400000)
    # Save results for use by 1d
    np.savetxt('data/jupiter_intercept/monte_carlo_1c_results.csv', results, delimiter=',')
    plot_1c_results(results)
