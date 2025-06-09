#include "DualParabolicWaveSimulation.h"
#include <cmath>
#include <iostream>
#include <iomanip>

namespace WaveSimulation {

DualParabolicWaveSimulation::DualParabolicWaveSimulation() {
    setupParabolas();
    setupWaveParameters();
    setupSimulationConfig();
    initializeWaveField();
}

DualParabolicWaveSimulation::DualParabolicWaveSimulation(int gridSize, double domainSize, 
                                                       double waveSpeed, double timeStep, 
                                                       double simulationSpeed) {
    setupParabolas();
    setupWaveParameters();
    setupSimulationConfig();
    
    // Override config with custom parameters
    m_config.gridSize = gridSize;
    m_config.xMin = -domainSize / 2.0;
    m_config.xMax = domainSize / 2.0;
    m_config.yMin = -domainSize / 2.0;
    m_config.yMax = domainSize / 2.0;
    m_config.timeStep = timeStep;
    
    m_waveParams.speed = waveSpeed * 1000.0; // Convert m/s to mm/s
    
    initializeWaveField();
}

void DualParabolicWaveSimulation::setupParabolas() {
    // Convert units: 20 inches = 508mm, focus distances in mm
    const double majorDiameter = 20.0 * 25.4; // 508mm
    const double majorFocus = 100.0; // mm
    const double minorDiameter = 100.0; // mm
    const double minorFocus = 50.0; // mm
    
    // Focus point is at origin (coincident focus)
    m_focusPoint = Point2D(0.0, 0.0);
    
    // Major parabola (umbrella, concave down)
    // Vertex is 100mm above focus point
    Point2D majorVertex(0.0, majorFocus);
    m_majorParabola = std::make_shared<Parabola>(majorDiameter, majorFocus, majorVertex, false);
    
    // Minor parabola (bowl, concave up)
    // Vertex is 50mm below focus point
    Point2D minorVertex(0.0, -minorFocus);
    m_minorParabola = std::make_shared<Parabola>(minorDiameter, minorFocus, minorVertex, true);
}

void DualParabolicWaveSimulation::setupWaveParameters() {
    const double frequency = 1000.0; // Hz
    const double speed = 343000.0; // mm/s (speed of sound in air)
    const double wavelength = speed / frequency;
    
    m_waveParams.frequency = frequency;
    m_waveParams.wavelength = wavelength;
    m_waveParams.speed = speed;
    m_waveParams.amplitude = 1.0;
}

void DualParabolicWaveSimulation::setupSimulationConfig() {
    // Simulation domain should encompass both parabolas
    m_config.xMin = -300.0;
    m_config.xMax = 300.0;
    m_config.yMin = -100.0;
    m_config.yMax = 150.0;
    m_config.gridSize = 300;
    
    // Calculate CFL-compliant time step
    const double dx = (m_config.xMax - m_config.xMin) / (m_config.gridSize - 1);
    const double dy = (m_config.yMax - m_config.yMin) / (m_config.gridSize - 1);
    const double minGridSpacing = std::min(dx, dy);
    const double speed = m_waveParams.speed;
    
    // CFL condition: dt <= CFL_factor * min(dx,dy) / (c * sqrt(2))
    // Use CFL_factor = 0.4 for stability margin
    const double maxStableTimeStep = 0.4 * minGridSpacing / (speed * std::sqrt(2.0));
    
    m_config.timeStep = maxStableTimeStep;
    m_config.dampingFactor = 0.001; // Minimal damping for better wave propagation
    m_config.reflectionCoeff = 0.95; // High reflection coefficient
    
    std::cout << "CFL-compliant time step: " << std::scientific << maxStableTimeStep << " s" << std::endl;
    std::cout << "Grid spacing: dx=" << std::fixed << std::setprecision(3) << dx 
              << "mm, dy=" << dy << "mm" << std::endl;
}

void DualParabolicWaveSimulation::initializeWaveField() {
    m_waveField = std::make_shared<WaveField>(
        m_config,
        m_waveParams,
        m_majorParabola,
        m_minorParabola,
        m_focusPoint
    );
}

void DualParabolicWaveSimulation::update(double dt) {
    if (m_waveField) {
        m_waveField->update(dt);
        
        if (m_updateCallback) {
            m_updateCallback();
        }
    }
}

void DualParabolicWaveSimulation::reset() {
    if (m_waveField) {
        m_waveField->reset();
        
        if (m_updateCallback) {
            m_updateCallback();
        }
    }
}

void DualParabolicWaveSimulation::setFrequency(double frequency) {
    m_waveParams.frequency = frequency;
    m_waveParams.wavelength = m_waveParams.speed / frequency;
    
    if (m_waveField) {
        m_waveField->setFrequency(frequency);
    }
}

void DualParabolicWaveSimulation::setAmplitude(double amplitude) {
    m_waveParams.amplitude = amplitude;
    
    if (m_waveField) {
        m_waveField->setAmplitude(amplitude);
    }
}

void DualParabolicWaveSimulation::initialize() {
    // Initialize the simulation - WaveField is already initialized in constructor
    if (m_waveField) {
        m_waveField->reset();
    }
}

void DualParabolicWaveSimulation::update() {
    update(m_config.timeStep);
}

// Getter implementations for console mode
int DualParabolicWaveSimulation::getGridSize() const {
    return m_config.gridSize;
}

double DualParabolicWaveSimulation::getDomainSize() const {
    return m_config.xMax - m_config.xMin; // Return width of domain
}

double DualParabolicWaveSimulation::getWaveSpeed() const {
    return m_waveParams.speed / 1000.0; // Convert mm/s back to m/s
}

double DualParabolicWaveSimulation::getTimeStep() const {
    return m_config.timeStep;
}

double DualParabolicWaveSimulation::getSimulationSpeed() const {
    return 1.0; // Default simulation speed
}

const WaveField& DualParabolicWaveSimulation::getWaveField() const {
    return *m_waveField;
}

} // namespace WaveSimulation
