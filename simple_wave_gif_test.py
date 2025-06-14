#!/usr/bin/env python3
"""
Simple Wave GIF Generator - Test the wave animation functionality
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import os
from pathlib import Path

def generate_simple_wave_animation():
    """Generate a simple test wave animation."""
    print("🌊 Generating Simple Wave Animation Test")
    
    # Output directory
    output_dir = Path("/home/yuri/Documents/project/dual_parabolic_wave_cpp/wave_animation_output")
    output_dir.mkdir(exist_ok=True)
    
    # Parameters
    grid_size = 200
    num_frames = 30
    
    # Create coordinate grid
    x = np.linspace(-300, 300, grid_size)
    y = np.linspace(-300, 300, grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Generate wave frames
    wave_frames = []
    for frame in range(num_frames):
        t = frame * 0.01  # Time progression
        
        # Simple expanding circular wave
        r = np.sqrt(X**2 + Y**2)
        wave_radius = 50 * t  # Expanding wave
        
        # Wave equation
        wave_field = np.zeros_like(X)
        if wave_radius > 0:
            # Gaussian wave front
            wave_field = np.exp(-(r - wave_radius)**2 / 400) * np.cos(2 * np.pi * (r - wave_radius) / 50)
            wave_field *= np.exp(-r / 1000)  # Attenuation
        
        # Add source at center
        center = grid_size // 2
        source_amplitude = np.cos(2 * np.pi * frame / 10) * np.exp(-frame / 20)
        wave_field[center-5:center+5, center-5:center+5] += source_amplitude * 0.1
        
        wave_frames.append(wave_field)
        print(f"Generated frame {frame+1}/{num_frames}")
    
    # Create animation
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Determine color scale
    vmax = max(np.max(np.abs(frame)) for frame in wave_frames)
    vmin = -vmax
    
    # Initial plot
    im = ax.imshow(wave_frames[0], cmap='RdBu_r', origin='lower',
                  vmin=vmin, vmax=vmax, extent=[-300, 300, -300, 300])
    
    ax.set_xlabel('X Position (mm)')
    ax.set_ylabel('Y Position (mm)')
    title_text = ax.set_title('Simple Wave Propagation Test - Frame 0')
    
    plt.colorbar(im, ax=ax, label='Wave Amplitude')
    
    # Add parabola outlines
    theta = np.linspace(0, 2*np.pi, 100)
    
    # Major parabola (508mm diameter)
    major_x = 254 * np.cos(theta)
    major_y = 254 * np.sin(theta)
    ax.plot(major_x, major_y, 'k--', linewidth=2, alpha=0.7, label='Major Parabola')
    
    # Minor parabola (200mm diameter)
    minor_x = 100 * np.cos(theta)
    minor_y = 100 * np.sin(theta)
    ax.plot(minor_x, minor_y, 'k:', linewidth=2, alpha=0.7, label='Minor Parabola')
    
    # Focus point
    ax.plot(0, 0, 'yo', markersize=8, label='Focus Point')
    ax.legend()
    
    def animate(frame):
        im.set_array(wave_frames[frame])
        title_text.set_text(f'Simple Wave Propagation Test - Frame {frame}')
        return [im, title_text]
    
    # Create and save animation
    anim = animation.FuncAnimation(fig, animate, frames=len(wave_frames),
                                 interval=100, blit=True, repeat=True)
    
    gif_path = output_dir / "simple_wave_test.gif"
    print(f"Saving animation to {gif_path}...")
    anim.save(str(gif_path), writer='pillow', fps=10)
    
    plt.close()
    
    print(f"✅ Animation saved successfully!")
    print(f"📁 Location: {gif_path}")
    
    return str(gif_path)

if __name__ == "__main__":
    generate_simple_wave_animation()
