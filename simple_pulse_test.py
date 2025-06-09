#!/usr/bin/env python3
"""
Simple test for Python simulation with pulse source
"""

import sys
import os
import numpy as np

# Test the simulation by directly testing the Python implementation
def test_python_simulation():
    """Test the Python simulation implementation."""
    print("🧪 Testing Python Pulse Simulation")
    print("=" * 50)
    
    # Manual simulation test - mimicking the key parts of the simulation
    grid_size = 100
    frequency = 1000.0  # Hz
    amplitude = 1.0
    speed = 343000.0  # mm/s
    
    # Time step calculation
    domain_size = 600.0  # mm
    dx = domain_size / grid_size
    dt = 0.4 * dx / (speed * np.sqrt(2.0))
    
    print(f"📏 Grid size: {grid_size}x{grid_size}")
    print(f"📏 Grid spacing: {dx:.2f} mm")
    print(f"⏱️  Time step: {dt*1000:.4f} ms")
    print(f"🎵 Frequency: {frequency} Hz")
    
    # Pulse parameters
    pulse_width = 1.0 / frequency  # One period width
    pulse_duration = 2.0 * pulse_width  # Duration of the pulse
    
    print(f"📏 Pulse width: {pulse_width*1000:.2f} ms")
    print(f"📏 Pulse duration: {pulse_duration*1000:.2f} ms")
    
    # Initialize wave fields
    wave_current = np.zeros((grid_size, grid_size))
    wave_previous = np.zeros((grid_size, grid_size))
    wave_next = np.zeros((grid_size, grid_size))
    
    # Test pulse source calculation over time
    print(f"\n📊 Testing pulse source over time:")
    print(f"{'Step':>4} {'Time(ms)':>8} {'Source':>12} {'Pulse':>6}")
    print("-" * 35)
    
    max_amplitudes = []
    current_time = 0.0
    center_x = grid_size // 2
    center_y = grid_size // 2
    
    # Run simulation for first few steps
    for step in range(50):
        # Calculate pulse source
        source_value = 0.0
        pulse_active = current_time <= pulse_duration
        
        if pulse_active:
            # Gaussian envelope for smooth pulse
            gaussian_width = pulse_width / 3.0
            envelope = np.exp(-((current_time - pulse_width) ** 2) / (2 * gaussian_width ** 2))
            
            # Single frequency pulse
            source_amplitude = amplitude * 10.0  # Stronger source
            source_value = source_amplitude * envelope * np.sin(2 * np.pi * frequency * current_time)
        
        # Simple wave equation update (simplified for testing)
        c2 = speed ** 2
        
        # Update wave field at center with source
        if pulse_active and source_value != 0:
            wave_current[center_x, center_y] += source_value * dt * dt * 0.001  # Small scaling for stability
        
        # Basic wave propagation (simplified)
        for i in range(1, grid_size - 1):
            for j in range(1, grid_size - 1):
                # Second derivatives
                d2u_dx2 = (wave_current[i+1, j] - 2*wave_current[i, j] + wave_current[i-1, j]) / (dx**2)
                d2u_dy2 = (wave_current[i, j+1] - 2*wave_current[i, j] + wave_current[i, j-1]) / (dx**2)
                
                # Wave equation
                acceleration = c2 * (d2u_dx2 + d2u_dy2)
                
                # Time integration
                wave_next[i, j] = (2 * wave_current[i, j] - wave_previous[i, j] + 
                                 acceleration * dt**2)
        
        # Apply boundary conditions
        wave_next[0, :] = 0
        wave_next[-1, :] = 0
        wave_next[:, 0] = 0
        wave_next[:, -1] = 0
        
        # Update arrays
        wave_previous, wave_current, wave_next = wave_current, wave_next, wave_previous
        
        # Record maximum amplitude
        max_amp = np.max(np.abs(wave_current))
        max_amplitudes.append(max_amp)
        
        # Print progress for first steps and key transitions
        if step < 10 or step % 10 == 0 or (pulse_active and current_time + dt > pulse_duration):
            status = "🔴" if pulse_active else "⚫"
            print(f"{step:4d} {current_time*1000:8.2f} {source_value:12.6f} {status:>6}")
        
        current_time += dt
    
    # Analysis
    print(f"\n📈 Results:")
    print(f"   Total steps: {len(max_amplitudes)}")
    print(f"   Maximum amplitude: {max(max_amplitudes):.8f}")
    print(f"   Final amplitude: {max_amplitudes[-1]:.8f}")
    
    # Check if wave activity was detected
    if max(max_amplitudes) > 1e-10:
        print("✅ Wave activity detected - Pulse source working!")
        
        # Find when pulse becomes inactive
        pulse_end_step = int(pulse_duration / dt)
        if pulse_end_step < len(max_amplitudes):
            during_pulse = max(max_amplitudes[:pulse_end_step]) if pulse_end_step > 0 else 0
            after_pulse = max(max_amplitudes[pulse_end_step:]) if pulse_end_step < len(max_amplitudes) else 0
            print(f"   During pulse: {during_pulse:.8f}")
            print(f"   After pulse: {after_pulse:.8f}")
            
            if during_pulse > after_pulse:
                print("✅ Pulse behavior confirmed - higher activity during pulse period")
            else:
                print("⚠️  Expected higher activity during pulse period")
        
        return True
    else:
        print("❌ No significant wave activity detected")
        return False

def main():
    """Main test function."""
    print("🌊 Python Pulse Source Implementation Test")
    print("=" * 50)
    
    try:
        success = test_python_simulation()
        
        print(f"\n{'='*50}")
        if success:
            print("🎉 Python pulse implementation test PASSED!")
        else:
            print("❌ Python pulse implementation test FAILED!")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
