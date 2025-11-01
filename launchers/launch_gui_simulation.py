#!/usr/bin/env python3
"""
Launch simulation with GUI visibility checks
"""

import subprocess
import sys
import os

def launch_simulation():
    """Launch the simulation with proper GUI settings"""
    
    print("🖼️  LAUNCHING SIMULATION WITH GUI")
    print("=" * 50)
    
    # Set display environment
    env = os.environ.copy()
    env['DISPLAY'] = ':1'
    env['LIBGL_ALWAYS_INDIRECT'] = '1'  # For some OpenGL compatibility
    
    # Launch command
    cmd = [
        'python', 'sim_husky_kuka.py',
        '--scenario', 'none',
        '--episodes', '5',
        '--intensity', 'normal'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print(f"Display: {env.get('DISPLAY', 'Not set')}")
    print("=" * 50)
    
    print("🔍 WHAT TO EXPECT:")
    print("• A PyBullet 3D window should appear")
    print("• You'll see a Husky robot with KUKA arm")
    print("• The robot will move in circular patterns")
    print("• Camera can be controlled with mouse:")
    print("  - Left drag: Rotate view")
    print("  - Right drag: Pan view") 
    print("  - Scroll: Zoom in/out")
    print("• Console will show IMU data and diagnostics")
    print("=" * 50)
    
    print("🚀 Starting simulation...")
    
    try:
        process = subprocess.run(cmd, env=env, cwd='/home/marcoreis/q_ws')
        return process.returncode
    except KeyboardInterrupt:
        print("\n⏹️  Simulation stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error launching simulation: {e}")
        return 1

if __name__ == "__main__":
    exit_code = launch_simulation()
    
    if exit_code == 0:
        print("\n✅ Simulation completed successfully!")
    else:
        print(f"\n❌ Simulation exited with error code: {exit_code}")
        
    sys.exit(exit_code)