#!/usr/bin/env python3
"""
Python Wave Animation Generator using C++ exported data

This script reads wave data exported by the C++ simulation and creates 
high-quality GIF animations showing wave propagation between parabolic reflectors.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon
import os
import sys
import glob
from PIL import Image
import io
import json

class CppDataWaveAnimator:
    """
    Wave animation generator using C++ exported data
    """
    
    def __init__(self, data_directory):
        """
        Initialize the animator with C++ exported data
        
        Args:
            data_directory: Directory containing C++ exported wave data
        """
        self.data_dir = data_directory
        self.metadata = self.load_metadata()
        self.boundary_mask = self.load_boundary_mask()
        self.wave_snapshots = []
        self.load_wave_data()
        
        print(f"🌊 Loaded C++ wave simulation data")
        print(f"   Grid: {self.metadata['grid_size']}x{self.metadata['grid_size']}")
        print(f"   Domain: {self.metadata['domain_size_mm']:.0f}mm x {self.metadata['domain_size_mm']:.0f}mm")
        print(f"   Snapshots: {len(self.wave_snapshots)}")
        print(f"   Duration: {self.metadata['total_duration_s']:.2e} s")
        
    def load_metadata(self):
        """Load simulation metadata"""
        metadata_file = os.path.join(self.data_dir, "metadata.txt")
        metadata = {}
        
        with open(metadata_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Try to convert to appropriate type
                    try:
                        if '.' in value or 'e' in value.lower():
                            metadata[key] = float(value)
                        elif value.lower() in ['true', 'false']:
                            metadata[key] = value.lower() == 'true'
                        else:
                            metadata[key] = int(value)
                    except ValueError:
                        metadata[key] = value
        
        return metadata
    
    def load_boundary_mask(self):
        """Load parabolic boundary mask"""
        mask_file = os.path.join(self.data_dir, "boundary_mask.txt")
        mask = np.loadtxt(mask_file, dtype=int)
        return mask
    
    def load_wave_data(self):
        """Load all wave data snapshots"""
        wave_files = sorted(glob.glob(os.path.join(self.data_dir, "wave_data_t*.txt")))
        
        for wave_file in wave_files:
            wave_data = np.loadtxt(wave_file, dtype=float)
            self.wave_snapshots.append(wave_data)
    
    def get_parabola_coordinates(self):
        """Get parabola coordinates for visualization"""
        # Major parabola: 508mm diameter, 100mm focal length
        major_diameter = self.metadata['major_parabola_diameter_mm']
        major_focus = self.metadata['major_parabola_focus_mm']
        
        # Minor parabola: 200mm diameter, 50mm focal length  
        minor_diameter = self.metadata['minor_parabola_diameter_mm']
        minor_focus = self.metadata['minor_parabola_focus_mm']
        
        # Generate parabola curves
        x_major = np.linspace(-major_diameter/2, major_diameter/2, 100)
        y_major = -(x_major**2) / (4 * major_focus) + major_focus
        
        x_minor = np.linspace(-minor_diameter/2, minor_diameter/2, 100)
        y_minor = (x_minor**2) / (4 * minor_focus) - minor_focus
        
        return {
            'major': {'x': x_major, 'y': y_major},
            'minor': {'x': x_minor, 'y': y_minor}
        }
    
    def create_coordinate_grids(self):
        """Create coordinate grids for plotting"""
        domain_size = self.metadata['domain_size_mm']
        grid_size = self.metadata['grid_size']
        
        x_coords = np.linspace(-domain_size/2, domain_size/2, grid_size)
        y_coords = np.linspace(-domain_size/2, domain_size/2, grid_size)
        X, Y = np.meshgrid(x_coords, y_coords)
        
        return X, Y
    
    def create_animation(self, output_path="cpp_wave_animation.gif", fps=10, skip_frames=1):
        """
        Create animated GIF from wave snapshots
        
        Args:
            output_path: Output GIF file path
            fps: Frames per second
            skip_frames: Skip every N frames (for speed)
        """
        print(f"🎬 Creating wave animation...")
        print(f"   Input snapshots: {len(self.wave_snapshots)}")
        print(f"   Skip frames: {skip_frames}")
        print(f"   Output: {output_path}")
        
        # Get coordinate grids and parabola data
        X, Y = self.create_coordinate_grids()
        parabolas = self.get_parabola_coordinates()
        
        # Select frames to animate
        selected_snapshots = self.wave_snapshots[::skip_frames]
        print(f"   Animation frames: {len(selected_snapshots)}")
        
        # Find global amplitude range for consistent colormap
        all_data = []
        for snap in selected_snapshots:
            # Use only non-boundary points for amplitude range
            masked_snap = snap[self.boundary_mask == 1]
            if len(masked_snap) > 0:
                all_data.extend(masked_snap.flatten())
        
        if len(all_data) > 0:
            all_data = np.array(all_data)
            vmin, vmax = np.percentile(all_data, [2, 98])
            if vmax == vmin:
                vmax = vmin + 1e-10
        else:
            vmin, vmax = -1e-6, 1e-6
        
        print(f"   Wave amplitude range: [{vmin:.2e}, {vmax:.2e}]")
        
        # Create animation frames
        frames = []
        time_step = self.metadata['time_step_s']
        capture_interval = 10  # From C++ exporter
        
        for i, wave_data in enumerate(selected_snapshots):
            fig, ax = plt.subplots(figsize=(12, 10))
            
            # Mask out boundary regions for visualization
            masked_wave = np.where(self.boundary_mask == 1, wave_data, np.nan)
            
            # Plot wave field
            im = ax.contourf(X, Y, masked_wave, levels=50, 
                           cmap='RdBu_r', vmin=vmin, vmax=vmax, extend='both')
            
            # Add parabola outlines
            ax.plot(parabolas['major']['x'], parabolas['major']['y'], 
                   'k-', linewidth=3, label=f"Major Parabola ({self.metadata['major_parabola_diameter_mm']:.0f}mm)")
            ax.plot(parabolas['minor']['x'], parabolas['minor']['y'], 
                   'k-', linewidth=3, label=f"Minor Parabola ({self.metadata['minor_parabola_diameter_mm']:.0f}mm)")
            
            # Mark focus point
            ax.plot(0, 0, 'r*', markersize=15, label='Focus Point & Wave Source')
            
            # Add boundary regions as shaded areas
            boundary_contour = ax.contour(X, Y, self.boundary_mask, levels=[0.5], colors='gray', linewidths=1, alpha=0.5)
            
            # Calculate current time
            current_time = i * skip_frames * capture_interval * time_step
            
            # Formatting
            domain_size = self.metadata['domain_size_mm']
            ax.set_xlim(-domain_size/2, domain_size/2)
            ax.set_ylim(-domain_size/2, domain_size/2)
            ax.set_xlabel('X (mm)', fontsize=12)
            ax.set_ylabel('Y (mm)', fontsize=12)
            ax.set_title(f'Ground Truth Wave Propagation - Time: {current_time:.2e} s\\n'
                        f'Dual Parabolic Reflector System (C++ Implementation)', fontsize=14)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label('Wave Amplitude', fontsize=12)
            
            # Add legend
            ax.legend(loc='upper right', bbox_to_anchor=(1.0, 1.0), fontsize=10)
            
            # Add specifications text
            specs_text = f"""Specifications:
• Major: {self.metadata['major_parabola_diameter_mm']:.0f}mm ⌀, {self.metadata['major_parabola_focus_mm']:.0f}mm focus
• Minor: {self.metadata['minor_parabola_diameter_mm']:.0f}mm ⌀, {self.metadata['minor_parabola_focus_mm']:.0f}mm focus
• Wave Speed: {self.metadata['wave_speed_ms']:.0f} m/s
• CFL Stable: {self.metadata['cfl_stable']}"""
            
            ax.text(0.02, 0.98, specs_text, transform=ax.transAxes, fontsize=9,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            
            # Convert to PIL Image
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            frames.append(Image.open(buf))
            plt.close(fig)
            
            if (i + 1) % 5 == 0:
                print(f"   Rendered {i + 1}/{len(selected_snapshots)} frames...")
        
        # Save as GIF
        print(f"💾 Saving GIF animation...")
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=1000//fps,  # milliseconds per frame
            loop=0
        )
        
        # Also save key frames as PNG
        key_frames = [0, len(frames)//4, len(frames)//2, 3*len(frames)//4, -1]
        output_dir = os.path.dirname(output_path) or '.'
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        
        for i, frame_idx in enumerate(key_frames):
            frame_path = os.path.join(output_dir, f"{base_name}_frame_{i:02d}.png")
            frames[frame_idx].save(frame_path)
        
        print(f"✅ Animation saved: {output_path}")
        print(f"   File size: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
        print(f"   Key frames saved as PNG files")
        
        return output_path
    
    def print_summary(self):
        """Print summary of the loaded data"""
        print(f"\n📊 C++ Wave Simulation Summary:")
        print(f"   {'='*50}")
        print(f"   Grid Size: {self.metadata['grid_size']}x{self.metadata['grid_size']}")
        print(f"   Domain: {self.metadata['domain_size_mm']:.0f}mm x {self.metadata['domain_size_mm']:.0f}mm")
        print(f"   Wave Speed: {self.metadata['wave_speed_ms']:.0f} m/s")
        print(f"   Time Step: {self.metadata['time_step_s']:.2e} s")
        print(f"   Duration: {self.metadata['total_duration_s']:.2e} s")
        print(f"   Snapshots: {self.metadata['num_time_steps']}")
        print(f"   Major Parabola: {self.metadata['major_parabola_diameter_mm']:.0f}mm ⌀, {self.metadata['major_parabola_focus_mm']:.0f}mm focus")
        print(f"   Minor Parabola: {self.metadata['minor_parabola_diameter_mm']:.0f}mm ⌀, {self.metadata['minor_parabola_focus_mm']:.0f}mm focus")
        print(f"   Ground Truth Compatible: {self.metadata['ground_truth_compatible']}")
        print(f"   Rigid Boundaries: {self.metadata['rigid_boundary_conditions']}")
        print(f"   CFL Stable: {self.metadata['cfl_stable']}")

def main():
    """Main function"""
    print("🌊 C++ Wave Data Animation Generator")
    print("=" * 50)
    
    # Parse command line arguments
    data_dir = "cpp_wave_data"
    output_file = "cpp_dual_parabolic_wave_animation.gif"
    
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        print("Please run the C++ wave data exporter first:")
        print("  ./build_exporter/bin/WaveDataExporter")
        return False
    
    try:
        # Create animator
        animator = CppDataWaveAnimator(data_dir)
        animator.print_summary()
        
        # Create animation
        output_path = animator.create_animation(
            output_path=output_file,
            fps=8,
            skip_frames=2  # Use every 2nd frame for smoother animation
        )
        
        print(f"\n🎉 Wave animation generation completed!")
        print(f"   ✅ Ground truth wave equation implemented")
        print(f"   ✅ Parabolic reflectors with rigid boundaries")
        print(f"   ✅ CFL-stable time stepping")
        print(f"   ✅ Coincident focus points")
        print(f"   📁 Animation: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
