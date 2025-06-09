#include "WaveSimulationWidget.h"
#include <QOpenGLShaderProgram>
#include <QMouseEvent>
#include <GL/gl.h>
#include <cmath>
#include <algorithm>
#include <iostream>

namespace WaveSimulation {

WaveSimulationWidget::WaveSimulationWidget(QWidget* parent)
    : QOpenGLWidget(parent), m_simulation(nullptr), m_updateTimer(new QTimer(this)) {
    
    // Initialize simulation
    m_simulation = std::make_unique<DualParabolicWaveSimulation>();
    
    // Setup update callback
    m_simulation->setUpdateCallback([this]() {
        update(); // Trigger paintGL
    });
    
    // Setup timer for simulation updates
    connect(m_updateTimer, &QTimer::timeout, this, &WaveSimulationWidget::updateSimulation);
    
    // 60 FPS target for smooth animation
    m_updateTimer->setInterval(16); // ~60 FPS
    
    setMinimumSize(800, 600);
    
    m_frameTimer.start();
}

void WaveSimulationWidget::initializeGL() {
    initializeOpenGLFunctions();
    
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    
    // Setup view bounds from simulation config
    const auto& config = m_simulation->getConfig();
    m_viewBounds.xMin = static_cast<float>(config.xMin);
    m_viewBounds.xMax = static_cast<float>(config.xMax);
    m_viewBounds.yMin = static_cast<float>(config.yMin);
    m_viewBounds.yMax = static_cast<float>(config.yMax);
    m_viewBounds.gridSize = config.gridSize;
}

void WaveSimulationWidget::paintGL() {
    glClear(GL_COLOR_BUFFER_BIT);
    
    setupProjection();
    
    // Draw wave field first (background)
    drawWaveField();
    
    // Draw parabolas on top
    drawParabolas();
    
    // Update FPS counter
    m_frameCount++;
    double currentTime = m_frameTimer.elapsed() / 1000.0;
    if (currentTime - m_fpsUpdateTime >= 1.0) { // Update every second
        m_currentFPS = m_frameCount / (currentTime - m_fpsUpdateTime);
        emit fpsUpdated(m_currentFPS);
        m_frameCount = 0;
        m_fpsUpdateTime = currentTime;
    }
    
    // Emit simulation time
    if (m_simulation && m_simulation->getWaveField()) {
        emit simulationTimeUpdated(m_simulation->getWaveField()->getTime());
    }
}

void WaveSimulationWidget::resizeGL(int width, int height) {
    glViewport(0, 0, width, height);
}

void WaveSimulationWidget::setupProjection() {
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    
    // Setup orthographic projection to match simulation bounds
    glOrtho(m_viewBounds.xMin, m_viewBounds.xMax, 
            m_viewBounds.yMin, m_viewBounds.yMax, 
            -1.0, 1.0);
    
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
}

void WaveSimulationWidget::drawWaveField() {
    if (!m_simulation || !m_simulation->getWaveField()) return;
    
    const auto& grid = m_simulation->getWaveField()->getGrid();
    const auto& boundaryMask = m_simulation->getWaveField()->getBoundaryMask();
    const int gridSize = m_viewBounds.gridSize;
    
    // Find min/max values for normalization
    float minVal = std::numeric_limits<float>::max();
    float maxVal = std::numeric_limits<float>::lowest();
    
    for (int i = 0; i < gridSize; i++) {
        for (int j = 0; j < gridSize; j++) {
            int index = i * gridSize + j;
            if (boundaryMask[index]) {
                minVal = std::min(minVal, grid[index]);
                maxVal = std::max(maxVal, grid[index]);
            }
        }
    }
    
    float range = std::max(std::abs(minVal), std::abs(maxVal));
    if (range < 1e-10f) return; // No significant wave activity
    
    // Calculate grid spacing
    float dx = (m_viewBounds.xMax - m_viewBounds.xMin) / (gridSize - 1);
    float dy = (m_viewBounds.yMax - m_viewBounds.yMin) / (gridSize - 1);
    float halfDx = dx * 0.5f;
    float halfDy = dy * 0.5f;
    
    glBegin(GL_QUADS);
    
    for (int i = 0; i < gridSize; i++) {
        for (int j = 0; j < gridSize; j++) {
            int index = i * gridSize + j;
            
            if (!boundaryMask[index]) continue;
            
            float normalizedValue = grid[index] / range;
            float intensity = std::abs(normalizedValue);
            
            float r, g, b, a;
            waveValueToColor(normalizedValue, range, r, g, b, a);
            glColor4f(r, g, b, a);
            
            // Calculate quad corners
            float x = m_viewBounds.xMin + j * dx;
            float y = m_viewBounds.yMax - i * dy;
            
            glVertex2f(x - halfDx, y - halfDy);
            glVertex2f(x + halfDx, y - halfDy);
            glVertex2f(x + halfDx, y + halfDy);
            glVertex2f(x - halfDx, y + halfDy);
        }
    }
    
    glEnd();
}

void WaveSimulationWidget::drawParabolas() {
    if (!m_simulation) return;
    
    glLineWidth(2.0f);
    
    // Draw major parabola
    glColor3f(0.2f, 0.2f, 0.2f);
    glBegin(GL_LINE_STRIP);
    
    auto majorParabola = m_simulation->getMajorParabola();
    auto majorParams = majorParabola->getParams();
    
    for (float x = -majorParams.diameter / 2.0f; x <= majorParams.diameter / 2.0f; x += 5.0f) {
        float y = static_cast<float>(majorParabola->getY(x));
        glVertex2f(x, y);
    }
    glEnd();
    
    // Draw minor parabola
    glBegin(GL_LINE_STRIP);
    
    auto minorParabola = m_simulation->getMinorParabola();
    auto minorParams = minorParabola->getParams();
    
    for (float x = -minorParams.diameter / 2.0f; x <= minorParams.diameter / 2.0f; x += 5.0f) {
        float y = static_cast<float>(minorParabola->getY(x));
        glVertex2f(x, y);
    }
    glEnd();
    
    // Draw focus point
    glColor3f(1.0f, 0.0f, 0.0f);
    glPointSize(8.0f);
    glBegin(GL_POINTS);
    auto focus = m_simulation->getFocusPoint();
    glVertex2f(static_cast<float>(focus.x), static_cast<float>(focus.y));
    glEnd();
}

void WaveSimulationWidget::waveValueToColor(float value, float maxVal, float& r, float& g, float& b, float& a) {
    float intensity = std::abs(value) / maxVal;
    intensity = std::clamp(intensity, 0.0f, 1.0f);
    
    if (value > 0) {
        // Positive values in red
        r = intensity;
        g = 0.0f;
        b = 0.0f;
    } else {
        // Negative values in blue
        r = 0.0f;
        g = 0.0f;
        b = intensity;
    }
    
    a = intensity * 0.8f; // Some transparency
}

void WaveSimulationWidget::updateSimulation() {
    if (!m_isRunning || !m_simulation) return;
    
    double currentTime = m_frameTimer.elapsed() / 1000.0;
    double deltaTime = currentTime - m_lastFrameTime;
    m_lastFrameTime = currentTime;
    
    // Get the CFL-compliant time step
    double cflTimeStep = m_simulation->getCFLTimeStep();
    
    // Apply simulation speed scaling to target frame time
    double targetFrameTime = deltaTime * (m_simulationSpeed / 100.0);
    
    // Calculate how many CFL steps to run per frame to achieve the target time progression
    int stepsPerFrame = static_cast<int>(targetFrameTime / cflTimeStep);
    stepsPerFrame = std::max(1, std::min(stepsPerFrame, 100)); // Clamp between 1 and 100 steps
    
    // Update simulation multiple times with CFL-compliant time step
    for (int i = 0; i < stepsPerFrame; i++) {
        m_simulation->update(cflTimeStep);
    }
}

void WaveSimulationWidget::startSimulation() {
    if (!m_isRunning) {
        m_isRunning = true;
        m_lastFrameTime = m_frameTimer.elapsed() / 1000.0;
        m_updateTimer->start();
    }
}

void WaveSimulationWidget::stopSimulation() {
    if (m_isRunning) {
        m_isRunning = false;
        m_updateTimer->stop();
    }
}

void WaveSimulationWidget::resetSimulation() {
    bool wasRunning = m_isRunning;
    stopSimulation();
    
    if (m_simulation) {
        m_simulation->reset();
        update(); // Trigger redraw
    }
    
    if (wasRunning) {
        startSimulation();
    }
}

void WaveSimulationWidget::setFrequency(double frequency) {
    if (m_simulation) {
        m_simulation->setFrequency(frequency);
    }
}

void WaveSimulationWidget::setAmplitude(double amplitude) {
    if (m_simulation) {
        m_simulation->setAmplitude(amplitude);
    }
}

void WaveSimulationWidget::setSimulationSpeed(int speed) {
    m_simulationSpeed = std::clamp(speed, 1, 100);
}

} // namespace WaveSimulation

#include "WaveSimulationWidget.moc"
