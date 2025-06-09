#!/usr/bin/env python3
"""
Launch script for the Dual Parabolic Wave Simulation Gradio web interface.
"""

import sys
import os

# Add the python directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

# Import and launch the app
from dual_parabolic_wave.gradio_app import launch_app

if __name__ == "__main__":
    print("🌊 Dual Parabolic Wave Simulation - Gradio Web Interface")
    print("=" * 60)
    print("🚀 Starting web server...")
    print("📱 Features:")
    print("   • Interactive simulation control")
    print("   • Real-time 3D visualization")  
    print("   • Morlet wavelet source excitation")
    print("   • Performance analysis")
    print("   • Export capabilities")
    print("=" * 60)
    
    # Launch with sensible defaults
    try:
        launch_app(
            share=False,     # Set to True to create public link
            debug=False,     # Set to True for development
            port=7860       # Default Gradio port
        )
    except KeyboardInterrupt:
        print("\n👋 Gracefully shutting down...")
    except Exception as e:
        print(f"\n❌ Error launching app: {e}")
        sys.exit(1)
