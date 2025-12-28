# 3I/ATLAS Research Repository: An Educational Journey 🌌

Welcome to the **3I/ATLAS Research Repository**. This project is dedicated to the scientific analysis of the third confirmed interstellar visitor to our solar system, **C/2025 N1 (3I/ATLAS)**.

This repository is designed to be **educational**. We believe that complex orbital mechanics and statistical analyses should be accessible to everyone. Here, you will find the code, data, and visualizations used to explore the mysteries of this interstellar object.

---

## 📖 Science Stories on Medium

Each major analysis in this repository is paired with an explanatory article on Medium. These articles translate the raw code and data into a narrative that anyone can follow.

| Analysis Module | Educational Article (Medium) |
| :--- | :--- |
| **🎲 Monte Carlo Probability** | [The 3I/ATLAS "Fine-Tuned" Approach: A Statistical Reality Check](https://medium.com/@datastar/the-3i-atlas-alien-mothership-claim-a-statistical-reality-check-b6f0f5126da2) |
| **🎯 Jupiter Intercept** | [Could we have caught 3I/ATLAS? The Physics of Intercept](https://medium.com/your-article-link) |
| **📡 The WoW Signal** | [Could 3I/ATLAS be related to the WoW! Signal?](https://medium.com/your-article-link) |

---

## 🔬 Core Research Modules

### 1. Jupiter Intercept Analysis ✅
**The Question:** Was 3I/ATLAS aimed at Jupiter's Hill radius, and could we have intercepted it?  
**The Method:** We used the Lambert problem solver, high-precision JPL ephemerides (`de421.bsp`), and Monte Carlo simulations of 400,000 trajectories.  
**The Verdict:** While initial data suggested a low-cost intercept (~5 km/s), refined orbital elements show a much higher requirement (~27 km/s). Furthermore, we demonstrate that passing through the Hill radius is a **50/50 event** for any object in Jupiter's neighborhood, demystifying the "aiming" claim.

- **Explore Code:** `analyses/jupiter_intercept/`
- **Documentation:** `docs/jupiter_intercept/`
- **Visualizations:** `visualizations/jupiter_intercept/`

### 2. General Monte Carlo Orbit Simulation 🎲
**The Question:** Was 3I/ATLAS "fine-tuned" to pass close to Earth's vicinity?  
**The Method:** We ran simulations randomizing the arrival time to see how often multi-planet encounters occur for this specific hyperbolic path.  
**The Verdict:** A "Triple Hit" (passing within 100 MKM of any 3 planets) happens in about 6% of cases. The observed configuration is a precise instance of this broader statistical class.

- **Explore Code:** `analyses/montecarlo_orbit_simulation/`
- **Results Report:** `results/montecarlo_orbit_simulation/README.md`

---

## 📂 Repository Structure

- `analyses/`: The "Engine Room" where all Python simulations live.
- `docs/`: Explanatory guides and methodology reports for each figure.
- `visualizations/`: High-resolution plots and infographics.
- `data/`: Raw ephemeris and simulation outputs.

---

## 🚀 Get Started

If you want to run these simulations yourself:

```bash
# 1. Clone the repo
git clone https://github.com/drAbreu/3I_ATLAS.git
cd 3I_ATLAS

# 2. Setup your environment
source .venv/bin/activate
pip install -r requirements.txt

# 3. Run a simulation
python analyses/jupiter_intercept/plot_1c_monte_carlo.py
```

---

## 📄 License

This project is open-source under the MIT License. Feel free to use the code for your own interstellar research!

**Last Updated**: December 2025
