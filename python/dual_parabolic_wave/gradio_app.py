"""
Gradio web interface for Dual Parabolic Wave Simulation
"""

import gradio as gr
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from typing import Tuple, List, Optional
import time
import threading
import io
import base64

from .simulation import Simulation, SimulationResults
from .visualization import (
    plot_wave_field_2d, 
    plot_wave_field_3d,
    plot_parabola_geometry,
    create_interactive_surface_plot,
    plot_metrics_dashboard
)


class GradioWaveApp:
    """Gradio application for interactive wave simulation."""
    
    def __init__(self):
        self.simulation = None
        self.is_running = False
        self.results_history = []
        self.current_results = None
        
    def create_simulation(self, grid_size: int, frequency: float, amplitude: float) -> Tuple[str, any]:
        """Create a new simulation instance."""
        try:
            self.simulation = Simulation(grid_size=grid_size)
            self.simulation.set_frequency(frequency)
            self.simulation.set_amplitude(amplitude)
            
            info = self.simulation.get_simulation_info()
            info_text = f"""
✅ Simulation Created Successfully!

📊 Configuration:
• Grid Size: {info['grid_size']}×{info['grid_size']} ({info['grid_size']**2:,} points)
• Frequency: {info['frequency']:.1f} Hz
• Amplitude: {info['amplitude']:.2f}
• CFL Time Step: {info['cfl_timestep']:.2e} seconds
• Using C++ Core: {info['use_core']}

Ready to run simulation!
            """
            
            return info_text, None
            
        except Exception as e:
            return f"❌ Error creating simulation: {str(e)}", None
    
    def run_simulation_steps(self, num_steps: int, record_interval: int = 5) -> Tuple[str, any, any]:
        """Run simulation steps and return results."""
        if not self.simulation:
            return "❌ No simulation created. Please create a simulation first.", None, None
        
        try:
            start_time = time.time()
            results = self.simulation.run_steps(num_steps, record_interval)
            end_time = time.time()
            
            self.current_results = results
            self.results_history.append(results)
            
            # Create status message
            status = f"""
🌊 Simulation Completed!

⏱️ Performance:
• Steps: {results.metadata['total_steps']:,}
• Execution Time: {results.metadata['execution_time']:.3f} seconds
• Steps/Second: {results.metadata['steps_per_second']:.1f}
• Final Time: {results.metadata['final_time']:.6f} seconds

📈 Results:
• Final Max Amplitude: {results.max_amplitudes[-1]:.4f}
• Final Energy: {results.energy_levels[-1]:.4f}
• Data Points Recorded: {len(results.wave_data)}
            """
            
            # Create 3D plot
            if results.wave_data:
                fig_3d = plot_wave_field_3d(
                    results.get_final_wave_data(),
                    title=f"Wave Field at t={results.time_steps[-1]:.6f}s"
                )
                
                # Create 2D plot
                fig_2d = plot_wave_field_2d(
                    results.get_final_wave_data(),
                    title=f"Wave Field 2D View (t={results.time_steps[-1]:.6f}s)"
                )
                
                return status, fig_3d, fig_2d
            else:
                return status, None, None
                
        except Exception as e:
            return f"❌ Error running simulation: {str(e)}", None, None
    
    def update_parameters(self, frequency: float, amplitude: float) -> str:
        """Update simulation parameters."""
        if not self.simulation:
            return "❌ No simulation created."
        
        try:
            self.simulation.set_frequency(frequency)
            self.simulation.set_amplitude(amplitude)
            return f"✅ Parameters updated: Frequency={frequency}Hz, Amplitude={amplitude}"
        except Exception as e:
            return f"❌ Error updating parameters: {str(e)}"
    
    def reset_simulation(self) -> str:
        """Reset the simulation."""
        if not self.simulation:
            return "❌ No simulation to reset."
        
        try:
            self.simulation.reset()
            return "✅ Simulation reset to initial state."
        except Exception as e:
            return f"❌ Error resetting simulation: {str(e)}"
    
    def get_simulation_info(self) -> str:
        """Get current simulation information."""
        if not self.simulation:
            return "❌ No simulation created."
        
        info = self.simulation.get_simulation_info()
        return f"""
📊 Current Simulation Status:

🔧 Configuration:
• Grid Size: {info['grid_size']}×{info['grid_size']}
• Current Time: {info['current_time']:.6f} seconds
• Steps Executed: {info['step_count']:,}
• CFL Time Step: {info['cfl_timestep']:.2e} seconds

🌊 Wave Parameters:
• Frequency: {info['frequency']:.1f} Hz
• Amplitude: {info['amplitude']:.3f}

⚡ Performance:
• Using C++ Core: {info['use_core']}
• Core Available: {info['core_available']}
        """
    
    def create_geometry_plot(self) -> any:
        """Create parabola geometry visualization."""
        try:
            return plot_parabola_geometry()
        except Exception as e:
            print(f"Error creating geometry plot: {e}")
            return None
    
    def create_metrics_dashboard(self) -> any:
        """Create metrics dashboard from current results."""
        if not self.current_results:
            return None
        
        try:
            fig = plot_metrics_dashboard(self.current_results)
            return fig
        except Exception as e:
            print(f"Error creating metrics dashboard: {e}")
            return None
    
    def export_results(self) -> Tuple[str, str]:
        """Export simulation results to JSON."""
        if not self.current_results:
            return "❌ No results to export.", ""
        
        try:
            import json
            
            # Prepare data for export (convert numpy arrays to lists)
            export_data = {
                'metadata': self.current_results.metadata,
                'time_steps': self.current_results.time_steps,
                'max_amplitudes': self.current_results.max_amplitudes,
                'energy_levels': self.current_results.energy_levels,
                'final_wave_data': self.current_results.get_final_wave_data().tolist(),
                'export_timestamp': time.time(),
            }
            
            json_str = json.dumps(export_data, indent=2)
            filename = f"wave_simulation_results_{int(time.time())}.json"
            
            return f"✅ Results exported to {filename}", json_str
            
        except Exception as e:
            return f"❌ Error exporting results: {str(e)}", ""


def create_app() -> gr.Blocks:
    """Create the Gradio application interface."""
    
    app = GradioWaveApp()
    
    with gr.Blocks(
        title="🌊 Dual Parabolic Wave Simulation",
        theme=gr.themes.Soft(),
        css="""
        .container { max-width: 1200px; margin: auto; }
        .header { text-align: center; padding: 20px; }
        .status-box { background-color: #f0f0f0; padding: 15px; border-radius: 5px; }
        """
    ) as demo:
        
        # Header
        gr.Markdown("""
        # 🌊 Dual Parabolic Wave Simulation
        
        **Interactive Web Interface for High-Performance Wave Propagation Simulation**
        
        This application provides a real-time interface to the dual parabolic wave simulation,
        featuring advanced 3D visualization, parameter control, and performance analysis.
        """, elem_classes=["header"])
        
        with gr.Tabs():
            
            # Main Simulation Tab
            with gr.Tab("🎮 Simulation Control"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("## 🔧 Configuration")
                        
                        grid_size = gr.Slider(
                            minimum=100, maximum=500, value=300, step=50,
                            label="Grid Size", info="Simulation resolution (higher = more accurate, slower)"
                        )
                        
                        frequency = gr.Slider(
                            minimum=100, maximum=5000, value=1000, step=100,
                            label="Frequency (Hz)", info="Wave frequency"
                        )
                        
                        amplitude = gr.Slider(
                            minimum=0.1, maximum=10.0, value=1.0, step=0.1,
                            label="Amplitude", info="Wave amplitude"
                        )
                        
                        with gr.Row():
                            create_btn = gr.Button("🔨 Create Simulation", variant="primary")
                            reset_btn = gr.Button("🔄 Reset", variant="secondary")
                        
                        gr.Markdown("## 🏃 Execution")
                        
                        num_steps = gr.Slider(
                            minimum=10, maximum=1000, value=100, step=10,
                            label="Number of Steps", info="How many simulation steps to run"
                        )
                        
                        record_interval = gr.Slider(
                            minimum=1, maximum=20, value=5, step=1,
                            label="Record Interval", info="Record data every N steps"
                        )
                        
                        run_btn = gr.Button("▶️ Run Simulation", variant="primary", size="lg")
                        
                        status_text = gr.Textbox(
                            label="Status", 
                            value="Ready to create simulation...",
                            lines=10,
                            elem_classes=["status-box"]
                        )
                    
                    with gr.Column(scale=2):
                        gr.Markdown("## 📊 Real-time Visualization")
                        
                        with gr.Tabs():
                            with gr.Tab("🌊 3D Surface"):
                                plot_3d = gr.Plot(label="3D Wave Field")
                            
                            with gr.Tab("🗺️ 2D View"):
                                plot_2d = gr.Plot(label="2D Wave Field")
            
            # Geometry Visualization Tab
            with gr.Tab("🏗️ Cavity Geometry"):
                gr.Markdown("""
                ## Dual Parabolic Cavity System
                
                This visualization shows the geometric configuration of the dual parabolic reflectors:
                - **Major Parabola**: 20-inch (508mm) diameter umbrella, concave down
                - **Minor Parabola**: 100mm diameter bowl, concave up  
                - **Coincident Focus**: Both parabolas focus at the origin for optimal acoustic coupling
                """)
                
                geometry_plot = gr.Plot(label="Parabolic Cavity Geometry")
                geometry_btn = gr.Button("🔄 Update Geometry View")
            
            # Analysis Tab
            with gr.Tab("📈 Analysis & Metrics"):
                gr.Markdown("## 📊 Simulation Analysis Dashboard")
                
                with gr.Row():
                    info_btn = gr.Button("ℹ️ Get Simulation Info")
                    metrics_btn = gr.Button("📈 Generate Metrics Dashboard")
                    export_btn = gr.Button("💾 Export Results")
                
                with gr.Row():
                    info_display = gr.Textbox(label="Simulation Information", lines=15)
                    export_status = gr.Textbox(label="Export Status", lines=3)
                
                metrics_plot = gr.Plot(label="Metrics Dashboard")
                
                # Export file download
                export_file = gr.File(label="Download Results", visible=False)
            
            # Help Tab
            with gr.Tab("❓ Help & Documentation"):
                gr.Markdown("""
                ## 🎯 Quick Start Guide
                
                1. **Configure**: Set grid size, frequency, and amplitude
                2. **Create**: Click "Create Simulation" to initialize
                3. **Run**: Set number of steps and click "Run Simulation"  
                4. **Visualize**: View results in 3D surface or 2D plots
                5. **Analyze**: Check metrics and export data
                
                ## 🔧 Parameters
                
                - **Grid Size**: Higher values = better accuracy but slower computation
                - **Frequency**: Wave frequency in Hz (100-5000 Hz range)
                - **Amplitude**: Wave amplitude (0.1-10.0 range)
                - **Steps**: More steps = longer simulation time
                - **Record Interval**: How often to save data (every N steps)
                
                ## 🚀 Performance Tips
                
                - Start with smaller grid sizes (200-300) for faster testing
                - Use larger grids (400-500) for high-quality results
                - Adjust record interval to balance data detail vs memory usage
                - C++ core provides 10-100x speedup over Python-only mode
                
                ## 📊 Visualization
                
                - **3D Surface**: Interactive Plotly surface with zoom, rotate, pan
                - **2D View**: Traditional top-down heatmap view
                - **Geometry**: Shows the parabolic cavity structure
                - **Metrics**: Performance analysis and wave characteristics
                
                ## 🔬 Scientific Background
                
                This simulation models acoustic wave propagation in a dual parabolic cavity system
                using the 2D wave equation with finite difference methods and CFL-stable time stepping.
                
                The system consists of two parabolic reflectors with coincident focus points,
                creating optimal conditions for acoustic focusing and wave interference studies.
                """)
        
        # Event handlers
        create_btn.click(
            fn=app.create_simulation,
            inputs=[grid_size, frequency, amplitude],
            outputs=[status_text]
        )
        
        run_btn.click(
            fn=app.run_simulation_steps,
            inputs=[num_steps, record_interval],
            outputs=[status_text, plot_3d, plot_2d]
        )
        
        # Parameter updates
        frequency.change(
            fn=app.update_parameters,
            inputs=[frequency, amplitude],
            outputs=[status_text]
        )
        
        amplitude.change(
            fn=app.update_parameters,
            inputs=[frequency, amplitude], 
            outputs=[status_text]
        )
        
        reset_btn.click(
            fn=app.reset_simulation,
            outputs=[status_text]
        )
        
        # Geometry plot
        geometry_btn.click(
            fn=app.create_geometry_plot,
            outputs=[geometry_plot]
        )
        
        # Analysis functions
        info_btn.click(
            fn=app.get_simulation_info,
            outputs=[info_display]
        )
        
        metrics_btn.click(
            fn=app.create_metrics_dashboard,
            outputs=[metrics_plot]
        )
        
        export_btn.click(
            fn=app.export_results,
            outputs=[export_status, export_file]
        )
        
        # Initialize geometry plot on load
        demo.load(
            fn=app.create_geometry_plot,
            outputs=[geometry_plot]
        )
    
    return demo


def launch_app(share: bool = False, debug: bool = False, port: int = 7860):
    """Launch the Gradio application."""
    demo = create_app()
    
    print("🌊 Starting Dual Parabolic Wave Simulation Web Interface...")
    print(f"   Port: {port}")
    print(f"   Share: {share}")
    print(f"   Debug: {debug}")
    
    demo.launch(
        share=share,
        debug=debug,
        server_port=port,
        show_error=True,
        favicon_path=None
    )


if __name__ == "__main__":
    launch_app()
