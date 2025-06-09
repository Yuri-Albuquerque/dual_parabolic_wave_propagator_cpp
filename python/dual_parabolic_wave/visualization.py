"""
Advanced visualization tools for dual parabolic wave simulation
"""

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Tuple, Optional, Dict, Any
import matplotlib.animation as animation
from matplotlib.colors import Normalize
import matplotlib.cm as cm


def plot_wave_field_2d(wave_data: np.ndarray, 
                      title: str = "Wave Field",
                      colormap: str = "RdBu_r",
                      figsize: Tuple[int, int] = (10, 8),
                      show_colorbar: bool = True,
                      vmin: Optional[float] = None,
                      vmax: Optional[float] = None) -> plt.Figure:
    """
    Create a 2D matplotlib plot of the wave field.
    
    Args:
        wave_data: 2D numpy array of wave amplitudes
        title: Plot title
        colormap: Matplotlib colormap name
        figsize: Figure size (width, height)
        show_colorbar: Whether to show colorbar
        vmin, vmax: Color scale limits
        
    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Auto-scale if not provided
    if vmin is None:
        vmin = -np.max(np.abs(wave_data))
    if vmax is None:
        vmax = np.max(np.abs(wave_data))
    
    # Create the plot
    im = ax.imshow(wave_data, cmap=colormap, origin='lower', 
                   vmin=vmin, vmax=vmax, extent=[-300, 300, -300, 300])
    
    ax.set_xlabel('X Position (mm)')
    ax.set_ylabel('Y Position (mm)')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    if show_colorbar:
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Wave Amplitude')
    
    return fig


def plot_wave_field_3d(wave_data: np.ndarray,
                       title: str = "3D Wave Field Surface",
                       colorscale: str = "RdBu",
                       show_contours: bool = True,
                       opacity: float = 0.8) -> go.Figure:
    """
    Create an interactive 3D surface plot using Plotly.
    
    Args:
        wave_data: 2D numpy array of wave amplitudes
        title: Plot title
        colorscale: Plotly colorscale name
        show_contours: Whether to show contour lines
        opacity: Surface opacity (0-1)
        
    Returns:
        Plotly Figure object
    """
    grid_size = wave_data.shape[0]
    
    # Create coordinate grids
    x = np.linspace(-300, 300, grid_size)
    y = np.linspace(-300, 300, grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Create the surface plot
    fig = go.Figure(data=[
        go.Surface(
            x=X, y=Y, z=wave_data,
            colorscale=colorscale,
            opacity=opacity,
            showscale=True,
            colorbar=dict(title="Wave Amplitude"),
            contours=dict(
                z=dict(show=show_contours, usecolormap=True, highlightcolor="limegreen", project_z=True)
            ) if show_contours else {}
        )
    ])
    
    # Update layout
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='X Position (mm)',
            yaxis_title='Y Position (mm)',
            zaxis_title='Wave Amplitude',
            camera=dict(eye=dict(x=1.2, y=1.2, z=0.8))
        ),
        width=800,
        height=600
    )
    
    return fig


def plot_parabola_geometry(grid_size: int = 300) -> go.Figure:
    """
    Plot the parabolic geometry of the dual cavity system.
    
    Args:
        grid_size: Resolution for the geometry visualization
        
    Returns:
        Plotly Figure object
    """
    # Create coordinate grids
    x = np.linspace(-300, 300, grid_size)
    y = np.linspace(-300, 300, grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Major parabola (umbrella) - 20 inch diameter, concave down, 100mm focus
    major_diameter = 20 * 25.4  # 508mm
    major_focus = 100.0  # mm
    major_vertex_y = major_focus  # Focus at origin, vertex above
    
    # Minor parabola (bowl) - 100mm diameter, concave up, 50mm focus  
    minor_diameter = 100.0  # mm
    minor_focus = 50.0  # mm
    minor_vertex_y = -minor_focus  # Focus at origin, vertex below
    
    # Calculate parabola surfaces
    # For parabola y = ax² + bx + c with focus at (0,f), vertex at (0,v)
    # The equation is (x-h)² = 4p(y-k) where (h,k) is vertex and p is focal parameter
    
    # Major parabola (inverted)
    major_p = -major_focus  # Negative for downward opening
    major_z = np.zeros_like(X)
    mask_major = (X**2 + Y**2) <= (major_diameter/2)**2
    major_z[mask_major] = major_vertex_y + (X[mask_major]**2 + Y[mask_major]**2) / (4 * abs(major_p))
    
    # Minor parabola (upward)
    minor_p = minor_focus  # Positive for upward opening
    minor_z = np.zeros_like(X)
    mask_minor = (X**2 + Y**2) <= (minor_diameter/2)**2
    minor_z[mask_minor] = minor_vertex_y + (X[mask_minor]**2 + Y[mask_minor]**2) / (4 * minor_p)
    
    # Create the plot
    fig = go.Figure()
    
    # Major parabola surface
    fig.add_trace(go.Surface(
        x=X, y=Y, z=major_z,
        colorscale='Blues',
        opacity=0.7,
        name='Major Parabola (Umbrella)',
        showscale=False
    ))
    
    # Minor parabola surface  
    fig.add_trace(go.Surface(
        x=X, y=Y, z=minor_z,
        colorscale='Reds',
        opacity=0.7,
        name='Minor Parabola (Bowl)',
        showscale=False
    ))
    
    # Focus points
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=10, color='gold', symbol='circle'),
        name='Coincident Focus'
    ))
    
    # Update layout
    fig.update_layout(
        title='Dual Parabolic Cavity Geometry',
        scene=dict(
            xaxis_title='X Position (mm)',
            yaxis_title='Y Position (mm)', 
            zaxis_title='Z Position (mm)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0)),
            aspectmode='cube'
        ),
        width=900,
        height=700
    )
    
    return fig


def create_animation(wave_data_list: List[np.ndarray],
                    time_steps: List[float],
                    title: str = "Wave Propagation Animation",
                    interval: int = 100,
                    colormap: str = "RdBu_r") -> animation.FuncAnimation:
    """
    Create an animated visualization of wave propagation.
    
    Args:
        wave_data_list: List of 2D wave field arrays
        time_steps: Corresponding time values
        title: Animation title
        interval: Delay between frames in milliseconds
        colormap: Matplotlib colormap
        
    Returns:
        matplotlib FuncAnimation object
    """
    if not wave_data_list:
        raise ValueError("No wave data provided")
    
    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Determine global color scale
    vmin = min(np.min(data) for data in wave_data_list)
    vmax = max(np.max(data) for data in wave_data_list)
    v_abs_max = max(abs(vmin), abs(vmax))
    
    # Initial plot
    im = ax.imshow(wave_data_list[0], cmap=colormap, origin='lower',
                   vmin=-v_abs_max, vmax=v_abs_max, 
                   extent=[-300, 300, -300, 300])
    
    ax.set_xlabel('X Position (mm)')
    ax.set_ylabel('Y Position (mm)')
    title_text = ax.set_title(f'{title} - t = {time_steps[0]:.6f} s')
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Wave Amplitude')
    
    def animate(frame):
        """Animation function."""
        im.set_array(wave_data_list[frame])
        title_text.set_text(f'{title} - t = {time_steps[frame]:.6f} s')
        return [im, title_text]
    
    # Create animation
    anim = animation.FuncAnimation(
        fig, animate, frames=len(wave_data_list),
        interval=interval, blit=True, repeat=True
    )
    
    return anim


def plot_metrics_dashboard(results, figsize: Tuple[int, int] = (15, 10)) -> plt.Figure:
    """
    Create a comprehensive dashboard of simulation metrics.
    
    Args:
        results: SimulationResults object
        figsize: Figure size
        
    Returns:
        matplotlib Figure with subplots
    """
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle('Simulation Analysis Dashboard', fontsize=16)
    
    # Time series plots
    times = np.array(results.time_steps)
    
    # Max amplitude over time
    axes[0, 0].plot(times * 1000, results.max_amplitudes, 'b-', linewidth=2)
    axes[0, 0].set_xlabel('Time (ms)')
    axes[0, 0].set_ylabel('Max Amplitude')
    axes[0, 0].set_title('Maximum Amplitude vs Time')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Energy over time
    axes[0, 1].plot(times * 1000, results.energy_levels, 'r-', linewidth=2)
    axes[0, 1].set_xlabel('Time (ms)')
    axes[0, 1].set_ylabel('Total Energy')
    axes[0, 1].set_title('Energy Evolution')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Final wave field
    if results.wave_data:
        final_data = results.wave_data[-1]
        im = axes[0, 2].imshow(final_data, cmap='RdBu_r', origin='lower',
                              extent=[-300, 300, -300, 300])
        axes[0, 2].set_xlabel('X (mm)')
        axes[0, 2].set_ylabel('Y (mm)')
        axes[0, 2].set_title('Final Wave Field')
        plt.colorbar(im, ax=axes[0, 2])
    
    # Amplitude histogram
    if results.wave_data:
        all_amplitudes = np.concatenate([data.flatten() for data in results.wave_data])
        axes[1, 0].hist(all_amplitudes, bins=50, alpha=0.7, density=True)
        axes[1, 0].set_xlabel('Amplitude')
        axes[1, 0].set_ylabel('Probability Density')
        axes[1, 0].set_title('Amplitude Distribution')
        axes[1, 0].grid(True, alpha=0.3)
    
    # Time series at center point
    if results.wave_data:
        center = len(results.wave_data[0]) // 2
        center_amplitudes = [data[center, center] for data in results.wave_data]
        axes[1, 1].plot(times * 1000, center_amplitudes, 'g-', linewidth=2)
        axes[1, 1].set_xlabel('Time (ms)')
        axes[1, 1].set_ylabel('Amplitude at Center')
        axes[1, 1].set_title('Center Point Time Series')
        axes[1, 1].grid(True, alpha=0.3)
    
    # Metadata table
    axes[1, 2].axis('off')
    if results.metadata:
        metadata_text = []
        for key, value in results.metadata.items():
            if isinstance(value, float):
                metadata_text.append(f"{key}: {value:.4g}")
            else:
                metadata_text.append(f"{key}: {value}")
        
        axes[1, 2].text(0.05, 0.95, '\n'.join(metadata_text),
                       transform=axes[1, 2].transAxes,
                       verticalalignment='top',
                       fontfamily='monospace',
                       fontsize=10)
        axes[1, 2].set_title('Simulation Metadata')
    
    plt.tight_layout()
    return fig


def create_interactive_surface_plot(wave_data: np.ndarray,
                                   title: str = "Interactive Wave Surface") -> go.Figure:
    """
    Create an interactive 3D surface with additional controls.
    
    Args:
        wave_data: 2D wave field data
        title: Plot title
        
    Returns:
        Enhanced Plotly figure with controls
    """
    grid_size = wave_data.shape[0]
    x = np.linspace(-300, 300, grid_size)
    y = np.linspace(-300, 300, grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Create surface
    fig = go.Figure()
    
    # Main surface
    fig.add_trace(go.Surface(
        x=X, y=Y, z=wave_data,
        colorscale='RdBu',
        name='Wave Field',
        colorbar=dict(title="Amplitude", x=1.1)
    ))
    
    # Add contour projection
    fig.add_trace(go.Contour(
        x=x, y=y, z=wave_data,
        colorscale='RdBu',
        opacity=0.3,
        showscale=False,
        contours=dict(
            z=dict(start=np.min(wave_data), end=np.max(wave_data), size=(np.max(wave_data)-np.min(wave_data))/20)
        )
    ))
    
    # Update layout with enhanced controls
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='X Position (mm)',
            yaxis_title='Y Position (mm)',
            zaxis_title='Wave Amplitude',
            camera=dict(
                eye=dict(x=1.2, y=1.2, z=0.8),
                center=dict(x=0, y=0, z=0)
            ),
            aspectmode='cube'
        ),
        width=1000,
        height=700,
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=list([
                    dict(label="Top View",
                         method="relayout",
                         args=[{"scene.camera.eye": dict(x=0, y=0, z=2)}]),
                    dict(label="Side View",
                         method="relayout", 
                         args=[{"scene.camera.eye": dict(x=2, y=0, z=0)}]),
                    dict(label="3D View",
                         method="relayout",
                         args=[{"scene.camera.eye": dict(x=1.2, y=1.2, z=0.8)}])
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.01,
                xanchor="left",
                y=1.02,
                yanchor="top"
            ),
        ]
    )
    
    return fig
