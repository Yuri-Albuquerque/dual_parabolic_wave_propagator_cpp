#include <iostream>
#include <iomanip>
#include <chrono>
#include <thread>
#include <cmath>
#include <algorithm>
#include "DualParabolicWaveSimulation.h"
#include "WaveField.h"
#include "Types.h"

using namespace WaveSimulation;

class ConsoleVisualizer {
private:
    int width;
    int height;
    
public:
    ConsoleVisualizer(int w = 80, int h = 30) : width(w), height(h) {}
    
    void displayWaveField(const WaveField& field) {
        // Clear screen (ANSI escape sequence)
        std::cout << "\033[2J\033[H";
        
        const auto& amplitudes = field.getCurrentAmplitudes();
        int gridSize = field.getGridSize();
        
        // Find min/max for normalization
        double minAmp = *std::min_element(amplitudes.begin(), amplitudes.end());
        double maxAmp = *std::max_element(amplitudes.begin(), amplitudes.end());
        double range = maxAmp - minAmp;
        
        if (range < 1e-10) range = 1.0; // Prevent division by zero
        
        // Display header
        std::cout << "=== Dual Parabolic Wave Simulation ===\n";
        std::cout << "Grid Size: " << gridSize << "x" << gridSize << "\n";
        std::cout << "Amplitude Range: [" << std::fixed << std::setprecision(4) 
                  << minAmp << ", " << maxAmp << "]\n";
        std::cout << "Time: " << std::setprecision(2) << field.getCurrentTime() << "s\n\n";
        
        // Sample the field for console display
        for (int y = 0; y < height - 6; ++y) {
            for (int x = 0; x < width; ++x) {
                // Map console coordinates to field coordinates
                int fieldX = (x * gridSize) / width;
                int fieldY = (y * gridSize) / (height - 6);
                
                if (fieldX >= gridSize) fieldX = gridSize - 1;
                if (fieldY >= gridSize) fieldY = gridSize - 1;
                
                double amplitude = amplitudes[fieldY * gridSize + fieldX];
                
                // Normalize to [0, 1]
                double normalized = (amplitude - minAmp) / range;
                
                // Convert to character intensity
                char c;
                if (normalized < 0.1) c = ' ';
                else if (normalized < 0.2) c = '.';
                else if (normalized < 0.3) c = ':';
                else if (normalized < 0.4) c = '-';
                else if (normalized < 0.5) c = '=';
                else if (normalized < 0.6) c = '+';
                else if (normalized < 0.7) c = '*';
                else if (normalized < 0.8) c = '#';
                else if (normalized < 0.9) c = '%';
                else c = '@';
                
                std::cout << c;
            }
            std::cout << '\n';
        }
        
        std::cout << "\nPress Ctrl+C to exit...\n";
        std::cout.flush();
    }
};

void printSimulationInfo(const DualParabolicWaveSimulation& sim) {
    std::cout << "=== Dual Parabolic Wave Simulation - Console Mode ===\n\n";
    
    std::cout << "Configuration:\n";
    std::cout << "  Grid Size: " << sim.getGridSize() << "x" << sim.getGridSize() << "\n";
    std::cout << "  Domain Size: " << sim.getDomainSize() << " meters\n";
    std::cout << "  Wave Speed: " << sim.getWaveSpeed() << " m/s\n";
    std::cout << "  Time Step: " << sim.getTimeStep() << " seconds\n";
    std::cout << "  Simulation Speed: " << sim.getSimulationSpeed() << "x\n\n";
    
    std::cout << "Parabola Setup:\n";
    std::cout << "  Major Parabola: 20\" (508mm) diameter umbrella (concave down)\n";
    std::cout << "  Minor Parabola: 200mm diameter bowl (concave up)\n";
    std::cout << "  Focus points: Coincident for optimal wave focusing\n\n";
    
    std::cout << "Controls:\n";
    std::cout << "  Simulation runs automatically\n";
    std::cout << "  Wave visualization updates in real-time\n";
    std::cout << "  Press Ctrl+C to exit\n\n";
}

int main() {
    try {
        // Create simulation with reasonable defaults
        DualParabolicWaveSimulation simulation(
            200,    // gridSize
            2.0,    // domainSize (meters)
            343.0,  // waveSpeed (m/s, speed of sound in air)
            0.001,  // timeStep
            1.0     // simulationSpeed
        );
        
        // Initialize simulation
        simulation.initialize();
        
        // Print initial information
        printSimulationInfo(simulation);
        
        // Create console visualizer
        ConsoleVisualizer visualizer(120, 40);
        
        // Simulation loop
        const double frameRate = 30.0; // 30 FPS for visualization
        const auto frameDuration = std::chrono::microseconds(
            static_cast<long>(1000000.0 / frameRate)
        );
        
        std::cout << "Starting simulation...\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        
        auto lastFrameTime = std::chrono::high_resolution_clock::now();
        
        while (true) {
            auto currentTime = std::chrono::high_resolution_clock::now();
            auto elapsed = currentTime - lastFrameTime;
            
            if (elapsed >= frameDuration) {
                // Update simulation
                simulation.update();
                
                // Display current state
                visualizer.displayWaveField(simulation.getWaveField());
                
                lastFrameTime = currentTime;
            }
            
            // Small sleep to prevent 100% CPU usage
            std::this_thread::sleep_for(std::chrono::microseconds(100));
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    } catch (...) {
        std::cerr << "Unknown error occurred" << std::endl;
        return 1;
    }
    
    return 0;
}
