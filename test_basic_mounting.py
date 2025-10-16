#!/usr/bin/env python3
"""
Simple test to verify KUKA is mounted on top of Husky
"""

import pybullet as p
import pybullet_data
import time
import numpy as np

print("🔍 TESTING BASIC KUKA-HUSKY MOUNTING")
print("=" * 40)

# Connect to PyBullet GUI so you can see the result
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
p.setTimeStep(1./240.)

# Load ground
planeId = p.loadURDF("plane.urdf")
print("✅ Ground plane loaded")

# Load Husky at ground level
husky_pos = [0, 0, 0]
husky = p.loadURDF("husky/husky.urdf", husky_pos, [0, 0, 0, 1])
print(f"✅ Husky loaded at {husky_pos}")

# Load KUKA on top of Husky
kuka_pos = [0, 0, 0.5]  # 0.5m above Husky
kukaId = p.loadURDF("kuka_iiwa/model.urdf", kuka_pos, [0, 0, 0, 1])
print(f"✅ KUKA loaded at {kuka_pos}")

# Check initial positions
husky_pos_actual, _ = p.getBasePositionAndOrientation(husky)
kuka_pos_actual, _ = p.getBasePositionAndOrientation(kukaId)
height_diff = kuka_pos_actual[2] - husky_pos_actual[2]

print(f"\n🔍 INITIAL POSITIONS:")
print(f"   Husky: {husky_pos_actual}")
print(f"   KUKA: {kuka_pos_actual}")
print(f"   Height difference: {height_diff:.3f}m")

# Create simple mounting constraint
print(f"\n🔧 Creating mounting constraint...")
cid = p.createConstraint(husky, -1, kukaId, -1, p.JOINT_FIXED, 
                         [0, 0, 0],      # Parent frame (Husky center)
                         [0, 0, 0],      # Child frame (KUKA base)  
                         [0., 0., 0.5],  # Parent offset: 0.5m UP from Husky center
                         [0, 0, 0, 1])   # Child offset: at KUKA base

# Make constraint strong
p.changeConstraint(cid, maxForce=10000)
print(f"✅ Constraint created with ID {cid}, max force 10,000N")

# Let physics settle
print(f"\n⏱️  Letting physics settle for 2 seconds...")
for i in range(480):  # 2 seconds at 240 FPS
    p.stepSimulation()
    time.sleep(1./240.)

# Check final positions
husky_final, _ = p.getBasePositionAndOrientation(husky)
kuka_final, _ = p.getBasePositionAndOrientation(kukaId)
final_height_diff = kuka_final[2] - husky_final[2]

print(f"\n🔍 FINAL POSITIONS:")
print(f"   Husky: {husky_final}")
print(f"   KUKA: {kuka_final}")
print(f"   Height difference: {final_height_diff:.3f}m")

# Check constraint
try:
    constraint_state = p.getConstraintState(cid)
    if constraint_state:
        force = np.linalg.norm(constraint_state[0])
        print(f"   Constraint force: {force:.1f}N")
    else:
        print("   ❌ Could not read constraint state")
except Exception as e:
    print(f"   ❌ Constraint error: {e}")

# Verdict
if 0.4 < final_height_diff < 0.6:
    print(f"\n✅ SUCCESS: KUKA is properly mounted on top of Husky!")
    print(f"   Height difference {final_height_diff:.3f}m is correct (~0.5m)")
else:
    print(f"\n❌ FAILURE: KUKA is not properly mounted!")
    print(f"   Height difference {final_height_diff:.3f}m is wrong (should be ~0.5m)")

print(f"\n💡 You can now see the result in the PyBullet GUI window.")
print(f"   The KUKA arm should be sitting on top of the Husky robot.")
print(f"\nPress Enter to exit...")
input()

p.disconnect()