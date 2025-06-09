#include <QApplication>
#include <QStyleFactory>
#include <QDir>
#include <iostream>
#include "MainWindow.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    
    // Set application metadata
    app.setApplicationName("Dual Parabolic Wave Simulation");
    app.setApplicationVersion("1.0.0");
    app.setOrganizationName("Wave Simulation Lab");
    app.setApplicationDisplayName("Dual Parabolic Wave Propagation Simulation");
    
    // Set a modern style
    app.setStyle(QStyleFactory::create("Fusion"));
    
    // Apply dark theme
    QPalette darkPalette;
    darkPalette.setColor(QPalette::Window, QColor(53, 53, 53));
    darkPalette.setColor(QPalette::WindowText, Qt::white);
    darkPalette.setColor(QPalette::Base, QColor(25, 25, 25));
    darkPalette.setColor(QPalette::AlternateBase, QColor(53, 53, 53));
    darkPalette.setColor(QPalette::ToolTipBase, Qt::white);
    darkPalette.setColor(QPalette::ToolTipText, Qt::white);
    darkPalette.setColor(QPalette::Text, Qt::white);
    darkPalette.setColor(QPalette::Button, QColor(53, 53, 53));
    darkPalette.setColor(QPalette::ButtonText, Qt::white);
    darkPalette.setColor(QPalette::BrightText, Qt::red);
    darkPalette.setColor(QPalette::Link, QColor(42, 130, 218));
    darkPalette.setColor(QPalette::Highlight, QColor(42, 130, 218));
    darkPalette.setColor(QPalette::HighlightedText, Qt::black);
    app.setPalette(darkPalette);
    
    // Print system information
    std::cout << "=== Dual Parabolic Wave Propagation Simulation ===" << std::endl;
    std::cout << "C++/Qt Implementation" << std::endl;
    std::cout << "Qt Version: " << qVersion() << std::endl;
    std::cout << "Available OpenGL: " << (QOpenGLContext::openGLModuleType() == QOpenGLContext::LibGL ? "Desktop" : "ES") << std::endl;
    std::cout << "======================================================" << std::endl;
    
    try {
        // Create and show main window
        WaveSimulation::MainWindow window;
        window.show();
        
        std::cout << "Application started successfully." << std::endl;
        std::cout << "Simulation parameters:" << std::endl;
        std::cout << "- Major parabola: 20 inches (508mm) diameter, 100mm focus" << std::endl;
        std::cout << "- Minor parabola: 100mm diameter, 50mm focus" << std::endl;
        std::cout << "- Wave frequency: 1000Hz" << std::endl;
        std::cout << "- Sound speed: 343 m/s" << std::endl;
        std::cout << "- Grid resolution: 300x300" << std::endl;
        std::cout << "\nUse the control panel to start the simulation." << std::endl;
        
        return app.exec();
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    } catch (...) {
        std::cerr << "Unknown error occurred" << std::endl;
        return 1;
    }
}
