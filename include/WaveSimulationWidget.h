#pragma once

#include <QOpenGLWidget>
#include <QOpenGLFunctions>
#include <QTimer>
#include <QElapsedTimer>
#include <memory>
#include "DualParabolicWaveSimulation.h"

namespace WaveSimulation {

class WaveSimulationWidget : public QOpenGLWidget, protected QOpenGLFunctions {
    Q_OBJECT

public:
    explicit WaveSimulationWidget(QWidget* parent = nullptr);
    ~WaveSimulationWidget() override = default;

public slots:
    void startSimulation();
    void stopSimulation();
    void resetSimulation();
    void setFrequency(double frequency);
    void setAmplitude(double amplitude);
    void setSimulationSpeed(int speed); // 1-100%

protected:
    void initializeGL() override;
    void paintGL() override;
    void resizeGL(int width, int height) override;

private slots:
    void updateSimulation();

private:
    void drawWaveField();
    void drawParabolas();
    void setupProjection();
    
    // Color mapping
    void waveValueToColor(float value, float maxVal, float& r, float& g, float& b, float& a);
    
    std::unique_ptr<DualParabolicWaveSimulation> m_simulation;
    QTimer* m_updateTimer;
    QElapsedTimer m_frameTimer;
    
    bool m_isRunning = false;
    int m_simulationSpeed = 100; // percentage
    double m_lastFrameTime = 0.0;
    
    // OpenGL resources
    struct {
        float xMin, xMax, yMin, yMax;
        int gridSize;
    } m_viewBounds;
    
    // Performance monitoring
    int m_frameCount = 0;
    double m_fpsUpdateTime = 0.0;
    double m_currentFPS = 0.0;
    
signals:
    void fpsUpdated(double fps);
    void simulationTimeUpdated(double time);
};

} // namespace WaveSimulation
