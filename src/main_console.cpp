#include <iostream>
#include <chrono>
#include <thread>
#include <iomanip>
#include <sstream>
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <cmath>
#include "DualParabolicWaveSimulation.h"

using namespace WaveSimulation;

// ANSI color codes for enhanced visualization
namespace Colors {
    const std::string RESET = "\033[0m";
    const std::string RED = "\033[31m";
    const std::string GREEN = "\033[32m";
    const std::string YELLOW = "\033[33m";
    const std::string BLUE = "\033[34m";
    const std::string MAGENTA = "\033[35m";
    const std::string CYAN = "\033[36m";
    const std::string WHITE = "\033[37m";
    const std::string BRIGHT_RED = "\033[91m";
    const std::string BRIGHT_GREEN = "\033[92m";
    const std::string BRIGHT_YELLOW = "\033[93m";
    const std::string BRIGHT_BLUE = "\033[94m";
    const std::string BRIGHT_MAGENTA = "\033[95m";
    const std::string BRIGHT_CYAN = "\033[96m";
    const std::string BRIGHT_WHITE = "\033[97m";
}

class ConsoleVisualizer {
public:
    ConsoleVisualizer(int width = 120, int height = 50) : m_width(width), m_height(height) {}
    
    void visualizeWaveField(const WaveField& waveField) {
        auto gridSize = waveField.getGridSize();
        auto data = waveField.getCurrentData();
        
        // Sample the wave field for console display
        std::vector<std::vector<std::string>> display(m_height, std::vector<std::string>(m_width, " "));
        
        double maxAmp = 0.0;
        for (int i = 0; i < gridSize; ++i) {
            for (int j = 0; j < gridSize; ++j) {
                double amp = std::abs(data[i * gridSize + j]);
                maxAmp = std::max(maxAmp, amp);
            }
        }
        
        // Map wave field to console display with colors
        for (int row = 0; row < m_height; ++row) {
            for (int col = 0; col < m_width; ++col) {
                int i = static_cast<int>(row * double(gridSize) / m_height);
                int j = static_cast<int>(col * double(gridSize) / m_width);
                
                if (i < gridSize && j < gridSize) {
                    double amp = data[i * gridSize + j];
                    double normalized = amp / (maxAmp + 1e-6);
                    
                    // Enhanced color-coded visualization
                    if (std::abs(normalized) < 0.05) {
                        display[row][col] = " ";  // Empty space for low amplitude
                    } else if (std::abs(normalized) < 0.15) {
                        display[row][col] = (normalized > 0) ? Colors::CYAN + "·" + Colors::RESET 
                                                              : Colors::BLUE + "·" + Colors::RESET;
                    } else if (std::abs(normalized) < 0.3) {
                        display[row][col] = (normalized > 0) ? Colors::GREEN + "o" + Colors::RESET 
                                                              : Colors::BLUE + "o" + Colors::RESET;
                    } else if (std::abs(normalized) < 0.5) {
                        display[row][col] = (normalized > 0) ? Colors::YELLOW + "O" + Colors::RESET 
                                                              : Colors::MAGENTA + "O" + Colors::RESET;
                    } else if (std::abs(normalized) < 0.7) {
                        display[row][col] = (normalized > 0) ? Colors::BRIGHT_RED + "●" + Colors::RESET 
                                                              : Colors::BRIGHT_BLUE + "●" + Colors::RESET;
                    } else {
                        display[row][col] = (normalized > 0) ? Colors::BRIGHT_WHITE + "●" + Colors::RESET 
                                                              : Colors::BRIGHT_CYAN + "●" + Colors::RESET;
                    }
                }
            }
        }
        
        // Clear screen and display with enhanced info header
        std::cout << "\033[2J\033[H"; // Clear screen and move cursor to top
        
        // Display border and title
        std::cout << Colors::BRIGHT_CYAN << "╔";
        for (int i = 0; i < m_width; ++i) std::cout << "═";
        std::cout << "╗" << Colors::RESET << std::endl;
        
        std::cout << Colors::BRIGHT_CYAN << "║" << Colors::RESET;
        std::string title = "  DUAL PARABOLIC WAVE SIMULATION - Real-time Visualization  ";
        int padding = (m_width - title.length()) / 2;
        for (int i = 0; i < padding; ++i) std::cout << " ";
        std::cout << Colors::BRIGHT_WHITE << title << Colors::RESET;
        for (int i = 0; i < m_width - padding - title.length(); ++i) std::cout << " ";
        std::cout << Colors::BRIGHT_CYAN << "║" << Colors::RESET << std::endl;
        
        std::cout << Colors::BRIGHT_CYAN << "╚";
        for (int i = 0; i < m_width; ++i) std::cout << "═";
        std::cout << "╝" << Colors::RESET << std::endl;
        
        // Display the wave field
        for (const auto& row : display) {
            for (const std::string& pixel : row) {
                std::cout << pixel;
            }
            std::cout << '\n';
        }
        
        // Display legend
        std::cout << "\n" << Colors::BRIGHT_WHITE << "Legend: " << Colors::RESET;
        std::cout << Colors::CYAN << "· " << Colors::RESET << "Low  ";
        std::cout << Colors::GREEN << "o " << Colors::RESET << "Med+ ";
        std::cout << Colors::BLUE << "o " << Colors::RESET << "Med- ";
        std::cout << Colors::YELLOW << "O " << Colors::RESET << "High+ ";
        std::cout << Colors::MAGENTA << "O " << Colors::RESET << "High- ";
        std::cout << Colors::BRIGHT_RED << "● " << Colors::RESET << "Max+ ";
        std::cout << Colors::BRIGHT_BLUE << "● " << Colors::RESET << "Max-" << std::endl;
    }
    
    void drawParabolaOutline(const WaveField& waveField) {
        // TODO: Add parabola boundary visualization
    }
    
private:
    int m_width, m_height;
};

void printSimulationInfo(const DualParabolicWaveSimulation& sim) {
    auto config = sim.getConfig();
    auto waveParams = sim.getWaveParams();
    auto focus = sim.getFocusPoint();
    
    std::cout << Colors::BRIGHT_CYAN << "╔══════════════════════════════════════════════════════════════╗" << Colors::RESET << std::endl;
    std::cout << Colors::BRIGHT_CYAN << "║" << Colors::BRIGHT_WHITE << "               DUAL PARABOLIC WAVE SIMULATION                 " << Colors::BRIGHT_CYAN << "║" << Colors::RESET << std::endl;
    std::cout << Colors::BRIGHT_CYAN << "╠══════════════════════════════════════════════════════════════╣" << Colors::RESET << std::endl;
    std::cout << Colors::BRIGHT_CYAN << "║" << Colors::RESET << " Grid Size: " << Colors::YELLOW << config.gridSize << "x" << config.gridSize << Colors::RESET;
    std::cout << "                                      " << Colors::BRIGHT_CYAN << "║" << Colors::RESET << std::endl;
    std::cout << Colors::BRIGHT_CYAN << "║" << Colors::RESET << " Domain: X[" << Colors::GREEN << config.xMin << ", " << config.xMax << Colors::RESET << "] mm, Y[" 
              << Colors::GREEN << config.yMin << ", " << config.yMax << Colors::RESET << "] mm     " << Colors::BRIGHT_CYAN << "║" << Colors::RESET << std::endl;
    std::cout << Colors::BRIGHT_CYAN << "║" << Colors::RESET << " Wave Speed: " << Colors::CYAN << waveParams.speed << Colors::RESET << " mm/s                              " << Colors::BRIGHT_CYAN << "║" << Colors::RESET << std::endl;
    std::cout << Colors::BRIGHT_CYAN << "║" << Colors::RESET << " Frequency: " << Colors::MAGENTA << waveParams.frequency << Colors::RESET << " Hz                                   " << Colors::BRIGHT_CYAN << "║" << Colors::RESET << std::endl;
    std::cout << Colors::BRIGHT_CYAN << "║" << Colors::RESET << " Amplitude: " << Colors::RED << waveParams.amplitude << Colors::RESET << "                                       " << Colors::BRIGHT_CYAN << "║" << Colors::RESET << std::endl;
    std::cout << Colors::BRIGHT_CYAN << "║" << Colors::RESET << " Focus Point: (" << Colors::BRIGHT_YELLOW << focus.x << ", " << focus.y << Colors::RESET << ")                            " << Colors::BRIGHT_CYAN << "║" << Colors::RESET << std::endl;
    std::cout << Colors::BRIGHT_CYAN << "╚══════════════════════════════════════════════════════════════╝" << Colors::RESET << std::endl;
}

void printControls() {
    std::cout << "\n" << Colors::BRIGHT_GREEN << "🎮 INTERACTIVE CONTROLS:" << Colors::RESET << std::endl;
    std::cout << Colors::GREEN << "  q" << Colors::RESET << " - Quit simulation" << std::endl;
    std::cout << Colors::GREEN << "  p" << Colors::RESET << " - Pause/Resume" << std::endl;
    std::cout << Colors::GREEN << "  r" << Colors::RESET << " - Reset simulation" << std::endl;
    std::cout << Colors::GREEN << "  +" << Colors::RESET << " - Increase frequency (up to 5000 Hz)" << std::endl;
    std::cout << Colors::GREEN << "  -" << Colors::RESET << " - Decrease frequency (down to 100 Hz)" << std::endl;
    std::cout << Colors::GREEN << "  [" << Colors::RESET << " - Decrease amplitude" << std::endl;
    std::cout << Colors::GREEN << "  ]" << Colors::RESET << " - Increase amplitude" << std::endl;
    std::cout << "\n" << Colors::BRIGHT_YELLOW << "Press Enter to start the real-time simulation..." << Colors::RESET << std::endl;
}

int main() {
    try {
        std::cout << "Initializing Dual Parabolic Wave Simulation..." << std::endl;
        
        DualParabolicWaveSimulation simulation;
        ConsoleVisualizer visualizer(100, 45);  // Larger display area
        
        printSimulationInfo(simulation);
        printControls();
        
        // Wait for user to start
        std::cin.get();
        
        // Get the CFL-compliant time step
        const double cflTimeStep = simulation.getCFLTimeStep();
        std::cout << "Using CFL-compliant time step: " << cflTimeStep << " seconds\n";
        
        // Simulation parameters for display timing
        const double targetFrameTime = 0.001; // Target to advance simulation by 1ms per frame
        const int frameSkip = 10; // Update display every 10 steps
        const auto frameTime = std::chrono::milliseconds(50); // 20 FPS display
        
        bool running = true;
        bool paused = false;
        int frameCount = 0;
        double currentFreq = 1000.0; // 1 kHz
        double currentAmp = 1.0;
        
        simulation.setFrequency(currentFreq);
        simulation.setAmplitude(currentAmp);
        
        auto lastFrameTime = std::chrono::steady_clock::now();
        
        std::cout << "Simulation started. Use 'q' + Enter to quit.\n" << std::endl;
        
        while (running) {
            auto currentTime = std::chrono::steady_clock::now();
            
            if (!paused) {
                // Calculate how many CFL steps to run per frame to achieve reasonable time progression
                int stepsPerFrame = static_cast<int>(targetFrameTime / cflTimeStep);
                stepsPerFrame = std::max(1, std::min(stepsPerFrame, 100)); // Clamp between 1 and 100 steps
                
                // Update simulation multiple times with CFL-compliant time step
                for (int step = 0; step < stepsPerFrame; ++step) {
                    simulation.update(cflTimeStep);
                }
                frameCount++;
                
                // Update display periodically
                if (frameCount % frameSkip == 0) {
                    auto waveField = simulation.getWaveField();
                    if (waveField) {
                        visualizer.visualizeWaveField(*waveField);
                        
                        // Show current parameters with enhanced display
                        std::cout << "\n" << Colors::BRIGHT_WHITE << "📊 STATUS: " << Colors::RESET;
                        std::cout << Colors::CYAN << "Time: " << std::fixed << std::setprecision(3) 
                                  << frameCount * targetFrameTime << "s" << Colors::RESET << " | ";
                        std::cout << Colors::MAGENTA << "Freq: " << currentFreq << "Hz" << Colors::RESET << " | ";
                        std::cout << Colors::YELLOW << "Amp: " << std::setprecision(2) << currentAmp << Colors::RESET << " | ";
                        std::cout << Colors::GREEN << "Steps/Frame: " << stepsPerFrame << Colors::RESET << " | ";
                        std::cout << Colors::BRIGHT_BLUE << "CFL dt: " << std::scientific << std::setprecision(2) 
                                  << cflTimeStep << "s" << Colors::RESET << " | ";
                        std::cout << (paused ? Colors::RED + "⏸ PAUSED" : Colors::BRIGHT_GREEN + "▶ RUNNING") << Colors::RESET << std::endl;
                    }
                }
            }
            
            // Simple input handling (non-blocking would be better but this works for demo)
            auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
                currentTime - lastFrameTime);
            
            if (elapsed >= frameTime) {
                lastFrameTime = currentTime;
                
                // Check for input (this is blocking, but works for demo)
                if (std::cin.rdbuf()->in_avail() > 0) {
                    char input;
                    std::cin >> input;
                    
                    switch (input) {
                        case 'q':
                        case 'Q':
                            running = false;
                            break;
                        case 'p':
                        case 'P':
                            paused = !paused;
                            break;
                        case 'r':
                        case 'R':
                            simulation.reset();
                            frameCount = 0;
                            break;
                        case '+':
                        case '=':
                            currentFreq = std::min(5000.0, currentFreq * 1.1);
                            simulation.setFrequency(currentFreq);
                            break;
                        case '-':
                        case '_':
                            currentFreq = std::max(100.0, currentFreq * 0.9);
                            simulation.setFrequency(currentFreq);
                            break;
                        case '[':
                            currentAmp = std::max(0.1, currentAmp * 0.9);
                            simulation.setAmplitude(currentAmp);
                            break;
                        case ']':
                            currentAmp = std::min(10.0, currentAmp * 1.1);
                            simulation.setAmplitude(currentAmp);
                            break;
                    }
                }
            } else {
                // Sleep for remaining frame time
                std::this_thread::sleep_for(frameTime - elapsed);
            }
        }
        
        std::cout << "\nSimulation finished." << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}