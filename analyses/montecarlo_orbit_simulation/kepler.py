import numpy as np

# Constants
AU_KM = 149597870.7
K = 0.01720209895
GM = K**2

def solve_hyperbolic_kepler(M, e, tol=1e-8, max_iter=100):
    """
    Solve Kepler's equation for hyperbolic orbit: M = e * sinh(H) - H
    using Newton-Raphson.
    M and e can be arrays.
    """
    H = M / (e - 1) # Initial guess
    
    # If e is array, ensure H is array
    if np.isscalar(H):
        H = np.array(H)
        
    for _ in range(max_iter):
        sinh_H = np.sinh(H)
        cosh_H = np.cosh(H)
        f = e * sinh_H - H - M
        df = e * cosh_H - 1
        dH = f / df
        H = H - dH
        if np.all(np.abs(dH) < tol):
            break
    return H

def orbital_elements_to_pos_vel(a, e, i_deg, node_deg, peri_deg, T_p, t_array):
    """
    Calculate position vectors for an array of times.
    Supports vectorized inputs for elements (Batch,) and times (Steps,).
    
    a: semi-major axis (AU). Shape (Batch,) or scalar.
    e: eccentricity (> 1). Shape (Batch,) or scalar.
    i_deg: inclination (degrees). Shape (Batch,) or scalar.
    node_deg: LAN (degrees). Shape (Batch,) or scalar.
    peri_deg: Arg Peri (degrees). Shape (Batch,) or scalar.
    T_p: Time of perihelion (days). Shape (Batch,) or scalar.
    t_array: Time points (days). Shape (Steps,).
    
    Returns:
    r_vec: (Batch, Steps, 3) or (Steps, 3) if batch=1
    """
    
    # Ensure inputs are arrays for broadcasting
    # If scalar, keep as scalar or 0-d array, numpy handles it.
    # But if we want specific output shape (Batch, Steps, 3), we need to be careful.
    
    # Cast to arrays
    a = np.asarray(a)
    e = np.asarray(e)
    i_deg = np.asarray(i_deg)
    node_deg = np.asarray(node_deg)
    peri_deg = np.asarray(peri_deg)
    T_p = np.asarray(T_p)
    t_array = np.asarray(t_array)
    
    # Reshape for broadcasting:
    # Elements: (Batch, 1)
    # Time: (1, Steps)
    
    # Check if batch dimension exists
    is_batch = a.ndim > 0 or e.ndim > 0
    
    if is_batch:
        a = a.reshape(-1, 1)
        e = e.reshape(-1, 1)
        i = np.deg2rad(i_deg).reshape(-1, 1)
        node = np.deg2rad(node_deg).reshape(-1, 1)
        peri = np.deg2rad(peri_deg).reshape(-1, 1)
        T_p = T_p.reshape(-1, 1)
        t = t_array.reshape(1, -1)
    else:
        i = np.deg2rad(i_deg)
        node = np.deg2rad(node_deg)
        peri = np.deg2rad(peri_deg)
        t = t_array
    
    # Mean motion
    n = np.sqrt(GM / np.abs(a)**3) # (Batch, 1)
    
    # Mean anomaly
    dt = t - T_p # (Batch, Steps)
    M = n * dt
    
    # Solve Kepler
    H = solve_hyperbolic_kepler(M, e) # (Batch, Steps)
    
    # Orbital Coordinates
    # Hyperbolic: x = a(cosh H - e), y = -a sqrt(e^2-1) sinh H
    # Note: check y sign relative to true anomaly.
    # True anomaly nu: tan(nu/2) = sqrt((e+1)/(e-1)) tanh(H/2)
    # If H > 0, nu > 0.
    # x = r cos nu, y = r sin nu.
    # If H > 0, y should be positive?
    # Let's check: y_orb = -a ...
    # a < 0. So -a > 0. sqrt(...) > 0. sinh H > 0. So y_orb > 0. Correct.
    
    cosh_H = np.cosh(H)
    sinh_H = np.sinh(H)
    
    x_orb = a * (cosh_H - e)
    y_orb = -a * np.sqrt(e**2 - 1) * sinh_H
    z_orb = np.zeros_like(x_orb)
    
    # Rotations
    # Transform from Perifocal (Orbital) to Heliocentric Ecliptic
    # r_vec = Rz(-node) * Rx(-i) * Rz(-peri) * r_orb ? 
    # NO. Standard: r_vec = Rz(node) * Rx(i) * Rz(peri) * r_orb.
    # Because we apply rotations to the VECTOR:
    # 1. Rotate by peri around Z (aligns perihelion)
    # 2. Rotate by i around X (tilts plane)
    # 3. Rotate by node around Z (aligns node)
    
    # 1. Rotate by peri around Z
    cos_peri = np.cos(peri)
    sin_peri = np.sin(peri)
    
    x1 = x_orb * cos_peri - y_orb * sin_peri
    y1 = x_orb * sin_peri + y_orb * cos_peri
    z1 = z_orb
    
    # 2. Rotate by i around X
    cos_i = np.cos(i)
    sin_i = np.sin(i)
    
    x2 = x1
    y2 = y1 * cos_i - z1 * sin_i
    z2 = y1 * sin_i + z1 * cos_i
    
    # 3. Rotate by node around Z
    cos_node = np.cos(node)
    sin_node = np.sin(node)
    
    x3 = x2 * cos_node - y2 * sin_node
    y3 = x2 * sin_node + y2 * cos_node
    z3 = z2
    
    # Stack -> (Batch, Steps, 3)
    # x3 is (Batch, Steps)
    
    r_vec = np.stack([x3, y3, z3], axis=-1)
    
    if not is_batch:
        # if input was scalar elements, output (Steps, 3)
        # But our reshape logic handled it?
        # If scalar, is_batch=False.
        # x3 is (Steps,).
        pass
        
    return r_vec
