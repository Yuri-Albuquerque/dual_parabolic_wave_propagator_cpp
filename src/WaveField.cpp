#include "WaveField.h"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <omp.h>

namespace WaveSimulation {

WaveField::WaveField(const SimulationConfig& config, 
                     const WaveParams& waveParams,
                     std::shared_ptr<Parabola> majorParabola,
                     std::shared_ptr<Parabola> minorParabola,
                     const Point2D& focusPoint)
    : m_config(config), m_waveParams(waveParams), 
      m_majorParabola(majorParabola), m_minorParabola(minorParabola),
      m_focusPoint(focusPoint), m_time(0.0) {
    
    validateCFLCondition();
    initializeGrids();
    createBoundaryMask();
    calculateFocusPosition();
}

void WaveField::validateCFLCondition() const {
    double dx = (m_config.xMax - m_config.xMin) / (m_config.gridSize - 1);
    double dy = (m_config.yMax - m_config.yMin) / (m_config.gridSize - 1);
    double minGridSpacing = std::min(dx, dy);
    
    // CFL condition: dt <= CFL_factor * min(dx,dy) / (c * sqrt(2))
    double maxStableTimeStep = 0.4 * minGridSpacing / (m_waveParams.speed * std::sqrt(2.0));
    
    if (m_config.timeStep > maxStableTimeStep) {
        std::cerr << "Warning: Time step " << m_config.timeStep 
                  << " exceeds CFL stability limit " << maxStableTimeStep << std::endl;
        std::cerr << "Grid spacing: dx=" << dx << ", dy=" << dy 
                  << ", wave speed=" << m_waveParams.speed << std::endl;
    }
}

void WaveField::initializeGrids() {
    int totalSize = m_config.gridSize * m_config.gridSize;
    
    m_grid.resize(totalSize, 0.0f);
    m_previousGrid.resize(totalSize, 0.0f);
    m_boundaryMask.resize(totalSize, 0);
    m_sourceGrid.resize(totalSize, 0.0f);
}

void WaveField::createBoundaryMask() {
    const int gridSize = m_config.gridSize;
    const double dx = (m_config.xMax - m_config.xMin) / (gridSize - 1);
    const double dy = (m_config.yMax - m_config.yMin) / (gridSize - 1);
    
    // Parabola parameters (same as TypeScript version)
    const double majorDiameter = 20.0 * 25.4; // 508mm
    const double majorFocus = 100.0;
    const double minorDiameter = 10.0;  // mm (CORRECTED from 100.0 to 10.0)
    const double minorFocus = 50.0;
    
    #pragma omp parallel for collapse(2)
    for (int i = 0; i < gridSize; i++) {
        for (int j = 0; j < gridSize; j++) {
            double x = m_config.xMin + j * dx;
            double y = m_config.yMax - i * dy; // Flip Y coordinate
            
            // Major parabola (concave down): y = -x²/(4*f) + f
            double majorY = -(x * x) / (4.0 * majorFocus) + majorFocus;
            bool insideMajor = y <= majorY && std::abs(x) <= majorDiameter / 2.0;
            
            // Minor parabola (concave up): y = x²/(4*f) - f
            double minorY = (x * x) / (4.0 * minorFocus) - minorFocus;
            bool outsideMinor = y >= minorY || std::abs(x) > minorDiameter / 2.0;
            
            int index = i * gridSize + j;
            m_boundaryMask[index] = (insideMajor && outsideMinor) ? 1 : 0;
        }
    }
}

void WaveField::calculateFocusPosition() {
    const int gridSize = m_config.gridSize;
    const double dx = (m_config.xMax - m_config.xMin) / (gridSize - 1);
    const double dy = (m_config.yMax - m_config.yMin) / (gridSize - 1);
    
    m_focusI = static_cast<int>(std::round((m_config.yMax - m_focusPoint.y) / dy));
    m_focusJ = static_cast<int>(std::round((m_focusPoint.x - m_config.xMin) / dx));
    
    // Clamp to valid range
    m_focusI = std::clamp(m_focusI, 0, gridSize - 1);
    m_focusJ = std::clamp(m_focusJ, 0, gridSize - 1);
}

void WaveField::addSourceExcitation(double time) {
    const int gridSize = m_config.gridSize;
    std::fill(m_sourceGrid.begin(), m_sourceGrid.end(), 0.0f);
    
    if (m_focusI >= 0 && m_focusI < gridSize && m_focusJ >= 0 && m_focusJ < gridSize) {
        int index = m_focusI * gridSize + m_focusJ;
        
        if (m_boundaryMask[index]) {
            // Complete Morlet wavelet implementation (matching TypeScript version)
            // Formula: Ψ_σ(t) = c_σ π^(-1/4) e^(-1/2 t²) (cos(σt) - κ_σ)
            // Where:
            // - κ_σ = e^(-1/2 σ²) (admissibility criterion)
            // - c_σ = (1 + e^(-σ²) - 2e^(-3/4 σ²))^(-1/2) (normalization constant)
            // - σ = 6.0 (frequency parameter for good time-frequency localization)
            
            const double centralFreq = m_waveParams.frequency;
            const double timeScale = 1.0 / centralFreq; // Scale time relative to frequency
            const double pulseCenter = 3.0 * timeScale;  // Center time
            const double pulseDuration = 8.0 * timeScale; // Total duration (±4 time units)
            
            double amplitude = 0.0;
            if (time <= pulseDuration) {
                // Scale time for proper wavelet duration (centered around t=0)
                const double scaledTime = (time - pulseCenter) / timeScale;
                
                // Use sigma = 6.0 for good time-frequency localization (σ > 5 recommended)
                const double sigma = 6.0;
                
                // Limit wavelet duration to ±4 time units
                if (std::abs(scaledTime) <= 4.0) {
                    // Admissibility criterion
                    const double kappa_sigma = std::exp(-0.5 * sigma * sigma);
                    
                    // Normalization constant
                    const double c_sigma = std::pow(1.0 + std::exp(-sigma * sigma) - 2.0 * std::exp(-0.75 * sigma * sigma), -0.5);
                    
                    // Gaussian envelope
                    const double gaussian = std::exp(-0.5 * scaledTime * scaledTime);
                    
                    // Complex exponential - we take the real part (cosine)
                    const double carrier = std::cos(sigma * scaledTime);
                    
                    // Complete Morlet wavelet (real part)
                    const double normalization = c_sigma * std::pow(M_PI, -0.25);
                    const double morlet_value = normalization * gaussian * (carrier - kappa_sigma);
                    
                    // Scale by amplitude (strong enough for visibility)
                    const double source_amplitude = m_waveParams.amplitude * 15.0;
                    amplitude = source_amplitude * morlet_value;
                }
            }
            
            m_sourceGrid[index] = static_cast<float>(amplitude);
            
            // Excite neighboring points for better visibility
            const int neighbors[][2] = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};
            for (const auto& neighbor : neighbors) {
                int ni = m_focusI + neighbor[0];
                int nj = m_focusJ + neighbor[1];
                
                if (ni >= 0 && ni < gridSize && nj >= 0 && nj < gridSize) {
                    int neighborIndex = ni * gridSize + nj;
                    if (m_boundaryMask[neighborIndex]) {
                        m_sourceGrid[neighborIndex] = static_cast<float>(amplitude * 0.5);
                    }
                }
            }
        }
    }
}

void WaveField::applyWaveEquation(double dt) {
    const int gridSize = m_config.gridSize;
    const double c = m_waveParams.speed;
    const double c2 = c * c;
    const double dx = (m_config.xMax - m_config.xMin) / (gridSize - 1);
    const double dy = (m_config.yMax - m_config.yMin) / (gridSize - 1);
    const double dampingFactor = m_config.dampingFactor;
    
    // Wave equation coefficients (same as C++ reference implementation)
    const double q0 = c * dt;
    const double q1 = c2 * dt * dt;
    const double q2 = (c * dt / dx) * (c * dt / dx);
    const double q3 = (c * dt / dy) * (c * dt / dy);
    
    std::vector<float> newGrid(gridSize * gridSize, 0.0f);
    
    // Apply wave equation with OpenMP parallelization
    #pragma omp parallel for collapse(2)
    for (int i = 1; i < gridSize - 1; i++) {
        for (int j = 1; j < gridSize - 1; j++) {
            int index = i * gridSize + j;
            
            if (!m_boundaryMask[index]) {
                newGrid[index] = 0.0f;
                continue;
            }
            
            // Finite difference operators
            float dxx = m_grid[(i * gridSize) + j - 1] - 2.0f * m_grid[index] + m_grid[(i * gridSize) + j + 1];
            float dyy = m_grid[((i - 1) * gridSize) + j] - 2.0f * m_grid[index] + m_grid[((i + 1) * gridSize) + j];
            
            // Wave equation: u(t+dt) = (1 / (1 + damping*q0)) * 
            //                (-u(t-dt) + 2*u(t) + damping*q0*u(t-dt) + q1*source + q2*dxx + q3*dyy)
            double dampingTerm = dampingFactor * q0;
            double denominator = 1.0 + dampingTerm;
            
            newGrid[index] = static_cast<float>((
                -m_previousGrid[index] + 
                2.0 * m_grid[index] + 
                dampingTerm * m_previousGrid[index] +
                q1 * m_sourceGrid[index] +
                q2 * dxx +
                q3 * dyy
            ) / denominator);
        }
    }
    
    // Update grids
    m_previousGrid = m_grid;
    m_grid = std::move(newGrid);
    
    applyBoundaryConditions();
}

void WaveField::applyBoundaryConditions() {
    const int gridSize = m_config.gridSize;
    const double reflectionCoeff = m_config.reflectionCoeff;
    
    #pragma omp parallel for
    for (int i = 0; i < gridSize * gridSize; i++) {
        if (!m_boundaryMask[i]) {
            m_grid[i] = 0.0f;
            m_previousGrid[i] = 0.0f;
        }
    }
}

void WaveField::update(double dt) {
    m_time += dt;
    addSourceExcitation(m_time);
    applyWaveEquation(dt);
}

void WaveField::reset() {
    m_time = 0.0;
    std::fill(m_grid.begin(), m_grid.end(), 0.0f);
    std::fill(m_previousGrid.begin(), m_previousGrid.end(), 0.0f);
    std::fill(m_sourceGrid.begin(), m_sourceGrid.end(), 0.0f);
}

void WaveField::setFrequency(double frequency) {
    m_waveParams.frequency = frequency;
    m_waveParams.wavelength = m_waveParams.speed / frequency;
}

Point2D WaveField::getGridCoordinates(int gridI, int gridJ) const {
    const double dx = (m_config.xMax - m_config.xMin) / (m_config.gridSize - 1);
    const double dy = (m_config.yMax - m_config.yMin) / (m_config.gridSize - 1);
    
    double x = m_config.xMin + gridJ * dx;
    double y = m_config.yMax - gridI * dy;
    
    return Point2D(x, y);
}

} // namespace WaveSimulation
