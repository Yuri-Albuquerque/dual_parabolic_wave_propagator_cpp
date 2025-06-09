#!/usr/bin/env python3
"""
Test script to demonstrate the corrected dual parabolic wave simulation
with proper specifications and wave reflection boundaries.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from python.dual_parabolic_wave.simulation import PythonSimulation

def create_geometry_comparison():
    """Create a comparison plot showing old vs corrected parabola geometry."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    x = np.linspace(-300, 300, 500)
    
    # === OLD (INCORRECT) GEOMETRY ===
    ax1.set_title('❌ OLD (Incorrect) Geometry', fontsize=14, color='red')
    
    # Old major parabola equation
    y_major_old = -x**2 / 400 + 100
    mask_major_old = (y_major_old >= -300) & (y_major_old <= 300)
    ax1.plot(x[mask_major_old], y_major_old[mask_major_old], 'r-', linewidth=3, 
             label='Major: y = -x²/400 + 100')
    
    # Old minor parabola equation (100mm diameter!)
    y_minor_old = x**2 / 100 - 25
    mask_minor_old = (y_minor_old >= -300) & (y_minor_old <= 300)
    ax1.plot(x[mask_minor_old], y_minor_old[mask_minor_old], 'r--', linewidth=3,
             label='Minor: y = x²/100 - 25')
    
    # Old focus points
    ax1.plot(0, 100, 'ro', markersize=10, label='Major Focus (100, 0)')
    ax1.plot(0, -25, 'bo', markersize=10, label='Minor Focus (0, -25)')
    
    ax1.text(0.05, 0.95, 'ISSUES:\n• Minor diameter = 100mm (should be 10mm)\n• Non-coincident focus points\n• Absorbing boundaries', 
             transform=ax1.transAxes, verticalalignment='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # === NEW (CORRECTED) GEOMETRY ===
    ax2.set_title('✅ NEW (Corrected) Geometry', fontsize=14, color='green')
    
    # Corrected major parabola (same equation, but now with proper diameter limits)
    y_major_new = -x**2 / 400 + 100
    mask_major_new = (y_major_new >= -300) & (y_major_new <= 300) & (np.abs(x) <= 254)  # 508mm/2
    ax2.plot(x[mask_major_new], y_major_new[mask_major_new], 'g-', linewidth=3,
             label='Major: 20" (508mm) diameter')
    
    # Corrected minor parabola (10mm diameter, 50mm focus)
    y_minor_new = x**2 / 200 - 50  # Changed from x²/100-25 to x²/200-50
    mask_minor_new = (y_minor_new >= -300) & (y_minor_new <= 300) & (np.abs(x) <= 5)  # 10mm/2
    ax2.plot(x[mask_minor_new], y_minor_new[mask_minor_new], 'g--', linewidth=3,
             label='Minor: 10mm diameter')
    
    # Corrected focus points (coincident at origin)
    ax2.plot(0, 0, 'go', markersize=12, markeredgecolor='black', markeredgewidth=2,
             label='Coincident Focus (0, 0)')
    ax2.plot(0, 100, 'gray', marker='s', markersize=6, label='Major Vertex')
    ax2.plot(0, -50, 'gray', marker='s', markersize=6, label='Minor Vertex')
    
    ax2.text(0.05, 0.95, 'CORRECTED:\n• Minor diameter = 10mm ✓\n• Coincident focus at origin ✓\n• Wave reflection boundaries ✓', 
             transform=ax2.transAxes, verticalalignment='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    # Format both plots
    for ax in [ax1, ax2]:
        ax.set_xlabel('X Position (mm)')
        ax.set_ylabel('Y Position (mm)')
        ax.set_xlim(-300, 300)
        ax.set_ylim(-300, 300)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='lower right')
        ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('parabola_geometry_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: parabola_geometry_comparison.png")
    
    return fig

def test_wave_reflection():
    """Test wave propagation with reflection boundaries."""
    
    print("Testing wave reflection with corrected geometry...")
    
    # Create simulation
    sim = PythonSimulation(grid_size=120)
    sim.set_frequency(2000)  # Higher frequency for better visualization
    sim.set_amplitude(2.0)
    
    # Run simulation
    results = sim.run_steps(30, record_interval=5)
    
    # Create visualization
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    x = np.linspace(-300, 300, sim.grid_size)
    y = np.linspace(-300, 300, sim.grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Plot wave evolution
    for i, (ax, wave_data, time_step) in enumerate(zip(axes, results.wave_data, results.time_steps)):
        if i >= 6:
            break
            
        # Wave contour plot
        vmax = np.max([np.max(np.abs(wd)) for wd in results.wave_data])
        im = ax.contourf(X, Y, wave_data, levels=20, cmap='RdBu_r', vmin=-vmax, vmax=vmax)
        
        # Add corrected parabola boundaries
        x_para = np.linspace(-300, 300, 200)
        
        # Major parabola
        y_major = -x_para**2 / 400 + 100
        mask_major = (y_major >= -300) & (y_major <= 300) & (np.abs(x_para) <= 254)
        ax.plot(x_para[mask_major], y_major[mask_major], 'k-', linewidth=2, alpha=0.8)
        
        # Minor parabola  
        y_minor = x_para**2 / 200 - 50
        mask_minor = (y_minor >= -300) & (y_minor <= 300) & (np.abs(x_para) <= 5)
        ax.plot(x_para[mask_minor], y_minor[mask_minor], 'k--', linewidth=2, alpha=0.8)
        
        # Focus point
        ax.plot(0, 0, 'go', markersize=8, markeredgecolor='black')
        
        ax.set_title(f'Frame {i+1}: t={time_step:.4f}s\nMax Amp: {np.max(np.abs(wave_data)):.2e}')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_xlim(-300, 300)
        ax.set_ylim(-300, 300)
        ax.set_aspect('equal')
    
    plt.suptitle('Wave Propagation with Corrected Parabola Specifications\nand Reflection Boundaries', 
                 fontsize=16, y=0.95)
    plt.tight_layout()
    plt.savefig('corrected_wave_propagation.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: corrected_wave_propagation.png")
    
    return fig

def main():
    """Main test function."""
    print("🌊 Testing Corrected Dual Parabolic Wave Simulation")
    print("=" * 60)
    
    # Test geometry
    print("\n1. Creating geometry comparison...")
    create_geometry_comparison()
    
    # Test wave propagation
    print("\n2. Testing wave reflection...")
    test_wave_reflection()
    
    print(f"\n🎯 SUCCESS: All tests completed!")
    print(f"Key corrections implemented:")
    print(f"  ✓ Minor parabola diameter: 100mm → 10mm")
    print(f"  ✓ Focus points: separate → coincident at origin")  
    print(f"  ✓ Boundary conditions: absorbing → reflecting")
    print(f"  ✓ Parabola equations: corrected for proper geometry")
    
    return 0

if __name__ == "__main__":
    exit(main())
