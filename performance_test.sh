#!/bin/bash

echo "=== Performance Test for C++ Dual Parabolic Wave Simulation ==="
echo ""

cd build/bin

# Run simulation for a few seconds and capture performance metrics
echo "Running 3-second performance test..."
echo ""

timeout 3s sh -c 'echo "" | ./DualParabolicWaveSimulation 2>/dev/null' | grep "Time:" | tail -5

echo ""
echo "Performance Summary:"
echo "- Grid Size: 300x300 (90,000 cells)"
echo "- Time Step: ~6.89e-07 seconds (CFL-stable)"
echo "- Parallelization: OpenMP with all available CPU cores"
echo "- Optimization: -O3 -march=native compiler flags"
echo "- Memory Layout: Flat array indexing for cache efficiency"
echo ""
echo "Expected Performance Improvement vs TypeScript:"
echo "- 10-100x faster computation (native C++ vs interpreted JS)"
echo "- Better memory management (no garbage collection pauses)"
echo "- Hardware-accelerated visualization (OpenGL vs Canvas)"
echo "- Multi-threaded wave equation solving (OpenMP)"
