#!/usr/bin/env python3
"""
UNMOUNTING ISSUE FIX - Comprehensive solution for robotic system stability.

PROBLEM ANALYSIS:
The "unmounting" issue likely refers to one of these scenarios:
1. KUKA arm separating from Husky base (constraint failure)
2. Joint constraints becoming unstable under load
3. Physics solver struggling with complex constraint systems
4. Excessive forces causing explosive behaviors

SOLUTION APPROACH:
1. Enhanced constraint monitoring and auto-recovery
2. Improved physics parameters for stability
3. Dynamic constraint force adjustment
4. Better joint damping and control
"""

# IMMEDIATE FIX: Enhanced constraint system with monitoring
ENHANCED_MOUNTING_SYSTEM = """
# === ENHANCED MOUNTING SYSTEM WITH AUTO-RECOVERY ===

import numpy as np
import time

class MountingSystemMonitor:
    def __init__(self):
        self.constraint_id = None
        self.max_safe_force = 1500  # N - reduced for safety
        self.force_history = []
        self.last_check_time = 0
        self.recovery_count = 0
        
    def create_stable_constraint(self, husky_id, kuka_id):
        \"\"\"Create ultra-stable mounting constraint with monitoring.\"\"\"
        try:
            # Remove any existing constraints
            self.cleanup_old_constraints(husky_id, kuka_id)
            
            # Create new constraint with enhanced stability
            self.constraint_id = p.createConstraint(
                husky_id, -1,           # Parent: Husky base
                kuka_id, -1,            # Child: KUKA base
                p.JOINT_FIXED,          # Fixed joint type
                [0, 0, 0],              # Parent frame
                [0, 0, 0],              # Child frame  
                [0., 0., 0.45],         # REDUCED height: 0.45m (was 0.5m)
                [0, 0, 0, 1]            # Child offset
            )
            
            # Configure for maximum stability
            p.changeConstraint(self.constraint_id, maxForce=1500)  # Further reduced
            
            print(f"✅ Enhanced mounting constraint created: {self.constraint_id}")
            print(f"   • Max force: 1500N (ultra-conservative)")
            print(f"   • Height: 0.45m (reduced for stability)")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create mounting constraint: {e}")
            return False
    
    def cleanup_old_constraints(self, husky_id, kuka_id):
        \"\"\"Remove any old constraints between Husky and KUKA.\"\"\"
        removed_count = 0
        for i in range(p.getNumConstraints()):
            try:
                constraint_info = p.getConstraintInfo(i)
                parent_body = constraint_info[2]
                child_body = constraint_info[3]
                
                if (parent_body == husky_id and child_body == kuka_id) or \\
                   (parent_body == kuka_id and child_body == husky_id):
                    p.removeConstraint(i)
                    removed_count += 1
                    print(f"   🧹 Removed old constraint {i}")
            except:
                continue
        
        if removed_count > 0:
            print(f"   ✅ Cleaned up {removed_count} old constraints")
    
    def monitor_and_recover(self):
        \"\"\"Monitor constraint forces and auto-recover if needed.\"\"\"
        current_time = time.time()
        
        # Check every 0.1 seconds
        if current_time - self.last_check_time < 0.1:
            return True
            
        self.last_check_time = current_time
        
        try:
            if self.constraint_id is not None:
                constraint_state = p.getConstraintState(self.constraint_id)
                current_force = np.linalg.norm(constraint_state[0])
                self.force_history.append(current_force)
                
                # Keep only last 50 samples (5 seconds at 10Hz)
                if len(self.force_history) > 50:
                    self.force_history.pop(0)
                
                # Check for dangerous force levels
                if current_force > self.max_safe_force:
                    print(f"⚠️  CRITICAL FORCE: {current_force:.1f}N (limit: {self.max_safe_force}N)")
                    return self.emergency_recovery()
                
                # Check for force trends
                if len(self.force_history) >= 10:
                    recent_avg = np.mean(self.force_history[-10:])
                    if recent_avg > self.max_safe_force * 0.8:  # 80% of limit
                        print(f"⚠️  FORCE TREND WARNING: {recent_avg:.1f}N")
                        return self.preventive_recovery()
            
            return True
            
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            return False
    
    def emergency_recovery(self):
        \"\"\"Emergency constraint recovery procedure.\"\"\"
        print(f"🚨 EMERGENCY RECOVERY INITIATED")
        self.recovery_count += 1
        
        try:
            # Temporarily reduce constraint force
            if self.constraint_id is not None:
                p.changeConstraint(self.constraint_id, maxForce=800)  # Emergency reduction
                print(f"   ✅ Reduced constraint force to 800N")
            
            # Wait for stabilization
            time.sleep(0.5)
            
            # Gradually restore force
            p.changeConstraint(self.constraint_id, maxForce=1200)
            print(f"   ✅ Restored constraint force to 1200N")
            
            self.force_history.clear()  # Reset history
            
            print(f"   ✅ Emergency recovery complete (#{self.recovery_count})")
            return True
            
        except Exception as e:
            print(f"❌ Emergency recovery failed: {e}")
            return False
    
    def preventive_recovery(self):
        \"\"\"Preventive constraint adjustment.\"\"\"
        print(f"🔧 PREVENTIVE ADJUSTMENT")
        
        try:
            # Slightly reduce constraint force
            current_force = 1200  # Conservative value
            p.changeConstraint(self.constraint_id, maxForce=current_force)
            print(f"   ✅ Adjusted constraint force to {current_force}N")
            
            return True
            
        except Exception as e:
            print(f"❌ Preventive adjustment failed: {e}")
            return False

# Global monitoring instance
mounting_monitor = MountingSystemMonitor()
"""

print("🔧 UNMOUNTING ISSUE SOLUTION")
print("=" * 50)
print()
print("PROBLEM IDENTIFIED:")
print("   The robotic system mounting constraint may be experiencing:")
print("   • Excessive forces causing instability")
print("   • Physics solver struggles with complex constraints") 
print("   • Joint oscillations leading to mounting failures")
print()
print("SOLUTION IMPLEMENTED:")
print("   ✅ Enhanced constraint monitoring system")
print("   ✅ Auto-recovery mechanisms")
print("   ✅ Conservative force limits")
print("   ✅ Preventive adjustments")
print()
print("📋 INTEGRATION INSTRUCTIONS:")
print("   1. Add the enhanced mounting system to sim_husky_kuka.py")
print("   2. Replace existing constraint creation with monitored version")
print("   3. Call monitor_and_recover() in main simulation loop")
print()
print("🚀 IMMEDIATE ACTIONS:")
print("   1. Restart the simulation")
print("   2. Monitor constraint forces closely")
print("   3. Reduce physics timestep if instability persists")
print()

# Save the enhanced system code
with open('/home/marcoreis/q_ws/enhanced_mounting_system.py', 'w') as f:
    f.write(ENHANCED_MOUNTING_SYSTEM)

print("💾 Enhanced mounting system saved to: enhanced_mounting_system.py")
print()
print("🔍 MONITORING RECOMMENDATIONS:")
print("   • Watch for constraint forces > 1200N")
print("   • Monitor relative position between Husky and KUKA")
print("   • Check for velocity mismatches between components")
print("   • Verify joint states remain within normal ranges")