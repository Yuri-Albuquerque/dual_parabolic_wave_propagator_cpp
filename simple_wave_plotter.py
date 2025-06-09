#!/usr/bin/env python3
"""
Simple Wave Propagation Plotter Test
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

def test_basic_plot():
    """Test basic matplotlib functionality."""
    print("Testing basic matplotlib...")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create some test data
    x = np.linspace(-10, 10, 100)
    y = np.sin(x)
    
    ax.plot(x, y, 'b-', linewidth=2)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Test Plot')
    ax.grid(True)
    
    # Save test plot
    output_dir = Path('wave_snapshots')
    output_dir.mkdir(exist_ok=True)
    
    test_path = output_dir / 'test_plot.png'
    plt.savefig(test_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Test plot saved: {test_path}")
    return test_path

def test_simulation():
    """Test simulation import and basic functionality."""
    print("Testing simulation...")
    
    try:
        from dual_parabolic_wave.simulation import PythonSimulation
        
        print("Creating simulation...")
        sim = PythonSimulation(grid_size=50)
        print(f"Grid size: {sim.grid_size}")
        print(f"CFL timestep: {sim.cfl_timestep:.6e}")
        
        print("Running simulation steps...")
        results = sim.run_steps(5, record_interval=1)
        print(f"Generated {len(results.wave_data)} frames")
        
        if results.wave_data:
            data = results.get_final_wave_data()
            max_amp = np.max(np.abs(data))
            print(f"Max amplitude: {max_amp:.6e}")
            return True, results
        else:
            print("No data generated")
            return False, None
            
    except Exception as e:
        print(f"Error in simulation test: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def create_simple_wave_plot(wave_data, time_step, filename):
    """Create a simple wave plot."""
    print(f"Creating plot for t={time_step:.6f}s...")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create coordinate grids
    grid_size = wave_data.shape[0]
    x = np.linspace(-300, 300, grid_size)
    y = np.linspace(-300, 300, grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Plot wave field
    vmax = np.max(np.abs(wave_data))
    if vmax == 0:
        vmax = 1.0
    
    im = ax.contourf(X, Y, wave_data, levels=20, cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Wave Amplitude')
    
    # Formatting
    ax.set_xlabel('X Position (mm)')
    ax.set_ylabel('Y Position (mm)')
    ax.set_title(f'Wave Field at t={time_step:.6f}s\nMax Amplitude: {vmax:.6e}')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {filename}")

def main():
    """Main test function."""
    print("=== Simple Wave Propagation Test ===\n")
    
    # Test 1: Basic matplotlib
    try:
        test_path = test_basic_plot()
        print("✓ Matplotlib test passed\n")
    except Exception as e:
        print(f"✗ Matplotlib test failed: {e}\n")
        return 1
    
    # Test 2: Simulation
    try:
        success, results = test_simulation()
        if not success:
            print("✗ Simulation test failed\n")
            return 1
        print("✓ Simulation test passed\n")
    except Exception as e:
        print(f"✗ Simulation test failed: {e}\n")
        return 1
    
    # Test 3: Create wave plots
    try:
        print("Creating wave plots...")
        output_dir = Path('wave_snapshots')
        output_dir.mkdir(exist_ok=True)
        
        for i, (wave_data, time_step) in enumerate(zip(results.wave_data, results.time_steps)):
            filename = output_dir / f"simple_wave_{i:03d}.png"
            create_simple_wave_plot(wave_data, time_step, filename)
        
        print(f"✓ Created {len(results.wave_data)} wave plots")
        print(f"✓ All files saved to: {output_dir.absolute()}")
        
    except Exception as e:
        print(f"✗ Wave plot creation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n=== Test Complete ===")
    print("All tests passed successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
