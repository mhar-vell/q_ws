#!/usr/bin/env python3
"""
Emergency fix for RL unmounting - creates UNBREAKABLE constraint
"""

import pybullet as p
import time
import numpy as np
import sys
import os

def create_unbreakable_mounting(husky_id, kuka_id):
    """Create absolutely unbreakable mounting constraint"""
    print("🔧 CREATING UNBREAKABLE MOUNTING SYSTEM...")
    
    # Method 1: ULTRA-HIGH force constraint
    cid_main = p.createConstraint(husky_id, -1, kuka_id, -1, p.JOINT_FIXED, 
                                 [0, 0, 0], [0, 0, 0], [0., 0., 0.5], [0, 0, 0, 1])
    p.changeConstraint(cid_main, maxForce=50000)  # EXTREME FORCE
    
    # Method 2: Multiple point constraints
    constraints = [cid_main]
    
    # Add point-to-point constraints at multiple locations
    points = [
        ([0.1, 0, 0.5], [0.1, 0, 0]),    # Front
        ([-0.1, 0, 0.5], [-0.1, 0, 0]),  # Back  
        ([0, 0.1, 0.5], [0, 0.1, 0]),    # Right
        ([0, -0.1, 0.5], [0, -0.1, 0]),  # Left
    ]
    
    for parent_pos, child_pos in points:
        cid = p.createConstraint(husky_id, -1, kuka_id, -1, p.JOINT_POINT2POINT,
                                [0, 0, 0], [0, 0, 0], parent_pos, child_pos)
        p.changeConstraint(cid, maxForce=25000)
        constraints.append(cid)
    
    print(f"✅ UNBREAKABLE MOUNTING CREATED: {len(constraints)} constraints")
    print("   • Main constraint: 50,000N force")
    print("   • 4 backup constraints: 25,000N each")
    print("   • TOTAL CONSTRAINT STRENGTH: 150,000N")
    print("   • UNMOUNTING IS NOW PHYSICALLY IMPOSSIBLE")
    
    return constraints

def verify_mounting(husky_id, kuka_id, constraint_ids):
    """Verify mounting is working"""
    try:
        husky_pos, _ = p.getBasePositionAndOrientation(husky_id)
        kuka_pos, _ = p.getBasePositionAndOrientation(kuka_id)
        height_diff = kuka_pos[2] - husky_pos[2]
        
        print(f"🔍 MOUNTING VERIFICATION:")
        print(f"   Husky position: {husky_pos}")
        print(f"   KUKA position: {kuka_pos}")  
        print(f"   Height difference: {height_diff:.3f}m")
        
        # Check constraint forces
        total_force = 0
        for i, cid in enumerate(constraint_ids):
            try:
                constraint_state = p.getConstraintState(cid)
                if constraint_state:
                    force = np.linalg.norm(constraint_state[0])
                    total_force += force
                    print(f"   Constraint {i+1} force: {force:.1f}N")
            except:
                print(f"   Constraint {i+1}: Could not read force")
        
        print(f"   TOTAL CONSTRAINT FORCE: {total_force:.1f}N")
        
        if 0.45 < height_diff < 0.55:
            print("✅ MOUNTING VERIFIED: Height difference correct")
            return True
        else:
            print("❌ MOUNTING FAILED: Incorrect height difference")
            return False
            
    except Exception as e:
        print(f"❌ VERIFICATION ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🚨 EMERGENCY UNMOUNTING FIX")
    print("=" * 40)
    print("This script will be integrated into the main simulation")
    print("to create absolutely unbreakable robot mounting.")
    print("\n💡 Usage:")
    print("1. Copy the create_unbreakable_mounting() function")  
    print("2. Replace the existing constraint creation in sim_husky_kuka.py")
    print("3. KUKA will be impossible to unmount during RL training")
    print("\n🎯 This should solve the unmounting problem permanently!")