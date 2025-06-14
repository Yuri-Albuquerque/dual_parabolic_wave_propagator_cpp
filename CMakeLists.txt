cmake_minimum_required(VERSION 3.16)
project(DualParabolicWaveSimulation)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Option to build with or without Qt GUI
option(BUILD_GUI "Build with Qt GUI" OFF)
option(BUILD_PYTHON_BINDINGS "Build Python bindings with pybind11" OFF)

if(BUILD_GUI)
    # Find Qt6 components for GUI version
    find_package(Qt6 REQUIRED COMPONENTS Core Widgets OpenGL OpenGLWidgets)
    
    # Enable Qt's automatic MOC, UIC, and RCC
    set(CMAKE_AUTOMOC ON)
    set(CMAKE_AUTOUIC ON)
    set(CMAKE_AUTORCC ON)
    
    add_compile_definitions(ENABLE_GUI)
endif()

# Find OpenMP for parallel processing
find_package(OpenMP)

# Include directories
include_directories(include)

# Source files - different sources based on GUI/console mode
if(BUILD_GUI)
    set(SOURCES
        src/main.cpp
        src/MainWindow.cpp
        src/WaveSimulationWidget.cpp
        src/WaveField.cpp
        src/Parabola.cpp
        src/DualParabolicWaveSimulation.cpp
    )
    
    set(HEADERS
        include/MainWindow.h
        include/WaveSimulationWidget.h
        include/WaveField.h
        include/Parabola.h
        include/DualParabolicWaveSimulation.h
        include/Types.h
    )
else()
    # Console-only version
    set(SOURCES
        src/main_console.cpp
        src/WaveField.cpp
        src/Parabola.cpp
        src/DualParabolicWaveSimulation.cpp
    )
    
    set(HEADERS
        include/WaveField.h
        include/Parabola.h
        include/DualParabolicWaveSimulation.h
        include/Types.h
    )
    
    # Also create wave data exporter
    add_executable(WaveDataExporter
        src/wave_data_exporter.cpp
        src/WaveField.cpp
        src/Parabola.cpp
        src/DualParabolicWaveSimulation.cpp
    )
    
    # Link OpenMP to data exporter if available
    if(OpenMP_CXX_FOUND)
        target_link_libraries(WaveDataExporter PRIVATE OpenMP::OpenMP_CXX)
    endif()
endif()

# Create executable
add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

# Link libraries based on build mode
if(BUILD_GUI)
    target_link_libraries(${PROJECT_NAME} 
        Qt6::Core 
        Qt6::Widgets 
        Qt6::OpenGL 
        Qt6::OpenGLWidgets
    )
endif()

# Link OpenMP if available
if(OpenMP_CXX_FOUND)
    target_link_libraries(${PROJECT_NAME} OpenMP::OpenMP_CXX)
    target_compile_definitions(${PROJECT_NAME} PRIVATE ENABLE_OPENMP)
endif()

# Compiler optimizations for performance
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    target_compile_options(${PROJECT_NAME} PRIVATE -O3 -march=native -DNDEBUG)
endif()

# Set output directory
set_target_properties(${PROJECT_NAME} PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

# Set output directory for data exporter if it exists
if(TARGET WaveDataExporter)
    set_target_properties(WaveDataExporter PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    )
endif()

# Python bindings with pybind11
if(BUILD_PYTHON_BINDINGS)
    # Try to find pybind11 using pip installation
    execute_process(
        COMMAND python3 -m pybind11 --cmakedir
        OUTPUT_VARIABLE pybind11_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE pybind11_FOUND
    )
    
    if(pybind11_FOUND EQUAL 0)
        set(pybind11_DIR ${pybind11_DIR})
        find_package(pybind11 REQUIRED PATHS ${pybind11_DIR})
    else()
        # Fallback: try to find pybind11 normally
        find_package(pybind11 REQUIRED)
    endif()
    
    # Create Python module
    pybind11_add_module(dual_parabolic_wave_cpp 
        src/python_bindings.cpp
        src/WaveField.cpp
        src/Parabola.cpp
        src/DualParabolicWaveSimulation.cpp
    )
    
    # Link OpenMP if available
    if(OpenMP_CXX_FOUND)
        target_link_libraries(dual_parabolic_wave_cpp PRIVATE OpenMP::OpenMP_CXX)
    endif()
    
    # Compiler-specific options for Python module
    target_compile_definitions(dual_parabolic_wave_cpp PRIVATE VERSION_INFO="${PROJECT_VERSION}")
    
    # Set output directory for Python module
    set_target_properties(dual_parabolic_wave_cpp PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/python
    )
endif()

# Copy any resources if needed
# file(COPY resources DESTINATION ${CMAKE_BINARY_DIR})
