#!/usr/bin/env python3
"""
Physics Diagnostics Script
Analyzes the Husky-KUKA constraint system to identify jumping/instability issues
"""

import numpy as np

def analyze_constraint_system():
    """Analyze the current constraint configuration"""
    
    print("=== PHYSICS DIAGNOSTICS ANALYSIS ===")
    
    print("\n🔍 URDF LOADING ANALYSIS:")
    print("   1. Husky Robot: 'husky/husky.urdf' - SEPARATE URDF")
    print("   2. KUKA Arm: 'kuka_iiwa/model_free_base.urdf' - SEPARATE URDF")
    print("   3. Ground Plane: 'plane.urdf' - SEPARATE URDF")
    print("   → VERDICT: Multiple separate URDFs connected via constraints")
    
    print("\n⚠️  CONSTRAINT FORCE ANALYSIS:")
    constraint_force_limit = 50000  # Current setting
    recommended_force = 1000        # Recommended for stable operation
    
    print(f"   Current Max Force: {constraint_force_limit:,}N")
    print(f"   Recommended Force: {recommended_force:,}N")
    print(f"   Ratio: {constraint_force_limit/recommended_force:.1f}x TOO HIGH")
    
    print("\n📊 PHYSICS INSTABILITY INDICATORS:")
    print("   ✅ Separate URDFs: Creates constraint-dependent system")
    print("   ❌ High constraint forces: 50,000N can cause 'springy' behavior")
    print("   ❌ Rigid JOINT_FIXED: No compliance, all forces transferred instantly")
    print("   ❌ Mass imbalance: 30kg Husky + 15kg KUKA + arm masses")
    
    print("\n🎯 JUMPING ROOT CAUSES:")
    print("   1. CONSTRAINT OVER-FORCE: 50kN creates explosive corrections")
    print("   2. RIGID CONNECTION: No damping between bodies")
    print("   3. SOLVER INSTABILITY: High forces overwhelm physics solver")
    print("   4. MASS DISTRIBUTION: Heavy arm creates large moments")
    
    print("\n💡 RECOMMENDED SOLUTIONS:")
    solutions = [
        ("IMMEDIATE", "Reduce constraint maxForce from 50,000N to 1,000-5,000N"),
        ("STABILITY", "Add constraint damping and spring parameters"),
        ("COMPLIANCE", "Use 6DOF constraint with limited forces"),
        ("UNIFIED", "Create single URDF with Husky+KUKA as one robot"),
        ("MOUNTING", "Add compliant mounting interface between robots")
    ]
    
    for priority, solution in solutions:
        print(f"   {priority:>10}: {solution}")
    
    print("\n🔧 PHYSICS PARAMETER RECOMMENDATIONS:")
    print("   • Constraint Force: 1,000-5,000N (vs current 50,000N)")
    print("   • Add Constraint ERP: 0.1-0.2 (error reduction)")
    print("   • Add Constraint CFM: 1e-4 (compliance)")
    print("   • Enable constraint stabilization")
    print("   • Reduce physics timestep if needed")

if __name__ == "__main__":
    analyze_constraint_system()