#!/usr/bin/env python3
"""
Standalone Gradio launcher that doesn't depend on complex imports.
"""

import sys
import os

# Fix matplotlib backend before any imports
import matplotlib
matplotlib.use('Agg')

def launch_gradio():
    """Launch the Gradio app with minimal dependencies."""
    
    # Add the python directory to the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    python_dir = os.path.join(current_dir, 'python')
    
    if python_dir not in sys.path:
        sys.path.insert(0, python_dir)
    
    print(f"Adding to Python path: {python_dir}")
    
    try:
        # Test basic imports first
        print("Testing imports...")
        import numpy as np
        print("✓ numpy imported")
        
        import gradio as gr
        print("✓ gradio imported")
        
        import plotly.graph_objects as go
        print("✓ plotly imported")
        
        # Import our simulation module
        print("Importing simulation module...")
        from dual_parabolic_wave.simulation import Simulation
        print("✓ simulation module imported")
        
        # Import visualization
        print("Importing visualization module...")
        from dual_parabolic_wave.visualization import plot_wave_field_3d
        print("✓ visualization module imported")
        
        # Import and run the Gradio app
        print("Importing Gradio app...")
        from dual_parabolic_wave.gradio_app import launch_app
        print("✓ gradio_app module imported")
        
        print("\n🚀 Launching Gradio app...")
        launch_app(share=False, debug=False, port=7860)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nDebugging info:")
        print(f"Python path: {sys.path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python directory exists: {os.path.exists(python_dir)}")
        if os.path.exists(python_dir):
            print(f"Contents of python dir: {os.listdir(python_dir)}")
        return 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(launch_gradio())
