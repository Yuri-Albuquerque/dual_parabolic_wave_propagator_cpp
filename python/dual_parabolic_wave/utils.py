"""
Utility functions for the dual parabolic wave simulation package
"""

import json
import numpy as np
import pickle
from typing import Dict, Any, Tuple, List, Union
from pathlib import Path
import warnings


def export_data(results, filename: str, format: str = "json") -> bool:
    """
    Export simulation results to file.
    
    Args:
        results: SimulationResults object
        filename: Output filename
        format: Export format ("json", "pickle", "npz")
        
    Returns:
        Success status
    """
    try:
        filepath = Path(filename)
        
        if format.lower() == "json":
            # Convert numpy arrays to lists for JSON serialization
            export_dict = {
                'metadata': results.metadata,
                'time_steps': results.time_steps,
                'max_amplitudes': results.max_amplitudes,
                'energy_levels': results.energy_levels,
                'wave_data_shape': [len(results.wave_data)] + list(results.wave_data[0].shape) if results.wave_data else [],
                'final_wave_data': results.get_final_wave_data().tolist() if results.wave_data else []
            }
            
            with open(filepath.with_suffix('.json'), 'w') as f:
                json.dump(export_dict, f, indent=2)
                
        elif format.lower() == "pickle":
            with open(filepath.with_suffix('.pkl'), 'wb') as f:
                pickle.dump(results, f)
                
        elif format.lower() == "npz":
            # Save as compressed numpy archive
            save_dict = {
                'time_steps': np.array(results.time_steps),
                'max_amplitudes': np.array(results.max_amplitudes),
                'energy_levels': np.array(results.energy_levels),
            }
            
            # Add wave data arrays
            for i, wave_data in enumerate(results.wave_data):
                save_dict[f'wave_data_{i:04d}'] = wave_data
            
            # Add metadata as JSON string
            save_dict['metadata'] = json.dumps(results.metadata)
            
            np.savez_compressed(filepath.with_suffix('.npz'), **save_dict)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        return True
        
    except Exception as e:
        print(f"Error exporting data: {e}")
        return False


def load_data(filename: str):
    """
    Load simulation results from file.
    
    Args:
        filename: Input filename
        
    Returns:
        Loaded data (format depends on file type)
    """
    filepath = Path(filename)
    
    try:
        if filepath.suffix.lower() == '.json':
            with open(filepath, 'r') as f:
                return json.load(f)
                
        elif filepath.suffix.lower() == '.pkl':
            with open(filepath, 'rb') as f:
                return pickle.load(f)
                
        elif filepath.suffix.lower() == '.npz':
            return np.load(filepath, allow_pickle=True)
            
        else:
            # Try to infer format
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                with open(filepath, 'rb') as f:
                    return pickle.load(f)
                    
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def calculate_metrics(wave_data: np.ndarray) -> Dict[str, float]:
    """
    Calculate various metrics for wave field data.
    
    Args:
        wave_data: 2D numpy array of wave amplitudes
        
    Returns:
        Dictionary of calculated metrics
    """
    metrics = {}
    
    # Basic statistics
    metrics['max_amplitude'] = float(np.max(np.abs(wave_data)))
    metrics['min_amplitude'] = float(np.min(wave_data))
    metrics['mean_amplitude'] = float(np.mean(wave_data))
    metrics['std_amplitude'] = float(np.std(wave_data))
    metrics['rms_amplitude'] = float(np.sqrt(np.mean(wave_data**2)))
    
    # Energy metrics
    metrics['total_energy'] = float(np.sum(wave_data**2))
    metrics['average_energy_density'] = metrics['total_energy'] / wave_data.size
    
    # Spatial distribution metrics
    center_x, center_y = wave_data.shape[0] // 2, wave_data.shape[1] // 2
    metrics['center_amplitude'] = float(wave_data[center_x, center_y])
    
    # Calculate center of mass
    x_indices, y_indices = np.meshgrid(
        np.arange(wave_data.shape[1]), 
        np.arange(wave_data.shape[0])
    )
    total_abs = np.sum(np.abs(wave_data))
    if total_abs > 0:
        metrics['center_of_mass_x'] = float(np.sum(x_indices * np.abs(wave_data)) / total_abs)
        metrics['center_of_mass_y'] = float(np.sum(y_indices * np.abs(wave_data)) / total_abs)
    else:
        metrics['center_of_mass_x'] = center_x
        metrics['center_of_mass_y'] = center_y
    
    # Spread/dispersion metrics
    if total_abs > 0:
        x_spread = np.sqrt(np.sum((x_indices - metrics['center_of_mass_x'])**2 * np.abs(wave_data)) / total_abs)
        y_spread = np.sqrt(np.sum((y_indices - metrics['center_of_mass_y'])**2 * np.abs(wave_data)) / total_abs)
        metrics['spatial_spread_x'] = float(x_spread)
        metrics['spatial_spread_y'] = float(y_spread)
        metrics['spatial_spread_total'] = float(np.sqrt(x_spread**2 + y_spread**2))
    else:
        metrics['spatial_spread_x'] = 0.0
        metrics['spatial_spread_y'] = 0.0
        metrics['spatial_spread_total'] = 0.0
    
    # Frequency domain analysis (if applicable)
    try:
        fft_2d = np.fft.fft2(wave_data)
        power_spectrum = np.abs(fft_2d)**2
        metrics['spectral_peak'] = float(np.max(power_spectrum))
        metrics['spectral_centroid_x'] = float(np.sum(x_indices * power_spectrum) / np.sum(power_spectrum))
        metrics['spectral_centroid_y'] = float(np.sum(y_indices * power_spectrum) / np.sum(power_spectrum))
    except:
        # Skip if FFT fails
        pass
    
    return metrics


def validate_parameters(frequency: float = None, 
                       amplitude: float = None,
                       grid_size: int = None,
                       time_step: float = None) -> Tuple[bool, List[str]]:
    """
    Validate simulation parameters.
    
    Args:
        frequency: Wave frequency in Hz
        amplitude: Wave amplitude
        grid_size: Grid resolution
        time_step: Time step size
        
    Returns:
        (is_valid, list_of_warnings)
    """
    warnings_list = []
    is_valid = True
    
    # Frequency validation
    if frequency is not None:
        if frequency <= 0:
            warnings_list.append("Frequency must be positive")
            is_valid = False
        elif frequency < 10:
            warnings_list.append("Very low frequency (<10 Hz) may not propagate well")
        elif frequency > 10000:
            warnings_list.append("Very high frequency (>10 kHz) may require finer grid resolution")
    
    # Amplitude validation
    if amplitude is not None:
        if amplitude <= 0:
            warnings_list.append("Amplitude must be positive")
            is_valid = False
        elif amplitude > 100:
            warnings_list.append("Very large amplitude may cause numerical instability")
    
    # Grid size validation
    if grid_size is not None:
        if grid_size < 50:
            warnings_list.append("Grid size too small (<50) - results may be inaccurate")
            is_valid = False
        elif grid_size > 1000:
            warnings_list.append("Very large grid size (>1000) will be slow")
        elif grid_size % 2 == 1:
            warnings_list.append("Even grid sizes are recommended for symmetric problems")
    
    # Time step validation
    if time_step is not None:
        if time_step <= 0:
            warnings_list.append("Time step must be positive")
            is_valid = False
        elif time_step > 1e-3:
            warnings_list.append("Large time step may violate CFL stability condition")
    
    return is_valid, warnings_list


def create_parameter_sweep_config(param_name: str, 
                                 start: float, 
                                 end: float, 
                                 num_points: int,
                                 base_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Create configuration for parameter sweep studies.
    
    Args:
        param_name: Name of parameter to sweep
        start: Starting value
        end: Ending value
        num_points: Number of points in sweep
        base_config: Base configuration dictionary
        
    Returns:
        List of configuration dictionaries
    """
    if base_config is None:
        base_config = {
            'grid_size': 300,
            'frequency': 1000.0,
            'amplitude': 1.0,
            'num_steps': 100
        }
    
    configs = []
    param_values = np.linspace(start, end, num_points)
    
    for value in param_values:
        config = base_config.copy()
        config[param_name] = float(value)
        config['sweep_param'] = param_name
        config['sweep_value'] = float(value)
        configs.append(config)
    
    return configs


def benchmark_performance(grid_sizes: List[int] = None, 
                         num_steps: int = 50) -> Dict[str, Any]:
    """
    Benchmark simulation performance across different grid sizes.
    
    Args:
        grid_sizes: List of grid sizes to test
        num_steps: Number of simulation steps for each test
        
    Returns:
        Benchmark results dictionary
    """
    if grid_sizes is None:
        grid_sizes = [100, 200, 300, 400, 500]
    
    # Import here to avoid circular imports
    from .simulation import Simulation
    import time
    
    results = {
        'grid_sizes': [],
        'execution_times': [],
        'steps_per_second': [],
        'memory_usage': [],
        'use_core': [],
        'num_steps': num_steps
    }
    
    for grid_size in grid_sizes:
        print(f"Benchmarking grid size {grid_size}...")
        
        try:
            # Test with C++ core if available
            sim = Simulation(grid_size=grid_size, use_core=True)
            sim.set_frequency(1000.0)
            sim.set_amplitude(1.0)
            
            start_time = time.time()
            test_results = sim.run_steps(num_steps, record_interval=num_steps)
            end_time = time.time()
            
            execution_time = end_time - start_time
            steps_per_sec = num_steps / execution_time
            
            results['grid_sizes'].append(grid_size)
            results['execution_times'].append(execution_time)
            results['steps_per_second'].append(steps_per_sec)
            results['use_core'].append(sim.use_core)
            
            # Estimate memory usage (rough approximation)
            memory_mb = (grid_size**2 * 8 * 3) / (1024**2)  # 3 double arrays
            results['memory_usage'].append(memory_mb)
            
        except Exception as e:
            print(f"Error benchmarking grid size {grid_size}: {e}")
            continue
    
    # Add summary statistics
    if results['execution_times']:
        results['fastest_grid'] = results['grid_sizes'][np.argmax(results['steps_per_second'])]
        results['slowest_grid'] = results['grid_sizes'][np.argmin(results['steps_per_second'])]
        results['speedup_ratio'] = max(results['steps_per_second']) / min(results['steps_per_second'])
    
    return results


def generate_test_data(grid_size: int = 300, 
                      wave_type: str = "gaussian") -> np.ndarray:
    """
    Generate test wave data for visualization testing.
    
    Args:
        grid_size: Size of the grid
        wave_type: Type of test pattern ("gaussian", "sine", "interference")
        
    Returns:
        2D numpy array of test wave data
    """
    x = np.linspace(-300, 300, grid_size)
    y = np.linspace(-300, 300, grid_size)
    X, Y = np.meshgrid(x, y)
    
    if wave_type == "gaussian":
        # Gaussian pulse
        sigma = 50.0
        amplitude = 1.0
        wave_data = amplitude * np.exp(-(X**2 + Y**2) / (2 * sigma**2))
        
    elif wave_type == "sine":
        # Sinusoidal pattern
        wavelength = 100.0
        k = 2 * np.pi / wavelength
        wave_data = np.sin(k * X) * np.sin(k * Y)
        
    elif wave_type == "interference":
        # Two-source interference pattern
        x1, y1 = -100, 0
        x2, y2 = 100, 0
        r1 = np.sqrt((X - x1)**2 + (Y - y1)**2)
        r2 = np.sqrt((X - x2)**2 + (Y - y2)**2)
        k = 0.1
        wave_data = np.cos(k * r1) + np.cos(k * r2)
        
    else:
        # Default: radial wave
        r = np.sqrt(X**2 + Y**2)
        k = 0.05
        wave_data = np.cos(k * r) * np.exp(-r / 200.0)
    
    return wave_data


def print_system_info():
    """Print system information and package status."""
    import platform
    import sys
    
    print("🌊 Dual Parabolic Wave Simulation - System Information")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()[0]}")
    print(f"Processor: {platform.processor()}")
    
    # Check package dependencies
    dependencies = {
        'numpy': 'numpy',
        'matplotlib': 'matplotlib', 
        'plotly': 'plotly',
        'gradio': 'gradio',
        'scipy': 'scipy'
    }
    
    print("\n📦 Package Dependencies:")
    for name, import_name in dependencies.items():
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✅ {name}: {version}")
        except ImportError:
            print(f"  ❌ {name}: Not installed")
    
    # Check C++ core availability
    try:
        from . import _CORE_AVAILABLE
        if _CORE_AVAILABLE:
            print("\n⚡ C++ Core: ✅ Available")
        else:
            print("\n⚡ C++ Core: ❌ Not available (using Python fallback)")
    except:
        print("\n⚡ C++ Core: ❓ Unknown status")
    
    print("\n" + "=" * 60)
