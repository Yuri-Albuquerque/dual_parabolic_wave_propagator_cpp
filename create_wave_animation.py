#!/usr/bin/env python3
"""
Wave Animation Creator
Creates animated GIF from the wave propagation frame sequence.
"""

import sys
import os
from pathlib import Path
import subprocess

def create_wave_animation():
    """Create an animated GIF from wave frames."""
    print("🎬 Creating Wave Animation GIF...")
    
    # Check if frames exist
    frames_dir = Path('wave_sequence_plots')
    if not frames_dir.exists():
        print("❌ No wave frames found. Run complete_wave_plotter.py first!")
        return False
        
    frame_files = sorted(frames_dir.glob('wave_frame_*.png'))
    if not frame_files:
        print("❌ No wave frame files found!")
        return False
        
    print(f"✅ Found {len(frame_files)} wave frames")
    
    # Create GIF using ImageMagick (if available)
    output_gif = frames_dir / 'wave_propagation_animation.gif'
    
    try:
        # Try using ImageMagick convert
        cmd = [
            'convert',
            '-delay', '20',  # 20/100 seconds = 0.2 seconds per frame
            '-loop', '0',    # Loop indefinitely
            str(frames_dir / 'wave_frame_*.png'),
            str(output_gif)
        ]
        
        print("🔄 Creating GIF with ImageMagick...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ GIF created successfully: {output_gif}")
            print(f"📏 File size: {output_gif.stat().st_size / (1024*1024):.1f} MB")
            return True
        else:
            print(f"❌ ImageMagick failed: {result.stderr}")
            
    except FileNotFoundError:
        print("⚠️  ImageMagick not found, trying alternative method...")
        
    # Try using Python PIL
    try:
        from PIL import Image
        print("🔄 Creating GIF with Python PIL...")
        
        # Load all frames
        images = []
        for frame_file in frame_files:
            img = Image.open(frame_file)
            images.append(img)
            
        # Save as GIF
        images[0].save(
            output_gif,
            save_all=True,
            append_images=images[1:],
            duration=200,  # 200ms per frame
            loop=0
        )
        
        print(f"✅ GIF created successfully: {output_gif}")
        print(f"📏 File size: {output_gif.stat().st_size / (1024*1024):.1f} MB")
        return True
        
    except ImportError:
        print("❌ PIL not available. Install with: pip install Pillow")
        return False
        
    except Exception as e:
        print(f"❌ Error creating GIF: {e}")
        return False

def create_video_animation():
    """Create MP4 video from wave frames using ffmpeg."""
    print("🎥 Creating Wave Animation Video...")
    
    frames_dir = Path('wave_sequence_plots')
    if not frames_dir.exists():
        print("❌ No wave frames found!")
        return False
        
    output_video = frames_dir / 'wave_propagation_animation.mp4'
    
    try:
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-framerate', '5',  # 5 fps
            '-pattern_type', 'glob',
            '-i', str(frames_dir / 'wave_frame_*.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            str(output_video)
        ]
        
        print("🔄 Creating video with ffmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Video created successfully: {output_video}")
            print(f"📏 File size: {output_video.stat().st_size / (1024*1024):.1f} MB")
            return True
        else:
            print(f"❌ ffmpeg failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  ffmpeg not found, skipping video creation")
        return False

def main():
    """Main function."""
    print("=" * 50)
    print("🎬 WAVE ANIMATION CREATOR 🎬")
    print("=" * 50)
    
    success_gif = create_wave_animation()
    success_video = create_video_animation()
    
    print("\n" + "=" * 50)
    if success_gif or success_video:
        print("✅ Animation creation completed!")
        if success_gif:
            print("   📁 GIF: wave_sequence_plots/wave_propagation_animation.gif")
        if success_video:
            print("   📁 Video: wave_sequence_plots/wave_propagation_animation.mp4")
    else:
        print("❌ No animations were created")
        print("💡 Try installing ImageMagick, PIL, or ffmpeg")
        
    print("=" * 50)
    
    return 0 if (success_gif or success_video) else 1

if __name__ == "__main__":
    exit(main())
