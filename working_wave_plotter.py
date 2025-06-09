#!/usr/bin/env python3
"""
Working Wave Propagation Plotter
Creates matplotlib snapshots of wave propagation over time.
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

# Add the python package to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

def create_wave_plots():
    """Create wave propagation plots."""
    print("=== Wave Propagation Plotter ===")
    
    # Import simulation
    try:
        from dual_parabolic_wave.simulation import PythonSimulation
        print("✓ Simulation module imported")
    except ImportError as e:
        print(f"✗ Failed to import simulation: {e}")
        return False
    
    # Create output directory
    output_dir = Path('wave_snapshots')
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Output directory: {output_dir.absolute()}")
    
    # Configuration
    grid_size = 100
    num_steps = 30
    record_interval = 2
    frequency = 1000.0
    amplitude = 1.0
    
    print(f"✓ Configuration: {grid_size}x{grid_size} grid, {num_steps} steps")
    
    # Create simulation
    print("Creating simulation...")
    sim = PythonSimulation(grid_size=grid_size)
    sim.set_frequency(frequency)
    sim.set_amplitude(amplitude)
    
    print(f"✓ Simulation created (using {'C++' if sim.use_core else 'Python'} core)")
    print(f"✓ CFL timestep: {sim.cfl_timestep:.2e} seconds")
    
    # Run simulation
    print(f"Running {num_steps} simulation steps...")
    results = sim.run_steps(num_steps, record_interval)
    print(f"✓ Generated {len(results.wave_data)} frames")
    
    # Find global amplitude range for consistent coloring
    max_amps = [np.max(np.abs(data)) for data in results.wave_data]
    global_vmax = max(max_amps) if max_amps else 1.0
    print(f"✓ Global amplitude range: [0, {global_vmax:.6e}]")
    
    # Create coordinate grids
    x = np.linspace(-300, 300, grid_size)
    y = np.linspace(-300, 300, grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Create plots
    print("Creating wave plots...")
    plot_files = []
    
    for i, (wave_data, time_step) in enumerate(zip(results.wave_data, results.time_steps)):
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot wave field with contours
        if global_vmax > 0:
            levels = np.linspace(-global_vmax, global_vmax, 21)
            im = ax.contourf(X, Y, wave_data, levels=levels, cmap='RdBu_r', extend='both')
        else:
            im = ax.contourf(X, Y, wave_data, levels=20, cmap='RdBu_r')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Wave Amplitude', fontsize=12)
        
        # Add parabola outlines (CORRECTED SPECIFICATIONS)
        x_para = np.linspace(-200, 200, 100)
        
        # Major parabola: 20" (508mm) diameter, 100mm focus
        # Equation: y = -x²/(4*f) + f = -x²/400 + 100
        y_major = -x_para**2 / 400 + 100
        mask_major = (y_major >= -300) & (y_major <= 300) & (np.abs(x_para) <= 254)  # 508mm/2 = 254mm
        ax.plot(x_para[mask_major], y_major[mask_major], 'k-', linewidth=2, alpha=0.8, label='Major Parabola (20")')
        
        # Minor parabola: 10mm diameter, 50mm focus (CORRECTED from 100mm diameter!)
        # Equation: y = x²/(4*f) - f = x²/200 - 50
        y_minor = x_para**2 / 200 - 50
        mask_minor = (y_minor >= -300) & (y_minor <= 300) & (np.abs(x_para) <= 5)  # 10mm/2 = 5mm
        ax.plot(x_para[mask_minor], y_minor[mask_minor], 'k--', linewidth=2, alpha=0.8, label='Minor Parabola (10mm)')
        
        # Mark focus points (coincident at origin)
        ax.plot(0, 0, 'go', markersize=10, label='Coincident Focus', markeredgecolor='black', markeredgewidth=1)
        # Show where the parabola vertices are
        ax.plot(0, 100, 'ro', markersize=6, label='Major Vertex')
        ax.plot(0, -50, 'bo', markersize=6, label='Minor Vertex')
        
        # Formatting
        ax.set_xlabel('X Position (mm)', fontsize=12)
        ax.set_ylabel('Y Position (mm)', fontsize=12)
        ax.set_title(f'Wave Propagation - Frame {i:02d}\\nTime: {time_step:.6f} s, Max Amp: {max_amps[i]:.2e}', fontsize=14)
        ax.set_xlim(-300, 300)
        ax.set_ylim(-300, 300)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=10)
        
        # Save plot
        step_num = i * record_interval
        filename = output_dir / f"wave_frame_{i:03d}_step_{step_num:03d}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        plot_files.append(filename)
        print(f"  Saved frame {i+1}/{len(results.wave_data)}: {filename.name}")
    
    # Create summary plots
    print("Creating summary plots...")
    
    # Amplitude evolution
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(results.time_steps, max_amps, 'b-', linewidth=2, marker='o', markersize=4)
    plt.xlabel('Time (s)')
    plt.ylabel('Maximum Amplitude')
    plt.title('Wave Amplitude Evolution')
    plt.grid(True, alpha=0.3)
    
    # Energy evolution
    plt.subplot(1, 2, 2)
    plt.plot(results.time_steps, results.energy_levels, 'r-', linewidth=2, marker='s', markersize=4)
    plt.xlabel('Time (s)')
    plt.ylabel('Total Energy')
    plt.title('Wave Energy Evolution')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    summary_file = output_dir / "wave_evolution_summary.png"
    plt.savefig(summary_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Summary saved: {summary_file.name}")
    
    # Create comparison grid (first and last few frames)
    print("Creating comparison grid...")
    
    frames_to_show = min(6, len(results.wave_data))
    if frames_to_show >= 4:
        frame_indices = [0, len(results.wave_data)//3, 2*len(results.wave_data)//3, len(results.wave_data)-1]
    else:
        frame_indices = list(range(frames_to_show))
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for idx, frame_i in enumerate(frame_indices[:4]):
        ax = axes[idx]
        wave_data = results.wave_data[frame_i]
        time_step = results.time_steps[frame_i]
        
        if global_vmax > 0:
            levels = np.linspace(-global_vmax, global_vmax, 15)
            im = ax.contourf(X, Y, wave_data, levels=levels, cmap='RdBu_r', extend='both')
        else:
            im = ax.contourf(X, Y, wave_data, levels=15, cmap='RdBu_r')
        
        ax.set_title(f'Frame {frame_i:02d} (t={time_step:.6f}s)', fontsize=12)
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
    
    # Add global colorbar
    fig.subplots_adjust(right=0.92)
    cbar_ax = fig.add_axes([0.94, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label('Wave Amplitude', fontsize=12)
    
    plt.suptitle('Wave Propagation - Key Frames Comparison', fontsize=16, y=0.95)
    
    comparison_file = output_dir / "wave_comparison_grid.png"
    plt.savefig(comparison_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Comparison grid saved: {comparison_file.name}")
    
    # Final summary
    print(f"\\n=== Results Summary ===")
    print(f"Total frames created: {len(plot_files)}")
    print(f"Time range: {results.time_steps[0]:.6f} - {results.time_steps[-1]:.6f} seconds")
    print(f"Amplitude range: {min(max_amps):.2e} - {max(max_amps):.2e}")
    print(f"Final max amplitude: {max_amps[-1]:.2e}")
    print(f"All files saved to: {output_dir.absolute()}")
    
    print(f"\\n✅ Wave propagation plots created successfully!")
    print(f"\\n📁 Files created:")
    print(f"  - {len(plot_files)} individual wave frames")
    print(f"  - 1 evolution summary plot")
    print(f"  - 1 comparison grid plot")
    
    return True

def main():
    """Main function."""
    try:
        success = create_wave_plots()
        return 0 if success else 1
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
