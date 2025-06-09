#!/usr/bin/env python3
"""
Test script to debug simulation issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

try:
    from dual_parabolic_wave.simulation import Simulation
    import numpy as np
    
    print("=== Testing Simulation ===")
    
    # Test simulation creation
    print("Creating simulation...")
    sim = Simulation(grid_size=100)
    print(f"✓ Core available: {sim.use_core}")
    print(f"✓ Grid size: {sim.grid_size}")
    print(f"✓ CFL timestep: {sim.cfl_timestep:.6e}")
    
    # Test running a few steps
    print("\nRunning 5 simulation steps...")
    try:
        results = sim.run_steps(5, record_interval=1)
        print(f"✓ Results generated: {len(results.wave_data)} frames")
        print(f"✓ Time steps: {results.time_steps}")
        print(f"✓ Max amplitudes: {results.max_amplitudes}")
        
        if results.wave_data:
            final_data = results.get_final_wave_data()
            print(f"✓ Final wave data shape: {final_data.shape}")
            print(f"✓ Final wave data range: [{np.min(final_data):.6f}, {np.max(final_data):.6f}]")
            
            # Check if we have any significant wave activity
            max_abs = np.max(np.abs(final_data))
            if max_abs > 1e-10:
                print(f"✓ Wave activity detected (max amplitude: {max_abs:.6e})")
            else:
                print(f"⚠️  Very low wave activity (max amplitude: {max_abs:.6e})")
        else:
            print("❌ No wave data generated")
            
    except Exception as e:
        print(f"❌ Error running simulation: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with longer simulation
    print("\nRunning longer simulation (20 steps)...")
    try:
        sim.reset()
        results = sim.run_steps(20, record_interval=2)
        print(f"✓ Results generated: {len(results.wave_data)} frames")
        
        if results.wave_data:
            # Check progression of max amplitudes
            print("Max amplitude progression:")
            for i, (t, amp) in enumerate(zip(results.time_steps, results.max_amplitudes)):
                print(f"  Frame {i}: t={t:.6f}s, max_amp={amp:.6e}")
                
        else:
            print("❌ No wave data in longer simulation")
            
    except Exception as e:
        print(f"❌ Error in longer simulation: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
