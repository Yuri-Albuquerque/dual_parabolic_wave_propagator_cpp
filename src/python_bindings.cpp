#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <pybind11/eigen.h>
#include "DualParabolicWaveSimulation.h"
#include "WaveField.h"
#include "Types.h"

namespace py = pybind11;
using namespace WaveSimulation;

// Helper function to extract wave field data as numpy array
py::array_t<float> getWaveFieldData(const WaveField& waveField) {
    const auto& grid = waveField.getGrid();
    int gridSize = waveField.getGridSize();
    
    // Create numpy array with shape (gridSize, gridSize)
    py::array_t<float> result = py::array_t<float>(
        {gridSize, gridSize},
        {sizeof(float) * gridSize, sizeof(float)},
        grid.data()
    );
    
    return result;
}

// Helper function to get parabola boundary mask
py::array_t<int> getBoundaryMask(const WaveField& waveField) {
    const auto& mask = waveField.getBoundaryMask();
    int gridSize = waveField.getGridSize();
    
    py::array_t<int> result = py::array_t<int>(
        {gridSize, gridSize},
        {sizeof(int) * gridSize, sizeof(int)},
        mask.data()
    );
    
    return result;
}

// Ground truth compatible wave solver function
py::array_t<float> solve_dual_parabolic_wave(
    py::array_t<double> parameters,
    py::array_t<float> initial_field,
    py::array_t<float> velocity_field,
    py::array_t<float> damping_field,
    py::array_t<float> source_field,
    int num_time_steps) {
    
    auto par = parameters.unchecked<1>();
    
    // Extract parameters (matching ground truth format)
    double xMin = par(0);
    double xMax = par(1);
    double zMin = par(2);  // Using z for y in 2D
    double zMax = par(3);
    double tMin = par(4);
    double tMax = par(5);
    double hx = par(6);
    double hz = par(7);
    double ht = par(8);
    
    // Calculate grid size from domain and spacing
    int nx = static_cast<int>((xMax - xMin) / hx) + 1;
    int nz = static_cast<int>((zMax - zMin) / hz) + 1;
    
    // Calculate wave speed from velocity field (c = 1/sqrt(rho), assuming rho from velocity)
    double waveSpeed = 343.0; // Default speed of sound in air (m/s)
    
    // Create simulation
    DualParabolicWaveSimulation simulation(
        nx,                    // gridSize
        xMax - xMin,          // domainSize
        waveSpeed,            // waveSpeed
        ht,                   // timeStep (will be overridden by CFL)
        1.0                   // simulationSpeed
    );
    
    // Run simulation for specified number of time steps
    const WaveField& waveField = simulation.getWaveField();
    int gridSize = waveField.getGridSize();
    
    // Prepare output array: (nz, nx, nt)
    py::array_t<float> result = py::array_t<float>({nz, nx, num_time_steps});
    auto result_ptr = static_cast<float*>(result.mutable_unchecked<3>().mutable_data(0, 0, 0));
    
    // Run simulation and store snapshots
    for (int t = 0; t < num_time_steps; t++) {
        if (t > 0) {
            simulation.update();
        }
        
        // Copy current wave field to result
        const auto& grid = waveField.getGrid();
        for (int i = 0; i < nz && i < gridSize; i++) {
            for (int j = 0; j < nx && j < gridSize; j++) {
                int srcIndex = i * gridSize + j;
                int dstIndex = i * nx * num_time_steps + j * num_time_steps + t;
                result_ptr[dstIndex] = grid[srcIndex];
            }
        }
    }
    
    return result;
}

PYBIND11_MODULE(dual_parabolic_wave_cpp, m) {
    m.doc() = R"pbdoc(
        Dual Parabolic Wave Simulation - Python Bindings
        ================================================
        
        This module provides Python bindings for the C++ dual parabolic wave
        simulation that implements the ground truth solve_wv function for
        acoustic wave propagation between parabolic reflectors.
        
        Features:
        - Ground truth acoustic wave PDE solver: ρ∂²u/∂t² - η∂u/∂t + ∇·∇u = f
        - Dual parabolic reflector system (508mm major, 200mm minor)
        - Coincident focus points for optimal wave focusing
        - CFL-stable time stepping
        - Rigid boundary conditions at parabolic surfaces
    )pbdoc";
    
    // Expose Point2D class
    py::class_<Point2D>(m, "Point2D")
        .def(py::init<double, double>())
        .def_readwrite("x", &Point2D::x)
        .def_readwrite("y", &Point2D::y);
    
    // Expose SimulationConfig struct
    py::class_<SimulationConfig>(m, "SimulationConfig")
        .def(py::init<>())
        .def_readwrite("gridSize", &SimulationConfig::gridSize)
        .def_readwrite("xMin", &SimulationConfig::xMin)
        .def_readwrite("xMax", &SimulationConfig::xMax)
        .def_readwrite("yMin", &SimulationConfig::yMin)
        .def_readwrite("yMax", &SimulationConfig::yMax)
        .def_readwrite("timeStep", &SimulationConfig::timeStep)
        .def_readwrite("dampingFactor", &SimulationConfig::dampingFactor)
        .def_readwrite("reflectionCoeff", &SimulationConfig::reflectionCoeff);
    
    // Expose WaveParams struct
    py::class_<WaveParams>(m, "WaveParams")
        .def(py::init<>())
        .def_readwrite("frequency", &WaveParams::frequency)
        .def_readwrite("wavelength", &WaveParams::wavelength)
        .def_readwrite("speed", &WaveParams::speed)
        .def_readwrite("amplitude", &WaveParams::amplitude);
    
    // Expose WaveField class
    py::class_<WaveField>(m, "WaveField")
        .def("getGridSize", &WaveField::getGridSize)
        .def("getTime", &WaveField::getTime)
        .def("update", &WaveField::update)
        .def("reset", &WaveField::reset)
        .def("setFrequency", &WaveField::setFrequency)
        .def("setAmplitude", &WaveField::setAmplitude);
    
    // Expose main simulation class
    py::class_<DualParabolicWaveSimulation>(m, "DualParabolicWaveSimulation")
        .def(py::init<>())
        .def(py::init<int, double, double, double, double>(),
             py::arg("gridSize"), py::arg("domainSize"), py::arg("waveSpeed"), 
             py::arg("timeStep"), py::arg("simulationSpeed"))
        .def("update", py::overload_cast<>(&DualParabolicWaveSimulation::update))
        .def("update", py::overload_cast<double>(&DualParabolicWaveSimulation::update))
        .def("reset", &DualParabolicWaveSimulation::reset)
        .def("setFrequency", &DualParabolicWaveSimulation::setFrequency)
        .def("setAmplitude", &DualParabolicWaveSimulation::setAmplitude)
        .def("initialize", &DualParabolicWaveSimulation::initialize)
        .def("getGridSize", &DualParabolicWaveSimulation::getGridSize)
        .def("getDomainSize", &DualParabolicWaveSimulation::getDomainSize)
        .def("getWaveSpeed", &DualParabolicWaveSimulation::getWaveSpeed)
        .def("getTimeStep", &DualParabolicWaveSimulation::getTimeStep)
        .def("getWaveField", &DualParabolicWaveSimulation::getWaveField,
             py::return_value_policy::reference_internal);
    
    // Helper functions for numpy integration
    m.def("getWaveFieldData", &getWaveFieldData, 
          "Extract wave field data as numpy array",
          py::arg("waveField"));
    
    m.def("getBoundaryMask", &getBoundaryMask,
          "Get parabolic boundary mask as numpy array", 
          py::arg("waveField"));
    
    // Ground truth compatible solver function
    m.def("solve_dual_parabolic_wave", &solve_dual_parabolic_wave,
          R"pbdoc(
          Ground truth compatible wave solver for dual parabolic system.
          
          This function matches the interface of the original solve_wv function
          but implements wave propagation between parabolic reflectors.
          
          Parameters:
          - parameters: Array with [xMin, xMax, zMin, zMax, tMin, tMax, hx, hz, ht]
          - initial_field: Initial wave field (not used, starts from zero)
          - velocity_field: Velocity field (not used, uses constant wave speed)
          - damping_field: Damping field (minimal damping applied)
          - source_field: Source field (Morlet wavelet at focus point)
          - num_time_steps: Number of time steps to simulate
          
          Returns:
          - Wave field evolution as (nz, nx, nt) numpy array
          )pbdoc",
          py::arg("parameters"), py::arg("initial_field"), py::arg("velocity_field"),
          py::arg("damping_field"), py::arg("source_field"), py::arg("num_time_steps"));

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
