#!/usr/bin/env python3
"""
Create a visualization showing the angular separation between
3I/ATLAS and the Wow! Signal direction
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from astropy.coordinates import SkyCoord
from astropy import units as u

# Set up figure
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Wow! Signal coordinates (J2000)
wow_ra = 291.3792  # degrees
wow_dec = -26.95   # degrees

# 3I/ATLAS position on Aug 15, 1977 (Loeb's claim)
atlas_ra = 295.0   # degrees
atlas_dec = -19.0  # degrees

# Create coordinate objects
wow_coord = SkyCoord(wow_ra*u.deg, wow_dec*u.deg, frame='icrs')
atlas_coord = SkyCoord(atlas_ra*u.deg, atlas_dec*u.deg, frame='icrs')

# Calculate separation
separation = atlas_coord.separation(wow_coord).deg

# Plot setup - centered on Wow! Signal
center_ra = wow_ra
center_dec = wow_dec

# Plot range: ±10 degrees
plot_range = 12

ax.set_xlim(center_ra - plot_range, center_ra + plot_range)
ax.set_ylim(center_dec - plot_range, center_dec + plot_range)

# Grid
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xlabel('Right Ascension (degrees)', fontsize=14, fontweight='bold')
ax.set_ylabel('Declination (degrees)', fontsize=14, fontweight='bold')
ax.set_title('Angular Separation: 3I/ATLAS vs Wow! Signal\n(August 15, 1977)', 
             fontsize=16, fontweight='bold', pad=20)

# Plot Wow! Signal position
ax.scatter(wow_ra, wow_dec, s=500, c='red', marker='*', 
          edgecolors='darkred', linewidths=2, zorder=5,
          label='Wow! Signal (1977)')

# Add error circle for Wow! Signal (±20 arcmin in Dec)
wow_error = 20/60  # convert arcmin to degrees
circle_wow = Circle((wow_ra, wow_dec), wow_error, 
                    color='red', fill=False, linestyle='--', 
                    linewidth=2, alpha=0.5, label='Wow! Signal uncertainty')
ax.add_patch(circle_wow)

# Plot 3I/ATLAS position
ax.scatter(atlas_ra, atlas_dec, s=300, c='blue', marker='o', 
          edgecolors='darkblue', linewidths=2, zorder=5,
          label='3I/ATLAS (Loeb\'s claim)')

# Draw line connecting them
ax.plot([wow_ra, atlas_ra], [wow_dec, atlas_dec], 
        'k--', linewidth=2, alpha=0.7)

# Add separation annotation
mid_ra = (wow_ra + atlas_ra) / 2
mid_dec = (wow_dec + atlas_dec) / 2
ax.annotate(f'{separation:.2f}°\n= {separation*60:.0f} arcmin', 
           xy=(mid_ra, mid_dec), 
           fontsize=14, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8),
           ha='center')

# Add reference: Full Moon angular diameter
moon_diameter = 0.5  # degrees
# Plot several Moon reference circles
for i in range(int(separation/moon_diameter) + 2):
    moon_circle = Circle((wow_ra, wow_dec), moon_diameter * (i+1), 
                        color='gray', fill=False, linestyle=':', 
                        linewidth=1, alpha=0.3)
    ax.add_patch(moon_circle)
    if i == 0:
        ax.text(wow_ra + moon_diameter + 0.5, wow_dec, 
               f'{i+1} Moon', fontsize=9, alpha=0.6, style='italic')
    elif (i+1) % 3 == 0:
        ax.text(wow_ra + moon_diameter * (i+1) + 0.5, wow_dec, 
               f'{i+1} Moons', fontsize=9, alpha=0.6, style='italic')

# Add scale bar showing 1 degree
scale_start = center_ra - plot_range + 2
scale_y = center_dec - plot_range + 1
ax.plot([scale_start, scale_start + 1], [scale_y, scale_y], 
        'k-', linewidth=3)
ax.text(scale_start + 0.5, scale_y - 0.5, '1°', 
       ha='center', fontsize=11, fontweight='bold')

# Add Moon reference
moon_y = center_dec - plot_range + 3
ax.plot([scale_start, scale_start + moon_diameter], [moon_y, moon_y], 
        'gray', linewidth=3)
ax.text(scale_start + moon_diameter/2, moon_y - 0.5, 'Full Moon (0.5°)', 
       ha='center', fontsize=10, style='italic', color='gray')

# Legend
ax.legend(loc='upper right', fontsize=11, framealpha=0.9)

# Add text box with key information
textstr = f'Key Facts:\n' \
          f'• Angular separation: {separation:.2f}°\n' \
          f'• That\'s ~{separation/moon_diameter:.0f}× the Moon\'s diameter!\n' \
          f'• Component separation:\n' \
          f'  - RA: {abs(atlas_ra - wow_ra):.2f}°\n' \
          f'  - Dec: {abs(atlas_dec - wow_dec):.2f}°\n' \
          f'• Sky coverage probability: 0.53%'

props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
       verticalalignment='top', bbox=props, family='monospace')

# Invert RA axis (astronomical convention)
ax.invert_xaxis()

plt.tight_layout()
plt.savefig('visualizations/wow/wow_signal_separation.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved to: wow_signal_separation.png")

# Create a second figure showing scale comparison
fig2, ax2 = plt.subplots(1, 1, figsize=(10, 8))

# Data for comparison
objects = ['Full Moon', 'Wow!-3I/ATLAS\nseparation', 'Small sample\nprobability']
sizes = [0.5, separation, 100*0.53]  # Full Moon, separation, probability in %
colors = ['gray', 'red', 'green']
labels = ['0.5°', f'{separation:.2f}°', '0.53% of sky']

# Create horizontal bar chart
y_pos = np.arange(len(objects))
bars = ax2.barh(y_pos, sizes, color=colors, alpha=0.7, edgecolor='black', linewidth=2)

# Add value labels on bars
for i, (bar, label) in enumerate(zip(bars, labels)):
    width = bar.get_width()
    ax2.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
            label, ha='left', va='center', fontsize=12, fontweight='bold')

ax2.set_yticks(y_pos)
ax2.set_yticklabels(objects, fontsize=12)
ax2.set_xlabel('Angular Size (degrees) / Probability (%)', fontsize=12, fontweight='bold')
ax2.set_title('Scale Comparison:\nHow "Close" is 8.4 degrees?', 
             fontsize=14, fontweight='bold', pad=20)
ax2.grid(axis='x', alpha=0.3, linestyle='--')

# Add annotation
note = "The separation is 17× larger than the Moon!\n" \
       "A 0.5% probability is not that remarkable\n" \
       "when we've only detected 3 interstellar objects."
ax2.text(0.95, 0.05, note, transform=ax2.transAxes, 
        fontsize=10, verticalalignment='bottom', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
        style='italic')

plt.tight_layout()
plt.savefig('visualizations/wow/wow_signal_scale_comparison.png', dpi=300, bbox_inches='tight')
print("Scale comparison saved to: wow_signal_scale_comparison.png")
print("\nAll visualizations created successfully!")
