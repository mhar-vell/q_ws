#!/usr/bin/env python3
"""
Minimal test to isolate the 't' key issue
"""

import pybullet as p
import pybullet_data
import time

# Connect to physics server
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
p.setTimeStep(1./240.)

# Load plane
planeId = p.loadURDF("plane.urdf")

# Load Husky
husky = p.loadURDF("husky/husky.urdf", [0, 0, 0.1])

# Load KUKA
kukaId = p.loadURDF("kuka_iiwa/model_free_base.urdf", [0, 0, 0.65])

# Create constraint EXACTLY as in main simulation
print("Creating constraint...")
cid = p.createConstraint(husky, -1, kukaId, -1, p.JOINT_FIXED, 
                        [0,0,0], [0,0,0], [0,0,0.5], [0,0,0,1])
print(f"Constraint created: {cid}")

# Check initial constraint info
constraint_info = p.getConstraintInfo(cid)
print(f"Initial constraint info: {constraint_info}")

rl_training_mode = False
key_states = {}

print("Simulation started. Press 't' to toggle RL mode, 'q' to quit.")

while True:
    p.stepSimulation()
    time.sleep(1./240.)
    
    # Get keyboard input
    keys = p.getKeyboardEvents()
    
    # Handle 't' key EXACTLY as in main simulation
    if ord('t') in keys and keys[ord('t')] == p.KEY_WAS_TRIGGERED:
        rl_training_mode = not rl_training_mode
        print(f"RL Training Mode: {'ON' if rl_training_mode else 'OFF'}")
        
        # Check constraint after toggle
        try:
            constraint_info = p.getConstraintInfo(cid)
            print(f"Constraint after toggle: {constraint_info}")
        except Exception as e:
            print(f"ERROR getting constraint info: {e}")
    
    # Quit on 'q'
    if ord('q') in keys and keys[ord('q')] == p.KEY_WAS_TRIGGERED:
        break

p.disconnect()
print("Test completed.")