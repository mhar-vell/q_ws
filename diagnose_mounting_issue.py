#!/usr/bin/env python3
"""
Diagnostic script to identify and fix robotic system mounting issues.
This script analyzes constraint forces, joint stability, and physics parameters.
"""

import pybullet as p
import time
import numpy as np

def diagnose_physics_stability():
    """
    Comprehensive diagnostic for physics stability issues that could cause unmounting.
    """
    print("\n🔬 ROBOTIC SYSTEM MOUNTING DIAGNOSTICS")
    print("=" * 60)
    
    # Connect to existing physics engine or start new one
    try:
        p.getConnectionInfo()
        print("✅ Connected to existing PyBullet session")
    except:
        p.connect(p.GUI)
        print("⚠️  Started new PyBullet session for diagnostics")
    
    # Get all bodies in simulation
    bodies = []
    for i in range(p.getNumBodies()):
        body_id = p.getBodyUniqueId(i)
        body_info = p.getBodyInfo(body_id)
        bodies.append((body_id, body_info[0].decode('utf-8')))
    
    print(f"\n📋 Found {len(bodies)} bodies in simulation:")
    husky_id = None
    kuka_id = None
    
    for body_id, name in bodies:
        print(f"   • Body {body_id}: {name}")
        if 'husky' in name.lower():
            husky_id = body_id
        elif 'kuka' in name.lower():
            kuka_id = body_id
    
    if husky_id is None or kuka_id is None:
        print("❌ Could not find Husky or KUKA bodies - system may not be running")
        return
    
    print(f"\n🤖 Identified components:")
    print(f"   • Husky Robot: Body {husky_id}")
    print(f"   • KUKA Arm: Body {kuka_id}")
    
    # Check constraint information
    print(f"\n🔗 CONSTRAINT ANALYSIS:")
    num_constraints = p.getNumConstraints()
    print(f"   • Total constraints: {num_constraints}")
    
    mounting_constraint = None
    for i in range(num_constraints):
        constraint_info = p.getConstraintInfo(i)
        parent_body = constraint_info[2]
        child_body = constraint_info[3]
        
        if (parent_body == husky_id and child_body == kuka_id) or \
           (parent_body == kuka_id and child_body == husky_id):
            mounting_constraint = i
            print(f"   • Found mounting constraint {i}: Body {parent_body} ↔ Body {child_body}")
            
            # Get constraint state
            constraint_state = p.getConstraintState(i)
            applied_force = np.linalg.norm(constraint_state[0])
            print(f"   • Applied force: {applied_force:.2f}N")
            
            if applied_force > 1500:
                print(f"   ⚠️  HIGH CONSTRAINT FORCE - May cause instability!")
            elif applied_force > 1000:
                print(f"   ⚠️  ELEVATED constraint force - Monitor closely")
            else:
                print(f"   ✅ Constraint force within normal range")
    
    if mounting_constraint is None:
        print("   ❌ NO MOUNTING CONSTRAINT FOUND - This is the problem!")
        print("   🔧 SOLUTION: Re-establish Husky-KUKA constraint")
        return fix_mounting_constraint(husky_id, kuka_id)
    
    # Check body positions and velocities
    print(f"\n📍 POSITION & VELOCITY ANALYSIS:")
    
    husky_pos, husky_orn = p.getBasePositionAndOrientation(husky_id)
    husky_vel, husky_ang_vel = p.getBaseVelocity(husky_id)
    
    kuka_pos, kuka_orn = p.getBasePositionAndOrientation(kuka_id)
    kuka_vel, kuka_ang_vel = p.getBaseVelocity(kuka_id)
    
    print(f"   Husky position: {husky_pos}")
    print(f"   KUKA position:  {kuka_pos}")
    
    # Check relative position
    rel_pos = np.array(kuka_pos) - np.array(husky_pos)
    rel_dist = np.linalg.norm(rel_pos)
    
    print(f"   Relative distance: {rel_dist:.3f}m")
    print(f"   Expected distance: ~0.5m (mounting height)")
    
    if rel_dist > 0.8:
        print("   ❌ EXCESSIVE SEPARATION - Components are separating!")
        return fix_mounting_constraint(husky_id, kuka_id)
    elif rel_dist < 0.3:
        print("   ❌ COMPONENTS TOO CLOSE - Collision or constraint failure!")
        return fix_mounting_constraint(husky_id, kuka_id)
    
    # Check velocities
    husky_speed = np.linalg.norm(husky_vel)
    kuka_speed = np.linalg.norm(kuka_vel)
    
    print(f"   Husky speed: {husky_speed:.3f}m/s")
    print(f"   KUKA speed:  {kuka_speed:.3f}m/s")
    
    if abs(husky_speed - kuka_speed) > 0.1:
        print("   ⚠️  VELOCITY MISMATCH - Components not moving together!")
        print("   🔧 May indicate constraint weakening")
    
    # Check joint states
    print(f"\n🔩 JOINT ANALYSIS:")
    
    for body_id, name in [(husky_id, "Husky"), (kuka_id, "KUKA")]:
        num_joints = p.getNumJoints(body_id)
        print(f"   {name}: {num_joints} joints")
        
        for j in range(num_joints):
            joint_info = p.getJointInfo(body_id, j)
            joint_state = p.getJointState(body_id, j)
            joint_name = joint_info[1].decode('utf-8')
            
            # Check for problematic joint states
            position = joint_state[0]
            velocity = joint_state[1]
            force = joint_state[3] if len(joint_state) > 3 else 0
            
            if abs(velocity) > 10:  # High joint velocity
                print(f"     ⚠️  Joint {j} ({joint_name}): High velocity {velocity:.2f}")
            if abs(force) > 100:    # High joint force
                print(f"     ⚠️  Joint {j} ({joint_name}): High force {force:.2f}")
    
    print(f"\n✅ DIAGNOSTIC COMPLETE")
    return True

def fix_mounting_constraint(husky_id, kuka_id):
    """
    Re-establish the mounting constraint between Husky and KUKA arm.
    """
    print(f"\n🔧 FIXING MOUNTING CONSTRAINT")
    print("=" * 40)
    
    try:
        # Remove any existing constraints between these bodies
        for i in range(p.getNumConstraints()):
            constraint_info = p.getConstraintInfo(i)
            parent_body = constraint_info[2]
            child_body = constraint_info[3]
            
            if (parent_body == husky_id and child_body == kuka_id) or \
               (parent_body == kuka_id and child_body == husky_id):
                p.removeConstraint(i)
                print(f"   ✅ Removed old constraint {i}")
        
        # Create new stable mounting constraint
        cid = p.createConstraint(
            husky_id, -1,           # Parent: Husky base
            kuka_id, -1,            # Child: KUKA base
            p.JOINT_FIXED,          # Fixed joint type
            [0, 0, 0],              # Parent frame
            [0, 0, 0],              # Child frame  
            [0., 0., 0.5],          # Parent offset: 0.5m UP
            [0, 0, 0, 1]            # Child offset: at KUKA base
        )
        
        # Configure constraint for stability
        p.changeConstraint(cid, maxForce=2000)  # Stable force limit
        
        print(f"   ✅ Created new mounting constraint {cid}")
        print(f"   ✅ Max force: 2000N")
        print(f"   ✅ Fixed joint with compliant mounting")
        
        # Verify constraint
        time.sleep(0.1)  # Let physics settle
        constraint_state = p.getConstraintState(cid)
        applied_force = np.linalg.norm(constraint_state[0])
        print(f"   ✅ Initial applied force: {applied_force:.2f}N")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to fix mounting constraint: {e}")
        return False

def monitor_system_health(duration=10):
    """
    Monitor system health for a specified duration to detect mounting issues.
    """
    print(f"\n📊 MONITORING SYSTEM HEALTH ({duration}s)")
    print("=" * 50)
    
    start_time = time.time()
    samples = []
    
    while time.time() - start_time < duration:
        try:
            # Get constraint forces
            constraint_forces = []
            for i in range(p.getNumConstraints()):
                constraint_state = p.getConstraintState(i)
                force = np.linalg.norm(constraint_state[0])
                constraint_forces.append(force)
            
            max_force = max(constraint_forces) if constraint_forces else 0
            samples.append(max_force)
            
            # Real-time monitoring
            if max_force > 1500:
                print(f"   ⚠️  HIGH FORCE DETECTED: {max_force:.1f}N at t={time.time()-start_time:.1f}s")
            
            time.sleep(0.1)  # 10Hz monitoring
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"   ❌ Monitoring error: {e}")
            break
    
    if samples:
        avg_force = np.mean(samples)
        max_observed = np.max(samples)
        print(f"\n📈 MONITORING RESULTS:")
        print(f"   • Average constraint force: {avg_force:.1f}N")
        print(f"   • Maximum observed force: {max_observed:.1f}N")
        print(f"   • Samples collected: {len(samples)}")
        
        if max_observed > 1800:
            print(f"   ❌ CRITICAL: Forces approaching limit (2000N)")
            return False
        elif max_observed > 1200:
            print(f"   ⚠️  WARNING: Elevated force levels detected")
            return False
        else:
            print(f"   ✅ System operating within normal parameters")
            return True
    
    return False

def main():
    """Main diagnostic routine."""
    print("🚀 ROBOTIC MOUNTING SYSTEM DIAGNOSTICS")
    print("This tool helps identify and fix mounting/unmounting issues")
    print("-" * 60)
    
    # Run diagnostics
    if diagnose_physics_stability():
        print("\n🔍 Running extended monitoring...")
        monitor_system_health(duration=5)
    
    print("\n🏁 DIAGNOSTIC SESSION COMPLETE")
    print("If problems persist, consider:")
    print("   1. Reducing physics timestep")
    print("   2. Increasing solver iterations")
    print("   3. Adjusting constraint parameters")
    print("   4. Restarting the simulation")

if __name__ == "__main__":
    main()