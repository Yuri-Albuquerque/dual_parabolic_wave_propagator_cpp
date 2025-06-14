#!/usr/bin/env python3
"""
Thick Parabolic Wave Animation Generator
Creates GIF animation showing wave propagation with thick parabolic boundaries
that have 1000x slower wave velocity.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import glob
from typing import List, Tuple, Dict
import json

def load_simulation_metadata(data_dir: str) -> Dict:
    """Load simulation metadata from the C++ export."""
    metadata_file = os.path.join(data_dir, "metadata.txt")
    metadata = {}
    
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    try:
                        metadata[key] = float(value)
                    except ValueError:
                        metadata[key] = value
    
    return metadata

def load_boundary_data(data_dir: str) -> Tuple[np.ndarray, np.ndarray]:
    """Load boundary mask and boundary types from C++ export."""
    boundary_file = os.path.join(data_dir, "boundary_mask.txt")
    
    if not os.path.exists(boundary_file):
        raise FileNotFoundError(f"Boundary mask file not found: {boundary_file}")
    
    # Load boundary mask
    boundary_data = np.loadtxt(boundary_file)
    
    # For thick parabolic boundaries, we need to identify different material types
    # The C++ code exports the boundary mask (0=rigid, 1=propagation)
    # We'll create boundary types based on geometry analysis
    
    grid_size = int(np.sqrt(len(boundary_data)))
    boundary_mask = boundary_data.reshape(grid_size, grid_size)
    
    # Create boundary types array
    # 0 = AIR, 1 = PARABOLIC (thick), 2 = RIGID
    boundary_types = np.zeros_like(boundary_mask, dtype=int)
    
    # The actual boundary types will be determined from wave behavior
    # For now, use the mask as a proxy
    boundary_types[boundary_mask == 0] = 2  # Rigid boundaries
    boundary_types[boundary_mask == 1] = 0  # Air (will be refined below)
    
    return boundary_mask, boundary_types

def detect_parabolic_regions(wave_data: np.ndarray, boundary_mask: np.ndarray) -> np.ndarray:
    """Detect thick parabolic regions based on wave propagation behavior."""
    grid_size = wave_data.shape[0]
    
    # Create coordinate grids
    x_coords = np.linspace(-5, 5, grid_size)  # 10mm domain
    y_coords = np.linspace(5, -5, grid_size)  # Flipped Y
    X, Y = np.meshgrid(x_coords, y_coords)
    
    # Parabola parameters (30mm thick boundaries)
    major_focus = 100.0  # mm
    minor_focus = 50.0   # mm
    major_diameter = 508.0  # 20 inches in mm
    minor_diameter = 200.0  # mm
    thickness = 30.0     # 30mm thick parabolic material
    
    # Major parabola (umbrella): y = -x²/(4*f) + f
    major_y = -(X**2) / (4.0 * major_focus) + major_focus
    inside_major = (Y <= major_y) & (np.abs(X) <= major_diameter / 2.0)
    
    # Minor parabola (bowl): y = x²/(4*f) - f
    minor_y = (X**2) / (4.0 * minor_focus) - minor_focus
    outside_minor = (Y >= minor_y) & (np.abs(X) <= minor_diameter / 2.0)
    
    # Calculate distances to parabolic surfaces
    dist_to_major = np.abs(Y - major_y)
    dist_to_minor = np.abs(Y - minor_y)
    
    # Air region (normal propagation)
    air_region = inside_major & outside_minor
    
    # Thick parabolic material regions
    near_major = inside_major & (dist_to_major <= thickness)
    near_minor = outside_minor & (dist_to_minor <= thickness)
    parabolic_region = (near_major | near_minor) & air_region
    
    # Create boundary types array
    boundary_types = np.zeros_like(boundary_mask, dtype=int)
    boundary_types[boundary_mask == 0] = 2  # Rigid
    boundary_types[air_region & (boundary_mask == 1) & ~parabolic_region] = 0  # Air
    boundary_types[parabolic_region & (boundary_mask == 1)] = 1  # Parabolic material
    
    return boundary_types

def load_wave_snapshots(data_dir: str, max_frames: int = 50) -> List[np.ndarray]:
    """Load wave field snapshots from C++ export."""
    wave_files = sorted(glob.glob(os.path.join(data_dir, "wave_data_t*.txt")))
    
    print(f"Found {len(wave_files)} wave data files")
    
    # Sample frames evenly
    if len(wave_files) > max_frames:
        indices = np.linspace(0, len(wave_files) - 1, max_frames, dtype=int)
        wave_files = [wave_files[i] for i in indices]
    
    wave_snapshots = []
    grid_size = None
    
    for i, file_path in enumerate(wave_files):
        try:
            wave_data = np.loadtxt(file_path)
            
            if grid_size is None:
                grid_size = int(np.sqrt(len(wave_data)))
                print(f"Grid size detected: {grid_size}x{grid_size}")
            
            wave_field = wave_data.reshape(grid_size, grid_size)
            wave_snapshots.append(wave_field)
            
            if (i + 1) % 10 == 0:
                print(f"Loaded {i + 1}/{len(wave_files)} wave snapshots...")
                
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue
    
    print(f"Successfully loaded {len(wave_snapshots)} wave snapshots")
    return wave_snapshots

def create_thick_parabolic_animation(data_dir: str, output_file: str):
    """Create animation showing wave propagation with thick parabolic boundaries."""
    print("🎬 Creating thick parabolic wave animation...")
    
    # Load simulation data
    metadata = load_simulation_metadata(data_dir)
    print(f"Metadata: {metadata}")
    
    boundary_mask, _ = load_boundary_data(data_dir)
    wave_snapshots = load_wave_snapshots(data_dir, max_frames=100)
    
    if not wave_snapshots:
        raise ValueError("No wave snapshots loaded!")
    
    # Detect parabolic regions from first frame
    boundary_types = detect_parabolic_regions(wave_snapshots[0], boundary_mask)
    
    grid_size = wave_snapshots[0].shape[0]
    domain_size = metadata.get('domain_size_mm', 10.0)
    
    # Create coordinate grids
    x_coords = np.linspace(-domain_size/2, domain_size/2, grid_size)
    y_coords = np.linspace(domain_size/2, -domain_size/2, grid_size)
    X, Y = np.meshgrid(x_coords, y_coords)
    
    # Set up the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Find global amplitude range
    all_amplitudes = np.concatenate([frame.flatten() for frame in wave_snapshots])
    vmin, vmax = np.percentile(all_amplitudes, [1, 99])
    if vmax == vmin:
        vmax = vmin + 1e-10
    
    print(f"Animation amplitude range: [{vmin:.2e}, {vmax:.2e}]")
    
    # Plot 1: Wave field with boundaries
    im1 = ax1.imshow(wave_snapshots[0], extent=[-domain_size/2, domain_size/2, -domain_size/2, domain_size/2],
                     cmap='RdBu_r', vmin=vmin, vmax=vmax, origin='upper')
    
    # Overlay boundary types
    boundary_colors = np.zeros((*boundary_types.shape, 4))  # RGBA
    boundary_colors[boundary_types == 0] = [0, 0, 0, 0]        # Transparent (Air)
    boundary_colors[boundary_types == 1] = [1, 1, 0, 0.3]      # Yellow (Parabolic material)
    boundary_colors[boundary_types == 2] = [0.5, 0.5, 0.5, 0.8]  # Gray (Rigid boundary)
    
    overlay1 = ax1.imshow(boundary_colors, extent=[-domain_size/2, domain_size/2, -domain_size/2, domain_size/2],
                          origin='upper')
    
    ax1.set_title('Wave Field with Thick Parabolic Boundaries\n(Yellow=Parabolic Material, Gray=Rigid)', fontsize=12)
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    
    # Add colorbar
    cbar1 = fig.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('Wave Amplitude')
    
    # Plot 2: Material properties
    material_display = np.zeros_like(boundary_types, dtype=float)
    material_display[boundary_types == 0] = 1.0   # Air (normal speed)
    material_display[boundary_types == 1] = 0.001 # Parabolic (1000x slower)
    material_display[boundary_types == 2] = 0.0   # Rigid (no propagation)
    
    im2 = ax2.imshow(material_display, extent=[-domain_size/2, domain_size/2, -domain_size/2, domain_size/2],
                     cmap='viridis', origin='upper')
    ax2.set_title('Material Properties\n(Relative Wave Speed)', fontsize=12)
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    
    cbar2 = fig.colorbar(im2, ax=ax2, shrink=0.8)
    cbar2.set_label('Relative Wave Speed')
    
    # Add time display
    time_text = fig.suptitle('Time: 0.00 μs', fontsize=14)
    
    def update_frame(frame_idx):
        if frame_idx < len(wave_snapshots):
            # Update wave field
            im1.set_array(wave_snapshots[frame_idx])
            
            # Update time
            time_step = metadata.get('time_step', 1e-9)
            capture_interval = metadata.get('capture_interval', 10)
            current_time = frame_idx * capture_interval * time_step * 1e6  # Convert to microseconds
            time_text.set_text(f'Time: {current_time:.3f} μs - Thick Parabolic Boundaries (30mm, 1000x slower)')
        
        return [im1]
    
    # Create animation
    print(f"Creating animation with {len(wave_snapshots)} frames...")
    anim = FuncAnimation(fig, update_frame, frames=len(wave_snapshots), 
                        interval=100, blit=False, repeat=True)
    
    # Save animation
    print(f"Saving animation to {output_file}...")
    anim.save(output_file, writer='pillow', fps=10, dpi=100)
    
    plt.tight_layout()
    print(f"✅ Animation saved: {output_file}")
    
    # Create summary plot
    summary_file = output_file.replace('.gif', '_summary.png')
    plt.savefig(summary_file, dpi=150, bbox_inches='tight')
    print(f"✅ Summary plot saved: {summary_file}")
    
    plt.close()

def main():
    data_dir = "thick_parabolic_wave_data"
    output_file = "thick_parabolic_wave_animation.gif"
    
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        print("Please run the WaveDataExporter first to generate simulation data.")
        return
    
    try:
        create_thick_parabolic_animation(data_dir, output_file)
        
        # Show file size
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
            print(f"📊 Animation file size: {file_size:.1f} MB")
            
    except Exception as e:
        print(f"❌ Error creating animation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
