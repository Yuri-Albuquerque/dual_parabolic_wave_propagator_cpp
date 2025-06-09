#pragma once

#include "Types.h"
#include "WaveField.h"
#include "Parabola.h"
#include <memory>
#include <functional>

namespace WaveSimulation {

class DualParabolicWaveSimulation {
public:
    DualParabolicWaveSimulation();
    DualParabolicWaveSimulation(int gridSize, double domainSize, double waveSpeed, 
                               double timeStep, double simulationSpeed);
    ~DualParabolicWaveSimulation() = default;
    
    void initialize();
    void reset();
    void update();
    void update(double dt);
    
    // Configuration
    void setFrequency(double frequency);
    void setAmplitude(double amplitude);
    
    // Getters for console mode
    int getGridSize() const;
    double getDomainSize() const;
    double getWaveSpeed() const;
    double getTimeStep() const;
    double getSimulationSpeed() const;
    const WaveField& getWaveField() const;
    
    // Existing getters
    std::shared_ptr<WaveField> getWaveFieldPtr() const { return m_waveField; }
    const Point2D& getFocusPoint() const { return m_focusPoint; }
    std::shared_ptr<Parabola> getMajorParabola() const { return m_majorParabola; }
    std::shared_ptr<Parabola> getMinorParabola() const { return m_minorParabola; }
    const WaveParams& getWaveParams() const { return m_waveParams; }
    const SimulationConfig& getConfig() const { return m_config; }
    
    // Callback for updates
    void setUpdateCallback(std::function<void()> callback) { m_updateCallback = callback; }
    
private:
    void setupParabolas();
    void setupWaveParameters();
    void setupSimulationConfig();
    void initializeWaveField();
    
    std::shared_ptr<Parabola> m_majorParabola;
    std::shared_ptr<Parabola> m_minorParabola;
    std::shared_ptr<WaveField> m_waveField;
    Point2D m_focusPoint;
    SimulationConfig m_config;
    WaveParams m_waveParams;
    
    std::function<void()> m_updateCallback;
};

} // namespace WaveSimulation
