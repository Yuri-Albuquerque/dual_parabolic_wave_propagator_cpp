#include "MainWindow.h"
#include <QApplication>
#include <QStatusBar>
#include <QMenuBar>
#include <QAction>
#include <QSplitter>
#include <QFormLayout>
#include <QGroupBox>

namespace WaveSimulation {

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent), m_simulationWidget(nullptr), m_controlPanel(nullptr) {
    setupUI();
    setupStatusBar();
    updateControlsState();
    
    setWindowTitle("Dual Parabolic Wave Propagation Simulation - C++/Qt");
    setMinimumSize(1200, 800);
    resize(1400, 900);
}

void MainWindow::setupUI() {
    // Create central widget with splitter
    auto* centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);
    
    auto* mainLayout = new QHBoxLayout(centralWidget);
    auto* splitter = new QSplitter(Qt::Horizontal, this);
    mainLayout->addWidget(splitter);
    
    // Create simulation widget
    m_simulationWidget = new WaveSimulationWidget(this);
    splitter->addWidget(m_simulationWidget);
    
    // Setup control panel
    setupControlPanel();
    splitter->addWidget(m_controlPanel);
    
    // Set splitter proportions (80% simulation, 20% controls)
    splitter->setStretchFactor(0, 4);
    splitter->setStretchFactor(1, 1);
    
    // Connect signals
    connect(m_simulationWidget, &WaveSimulationWidget::fpsUpdated,
            this, &MainWindow::onFpsUpdated);
    connect(m_simulationWidget, &WaveSimulationWidget::simulationTimeUpdated,
            this, &MainWindow::onSimulationTimeUpdated);
}

void MainWindow::setupControlPanel() {
    m_controlPanel = new QWidget(this);
    m_controlPanel->setFixedWidth(300);
    m_controlPanel->setMaximumWidth(350);
    
    auto* layout = new QVBoxLayout(m_controlPanel);
    
    // Control buttons group
    auto* controlGroup = new QGroupBox("Simulation Control", this);
    auto* controlLayout = new QVBoxLayout(controlGroup);
    
    m_startButton = new QPushButton("Start", this);
    m_stopButton = new QPushButton("Stop", this);
    m_resetButton = new QPushButton("Reset", this);
    
    m_startButton->setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; }");
    m_stopButton->setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 8px; }");
    m_resetButton->setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px; }");
    
    controlLayout->addWidget(m_startButton);
    controlLayout->addWidget(m_stopButton);
    controlLayout->addWidget(m_resetButton);
    
    // Wave parameters group
    auto* paramGroup = new QGroupBox("Wave Parameters", this);
    auto* paramLayout = new QFormLayout(paramGroup);
    
    m_frequencySpinBox = new QDoubleSpinBox(this);
    m_frequencySpinBox->setRange(100.0, 5000.0);
    m_frequencySpinBox->setValue(1000.0);
    m_frequencySpinBox->setSuffix(" Hz");
    m_frequencySpinBox->setDecimals(0);
    paramLayout->addRow("Frequency:", m_frequencySpinBox);
    
    m_amplitudeSpinBox = new QDoubleSpinBox(this);
    m_amplitudeSpinBox->setRange(0.1, 10.0);
    m_amplitudeSpinBox->setValue(1.0);
    m_amplitudeSpinBox->setSingleStep(0.1);
    m_amplitudeSpinBox->setDecimals(1);
    paramLayout->addRow("Amplitude:", m_amplitudeSpinBox);
    
    // Simulation speed group
    auto* speedGroup = new QGroupBox("Simulation Speed", this);
    auto* speedLayout = new QVBoxLayout(speedGroup);
    
    m_simulationSpeedSlider = new QSlider(Qt::Horizontal, this);
    m_simulationSpeedSlider->setRange(1, 100);
    m_simulationSpeedSlider->setValue(100);
    m_simulationSpeedSlider->setTickPosition(QSlider::TicksBelow);
    m_simulationSpeedSlider->setTickInterval(25);
    
    m_simulationSpeedLabel = new QLabel("100%", this);
    m_simulationSpeedLabel->setAlignment(Qt::AlignCenter);
    
    speedLayout->addWidget(m_simulationSpeedSlider);
    speedLayout->addWidget(m_simulationSpeedLabel);
    
    // Information group
    auto* infoGroup = new QGroupBox("Information", this);
    auto* infoLayout = new QVBoxLayout(infoGroup);
    
    m_fpsLabel = new QLabel("FPS: 0.0", this);
    m_timeLabel = new QLabel("Time: 0.000s", this);
    m_parametersLabel = new QLabel(
        "Major parabola: 20\" (508mm) ⌀, 100mm focus\n"
        "Minor parabola: 100mm ⌀, 50mm focus\n"
        "Grid: 300×300\n"
        "Sound speed: 343 m/s", this);
    m_parametersLabel->setWordWrap(true);
    m_parametersLabel->setStyleSheet("QLabel { font-size: 9pt; color: #666; }");
    
    infoLayout->addWidget(m_fpsLabel);
    infoLayout->addWidget(m_timeLabel);
    infoLayout->addWidget(m_parametersLabel);
    
    // Add all groups to main layout
    layout->addWidget(controlGroup);
    layout->addWidget(paramGroup);
    layout->addWidget(speedGroup);
    layout->addWidget(infoGroup);
    layout->addStretch(); // Push everything to top
    
    // Connect control signals
    connect(m_startButton, &QPushButton::clicked, this, &MainWindow::onStartClicked);
    connect(m_stopButton, &QPushButton::clicked, this, &MainWindow::onStopClicked);
    connect(m_resetButton, &QPushButton::clicked, this, &MainWindow::onResetClicked);
    
    connect(m_frequencySpinBox, QOverload<double>::of(&QDoubleSpinBox::valueChanged),
            this, &MainWindow::onFrequencyChanged);
    connect(m_amplitudeSpinBox, QOverload<double>::of(&QDoubleSpinBox::valueChanged),
            this, &MainWindow::onAmplitudeChanged);
    connect(m_simulationSpeedSlider, &QSlider::valueChanged,
            this, &MainWindow::onSimulationSpeedChanged);
}

void MainWindow::setupStatusBar() {
    statusBar()->showMessage("Ready - Click Start to begin simulation");
}

void MainWindow::onStartClicked() {
    if (!m_isRunning) {
        m_simulationWidget->startSimulation();
        m_isRunning = true;
        updateControlsState();
        statusBar()->showMessage("Simulation running...");
    }
}

void MainWindow::onStopClicked() {
    if (m_isRunning) {
        m_simulationWidget->stopSimulation();
        m_isRunning = false;
        updateControlsState();
        statusBar()->showMessage("Simulation stopped");
    }
}

void MainWindow::onResetClicked() {
    m_simulationWidget->resetSimulation();
    statusBar()->showMessage("Simulation reset");
}

void MainWindow::onFrequencyChanged() {
    double frequency = m_frequencySpinBox->value();
    m_simulationWidget->setFrequency(frequency);
    statusBar()->showMessage(QString("Frequency changed to %1 Hz").arg(frequency, 0, 'f', 0));
}

void MainWindow::onAmplitudeChanged() {
    double amplitude = m_amplitudeSpinBox->value();
    m_simulationWidget->setAmplitude(amplitude);
    statusBar()->showMessage(QString("Amplitude changed to %1").arg(amplitude, 0, 'f', 1));
}

void MainWindow::onSimulationSpeedChanged() {
    int speed = m_simulationSpeedSlider->value();
    m_simulationSpeedLabel->setText(QString("%1%").arg(speed));
    m_simulationWidget->setSimulationSpeed(speed);
}

void MainWindow::onFpsUpdated(double fps) {
    m_fpsLabel->setText(QString("FPS: %1").arg(fps, 0, 'f', 1));
}

void MainWindow::onSimulationTimeUpdated(double time) {
    m_timeLabel->setText(QString("Time: %1s").arg(time, 0, 'f', 3));
}

void MainWindow::updateControlsState() {
    m_startButton->setEnabled(!m_isRunning);
    m_stopButton->setEnabled(m_isRunning);
    
    // Allow parameter changes even while running for real-time adjustment
    m_frequencySpinBox->setEnabled(true);
    m_amplitudeSpinBox->setEnabled(true);
    m_simulationSpeedSlider->setEnabled(true);
    m_resetButton->setEnabled(true);
}

} // namespace WaveSimulation

#include "MainWindow.moc"
