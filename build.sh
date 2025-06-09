#!/bin/bash

# Build script for Dual Parabolic Wave Simulation C++/Qt
# Usage: ./build.sh [clean|debug|release]

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${PROJECT_DIR}/build"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check dependencies
check_dependencies() {
    print_info "Checking dependencies..."
    
    # Check CMake
    if ! command -v cmake &> /dev/null; then
        print_error "CMake is not installed. Please install CMake 3.16 or higher."
        exit 1
    fi
    
    CMAKE_VERSION=$(cmake --version | head -n1 | cut -d' ' -f3)
    print_info "Found CMake version: $CMAKE_VERSION"
    
    # Check Qt6
    if ! command -v qmake6 &> /dev/null && ! command -v qmake &> /dev/null; then
        print_warning "Qt6 qmake not found in PATH. Make sure Qt6 is properly installed."
    fi
    
    # Check compiler
    if command -v g++ &> /dev/null; then
        GCC_VERSION=$(g++ --version | head -n1)
        print_info "Found compiler: $GCC_VERSION"
    elif command -v clang++ &> /dev/null; then
        CLANG_VERSION=$(clang++ --version | head -n1)
        print_info "Found compiler: $CLANG_VERSION"
    else
        print_error "No suitable C++ compiler found (g++ or clang++)"
        exit 1
    fi
    
    # Check OpenMP
    if echo '#include <omp.h>' | g++ -fopenmp -x c++ -c - -o /dev/null 2>/dev/null; then
        print_info "OpenMP support: Available"
    else
        print_warning "OpenMP not available. Simulation will run single-threaded."
    fi
    
    print_success "Dependencies check completed"
}

# Function to clean build directory
clean_build() {
    print_info "Cleaning build directory..."
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
        print_success "Build directory cleaned"
    else
        print_info "Build directory doesn't exist, nothing to clean"
    fi
}

# Function to configure build
configure_build() {
    local build_type="$1"
    
    print_info "Configuring build (type: $build_type)..."
    
    # Create build directory
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"
    
    # Set Qt6 path if needed (common locations)
    local qt_paths=(
        "/usr/lib/qt6"
        "/usr/lib/x86_64-linux-gnu/qt6"
        "/opt/qt6"
        "/usr/local/qt6"
        "$HOME/Qt/6.*/gcc_64"
    )
    
    for qt_path in "${qt_paths[@]}"; do
        if [ -d "$qt_path" ] && [ -f "$qt_path/lib/cmake/Qt6/Qt6Config.cmake" ]; then
            export CMAKE_PREFIX_PATH="$qt_path:$CMAKE_PREFIX_PATH"
            print_info "Found Qt6 at: $qt_path"
            break
        fi
    done
    
    # Configure with CMake
    cmake \
        -DCMAKE_BUILD_TYPE="$build_type" \
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
        "$PROJECT_DIR"
    
    print_success "Configuration completed"
}

# Function to build project
build_project() {
    print_info "Building project..."
    
    cd "$BUILD_DIR"
    
    # Get number of CPU cores for parallel build
    NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
    print_info "Building with $NPROC parallel jobs"
    
    # Build
    make -j"$NPROC"
    
    print_success "Build completed successfully"
}

# Function to display build info
show_build_info() {
    print_info "Build Information:"
    echo "  Project Directory: $PROJECT_DIR"
    echo "  Build Directory: $BUILD_DIR"
    echo "  Executable: $BUILD_DIR/bin/DualParabolicWaveSimulation"
    echo ""
    
    if [ -f "$BUILD_DIR/bin/DualParabolicWaveSimulation" ]; then
        print_success "Executable built successfully!"
        echo ""
        echo "To run the simulation:"
        echo "  cd $BUILD_DIR"
        echo "  ./bin/DualParabolicWaveSimulation"
        echo ""
        echo "Or directly:"
        echo "  $BUILD_DIR/bin/DualParabolicWaveSimulation"
    else
        print_error "Executable not found. Build may have failed."
        exit 1
    fi
}

# Main script logic
main() {
    echo "=================================================="
    echo "  Dual Parabolic Wave Simulation - Build Script"
    echo "=================================================="
    echo ""
    
    local command="${1:-release}"
    
    case "$command" in
        "clean")
            clean_build
            ;;
        "debug")
            check_dependencies
            clean_build
            configure_build "Debug"
            build_project
            show_build_info
            ;;
        "release")
            check_dependencies
            clean_build
            configure_build "Release"
            build_project
            show_build_info
            ;;
        "run")
            if [ ! -f "$BUILD_DIR/bin/DualParabolicWaveSimulation" ]; then
                print_warning "Executable not found. Building first..."
                check_dependencies
                configure_build "Release"
                build_project
            fi
            run_application
            ;;
        "install-deps")
            print_info "Installing dependencies (Ubuntu/Debian)..."
            sudo apt update
            sudo apt install -y build-essential cmake qt6-base-dev qt6-opengl-dev libomp-dev
            print_success "Dependencies installed"
            ;;
        *)
            echo "Usage: $0 [clean|debug|release|run|install-deps]"
            echo ""
            echo "Commands:"
            echo "  clean        - Clean build directory"
            echo "  debug        - Build debug version"
            echo "  release      - Build optimized release version (default)"
            echo "  run          - Build (if needed) and run the application"
            echo "  install-deps - Install dependencies (Ubuntu/Debian only)"
            echo ""
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
