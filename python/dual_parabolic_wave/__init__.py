"""
Dual Parabolic Wave Simulation - Python Package
===============================================

A high-performance wave simulation package with Python bindings for C++ core
and modern visualization capabilities using Gradio and Plotly.

This package provides:
- Fast C++ wave equation solver with Python bindings
- Real-time Gradio web interface for interactive simulation
- 3D surface plotting with Plotly
- Scientific visualization tools
- Command-line interface

Example usage:
    >>> import dual_parabolic_wave as dpw
    >>> sim = dpw.Simulation()
    >>> sim.set_frequency(1000)  # 1 kHz
    >>> sim.run_steps(100)
    >>> data = sim.get_wave_data()
    >>> dpw.plot_3d_surface(data)
"""

__version__ = "1.0.0"
__author__ = "Dual Parabolic Wave Team"
__email__ = "info@example.com"

# Import core C++ bindings
try:
    from .core import (
        Point2D,
        SimulationConfig,
        WaveParameters,
        ParabolaConfig,
        Parabola,
        WaveField,
        DualParabolicWaveSimulation,
        calculate_cfl_timestep,
        version as core_version
    )
    _CORE_AVAILABLE = True
except ImportError as e:
    _CORE_AVAILABLE = False
    _CORE_IMPORT_ERROR = str(e)

# Import Python modules
from .simulation import Simulation, SimulationResults
from .visualization import (
    plot_wave_field_2d,
    plot_wave_field_3d,
    create_animation,
    plot_parabola_geometry
)
from .gradio_app import create_app, launch_app
from .utils import (
    export_data,
    load_data,
    calculate_metrics,
    validate_parameters
)

# Export main classes and functions
__all__ = [
    # Core classes (if available)
    "Point2D",
    "SimulationConfig", 
    "WaveParameters",
    "ParabolaConfig",
    "Parabola",
    "WaveField",
    "DualParabolicWaveSimulation",
    
    # Python wrapper classes
    "Simulation",
    "SimulationResults",
    
    # Visualization functions
    "plot_wave_field_2d",
    "plot_wave_field_3d", 
    "create_animation",
    "plot_parabola_geometry",
    
    # App functions
    "create_app",
    "launch_app",
    
    # Utility functions
    "export_data",
    "load_data",
    "calculate_metrics",
    "validate_parameters",
    "calculate_cfl_timestep",
]

def check_installation():
    """Check if the package is properly installed with C++ core."""
    if not _CORE_AVAILABLE:
        print(f"⚠️  C++ core not available: {_CORE_IMPORT_ERROR}")
        print("   The package will work with reduced functionality.")
        print("   To get full performance, please build the C++ extensions.")
        return False
    else:
        print(f"✅ Dual Parabolic Wave package v{__version__} ready!")
        print(f"   C++ core version: {core_version()}")
        return True

def quick_demo():
    """Run a quick demonstration of the package capabilities."""
    print("🌊 Dual Parabolic Wave Simulation - Quick Demo")
    print("=" * 50)
    
    if not _CORE_AVAILABLE:
        print("⚠️  Running in Python-only mode (slower)")
        from .simulation import PythonSimulation
        sim = PythonSimulation()
    else:
        sim = Simulation()
    
    print("Setting up simulation...")
    sim.set_frequency(1000)  # 1 kHz
    sim.set_amplitude(1.0)
    
    print("Running simulation steps...")
    results = sim.run_steps(50)
    
    print(f"✅ Completed {len(results.time_steps)} time steps")
    print(f"   Final time: {results.time_steps[-1]:.6f} seconds")
    print(f"   Max amplitude: {results.max_amplitudes[-1]:.3f}")
    print(f"   Grid size: {sim.get_grid_size()}x{sim.get_grid_size()}")
    
    print("\nTo visualize:")
    print("  >>> import dual_parabolic_wave as dpw")
    print("  >>> dpw.launch_app()  # Launch Gradio web interface")
    
    return results
