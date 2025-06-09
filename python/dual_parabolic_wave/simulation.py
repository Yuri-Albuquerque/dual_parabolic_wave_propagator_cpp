"""
High-level simulation interface for Dual Parabolic Wave Simulation
"""

import numpy as np
import time
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field

try:
    from .core import DualParabolicWaveSimulation as CoreSimulation
    _CORE_AVAILABLE = True
except ImportError:
    _CORE_AVAILABLE = False


@dataclass
class SimulationResults:
    """Container for simulation results and metadata."""
    wave_data: List[np.ndarray] = field(default_factory=list)
    time_steps: List[float] = field(default_factory=list)
    max_amplitudes: List[float] = field(default_factory=list)
    energy_levels: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_final_wave_data(self) -> np.ndarray:
        """Get the final wave field data."""
        return self.wave_data[-1] if self.wave_data else np.array([])
    
    def get_time_series(self, x: int, y: int) -> Tuple[np.ndarray, np.ndarray]:
        """Get time series data for a specific grid point."""
        if not self.wave_data:
            return np.array([]), np.array([])
        
        amplitudes = [data[x, y] for data in self.wave_data]
        return np.array(self.time_steps), np.array(amplitudes)


class Simulation:
    """High-level interface for the dual parabolic wave simulation."""
    
    def __init__(self, grid_size: int = 300, use_core: bool = True):
        """
        Initialize the simulation.
        
        Args:
            grid_size: Grid resolution (grid_size x grid_size)
            use_core: Whether to use C++ core (if available)
        """
        self.grid_size = grid_size
        self.use_core = use_core and _CORE_AVAILABLE
        self.current_time = 0.0
        self.step_count = 0
        
        if self.use_core:
            self._core_sim = CoreSimulation()
            self.cfl_timestep = self._core_sim.getCFLTimeStep()
        else:
            self._core_sim = None
            self.cfl_timestep = self._calculate_python_timestep()
            self._init_python_simulation()
    
    def _calculate_python_timestep(self) -> float:
        """Calculate CFL timestep for Python simulation."""
        # Simulation domain: -300 to 300 mm in both directions
        domain_size = 600.0  # mm
        dx = domain_size / self.grid_size
        dy = dx
        speed = 343000.0  # mm/s (speed of sound)
        return 0.4 * min(dx, dy) / (speed * np.sqrt(2.0))
    
    def _init_python_simulation(self):
        """Initialize Python-only simulation (fallback)."""
        # Create wave field arrays
        self.wave_current = np.zeros((self.grid_size, self.grid_size))
        self.wave_previous = np.zeros((self.grid_size, self.grid_size))
        self.wave_next = np.zeros((self.grid_size, self.grid_size))
        
        # Simulation parameters
        self.frequency = 1000.0  # Hz
        self.amplitude = 1.0
        self.speed = 343000.0  # mm/s
        
        # Grid parameters
        self.x_min = -300.0
        self.x_max = 300.0
        self.y_min = -300.0
        self.y_max = 300.0
        self.dx = (self.x_max - self.x_min) / self.grid_size
        self.dy = (self.y_max - self.y_min) / self.grid_size
    
    def set_frequency(self, frequency: float):
        """Set wave frequency in Hz."""
        if self.use_core:
            self._core_sim.setFrequency(frequency)
        else:
            self.frequency = frequency
    
    def set_amplitude(self, amplitude: float):
        """Set wave amplitude."""
        if self.use_core:
            self._core_sim.setAmplitude(amplitude)
        else:
            self.amplitude = amplitude
    
    def reset(self):
        """Reset simulation to initial state."""
        if self.use_core:
            self._core_sim.reset()
        else:
            self.wave_current.fill(0.0)
            self.wave_previous.fill(0.0)
            self.wave_next.fill(0.0)
        
        self.current_time = 0.0
        self.step_count = 0
    
    def step(self) -> np.ndarray:
        """Advance simulation by one time step."""
        if self.use_core:
            self._core_sim.update(self.cfl_timestep)
            self.current_time = self._core_sim.getCurrentTime()
            self.step_count += 1
            return self._core_sim.getWaveFieldData()
        else:
            return self._python_step()
    
    def _python_step(self) -> np.ndarray:
        """Python implementation of wave equation step."""
        dt = self.cfl_timestep
        c2 = self.speed ** 2
        
        # Add source at center (focus point)
        center_x = self.grid_size // 2
        center_y = self.grid_size // 2
        
        # Single pulse using Morlet wavelet at initial time
        # Morlet wavelet: ψ(t) = π^(-1/4) * exp(-t²/2) * exp(iσt)
        # For real-valued version: ψ(t) = π^(-1/4) * exp(-t²/2) * cos(σt)
        
        sigma = 2 * np.pi * self.frequency  # Angular frequency
        pulse_center = 1.0 / self.frequency  # Center time (1 period - earlier start)
        pulse_duration = 4.0 / self.frequency  # Total duration (4 periods for better localization)
        
        source_value = 0.0
        if self.current_time <= pulse_duration:
            # Morlet wavelet centered at pulse_center
            t_shifted = self.current_time - pulse_center
            
            # Enhanced Morlet wavelet formula with better scaling
            normalization = np.pi ** (-0.25)  # Normalization constant
            
            # Scale the time for better envelope
            time_scale = self.frequency / 1000.0  # Normalize by reference frequency
            scaled_t = t_shifted * time_scale
            
            gaussian_envelope = np.exp(-0.5 * scaled_t ** 2)
            complex_exponential = np.cos(sigma * t_shifted)  # Real part of exp(iσt)
            
            # Complete Morlet wavelet
            morlet_value = normalization * gaussian_envelope * complex_exponential
            
            # Much stronger source amplitude for better visibility
            source_amplitude = self.amplitude * 1000.0  # Increased from 10.0 to 1000.0
            source_value = source_amplitude * morlet_value
        
        # Wave equation with finite differences
        for i in range(1, self.grid_size - 1):
            for j in range(1, self.grid_size - 1):
                # Second derivatives
                d2u_dx2 = (self.wave_current[i+1, j] - 2*self.wave_current[i, j] + self.wave_current[i-1, j]) / (self.dx**2)
                d2u_dy2 = (self.wave_current[i, j+1] - 2*self.wave_current[i, j] + self.wave_current[i, j-1]) / (self.dy**2)
                
                # Wave equation: d²u/dt² = c²(d²u/dx² + d²u/dy²)
                acceleration = c2 * (d2u_dx2 + d2u_dy2)
                
                # Add source
                if i == center_x and j == center_y:
                    acceleration += source_value * 10000.0  # Much stronger source (increased from 1000.0)
                
                # Time integration (Verlet method)
                self.wave_next[i, j] = (2 * self.wave_current[i, j] - self.wave_previous[i, j] + 
                                       acceleration * dt**2)
        
        # Boundary conditions (absorbing)
        self.wave_next[0, :] = 0
        self.wave_next[-1, :] = 0
        self.wave_next[:, 0] = 0
        self.wave_next[:, -1] = 0
        
        # Update arrays
        self.wave_previous, self.wave_current, self.wave_next = (
            self.wave_current, self.wave_next, self.wave_previous
        )
        
        self.current_time += dt
        self.step_count += 1
        
        return self.wave_current.copy()
    
    def run_steps(self, num_steps: int, record_interval: int = 1) -> SimulationResults:
        """
        Run multiple simulation steps and record results.
        
        Args:
            num_steps: Number of simulation steps to run
            record_interval: Record data every N steps
            
        Returns:
            SimulationResults containing wave data and metadata
        """
        results = SimulationResults()
        
        start_time = time.time()
        
        for step in range(num_steps):
            wave_data = self.step()
            
            if step % record_interval == 0:
                results.wave_data.append(wave_data.copy())
                results.time_steps.append(self.current_time)
                results.max_amplitudes.append(np.max(np.abs(wave_data)))
                results.energy_levels.append(np.sum(wave_data**2))
        
        end_time = time.time()
        
        # Store metadata
        results.metadata = {
            'grid_size': self.grid_size,
            'total_steps': num_steps,
            'record_interval': record_interval,
            'execution_time': end_time - start_time,
            'steps_per_second': num_steps / (end_time - start_time),
            'cfl_timestep': self.cfl_timestep,
            'final_time': self.current_time,
            'use_core': self.use_core,
            'frequency': self.get_frequency(),
            'amplitude': self.get_amplitude(),
        }
        
        return results
    
    def get_wave_data(self) -> np.ndarray:
        """Get current wave field data."""
        if self.use_core:
            return self._core_sim.getWaveFieldData()
        else:
            return self.wave_current.copy()
    
    def get_grid_size(self) -> int:
        """Get grid size."""
        return self.grid_size
    
    def get_current_time(self) -> float:
        """Get current simulation time."""
        return self.current_time
    
    def get_step_count(self) -> int:
        """Get number of steps executed."""
        return self.step_count
    
    def get_frequency(self) -> float:
        """Get current frequency."""
        if self.use_core:
            return self._core_sim.getWaveParams().frequency
        else:
            return self.frequency
    
    def get_amplitude(self) -> float:
        """Get current amplitude."""
        if self.use_core:
            return self._core_sim.getWaveParams().amplitude
        else:
            return self.amplitude
    
    def get_simulation_info(self) -> Dict[str, Any]:
        """Get comprehensive simulation information."""
        return {
            'grid_size': self.grid_size,
            'current_time': self.current_time,
            'step_count': self.step_count,
            'cfl_timestep': self.cfl_timestep,
            'frequency': self.get_frequency(),
            'amplitude': self.get_amplitude(),
            'use_core': self.use_core,
            'core_available': _CORE_AVAILABLE,
        }


class PythonSimulation(Simulation):
    """Force Python-only simulation (for testing/fallback)."""
    
    def __init__(self, grid_size: int = 300):
        super().__init__(grid_size=grid_size, use_core=False)
