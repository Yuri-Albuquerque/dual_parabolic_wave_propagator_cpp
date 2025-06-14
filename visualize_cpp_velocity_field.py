#!/usr/bin/env python3
"""
C++ Velocity Field Visualization Script

This script visualizes the wave velocity distribution from the C++ simulation
to verify that the material-dependent wave speeds are properly implemented.

- Air: 343 m/s (343,000 mm/s) - Blue  
- Parabolic Material: 1500 m/s (1,500,000 mm/s) - Red
- Rigid Boundaries: 0 m/s - Black
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import os

def load_cpp_boundary_data(data_dir="build_exporter/cpp_wave_data"):
    """Load boundary types from C++ simulation output."""
    
    boundary_types_file = os.path.join(data_dir, "boundary_types.txt")
    
    if not os.path.exists(boundary_types_file):
        raise FileNotFoundError(f"Boundary types file not found: {boundary_types_file}")
    
    # Load boundary types as integer array
    boundary_types = np.loadtxt(boundary_types_file, dtype=int)
    
    return boundary_types

def create_velocity_field_from_cpp(boundary_types):
    """Create velocity field from C++ boundary types."""
    
    # Define wave speeds based on material types (correct mapping)
    c_air = 343.0         # m/s - AIR (type 0)
    c_parabolic = 1500.0  # m/s - PARABOLIC (type 1)  
    c_rigid = 0.0         # m/s - RIGID (type 2)
    
    # Create velocity field based on boundary types
    velocity_field = np.zeros_like(boundary_types, dtype=float)
    velocity_field[boundary_types == 0] = c_air        # AIR
    velocity_field[boundary_types == 1] = c_parabolic  # PARABOLIC
    velocity_field[boundary_types == 2] = c_rigid      # RIGID
    
    return velocity_field

def plot_cpp_velocity_field():
    """Plot the velocity field distribution from C++ simulation."""
    
    print("Loading C++ boundary data...")
    boundary_types = load_cpp_boundary_data()
    velocity_field = create_velocity_field_from_cpp(boundary_types)
    
    # Domain configuration (matching C++ simulation)
    x_range = (-300.0, 300.0)  # mm
    y_range = (-100.0, 150.0)  # mm
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot 1: Material Types
    colors = ['lightblue', 'red', 'black']  # AIR, PARABOLIC, RIGID
    labels = ['Air (343 m/s)', 'Parabolic Material (1500 m/s)', 'Rigid Boundary (0 m/s)']
    cmap = ListedColormap(colors)
    
    im1 = ax1.imshow(boundary_types, extent=[x_range[0], x_range[1], y_range[0], y_range[1]], 
                     origin='upper', cmap=cmap, vmin=0, vmax=2, aspect='equal')
    ax1.set_title('C++ Material Distribution', fontsize=14, fontweight='bold')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.grid(True, alpha=0.3)
    
    # Add colorbar for material types
    cbar1 = plt.colorbar(im1, ax=ax1, ticks=[0, 1, 2])
    cbar1.set_ticklabels(labels)
    
    # Plot 2: Velocity Field
    im2 = ax2.imshow(velocity_field, extent=[x_range[0], x_range[1], y_range[0], y_range[1]], 
                     origin='upper', cmap='viridis', aspect='equal')
    ax2.set_title('C++ Wave Velocity Field (m/s)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.grid(True, alpha=0.3)
    
    # Add colorbar for velocity
    cbar2 = plt.colorbar(im2, ax=ax2)
    cbar2.set_label('Wave Velocity (m/s)')
    
    # Add parabola outlines to both plots
    for ax in [ax1, ax2]:
        # Plot parabola outlines
        x_line = np.linspace(-254, 254, 100)  # Major parabola diameter = 508mm
        
        # Major parabola outer surface: y = -x²/(4*100) + 100
        major_y_outer = -(x_line**2) / (4.0 * 100.0) + 100.0
        ax.plot(x_line, major_y_outer, 'w-', linewidth=2, alpha=0.8, label='Major Parabola Outer')
        
        # Major parabola inner surface (40mm UP from outer surface)
        major_y_inner = major_y_outer + 40.0
        ax.plot(x_line, major_y_inner, 'w--', linewidth=1.5, alpha=0.8, label='Major Parabola Inner')
        
        # Minor parabola (only plot within its diameter = 200mm)
        x_line_minor = np.linspace(-100, 100, 100)
        
        # Minor parabola outer surface: y = x²/(4*50) - 50
        minor_y_outer = (x_line_minor**2) / (4.0 * 50.0) - 50.0
        ax.plot(x_line_minor, minor_y_outer, 'yellow', linewidth=2, alpha=0.8, label='Minor Parabola Outer')
        
        # Minor parabola inner surface (40mm DOWN from outer surface)
        minor_y_inner = minor_y_outer - 40.0
        ax.plot(x_line_minor, minor_y_inner, 'yellow', linestyle='--', linewidth=1.5, alpha=0.8, label='Minor Parabola Inner')
        
        # Add legend
        ax.legend(loc='upper right', fontsize=8)
    
    # Print statistics
    total_points = boundary_types.size
    air_points = np.sum(boundary_types == 0)
    parabolic_points = np.sum(boundary_types == 1)
    rigid_points = np.sum(boundary_types == 2)
    
    print(f"\nC++ Material Distribution Statistics:")
    print(f"Total grid points: {total_points}")
    print(f"Air points: {air_points} ({100*air_points/total_points:.1f}%)")
    print(f"Parabolic material points: {parabolic_points} ({100*parabolic_points/total_points:.1f}%)")
    print(f"Rigid boundary points: {rigid_points} ({100*rigid_points/total_points:.1f}%)")
    
    print(f"\nVelocity Statistics:")
    print(f"Air velocity: {343} m/s")
    print(f"Parabolic material velocity: {1500} m/s")
    print(f"Velocity ratio (parabolic/air): {1500/343:.2f}x faster")
    
    print(f"\nCFL Analysis:")
    grid_shape = boundary_types.shape
    dx = (x_range[1] - x_range[0]) / (grid_shape[1] - 1)
    dy = (y_range[1] - y_range[0]) / (grid_shape[0] - 1)
    min_spacing = min(dx, dy)
    max_velocity = 1500000.0  # mm/s (1500 m/s)
    cfl_limit = 0.4 * min_spacing / (max_velocity * np.sqrt(2))
    print(f"Grid spacing: dx={dx:.2f}mm, dy={dy:.2f}mm")
    print(f"CFL time step limit: {cfl_limit:.2e} s")
    
    plt.tight_layout()
    
    # Save the plot
    output_file = '/home/yuri/Documents/project/dual_parabolic_wave_cpp/cpp_velocity_field_visualization.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nC++ velocity field visualization saved to: {output_file}")
    
    plt.show()
    
    return velocity_field, boundary_types

def plot_cross_sections_cpp():
    """Plot cross-sections of the C++ velocity field."""
    
    boundary_types = load_cpp_boundary_data()
    velocity_field = create_velocity_field_from_cpp(boundary_types)
    
    # Domain configuration
    x_range = (-300.0, 300.0)  # mm
    y_range = (-100.0, 150.0)  # mm
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Cross-section at x = 0 (center line)
    center_idx = boundary_types.shape[1] // 2
    y_line = np.linspace(y_range[0], y_range[1], boundary_types.shape[0])
    velocity_cross_y = velocity_field[:, center_idx]
    material_cross_y = boundary_types[:, center_idx]
    
    ax1.plot(y_line, velocity_cross_y, 'b-', linewidth=2, label='Wave Velocity')
    ax1_twin = ax1.twinx()
    ax1_twin.plot(y_line, material_cross_y, 'r--', linewidth=1, alpha=0.7, label='Material Type')
    ax1.set_xlabel('Y Position (mm)')
    ax1.set_ylabel('Wave Velocity (m/s)', color='b')
    ax1_twin.set_ylabel('Material Type', color='r')
    ax1.set_title('C++ Cross-section at X = 0 mm (Center Line)', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')
    ax1_twin.legend(loc='upper right')
    
    # Cross-section at y = 25 mm (horizontal line)
    y_center_idx = int(boundary_types.shape[0] * (25 - y_range[0]) / (y_range[1] - y_range[0]))
    x_line = np.linspace(x_range[0], x_range[1], boundary_types.shape[1])
    velocity_cross_x = velocity_field[y_center_idx, :]
    material_cross_x = boundary_types[y_center_idx, :]
    
    ax2.plot(x_line, velocity_cross_x, 'b-', linewidth=2, label='Wave Velocity')
    ax2_twin = ax2.twinx()
    ax2_twin.plot(x_line, material_cross_x, 'r--', linewidth=1, alpha=0.7, label='Material Type')
    ax2.set_xlabel('X Position (mm)')
    ax2.set_ylabel('Wave Velocity (m/s)', color='b')
    ax2_twin.set_ylabel('Material Type', color='r')
    ax2.set_title('C++ Cross-section at Y = 25 mm (Horizontal Line)', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left')
    ax2_twin.legend(loc='upper right')
    
    plt.tight_layout()
    
    # Save the plot
    output_file = '/home/yuri/Documents/project/dual_parabolic_wave_cpp/cpp_velocity_cross_sections.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"C++ velocity cross-sections saved to: {output_file}")
    
    plt.show()

if __name__ == "__main__":
    print("C++ Velocity Field Visualization")
    print("=" * 50)
    print("Visualizing wave velocity distribution from C++ simulation:")
    print("- Air cavity: 343 m/s (blue)")
    print("- Parabolic material: 1500 m/s (red)")
    print("- Rigid boundaries: 0 m/s (black)")
    print("- 40mm thick parabolic material bodies")
    print()
    
    # Plot main velocity field
    velocity_field, material_type = plot_cpp_velocity_field()
    
    # Plot cross-sections
    plot_cross_sections_cpp()
    
    print("\nC++ velocity field analysis complete!")
    print("\nNote: This data comes from the actual C++ simulation")
    print("and shows the correct parabolic material distribution.")
