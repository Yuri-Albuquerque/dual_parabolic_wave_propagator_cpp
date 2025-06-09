#!/bin/bash

# Run X11 GUI Version - Dual Parabolic Wave Simulation
# =====================================================

echo "🌊 Dual Parabolic Wave Simulation - X11 GUI Runner"
echo "=================================================="

# Check if X11 build exists
if [ ! -f "build_x11/bin/DualParabolicWaveSimulation" ]; then
    echo "📦 X11 version not found. Building..."
    
    # Create build directory
    mkdir -p build_x11
    cd build_x11
    
    # Configure for X11 build
    echo "🔧 Configuring CMake for X11 build..."
    cmake -DBUILD_X11=ON -DCMAKE_BUILD_TYPE=Release ..
    
    # Build
    echo "🏗️ Building X11 GUI version..."
    make -j$(nproc)
    
    cd ..
fi

# Check if build was successful
if [ ! -f "build_x11/bin/DualParabolicWaveSimulation" ]; then
    echo "❌ Failed to build X11 version!"
    exit 1
fi

echo "🚀 Starting X11 GUI simulation..."
echo ""
echo "Controls:"
echo "  Space     - Start/Stop simulation"
echo "  R         - Reset simulation"
echo "  +/-       - Increase/Decrease frequency"
echo "  A/Z       - Increase/Decrease amplitude"  
echo "  Q/Escape  - Quit"
echo ""

# Run the X11 GUI version
cd build_x11
./bin/DualParabolicWaveSimulation
