#!/usr/bin/env python3
"""
Analysis of the claim that 3I/ATLAS is connected to the Wow! Signal

This script calculates:
1. The actual angular separation between 3I/ATLAS and Wow! Signal in 1977
2. The energy required to change trajectories
"""

import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, get_body_barycentric
from astropy import units as u
from astroquery.jplhorizons import Horizons
import matplotlib.pyplot as plt

# Wow! Signal coordinates (J2000)
# Two possible positions due to dual horn antenna
WOW_RA1 = "19h25m31s"  # First possible position
WOW_RA2 = "19h28m22s"  # Second possible position
WOW_DEC = "-26d57m00s"  # Declination (same for both)

wow_coord1 = SkyCoord(WOW_RA1, WOW_DEC, frame='icrs')
wow_coord2 = SkyCoord(WOW_RA2, WOW_DEC, frame='icrs')

print("="*80)
print("Debunking the 3I/ATLAS - Wow! Signal Connection")
print("="*80)
print("\n1. WOW! SIGNAL COORDINATES")
print("-"*80)
print(f"Wow! Signal Position 1: RA = {wow_coord1.ra.deg:.4f}°, Dec = {wow_coord1.dec.deg:.4f}°")
print(f"Wow! Signal Position 2: RA = {wow_coord2.ra.deg:.4f}°, Dec = {wow_coord2.dec.deg:.4f}°")

# Query JPL Horizons for 3I/ATLAS position on August 15, 1977
print("\n2. 3I/ATLAS POSITION ON AUGUST 15, 1977")
print("-"*80)

# Date of Wow! Signal
wow_date = Time('1977-08-15 23:16:00', scale='utc')  # Approximate time of signal

try:
    # Query 3I/ATLAS (ID: 90003880 for interstellar comets, or we can try C/2025 N1)
    # First, let's try different object identifiers
    obj_ids = ['3I', 'C/2025 N1', '90003880']
    
    for obj_id in obj_ids:
        try:
            print(f"\nTrying object ID: {obj_id}")
            obj = Horizons(id=obj_id, 
                          location='500@0',  # Solar System Barycenter
                          epochs=wow_date.jd)
            
            # Get ephemerides
            eph = obj.ephemerides()
            
            if len(eph) > 0:
                atlas_ra = eph['RA'][0]
                atlas_dec = eph['DEC'][0]
                atlas_distance = eph['r'][0]  # heliocentric distance in AU
                
                print(f"\nSUCCESS! Using {obj_id}")
                print(f"3I/ATLAS Position on {wow_date.iso}:")
                print(f"  RA  = {atlas_ra:.4f}°")
                print(f"  Dec = {atlas_dec:.4f}°")
                print(f"  Heliocentric distance = {atlas_distance:.2f} AU")
                
                # Create coordinate object
                atlas_coord = SkyCoord(atlas_ra*u.deg, atlas_dec*u.deg, frame='icrs')
                
                # Calculate angular separations
                sep1 = atlas_coord.separation(wow_coord1)
                sep2 = atlas_coord.separation(wow_coord2)
                
                print("\n3. ANGULAR SEPARATION CALCULATION")
                print("-"*80)
                print(f"Angular separation from Wow! Position 1: {sep1.deg:.4f}° = {sep1.arcmin:.2f} arcmin")
                print(f"Angular separation from Wow! Position 2: {sep2.deg:.4f}° = {sep2.arcmin:.2f} arcmin")
                
                # Use the smaller separation
                min_sep = min(sep1, sep2)
                print(f"\nMinimum separation: {min_sep.deg:.4f}°")
                
                # Calculate solid angle probability
                # For a random alignment, the probability is approximately:
                # P ≈ (π * θ²) / (4π) = θ² / 4 for small θ
                # More accurately: solid angle = 2π(1 - cos(θ))
                solid_angle = 2 * np.pi * (1 - np.cos(min_sep.radian))
                prob = solid_angle / (4 * np.pi)
                
                print(f"\nProbability of random alignment within {min_sep.deg:.2f}°: {prob*100:.2f}%")
                print(f"(Compare to Loeb's claimed 0.6% for 9° separation)")
                
                # Component-wise separation
                dra = abs(atlas_ra - wow_coord1.ra.deg)
                ddec = abs(atlas_dec - wow_coord1.dec.deg)
                
                print(f"\nComponent separations from Wow! Position 1:")
                print(f"  ΔRA  = {dra:.4f}° ({dra*60:.2f} arcmin)")
                print(f"  ΔDec = {ddec:.4f}° ({ddec*60:.2f} arcmin)")
                
                break
        except Exception as e:
            print(f"Failed with {obj_id}: {e}")
            continue
    else:
        print("\nCould not retrieve 3I/ATLAS data from JPL Horizons")
        print("This might be because the object designation is not yet in the system")
        print("or requires a different identifier.")
        
        # Use Loeb's claimed values for the analysis
        print("\nUsing Loeb's claimed positions for demonstration:")
        atlas_ra = 295.0  # 19h40m = 295°
        atlas_dec = -19.0
        print(f"  RA  = {atlas_ra:.2f}°")
        print(f"  Dec = {atlas_dec:.2f}°")
        
        atlas_coord = SkyCoord(atlas_ra*u.deg, atlas_dec*u.deg, frame='icrs')
        
        sep1 = atlas_coord.separation(wow_coord1)
        sep2 = atlas_coord.separation(wow_coord2)
        
        print("\n3. ANGULAR SEPARATION CALCULATION")
        print("-"*80)
        print(f"Angular separation from Wow! Position 1: {sep1.deg:.4f}° = {sep1.arcmin:.2f} arcmin")
        print(f"Angular separation from Wow! Position 2: {sep2.deg:.4f}° = {sep2.arcmin:.2f} arcmin")
        
        min_sep = min(sep1, sep2)
        print(f"\nMinimum separation: {min_sep.deg:.4f}°")
        
        # Component-wise
        dra = abs(atlas_ra - wow_coord1.ra.deg)
        ddec = abs(atlas_dec - wow_coord1.dec.deg)
        
        print(f"\nComponent separations (using Loeb's RA=295°, Dec=-19°):")
        print(f"  ΔRA  = {dra:.2f}°")
        print(f"  ΔDec = {ddec:.2f}°")
        print(f"\nThis matches Loeb's claim of ~4° in RA and ~8° in Dec")
        
        atlas_distance = 600  # AU as claimed by Loeb

except Exception as e:
    print(f"\nError querying JPL Horizons: {e}")
    print("\nProceeding with Loeb's claimed values for educational purposes...")
    
    atlas_ra = 295.0  # 19h40m
    atlas_dec = -19.0
    atlas_distance = 600  # AU
    
    atlas_coord = SkyCoord(atlas_ra*u.deg, atlas_dec*u.deg, frame='icrs')
    
    sep1 = atlas_coord.separation(wow_coord1)
    sep2 = atlas_coord.separation(wow_coord2)
    
    print("\n3. ANGULAR SEPARATION CALCULATION")
    print("-"*80)
    print(f"Using Loeb's claimed 3I/ATLAS position: RA={atlas_ra}°, Dec={atlas_dec}°")
    print(f"Angular separation from Wow! Position 1: {sep1.deg:.4f}°")
    print(f"Angular separation from Wow! Position 2: {sep2.deg:.4f}°")
    
    min_sep = min(sep1, sep2)
    
    dra = abs(atlas_ra - wow_coord1.ra.deg)
    ddec = abs(atlas_dec - wow_coord1.dec.deg)
    
    # Calculate probability
    solid_angle = 2 * np.pi * (1 - np.cos(min_sep.radian))
    prob = solid_angle / (4 * np.pi)
    print(f"\nProbability of random alignment within {min_sep.deg:.2f}°: {prob*100:.2f}%")

# Calculate probability of alignment for conclusion
# (Need to ensure this is available in all code paths)
solid_angle = 2 * np.pi * (1 - np.cos(min_sep.radian))
prob = solid_angle / (4 * np.pi)

# Energy calculation
print("\n4. ENERGY REQUIRED FOR TRAJECTORY CHANGE")
print("-"*80)

# Current 3I/ATLAS parameters (known)
v_infinity_current = 58.0  # km/s - hyperbolic excess velocity (approaching Sun)
v_perihelion = 68.0  # km/s at perihelion

# Hypothetical: velocity needed if coming from Wow! direction
# If it was at ~10 km/s from Wow! direction (as Loeb suggests from blueshift)
# and now is at ~60 km/s from current direction
v_initial = 10.0  # km/s (hypothetical Wow! signal blueshift)
v_final = 60.0   # km/s (actual approach velocity to solar system)

# Estimate mass - for a nucleus of ~1-5 km diameter
# Typical comet density ~500 kg/m³
# For diameter = 3 km, volume = 4/3 * π * (1.5e3)³ m³
diameter_km = 3.0  # conservative estimate from observations
radius_m = (diameter_km * 1000) / 2
volume_m3 = (4/3) * np.pi * radius_m**3
density_kg_m3 = 500  # typical for comets
mass_kg = volume_m3 * density_kg_m3

print(f"Assumed comet parameters:")
print(f"  Diameter: {diameter_km} km")
print(f"  Mass: {mass_kg:.2e} kg ({mass_kg/1e12:.2f} trillion kg)")

# Angular change in velocity direction
# From Wow! direction to current direction
angular_separation_rad = min_sep.radian

# Calculate the delta-v required
# This is a change from one direction to another
# Minimum delta-v for direction change at constant speed:
# Δv = 2 * v * sin(θ/2)
# But we also have a magnitude change

# Method 1: Simple vector subtraction
# If velocity changed from v1 in direction 1 to v2 in direction 2
delta_v_magnitude_change = abs(v_final - v_initial)

# Direction change component
# Assuming velocity was v_initial in Wow! direction and changed to v_final in current direction
# Worst case: perpendicular change
# Better estimate: using actual angular separation
delta_v_direction = 2 * v_initial * np.sin(angular_separation_rad / 2)

# Total delta-v (vector sum - conservative estimate)
delta_v_total = np.sqrt(delta_v_magnitude_change**2 + delta_v_direction**2)

print(f"\nVelocity change analysis:")
print(f"  Initial velocity (from Wow! direction): {v_initial} km/s")
print(f"  Final velocity (current trajectory): {v_final} km/s")
print(f"  Angular separation: {min_sep.deg:.2f}°")
print(f"  Δv (magnitude change): {delta_v_magnitude_change:.2f} km/s")
print(f"  Δv (direction change): {delta_v_direction:.2f} km/s")
print(f"  Total Δv required: {delta_v_total:.2f} km/s")

# Kinetic energy required
# E = 0.5 * m * Δv²
delta_v_m_s = delta_v_total * 1000  # convert to m/s
energy_joules = 0.5 * mass_kg * delta_v_m_s**2

print(f"\nEnergy required for trajectory change:")
print(f"  Kinetic energy: {energy_joules:.2e} Joules")
print(f"  Equivalent to: {energy_joules/4.184e15:.2e} megatons of TNT")

# Compare to Tsar Bomba (largest nuclear weapon ever tested)
tsar_bomba_megatons = 50
equivalent_tsar_bombas = (energy_joules / 4.184e15) / tsar_bomba_megatons

print(f"  Equivalent to: {equivalent_tsar_bombas:.2e} Tsar Bomba explosions")

# Compare to annual world energy consumption
# World energy ~600 EJ/year = 6e20 J/year
world_annual_energy = 6e20  # Joules
years_of_world_energy = energy_joules / world_annual_energy

print(f"  Equivalent to: {years_of_world_energy:.2f} years of global energy consumption")

# Power requirement if done over distance traveled
# Time = distance / velocity
distance_au = atlas_distance
distance_m = distance_au * 1.496e11  # meters
time_s = distance_m / (v_initial * 1000)  # seconds
time_years = time_s / (365.25 * 24 * 3600)

power_watts = energy_joules / time_s

print(f"\nIf trajectory change occurred over {atlas_distance} AU:")
print(f"  Time available: {time_years:.2f} years")
print(f"  Required power: {power_watts:.2e} Watts")
print(f"  (For comparison, the Sun's total power output: ~3.8 × 10²⁶ W)")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print(f"The angular separation of {min_sep.deg:.2f}° is SIGNIFICANT, not small!")
print(f"This is approximately {min_sep.deg:.0f} times the angular diameter of the full Moon")
print(f"(The Moon appears about 0.5° across in the sky)")
print(f"\nThe energy required to change the comet's trajectory from the Wow! Signal")
print(f"direction to its current path would be astronomical - equivalent to")
print(f"{years_of_world_energy:.1f} years of ALL human energy production on Earth.")
print(f"\nThis 'coincidence' is not as remarkable as claimed when you consider:")
print(f"1. The sky has 41,253 square degrees")
print(f"2. A {min_sep.deg:.1f}° radius circle covers {100*prob:.2f}% of the sky")
print(f"3. We've only detected 3 interstellar objects - small sample size!")
print("="*80)