#!/usr/bin/env python3
"""
Test script to verify  manipulator mounting on mobile robot.
This script loads both robots and checks if they are properly positioned.
"""

import pybullet as p
import pybullet_data
import time
import numpy as np

def test_robot_mounting():
    """Test if  manipulator is properly mounted on Husky mobile robot."""
    
    print("🔧 ROBOT MOUNTING TEST")
    print("=" * 50)
    
    # Connect to PyBullet with GUI
    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    
    # Set up physics
    p.setGravity(0, 0, -9.81)
    p.setTimeStep(1./240.)
    
    # Load ground plane
    plane = p.loadURDF("plane.urdf")
    print("✅ Ground plane loaded")
    
    # Load Husky mobile robot at ground level
    husky_start_pos = [0, 0, 0.1]  # Slightly above ground
    husky_start_orientation = p.getQuaternionFromEuler([0, 0, 0])
    
    husky = p.loadURDF("husky/husky.urdf", 
                       husky_start_pos, 
                       husky_start_orientation)
    
    print(f"✅ Husky loaded at position: {husky_start_pos}")
    
    # Load  manipulator mounted on top of Husky
    _start_pos = [0, 0, 0.6]  # 0.6m above ground = on top of Husky
    _start_orientation = p.getQuaternionFromEuler([0, 0, 0])
    
     = p.loadURDF("_iiwa/model.urdf",
                      _start_pos,
                      _start_orientation)
    
    print(f"✅  loaded at position: {_start_pos}")
    
    # Let physics settle
    for _ in range(100):
        p.stepSimulation()
    
    # Check actual positions after physics settling
    husky_pos, husky_orn = p.getBasePositionAndOrientation(husky)
    _pos, _orn = p.getBasePositionAndOrientation()
    
    print(f"\n📍 ACTUAL POSITIONS AFTER PHYSICS:")
    print(f"   Husky: {[round(x, 3) for x in husky_pos]}")
    print(f"   :  {[round(x, 3) for x in _pos]}")
    
    # Calculate relative position
    rel_height = _pos[2] - husky_pos[2]
    horizontal_dist = np.sqrt((_pos[0] - husky_pos[0])**2 + 
                             (_pos[1] - husky_pos[1])**2)
    
    print(f"\n📏 RELATIVE POSITIONING:")
    print(f"   Height difference: {rel_height:.3f}m")
    print(f"   Horizontal distance: {horizontal_dist:.3f}m")
    
    # Create constraint to mount  on Husky
    constraint_id = p.createConstraint(
        husky, -1,           # Parent: Husky base
        , -1,            # Child:  base
        p.JOINT_FIXED,       # Fixed joint type
        [0, 0, 0],           # Parent frame
        [0, 0, 0],           # Child frame  
        [0., 0., 0.5],       # Parent offset: 0.5m UP from Husky center
        [0, 0, 0, 1]         # Child offset: at  base
    )
    
    # Configure constraint for stability
    p.changeConstraint(constraint_id, maxForce=1500)  # Stable force limit
    
    print(f"✅ Mounting constraint created (ID: {constraint_id})")
    print(f"   Max force: 1500N")
    
    # Let physics settle with constraint
    for _ in range(200):
        p.stepSimulation()
    
    # Check final positions
    husky_final, _ = p.getBasePositionAndOrientation(husky)
    _final, _ = p.getBasePositionAndOrientation()
    
    print(f"\n📍 FINAL POSITIONS WITH CONSTRAINT:")
    print(f"   Husky: {[round(x, 3) for x in husky_final]}")
    print(f"   :  {[round(x, 3) for x in _final]}")
    
    # Calculate final relative position
    final_rel_height = _final[2] - husky_final[2]
    final_horizontal_dist = np.sqrt((_final[0] - husky_final[0])**2 + 
                                   (_final[1] - husky_final[1])**2)
    
    print(f"\n📏 FINAL RELATIVE POSITIONING:")
    print(f"   Height difference: {final_rel_height:.3f}m")
    print(f"   Horizontal distance: {final_horizontal_dist:.3f}m")
    
    # Check constraint force
    try:
        constraint_state = p.getConstraintState(constraint_id)
        constraint_force = np.linalg.norm(constraint_state[0])
        print(f"\n🔧 CONSTRAINT STATUS:")
        print(f"   Applied force: {constraint_force:.1f}N (limit: 1500N)")
        
        if constraint_force > 1200:
            print("   ⚠️  HIGH constraint force - may indicate problems")
        else:
            print("   ✅ Constraint force within normal range")
    except:
        print("   ⚠️  Could not read constraint force")
    
    # Assessment
    print(f"\n🎯 MOUNTING ASSESSMENT:")
    
    if 0.4 < final_rel_height < 0.6:
        print("   ✅ HEIGHT:  properly mounted on top of Husky")
        height_ok = True
    else:
        print(f"   ❌ HEIGHT:  not at correct height (expected ~0.5m, got {final_rel_height:.3f}m)")
        height_ok = False
    
    if final_horizontal_dist < 0.1:
        print("   ✅ ALIGNMENT:  centered over Husky")
        alignment_ok = True
    else:
        print(f"   ❌ ALIGNMENT:  not centered (distance: {final_horizontal_dist:.3f}m)")
        alignment_ok = False
    
    # Overall assessment
    if height_ok and alignment_ok:
        print("\n🎉 MOUNTING TEST: PASSED")
        print("   The  manipulator is properly mounted on the Husky!")
        success = True
    else:
        print("\n❌ MOUNTING TEST: FAILED")
        print("   The  manipulator is NOT properly mounted.")
        success = False
    
    print(f"\n🔍 VISUAL INSPECTION:")
    print("   Look at the PyBullet GUI window to visually verify mounting")
    print("   -  should be sitting on top of Husky")
    print("   - They should move together as one unit")
    print("   - No gap or overlap between the robots")
    
    print("\n🔍 KEEPING SIMULATION OPEN FOR VISUAL INSPECTION")
    print("Press ENTER to close the simulation...")
    
    # Keep simulation open for inspection
    input("Press ENTER to close...")
    
    # Disconnect
    p.disconnect()
    
    return success

if __name__ == "__main__":
    success = test_robot_mounting()
    if success:
        print("\n✅ Test completed successfully!")
        print("The main simulation should now work with proper mounting.")
    else:
        print("\n❌ Test failed!")
        print("Check the robot loading positions in sim_husky_kuka.py")
        return True
    else:
        print("❌ MOUNTING TEST FAILED -  not properly positioned")
        return False

def main():
    """Main test function."""
    success = test_mounting()
    
    if success:
        print("\n🎉 MOUNTING CONFIGURATION VERIFIED")
        print("The  manipulator is properly mounted on the Husky mobile robot.")
    else:
        print("\n🚨 MOUNTING ISSUES DETECTED")
        print("Please check URDF files and constraint configuration.")
    
    # Keep window open
    input("\nPress Enter to exit...")
    p.disconnect()

if __name__ == "__main__":
    main()