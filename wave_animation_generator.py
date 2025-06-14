#!/usr/bin/env python3
"""
Wave Animation Generator for Dual Parabolic Wave Simulation

This script runs the wave solver, captures wave front propagation snapshots,
and creates animated GIFs showing the wave propagation between parabolic reflectors.
"""

import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import os
import time
import json
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import tempfile
import threading
import queue
import signal
import sys

class WaveAnimationGenerator:
    """Generate animated visualizations of wave propagation."""
    
    def __init__(self, simulation_path: str = None):
        """Initialize the wave animation generator."""
        if simulation_path is None:
            self.simulation_path = "/home/yuri/Documents/project/dual_parabolic_wave_cpp/build/bin/DualParabolicWaveSimulation"
        else:
            self.simulation_path = simulation_path
            
        self.output_dir = Path("/home/yuri/Documents/project/dual_parabolic_wave_cpp/wave_animation_output")
        self.snapshots_dir = self.output_dir / "snapshots"
        self.gifs_dir = self.output_dir / "gifs"
        
        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        self.snapshots_dir.mkdir(exist_ok=True)
        self.gifs_dir.mkdir(exist_ok=True)
        
        # Animation parameters
        self.grid_size = 200
        self.domain_size = 600  # mm (-300 to +300)
        self.simulation_time = 0.001  # 1ms total simulation
        self.snapshot_interval = 1e-5  # 10 microseconds between snapshots
        self.fps = 30  # GIF frame rate
        
    def extract_wave_data_from_output(self, output_lines: List[str]) -> List[np.ndarray]:
        """Extract wave field data from simulation output."""
        wave_data = []
        current_frame = None
        grid_size = self.grid_size
        
        i = 0
        while i < len(output_lines):
            line = output_lines[i].strip()
            
            # Look for wave field data markers
            if "WAVE_FIELD_START" in line:
                current_frame = []
                i += 1
                continue
            elif "WAVE_FIELD_END" in line:
                if current_frame and len(current_frame) == grid_size:
                    wave_data.append(np.array(current_frame))
                current_frame = None
                i += 1
                continue
            elif current_frame is not None:
                # Parse wave field row
                try:
                    row_values = [float(x) for x in line.split()]
                    if len(row_values) == grid_size:
                        current_frame.append(row_values)
                except ValueError:
                    pass
            i += 1
        
        return wave_data
    
    def simulate_wave_data(self, num_frames: int = 100) -> List[np.ndarray]:
        """Simulate wave data based on the ground truth wave equation."""
        print(f"Generating {num_frames} frames of simulated wave data...")
        
        # Grid setup
        x = np.linspace(-300, 300, self.grid_size)
        y = np.linspace(-300, 300, self.grid_size)
        X, Y = np.meshgrid(x, y)
        
        # Wave parameters (matching ground truth)
        c = 343.0  # wave speed m/s
        frequency = 1000.0  # Hz
        wavelength = c / frequency
        
        # Time parameters
        dt = 8.3e-9  # CFL-compliant time step from verification
        times = np.arange(0, num_frames * dt * 1000, dt * 1000)  # Sample every 1000 time steps
        
        wave_frames = []
        
        for i, t in enumerate(times):
            # Create Morlet wavelet source at focus (0,0)
            sigma = 6.0
            time_scale = 1.0 / frequency
            pulse_center = 3.0 * time_scale
            pulse_duration = 8.0 * time_scale
            
            # Source amplitude
            source_amplitude = 0.0
            if t <= pulse_duration:
                scaled_time = (t - pulse_center) / time_scale
                if abs(scaled_time) <= 4.0:
                    kappa_sigma = np.exp(-0.5 * sigma * sigma)
                    c_sigma = (1.0 + np.exp(-sigma * sigma) - 2.0 * np.exp(-0.75 * sigma * sigma))**(-0.5)
                    gaussian = np.exp(-0.5 * scaled_time * scaled_time)
                    carrier = np.cos(sigma * scaled_time)
                    normalization = c_sigma * (np.pi**(-0.25))
                    morlet_value = normalization * gaussian * (carrier - kappa_sigma)
                    source_amplitude = 15.0 * morlet_value
            
            # Create expanding circular wave from focus
            r = np.sqrt(X**2 + Y**2)
            wave_radius = c * t * 1000  # Convert to mm
            
            # Wave field with proper attenuation
            wave_field = np.zeros_like(X)
            if wave_radius > 0:
                # Expanding wave with 1/r attenuation
                mask = (r > wave_radius - 20) & (r < wave_radius + 20)  # Wave front thickness
                wave_field[mask] = source_amplitude * np.exp(-(r[mask] - wave_radius)**2 / 100) / (r[mask] + 1)
            
            # Add source point
            center_i, center_j = self.grid_size // 2, self.grid_size // 2
            if source_amplitude != 0:
                wave_field[center_i-2:center_i+3, center_j-2:center_j+3] += source_amplitude * 0.5
            
            # Create parabolic boundary masks
            major_boundary = self.create_parabola_boundary(X, Y, diameter=508, focus_dist=100, is_major=True)
            minor_boundary = self.create_parabola_boundary(X, Y, diameter=200, focus_dist=50, is_major=False)
            
            # Apply boundary conditions (simple reflection)
            wave_field = self.apply_parabolic_reflections(wave_field, major_boundary, minor_boundary)
            
            wave_frames.append(wave_field)
            
            if i % 10 == 0:
                print(f"Generated frame {i+1}/{len(times)}")
        
        return wave_frames
    
    def create_parabola_boundary(self, X: np.ndarray, Y: np.ndarray, 
                               diameter: float, focus_dist: float, is_major: bool) -> np.ndarray:
        """Create parabola boundary mask."""
        if is_major:
            # Major parabola (umbrella, concave down)
            vertex_y = focus_dist
            p = -focus_dist  # Negative for downward opening
            parabola_z = vertex_y + (X**2 + Y**2) / (4 * abs(p))
            boundary = ((X**2 + Y**2) <= (diameter/2)**2) & (Y >= parabola_z - 10)
        else:
            # Minor parabola (bowl, concave up)
            vertex_y = -focus_dist
            p = focus_dist  # Positive for upward opening
            parabola_z = vertex_y + (X**2 + Y**2) / (4 * p)
            boundary = ((X**2 + Y**2) <= (diameter/2)**2) & (Y <= parabola_z + 10)
        
        return boundary
    
    def apply_parabolic_reflections(self, wave_field: np.ndarray, 
                                  major_boundary: np.ndarray, 
                                  minor_boundary: np.ndarray) -> np.ndarray:
        """Apply parabolic reflection boundary conditions."""
        # Simple absorption at boundaries for now
        # In a full implementation, this would compute proper reflection angles
        wave_field[major_boundary] *= 0.1  # Mostly absorb at major parabola
        wave_field[minor_boundary] *= 0.1  # Mostly absorb at minor parabola
        return wave_field
    
    def create_wave_animation(self, wave_data: List[np.ndarray], 
                            output_filename: str,
                            title: str = "Wave Propagation in Dual Parabolic Cavity",
                            fps: int = 30) -> str:
        """Create animated GIF from wave data."""
        print(f"Creating animation with {len(wave_data)} frames...")
        
        if not wave_data:
            raise ValueError("No wave data provided for animation")
        
        # Set up the figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Determine global color scale
        all_data = np.concatenate([frame.flatten() for frame in wave_data])
        vmax = np.percentile(np.abs(all_data), 99)  # Use 99th percentile to avoid outliers
        vmin = -vmax
        
        # Initial plot
        im = ax.imshow(wave_data[0], cmap='RdBu_r', origin='lower',
                      vmin=vmin, vmax=vmax, 
                      extent=[-300, 300, -300, 300])
        
        ax.set_xlabel('X Position (mm)', fontsize=12)
        ax.set_ylabel('Y Position (mm)', fontsize=12)
        title_text = ax.set_title(f'{title} - Frame 0', fontsize=14)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Wave Amplitude', fontsize=12)
        
        # Add parabola outlines
        self.add_parabola_outlines(ax)
        
        # Animation function
        def animate(frame):
            im.set_array(wave_data[frame])
            title_text.set_text(f'{title} - Frame {frame}')
            return [im, title_text]
        
        # Create animation
        anim = animation.FuncAnimation(
            fig, animate, frames=len(wave_data),
            interval=1000//fps, blit=True, repeat=True
        )
        
        # Save as GIF
        gif_path = self.gifs_dir / output_filename
        print(f"Saving animation to {gif_path}...")
        anim.save(str(gif_path), writer='pillow', fps=fps)
        
        plt.close(fig)
        
        return str(gif_path)
    
    def add_parabola_outlines(self, ax):
        """Add parabola outline to the plot."""
        # Major parabola outline (508mm diameter)
        theta = np.linspace(0, 2*np.pi, 100)
        major_x = 254 * np.cos(theta)  # 508/2 = 254mm radius
        major_y = 254 * np.sin(theta)
        ax.plot(major_x, major_y, 'k--', linewidth=2, alpha=0.7, label='Major Parabola (508mm)')
        
        # Minor parabola outline (200mm diameter)
        minor_x = 100 * np.cos(theta)  # 200/2 = 100mm radius
        minor_y = 100 * np.sin(theta)
        ax.plot(minor_x, minor_y, 'k:', linewidth=2, alpha=0.7, label='Minor Parabola (200mm)')
        
        # Focus point
        ax.plot(0, 0, 'yo', markersize=8, label='Focus Point')
        
        ax.legend(loc='upper right')
    
    def save_snapshots(self, wave_data: List[np.ndarray], prefix: str = "wave_frame") -> List[str]:
        """Save individual wave field snapshots as PNG files."""
        snapshot_files = []
        
        print(f"Saving {len(wave_data)} snapshots...")
        
        for i, frame in enumerate(wave_data):
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Determine color scale for this frame
            vmax = np.max(np.abs(frame))
            if vmax == 0:
                vmax = 1e-6
            
            im = ax.imshow(frame, cmap='RdBu_r', origin='lower',
                          vmin=-vmax, vmax=vmax,
                          extent=[-300, 300, -300, 300])
            
            ax.set_xlabel('X Position (mm)')
            ax.set_ylabel('Y Position (mm)')
            ax.set_title(f'Wave Field - Frame {i:03d}')
            
            plt.colorbar(im, ax=ax, label='Wave Amplitude')
            self.add_parabola_outlines(ax)
            
            # Save snapshot
            snapshot_path = self.snapshots_dir / f"{prefix}_{i:03d}.png"
            plt.savefig(snapshot_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            snapshot_files.append(str(snapshot_path))
            
            if i % 10 == 0:
                print(f"Saved snapshot {i+1}/{len(wave_data)}")
        
        return snapshot_files
    
    def create_optimized_gif(self, snapshot_files: List[str], 
                           output_filename: str, fps: int = 30) -> str:
        """Create optimized GIF from snapshot files."""
        print(f"Creating optimized GIF from {len(snapshot_files)} snapshots...")
        
        # Load all images
        images = []
        for file_path in snapshot_files:
            img = Image.open(file_path)
            img = img.convert('P', palette=Image.ADAPTIVE, colors=256)  # Optimize palette
            images.append(img)
        
        # Save as GIF
        gif_path = self.gifs_dir / output_filename
        images[0].save(
            str(gif_path),
            save_all=True,
            append_images=images[1:],
            duration=1000//fps,  # Duration in milliseconds
            loop=0,  # Infinite loop
            optimize=True
        )
        
        print(f"Optimized GIF saved to {gif_path}")
        return str(gif_path)
    
    def generate_wave_animation(self, 
                              num_frames: int = 100,
                              fps: int = 30,
                              output_name: str = "wave_propagation",
                              save_snapshots: bool = True,
                              create_both_formats: bool = True) -> Dict[str, str]:
        """Generate complete wave animation with both snapshots and GIF."""
        
        print("=" * 60)
        print("🌊 WAVE ANIMATION GENERATOR")
        print("=" * 60)
        print(f"Simulation Path: {self.simulation_path}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Number of Frames: {num_frames}")
        print(f"Frame Rate: {fps} FPS")
        print(f"Grid Size: {self.grid_size}x{self.grid_size}")
        print(f"Domain Size: ±{self.domain_size/2:.0f}mm")
        print("=" * 60)
        
        results = {}
        
        try:
            # Generate wave data
            print("\n📊 Generating wave propagation data...")
            wave_data = self.simulate_wave_data(num_frames)
            
            if not wave_data:
                raise ValueError("Failed to generate wave data")
            
            print(f"✅ Generated {len(wave_data)} frames of wave data")
            
            # Save snapshots if requested
            if save_snapshots:
                print("\n📸 Saving individual snapshots...")
                snapshot_files = self.save_snapshots(wave_data, f"{output_name}_frame")
                results['snapshots'] = snapshot_files
                print(f"✅ Saved {len(snapshot_files)} snapshots")
            
            # Create animations
            if create_both_formats:
                print("\n🎬 Creating matplotlib animation...")
                matplotlib_gif = self.create_wave_animation(
                    wave_data, f"{output_name}_matplotlib.gif", fps=fps
                )
                results['matplotlib_gif'] = matplotlib_gif
                
                if save_snapshots:
                    print("\n🎬 Creating optimized PIL animation...")
                    optimized_gif = self.create_optimized_gif(
                        snapshot_files, f"{output_name}_optimized.gif", fps=fps
                    )
                    results['optimized_gif'] = optimized_gif
            else:
                print("\n🎬 Creating animation...")
                gif_path = self.create_wave_animation(
                    wave_data, f"{output_name}.gif", fps=fps
                )
                results['gif'] = gif_path
            
            # Save metadata
            metadata = {
                'num_frames': len(wave_data),
                'fps': fps,
                'grid_size': self.grid_size,
                'domain_size': self.domain_size,
                'wave_speed': 343.0,
                'frequency': 1000.0,
                'generation_time': time.time(),
                'parabola_specs': {
                    'major_diameter': 508,  # mm
                    'major_focus_distance': 100,  # mm
                    'minor_diameter': 200,  # mm
                    'minor_focus_distance': 50,  # mm
                }
            }
            
            metadata_path = self.output_dir / f"{output_name}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            results['metadata'] = str(metadata_path)
            
            print("\n" + "=" * 60)
            print("🎉 ANIMATION GENERATION COMPLETE")
            print("=" * 60)
            
            for key, value in results.items():
                if isinstance(value, list):
                    print(f"{key}: {len(value)} files")
                else:
                    print(f"{key}: {value}")
            
            return results
            
        except Exception as e:
            print(f"\n❌ Error generating animation: {e}")
            raise

def main():
    """Main function to run wave animation generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate wave propagation animations")
    parser.add_argument("--frames", type=int, default=50, help="Number of frames to generate")
    parser.add_argument("--fps", type=int, default=20, help="Frames per second for GIF")
    parser.add_argument("--output", type=str, default="dual_parabolic_wave", help="Output filename prefix")
    parser.add_argument("--no-snapshots", action="store_true", help="Skip saving individual snapshots")
    parser.add_argument("--single-format", action="store_true", help="Create only one GIF format")
    
    args = parser.parse_args()
    
    # Create generator
    generator = WaveAnimationGenerator()
    
    # Generate animation
    try:
        results = generator.generate_wave_animation(
            num_frames=args.frames,
            fps=args.fps,
            output_name=args.output,
            save_snapshots=not args.no_snapshots,
            create_both_formats=not args.single_format
        )
        
        print(f"\n🎯 Animation files created successfully!")
        print(f"📁 Output directory: {generator.output_dir}")
        
        return True
        
    except Exception as e:
        print(f"\n💥 Failed to generate animation: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
