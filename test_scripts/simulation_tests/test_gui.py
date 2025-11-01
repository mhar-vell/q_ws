#!/usr/bin/env python3
"""
Simple PyBullet GUI Test Script
This script tests if the PyBullet GUI is working properly.
"""

import pybullet as p
import pybullet_data
import time
import sys

def test_gui():
    """Test PyBullet GUI functionality"""
    print("🖼️  Testing PyBullet GUI...")
    print("=" * 50)
    
    try:
        # Connect to PyBullet GUI
        print("1. Connecting to PyBullet GUI...")
        physics_client = p.connect(p.GUI)
        
        if physics_client < 0:
            print("❌ Failed to connect to PyBullet GUI")
            return False
        
        print("✅ PyBullet GUI connected successfully")
        
        # Set up search path
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        
        # Load a ground plane
        print("2. Loading ground plane...")
        ground_id = p.loadURDF("plane.urdf")
        print(f"✅ Ground plane loaded (ID: {ground_id})")
        
        # Load a simple object for visibility
        print("3. Loading test objects...")
        cube_id = p.loadURDF("cube_small.urdf", [0, 0, 1])
        print(f"✅ Test cube loaded (ID: {cube_id})")
        
        # Set gravity
        p.setGravity(0, 0, -9.81)
        
        # Configure camera view
        p.resetDebugVisualizerCamera(
            cameraDistance=3.0,
            cameraYaw=45,
            cameraPitch=-30,
            cameraTargetPosition=[0, 0, 0]
        )
        
        print("4. GUI should now be visible with a ground plane and falling cube")
        print("   🖼️  If you see a 3D window with physics simulation, the GUI is working!")
        print("   ⏱️  The simulation will run for 10 seconds...")
        
        # Run simulation for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10.0:
            p.stepSimulation()
            time.sleep(1./240.)  # 240 Hz physics
        
        print("5. Closing GUI...")
        p.disconnect()
        print("✅ GUI test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

if __name__ == "__main__":
    print("PyBullet GUI Test")
    print("If the GUI appears, you should see:")
    print("• A 3D window with controls")
    print("• A gray ground plane")
    print("• A small cube falling due to gravity")
    print("• Camera controls (mouse drag to rotate view)")
    print("")
    
    success = test_gui()
    
    if success:
        print("\n🎉 GUI is working properly!")
        print("You can now run the main simulation:")
        print("   python sim_husky_kuka.py --scenario none --episodes 5")
    else:
        print("\n❌ GUI test failed!")
        print("This might indicate:")
        print("• Display forwarding issues (if using SSH)")
        print("• Missing graphics drivers")
        print("• PyBullet installation problems")
        
    sys.exit(0 if success else 1)