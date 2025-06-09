#include <GL/gl.h>
#include <GL/glut.h>
#include <iostream>
#include <chrono>
#include <thread>
#include <cmath>
#include "DualParabolicWaveSimulation.h"

using namespace WaveSimulation;

// Global simulation object
DualParabolicWaveSimulation* g_simulation = nullptr;
int g_windowWidth = 800;
int g_windowHeight = 600;
bool g_running = true;
bool g_paused = false;
double g_frequency = 1000.0;
double g_amplitude = 1.0;

// Color mapping for wave visualization
void getWaveColor(double amplitude, double maxAmplitude, float& r, float& g, float& b) {
    double normalized = amplitude / (maxAmplitude + 1e-6);
    
    if (std::abs(normalized) < 0.1) {
        r = 0.1f; g = 0.1f; b = 0.2f; // Dark blue for low amplitude
    } else if (normalized > 0) {
        // Positive amplitude: blue to red
        float intensity = std::min(1.0f, static_cast<float>(std::abs(normalized)));
        r = intensity;
        g = 0.2f * intensity;
        b = 0.3f * (1.0f - intensity);
    } else {
        // Negative amplitude: blue to cyan
        float intensity = std::min(1.0f, static_cast<float>(std::abs(normalized)));
        r = 0.1f * (1.0f - intensity);
        g = 0.5f * intensity;
        b = intensity;
    }
}

void display() {
    glClear(GL_COLOR_BUFFER_BIT);
    
    if (!g_simulation) {
        glutSwapBuffers();
        return;
    }
    
    auto waveField = g_simulation->getWaveField();
    if (!waveField) {
        glutSwapBuffers();
        return;
    }
    
    auto gridSize = waveField->getGridSize();
    auto data = waveField->getCurrentData();
    
    // Find maximum amplitude for normalization
    double maxAmp = 0.0;
    for (int i = 0; i < gridSize; ++i) {
        for (int j = 0; j < gridSize; ++j) {
            double amp = std::abs(data[i * gridSize + j]);
            maxAmp = std::max(maxAmp, amp);
        }
    }
    
    // Draw wave field as colored quads
    float cellWidth = 2.0f / gridSize;
    float cellHeight = 2.0f / gridSize;
    
    glBegin(GL_QUADS);
    for (int i = 0; i < gridSize; ++i) {
        for (int j = 0; j < gridSize; ++j) {
            double amplitude = data[i * gridSize + j];
            
            float r, g, b;
            getWaveColor(amplitude, maxAmp, r, g, b);
            glColor3f(r, g, b);
            
            float x1 = -1.0f + j * cellWidth;
            float y1 = -1.0f + i * cellHeight;
            float x2 = x1 + cellWidth;
            float y2 = y1 + cellHeight;
            
            glVertex2f(x1, y1);
            glVertex2f(x2, y1);
            glVertex2f(x2, y2);
            glVertex2f(x1, y2);
        }
    }
    glEnd();
    
    // Draw title and info
    glColor3f(1.0f, 1.0f, 1.0f);
    glRasterPos2f(-0.9f, 0.9f);
    std::string title = "Dual Parabolic Wave Simulation - OpenGL Visualization";
    for (char c : title) {
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, c);
    }
    
    // Draw status
    glRasterPos2f(-0.9f, 0.85f);
    char status[256];
    snprintf(status, sizeof(status), "Freq: %.1f Hz | Amp: %.2f | %s", 
             g_frequency, g_amplitude, g_paused ? "PAUSED" : "RUNNING");
    for (int i = 0; status[i]; ++i) {
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, status[i]);
    }
    
    glutSwapBuffers();
}

void reshape(int width, int height) {
    g_windowWidth = width;
    g_windowHeight = height;
    glViewport(0, 0, width, height);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
}

void keyboard(unsigned char key, int x, int y) {
    switch (key) {
        case 'q':
        case 'Q':
        case 27: // ESC
            g_running = false;
            exit(0);
            break;
        case 'p':
        case 'P':
            g_paused = !g_paused;
            break;
        case 'r':
        case 'R':
            if (g_simulation) {
                g_simulation->reset();
            }
            break;
        case '+':
        case '=':
            g_frequency = std::min(5000.0, g_frequency * 1.1);
            if (g_simulation) {
                g_simulation->setFrequency(g_frequency);
            }
            break;
        case '-':
        case '_':
            g_frequency = std::max(100.0, g_frequency * 0.9);
            if (g_simulation) {
                g_simulation->setFrequency(g_frequency);
            }
            break;
        case '[':
            g_amplitude = std::max(0.1, g_amplitude * 0.9);
            if (g_simulation) {
                g_simulation->setAmplitude(g_amplitude);
            }
            break;
        case ']':
            g_amplitude = std::min(10.0, g_amplitude * 1.1);
            if (g_simulation) {
                g_simulation->setAmplitude(g_amplitude);
            }
            break;
    }
}

void timer(int value) {
    if (g_running && !g_paused && g_simulation) {
        // Update simulation multiple times per frame for better temporal resolution
        const double dt = 0.0001; // 0.1ms time step
        const int stepsPerFrame = 5;
        
        for (int i = 0; i < stepsPerFrame; ++i) {
            g_simulation->update(dt);
        }
    }
    
    glutPostRedisplay();
    glutTimerFunc(16, timer, 0); // ~60 FPS
}

void printInstructions() {
    std::cout << "\n=== OpenGL Dual Parabolic Wave Simulation ===" << std::endl;
    std::cout << "Controls:" << std::endl;
    std::cout << "  Q/ESC - Quit" << std::endl;
    std::cout << "  P - Pause/Resume" << std::endl;
    std::cout << "  R - Reset simulation" << std::endl;
    std::cout << "  +/- - Increase/Decrease frequency" << std::endl;
    std::cout << "  [/] - Decrease/Increase amplitude" << std::endl;
    std::cout << "\nStarting OpenGL visualization..." << std::endl;
}

int main(int argc, char* argv[]) {
    try {
        // Initialize GLUT
        glutInit(&argc, argv);
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
        glutInitWindowSize(g_windowWidth, g_windowHeight);
        glutCreateWindow("Dual Parabolic Wave Simulation - OpenGL");
        
        // Set up OpenGL
        glClearColor(0.0f, 0.0f, 0.1f, 1.0f);
        glDisable(GL_DEPTH_TEST);
        
        // Initialize simulation
        g_simulation = new DualParabolicWaveSimulation();
        g_simulation->setFrequency(g_frequency);
        g_simulation->setAmplitude(g_amplitude);
        
        printInstructions();
        
        // Set up GLUT callbacks
        glutDisplayFunc(display);
        glutReshapeFunc(reshape);
        glutKeyboardFunc(keyboard);
        glutTimerFunc(16, timer, 0);
        
        // Start main loop
        glutMainLoop();
        
        delete g_simulation;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
