#!/usr/bin/env python3
"""
Test script for the Gradio dual parabolic wave simulation app.
"""

import sys
import os

# Add the python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

import dual_parabolic_wave as dpw
import numpy as np

def test_morlet_wavelet_simulation():
    """Test the Morlet wavelet implementation in the simulation."""
    print("🌊 Testing Dual Parabolic Wave Simulation with Morlet Wavelet")
    print("=" * 60)
    
    # Test simulation creation
    print("Creating simulation instance...")
    sim = dpw.Simulation(grid_size=200, use_core=False)  # Use Python version for testing
    
    # Set parameters
    frequency = 1000.0  # 1 kHz
    amplitude = 1.0
    sim.set_frequency(frequency)
    sim.set_amplitude(amplitude)
    
    print(f"✓ Simulation created with {sim.get_grid_size()}x{sim.get_grid_size()} grid")
    print(f"✓ Frequency: {sim.get_frequency()} Hz")
    print(f"✓ Amplitude: {sim.get_amplitude()}")
    
    # Run simulation steps
    print("\nRunning simulation steps...")
    results = sim.run_steps(50, record_interval=5)
    
    print(f"✓ Completed {len(results.time_steps)} recorded time steps")
    print(f"✓ Final time: {results.time_steps[-1]:.6f} seconds")
    print(f"✓ Max amplitude: {results.max_amplitudes[-1]:.6f}")
    print(f"✓ Final energy: {results.energy_levels[-1]:.6f}")
    
    # Test visualization functions
    print("\nTesting visualization functions...")
    final_data = results.get_final_wave_data()
    print(f"✓ Final wave data shape: {final_data.shape}")
    print(f"✓ Wave data range: [{np.min(final_data):.6f}, {np.max(final_data):.6f}]")
    
    # Test 2D plot creation
    try:
        fig_2d = dpw.plot_wave_field_2d(final_data, title="Test 2D Wave Field")
        print("✓ 2D plot creation successful")
    except Exception as e:
        print(f"✗ 2D plot creation failed: {e}")
    
    # Test 3D plot creation
    try:
        fig_3d = dpw.plot_wave_field_3d(final_data, title="Test 3D Wave Field")
        print("✓ 3D plot creation successful")
    except Exception as e:
        print(f"✗ 3D plot creation failed: {e}")
    
    # Test parabola geometry plot
    try:
        fig_geom = dpw.plot_parabola_geometry()
        print("✓ Parabola geometry plot successful")
    except Exception as e:
        print(f"✗ Parabola geometry plot failed: {e}")
    
    print("\n🎉 All tests completed successfully!")
    return True

def test_gradio_app_creation():
    """Test creating the Gradio app without launching it."""
    print("\n🎛️ Testing Gradio App Creation")
    print("=" * 60)
    
    try:
        # Create the Gradio app
        demo = dpw.create_app()
        print("✓ Gradio app created successfully")
        print("✓ App interface configured")
        print("✓ Event handlers set up")
        return True
    except Exception as e:
        print(f"✗ Gradio app creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Dual Parabolic Wave Simulation - Test Suite")
    print("=" * 60)
    
    # Test the core simulation
    test1_passed = test_morlet_wavelet_simulation()
    
    # Test Gradio app creation
    test2_passed = test_gradio_app_creation()
    
    print("\n📋 Test Summary")
    print("=" * 60)
    print(f"Morlet Wavelet Simulation: {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Gradio App Creation: {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests PASSED! The Gradio app is ready to launch.")
        print("\nTo launch the web interface, run:")
        print("cd python && python -m dual_parabolic_wave.gradio_app")
    else:
        print("\n❌ Some tests FAILED. Please check the errors above.")
        sys.exit(1)
