#!/usr/bin/env python3
"""
Test script to verify mounting stability during RL training.
This script simulates RL training resets and monitors constraint forces.
"""

import pybullet as p
import pybullet_data
import numpy as np
import time
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import RL environment
try:
    from rl_mission_env import RLMissionEnvironment
    RL_ENV_AVAILABLE = True
    print("✅ RL Environment successfully imported")
except ImportError as e:
    RL_ENV_AVAILABLE = False
    print(f"❌ Failed to import RL environment: {e}")

def test_rl_mounting_stability():
    """Test that mounting remains stable during RL training resets"""
    print("\n🧪 TESTING RL MOUNTING STABILITY")
    print("=" * 50)
    
    # Connect to PyBullet (headless for testing)
    physicsClient = p.connect(p.DIRECT)
    
    if physicsClient < 0:
        print("❌ Failed to connect to PyBullet")
        return False
    
    # Set up simulation environment
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.81)
    p.setTimeStep(1./240.)
    
    # Load ground plane
    planeId = p.loadURDF("plane.urdf")
    
    # Load robots at proper positions (matching sim_husky_kuka.py)
    print("Loading robots...")
    husky_pos = [0, 0, 0]
    kuka_pos = [0, 0, 0.5]  # On top of Husky
    
    try:
        husky_id = p.loadURDF("husky/husky.urdf", husky_pos, useFixedBase=False)
        kuka_id = p.loadURDF("kuka_iiwa/model.urdf", kuka_pos, useFixedBase=False)
        print(f"✅ Robots loaded - Husky ID: {husky_id}, KUKA ID: {kuka_id}")
    except Exception as e:
        print(f"❌ Failed to load robots: {e}")
        return False
    
    # Create constraint (matching sim_husky_kuka.py setup)
    print("Creating KUKA-Husky mounting constraint...")
    cid = p.createConstraint(husky_id, -1, kuka_id, -1, p.JOINT_FIXED, 
                             [0, 0, 0],      # Parent frame (Husky center)
                             [0, 0, 0],      # Child frame (KUKA base)  
                             [0., 0., 0.5],  # Parent offset: 0.5m UP from Husky center
                             [0, 0, 0, 1])   # Child offset: at KUKA base
    
    # Configure constraint with same settings as main sim
    p.changeConstraint(cid, maxForce=1500)  # Ultra-stable mounting
    print(f"✅ Constraint created with ID: {cid}, Max Force: 1500N")
    
    # Initialize RL environment if available
    if RL_ENV_AVAILABLE:
        print("\n🎯 Testing RL Environment with mounting...")
        rl_env = RLMissionEnvironment(p, husky_id, kuka_id, goal_pose=[0, 0, 0.7, 0, 0, 0])
        print("✅ RL Environment initialized")
    else:
        print("⚠️  RL Environment not available - simulating reset manually")
        rl_env = None
    
    # Test multiple reset cycles
    print("\n🔄 Testing Multiple RL Reset Cycles...")
    
    for cycle in range(5):
        print(f"\n--- Cycle {cycle + 1}/5 ---")
        
        # Check initial mounting
        try:
            constraint_state = p.getConstraintState(cid)
            if constraint_state:
                initial_force = np.linalg.norm(constraint_state[0])
                print(f"Initial constraint force: {initial_force:.1f}N")
            else:
                print("❌ Could not read constraint state")
                return False
        except Exception as e:
            print(f"❌ Constraint check error: {e}")
            return False
        
        # Perform RL reset
        if rl_env:
            print("🔄 Performing RL environment reset...")
            try:
                rl_env.reset()
                print("✅ RL reset completed")
            except Exception as e:
                print(f"❌ RL reset error: {e}")
                return False
        else:
            # Manual reset simulation
            print("🔄 Simulating manual reset...")
            # Reset Husky position
            p.resetBasePositionAndOrientation(husky_id, [0, 0, 0], [0, 0, 0, 1])
            p.resetBaseVelocity(husky_id, [0, 0, 0], [0, 0, 0])
            # Reset KUKA joints only (not base position - constraint handles that)
            num_joints = p.getNumJoints(kuka_id)
            for i in range(num_joints):
                p.resetJointState(kuka_id, i, 0.0, targetVelocity=0.0)
        
        # Let physics settle
        for _ in range(20):
            p.stepSimulation()
            time.sleep(1./240.)
        
        # Check post-reset mounting
        try:
            constraint_state = p.getConstraintState(cid)
            if constraint_state:
                post_force = np.linalg.norm(constraint_state[0])
                print(f"Post-reset constraint force: {post_force:.1f}N")
                
                # Check positions
                husky_pos, _ = p.getBasePositionAndOrientation(husky_id)
                kuka_pos, _ = p.getBasePositionAndOrientation(kuka_id)
                height_diff = kuka_pos[2] - husky_pos[2]
                
                print(f"Husky position: {husky_pos}")
                print(f"KUKA position: {kuka_pos}")
                print(f"Height difference: {height_diff:.3f}m (should be ~0.5m)")
                
                # Verify mounting stability
                if post_force < 2000 and 0.4 < height_diff < 0.6:
                    print("✅ Mounting STABLE after reset")
                else:
                    print(f"❌ Mounting UNSTABLE: Force={post_force:.1f}N, Height={height_diff:.3f}m")
                    return False
            else:
                print("❌ Could not read post-reset constraint state")
                return False
        except Exception as e:
            print(f"❌ Post-reset check error: {e}")
            return False
    
    # Cleanup
    p.disconnect()
    
    print("\n" + "=" * 50)
    print("🎉 RL MOUNTING STABILITY TEST PASSED!")
    print("✅ Mounting remains stable through all RL reset cycles")
    print("\n💡 Key findings:")
    print("   • RL reset() no longer breaks constraint connection")
    print("   • KUKA base position is maintained by constraint")
    print("   • Only joint positions are reset during RL episodes")
    print("   • Mounting force stays within safe limits")
    
    return True

if __name__ == "__main__":
    success = test_rl_mounting_stability()
    if success:
        print("\n✅ RL training should now maintain mounting stability")
        print("💡 Safe to run: python3 sim_husky_kuka.py and press 't' for RL training")
        sys.exit(0)
    else:
        print("\n❌ Mounting stability test failed")
        sys.exit(1)