#pragma once

#include "Types.h"
#include "Parabola.h"
#include <vector>
#include <memory>

namespace WaveSimulation {

class WaveField {
public:
    WaveField(const SimulationConfig& config, 
              const WaveParams& waveParams,
              std::shared_ptr<Parabola> majorParabola,
              std::shared_ptr<Parabola> minorParabola,
              const Point2D& focusPoint);
    
    ~WaveField() = default;
    
    void update(double dt);
    void reset();
    
    // Getters
    const std::vector<float>& getGrid() const { return m_grid; }
    const std::vector<float>& getCurrentAmplitudes() const { return m_grid; }
    const std::vector<uint8_t>& getBoundaryMask() const { return m_boundaryMask; }
    const std::vector<BoundaryType>& getBoundaryTypes() const { return m_boundaryTypes; }
    double getTime() const { return m_time; }
    double getCurrentTime() const { return m_time; }
    int getGridSize() const { return m_config.gridSize; }
    
    // Configuration
    void setAmplitude(double amplitude) { m_waveParams.amplitude = amplitude; }
    void setFrequency(double frequency);
    
private:
    void initializeGrids();
    void createBoundaryMask();
    void applyWaveEquation(double dt);
    void applyBoundaryConditions();
    void applyParabolicReflection(int i, int j);
    void applyGhostPointReflection(int i, int j, const Point2D& normal);
    void addSourceExcitation(double time);
    void validateCFLCondition() const;
    
    // Reflection boundary condition helpers
    Point2D calculateParabolicNormal(double x, double y) const;
    bool isOnParabolicBoundary(double x, double y) const;
    
    // Finite difference helpers for boundary-aware wave propagation
    double getFiniteDifferenceX(int i, int j) const;
    double getFiniteDifferenceY(int i, int j) const;
    double getBoundaryAwareFiniteDifferenceX(int i, int j) const;
    double getBoundaryAwareFiniteDifferenceY(int i, int j) const;
    
    Point2D getGridCoordinates(int gridI, int gridJ) const;
    void calculateFocusPosition();
    
    SimulationConfig m_config;
    WaveParams m_waveParams;
    std::shared_ptr<Parabola> m_majorParabola;
    std::shared_ptr<Parabola> m_minorParabola;
    Point2D m_focusPoint;
    
    std::vector<float> m_grid;
    std::vector<float> m_previousGrid;
    std::vector<uint8_t> m_boundaryMask;
    std::vector<BoundaryType> m_boundaryTypes;
    std::vector<float> m_sourceGrid;
    
    double m_time;
    int m_focusI, m_focusJ;
};

} // namespace WaveSimulation
