#!/usr/bin/env python3
"""
Test script for the dual parabolic wave simulation with pulse source.
This tests the Python implementation to ensure the pulse source changes work correctly.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add the python package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

try:
    from dual_parabolic_wave.simulation import DualParabolicWaveSimulation
    print("✅ Successfully imported DualParabolicWaveSimulation")
except ImportError as e:
    print(f"❌ Failed to import simulation module: {e}")
    sys.exit(1)

def test_pulse_simulation():
    """Test the simulation with pulse source."""
    print("\n🧪 Testing Dual Parabolic Wave Simulation with Pulse Source")
    print("=" * 60)
    
    # Create simulation instance
    try:
        sim = DualParabolicWaveSimulation()
        print("✅ Successfully created simulation instance")
    except Exception as e:
        print(f"❌ Failed to create simulation: {e}")
        return False
    
    # Test parameters
    frequency = 1000.0  # 1 kHz
    amplitude = 1.0
    
    # Set wave parameters
    try:
        sim.set_frequency(frequency)
        sim.set_amplitude(amplitude)
        print(f"✅ Set frequency to {frequency} Hz and amplitude to {amplitude}")
    except Exception as e:
        print(f"❌ Failed to set parameters: {e}")
        return False
    
    # Run simulation for a few time steps to test pulse behavior
    print("\n📊 Running simulation to test pulse source...")
    
    time_steps = []
    max_amplitudes = []
    source_values = []
    
    # Test the first few time steps when pulse should be active
    dt = 0.0001  # 0.1 ms time step
    pulse_width = 1.0 / frequency  # One period = 1 ms for 1 kHz
    pulse_duration = 2.0 * pulse_width  # 2 ms total pulse duration
    
    print(f"📏 Pulse width: {pulse_width*1000:.2f} ms")
    print(f"📏 Pulse duration: {pulse_duration*1000:.2f} ms")
    print(f"⏱️  Time step: {dt*1000:.2f} ms")
    
    for step in range(100):  # Test first 100 steps (10 ms)
        current_time = step * dt
        
        try:
            # Get state before update
            state_before = sim.get_wave_field()
            max_before = np.max(np.abs(state_before)) if state_before.size > 0 else 0
            
            # Update simulation
            sim.step(dt)
            
            # Get state after update
            state_after = sim.get_wave_field()
            max_after = np.max(np.abs(state_after)) if state_after.size > 0 else 0
            
            # Record data
            time_steps.append(current_time)
            max_amplitudes.append(max_after)
            
            # Check if we're in pulse duration and calculate expected source
            if current_time <= pulse_duration:
                gaussian_width = pulse_width / 3.0
                envelope = np.exp(-(current_time - pulse_width)**2 / (2 * gaussian_width**2))
                expected_source = amplitude * 10.0 * envelope * np.sin(2 * np.pi * frequency * current_time)
                source_values.append(abs(expected_source))
            else:
                source_values.append(0.0)
            
            # Print progress for key time points
            if step % 20 == 0 or current_time <= pulse_duration:
                pulse_active = "🔴 ACTIVE" if current_time <= pulse_duration else "⚫ INACTIVE"
                print(f"  Step {step:3d}: t={current_time*1000:5.2f}ms, "
                      f"max_amp={max_after:.6f}, pulse={pulse_active}")
                
        except Exception as e:
            print(f"❌ Error at step {step}: {e}")
            return False
    
    # Analyze results
    print(f"\n📈 Analysis Results:")
    print(f"   Total time steps: {len(time_steps)}")
    print(f"   Maximum amplitude reached: {max(max_amplitudes):.6f}")
    print(f"   Final amplitude: {max_amplitudes[-1]:.6f}")
    
    # Check pulse behavior
    pulse_steps = [i for i, t in enumerate(time_steps) if t <= pulse_duration]
    post_pulse_steps = [i for i, t in enumerate(time_steps) if t > pulse_duration]
    
    if pulse_steps:
        max_during_pulse = max([max_amplitudes[i] for i in pulse_steps])
        print(f"   Max amplitude during pulse: {max_during_pulse:.6f}")
    
    if post_pulse_steps:
        max_after_pulse = max([max_amplitudes[i] for i in post_pulse_steps])
        print(f"   Max amplitude after pulse: {max_after_pulse:.6f}")
    
    # Success criteria
    success = True
    if max(max_amplitudes) < 1e-10:
        print("❌ No significant wave activity detected")
        success = False
    elif len(pulse_steps) > 0 and max([max_amplitudes[i] for i in pulse_steps]) < 1e-6:
        print("❌ No wave activity during pulse period")
        success = False
    else:
        print("✅ Wave propagation detected successfully")
    
    # Create a simple plot if matplotlib is available
    try:
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.plot([t*1000 for t in time_steps], max_amplitudes, 'b-', linewidth=2)
        plt.axvline(pulse_duration*1000, color='r', linestyle='--', alpha=0.7, label='Pulse End')
        plt.xlabel('Time (ms)')
        plt.ylabel('Max Wave Amplitude')
        plt.title('Wave Amplitude vs Time')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.subplot(2, 2, 2)
        plt.plot([t*1000 for t in time_steps], source_values, 'r-', linewidth=2)
        plt.xlabel('Time (ms)')
        plt.ylabel('Source Amplitude')
        plt.title('Pulse Source vs Time')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(2, 2, 3)
        # Show final wave field state
        final_state = sim.get_wave_field()
        if final_state.size > 0:
            plt.imshow(final_state, cmap='RdBu_r', interpolation='bilinear')
            plt.colorbar(label='Wave Amplitude')
            plt.title('Final Wave Field State')
        
        plt.subplot(2, 2, 4)
        # Show wave field at peak pulse time
        sim_peak = DualParabolicWaveSimulation()
        sim_peak.set_frequency(frequency)
        sim_peak.set_amplitude(amplitude)
        # Step to peak time
        peak_steps = int(pulse_width / dt)
        for _ in range(peak_steps):
            sim_peak.step(dt)
        peak_state = sim_peak.get_wave_field()
        if peak_state.size > 0:
            plt.imshow(peak_state, cmap='RdBu_r', interpolation='bilinear')
            plt.colorbar(label='Wave Amplitude')
            plt.title(f'Wave Field at Peak Pulse ({pulse_width*1000:.1f}ms)')
        
        plt.tight_layout()
        plt.savefig('python_pulse_test_results.png', dpi=150, bbox_inches='tight')
        print(f"📊 Results plot saved as 'python_pulse_test_results.png'")
        plt.close()
        
    except Exception as e:
        print(f"⚠️  Could not create plot: {e}")
    
    return success

def main():
    """Main test function."""
    print("🌊 Dual Parabolic Wave Simulation - Python Pulse Test")
    print("=" * 60)
    
    success = test_pulse_simulation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests PASSED! Python pulse implementation is working correctly.")
    else:
        print("❌ Tests FAILED! Check the implementation.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
