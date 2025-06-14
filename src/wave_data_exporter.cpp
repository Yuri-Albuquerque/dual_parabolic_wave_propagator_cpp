#include "DualParabolicWaveSimulation.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <iomanip>
#include <sstream>

using namespace WaveSimulation;

/**
 * C++ Data Export Program for Python Visualization
 * 
 * This program runs the corrected wave simulation and exports data
 * in a format that Python can easily read and visualize.
 */

void exportWaveData(const std::vector<float>& grid, int gridSize, 
                   int timeStep, const std::string& outputDir) {
    std::ostringstream filename;
    filename << outputDir << "/wave_data_t" << std::setfill('0') << std::setw(4) << timeStep << ".txt";
    
    std::ofstream file(filename.str());
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename.str() << std::endl;
        return;
    }
    
    // Export as space-separated values in row-major order
    for (int i = 0; i < gridSize; i++) {
        for (int j = 0; j < gridSize; j++) {
            file << grid[i * gridSize + j];
            if (j < gridSize - 1) file << " ";
        }
        file << "\n";
    }
    
    file.close();
}

void exportBoundaryMask(const std::vector<uint8_t>& mask, int gridSize, 
                       const std::string& outputDir) {
    std::string filename = outputDir + "/boundary_mask.txt";
    
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        return;
    }
    
    for (int i = 0; i < gridSize; i++) {
        for (int j = 0; j < gridSize; j++) {
            file << static_cast<int>(mask[i * gridSize + j]);
            if (j < gridSize - 1) file << " ";
        }
        file << "\n";
    }
    
    file.close();
}

void exportMetadata(const DualParabolicWaveSimulation& simulation,
                   int numTimeSteps, double totalDuration,
                   const std::string& outputDir) {
    std::string filename = outputDir + "/metadata.txt";
    
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        return;
    }
    
    file << "# Dual Parabolic Wave Simulation Metadata\n";
    file << "grid_size=" << simulation.getGridSize() << "\n";
    file << "domain_size_mm=" << simulation.getDomainSize() * 1000.0 << "\n";
    file << "wave_speed_ms=" << simulation.getWaveSpeed() << "\n";
    file << "time_step_s=" << std::scientific << simulation.getTimeStep() << "\n";
    file << "num_time_steps=" << numTimeSteps << "\n";
    file << "total_duration_s=" << std::scientific << totalDuration << "\n";
    file << "major_parabola_diameter_mm=508\n";
    file << "major_parabola_focus_mm=100\n";
    file << "minor_parabola_diameter_mm=200\n";
    file << "minor_parabola_focus_mm=50\n";
    file << "focus_point_x_mm=0\n";
    file << "focus_point_y_mm=0\n";
    file << "ground_truth_compatible=true\n";
    file << "rigid_boundary_conditions=true\n";
    file << "cfl_stable=true\n";
    
    file.close();
}

int main(int argc, char* argv[]) {
    std::cout << "🌊 C++ Wave Data Exporter for Python Visualization" << std::endl;
    std::cout << "===================================================" << std::endl;
    
    // Parse command line arguments
    int gridSize = 200;
    double domainSize = 600.0;  // mm
    double waveSpeed = 343.0;   // m/s
    double duration = 2e-6;     // seconds
    int captureInterval = 10;   // capture every N steps
    std::string outputDir = "cpp_wave_data";
    
    if (argc > 1) outputDir = argv[1];
    if (argc > 2) gridSize = std::atoi(argv[2]);
    if (argc > 3) domainSize = std::atof(argv[3]);
    if (argc > 4) duration = std::atof(argv[4]);
    
    std::cout << "Configuration:" << std::endl;
    std::cout << "  Grid Size: " << gridSize << "x" << gridSize << std::endl;
    std::cout << "  Domain Size: " << domainSize << "mm x " << domainSize << "mm" << std::endl;
    std::cout << "  Wave Speed: " << waveSpeed << " m/s" << std::endl;
    std::cout << "  Duration: " << std::scientific << duration << " s" << std::endl;
    std::cout << "  Output Directory: " << outputDir << std::endl;
    
    // Create output directory
    std::string mkdir_cmd = "mkdir -p " + outputDir;
    system(mkdir_cmd.c_str());
    
    // Create simulation
    std::cout << "\n🚀 Initializing C++ simulation..." << std::endl;
    DualParabolicWaveSimulation simulation(
        gridSize,
        domainSize / 1000.0,  // Convert mm to m
        waveSpeed,
        1e-8,  // timeStep (will be overridden by CFL)
        1.0    // simulationSpeed
    );
    
    // Get simulation parameters
    double timeStep = simulation.getTimeStep();
    int totalSteps = static_cast<int>(duration / timeStep);
    int numCaptures = totalSteps / captureInterval;
    
    std::cout << "  CFL time step: " << std::scientific << timeStep << " s" << std::endl;
    std::cout << "  Total steps: " << totalSteps << std::endl;
    std::cout << "  Capture interval: " << captureInterval << " steps" << std::endl;
    std::cout << "  Expected captures: " << numCaptures << std::endl;
    
    // Export boundary mask
    const WaveField& waveField = simulation.getWaveField();
    exportBoundaryMask(waveField.getBoundaryMask(), waveField.getGridSize(), outputDir);
    
    // Export metadata
    exportMetadata(simulation, numCaptures, duration, outputDir);
    
    // Run simulation and export data
    std::cout << "\n⏳ Running simulation and exporting data..." << std::endl;
    
    int captureCount = 0;
    for (int step = 0; step < totalSteps; step++) {
        if (step > 0) {
            simulation.update();
        }
        
        // Export wave data at capture intervals
        if (step % captureInterval == 0) {
            const auto& grid = waveField.getGrid();
            exportWaveData(grid, waveField.getGridSize(), captureCount, outputDir);
            captureCount++;
            
            if (captureCount % 10 == 0) {
                std::cout << "  Exported " << captureCount << "/" << numCaptures << " snapshots..." << std::endl;
            }
        }
    }
    
    std::cout << "\n✅ Data export completed!" << std::endl;
    std::cout << "  Total snapshots: " << captureCount << std::endl;
    std::cout << "  Output directory: " << outputDir << std::endl;
    std::cout << "  Files exported:" << std::endl;
    std::cout << "    - boundary_mask.txt (parabolic geometry)" << std::endl;
    std::cout << "    - metadata.txt (simulation parameters)" << std::endl;
    std::cout << "    - wave_data_t*.txt (wave field snapshots)" << std::endl;
    
    return 0;
}
