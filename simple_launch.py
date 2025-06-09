#!/usr/bin/env python3
"""
Simple Gradio launcher with better error handling.
"""

import sys
import os

# Fix matplotlib backend before any imports
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Add the python directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(current_dir, 'python')
if python_dir not in sys.path:
    sys.path.insert(0, python_dir)

# Verify the path exists
if not os.path.exists(python_dir):
    print(f"Error: Python directory not found: {python_dir}")
    sys.exit(1)

try:
    print("Starting Gradio app...")
    print(f"Python path: {python_dir}")
    
    # Import the module
    import dual_parabolic_wave
    print("Module imported successfully")
    
    # Use the launch_app function from the package
    dual_parabolic_wave.launch_app
    
    # Launch the app directly
    launch_app(
        share=False,
        debug=False,
        port=7860
    )
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
