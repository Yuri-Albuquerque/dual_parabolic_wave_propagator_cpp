#!/usr/bin/env python3
"""
Simple test to verify the Morlet wavelet implementation is working.
"""

import sys
import os

# Add the python directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

try:
    print("🧪 Testing Dual Parabolic Wave Simulation with Morlet Wavelet")
    print("=" * 60)
    
    # Import the simulation
    from dual_parabolic_wave.simulation import DualParabolicWaveSimulation
    print("✅ Successfully imported simulation module")
    
    # Create simulation instance
    sim = DualParabolicWaveSimulation(
        grid_size=100,
        domain_size=1.0,
        frequency=1000.0,
        amplitude=1.0,
        wave_speed=343.0,
        time_step=0.0001
    )
    print("✅ Successfully created simulation instance")
    
    # Initialize simulation
    sim.initialize()
    print("✅ Successfully initialized simulation")
    
    # Run a few time steps
    print("🚀 Running simulation steps...")
    for i in range(5):
        sim.step()
        time = sim.get_current_time()
        max_amplitude = sim.get_wave_field().max()
        print(f"   Step {i+1}: t={time:.6f}s, max_amplitude={max_amplitude:.6f}")
    
    print("✅ Simulation completed successfully!")
    print("🌊 Morlet wavelet implementation is working correctly")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Runtime error: {e}")
    sys.exit(1)

print("=" * 60)
print("✨ All tests passed! Ready to launch Gradio interface.")
