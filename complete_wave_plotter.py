#!/usr/bin/env python3
"""
Complete Wave Propagation Plotter
A comprehensive script to run wave simulation and create all sequence plots with matplotlib.
This script provides immediate feedback and creates beautiful wave propagation visualizations.
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path
import time

# Add python package to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

def print_header():
    """Print a nice header."""
    print("=" * 60)
    print("🌊 COMPLETE WAVE PROPAGATION PLOTTER 🌊")
    print("=" * 60)
    print("Creating comprehensive matplotlib visualizations")
    print("of wave propagation in dual parabolic cavity...")
    print()

def run_wave_simulation():
    """Run the wave simulation and return results."""
    print("📡 Setting up wave simulation...")
    
    try:
        from dual_parabolic_wave.simulation import PythonSimulation
        print("✅ Simulation module loaded successfully")
    except ImportError as e:
        print(f"❌ Failed to import simulation: {e}")
        return None
        
    # Simulation parameters (optimized for quick results)
    grid_size = 80
    num_steps = 25
    record_interval = 1
    frequency = 1000.0
    amplitude = 1.0
    
    print(f"⚙️  Configuration:")
    print(f"   • Grid size: {grid_size}x{grid_size}")
    print(f"   • Time steps: {num_steps}")
    print(f"   • Recording interval: {record_interval}")
    print(f"   • Frequency: {frequency} Hz")
    print(f"   • Amplitude: {amplitude}")
    
    # Create and configure simulation
    sim = PythonSimulation(grid_size=grid_size)
    sim.set_frequency(frequency)
    sim.set_amplitude(amplitude)
    
    print(f"✅ Simulation created (using {'C++' if sim.use_core else 'Python'} backend)")
    print(f"⏱️  CFL timestep: {sim.cfl_timestep:.2e} seconds")
    
    # Run simulation
    print("\n🚀 Running simulation...")
    start_time = time.time()
    
    results = sim.run_steps(num_steps, record_interval)
    
    end_time = time.time()
    print(f"✅ Simulation completed in {end_time - start_time:.2f} seconds")
    print(f"📊 Generated {len(results.wave_data)} frames")
    
    return results, grid_size

def create_wave_plots(results, grid_size):
    """Create all wave propagation plots."""
    print("\n🎨 Creating wave plots...")
    
    # Create output directory
    output_dir = Path('wave_sequence_plots')
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Output directory: {output_dir.absolute()}")
    
    # Calculate global statistics
    max_amps = [np.max(np.abs(data)) for data in results.wave_data]
    global_vmax = max(max_amps) if max_amps else 1.0
    
    print(f"📈 Global amplitude range: [0, {global_vmax:.6e}]")
    
    # Create coordinate grids
    x = np.linspace(-300, 300, grid_size)
    y = np.linspace(-300, 300, grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Create individual frame plots
    print("🖼️  Creating individual frame plots...")
    frame_files = []
    
    for i, (wave_data, time_step) in enumerate(zip(results.wave_data, results.time_steps)):
        print(f"   📸 Frame {i+1}/{len(results.wave_data)}: t={time_step:.6f}s", end="")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot wave field
        if global_vmax > 0:
            levels = np.linspace(-global_vmax, global_vmax, 21)
            im = ax.contourf(X, Y, wave_data, levels=levels, cmap='RdBu_r', extend='both')
        else:
            im = ax.contourf(X, Y, wave_data, levels=21, cmap='RdBu_r')
            
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Wave Amplitude', fontsize=12)
        
        # Add parabola boundaries with CORRECTED specifications
        x_para = np.linspace(-250, 250, 100)
        
        # Major parabola: 20" (508mm) diameter, 100mm focus
        # Equation: y = -x²/(4*f) + f = -x²/400 + 100
        y_major = -x_para**2 / 400 + 100
        mask_major = (y_major >= -300) & (y_major <= 300) & (np.abs(x_para) <= 254)  # 508mm/2 = 254mm
        ax.plot(x_para[mask_major], y_major[mask_major], 'k-', linewidth=3, alpha=0.9, label='Major Parabola (20")')
        
        # Minor parabola: 10mm diameter, 50mm focus (CORRECTED from 100mm!)
        # Equation: y = x²/(4*f) - f = x²/200 - 50
        y_minor = x_para**2 / 200 - 50
        mask_minor = (y_minor >= -300) & (y_minor <= 300) & (np.abs(x_para) <= 5)  # 10mm/2 = 5mm
        ax.plot(x_para[mask_minor], y_minor[mask_minor], 'k--', linewidth=3, alpha=0.9, label='Minor Parabola (10mm)')
        
        # Mark focus points (corrected to coincident at origin)
        ax.plot(0, 0, 'go', markersize=10, markeredgecolor='black', markeredgewidth=2, label='Coincident Focus')
        # Show parabola vertices for reference
        ax.plot(0, 100, 'ro', markersize=6, label='Major Vertex')
        ax.plot(0, -50, 'bo', markersize=6, label='Minor Vertex')
        
        # Calculate current amplitude
        current_max = np.max(np.abs(wave_data))
        
        # Formatting
        ax.set_xlabel('X Position (mm)', fontsize=12)
        ax.set_ylabel('Y Position (mm)', fontsize=12)
        ax.set_title(f'Wave Propagation - Frame {i:03d}\\n' + 
                    f'Time: {time_step:.6f} s | Max Amplitude: {current_max:.2e}', fontsize=14)
        ax.set_xlim(-300, 300)
        ax.set_ylim(-300, 300)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
        
        # Save frame
        filename = output_dir / f"wave_frame_{i:03d}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        frame_files.append(filename)
        print(f" ✅ Saved")
        
    print(f"✅ Created {len(frame_files)} individual frame plots")
    
    return frame_files, max_amps

def create_summary_plots(results, max_amps, output_dir):
    """Create summary and analysis plots."""
    print("\n📊 Creating summary plots...")
    
    # Evolution summary
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Amplitude evolution
    ax = axes[0, 0]
    ax.plot(results.time_steps, max_amps, 'b-', linewidth=2, marker='o', markersize=4)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Maximum Amplitude')
    ax.set_title('Wave Amplitude Evolution')
    ax.grid(True, alpha=0.3)
    
    # Energy evolution
    ax = axes[0, 1]
    ax.plot(results.time_steps, results.energy_levels, 'r-', linewidth=2, marker='s', markersize=4)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Total Energy')
    ax.set_title('Wave Energy Evolution')
    ax.grid(True, alpha=0.3)
    
    # Amplitude histogram
    ax = axes[1, 0]
    ax.hist(max_amps, bins=12, alpha=0.7, color='green', edgecolor='black')
    ax.axvline(np.mean(max_amps), color='red', linestyle='--', linewidth=2, 
              label=f'Mean: {np.mean(max_amps):.2e}')
    ax.set_xlabel('Maximum Amplitude')
    ax.set_ylabel('Frequency')
    ax.set_title('Amplitude Distribution')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Amplitude vs Energy scatter
    ax = axes[1, 1]
    scatter = ax.scatter(max_amps, results.energy_levels, c=results.time_steps, 
                        cmap='viridis', s=50, alpha=0.7)
    ax.set_xlabel('Maximum Amplitude')
    ax.set_ylabel('Total Energy')
    ax.set_title('Amplitude vs Energy')
    plt.colorbar(scatter, ax=ax, label='Time (s)')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    summary_file = output_dir / "wave_analysis_summary.png"
    plt.savefig(summary_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Summary plots saved: {summary_file.name}")
    return summary_file

def create_comparison_grid(results, max_amps, output_dir):
    """Create a comparison grid of key frames."""
    print("🔍 Creating comparison grid...")
    
    # Select key frames
    n_frames = len(results.wave_data)
    if n_frames >= 9:
        indices = [0, n_frames//8, n_frames//4, 3*n_frames//8, n_frames//2, 
                  5*n_frames//8, 3*n_frames//4, 7*n_frames//8, n_frames-1]
        grid_shape = (3, 3)
    else:
        indices = [0, n_frames//3, 2*n_frames//3, n_frames-1]
        grid_shape = (2, 2)
        
    # Create coordinate grids
    grid_size = int(np.sqrt(results.wave_data[0].size))
    x = np.linspace(-300, 300, grid_size)
    y = np.linspace(-300, 300, grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Create figure
    fig, axes = plt.subplots(*grid_shape, figsize=(15, 12))
    axes = axes.flatten()
    
    global_vmax = max(max_amps)
    
    for i, idx in enumerate(indices[:len(axes)]):
        ax = axes[i]
        wave_data = results.wave_data[idx]
        time_step = results.time_steps[idx]
        
        # Plot wave
        levels = np.linspace(-global_vmax, global_vmax, 15)
        im = ax.contourf(X, Y, wave_data, levels=levels, cmap='RdBu_r', extend='both')
        
        # Add parabola outlines (simplified)
        x_para = np.linspace(-200, 200, 50)
        y_major = -x_para**2 / 400 + 100
        y_minor = x_para**2 / 100 - 25
        
        mask_major = (y_major >= -300) & (y_major <= 300)
        mask_minor = (y_minor >= -300) & (y_minor <= 300)
        
        ax.plot(x_para[mask_major], y_major[mask_major], 'k-', linewidth=2, alpha=0.8)
        ax.plot(x_para[mask_minor], y_minor[mask_minor], 'k--', linewidth=2, alpha=0.8)
        
        ax.set_title(f'Frame {idx:02d}\\nt={time_step:.4f}s\\nMax={max_amps[idx]:.2e}', fontsize=11)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
    # Hide unused subplots
    for i in range(len(indices), len(axes)):
        axes[i].set_visible(False)
        
    # Add colorbar
    fig.subplots_adjust(right=0.92)
    cbar_ax = fig.add_axes([0.94, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label('Wave Amplitude', fontsize=12)
    
    plt.suptitle('Wave Propagation - Key Frames Comparison', fontsize=16, y=0.95)
    
    comparison_file = output_dir / "wave_key_frames_comparison.png"
    plt.savefig(comparison_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Comparison grid saved: {comparison_file.name}")
    return comparison_file

def print_final_summary(frame_files, summary_file, comparison_file, results, max_amps):
    """Print final summary."""
    print("\n" + "="*60)
    print("🎉 WAVE PROPAGATION ANALYSIS COMPLETE! 🎉")
    print("="*60)
    
    print(f"📊 RESULTS:")
    print(f"   • Total frames created: {len(frame_files)}")
    print(f"   • Time range: {results.time_steps[0]:.6f} - {results.time_steps[-1]:.6f} seconds")
    print(f"   • Maximum amplitude: {max(max_amps):.6e}")
    print(f"   • Final amplitude: {max_amps[-1]:.6e}")
    
    print(f"\\n📁 FILES CREATED:")
    print(f"   • {len(frame_files)} individual wave frame plots")
    print(f"   • 1 comprehensive analysis summary")
    print(f"   • 1 key frames comparison grid")
    print(f"   • Total files: {len(frame_files) + 2}")
    
    print(f"\\n🔍 TO VIEW RESULTS:")
    print(f"   • Individual frames: wave_sequence_plots/wave_frame_*.png")
    print(f"   • Analysis summary: {summary_file.name}")
    print(f"   • Key comparison: {comparison_file.name}")
    
    print("\\n✨ Wave propagation visualization completed successfully! ✨")

def main():
    """Main function."""
    print_header()
    
    try:
        # Run simulation
        result = run_wave_simulation()
        if not result:
            print("❌ Simulation failed")
            return 1
            
        results, grid_size = result
        
        # Create plots
        output_dir = Path('wave_sequence_plots')
        frame_files, max_amps = create_wave_plots(results, grid_size)
        summary_file = create_summary_plots(results, max_amps, output_dir)
        comparison_file = create_comparison_grid(results, max_amps, output_dir)
        
        # Print summary
        print_final_summary(frame_files, summary_file, comparison_file, results, max_amps)
        
        return 0
        
    except Exception as e:
        print(f"\\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
