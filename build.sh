#!/bin/bash

# Build script for Dual Parabolic Wave Simulation C++/Qt
echo "==================================================" 
echo "  Dual Parabolic Wave Simulation - Build Script"
echo "=================================================="
echo ""

# Check dependencies first
echo "[INFO] Checking dependencies..."

# Check CMake
if ! command -v cmake >/dev/null 2>&1; then
    echo "[ERROR] CMake is not installed. Please install CMake 3.16 or higher."
    exit 1
fi

CMAKE_VERSION=$(cmake --version | head -n1 | cut -d' ' -f3)
echo "[INFO] Found CMake version: $CMAKE_VERSION"

# Check compiler
if command -v g++ >/dev/null 2>&1; then
    GCC_VERSION=$(g++ --version | head -n1)
    echo "[INFO] Found compiler: $GCC_VERSION"
elif command -v clang++ >/dev/null 2>&1; then
    CLANG_VERSION=$(clang++ --version | head -n1)
    echo "[INFO] Found compiler: $CLANG_VERSION"
else
    echo "[ERROR] No suitable C++ compiler found (g++ or clang++)"
    exit 1
fi

# Clean and create build directory
echo "[INFO] Cleaning and preparing build directory..."
rm -rf build
mkdir -p build
cd build

# Configure with CMake
echo "[INFO] Configuring build..."
cmake -DCMAKE_BUILD_TYPE=Release ..

# Build
echo "[INFO] Building project..."
make -j$(nproc)

echo "[SUCCESS] Build completed!"
echo "Executable: $(pwd)/bin/DualParabolicWaveSimulation"
