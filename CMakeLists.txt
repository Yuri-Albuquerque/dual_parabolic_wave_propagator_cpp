cmake_minimum_required(VERSION 3.16)
project(DualParabolicWaveSimulation)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Option to build with or without Qt GUI
option(BUILD_GUI "Build with Qt GUI" OFF)

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

# Copy any resources if needed
# file(COPY resources DESTINATION ${CMAKE_BINARY_DIR})
