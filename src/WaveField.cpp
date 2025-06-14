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
    m_boundaryTypes.resize(totalSize, BoundaryType::AIR);
    m_sourceGrid.resize(totalSize, 0.0f);
    
    // Initialize with ground truth initial conditions
    // u(i,j,0) = 0.0 and u(i,j,1) = u(i,j,0) + ht * 0.0 = 0.0
    const double init_cond_u0 = 0.0;
    const double init_cond_u1 = init_cond_u0 + m_config.timeStep * init_cond_u0;
    
    std::fill(m_grid.begin(), m_grid.end(), static_cast<float>(init_cond_u1));
    std::fill(m_previousGrid.begin(), m_previousGrid.end(), static_cast<float>(init_cond_u0));
}

void WaveField::createBoundaryMask() {
    const int gridSize = m_config.gridSize;
    const double dx = (m_config.xMax - m_config.xMin) / (gridSize - 1);
    const double dy = (m_config.yMax - m_config.yMin) / (gridSize - 1);
    
    // Parabola parameters - corrected to match specifications
    const double majorDiameter = 20.0 * 25.4; // 508mm
    const double majorFocus = 100.0;
    const double minorDiameter = 200.0;  // mm (CORRECTED to match specification)
    const double minorFocus = 50.0;
    
    // Thick parabolic boundary parameters
    const double parabolicThickness = 30.0; // 30mm thick parabolic material
    
    // Initialize all points as AIR medium
    std::fill(m_boundaryMask.begin(), m_boundaryMask.end(), 1); // 1 = allow propagation
    std::fill(m_boundaryTypes.begin(), m_boundaryTypes.end(), BoundaryType::AIR);
    
    #pragma omp parallel for collapse(2)
    for (int i = 0; i < gridSize; i++) {
        for (int j = 0; j < gridSize; j++) {
            double x = m_config.xMin + j * dx;
            double y = m_config.yMax - i * dy; // Flip Y coordinate
            int index = i * gridSize + j;
            
            // Major parabola (concave down, umbrella): y = -x²/(4*f) + f
            double majorY = -(x * x) / (4.0 * majorFocus) + majorFocus;
            bool insideMajorParabola = y <= majorY && std::abs(x) <= majorDiameter / 2.0;
            
            // Minor parabola (concave up, bowl): y = x²/(4*f) - f  
            double minorY = (x * x) / (4.0 * minorFocus) - minorFocus;
            bool outsideMinorParabola = y >= minorY && std::abs(x) <= minorDiameter / 2.0;
            
            // Calculate distances to parabolic surfaces for thickness
            double distToMajor = std::abs(y - majorY);
            double distToMinor = std::abs(y - minorY);
            
            // Point is in AIR propagation region if it's:
            // 1. Inside the major parabola (below umbrella)
            // 2. Outside the minor parabola (above bowl)
            // 3. Not within the thick parabolic material
            bool inAirRegion = insideMajorParabola && outsideMinorParabola;
            
            if (inAirRegion) {
                // Check if we're within the thick parabolic boundaries
                bool nearMajorSurface = insideMajorParabola && distToMajor <= parabolicThickness;
                bool nearMinorSurface = outsideMinorParabola && distToMinor <= parabolicThickness;
                
                if (nearMajorSurface || nearMinorSurface) {
                    // Point is in thick parabolic material (1000x slower wave speed)
                    m_boundaryMask[index] = 1; // Allow wave propagation but slower
                    m_boundaryTypes[index] = BoundaryType::PARABOLIC;
                } else {
                    // Point is in normal air propagation region
                    m_boundaryMask[index] = 1; // Allow normal wave propagation
                    m_boundaryTypes[index] = BoundaryType::AIR;
                }
            } else {
                // Point is outside the propagation region - rigid boundary
                m_boundaryMask[index] = 0; // No wave propagation
                m_boundaryTypes[index] = BoundaryType::RIGID;
            }
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
    const double c_air = m_waveParams.speed;           // Normal air speed (343,000 mm/s)
    const double c_parabolic = c_air / 1000.0;         // Parabolic material speed (343 mm/s)
    const double dx = (m_config.xMax - m_config.xMin) / (gridSize - 1);
    const double dy = (m_config.yMax - m_config.yMin) / (gridSize - 1);
    const double dampingFactor = m_config.dampingFactor;
    
    std::vector<float> newGrid(gridSize * gridSize, 0.0f);
    
    // Apply wave equation with material-dependent wave speeds
    #pragma omp parallel for
    for (int i = 0; i < gridSize; i++) {
        for (int j = 0; j < gridSize; j++) {
            int index = i * gridSize + j;
            
            // Handle rigid boundaries - force to zero
            if (m_boundaryTypes[index] == BoundaryType::RIGID) {
                newGrid[index] = 0.0f;
                continue;
            }
            
            // Get wave speed based on material type
            double c = (m_boundaryTypes[index] == BoundaryType::PARABOLIC) ? c_parabolic : c_air;
            
            // Wave equation coefficients (material-dependent)
            const double q0 = c * dt;
            const double q1 = c * c * dt * dt;
            const double q2 = (c * dt / dx) * (c * dt / dx);
            const double q3 = (c * dt / dy) * (c * dt / dy);
            
            // Skip edges that don't have enough neighbors for finite differences
            if (i == 0 || i == gridSize - 1 || j == 0 || j == gridSize - 1) {
                if (i == 0) {
                    // Special boundary condition for top row (i == 0), matching ground truth
                    if (j > 0 && j < gridSize - 1) {
                        // Use only x-direction derivatives for top boundary
                        double dxx = getFiniteDifferenceX(i, j);
                        // For top boundary, use special y-derivative: 2*(u(1,j) - u(0,j))
                        double dzz = 2.0 * (m_grid[(i + 1) * gridSize + j] - m_grid[index]);
                        
                        double dampingTerm = dampingFactor * q0;
                        double denominator = 1.0 + dampingTerm;
                        
                        newGrid[index] = static_cast<float>((
                            -1.0 * (m_previousGrid[index] - 2.0 * m_grid[index]) +
                            q0 * dampingFactor * m_previousGrid[index] +
                            q1 * m_sourceGrid[index] +
                            q2 * dxx +
                            q3 * dzz
                        ) / denominator);
                    } else {
                        newGrid[index] = 0.0f;
                    }
                } else {
                    // Other domain boundaries - absorb waves
                    newGrid[index] = 0.0f;
                }
                continue;
            }
            
            // Interior points - use material-dependent finite differences
            double dxx, dzz;
            
            // Check if any neighbor is a rigid boundary and use boundary-aware differences
            bool nearRigidBoundary = false;
            if ((i > 0 && m_boundaryTypes[(i-1) * gridSize + j] == BoundaryType::RIGID) ||
                (i < gridSize-1 && m_boundaryTypes[(i+1) * gridSize + j] == BoundaryType::RIGID) ||
                (j > 0 && m_boundaryTypes[i * gridSize + (j-1)] == BoundaryType::RIGID) ||
                (j < gridSize-1 && m_boundaryTypes[i * gridSize + (j+1)] == BoundaryType::RIGID)) {
                nearRigidBoundary = true;
            }
            
            if (nearRigidBoundary) {
                // Use boundary-aware finite differences for points near rigid surfaces
                dxx = getBoundaryAwareFiniteDifferenceX(i, j);
                dzz = getBoundaryAwareFiniteDifferenceY(i, j);
            } else {
                // Standard finite differences for interior points
                dxx = getFiniteDifferenceX(i, j);
                dzz = getFiniteDifferenceY(i, j);
            }
            
            // Wave equation implementation matching ground truth solve_wv
            double dampingTerm = dampingFactor * q0;
            double denominator = 1.0 + dampingTerm;
            
            newGrid[index] = static_cast<float>((
                -1.0 * (m_previousGrid[index] - 2.0 * m_grid[index]) +
                q0 * dampingFactor * m_previousGrid[index] +
                q1 * m_sourceGrid[index] +
                q2 * dxx +
                q3 * dzz
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
    
    // Apply boundary conditions based on material type
    #pragma omp parallel for collapse(2)
    for (int i = 0; i < gridSize; i++) {
        for (int j = 0; j < gridSize; j++) {
            int index = i * gridSize + j;
            
            if (m_boundaryTypes[index] == BoundaryType::RIGID) {
                // Rigid boundary - enforce zero displacement and velocity
                m_grid[index] = 0.0f;
                m_previousGrid[index] = 0.0f;
            }
            // AIR and PARABOLIC materials allow wave propagation
            // The wave equation already handles different speeds for these materials
        }
    }
}

void WaveField::applyParabolicReflection(int i, int j) {
    const int gridSize = m_config.gridSize;
    const double dx = (m_config.xMax - m_config.xMin) / (gridSize - 1);
    const double dy = (m_config.yMax - m_config.yMin) / (gridSize - 1);
    
    // Get physical coordinates
    double x = m_config.xMin + j * dx;
    double y = m_config.yMax - i * dy;
    
    // For parabolic boundaries, ensure ZERO VELOCITY at the barrier
    // This means: ∂u/∂t = 0 at boundary
    // In finite difference: (u_new - u_old) / dt = 0
    // Therefore: u_new = u_old at boundary
    
    int index = i * gridSize + j;
    
    // CRITICAL: Enforce zero velocity by setting u_new = u_old = 0
    // This ensures the wave cannot move at the boundary (zero velocity)
    m_grid[index] = 0.0f;           // Current time step
    m_previousGrid[index] = 0.0f;   // Previous time step
    
    // For proper reflection, we also need to ensure that waves incident
    // on the boundary are reflected back into the domain
    
    // Find the normal direction to the parabolic surface
    Point2D normal = calculateParabolicNormal(x, y);
    
    // Apply ghost point method for perfect reflection
    // The wave amplitude just inside the boundary should be mirrored
    // This creates the reflection effect
    applyGhostPointReflection(i, j, normal);
}

void WaveField::applyGhostPointReflection(int i, int j, const Point2D& normal) {
    const int gridSize = m_config.gridSize;
    int index = i * gridSize + j;
    
    // For perfect reflection at parabolic surfaces:
    // 1. The boundary point must have zero displacement: u(boundary) = 0
    // 2. The boundary point must have zero velocity: ∂u/∂t(boundary) = 0
    
    // Enforce zero displacement and zero velocity
    m_grid[index] = 0.0f;           // Zero displacement at current time
    m_previousGrid[index] = 0.0f;   // Zero displacement at previous time
    
    // The zero velocity condition is automatically satisfied since:
    // velocity ≈ (u_current - u_previous) / dt = (0 - 0) / dt = 0
    
    // For proper wave reflection, we need to ensure that when a wave hits
    // the boundary, it bounces back. This is achieved by the finite difference
    // scheme automatically when boundary points are kept at zero.
    
    // The reflection happens naturally in the wave equation when:
    // - Boundary points are fixed at zero (rigid boundary)
    // - Interior points near the boundary experience the zero boundary values
    // - This creates a "node" that reflects incoming waves
}

void WaveField::update(double dt) {
    m_time += dt;
    addSourceExcitation(m_time);
    applyWaveEquation(dt);
}

void WaveField::reset() {
    m_time = 0.0;
    
    // Initialize with ground truth initial conditions
    // u(i,j,0) = 0.0 and u(i,j,1) = u(i,j,0) + ht * 0.0 = 0.0
    const double init_cond_u0 = 0.0;
    const double init_cond_u1 = init_cond_u0 + m_config.timeStep * init_cond_u0;
    
    std::fill(m_grid.begin(), m_grid.end(), static_cast<float>(init_cond_u1));
    std::fill(m_previousGrid.begin(), m_previousGrid.end(), static_cast<float>(init_cond_u0));
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

// Finite difference helper functions for boundary-aware wave propagation
double WaveField::getFiniteDifferenceX(int i, int j) const {
    const int gridSize = m_config.gridSize;
    int index = i * gridSize + j;
    
    // Standard centered difference in x-direction
    return m_grid[i * gridSize + (j - 1)] - 2.0 * m_grid[index] + m_grid[i * gridSize + (j + 1)];
}

double WaveField::getFiniteDifferenceY(int i, int j) const {
    const int gridSize = m_config.gridSize;
    int index = i * gridSize + j;
    
    // Standard centered difference in y-direction
    return m_grid[(i - 1) * gridSize + j] - 2.0 * m_grid[index] + m_grid[(i + 1) * gridSize + j];
}

double WaveField::getBoundaryAwareFiniteDifferenceX(int i, int j) const {
    const int gridSize = m_config.gridSize;
    int index = i * gridSize + j;
    
    // Check boundary conditions for x-direction finite difference
    double leftValue = 0.0;
    double rightValue = 0.0;
    
    if (j > 0) {
        BoundaryType leftType = m_boundaryTypes[i * gridSize + (j - 1)];
        if (leftType == BoundaryType::RIGID) {
            leftValue = 0.0; // Rigid boundary - zero displacement
        } else {
            leftValue = m_grid[i * gridSize + (j - 1)]; // Normal or parabolic material
        }
    }
    
    if (j < gridSize - 1) {
        BoundaryType rightType = m_boundaryTypes[i * gridSize + (j + 1)];
        if (rightType == BoundaryType::RIGID) {
            rightValue = 0.0; // Rigid boundary - zero displacement
        } else {
            rightValue = m_grid[i * gridSize + (j + 1)]; // Normal or parabolic material
        }
    }
    
    return leftValue - 2.0 * m_grid[index] + rightValue;
}

double WaveField::getBoundaryAwareFiniteDifferenceY(int i, int j) const {
    const int gridSize = m_config.gridSize;
    int index = i * gridSize + j;
    
    // Check boundary conditions for y-direction finite difference
    double topValue = 0.0;
    double bottomValue = 0.0;
    
    if (i > 0) {
        BoundaryType topType = m_boundaryTypes[(i - 1) * gridSize + j];
        if (topType == BoundaryType::RIGID) {
            topValue = 0.0; // Rigid boundary - zero displacement
        } else {
            topValue = m_grid[(i - 1) * gridSize + j]; // Normal or parabolic material
        }
    }
    
    if (i < gridSize - 1) {
        BoundaryType bottomType = m_boundaryTypes[(i + 1) * gridSize + j];
        if (bottomType == BoundaryType::RIGID) {
            bottomValue = 0.0; // Rigid boundary - zero displacement
        } else {
            bottomValue = m_grid[(i + 1) * gridSize + j]; // Normal or parabolic material
        }
    }
    
    return topValue - 2.0 * m_grid[index] + bottomValue;
}

Point2D WaveField::calculateParabolicNormal(double x, double y) const {
    // First determine which parabola we're closest to
    double majorY = m_majorParabola->getY(x);
    double minorY = m_minorParabola->getY(x);
    double distToMajor = std::abs(y - majorY);
    double distToMinor = std::abs(y - minorY);
    
    Point2D normal;
    
    if (distToMajor < distToMinor) {
        // We're on the major parabola
        // Calculate normal from parabola parameters
        auto params = m_majorParabola->getParams();
        double dx = x - params.vertex.x;
        double slope = 2.0 * params.coefficient * dx;  // dy/dx = 2a(x-h)
        
        // Normal vector is perpendicular to tangent: (-slope, 1)
        normal.x = -slope;
        normal.y = 1.0;
    } else {
        // We're on the minor parabola
        auto params = m_minorParabola->getParams();
        double dx = x - params.vertex.x;
        double slope = 2.0 * params.coefficient * dx;  // dy/dx = 2a(x-h)
        
        // Normal vector is perpendicular to tangent: (-slope, 1)
        normal.x = -slope;
        normal.y = 1.0;
    }
    
    // Normalize the normal vector
    double magnitude = std::sqrt(normal.x * normal.x + normal.y * normal.y);
    if (magnitude > 1e-10) {
        normal.x /= magnitude;
        normal.y /= magnitude;
    }
    
    return normal;
}

bool WaveField::isOnParabolicBoundary(double x, double y) const {
    const double tolerance = 1e-6; // Small tolerance for numerical precision
    
    // Check if point is on major parabola
    double majorY = m_majorParabola->getY(x);
    if (std::abs(y - majorY) < tolerance) {
        return true;
    }
    
    // Check if point is on minor parabola
    double minorY = m_minorParabola->getY(x);
    if (std::abs(y - minorY) < tolerance) {
        return true;
    }
    
    return false;
}

} // namespace WaveSimulation
