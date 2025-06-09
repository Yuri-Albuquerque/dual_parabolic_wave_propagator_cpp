#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <pybind11/eigen.h>
#include <memory>
#include <vector>

#include "../include/DualParabolicWaveSimulation.h"
#include "../include/WaveField.h"
#include "../include/Parabola.h"
#include "../include/Types.h"

namespace py = pybind11;
using namespace WaveSimulation;

PYBIND11_MODULE(core, m) {
    m.doc() = "Dual Parabolic Wave Simulation - Python bindings";

    // Point2D binding
    py::class_<Point2D>(m, "Point2D")
        .def(py::init<double, double>())
        .def_readwrite("x", &Point2D::x)
        .def_readwrite("y", &Point2D::y)
        .def("__repr__", [](const Point2D& p) {
            return "Point2D(x=" + std::to_string(p.x) + ", y=" + std::to_string(p.y) + ")";
        });

    // SimulationConfig binding
    py::class_<SimulationConfig>(m, "SimulationConfig")
        .def(py::init<>())
        .def_readwrite("gridSize", &SimulationConfig::gridSize)
        .def_readwrite("xMin", &SimulationConfig::xMin)
        .def_readwrite("xMax", &SimulationConfig::xMax)
        .def_readwrite("yMin", &SimulationConfig::yMin)
        .def_readwrite("yMax", &SimulationConfig::yMax)
        .def_readwrite("timeStep", &SimulationConfig::timeStep)
        .def_readwrite("dampingFactor", &SimulationConfig::dampingFactor);

    // WaveParameters binding
    py::class_<WaveParameters>(m, "WaveParameters")
        .def(py::init<>())
        .def_readwrite("speed", &WaveParameters::speed)
        .def_readwrite("frequency", &WaveParameters::frequency)
        .def_readwrite("amplitude", &WaveParameters::amplitude);

    // ParabolaConfig binding
    py::class_<ParabolaConfig>(m, "ParabolaConfig")
        .def(py::init<>())
        .def_readwrite("vertex", &ParabolaConfig::vertex)
        .def_readwrite("focus", &ParabolaConfig::focus)
        .def_readwrite("diameter", &ParabolaConfig::diameter)
        .def_readwrite("isInverted", &ParabolaConfig::isInverted);

    // Parabola binding
    py::class_<Parabola>(m, "Parabola")
        .def(py::init<const ParabolaConfig&>())
        .def("isPointInside", &Parabola::isPointInside)
        .def("getDistanceToFocus", &Parabola::getDistanceToFocus)
        .def("getReflectionCoefficient", &Parabola::getReflectionCoefficient)
        .def("getConfig", &Parabola::getConfig);

    // WaveField binding
    py::class_<WaveField>(m, "WaveField")
        .def(py::init<const SimulationConfig&>())
        .def("update", &WaveField::update)
        .def("reset", &WaveField::reset)
        .def("addSource", &WaveField::addSource)
        .def("applyBoundaryConditions", &WaveField::applyBoundaryConditions)
        .def("getGridSize", &WaveField::getGridSize)
        .def("getCurrentData", [](const WaveField& wf) {
            auto data = wf.getCurrentData();
            int gridSize = wf.getGridSize();
            return py::array_t<double>(
                {gridSize, gridSize},  // shape
                {sizeof(double) * gridSize, sizeof(double)},  // strides
                data,  // data pointer
                py::cast(wf)  // parent object to keep data alive
            );
        })
        .def("getPreviousData", [](const WaveField& wf) {
            auto data = wf.getPreviousData();
            int gridSize = wf.getGridSize();
            return py::array_t<double>(
                {gridSize, gridSize},
                {sizeof(double) * gridSize, sizeof(double)},
                data,
                py::cast(wf)
            );
        });

    // DualParabolicWaveSimulation binding
    py::class_<DualParabolicWaveSimulation>(m, "DualParabolicWaveSimulation")
        .def(py::init<>())
        .def("update", &DualParabolicWaveSimulation::update)
        .def("reset", &DualParabolicWaveSimulation::reset)
        .def("setFrequency", &DualParabolicWaveSimulation::setFrequency)
        .def("setAmplitude", &DualParabolicWaveSimulation::setAmplitude)
        .def("getConfig", &DualParabolicWaveSimulation::getConfig)
        .def("getWaveParams", &DualParabolicWaveSimulation::getWaveParams)
        .def("getFocusPoint", &DualParabolicWaveSimulation::getFocusPoint)
        .def("getCFLTimeStep", &DualParabolicWaveSimulation::getCFLTimeStep)
        .def("getCurrentTime", &DualParabolicWaveSimulation::getCurrentTime)
        .def("getWaveField", &DualParabolicWaveSimulation::getWaveField, 
             py::return_value_policy::reference_internal)
        .def("getWaveFieldData", [](const DualParabolicWaveSimulation& sim) {
            auto waveField = sim.getWaveField();
            if (!waveField) {
                throw std::runtime_error("WaveField is not initialized");
            }
            auto data = waveField->getCurrentData();
            int gridSize = waveField->getGridSize();
            return py::array_t<double>(
                {gridSize, gridSize},
                {sizeof(double) * gridSize, sizeof(double)},
                data,
                py::cast(*waveField)
            );
        })
        .def("getParabolaBoundary", [](const DualParabolicWaveSimulation& sim) {
            // Return parabola boundary points for visualization
            auto config = sim.getConfig();
            std::vector<std::vector<double>> boundary;
            
            int gridSize = config.gridSize;
            double dx = (config.xMax - config.xMin) / gridSize;
            double dy = (config.yMax - config.yMin) / gridSize;
            
            for (int i = 0; i < gridSize; ++i) {
                for (int j = 0; j < gridSize; ++j) {
                    double x = config.xMin + i * dx;
                    double y = config.yMin + j * dy;
                    // This is a simplified boundary detection
                    // In a real implementation, you'd check against actual parabola geometry
                    if (std::abs(x*x + y*y - 100.0) < 10.0) {  // Rough circular approximation
                        boundary.push_back({x, y});
                    }
                }
            }
            return boundary;
        });

    // Utility functions
    m.def("calculate_cfl_timestep", [](double dx, double dy, double speed) {
        return 0.4 * std::min(dx, dy) / (speed * std::sqrt(2.0));
    }, "Calculate CFL-stable time step");

    m.def("version", []() {
        return "1.0.0";
    }, "Get library version");
}
