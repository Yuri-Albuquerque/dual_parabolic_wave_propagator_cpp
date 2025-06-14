#!/usr/bin/env python3
"""
Corrected visualization of C++ wave simulation data with proper coordinate system alignment.
"""

import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from matplotlib.animation import FuncAnimation
import re

def load_cpp_geometry():
    """Load and correctly interpret C++ geometry data."""
    
    # Load boundary types from C++ simulation
    boundary_file = '/home/yuri/Documents/project/dual_parabolic_wave_cpp/build_exporter/cpp_wave_data/boundary_types.txt'
    
    if not os.path.exists(boundary_file):
        print(f"Error: {boundary_file} not found")
        return None, None, None
    
    # Read boundary types
    with open(boundary_file, 'r') as f:
        lines = f.readlines()
    
    # Skip header line if present
    data_lines = [line.strip() for line in lines if not line.startswith('#') and line.strip()]
    
    # Convert to numpy array
    boundary_data = []
    for line in data_lines:
        values = [int(val) for val in line.split()]
        boundary_data.extend(values)
    
    boundary_array = np.array(boundary_data)
    
    # C++ domain configuration (from metadata and WaveField.cpp)
    grid_size = 120
    x_min, x_max = -300.0, 300.0
    y_min, y_max = -100.0, 150.0
    
    # Reshape to 2D grid (120x120)
    boundary_types = boundary_array.reshape(grid_size, grid_size)
    
    print(f"Loaded C++ boundary data: {boundary_types.shape}")
    print(f"Boundary type distribution (C++ mapping):")
    print(f"  RIGID (0): {np.sum(boundary_types == 0)} ({100*np.sum(boundary_types == 0)/boundary_types.size:.1f}%)")
    print(f"  AIR (1): {np.sum(boundary_types == 1)} ({100*np.sum(boundary_types == 1)/boundary_types.size:.1f}%)")
    print(f"  PARABOLIC (2): {np.sum(boundary_types == 2)} ({100*np.sum(boundary_types == 2)/boundary_types.size:.1f}%)")
    
    # Remap boundary types to Python convention: 0=AIR, 1=PARABOLIC, 2=RIGID
    boundary_types_remapped = np.zeros_like(boundary_types)
    boundary_types_remapped[boundary_types == 1] = 0  # AIR: C++ 1 -> Python 0
    boundary_types_remapped[boundary_types == 2] = 1  # PARABOLIC: C++ 2 -> Python 1  
    boundary_types_remapped[boundary_types == 0] = 2  # RIGID: C++ 0 -> Python 2
    
    print(f"Remapped boundary type distribution (Python mapping):")
    print(f"  AIR (0): {np.sum(boundary_types_remapped == 0)} ({100*np.sum(boundary_types_remapped == 0)/boundary_types_remapped.size:.1f}%)")
    print(f"  PARABOLIC (1): {np.sum(boundary_types_remapped == 1)} ({100*np.sum(boundary_types_remapped == 1)/boundary_types_remapped.size:.1f}%)")
    print(f"  RIGID (2): {np.sum(boundary_types_remapped == 2)} ({100*np.sum(boundary_types_remapped == 2)/boundary_types_remapped.size:.1f}%)")
    
    # Use remapped boundary types
    boundary_types = boundary_types_remapped
    
    # Create coordinate grids matching C++ coordinate system
    dx = (x_max - x_min) / (grid_size - 1)
    dy = (y_max - y_min) / (grid_size - 1)
    
    x_coords = np.linspace(x_min, x_max, grid_size)
    y_coords = np.linspace(y_max, y_min, grid_size)  # NOTE: y_max to y_min (flipped)
    X, Y = np.meshgrid(x_coords, y_coords)
    
    print(f"C++ coordinate system recreation:")
    print(f"  Grid size: {grid_size}x{grid_size}")
    print(f"  X range: [{x_min}, {x_max}], dx = {dx:.3f}")
    print(f"  Y range: [{y_max}, {y_min}], dy = {-dy:.3f} (note: y_max to y_min)")
    print(f"  X shape: {X.shape}, Y shape: {Y.shape}")
    
    # Verify coordinate system matches C++
    print(f"Verification - Top-left corner:")
    print(f"  boundary_types[0,0] = {boundary_types[0,0]} at (x,y) = ({X[0,0]}, {Y[0,0]})")
    print(f"  Should be: x = {x_min}, y = {y_max}")
    
    print(f"Verification - Bottom-right corner:")
    print(f"  boundary_types[{grid_size-1},{grid_size-1}] = {boundary_types[grid_size-1,grid_size-1]} at (x,y) = ({X[grid_size-1,grid_size-1]}, {Y[grid_size-1,grid_size-1]})")
    print(f"  Should be: x = {x_max}, y = {y_min}")
    
    return X, Y, boundary_types

def load_wave_data(data_dir):
    """Load all wave data files."""
    wave_files = sorted(glob.glob(os.path.join(data_dir, 'wave_data_t*.txt')))
    
    wave_data = []
    times = []
    
    for file_path in wave_files:
        # Extract time step from filename
        match = re.search(r'wave_data_t(\d+)\.txt', os.path.basename(file_path))
        if match:
            time_step = int(match.group(1))
            
            # Load wave data
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Process all non-empty lines (no header filtering needed)
            data_lines = [line.strip() for line in lines if line.strip()]
            
            print(f"Loading {file_path}: {len(data_lines)} data lines")
            
            # Convert to numpy array
            wave_values = []
            for line in data_lines:
                values = [float(val) for val in line.split()]
                wave_values.extend(values)
            
            wave_array = np.array(wave_values)
            print(f"  Total values: {wave_array.size}, expected: {120*120}")
            
            if wave_array.size != 120*120:
                print(f"  ERROR: Size mismatch! Got {wave_array.size}, expected {120*120}")
                continue
            
            wave_2d = wave_array.reshape(120, 120)  # Reshape to match grid
            
            wave_data.append(wave_2d)
            times.append(time_step)
    
    return np.array(wave_data), np.array(times)

def create_corrected_animation():
    """Create animation with corrected coordinate system matching C++."""
    
    print("Loading C++ geometry data...")
    X, Y, boundary_types = load_cpp_geometry()
    
    if X is None:
        print("Failed to load geometry data")
        return
    
    print("\nLoading C++ wave data...")
    data_dir = '/home/yuri/Documents/project/dual_parabolic_wave_cpp/build_exporter/cpp_wave_data'
    wave_data, times = load_wave_data(data_dir)
    
    if len(wave_data) == 0:
        print("No wave data found")
        return
    
    print(f"Loaded {len(wave_data)} time steps")
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Geometry (Material types)
    im1 = ax1.imshow(boundary_types, extent=[X.min(), X.max(), Y.min(), Y.max()], 
                     origin='upper', cmap='viridis', aspect='equal')
    ax1.set_title('Material Geometry (C++ Data)\nMatching C++ Coordinate System')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.grid(True, alpha=0.3)
    
    # Add colorbar for geometry
    cbar1 = plt.colorbar(im1, ax=ax1)
    cbar1.set_label('Material: 0=Air, 1=Parabolic, 2=Rigid')
    
    # Plot 2: Wave amplitude (will be animated)
    vmin, vmax = -0.5, 0.5  # Adjust based on actual wave amplitude range
    im2 = ax2.imshow(wave_data[0], extent=[X.min(), X.max(), Y.min(), Y.max()], 
                     origin='upper', cmap='seismic', vmin=vmin, vmax=vmax, aspect='equal')
    ax2.set_title(f'Wave Amplitude - Time Step: {times[0]}')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.grid(True, alpha=0.3)
    
    # Add colorbar for wave amplitude
    cbar2 = plt.colorbar(im2, ax=ax2)
    cbar2.set_label('Wave Amplitude')
    
    # Add annotations to verify coordinate system
    ax1.text(-280, 130, 'Major Parabola\n(Top)', 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    ax1.text(-280, -80, 'Minor Parabola\n(Bottom)', 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="cyan", alpha=0.7))
    
    plt.tight_layout()
    
    def animate(frame):
        """Animation function."""
        if frame < len(wave_data):
            im2.set_array(wave_data[frame])
            ax2.set_title(f'Wave Amplitude - Time Step: {times[frame]}')
        return [im2]
    
    # Create animation
    anim = FuncAnimation(fig, animate, frames=len(wave_data), interval=200, blit=False, repeat=True)
    
    # Save as GIF
    output_path = '/home/yuri/Documents/project/dual_parabolic_wave_cpp/corrected_wave_animation.gif'
    print(f"\nSaving animation to {output_path}...")
    anim.save(output_path, writer='pillow', fps=5, dpi=100)
    print("Animation saved successfully!")
    
    # Also save static geometry plot
    geometry_path = '/home/yuri/Documents/project/dual_parabolic_wave_cpp/corrected_geometry.png'
    fig_geo, ax_geo = plt.subplots(1, 1, figsize=(10, 6))
    im_geo = ax_geo.imshow(boundary_types, extent=[X.min(), X.max(), Y.min(), Y.max()], 
                          origin='upper', cmap='viridis', aspect='equal')
    ax_geo.set_title('Corrected Geometry - C++ Coordinate System\n40mm Thick Parabolic Material Bodies')
    ax_geo.set_xlabel('X (mm)')
    ax_geo.set_ylabel('Y (mm)')
    ax_geo.grid(True, alpha=0.3)
    
    # Add parabola annotations
    ax_geo.text(-280, 130, 'Major Parabola\n(Concave down, 508mm dia)\n40mm thick material', 
               bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.8))
    ax_geo.text(-280, -80, 'Minor Parabola\n(Concave up, 200mm dia)\n40mm thick material', 
               bbox=dict(boxstyle="round,pad=0.5", facecolor="cyan", alpha=0.8))
    ax_geo.text(150, 25, 'Air Cavity\n(343 m/s)', 
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.8))
    ax_geo.text(200, 120, 'Parabolic Material\n(1500 m/s)', 
               bbox=dict(boxstyle="round,pad=0.5", facecolor="orange", alpha=0.8))
    
    cbar_geo = plt.colorbar(im_geo, ax=ax_geo)
    cbar_geo.set_label('Material: 0=Air, 1=Parabolic, 2=Rigid')
    
    plt.tight_layout()
    plt.savefig(geometry_path, dpi=150, bbox_inches='tight')
    print(f"Geometry plot saved to {geometry_path}")
    
    # Show plots
    plt.show()

if __name__ == "__main__":
    create_corrected_animation()
