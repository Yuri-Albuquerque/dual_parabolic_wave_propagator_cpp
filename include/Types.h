#pragma once

#include <cstdint>
#include <memory>

// Boundary material types for thick parabolic reflectors
enum class BoundaryType : uint8_t {
    AIR = 0,        // Normal propagation medium (343 m/s)
    PARABOLIC = 1,  // Thick parabolic material (1500 m/s - 4.4x faster)
    RIGID = 2       // Rigid boundary (zero displacement)
};

namespace WaveSimulation {

struct Point2D {
    double x = 0.0;
    double y = 0.0;
    
    Point2D() = default;
    Point2D(double x_, double y_) : x(x_), y(y_) {}
};

struct ParabolaParams {
    double diameter = 0.0;
    double focus = 0.0;
    Point2D vertex;
    double coefficient = 0.0;
    bool concaveUp = false;
};

struct WaveParams {
    double frequency = 1000.0;    // Hz
    double wavelength = 343.0;    // mm
    double speed = 343000.0;      // mm/s
    double amplitude = 1.0;
};

struct SimulationConfig {
    int gridSize = 300;
    double xMin = -300.0, xMax = 300.0;  // mm
    double yMin = -100.0, yMax = 150.0;  // mm
    double timeStep = 1e-6;              // seconds
    double dampingFactor = 0.001;
    double reflectionCoeff = 0.95;
};

// Forward declarations
class WaveField;
class Parabola;
class DualParabolicWaveSimulation;

} // namespace WaveSimulation
