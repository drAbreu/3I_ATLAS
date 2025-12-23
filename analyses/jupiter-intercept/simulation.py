import numpy as np
import pandas as pd
from astroquery.jplhorizons import Horizons
from astropy.time import Time
from astropy import units as u
from poliastro.bodies import Sun, Jupiter
from poliastro.iod import izzo
from poliastro.twobody import Orbit
import matplotlib.pyplot as plt
import os

# --- Monkeypatch for poliastro 0.7.0 bug in rv_pqw ---
# This version of poliastro has a bug where it uses a scalar 0 in the velocity array
# which fails when nu is an array during plotting.
from poliastro.twobody import classical
def rv_pqw_fixed(k, p, ecc, nu):
    r_pqw = (np.array([np.cos(nu), np.sin(nu), 0 * nu]) * p / (1 + ecc * np.cos(nu))).T
    v_pqw = (np.array([-np.sin(nu), (ecc + np.cos(nu)), 0 * nu]) * np.sqrt(k / p)).T
    return r_pqw, v_pqw
classical.rv_pqw = rv_pqw_fixed
# ----------------------------------------------------

def get_state_vector(target_id, epoch):
    """
    Fetches the state vector (position, velocity) of a target from JPL Horizons.
    """
    obj = Horizons(id=target_id, location='@sun', epochs=epoch.jd)
    vectors = obj.vectors()
    
    r = np.array([vectors['x'][0], vectors['y'][0], vectors['z'][0]]) * u.AU
    v = np.array([vectors['vx'][0], vectors['vy'][0], vectors['vz'][0]]) * u.AU / u.d
    
    return r, v

def solve_lambert_transfer(r0, v0, target_id, start_epoch, min_days=50, max_days=2000, step_days=10):
    """
    Finds the optimal Lambert transfer to the target.
    """
    best_dv = float('inf')
    best_transfer = None
    best_arrival_epoch = None
    
    print(f"Scanning arrival dates from {min_days} to {max_days} days from {start_epoch.iso}...")
    
    for days in range(min_days, max_days, step_days):
        arrival_epoch = start_epoch + days * u.d
        
        try:
            r_target, _ = get_state_vector(target_id, arrival_epoch)
            (v_dep, v_arr), = izzo.lambert(Sun.k, r0, r_target, days * u.d)
            
            dv_vec = v_dep - v0
            dv = np.linalg.norm(dv_vec)
            
            if dv < best_dv:
                best_dv = dv
                best_transfer = (v_dep, v_arr)
                best_arrival_epoch = arrival_epoch
        except Exception:
            continue
            
    return best_dv, best_transfer, best_arrival_epoch

def plot_trajectory(scenario, start_epoch, arrival_epoch, r0, v0, v_required, output_dir):
    """
    Plots the 2D top-down view of the Solar System showing the trajectories.
    """
    from poliastro.plotting import OrbitPlotter

    # Original orbit
    original_orbit = Orbit.from_vectors(Sun, r0, v0, epoch=start_epoch)
    
    # Intercept orbit
    intercept_orbit = Orbit.from_vectors(Sun, r0, v_required, epoch=start_epoch)

    op = OrbitPlotter()
    op.plot(original_orbit, label="Original 3I/ATLAS")
    op.plot(intercept_orbit, label="Intercept Trajectory")

    op.ax.set_title(f"Jupiter Intercept Trajectories ({scenario})")
    
    fig = op.ax.figure
    fig.savefig(f"{output_dir}/{scenario}_trajectory.png")
    plt.close(fig)

def plot_speed_difference(scenario, start_epoch, arrival_epoch, r0, v0, v_required, output_dir):
    """
    Plots the speed difference between the real and the interception trajectories.
    """
    tof = (arrival_epoch - start_epoch).to(u.d)
    
    original_orbit = Orbit.from_vectors(Sun, r0, v0, epoch=start_epoch)
    intercept_orbit = Orbit.from_vectors(Sun, r0, v_required, epoch=start_epoch)
    
    time_span = np.linspace(0, tof.value, num=100) * u.d
    
    # In poliastro 0.7.0, .propagate() doesn't support array time_span
    original_speeds = []
    intercept_speeds = []
    for t in time_span:
        orb_orig = original_orbit.propagate(t)
        orb_inter = intercept_orbit.propagate(t)
        original_speeds.append(np.linalg.norm(orb_orig.v.to(u.km/u.s).value))
        intercept_speeds.append(np.linalg.norm(orb_inter.v.to(u.km/u.s).value))
    
    speed_diff = np.array(intercept_speeds) - np.array(original_speeds)
    
    plt.figure(figsize=(10, 6))
    plt.plot(time_span.value, speed_diff)
    plt.title(f"Speed Difference (Intercept - Original) ({scenario})")
    plt.xlabel("Time (days)")
    plt.ylabel("Speed Difference (km/s)")
    plt.grid(True)
    plt.savefig(f"{output_dir}/{scenario}_speed_difference.png")
    plt.close()
    
def compare_delta_v(dv_val_kms, output_dir, scenario):
    """
    Compares the required delta-V to known probes and ships.
    """
    probes = {
        "Launch to LEO": 9.4,
        "Earth Escape from LEO": 3.2,
        "Voyager 1": 17,
        "New Horizons": 16.26,
        "Parker Solar Probe": 15.4
    }
    
    with open(f"{output_dir}/{scenario}_delta_v_comparison.txt", "w") as f:
        f.write("Delta-V Comparison\n")
        f.write("==================\n\n")
        f.write(f"Required Delta-V for 3I/ATLAS intercept: {dv_val_kms:.3f} km/s\n\n")
        f.write("Reference Delta-V values:\n")
        for name, dv in probes.items():
            f.write(f"- {name}: {dv} km/s\n")

def analyze_structural_integrity(dv_val_kms, time_of_flight, output_dir, scenario):
    """
    Calculates the g-forces and analyzes the structural integrity.
    """
    acceleration = (dv_val_kms * 1000 * u.m / u.s) / (time_of_flight)
    g_force = acceleration.to(u.g_force).value
    
    with open(f"{output_dir}/{scenario}_structural_integrity_analysis.txt", "w") as f:
        f.write("Structural Integrity Analysis\n")
        f.write("============================\n\n")
        f.write(f"Required continuous acceleration: {acceleration:.4f}\n")
        f.write(f"Equivalent to {g_force:.4f} g\n\n")
        f.write("Assuming 3I/ATLAS is a 'rubble pile' comet with low tensile strength, ")
        f.write("such a continuous acceleration would likely cause structural failure and disintegration.")

def run_scenario(scenario_name, start_time):
    obj_id = "C/2025 N1"  # 3I ATLAS
    jup_id = "599"        # Jupiter
    
    output_dir_data = f'data/jupiter_intercept/{scenario_name}'
    output_dir_viz = f'visualizations/jupiter_intercept/{scenario_name}'
    output_dir_docs = f'docs/jupiter_intercept/{scenario_name}'
    os.makedirs(output_dir_data, exist_ok=True)
    os.makedirs(output_dir_viz, exist_ok=True)
    os.makedirs(output_dir_docs, exist_ok=True)

    print(f"--- Running scenario: {scenario_name} ---")
    print(f"Fetching initial state for {obj_id} at {start_time.iso}...")
    try:
        r0, v0 = get_state_vector(obj_id, start_time)
    except Exception as e:
        print(f"Failed to fetch object data: {e}")
        return

    print("Calculating optimal intercept trajectory (Lambert)...")
    dv, transfer, arrival_time = solve_lambert_transfer(r0, v0, jup_id, start_time)
    
    if transfer is None:
        print("Could not find a valid transfer.")
        return
        
    v_required = transfer[0]
    dv_val_kms = dv.to(u.km/u.s).value
    
    print(f"Optimal Intercept Found:")
    print(f"  Arrival Date: {arrival_time.iso}")
    print(f"  Required Delta-V: {dv_val_kms:.3f} km/s")

    # Generate plots and analysis
    plot_trajectory(scenario_name, start_time, arrival_time, r0, v0, v_required, output_dir_viz)
    plot_speed_difference(scenario_name, start_time, arrival_time, r0, v0, v_required, output_dir_viz)
    compare_delta_v(dv_val_kms, output_dir_docs, scenario_name)
    tof = (arrival_time - start_time).to(u.s)
    analyze_structural_integrity(dv_val_kms, tof, output_dir_docs, scenario_name)

    # Generate Data Table
    data = []
    intercept_orbit = Orbit.from_vectors(Sun, r0, v_required, epoch=start_time)
    days_to_simulate = int((arrival_time - start_time).jd)
    step = 10
    
    print("\nGenerating simulation data...")
    for day_offset in range(0, days_to_simulate, step):
        current_time = start_time + day_offset * u.d
        
        try:
            r_obs, v_obs = get_state_vector(obj_id, current_time)
            vel_obs = np.linalg.norm(v_obs.to(u.km/u.s))
        except:
            continue
            
        r_hyp = intercept_orbit.propagate(day_offset * u.d).r
        v_hyp = intercept_orbit.propagate(day_offset * u.d).v
        vel_hyp = np.linalg.norm(v_hyp.to(u.km/u.s))
        
        row = {
            "Date": current_time.iso[:10],
            "Days_From_Start": day_offset,
            "Obs_Dist_AU": np.linalg.norm(r_obs.to(u.AU).value),
            "Hyp_Dist_AU": np.linalg.norm(r_hyp.to(u.AU).value),
            "Obs_Vel_km_s": vel_obs.value,
            "Hyp_Vel_km_s": vel_hyp.value,
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    df.to_csv(f"{output_dir_data}/{scenario_name}_simulation_data.csv", index=False)
    print(f"Data saved to {output_dir_data}/{scenario_name}_simulation_data.csv")

def main():
    # Scenario 1: Start from "today"
    start_time_today = Time("2025-12-22", scale='tdb')
    run_scenario("today", start_time_today)

    # Scenario 2: Start from discovery date
    start_time_discovery = Time("2025-07-01", scale='tdb')
    run_scenario("discovery", start_time_discovery)

if __name__ == "__main__":
    main()
