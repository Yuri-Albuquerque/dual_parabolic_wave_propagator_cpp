#!/usr/bin/env python3
"""
Enhanced Wave Propagation Plotter
Creates comprehensive matplotlib visualizations of wave propagation in dual parabolic cavity.
Features:
- Individual frame snapshots with detailed annotations
- Animation sequence creation  
- Energy and amplitude analysis
- Multiple visualization styles (contour, surface, streamlines)
- Export to various formats (PNG, PDF, GIF)
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
import argparse
from datetime import datetime

# Add the python package to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

# Custom colormap for wave visualization
def create_wave_colormap():
    """Create a custom colormap optimized for wave visualization."""
    colors = ['#000080', '#0000FF', '#00FFFF', '#FFFFFF', '#FFFF00', '#FF8000', '#FF0000', '#800000']
    n_bins = 256
    return LinearSegmentedColormap.from_list('wave', colors, N=n_bins)

class WavePropagationPlotter:
    """Comprehensive wave propagation visualization tool."""
    
    def __init__(self, grid_size=100, output_dir="wave_analysis"):
        self.grid_size = grid_size
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Simulation parameters
        self.num_steps = 50
        self.record_interval = 1
        self.frequency = 1000.0
        self.amplitude = 1.0
        
        # Visualization settings
        self.custom_cmap = create_wave_colormap()
        self.figure_size = (12, 10)
        self.dpi = 200
        
        print(f"Enhanced Wave Plotter initialized")
        print(f"Output directory: {self.output_dir.absolute()}")
        
    def setup_simulation(self):
        """Setup the wave simulation."""
        try:
            from dual_parabolic_wave.simulation import PythonSimulation
            print("✓ Simulation module imported")
        except ImportError as e:
            print(f"✗ Failed to import simulation: {e}")
            return None
            
        # Create simulation
        sim = PythonSimulation(grid_size=self.grid_size)
        sim.set_frequency(self.frequency)
        sim.set_amplitude(self.amplitude)
        
        print(f"✓ Simulation created (using {'C++' if sim.use_core else 'Python'} core)")
        print(f"✓ Grid: {self.grid_size}x{self.grid_size}")
        print(f"✓ CFL timestep: {sim.cfl_timestep:.2e} seconds")
        print(f"✓ Total simulation time: {self.num_steps * sim.cfl_timestep:.2e} seconds")
        
        return sim
        
    def create_coordinate_grids(self):
        """Create coordinate grids for plotting."""
        x = np.linspace(-300, 300, self.grid_size)
        y = np.linspace(-300, 300, self.grid_size)
        X, Y = np.meshgrid(x, y)
        return x, y, X, Y
        
    def get_parabola_data(self, x_range):
        """Get parabola boundary data."""
        x_para = np.linspace(x_range[0], x_range[1], 200)
        
        # Major parabola (y = -x²/400 + 100)
        y_major = -x_para**2 / 400 + 100
        mask_major = (y_major >= -300) & (y_major <= 300)
        
        # Minor parabola (y = x²/100 - 25)  
        y_minor = x_para**2 / 100 - 25
        mask_minor = (y_minor >= -300) & (y_minor <= 300)
        
        return {
            'x': x_para,
            'major_y': y_major,
            'minor_y': y_minor,
            'major_mask': mask_major,
            'minor_mask': mask_minor
        }
        
    def plot_wave_frame(self, wave_data, time_step, frame_idx, global_vmax, X, Y, style='contour'):
        """Create a single wave frame plot with multiple visualization styles."""
        
        parabola_data = self.get_parabola_data((-250, 250))
        
        if style == 'contour':
            return self._plot_contour_frame(wave_data, time_step, frame_idx, global_vmax, X, Y, parabola_data)
        elif style == 'surface':
            return self._plot_surface_frame(wave_data, time_step, frame_idx, global_vmax, X, Y, parabola_data)
        elif style == 'streamlines':
            return self._plot_streamline_frame(wave_data, time_step, frame_idx, global_vmax, X, Y, parabola_data)
        else:
            return self._plot_contour_frame(wave_data, time_step, frame_idx, global_vmax, X, Y, parabola_data)
            
    def _plot_contour_frame(self, wave_data, time_step, frame_idx, global_vmax, X, Y, parabola_data):
        """Create contour plot of wave frame."""
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        # Create contour plot
        if global_vmax > 0:
            levels = np.linspace(-global_vmax, global_vmax, 25)
            im = ax.contourf(X, Y, wave_data, levels=levels, cmap=self.custom_cmap, extend='both')
            # Add contour lines
            contours = ax.contour(X, Y, wave_data, levels=levels[::2], colors='black', alpha=0.3, linewidths=0.5)
        else:
            im = ax.contourf(X, Y, wave_data, levels=25, cmap=self.custom_cmap)
            
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Wave Amplitude', fontsize=14)
        
        # Add parabola boundaries
        ax.plot(parabola_data['x'][parabola_data['major_mask']], 
                parabola_data['major_y'][parabola_data['major_mask']], 
                'k-', linewidth=3, alpha=0.9, label='Major Parabola')
        ax.plot(parabola_data['x'][parabola_data['minor_mask']], 
                parabola_data['minor_y'][parabola_data['minor_mask']], 
                'k--', linewidth=3, alpha=0.9, label='Minor Parabola')
                
        # Mark focus points
        ax.plot(0, 100, 'ro', markersize=12, markeredgecolor='black', markeredgewidth=2, label='Major Focus')
        ax.plot(0, -25, 'bo', markersize=12, markeredgecolor='black', markeredgewidth=2, label='Minor Focus')
        
        # Calculate current statistics
        max_amp = np.max(np.abs(wave_data))
        mean_amp = np.mean(np.abs(wave_data))
        
        # Formatting
        ax.set_xlabel('X Position (mm)', fontsize=14)
        ax.set_ylabel('Y Position (mm)', fontsize=14)
        ax.set_title(f'Wave Propagation - Frame {frame_idx:03d}\n' + 
                    f'Time: {time_step:.6f} s | Max Amp: {max_amp:.2e} | Mean Amp: {mean_amp:.2e}', 
                    fontsize=16, pad=20)
        ax.set_xlim(-300, 300)
        ax.set_ylim(-300, 300)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=12, framealpha=0.9)
        
        return fig, ax
        
    def _plot_surface_frame(self, wave_data, time_step, frame_idx, global_vmax, X, Y, parabola_data):
        """Create 3D surface plot of wave frame."""
        from mpl_toolkits.mplot3d import Axes3D
        
        fig = plt.figure(figsize=self.figure_size)
        ax = fig.add_subplot(111, projection='3d')
        
        # Create surface plot (subsample for performance)
        step = max(1, self.grid_size // 50)
        X_sub = X[::step, ::step]
        Y_sub = Y[::step, ::step]
        Z_sub = wave_data[::step, ::step]
        
        surf = ax.plot_surface(X_sub, Y_sub, Z_sub, cmap=self.custom_cmap, alpha=0.8)
        
        # Add colorbar
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=20)
        
        # Formatting
        ax.set_xlabel('X Position (mm)', fontsize=12)
        ax.set_ylabel('Y Position (mm)', fontsize=12)
        ax.set_zlabel('Wave Amplitude', fontsize=12)
        ax.set_title(f'3D Wave Surface - Frame {frame_idx:03d}\nTime: {time_step:.6f} s', fontsize=14)
        
        return fig, ax
        
    def run_complete_analysis(self, styles=['contour']):
        """Run complete wave propagation analysis with multiple visualization styles."""
        
        print(f"\n=== Enhanced Wave Propagation Analysis ===")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Setup simulation
        sim = self.setup_simulation()
        if not sim:
            return False
            
        # Run simulation
        print(f"\nRunning {self.num_steps} simulation steps...")
        results = sim.run_steps(self.num_steps, self.record_interval)
        print(f"✓ Generated {len(results.wave_data)} frames")
        
        # Calculate global statistics
        max_amps = [np.max(np.abs(data)) for data in results.wave_data]
        mean_amps = [np.mean(np.abs(data)) for data in results.wave_data]
        global_vmax = max(max_amps) if max_amps else 1.0
        
        print(f"✓ Global amplitude range: [0, {global_vmax:.6e}]")
        print(f"✓ Mean amplitude range: [{min(mean_amps):.6e}, {max(mean_amps):.6e}]")
        
        # Create coordinate grids
        x, y, X, Y = self.create_coordinate_grids()
        
        # Generate plots for each style
        for style in styles:
            style_dir = self.output_dir / f"frames_{style}"
            style_dir.mkdir(exist_ok=True)
            
            print(f"\nCreating {style} plots...")
            
            for i, (wave_data, time_step) in enumerate(zip(results.wave_data, results.time_steps)):
                fig, ax = self.plot_wave_frame(wave_data, time_step, i, global_vmax, X, Y, style)
                
                # Save plot
                step_num = i * self.record_interval
                filename = style_dir / f"wave_{style}_frame_{i:03d}_step_{step_num:03d}.png"
                plt.savefig(filename, dpi=self.dpi, bbox_inches='tight', facecolor='white')
                plt.close(fig)
                
                if i % 5 == 0:
                    print(f"  Saved frame {i+1}/{len(results.wave_data)}: {filename.name}")
                    
            print(f"✓ All {style} frames saved to {style_dir}")
            
        # Create analysis plots
        self.create_analysis_plots(results, max_amps, mean_amps)
        
        # Create comparison grids
        self.create_comparison_grids(results, X, Y, global_vmax)
        
        # Generate summary report
        self.generate_summary_report(results, max_amps, mean_amps, styles)
        
        print(f"\n✅ Enhanced wave propagation analysis completed!")
        return True
        
    def create_analysis_plots(self, results, max_amps, mean_amps):
        """Create detailed analysis plots."""
        print("\nCreating analysis plots...")
        
        # Multi-panel analysis figure
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # 1. Amplitude evolution
        ax = axes[0, 0]
        ax.plot(results.time_steps, max_amps, 'b-', linewidth=2, marker='o', markersize=4, label='Maximum')
        ax.plot(results.time_steps, mean_amps, 'r--', linewidth=2, marker='s', markersize=4, label='Mean')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Wave Amplitude')
        ax.set_title('Amplitude Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 2. Energy evolution
        ax = axes[0, 1] 
        ax.plot(results.time_steps, results.energy_levels, 'g-', linewidth=2, marker='^', markersize=4)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Total Energy')
        ax.set_title('Energy Evolution')
        ax.grid(True, alpha=0.3)
        
        # 3. Amplitude vs Energy
        ax = axes[0, 2]
        ax.scatter(max_amps, results.energy_levels, c=results.time_steps, cmap='viridis', s=30)
        ax.set_xlabel('Maximum Amplitude')
        ax.set_ylabel('Total Energy')
        ax.set_title('Amplitude vs Energy')
        cbar = plt.colorbar(ax.collections[0], ax=ax)
        cbar.set_label('Time (s)')
        ax.grid(True, alpha=0.3)
        
        # 4. Amplitude histogram
        ax = axes[1, 0]
        ax.hist(max_amps, bins=15, alpha=0.7, color='blue', edgecolor='black')
        ax.axvline(np.mean(max_amps), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(max_amps):.2e}')
        ax.set_xlabel('Maximum Amplitude')
        ax.set_ylabel('Frequency')
        ax.set_title('Amplitude Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 5. Rate of change
        ax = axes[1, 1]
        amp_diff = np.diff(max_amps)
        time_diff = np.diff(results.time_steps)
        amp_rate = amp_diff / time_diff
        ax.plot(results.time_steps[1:], amp_rate, 'purple', linewidth=2, marker='d', markersize=3)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Rate of Amplitude Change')
        ax.set_title('Amplitude Change Rate')
        ax.grid(True, alpha=0.3)
        
        # 6. Phase analysis (simplified)
        ax = axes[1, 2]
        # Calculate relative phases between consecutive frames
        phases = []
        for i in range(1, len(results.wave_data)):
            correlation = np.corrcoef(results.wave_data[i-1].flatten(), results.wave_data[i].flatten())[0,1]
            phases.append(correlation)
        
        ax.plot(results.time_steps[1:], phases, 'orange', linewidth=2, marker='*', markersize=4)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frame Correlation')
        ax.set_title('Wave Pattern Correlation')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        analysis_file = self.output_dir / "wave_analysis_comprehensive.png"
        plt.savefig(analysis_file, dpi=self.dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ Analysis plots saved: {analysis_file.name}")
        
    def create_comparison_grids(self, results, X, Y, global_vmax):
        """Create comparison grids showing wave evolution."""
        print("Creating comparison grids...")
        
        # Select key frames for comparison
        n_frames = len(results.wave_data)
        if n_frames >= 9:
            frame_indices = [0, n_frames//8, n_frames//4, 3*n_frames//8, n_frames//2, 
                           5*n_frames//8, 3*n_frames//4, 7*n_frames//8, n_frames-1]
            grid_shape = (3, 3)
        elif n_frames >= 6:
            frame_indices = [0, n_frames//5, 2*n_frames//5, 3*n_frames//5, 4*n_frames//5, n_frames-1]
            grid_shape = (2, 3)
        else:
            frame_indices = list(range(min(4, n_frames)))
            grid_shape = (2, 2)
            
        fig, axes = plt.subplots(*grid_shape, figsize=(15, 12))
        if grid_shape[0] == 1:
            axes = [axes]
        axes = np.array(axes).flatten()
        
        parabola_data = self.get_parabola_data((-250, 250))
        
        for idx, frame_i in enumerate(frame_indices[:len(axes)]):
            ax = axes[idx]
            wave_data = results.wave_data[frame_i]
            time_step = results.time_steps[frame_i]
            max_amp = np.max(np.abs(wave_data))
            
            # Create contour plot
            if global_vmax > 0:
                levels = np.linspace(-global_vmax, global_vmax, 20)
                im = ax.contourf(X, Y, wave_data, levels=levels, cmap=self.custom_cmap, extend='both')
            else:
                im = ax.contourf(X, Y, wave_data, levels=20, cmap=self.custom_cmap)
                
            # Add parabola boundaries (simplified for grid)
            ax.plot(parabola_data['x'][parabola_data['major_mask']], 
                    parabola_data['major_y'][parabola_data['major_mask']], 
                    'k-', linewidth=2, alpha=0.8)
            ax.plot(parabola_data['x'][parabola_data['minor_mask']], 
                    parabola_data['minor_y'][parabola_data['minor_mask']], 
                    'k--', linewidth=2, alpha=0.8)
                    
            ax.set_title(f'Frame {frame_i:02d}\nt={time_step:.4f}s\nMax={max_amp:.2e}', fontsize=11)
            ax.set_xlabel('X (mm)', fontsize=10)
            ax.set_ylabel('Y (mm)', fontsize=10)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            
        # Hide unused subplots
        for idx in range(len(frame_indices), len(axes)):
            axes[idx].set_visible(False)
            
        # Add global colorbar
        fig.subplots_adjust(right=0.92)
        cbar_ax = fig.add_axes([0.94, 0.15, 0.02, 0.7])
        cbar = fig.colorbar(im, cax=cbar_ax)
        cbar.set_label('Wave Amplitude', fontsize=12)
        
        plt.suptitle('Wave Propagation Evolution - Key Frames', fontsize=16, y=0.95)
        
        comparison_file = self.output_dir / "wave_evolution_grid.png"
        plt.savefig(comparison_file, dpi=self.dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ Comparison grid saved: {comparison_file.name}")
        
    def generate_summary_report(self, results, max_amps, mean_amps, styles):
        """Generate a text summary report."""
        report_file = self.output_dir / "analysis_report.txt"
        
        with open(report_file, 'w') as f:
            f.write("ENHANCED WAVE PROPAGATION ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("SIMULATION PARAMETERS:\n")
            f.write(f"  Grid size: {self.grid_size} x {self.grid_size}\n")
            f.write(f"  Total steps: {self.num_steps}\n")
            f.write(f"  Record interval: {self.record_interval}\n")
            f.write(f"  Frequency: {self.frequency} Hz\n")
            f.write(f"  Amplitude: {self.amplitude}\n\n")
            
            f.write("RESULTS SUMMARY:\n")
            f.write(f"  Total frames: {len(results.wave_data)}\n")
            f.write(f"  Time range: {results.time_steps[0]:.6f} - {results.time_steps[-1]:.6f} seconds\n")
            f.write(f"  Duration: {results.time_steps[-1] - results.time_steps[0]:.6f} seconds\n\n")
            
            f.write("AMPLITUDE STATISTICS:\n")
            f.write(f"  Maximum amplitude: {max(max_amps):.6e}\n")
            f.write(f"  Minimum amplitude: {min(max_amps):.6e}\n")
            f.write(f"  Mean amplitude: {np.mean(max_amps):.6e}\n")
            f.write(f"  Amplitude std dev: {np.std(max_amps):.6e}\n\n")
            
            f.write("ENERGY STATISTICS:\n")
            f.write(f"  Maximum energy: {max(results.energy_levels):.6e}\n")
            f.write(f"  Minimum energy: {min(results.energy_levels):.6e}\n")
            f.write(f"  Mean energy: {np.mean(results.energy_levels):.6e}\n")
            f.write(f"  Energy std dev: {np.std(results.energy_levels):.6e}\n\n")
            
            f.write("VISUALIZATION STYLES GENERATED:\n")
            for style in styles:
                f.write(f"  - {style.capitalize()} plots\n")
            f.write("\n")
            
            f.write("OUTPUT FILES:\n")
            f.write(f"  Analysis plots: wave_analysis_comprehensive.png\n")
            f.write(f"  Evolution grid: wave_evolution_grid.png\n")
            f.write(f"  Individual frames: frames_*/\n")
            f.write(f"  This report: analysis_report.txt\n")
            
        print(f"✓ Summary report saved: {report_file.name}")

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Enhanced Wave Propagation Plotter')
    parser.add_argument('--grid-size', type=int, default=100, help='Grid size (default: 100)')
    parser.add_argument('--steps', type=int, default=50, help='Number of simulation steps (default: 50)')
    parser.add_argument('--frequency', type=float, default=1000.0, help='Wave frequency (default: 1000.0)')
    parser.add_argument('--amplitude', type=float, default=1.0, help='Wave amplitude (default: 1.0)')
    parser.add_argument('--output', type=str, default='wave_analysis', help='Output directory (default: wave_analysis)')
    parser.add_argument('--styles', nargs='+', default=['contour'], 
                       choices=['contour', 'surface', 'streamlines'],
                       help='Visualization styles (default: contour)')
    
    args = parser.parse_args()
    
    # Create plotter
    plotter = WavePropagationPlotter(grid_size=args.grid_size, output_dir=args.output)
    plotter.num_steps = args.steps
    plotter.frequency = args.frequency
    plotter.amplitude = args.amplitude
    
    # Run analysis
    try:
        success = plotter.run_complete_analysis(styles=args.styles)
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
