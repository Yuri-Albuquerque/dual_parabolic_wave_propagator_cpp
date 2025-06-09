#!/usr/bin/env python3
"""
Debug Gradio launcher with detailed output.
"""

import sys
import os

# Fix matplotlib backend before any imports
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

print("Step 1: Setting up path...")
# Add the python directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)
print(f"Added to path: {python_dir}")

print("Step 2: Importing gradio...")
try:
    import gradio as gr
    print("Gradio imported successfully!")
except Exception as e:
    print(f"Error importing gradio: {e}")
    sys.exit(1)

print("Step 3: Importing our module...")
try:
    from dual_parabolic_wave.gradio_app import launch_app
    print("Module imported successfully!")
except Exception as e:
    print(f"Error importing module: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 4: Launching app...")
try:
    # Launch the app directly
    launch_app(
        share=False,
        debug=True,
        port=7860
    )
except Exception as e:
    print(f"Error launching app: {e}")
    import traceback
    traceback.print_exc()
