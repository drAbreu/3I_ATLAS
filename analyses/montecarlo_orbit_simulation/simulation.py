import numpy as np
import matplotlib.pyplot as plt
from skyfield.api import load
from kepler import orbital_elements_to_pos_vel
import pandas as pd
import os

# Constants
AU_KM = 149597870.7
HIT_DISTANCES_MKM = [25, 50, 75, 100, 125, 150]
HIT_DISTANCES_AU = [d * 1e6 / AU_KM for d in HIT_DISTANCES_MKM]
PLANET_NAMES = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']


# 3I/ATLAS Elements
ELEMENTS_3I = {
    'e': 6.1396580,
    'q': 1.3564840,
    'i': 175.1129,
    'node': 322.1549,
    'peri': 128.0072,
    'a': 1.3564840 / (1 - 6.1396580), # ~ -0.2638
    'Tp_jd': 2460977.9827
}

def get_planet_positions_batch(ts, t_array_jd):
    """
    Get positions of planets 1-8 relative to Sun at times t_array_jd.
    Returns array (N_times, 8, 3) in AU, ICRS frame.
    """
    planets = load('de421.bsp')
    sun = planets['sun']
    
    targets = [
        planets['mercury'], planets['venus'], planets['earth_barycenter'],
        planets['mars_barycenter'], planets['jupiter_barycenter'], planets['saturn_barycenter'],
        planets['uranus_barycenter'], planets['neptune_barycenter']
    ]
    
    t = ts.tt(jd=t_array_jd)
    
    positions = [ (target - sun).at(t).position.au.T for target in targets]
        
    return np.stack(positions, axis=1)

def run_simulation(num_trials=10000, comet_type='3I'):
    """
    comet_type: '3I' or 'Random'
    """
    ts = load.timescale()
    
    dt_days = np.arange(-2000, 2000, 2)
    n_steps = len(dt_days)
    
    start_jd = ts.utc(1910, 1, 1).tt
    end_jd = ts.utc(2040, 1, 1).tt
    
    batch_size = 100
    num_batches = num_trials // batch_size
    
    results_min_dist = []
    
    eps = np.deg2rad(23.4392911)
    c = np.cos(eps)
    s = np.sin(eps)
    R_ecl_to_eq = np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s, c]
    ])
    
    print(f"Starting simulation: {comet_type}, {num_trials} trials.")
    
    for b in range(num_batches):
        Tp_batch = np.random.uniform(start_jd, end_jd, batch_size)
        
        if comet_type == '3I':
            a = np.full(batch_size, ELEMENTS_3I['a'])
            e = np.full(batch_size, ELEMENTS_3I['e'])
            i = np.full(batch_size, ELEMENTS_3I['i'])
            node = np.full(batch_size, ELEMENTS_3I['node'])
            peri = np.full(batch_size, ELEMENTS_3I['peri'])
        else: # Random
            a = np.full(batch_size, ELEMENTS_3I['a'])
            q = np.random.uniform(0.387, 0.723, batch_size)
            e = 1 - q/a
            is_retro = np.random.choice([False, True], batch_size)
            i = np.where(is_retro, 180.0, 0.0)
            node = np.random.uniform(0, 360, batch_size)
            peri = np.random.uniform(0, 360, batch_size)
        
        comet_pos_ecl = orbital_elements_to_pos_vel(
            a, e, i, node, peri, 
            T_p=np.zeros(batch_size),
            t_array=dt_days
        )
        
        comet_pos_eq = comet_pos_ecl @ R_ecl_to_eq.T 
        
        t_eval_jd = Tp_batch[:, None] + dt_days[None, :]
        t_eval_flat = t_eval_jd.flatten()
        
        planet_pos_flat = get_planet_positions_batch(ts, t_eval_flat)
        
        planet_pos = planet_pos_flat.reshape(batch_size, n_steps, 8, 3)
        
        diff = planet_pos - comet_pos_eq[:, :, None, :]
        dists = np.linalg.norm(diff, axis=3)
        
        min_dists = np.min(dists, axis=1)
        
        results_min_dist.append(min_dists)
        
        print(f"Batch {b+1}/{num_batches} done.")
        
    all_min_dists = np.concatenate(results_min_dist, axis=0)
    
    return all_min_dists

def process_results(data, output_dir):
    """
    data: (N_trials, 8) array of min distances in AU
    """
    
    # Create DataFrame for hits
    hits_data = []
    for i, dist_au in enumerate(data):
        for p_idx, planet_name in enumerate(PLANET_NAMES):
            min_dist_au = dist_au[p_idx]
            for hit_dist_au in HIT_DISTANCES_AU:
                if min_dist_au <= hit_dist_au:
                    hits_data.append({
                        'simulation_id': i,
                        'planet': planet_name,
                        'min_distance_au': min_dist_au,
                        'hit_distance_au': hit_dist_au,
                        'hit_distance_mkm': int(round(hit_dist_au * AU_KM / 1e6))
                    })
    
    hits_df = pd.DataFrame(hits_data)
    hits_df.to_csv(f"{output_dir}/montecarlo_orbit_simulation_hits.csv", index=False)
    print(f"Saved hit data to {output_dir}/montecarlo_orbit_simulation_hits.csv")

    # Histogram 1: Hits per planet (Grouped by distance)
    plt.figure(figsize=(14, 8))
    
    # Use planets in correct order from Sun
    planets_with_hits = [p for p in PLANET_NAMES if p in hits_df['planet'].unique()]
    
    if not hits_df.empty:
        pivot_df = hits_df.groupby(['planet', 'hit_distance_mkm'])['simulation_id'].nunique().unstack(fill_value=0)
        # Reindex to ensure planet order and distance order
        pivot_df = pivot_df.reindex(planets_with_hits)
        # Ensure all columns exist
        for d in HIT_DISTANCES_MKM:
            if d not in pivot_df.columns:
                pivot_df[d] = 0
        pivot_df = pivot_df[HIT_DISTANCES_MKM]
        
        pivot_df.plot(kind='bar', ax=plt.gca(), width=0.8)
    
    plt.title('Number of Simulations with a Hit per Planet (by Distance Threshold)')
    plt.ylabel('Number of Simulations')
    plt.xlabel('Planet')
    plt.legend(title='Distance (< MKM)')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/hits_per_planet.png")
    print(f"Saved hits per planet histogram to {output_dir}/hits_per_planet.png")

    # Histogram 2: Hits per simulation
    plt.figure(figsize=(10, 6))
    # Number of planets hit in each simulation (at 100 MKM threshold)
    threshold_100_mkm = 100
    threshold_100_au = 100 * 1e6 / AU_KM
    
    num_trials = len(data)
    if not hits_df.empty:
        # Filter for hits within 100 MKM
        hits_at_100 = hits_df[hits_df['min_distance_au'] <= threshold_100_au]
        hits_per_sim = hits_at_100.groupby('simulation_id')['planet'].nunique()
        counts = hits_per_sim.value_counts()
        num_with_hits = hits_per_sim.index.nunique()
    else:
        counts = pd.Series()
        num_with_hits = 0

    # Add 0 hits case
    counts[0] = num_trials - num_with_hits
    
    # Ensure all possibilities 0 to 8 are present
    all_counts = pd.Series(0, index=range(9))
    for i in counts.index:
        if i < 9:
            all_counts[i] = counts[i]
    
    all_counts.plot(kind='bar')
    plt.title(f'Number of Planets Hit per Simulation (at < 100 MKM)')
    plt.xlabel('Number of Planets Hit')
    plt.ylabel('Number of Simulations')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/hits_per_simulation.png")
    print(f"Saved hits per simulation histogram (at 100 MKM) to {output_dir}/hits_per_simulation.png")


def calculate_p_value(simulation_data):
    # Calculate actual minimum distances for 3I/ATLAS
    ts = load.timescale()
    Tp = ELEMENTS_3I['Tp_jd']
    dt_days = np.arange(-730, 730, 2)
    t_eval = Tp + dt_days

    comet_pos = orbital_elements_to_pos_vel(
        ELEMENTS_3I['a'], ELEMENTS_3I['e'], ELEMENTS_3I['i'],
        ELEMENTS_3I['node'], ELEMENTS_3I['peri'], 
        T_p=Tp, t_array=t_eval
    )
    
    eps = np.deg2rad(23.4392911)
    c = np.cos(eps)
    s = np.sin(eps)
    R_ecl_to_eq = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    comet_pos_eq = comet_pos @ R_ecl_to_eq.T

    planet_pos_icrs = get_planet_positions_batch(ts, t_eval)
    
    actual_min_dists = {}
    for i, planet_name in enumerate(PLANET_NAMES):
        if planet_name in ['Venus', 'Mars', 'Jupiter']:
            diff = planet_pos_icrs[:, i, :] - comet_pos_eq
            dists = np.linalg.norm(diff, axis=1)
            actual_min_dists[planet_name] = dists.min()

    print("\nActual Minimum Distances:")
    for planet, dist in actual_min_dists.items():
        print(f"  {planet}: {dist:.4f} AU")

    # Calculate p-values
    print("\nP-values:")
    mask = np.ones(len(simulation_data), dtype=bool)
    for planet, actual_dist in actual_min_dists.items():
        planet_idx = PLANET_NAMES.index(planet)
        p_value = np.sum(simulation_data[:, planet_idx] <= actual_dist) / len(simulation_data)
        mask &= (simulation_data[:, planet_idx] <= actual_dist)
        print(f"  {planet}: {p_value:.4f}")
    
    joint_p_value = np.sum(mask) / len(simulation_data)
    print(f"\nJoint P-value (Venus & Mars & Jupiter): {joint_p_value:.6f}")
    
    return actual_min_dists, joint_p_value


if __name__ == "__main__":
    output_dir_data = 'data/montecarlo_orbit_simulation'
    output_dir_viz = 'visualizations/montecarlo_orbit_simulation'
    os.makedirs(output_dir_data, exist_ok=True)
    os.makedirs(output_dir_viz, exist_ok=True)

    # Part 1: 3I ATLAS
    print("Running Part 1: 3I ATLAS fixed, random times...")
    data_3i = run_simulation(num_trials=10000, comet_type='3I')
    
    # Save raw simulation data
    df_3i = pd.DataFrame(data_3i, columns=PLANET_NAMES)
    df_3i.to_csv(f"{output_dir_data}/montecarlo_simulation_min_distances.csv", index=False)
    print(f"Saved simulation minimum distances to {output_dir_data}/montecarlo_simulation_min_distances.csv")

    process_results(data_3i, output_dir_viz)

    actual_min_dists, joint_p_value = calculate_p_value(data_3i)
    
    # Generate report in results directory
    report_dir = 'results/montecarlo_orbit_simulation'
    os.makedirs(report_dir, exist_ok=True)
    
    # Calculate additional statistics for the report
    num_trials = len(data_3i)
    
    # Meaningful Baseline Threshold: 100 million km (~0.668 AU)
    threshold_100_mkm_au = 100 * 1e6 / AU_KM
    mask_100 = data_3i <= threshold_100_mkm_au
    num_hits_per_sim_100 = np.sum(mask_100, axis=1)
    prob_at_least_3_100 = np.sum(num_hits_per_sim_100 >= 3) / num_trials
    prob_at_least_4_100 = np.sum(num_hits_per_sim_100 >= 4) / num_trials
    
    # Calculate how many simulations hit at least as many planets as 3I ATLAS did (3)
    # at the 100 MKM threshold.
    hits_3_or_more = np.sum(num_hits_per_sim_100 >= 3)

    with open(f"{report_dir}/README.md", "w") as f:
        f.write("# 3I/ATLAS Monte Carlo Simulation Results\n\n")
        
        f.write("## 1. Probability Analysis: Pre-hoc vs. Post-hoc Perspectives\n\n")
        
        f.write("A critical distinction in this analysis is between the probability of a *specific* event and the probability of *any* event of a certain class.\n\n")
        
        f.write("### The 'Any 3+ Planet' Baseline (Meaningful Pre-hoc Probability)\n")
        f.write(f"To assess if 3I/ATLAS is truly anomalous, we must first look at how often any comet with its orbital parameters would pass within 'tens of millions of kilometers' (< 100 million km) of any 3 or more planets. This represents the background probability of a multi-planet encounter.\n\n")
        
        f.write("| Multi-Planet Encounter Class | Probability (at < 100 MKM) |\n")
        f.write("| --- | --- |\n")
        f.write(f"| At least 3 planets | {prob_at_least_3_100:.4f} ({int(prob_at_least_3_100*num_trials)} in {num_trials}) |\n")
        f.write(f"| At least 4 planets | {prob_at_least_4_100:.4f} ({int(prob_at_least_4_100*num_trials)} in {num_trials}) |\n")
        f.write(f"| At least 5 planets | {np.sum(num_hits_per_sim_100 >= 5)/num_trials:.4f} |\n\n")
        
        f.write(f"In our simulation of {num_trials} trials, **{hits_3_or_more} simulations** resulted in a close approach to 3 or more planets within 100 million km. This suggests that while multi-planet encounters are not the default, they are a statistically significant possibility (approx. {prob_at_least_3_100*100:.1f}%) for this specific orbit.\n\n")
        
        f.write("### The Specific 3I/ATLAS Anomaly (Post-hoc Configuration)\n")
        f.write(f"The 'Joint P-value' calculated below ({joint_p_value:.6f}) measures the probability of hitting Venus, Mars, and Jupiter at their *exact* observed proximities simultaneously. ")
        f.write("While this value is extremely low, it is a **post-hoc probability**—it measures the rarity of a specific outcome after it has already occurred. ")
        f.write(f"When viewed against the broader {prob_at_least_3_100*100:.1f}% chance of hitting *any* three planets, the observed configuration is less of a statistical impossibility and more of a specific (albeit very precise) instance of a broader class of multi-planet encounters.\n\n")
        
        f.write("| Planet | Actual Min Distance (AU) | Individual P-value |\n")
        f.write("| --- | --- | --- |\n")
        for planet, dist in actual_min_dists.items():
            planet_idx = PLANET_NAMES.index(planet)
            p_val = np.sum(data_3i[:, planet_idx] <= dist) / num_trials
            f.write(f"| {planet} | {dist:.4f} | {p_val:.4f} |\n")
        
        f.write(f"\n**Joint P-value for observed Venus-Mars-Jupiter config: {joint_p_value:.6f}**\n\n")
        
        f.write("## 2. Conclusion\n\n")
        f.write("The trajectory of 3I/ATLAS is undoubtedly 'fine-tuned' in the sense that it occupies a very small volume of the possible parameter space. However, it should be reported that:\n")
        f.write(f"1. There is a **{prob_at_least_3_100*100:.1f}% chance** for this interstellar object to pass within 100 million km of at least 3 planets.\n")
        f.write("2. The specific configuration observed is a particularly close and 'clean' version of these possible multi-planet passes, but its significance should be weighed against the background probability of multi-planet encounters for this orbit.\n\n")
        
        f.write("## 3. Visualizations\n\n")
        f.write("### Hits per Planet (by Distance Threshold)\n")
        f.write("![Hits per Planet](../../visualizations/montecarlo_orbit_simulation/hits_per_planet.png)\n\n")
        f.write("### Hits per Simulation (at 100 MKM threshold)\n")
        f.write("![Hits per Simulation](../../visualizations/montecarlo_orbit_simulation/hits_per_simulation.png)\n")
    
    print(f"\nGenerated results report at {report_dir}/README.md")
    
    # Part 2: Random Comets (optional, can be run by uncommenting)
    # print("\nRunning Part 2: Random Comets...")
    # data_random = run_simulation(num_trials=10000, comet_type='Random')
    # process_results(data_random, output_dir_viz)

