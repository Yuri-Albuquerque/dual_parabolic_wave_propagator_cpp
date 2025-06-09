#!/usr/bin/env python3
"""
Setup script for Dual Parabolic Wave Simulation Package
"""

from setuptools import setup, find_packages, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11

# Define the C++ extension using pybind11
ext_modules = [
    Pybind11Extension(
        "dual_parabolic_wave.core",
        [
            "python/src/python_bindings.cpp",
            "src/WaveField.cpp",
            "src/Parabola.cpp", 
            "src/DualParabolicWaveSimulation.cpp"
        ],
        include_dirs=[
            "include",
            pybind11.get_include(),
        ],
        language='c++',
        cxx_std=17,
    ),
]

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dual-parabolic-wave",
    version="1.0.0",
    author="Dual Parabolic Wave Team",
    author_email="info@example.com",
    description="High-performance dual parabolic wave propagation simulation with Python interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/dual-parabolic-wave",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "plotly>=5.0.0",
        "gradio>=4.0.0",
        "scipy>=1.7.0",
        "pillow>=8.0.0",
        "pybind11>=2.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "dual-wave-viz=dual_parabolic_wave.cli:main",
            "dual-wave-gradio=dual_parabolic_wave.gradio_app:launch",
        ],
    },
    include_package_data=True,
    package_data={
        "dual_parabolic_wave": ["*.json", "*.yaml", "templates/*"],
    },
)
