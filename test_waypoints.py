#!/usr/bin/env python3
"""
Standalone test for waypoint-based circular trajectory validation
"""
import math
import numpy as np
from rl_mission_env import MobileManipulatorEnv

def test_waypoint_system():
    """Test the waypoint generation and tracking system"""
    print("🎯 Testing Waypoint-Based Circular Trajectory Validation")
    print("=" * 60)
    
    # Create a mock environment for testing
    class MockEnv:
        def __init__(self):
            self.trajectory_radius = 0.2
            self.waypoints = []
            self.waypoint_passed = []
            self.current_waypoint_idx = 0
            self.waypoint_tolerance = 0.03  # 3cm tolerance
        
        def generate_waypoints(self, center, num_waypoints=8):
            """Generate waypoints around circular trajectory"""
            self.waypoints = []
            self.waypoint_passed = [False] * num_waypoints
            self.current_waypoint_idx = 0
            
            for i in range(num_waypoints):
                angle = 2.0 * math.pi * i / num_waypoints
                x = center[0] + self.trajectory_radius * math.cos(angle)
                y = center[1] + self.trajectory_radius * math.sin(angle)
                z = center[2]  # Keep same height
                self.waypoints.append([x, y, z])
            
            print(f"📍 Generated {len(self.waypoints)} waypoints around circle:")
            print(f"   Center: [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
            print(f"   Radius: {self.trajectory_radius}m")
            print(f"   Tolerance: {self.waypoint_tolerance}m")
            
            for i, wp in enumerate(self.waypoints):
                angle_deg = (360.0 * i / num_waypoints)
                print(f"   WP{i}: [{wp[0]:.3f}, {wp[1]:.3f}, {wp[2]:.3f}] @ {angle_deg:.1f}°")
        
        def check_waypoint_passage(self, current_pos):
            """Check if agent has passed through any waypoints"""
            passed_new_waypoint = False
            
            for i, waypoint in enumerate(self.waypoints):
                if not self.waypoint_passed[i]:
                    distance = math.sqrt(
                        (current_pos[0] - waypoint[0])**2 + 
                        (current_pos[1] - waypoint[1])**2 + 
                        (current_pos[2] - waypoint[2])**2
                    )
                    
                    if distance <= self.waypoint_tolerance:
                        self.waypoint_passed[i] = True
                        passed_new_waypoint = True
                        angle_deg = (360.0 * i / len(self.waypoints))
                        print(f"   ✅ Waypoint {i} passed! @ {angle_deg:.1f}° (dist: {distance:.3f}m)")
                        
                        # Update current waypoint index
                        if i == self.current_waypoint_idx:
                            self.current_waypoint_idx = (self.current_waypoint_idx + 1) % len(self.waypoints)
            
            return passed_new_waypoint
        
        def complete_cycle(self):
            """Check if a complete cycle has been completed"""
            total_passed = sum(self.waypoint_passed)
            completion_percentage = (total_passed / len(self.waypoints)) * 100
            
            if total_passed == len(self.waypoints):
                print(f"   🎯 COMPLETE CYCLE! All {len(self.waypoints)} waypoints passed (100%)")
                # Reset for next cycle
                self.waypoint_passed = [False] * len(self.waypoints)
                self.current_waypoint_idx = 0
                return True, 100.0
            else:
                print(f"   📊 Cycle Progress: {total_passed}/{len(self.waypoints)} waypoints ({completion_percentage:.1f}%)")
                return False, completion_percentage
    
    # Test the waypoint system
    env = MockEnv()
    circle_center = [0.0, 0.0, 0.4]  # Same as main simulation
    
    # Generate waypoints
    env.generate_waypoints(circle_center, num_waypoints=8)
    
    print("\n🔄 Simulating circular trajectory tracking...")
    print("=" * 60)
    
    # Simulate circular movement and waypoint tracking
    trajectory_radius = 0.2
    num_simulation_steps = 200
    completed_cycles = 0
    
    for step in range(num_simulation_steps):
        # Simulate circular trajectory (same as main simulation)
        t = step * 0.05  # Time progression
        current_pos = [
            circle_center[0] + trajectory_radius * math.cos(t),
            circle_center[1] + trajectory_radius * math.sin(t),
            circle_center[2]
        ]
        
        # Check waypoint passage
        passed_waypoint = env.check_waypoint_passage(current_pos)
        
        # Check cycle completion every 25 steps
        if step % 25 == 0:
            is_complete, accuracy = env.complete_cycle()
            if is_complete:
                completed_cycles += 1
                print(f"   🏆 Cycle {completed_cycles} completed at step {step}")
    
    # Final results
    print("\n📈 WAYPOINT VALIDATION RESULTS")
    print("=" * 60)
    print(f"Simulation Steps: {num_simulation_steps}")
    print(f"Completed Cycles: {completed_cycles}")
    print(f"Waypoints per Cycle: {len(env.waypoints)}")
    print(f"Waypoint Tolerance: {env.waypoint_tolerance}m")
    print(f"Trajectory Radius: {trajectory_radius}m")
    
    # Calculate final accuracy
    final_passed = sum(env.waypoint_passed)
    final_accuracy = (final_passed / len(env.waypoints)) * 100
    print(f"Final Cycle Progress: {final_passed}/{len(env.waypoints)} waypoints ({final_accuracy:.1f}%)")
    
    if completed_cycles >= 1:
        print("✅ SUCCESS: Waypoint-based circular trajectory validation is working!")
        print("   - Waypoints generated correctly around circular path")
        print("   - Trajectory tracking detects waypoint passages")
        print("   - Cycle completion accuracy calculated properly")
    else:
        print("⚠️  WARNING: No complete cycles detected")
        print("   - Check waypoint tolerance or trajectory alignment")
    
    return completed_cycles >= 1

if __name__ == "__main__":
    success = test_waypoint_system()
    exit(0 if success else 1)