#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/keysym.h>
#include <iostream>
#include <iomanip>
#include <chrono>
#include <thread>
#include <cmath>
#include <cstring>
#include <algorithm>
#include "DualParabolicWaveSimulation.h"

using namespace WaveSimulation;

class X11Visualizer {
private:
    Display* m_display;
    Window m_window;
    GC m_gc;
    XImage* m_image;
    char* m_imageData;
    int m_width;
    int m_height;
    int m_depth;
    Visual* m_visual;
    
public:
    X11Visualizer(int width = 800, int height = 600) 
        : m_width(width), m_height(height), m_imageData(nullptr) {
        
        // Open display
        m_display = XOpenDisplay(nullptr);
        if (!m_display) {
            throw std::runtime_error("Cannot open X11 display");
        }
        
        int screen = DefaultScreen(m_display);
        m_depth = DefaultDepth(m_display, screen);
        m_visual = DefaultVisual(m_display, screen);
        
        // Create window
        m_window = XCreateSimpleWindow(
            m_display,
            RootWindow(m_display, screen),
            100, 100,  // x, y
            m_width, m_height,
            1,  // border width
            BlackPixel(m_display, screen),  // border
            BlackPixel(m_display, screen)   // background
        );
        
        // Set window properties
        XStoreName(m_display, m_window, "Dual Parabolic Wave Simulation - X11");
        
        // Select input events
        XSelectInput(m_display, m_window, 
            ExposureMask | KeyPressMask | StructureNotifyMask);
        
        // Create graphics context
        m_gc = XCreateGC(m_display, m_window, 0, nullptr);
        
        // Map window
        XMapWindow(m_display, m_window);
        
        // Don't create XImage for now to avoid complications
        m_image = nullptr;
    }
    
    ~X11Visualizer() {
        if (m_imageData) delete[] m_imageData;
        if (m_image) XDestroyImage(m_image);
        if (m_gc) XFreeGC(m_display, m_gc);
        if (m_window) XDestroyWindow(m_display, m_window);
        if (m_display) XCloseDisplay(m_display);
    }
    
    void getWaveColor(double amplitude, double maxAmplitude, int& r, int& g, int& b) {
        double normalized = amplitude / (maxAmplitude + 1e-6);
        
        if (std::abs(normalized) < 0.1) {
            r = 25; g = 25; b = 50; // Dark blue for low amplitude
        } else if (normalized > 0) {
            // Positive amplitude: blue to red
            float intensity = std::min(1.0f, static_cast<float>(std::abs(normalized)));
            r = static_cast<int>(255 * intensity);
            g = static_cast<int>(50 * intensity);
            b = static_cast<int>(75 * (1.0f - intensity));
        } else {
            // Negative amplitude: blue to cyan
            float intensity = std::min(1.0f, static_cast<float>(std::abs(normalized)));
            r = static_cast<int>(25 * (1.0f - intensity));
            g = static_cast<int>(127 * intensity);
            b = static_cast<int>(255 * intensity);
        }
    }
    
    void visualizeWaveField(const WaveField& waveField) {
        auto gridSize = waveField.getGridSize();
        auto data = waveField.getCurrentData();
        
        // Find maximum amplitude for normalization
        double maxAmp = 0.0;
        for (int i = 0; i < gridSize; ++i) {
            for (int j = 0; j < gridSize; ++j) {
                if (i * gridSize + j < data.size()) {
                    double amp = std::abs(data[i * gridSize + j]);
                    maxAmp = std::max(maxAmp, amp);
                }
            }
        }
        
        // Clamp maxAmp to reasonable values to avoid numerical instability
        if (maxAmp > 100.0 || maxAmp < 1e-10) {
            maxAmp = 1.0;  // Use default amplitude if simulation is unstable
        }
        
        // Clear window to black
        XSetForeground(m_display, m_gc, BlackPixel(m_display, DefaultScreen(m_display)));
        XFillRectangle(m_display, m_window, m_gc, 0, 0, m_width, m_height);
        
        // Draw simplified visualization using rectangles instead of XImage
        for (int y = 0; y < m_height; y += 4) {  // Sample every 4 pixels for performance
            for (int x = 0; x < m_width; x += 4) {
                // Map screen coordinates to grid coordinates
                int gridI = static_cast<int>(y * double(gridSize) / m_height);
                int gridJ = static_cast<int>(x * double(gridSize) / m_width);
                
                if (gridI < gridSize && gridJ < gridSize && 
                    gridI * gridSize + gridJ < data.size()) {
                    double amplitude = data[gridI * gridSize + gridJ];
                    double normalized = amplitude / (maxAmp + 1e-6);
                    
                    // Simple color mapping
                    unsigned long color;
                    if (std::abs(normalized) < 0.1) {
                        continue; // Skip low amplitude (black background)
                    } else if (normalized > 0) {
                        // Positive amplitude - red tones
                        float intensity = std::min(1.0f, static_cast<float>(std::abs(normalized)));
                        int red = static_cast<int>(255 * intensity);
                        color = (red << 16) | (50 << 8) | 50;
                    } else {
                        // Negative amplitude - blue tones
                        float intensity = std::min(1.0f, static_cast<float>(std::abs(normalized)));
                        int blue = static_cast<int>(255 * intensity);
                        color = 50 | (100 << 8) | (blue << 16);
                    }
                    
                    XSetForeground(m_display, m_gc, color);
                    XFillRectangle(m_display, m_window, m_gc, x, y, 4, 4);
                }
            }
        }
        
        XFlush(m_display);
    }
    
    void drawStatusText(double time, double frequency, double amplitude, double fps) {
        // Set text color to white
        XSetForeground(m_display, m_gc, WhitePixel(m_display, DefaultScreen(m_display)));
        
        char statusText[256];
        snprintf(statusText, sizeof(statusText), 
                "Time: %.3fs | Freq: %.1fHz | Amp: %.2f | FPS: %.1f", 
                time, frequency, amplitude, fps);
        
        XDrawString(m_display, m_window, m_gc, 10, 20, statusText, strlen(statusText));
        
        const char* controls = "Controls: Q=Quit, P=Pause, R=Reset, +/-=Frequency, [/]=Amplitude";
        XDrawString(m_display, m_window, m_gc, 10, m_height - 10, controls, strlen(controls));
    }
    
    bool processEvents(bool& running, bool& paused, double& frequency, double& amplitude) {
        XEvent event;
        while (XPending(m_display)) {
            XNextEvent(m_display, &event);
            
            switch (event.type) {
                case KeyPress: {
                    KeySym key = XLookupKeysym(&event.xkey, 0);
                    
                    switch (key) {
                        case XK_q:
                        case XK_Q:
                        case XK_Escape:
                            running = false;
                            return false;
                            
                        case XK_p:
                        case XK_P:
                            paused = !paused;
                            break;
                            
                        case XK_r:
                        case XK_R:
                            return true; // Signal reset
                            
                        case XK_equal:
                        case XK_plus:
                            frequency = std::min(5000.0, frequency * 1.1);
                            break;
                            
                        case XK_minus:
                            frequency = std::max(100.0, frequency * 0.9);
                            break;
                            
                        case XK_bracketright:
                            amplitude = std::min(5.0, amplitude * 1.1);
                            break;
                            
                        case XK_bracketleft:
                            amplitude = std::max(0.1, amplitude * 0.9);
                            break;
                    }
                    break;
                }
                
                case Expose:
                    // Redraw needed
                    break;
                    
                case ConfigureNotify:
                    // Window resized - we could handle this but keep it simple for now
                    break;
            }
        }
        return false; // No reset requested
    }
};

int main() {
    try {
        std::cout << "🌊 Dual Parabolic Wave Simulation - X11 GUI Version\n";
        std::cout << "================================================\n\n";
        
        // Create X11 visualizer
        std::cout << "Creating X11 visualizer...\n";
        X11Visualizer visualizer(800, 600);
        std::cout << "X11 visualizer created successfully.\n";
        
        // Simulation parameters
        double frequency = 1000.0;
        double amplitude = 1.0;
        bool running = true;
        bool paused = false;
        
        // Create simulation once and reuse it
        std::cout << "Creating simulation...\n";
        DualParabolicWaveSimulation simulation;
        simulation.setFrequency(frequency);
        simulation.setAmplitude(amplitude);
        
        // Get the CFL-compliant time step
        double cflTimeStep = simulation.getCFLTimeStep();
        std::cout << "Using CFL-compliant time step: " << std::scientific << std::setprecision(6) 
                  << cflTimeStep << " seconds\n";
        std::cout << "Simulation created and configured.\n";
        
        std::cout << "Starting simulation loop...\n";
        
        // Timing for FPS calculation
        auto lastTime = std::chrono::high_resolution_clock::now();
        auto lastFpsTime = lastTime;
        int frameCount = 0;
        double fps = 0.0;
        
        while (running) {
            auto currentTime = std::chrono::high_resolution_clock::now();
            auto deltaTime = std::chrono::duration<double>(currentTime - lastTime).count();
            lastTime = currentTime;
            
            // Process events
            if (visualizer.processEvents(running, paused, frequency, amplitude)) {
                // Reset requested
                simulation.reset();
                simulation.setFrequency(frequency);
                simulation.setAmplitude(amplitude);
            }
            
            if (!paused) {
                // Calculate how many CFL steps to run per frame to achieve reasonable time progression
                // Target: advance simulation by 0.001 seconds per frame (original intention)
                double targetFrameTime = 0.001; // seconds per frame
                int stepsPerFrame = static_cast<int>(targetFrameTime / cflTimeStep);
                stepsPerFrame = std::max(1, std::min(stepsPerFrame, 100)); // Clamp between 1 and 100 steps
                
                // Update simulation multiple times with CFL-compliant time step
                for (int step = 0; step < stepsPerFrame; ++step) {
                    simulation.update(cflTimeStep);
                }
                
                // Visualize
                auto waveField = simulation.getWaveField();
                if (waveField) {
                    visualizer.visualizeWaveField(*waveField);
                    
                    // Calculate and display FPS
                    frameCount++;
                    auto fpsDelta = std::chrono::duration<double>(currentTime - lastFpsTime).count();
                    if (fpsDelta >= 1.0) {
                        fps = frameCount / fpsDelta;
                        frameCount = 0;
                        lastFpsTime = currentTime;
                    }
                    
                    double simTime = std::chrono::duration<double>(
                        currentTime.time_since_epoch()).count();
                    visualizer.drawStatusText(simTime, frequency, amplitude, fps);
                }
            } else {
                // Just process events when paused
                std::this_thread::sleep_for(std::chrono::milliseconds(16));
            }
            
            // Target 60 FPS
            std::this_thread::sleep_for(std::chrono::milliseconds(16));
        }
        
        std::cout << "\n✅ Simulation completed successfully!\n";
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
