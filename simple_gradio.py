#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

import gradio as gr
from dual_parabolic_wave.simulation import DualParabolicWaveSimulation
import numpy as np
import plotly.graph_objects as go

def create_simple_interface():
    """Create a simplified Gradio interface for testing"""
    
    def run_simulation(frequency, amplitude, grid_size, steps):
        # Create simulation
        sim = DualParabolicWaveSimulation(
            grid_size=int(grid_size),
            domain_size=1.0,
            frequency=frequency,
            amplitude=amplitude,
            wave_speed=343.0,
            time_step=0.0001
        )
        
        sim.initialize()
        
        # Run simulation steps
        for _ in range(int(steps)):
            sim.step()
        
        # Get wave field data
        wave_field = sim.get_wave_field()
        
        # Create simple 2D plot
        fig = go.Figure(data=go.Heatmap(z=wave_field, colorscale='RdBu'))
        fig.update_layout(title=f"Morlet Wavelet Simulation (f={frequency}Hz, t={sim.get_current_time():.6f}s)")
        
        return fig, f"Simulation completed: {steps} steps, max amplitude: {wave_field.max():.6f}"
    
    # Create interface
    with gr.Blocks(title="Dual Parabolic Wave Simulation - Morlet Wavelet") as interface:
        gr.Markdown("# 🌊 Dual Parabolic Wave Simulation with Morlet Wavelet")
        
        with gr.Row():
            frequency = gr.Slider(100, 2000, value=1000, label="Frequency (Hz)")
            amplitude = gr.Slider(0.1, 2.0, value=1.0, label="Amplitude")
        
        with gr.Row():
            grid_size = gr.Slider(50, 200, value=100, step=10, label="Grid Size")
            steps = gr.Slider(1, 100, value=10, label="Simulation Steps")
        
        run_btn = gr.Button("Run Simulation", variant="primary")
        
        plot_output = gr.Plot(label="Wave Field Visualization")
        status_output = gr.Textbox(label="Status", interactive=False)
        
        run_btn.click(
            run_simulation,
            inputs=[frequency, amplitude, grid_size, steps],
            outputs=[plot_output, status_output]
        )
    
    return interface

if __name__ == "__main__":
    print("🌊 Starting Simple Dual Parabolic Wave Simulation Interface")
    interface = create_simple_interface()
    interface.launch(server_name="0.0.0.0", server_port=7860, share=False)
