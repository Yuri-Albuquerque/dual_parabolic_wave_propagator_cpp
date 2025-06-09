#!/usr/bin/env python3
"""
Wave Propagation Plotter - Create matplotlib snapshots of wave propagation

This script runs the dual parabolic wave simulation and creates a sequence of
matplotlib plots showing the wave front propagation over time.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import time
from pathlib import Path

# Add the python package to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

from dual_parabolic_wave.simulation import Simulation, PythonSimulation


def create_wave_colormap():
    """Create a custom colormap for wave visualization."""
    # Create a blue-white-red colormap for positive/negative waves
    colors = ['#000080', '#4169E1', '#87CEEB', '#FFFFFF', '#FFB6C1', '#FF6347', '#8B0000']
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('wave', colors, N=n_bins)
    return cmap


def add_parabola_boundaries(ax, grid_size, x_min=-300, x_max=300, y_min=-300, y_max=300):
    """Add parabola boundary lines to the plot."""
    
    # Create coordinate arrays
    x = np.linspace(x_min, x_max, grid_size)
    y = np.linspace(y_min, y_max, grid_size)
    
    # Major parabola: 20" (508mm) diameter, 100mm focus
    # y = -x²/(4*f) + f, where f is the focal length
    focal_length_major = 100.0  # mm
    y_major = -x**2 / (4 * focal_length_major) + focal_length_major
    
    # Only plot the part within our domain and diameter limit
    mask_major = (y_major >= y_min) & (y_major <= y_max) & (np.abs(x) <= 254)  # 508mm/2 = 254mm
    ax.plot(x[mask_major], y_major[mask_major], 'k-', linewidth=2, alpha=0.7, label='Major Parabola (20")')
    
    # Minor parabola: 10mm diameter, 50mm focus (CORRECTED!)
    focal_length_minor = 50.0  # mm (was 25.0, corrected for 50mm focus)
    y_minor = x**2 / (4 * focal_length_minor) - focal_length_minor
    
    # Only plot the part within our domain and diameter limit
    mask_minor = (y_minor >= y_min) & (y_minor <= y_max) & (np.abs(x) <= 5)  # 10mm/2 = 5mm
    ax.plot(x[mask_minor], y_minor[mask_minor], 'k--', linewidth=2, alpha=0.7, label='Minor Parabola (10mm)')
    
    # Mark focus points (corrected to coincident at origin)
    ax.plot(0, 0, 'go', markersize=10, markeredgecolor='black', markeredgewidth=1, label='Coincident Focus')
    # Show parabola vertices for reference
    ax.plot(0, focal_length_major, 'ro', markersize=6, label='Major Vertex')
    ax.plot(0, -focal_length_minor, 'bo', markersize=6, label='Minor Vertex')
    
    return ax


def plot_wave_snapshot(wave_data, time_step, step_num, grid_size=300, 
                      x_min=-300, x_max=300, y_min=-300, y_max=300,
                      save_path=None, show_boundaries=True, vmax=None):
    """
    Plot a single wave field snapshot.
    
    Args:
        wave_data: 2D numpy array of wave amplitudes
        time_step: Current time in seconds
        step_num: Step number for title
        grid_size: Grid resolution
        x_min, x_max, y_min, y_max: Domain bounds in mm
        save_path: Optional path to save the plot
        show_boundaries: Whether to show parabola boundaries
        vmax: Maximum value for color scale (auto if None)
    """
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create coordinate grids
    x = np.linspace(x_min, x_max, grid_size)
    y = np.linspace(y_min, y_max, grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Determine color scale
    if vmax is None:
        vmax = np.max(np.abs(wave_data))
        if vmax == 0:
            vmax = 1.0  # Prevent division by zero
    
    # Create wave visualization
    cmap = create_wave_colormap()
    im = ax.contourf(X, Y, wave_data, levels=50, cmap=cmap, vmin=-vmax, vmax=vmax)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Wave Amplitude', fontsize=12)
    
    # Add parabola boundaries if requested
    if show_boundaries:
        add_parabola_boundaries(ax, grid_size, x_min, x_max, y_min, y_max)
        ax.legend(loc='upper right', fontsize=10)
    
    # Formatting
    ax.set_xlabel('X Position (mm)', fontsize=12)
    ax.set_ylabel('Y Position (mm)', fontsize=12)
    ax.set_title(f'Wave Propagation - Step {step_num:03d}\nTime: {time_step:.6f} s', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Set axis limits
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig, ax


def create_wave_sequence_plots(grid_size=200, num_steps=50, record_interval=2,
                              frequency=1000.0, amplitude=1.0, output_dir='wave_snapshots',
                              use_core=True, show_boundaries=True):
    """
    Create a sequence of wave propagation plots.
    
    Args:
        grid_size: Simulation grid resolution
        num_steps: Number of simulation steps
        record_interval: Record every N steps
        frequency: Wave frequency in Hz
        amplitude: Wave amplitude
        output_dir: Directory to save plots
        use_core: Whether to use C++ core (if available)
        show_boundaries: Whether to show parabola boundaries
    """
    
    print("=== Wave Propagation Sequence Plotter ===\n")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    print(f"Output directory: {output_path.absolute()}")
    
    # Initialize simulation
    print(f"Initializing simulation (grid: {grid_size}x{grid_size})...")
    if use_core:
        sim = Simulation(grid_size=grid_size, use_core=True)
    else:
        sim = PythonSimulation(grid_size=grid_size)
    
    sim.set_frequency(frequency)
    sim.set_amplitude(amplitude)
    
    print(f"Using {'C++' if sim.use_core else 'Python'} simulation core")
    print(f"CFL timestep: {sim.cfl_timestep:.2e} seconds")
    print(f"Frequency: {frequency} Hz, Amplitude: {amplitude}")
    
    # Run simulation and collect data
    print(f"\nRunning {num_steps} simulation steps (recording every {record_interval} steps)...")
    start_time = time.time()
    
    results = sim.run_steps(num_steps, record_interval)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"Simulation completed in {execution_time:.2f} seconds")
    print(f"Steps per second: {num_steps/execution_time:.1f}")
    print(f"Recorded {len(results.wave_data)} frames")
    
    # Determine global color scale for consistent visualization
    all_max_amps = [np.max(np.abs(data)) for data in results.wave_data]
    global_vmax = max(all_max_amps) if all_max_amps else 1.0
    
    print(f"Global amplitude range: [0, {global_vmax:.6f}]")
    
    # Create plots for each frame
    print(f"\nCreating plots...")
    
    for i, (wave_data, time_step) in enumerate(zip(results.wave_data, results.time_steps)):
        
        # Calculate actual step number
        actual_step = i * record_interval
        
        # Create filename
        filename = f"wave_step_{actual_step:04d}_t_{time_step:.6f}.png"
        save_path = output_path / filename
        
        # Create plot
        fig, ax = plot_wave_snapshot(
            wave_data, time_step, actual_step, grid_size,
            save_path=save_path, show_boundaries=show_boundaries,
            vmax=global_vmax
        )
        
        plt.close(fig)  # Close to save memory
        
        # Progress indicator
        if (i + 1) % 5 == 0 or i == 0:
            print(f"  Created {i+1}/{len(results.wave_data)} plots")
    
    # Create summary plot showing amplitude evolution
    print("\nCreating amplitude evolution plot...")
    
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(results.time_steps, results.max_amplitudes, 'b-', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Maximum Amplitude')
    plt.title('Wave Amplitude Evolution')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    plt.plot(results.time_steps, results.energy_levels, 'r-', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Total Energy')
    plt.title('Wave Energy Evolution')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    summary_path = output_path / "amplitude_summary.png"
    plt.savefig(summary_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved summary: {summary_path}")
    
    # Print final statistics
    print(f"\n=== Final Statistics ===")
    print(f"Total frames created: {len(results.wave_data)}")
    print(f"Time range: {results.time_steps[0]:.6f} - {results.time_steps[-1]:.6f} seconds")
    print(f"Final max amplitude: {results.max_amplitudes[-1]:.6f}")
    print(f"Final energy: {results.energy_levels[-1]:.6f}")
    print(f"Files saved to: {output_path.absolute()}")
    
    return results, output_path


def create_comparison_plot(results, output_dir='wave_snapshots', frames_to_show=6):
    """Create a comparison plot showing multiple frames side by side."""
    
    output_path = Path(output_dir)
    
    # Select frames to show (evenly spaced)
    total_frames = len(results.wave_data)
    frame_indices = np.linspace(0, total_frames-1, frames_to_show, dtype=int)
    
    # Determine global color scale
    all_max_amps = [np.max(np.abs(data)) for data in results.wave_data]
    global_vmax = max(all_max_amps) if all_max_amps else 1.0
    
    # Create subplot grid
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    cmap = create_wave_colormap()
    
    for i, frame_idx in enumerate(frame_indices):
        ax = axes[i]
        
        wave_data = results.wave_data[frame_idx]
        time_step = results.time_steps[frame_idx]
        
        # Create coordinate grids
        grid_size = wave_data.shape[0]
        x = np.linspace(-300, 300, grid_size)
        y = np.linspace(-300, 300, grid_size)
        X, Y = np.meshgrid(x, y)
        
        # Plot wave field
        im = ax.contourf(X, Y, wave_data, levels=30, cmap=cmap, vmin=-global_vmax, vmax=global_vmax)
        
        # Add boundaries
        add_parabola_boundaries(ax, grid_size, show_legend=(i==0))
        if i == 0:
            ax.legend(loc='upper right', fontsize=8)
        
        ax.set_title(f'Step {frame_idx*2:03d}\nt={time_step:.6f}s', fontsize=10)
        ax.set_xlabel('X (mm)', fontsize=10)
        ax.set_ylabel('Y (mm)', fontsize=10)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
    
    # Add colorbar
    fig.subplots_adjust(right=0.92)
    cbar_ax = fig.add_axes([0.94, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label('Wave Amplitude', fontsize=12)
    
    plt.suptitle('Wave Propagation Sequence - Selected Frames', fontsize=16, y=0.95)
    
    comparison_path = output_path / "wave_comparison.png"
    plt.savefig(comparison_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved comparison plot: {comparison_path}")
    
    return comparison_path


def main():
    """Main function to run the wave propagation plotter."""
    
    # Configuration
    config = {
        'grid_size': 150,        # Smaller for faster computation
        'num_steps': 60,         # Number of simulation steps
        'record_interval': 3,    # Record every N steps for smoother animation
        'frequency': 1000.0,     # Hz
        'amplitude': 1.0,        # Wave amplitude
        'output_dir': 'wave_snapshots',
        'use_core': True,        # Try C++ core first
        'show_boundaries': True  # Show parabola boundaries
    }
    
    try:
        # Create wave sequence plots
        results, output_path = create_wave_sequence_plots(**config)
        
        # Create comparison plot
        create_comparison_plot(results, config['output_dir'], frames_to_show=6)
        
        print(f"\n✅ Success! All plots created in: {output_path.absolute()}")
        print(f"\nTo view the sequence:")
        print(f"  1. Open the '{config['output_dir']}' folder")
        print(f"  2. View individual snapshots: wave_step_*.png")
        print(f"  3. View comparison: wave_comparison.png")
        print(f"  4. View statistics: amplitude_summary.png")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
