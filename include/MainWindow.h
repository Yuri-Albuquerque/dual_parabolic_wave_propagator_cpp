#pragma once

#include <QMainWindow>
#include <QSlider>
#include <QLabel>
#include <QPushButton>
#include <QDoubleSpinBox>
#include <QGridLayout>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QSpinBox>
#include "WaveSimulationWidget.h"

namespace WaveSimulation {

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget* parent = nullptr);
    ~MainWindow() override = default;

private slots:
    void onStartClicked();
    void onStopClicked();
    void onResetClicked();
    void onFrequencyChanged();
    void onAmplitudeChanged();
    void onSimulationSpeedChanged();
    void onFpsUpdated(double fps);
    void onSimulationTimeUpdated(double time);

private:
    void setupUI();
    void setupControlPanel();
    void setupStatusBar();
    void updateControlsState();
    
    // UI Components
    WaveSimulationWidget* m_simulationWidget;
    
    // Control panel
    QWidget* m_controlPanel;
    QPushButton* m_startButton;
    QPushButton* m_stopButton;
    QPushButton* m_resetButton;
    
    // Parameter controls
    QDoubleSpinBox* m_frequencySpinBox;
    QDoubleSpinBox* m_amplitudeSpinBox;
    QSlider* m_simulationSpeedSlider;
    QLabel* m_simulationSpeedLabel;
    
    // Display labels
    QLabel* m_fpsLabel;
    QLabel* m_timeLabel;
    QLabel* m_parametersLabel;
    
    // Status
    bool m_isRunning = false;
};

} // namespace WaveSimulation
