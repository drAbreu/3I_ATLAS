import numpy as np
import pandas as pd
from astroquery.jplhorizons import Horizons
from astropy.time import Time
from astropy import units as u
from poliastro.bodies import Sun
from poliastro.iod import izzo
from poliastro.twobody import Orbit

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
    
    # Iterate to find the best window
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

def calculate_acceleration(r):
    """
    Calculates the gravitational acceleration due to the Sun at position r.
    a = -mu * r / |r|^3
    """
    r_mag = np.linalg.norm(r)
    a = -Sun.k * r / (r_mag**3)
    return a.to(u.m / u.s**2)

def main():
    obj_id = "C/2025 N1"  # 3I ATLAS
    jup_id = "599"        # Jupiter
    
    start_time = Time("2025-12-22", scale='tdb')
    
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
    
    # Generate Data Table
    data = []
    
    # Hyp orbit
    hyp_orbit = Orbit.from_vectors(Sun, r0, v_required, epoch=start_time)
    
    # Simulate for 18 months (approx 540 days)
    days_to_simulate = 550
    step = 10
    
    print("\nGenerating simulation data...")
    for day_offset in range(0, days_to_simulate, step):
        current_time = start_time + day_offset * u.d
        
        # Observed
        try:
            r_obs, v_obs = get_state_vector(obj_id, current_time)
            acc_obs = calculate_acceleration(r_obs)
            vel_obs = np.linalg.norm(v_obs.to(u.km/u.s))
        except:
            continue
            
        # Hypothetical
        r_hyp = hyp_orbit.propagate(day_offset * u.d).r
        v_hyp = hyp_orbit.propagate(day_offset * u.d).v
        acc_hyp = calculate_acceleration(r_hyp)
        vel_hyp = np.linalg.norm(v_hyp.to(u.km/u.s))
        
        row = {
            "Date": current_time.iso[:10],
            "Days_From_Start": day_offset,
            "Obs_Dist_AU": np.linalg.norm(r_obs.to(u.AU).value),
            "Hyp_Dist_AU": np.linalg.norm(r_hyp.to(u.AU).value),
            "Obs_Vel_km_s": vel_obs.value,
            "Hyp_Vel_km_s": vel_hyp.value,
            "Obs_Acc_m_s2": np.linalg.norm(acc_obs.value),
            "Hyp_Acc_m_s2": np.linalg.norm(acc_hyp.value)
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    df.to_csv("simulation_data.csv", index=False)
    print("Data saved to simulation_data.csv")
    
    # Create a summary report
    with open("simulation_report.txt", "w") as f:
        f.write("3I ATLAS Jupiter Intercept Simulation Report\n")
        f.write("============================================\n\n")
        f.write(f"Target Object: 3I ATLAS (C/2025 N1)\n")
        f.write(f"Simulation Start Date: {start_time.iso}\n")
        f.write(f"Observed Initial Position (AU): {np.linalg.norm(r0.to(u.AU).value):.3f}\n")
        f.write(f"Observed Initial Velocity (km/s): {np.linalg.norm(v0.to(u.km/u.s).value):.3f}\n\n")
        f.write("Intercept Maneuver Calculation:\n")
        f.write(f"  Target: Jupiter\n")
        f.write(f"  Optimal Arrival Date: {arrival_time.iso}\n")
        f.write(f"  Time of Flight: {(arrival_time - start_time).jd:.1f} days\n")
        f.write(f"  Required Delta-V: {dv_val_kms:.3f} km/s\n\n")
        f.write("Comparison Summary (First 5 steps):\n")
        f.write(df.head().to_string())
        f.write("\n\nFull data available in simulation_data.csv\n")

if __name__ == "__main__":
    main()
