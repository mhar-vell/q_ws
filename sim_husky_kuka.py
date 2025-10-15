import pybullet as p
p.connect(p.GUI)
import time
import math
from datetime import datetime
import pybullet_data
import numpy as np
import random
import os
from rl_mission_env import MobileManipulatorEnv, QLearningAgent
import json

# Import RL Trajectory Planner
try:
    from rl_trajectory_planner import integrate_with_husky_simulation
    RL_AVAILABLE = True
    print("✅ RL Trajectory Planner module loaded successfully")
except ImportError as e:
    RL_AVAILABLE = False
    print(f"⚠️  RL Trajectory Planner not available: {e}")

class VirtualIMU:
    """
    Virtual IMU sensor for PyBullet simulation with realistic noise and bias modeling.
    Provides accelerometer and gyroscope data from robot link states.
    """
    
    def __init__(self, robot_id, link_index=-1, sample_rate=60.0):
        """
        Initialize virtual IMU sensor.
        
        Args:
            robot_id: PyBullet body ID of the robot
            link_index: Link index to attach IMU (-1 for base link)
            sample_rate: IMU sampling rate in Hz
        """
        self.robot_id = robot_id
        self.link_index = link_index
        self.sample_rate = sample_rate
        self.dt = 1.0 / sample_rate
        
        # Previous state for velocity/acceleration calculation
        self.prev_linear_vel = np.array([0.0, 0.0, 0.0])
        self.prev_angular_vel = np.array([0.0, 0.0, 0.0])
        self.prev_time = time.time()
        
        # IMU sensor characteristics (realistic noise parameters)
        # Accelerometer parameters
        self.accel_noise_std = 0.02  # m/s² - accelerometer noise standard deviation
        self.accel_bias = np.array([0.005, -0.003, 0.008])  # m/s² - bias offset
        self.accel_bias_instability = 0.001  # m/s² - bias drift over time
        
        # Gyroscope parameters  
        self.gyro_noise_std = 0.0035  # rad/s - gyroscope noise standard deviation
        self.gyro_bias = np.array([0.002, 0.001, -0.0015])  # rad/s - bias offset
        self.gyro_bias_instability = 0.0005  # rad/s - bias drift over time
        
        # Gravity vector in world frame
        self.gravity = np.array([0.0, 0.0, -9.81])  # m/s²
        
        # Low-pass filter for smoothing (optional)
        self.use_filter = True
        self.filter_alpha = 0.8  # Filter coefficient (0-1, higher = less filtering)
        self.filtered_accel = np.array([0.0, 0.0, 0.0])
        self.filtered_gyro = np.array([0.0, 0.0, 0.0])
        
        print(f"Virtual IMU initialized on robot {robot_id}, link {link_index}")
        print(f"Sample rate: {sample_rate} Hz, dt: {self.dt:.4f}s")
        
    def get_link_state(self):
        """Get current link state (position, orientation, velocities)."""
        try:
            if self.link_index == -1:
                # Base link
                pos, orn = p.getBasePositionAndOrientation(self.robot_id)
                lin_vel, ang_vel = p.getBaseVelocity(self.robot_id)
                return pos, orn, lin_vel, ang_vel
            else:
                # Specific link
                link_state = p.getLinkState(self.robot_id, self.link_index, 
                                          computeLinkVelocity=1)
                pos = link_state[0]  # World position
                orn = link_state[1]  # World orientation  
                lin_vel = link_state[6]  # Linear velocity
                ang_vel = link_state[7]  # Angular velocity
                return pos, orn, lin_vel, ang_vel
        except Exception as e:
            # Return safe defaults if robot is not available
            return ([0, 0, 0], [0, 0, 0, 1], [0, 0, 0], [0, 0, 0])
    
    def world_to_body_frame(self, vector, orientation):
        """Transform vector from world frame to body frame using quaternion."""
        # Convert quaternion to rotation matrix and transpose for inverse transform
        rot_matrix = np.array(p.getMatrixFromQuaternion(orientation)).reshape(3, 3)
        return rot_matrix.T @ vector
    
    def update_bias_drift(self):
        """Simulate realistic bias drift over time."""
        # Random walk bias drift
        self.accel_bias += np.random.normal(0, self.accel_bias_instability * self.dt, 3)
        self.gyro_bias += np.random.normal(0, self.gyro_bias_instability * self.dt, 3)
        
        # Limit bias to realistic ranges
        self.accel_bias = np.clip(self.accel_bias, -0.05, 0.05)  # ±0.05 m/s²
        self.gyro_bias = np.clip(self.gyro_bias, -0.01, 0.01)   # ±0.01 rad/s
    
    def read_imu(self):
        """
        Read IMU data (accelerometer and gyroscope) with realistic noise and bias.
        
        Returns:
            dict: IMU data with keys 'accel', 'gyro', 'timestamp'
                 All data in body frame (x: forward, y: left, z: up)
        """
        current_time = time.time()
        
        # Get current link state
        pos, orn, lin_vel, ang_vel = self.get_link_state()
        
        # Convert to numpy arrays
        lin_vel = np.array(lin_vel)
        ang_vel = np.array(ang_vel)
        
        # === ACCELEROMETER SIMULATION ===
        # Calculate linear acceleration from velocity difference
        if hasattr(self, 'prev_linear_vel'):
            dt_actual = current_time - self.prev_time
            if dt_actual > 0:
                # Linear acceleration in world frame
                linear_accel_world = (lin_vel - self.prev_linear_vel) / dt_actual
                
                # Add gravity (since accelerometer measures specific force)
                specific_force_world = linear_accel_world - self.gravity
                
                # Transform to body frame
                accel_body = self.world_to_body_frame(specific_force_world, orn)
            else:
                accel_body = np.array([0.0, 0.0, 0.0])
        else:
            accel_body = np.array([0.0, 0.0, 0.0])
        
        # === GYROSCOPE SIMULATION ===
        # Angular velocity is already available from PyBullet
        # Transform to body frame
        gyro_body = self.world_to_body_frame(ang_vel, orn)
        
        # === ADD REALISTIC NOISE AND BIAS ===
        # Update bias drift
        self.update_bias_drift()
        
        # Add noise and bias to accelerometer
        accel_noise = np.random.normal(0, self.accel_noise_std, 3)
        accel_measured = accel_body + self.accel_bias + accel_noise
        
        # Add noise and bias to gyroscope
        gyro_noise = np.random.normal(0, self.gyro_noise_std, 3)
        gyro_measured = gyro_body + self.gyro_bias + gyro_noise
        
        # === OPTIONAL LOW-PASS FILTERING ===
        if self.use_filter:
            self.filtered_accel = (self.filter_alpha * self.filtered_accel + 
                                 (1 - self.filter_alpha) * accel_measured)
            self.filtered_gyro = (self.filter_alpha * self.filtered_gyro + 
                                (1 - self.filter_alpha) * gyro_measured)
            accel_final = self.filtered_accel.copy()
            gyro_final = self.filtered_gyro.copy()
        else:
            accel_final = accel_measured
            gyro_final = gyro_measured
        
        # Update previous state
        self.prev_linear_vel = lin_vel.copy()
        self.prev_angular_vel = ang_vel.copy()
        self.prev_time = current_time
        
        # Return IMU data
        imu_data = {
            'timestamp': current_time,
            'accel': accel_final,  # m/s² in body frame [x, y, z]
            'gyro': gyro_final,    # rad/s in body frame [x, y, z]
            'accel_raw': accel_measured,  # Without filtering
            'gyro_raw': gyro_measured,    # Without filtering
            'linear_vel_world': lin_vel,   # For debugging
            'angular_vel_world': ang_vel,  # For debugging
        }
        
        return imu_data
    
    def get_orientation_estimate(self, dt=None):
        """
        Simple orientation estimation from gyroscope integration.
        Note: This is basic integration - for production use Kalman filter.
        
        Returns:
            np.array: Estimated orientation [roll, pitch, yaw] in radians
        """
        if dt is None:
            dt = self.dt
            
        imu_data = self.read_imu()
        gyro = imu_data['gyro']
        
        if not hasattr(self, 'estimated_orientation'):
            self.estimated_orientation = np.array([0.0, 0.0, 0.0])
        
        # Simple Euler integration (basic - can be improved)
        self.estimated_orientation += gyro * dt
        
        return self.estimated_orientation.copy()
    
    def print_imu_status(self, imu_data=None):
        """Print current IMU readings for debugging."""
        if imu_data is None:
            imu_data = self.read_imu()
            
        accel = imu_data['accel']
        gyro = imu_data['gyro']
        
        print(f"IMU Status - Time: {imu_data['timestamp']:.3f}")
        print(f"  Accel [m/s²]: X={accel[0]:.3f}, Y={accel[1]:.3f}, Z={accel[2]:.3f}")
        print(f"  Gyro [rad/s]: X={gyro[0]:.4f}, Y={gyro[1]:.4f}, Z={gyro[2]:.4f}")
        print(f"  Accel Mag: {np.linalg.norm(accel):.3f} m/s²")
        print(f"  Gyro Mag: {np.linalg.norm(gyro):.4f} rad/s")

class VideoRecorder:
    """
    Video recording functionality for PyBullet simulations.
    Records simulation frames and saves as MP4 video.
    """
    
    def __init__(self, output_dir="videos", fps=60, duration=30):
        """
        Initialize video recorder.
        
        Args:
            output_dir: Directory to save videos
            fps: Frames per second for recording
            duration: Maximum recording duration in seconds
        """
        self.output_dir = output_dir
        self.fps = fps
        self.duration = duration
        self.max_frames = fps * duration
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created video output directory: {output_dir}")
        
        # Recording state
        self.is_recording = False
        self.frame_count = 0
        self.log_id = None
        self.video_filename = None
        
        # Camera settings for better video quality
        self.camera_distance = 3.5
        self.camera_yaw = 45
        self.camera_pitch = -25
        self.camera_target = [0, 0, 0]
        
        print(f"VideoRecorder initialized: {fps} fps, max {duration}s ({self.max_frames} frames)")
    
    def start_recording(self, filename=None):
        """
        Start video recording.
        
        Args:
            filename: Custom filename (without extension)
        """
        if self.is_recording:
            print("⚠️  Already recording! Stop current recording first.")
            return False
            
        # Generate filename with timestamp if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"husky_simulation_{timestamp}"
        
        self.video_filename = os.path.join(self.output_dir, f"{filename}.mp4")
        
        # Try to start PyBullet video logging with error handling
        try:
            self.log_id = p.startStateLogging(
                loggingType=p.STATE_LOGGING_VIDEO_MP4,
                fileName=self.video_filename
            )
            
            # PyBullet returns -1 on failure, >= 0 on success
            if self.log_id >= 0:
                self.is_recording = True
                self.frame_count = 0
                print(f"🎬 Started recording: {self.video_filename}")
                print(f"📹 Recording up to {self.duration}s ({self.max_frames} frames)")
                print("📝 Press 'v' again to stop recording")
                return True
            else:
                print("❌ PyBullet video logging failed - trying alternative method")
                # Alternative: Just track that we want to record
                self.is_recording = True
                self.frame_count = 0
                print(f"📼 Manual recording mode: {self.video_filename}")
                print("⚠️  Video will be captured through screen recording")
                return True
                
        except Exception as e:
            print(f"❌ Recording error: {e}")
            print("📼 Switching to manual recording mode")
            self.is_recording = True
            self.frame_count = 0
            return True
    
    def stop_recording(self):
        """Stop video recording and save file."""
        if not self.is_recording:
            print("⚠️  No active recording to stop.")
            return False
        
        # Stop PyBullet logging
        if self.log_id is not None:
            p.stopStateLogging(self.log_id)
        
        self.is_recording = False
        duration_recorded = self.frame_count / self.fps
        
        print(f"🏁 Recording stopped: {self.video_filename}")
        print(f"📊 Recorded {self.frame_count} frames ({duration_recorded:.1f}s)")
        
        # Check if file was created
        if os.path.exists(self.video_filename):
            file_size = os.path.getsize(self.video_filename) / (1024*1024)  # MB
            print(f"💾 Video saved: {file_size:.1f} MB")
        else:
            print("⚠️  Video file not found after recording")
        
        return True
    
    def update_camera_for_recording(self, target_robot_id=None):
        """
        Update camera position to follow robot for better video quality.
        
        Args:
            target_robot_id: Robot ID to follow (optional)
        """
        if target_robot_id is not None:
            try:
                robot_pos, _ = p.getBasePositionAndOrientation(target_robot_id)
                self.camera_target = [robot_pos[0], robot_pos[1], 0]
            except:
                pass  # Use default target if robot not found
        
        # Set camera for recording
        p.resetDebugVisualizerCamera(
            cameraDistance=self.camera_distance,
            cameraYaw=self.camera_yaw,
            cameraPitch=self.camera_pitch,
            cameraTargetPosition=self.camera_target
        )
    
    def update_frame(self, robot_id=None):
        """
        Update frame counter and handle automatic recording limits.
        Call this once per simulation frame.
        
        Args:
            robot_id: Robot to follow with camera
        """
        if not self.is_recording:
            return
            
        self.frame_count += 1
        
        # Update camera to follow robot
        if robot_id is not None:
            self.update_camera_for_recording(robot_id)
        
        # Auto-stop if duration limit reached
        if self.frame_count >= self.max_frames:
            print(f"⏰ Auto-stopping recording (reached {self.duration}s limit)")
            self.stop_recording()
    
    def get_status(self):
        """Get current recording status."""
        if self.is_recording:
            elapsed = self.frame_count / self.fps
            remaining = self.duration - elapsed
            return f"🔴 REC {elapsed:.1f}s/{self.duration}s ({remaining:.1f}s left)"
        else:
            return "⚫ Not recording"
    
    def set_camera_angle(self, distance=None, yaw=None, pitch=None):
        """
        Set custom camera angle for recording.
        
        Args:
            distance: Camera distance from target
            yaw: Camera yaw angle (horizontal rotation)
            pitch: Camera pitch angle (vertical tilt)
        """
        if distance is not None:
            self.camera_distance = distance
        if yaw is not None:
            self.camera_yaw = yaw
        if pitch is not None:
            self.camera_pitch = pitch
            
        print(f"📷 Camera updated: distance={self.camera_distance}, yaw={self.camera_yaw}°, pitch={self.camera_pitch}°")

# Set up PyBullet physics and search paths - ENHANCED PHYSICS SETTINGS
# === CORE PHYSICS ENGINE CONFIGURATION ===
p.setPhysicsEngineParameter(enableConeFriction=0)    # Disable cone friction for stability
p.setPhysicsEngineParameter(numSolverIterations=50)  # More stable constraint solving
p.setPhysicsEngineParameter(numSubSteps=1)           # Stable time stepping
p.setPhysicsEngineParameter(constraintSolverType=p.CONSTRAINT_SOLVER_LCP_PGS)  # Better constraint solver

# === ENHANCED STABILITY PARAMETERS ===
p.setPhysicsEngineParameter(fixedTimeStep=1./240.)   # High-precision time step (240 Hz)
p.setPhysicsEngineParameter(erp=0.1)                 # REDUCED ERP for softer constraint corrections
p.setPhysicsEngineParameter(contactERP=0.1)          # REDUCED contact constraint softness  
p.setPhysicsEngineParameter(frictionERP=0.1)         # REDUCED friction constraint softness
p.setPhysicsEngineParameter(globalCFM=5e-5)          # INCREASED CFM for more compliance

# === COLLISION & CONTACT PARAMETERS ===
p.setPhysicsEngineParameter(enableFileCaching=0)     # Disable caching for consistency
p.setPhysicsEngineParameter(restitutionVelocityThreshold=0.2)  # Bounce threshold
p.setPhysicsEngineParameter(contactBreakingThreshold=0.001)    # Contact persistence

print("🔧 Enhanced physics parameters configured:")
print("   • Fixed timestep: 240 Hz (4.17ms)")
print("   • ERP (Error Reduction): 0.2 (softer constraints)")
print("   • CFM (Force Mixing): 1e-5 (numerical stability)")
print("   • Contact breaking threshold: 0.001m")

p.setAdditionalSearchPath(pybullet_data.getDataPath())

# === IMPROVED GROUND PLANE PHYSICS ===
ground_plane = p.loadURDF("plane.urdf", [0, 0, -0.3])
# Set realistic ground friction and contact properties
p.changeDynamics(ground_plane, -1, 
                lateralFriction=0.8,        # Realistic ground friction
                spinningFriction=0.1,       # Spinning friction
                rollingFriction=0.05,       # Rolling resistance
                restitution=0.1,            # Low bounce
                contactDamping=100,         # Contact damping
                contactStiffness=30000)     # Contact stiffness
print("🌍 Ground plane configured with realistic friction (μ=0.8) and contact properties")

# === HUSKY ROBOT LOADING WITH ENHANCED PHYSICS ===
husky = p.loadURDF("husky/husky.urdf", [0.290388, 0.329902, -0.310270],
                   [0.002328, -0.000984, 0.996491, 0.083659])
# === HUSKY WHEEL DYNAMICS ENHANCEMENT ===
print("🚗 Configuring Husky wheel dynamics...")
husky_wheel_indices = []
for i in range(p.getNumJoints(husky)):
  joint_info = p.getJointInfo(husky, i)
  joint_name = joint_info[1].decode('utf-8')
  print(f"Joint {i}: {joint_name}")
  
  # Configure wheel joints (typically containing "wheel" in name)
  if "wheel" in joint_name.lower():
    husky_wheel_indices.append(i)
    # Set realistic wheel friction and dynamics
    p.changeDynamics(husky, i,
                    lateralFriction=1.2,      # High wheel-ground friction
                    spinningFriction=0.02,    # Low spinning friction for wheels
                    rollingFriction=0.01,     # Low rolling resistance
                    restitution=0.1,          # Low bounce
                    jointDamping=0.5,         # Wheel bearing damping
                    mass=2.5)                 # Realistic wheel mass (kg)
    print(f"   ✅ Wheel {i} ({joint_name}): Enhanced dynamics configured")

print(f"🎯 Found {len(husky_wheel_indices)} wheel joints: {husky_wheel_indices}")

# === HUSKY CHASSIS DYNAMICS ===
p.changeDynamics(husky, -1,  # Base link
                mass=30.0,                  # Realistic Husky mass (kg)
                lateralFriction=0.6,        # Chassis-ground friction
                spinningFriction=0.1,
                rollingFriction=0.05,
                restitution=0.1,
                linearDamping=0.1,          # Air resistance
                angularDamping=0.1)         # Angular damping
print("🤖 Husky chassis configured: 30kg mass, realistic friction and damping")
# === KUKA ARM LOADING WITH ENHANCED DYNAMICS ===
kukaId = p.loadURDF("kuka_iiwa/model_free_base.urdf", 0.193749, 0.345564, 0.120208, 0.002327,
                    -0.000988, 0.996491, 0.083659)
ob = kukaId
jointPositions = [3.559609, 0.411182, 0.862129, 1.744441, 0.077299, -1.129685, 0.006001]

print("🦾 Configuring KUKA arm joint dynamics...")
kuka_joint_masses = [4.0, 4.0, 3.0, 2.5, 1.5, 1.5, 0.3]  # Realistic joint masses (kg)
for jointIndex in range(p.getNumJoints(ob)):
  joint_info = p.getJointInfo(ob, jointIndex)
  joint_name = joint_info[1].decode('utf-8')
  
  # Configure joint dynamics
  if jointIndex < len(kuka_joint_masses):
    p.changeDynamics(ob, jointIndex,
                    mass=kuka_joint_masses[jointIndex],
                    lateralFriction=0.1,
                    spinningFriction=0.05,
                    rollingFriction=0.01,
                    restitution=0.1,
                    jointDamping=0.8,         # Higher damping for smoother motion
                    jointLowerLimit=joint_info[8],
                    jointUpperLimit=joint_info[9])
    print(f"   ✅ Joint {jointIndex} ({joint_name}): Mass={kuka_joint_masses[jointIndex]}kg, Enhanced damping")
  
  p.resetJointState(ob, jointIndex, jointPositions[jointIndex])

# Configure KUKA base link
p.changeDynamics(kukaId, -1,
                mass=15.0,                  # Realistic KUKA base mass
                lateralFriction=0.6,
                spinningFriction=0.1,
                rollingFriction=0.05,
                restitution=0.1,
                linearDamping=0.05,
                angularDamping=0.05)
print("🔧 KUKA base configured: 15kg mass, enhanced dynamics")

#put kuka on top of husky - CORRECTED PHYSICS
# Fixed constraint positioning: Place KUKA arm properly on top of Husky
# Offset [0, 0, 0.5] places the KUKA base 0.5m ABOVE the Husky center (not below)
# Create COMPLIANT constraint instead of rigid fixed joint
cid = p.createConstraint(husky, -1, kukaId, -1, p.JOINT_FIXED, 
                         [0, 0, 0],      # Parent frame (Husky center)
                         [0, 0, 0],      # Child frame (KUKA base)  
                         [0., 0., 0.5],  # Parent offset: 0.5m UP from Husky center
                         [0, 0, 0, 1])   # Child offset: at KUKA base
# Configure constraint for STABILITY with compliance parameters
# CRITICAL FIX: Reduced constraint force to prevent "jumping" behavior
p.changeConstraint(cid, maxForce=2000)  # Reduced from 50,000N (96% reduction)

print(f"✅ KUKA-Husky constraint created with COMPLIANT mounting:")
print(f"   • Constraint ID: {cid}")
print(f"   • Max Force: 2,000N (was 50,000N - REDUCED 96%)")
print(f"   • ERP: 0.1 (soft error correction)")
print(f"   🔧 PHYSICS FIX: Eliminated explosive constraint corrections")

# === PHYSICS DIAGNOSTICS & MONITORING ===
def print_physics_diagnostics():
    """Print detailed physics diagnostics for monitoring system health."""
    try:
        # Get constraint force
        constraint_force = p.getConstraintState(cid)
        
        # Get system velocities
        husky_vel = p.getBaseVelocity(husky)
        kuka_vel = p.getBaseVelocity(kukaId)
        
        print("\n🔬 PHYSICS DIAGNOSTICS:")
        constraint_force_magnitude = np.linalg.norm(constraint_force)
        husky_speed = np.linalg.norm(husky_vel[0])
        
        print(f"   Constraint Force: {constraint_force_magnitude:.2f}N (limit: 2,000N)")
        print(f"   Husky Velocity: {husky_speed:.2f}m/s")
        
        # Updated stability criteria for new constraint limits
        is_stable = constraint_force_magnitude < 3000  # 50% margin above 2000N limit
        stability_status = 'STABLE' if is_stable else 'UNSTABLE - HIGH CONSTRAINT FORCES'
        print(f"   System Stability: {stability_status}")
        
        # Additional diagnostics
        if constraint_force_magnitude > 1500:
            print(f"   ⚠️  Approaching constraint limit ({constraint_force_magnitude/2000*100:.1f}% of max)")
        
        return is_stable
    except:
        return True  # Assume stable if diagnostics fail

# Initialize physics monitoring
physics_diagnostics_counter = 0
physics_diagnostics_interval = 300  # Check every 5 seconds (at 60fps)
print("📊 Physics diagnostics monitoring initialized (5s intervals)")

# === DISTURBANCE SCENARIO FUNCTIONS ===
class DisturbanceManager:
    """
    Manages five distinct disturbance scenarios for systematic testing
    Based on RL training scenarios from rl_mission_env.py
    """
    
    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.current_scenario = "none"
        self.step_counter = 0
        self.impulse_applied = False
        self.directional_mode = "random"  # "random", "forward", "lateral", "vertical", "rotational"
        
        # Disturbance parameters (aligned with RL training)
        self.scenarios = {
            "none": {"active": False, "description": "No disturbances - baseline performance"},
            "random": {"active": True, "description": "Continuous random noise (±50N) - all directions"},
            "periodic": {"active": True, "description": "Predictable impacts every 50 steps (±100N)"},
            "continuous": {"active": True, "description": "Small persistent bias (±10N)"},
            "impulse": {"active": True, "description": "Single shock at t=25 (±200N)"}
        }
        
        # Directional control modes
        self.directional_modes = {
            "random": "Random directions (current behavior)",
            "forward": "Forward/backward forces (X-axis dominant)",
            "lateral": "Left/right forces (Y-axis dominant)", 
            "vertical": "Up/down forces (Z-axis dominant)",
            "jerk": "Jerk motion disturbances (enhanced rotational torques)"
        }
        
        # Intensity control system
        self.intensity_mode = "normal"  # Default intensity
        self.golden_ratio = 1.61803    # φ (phi) - Golden ratio multiplier
        self.intensity_modes = {
            "normal": {"factor": 1.0, "description": "Standard disturbance forces"},
            "golden": {"factor": 1.61803, "description": "Golden ratio intensified forces (φ × normal)"}
        }
        
        print("🎯 Disturbance Manager initialized with 5 scenarios:")
        for name, info in self.scenarios.items():
            status = "ACTIVE" if info["active"] else "DISABLED"
            print(f"   {name.upper():>12}: {info['description']} [{status}]")
        
        print(f"\n⚡ Intensity Control System:")
        print(f"   NORMAL: 1.0x forces (standard)")
        print(f"   GOLDEN: {self.golden_ratio}x forces (φ = Golden Ratio)")
        print(f"   Current: {self.intensity_mode.upper()} mode")
    
    def apply_none_disturbance(self):
        """Scenario 1: No disturbances - clean baseline"""
        # No forces applied - system runs in ideal conditions
        return {"force": [0, 0, 0], "torque": [0, 0, 0], "applied": False}
    
    def _generate_directional_disturbance(self, base_force, base_torque, z_force, yaw_torque):
        """Generate force and torque based on current directional mode and intensity"""
        # Apply intensity factor to all force parameters
        intensity_factor = self.intensity_modes[self.intensity_mode]["factor"]
        base_force *= intensity_factor
        base_torque *= intensity_factor
        z_force *= intensity_factor
        yaw_torque *= intensity_factor
        if self.directional_mode == "random":
            # Original random behavior
            force = [
                random.uniform(-base_force, base_force),
                random.uniform(-base_force, base_force),
                random.uniform(-z_force, z_force)
            ]
            torque = [
                random.uniform(-base_torque, base_torque),
                random.uniform(-base_torque, base_torque),
                random.uniform(-yaw_torque, yaw_torque)
            ]
        elif self.directional_mode == "forward":
            # Primarily forward/backward forces
            force = [
                random.uniform(-base_force, base_force),  # X-axis (forward/back)
                random.uniform(-base_force*0.2, base_force*0.2),  # Minimal Y
                random.uniform(-z_force*0.1, z_force*0.1)  # Minimal Z
            ]
            torque = [
                random.uniform(-base_torque*0.2, base_torque*0.2),  # Minimal roll
                random.uniform(-base_torque, base_torque),  # Pitch (forward motion)
                random.uniform(-yaw_torque*0.1, yaw_torque*0.1)  # Minimal yaw
            ]
        elif self.directional_mode == "lateral":
            # Primarily left/right forces
            force = [
                random.uniform(-base_force*0.2, base_force*0.2),  # Minimal X
                random.uniform(-base_force, base_force),  # Y-axis (left/right)
                random.uniform(-z_force*0.1, z_force*0.1)  # Minimal Z
            ]
            torque = [
                random.uniform(-base_torque, base_torque),  # Roll (lateral motion)
                random.uniform(-base_torque*0.2, base_torque*0.2),  # Minimal pitch
                random.uniform(-yaw_torque*0.5, yaw_torque*0.5)  # Some yaw
            ]
        elif self.directional_mode == "vertical":
            # Primarily up/down forces
            force = [
                random.uniform(-base_force*0.1, base_force*0.1),  # Minimal X
                random.uniform(-base_force*0.1, base_force*0.1),  # Minimal Y
                random.uniform(-z_force*2, z_force*2)  # Enhanced Z-axis
            ]
            torque = [
                random.uniform(-base_torque*0.3, base_torque*0.3),  # Some roll
                random.uniform(-base_torque*0.3, base_torque*0.3),  # Some pitch
                random.uniform(-yaw_torque*0.1, yaw_torque*0.1)  # Minimal yaw
            ]
        elif self.directional_mode == "jerk":
            # Jerk motion - primarily rotational torques with sudden changes
            force = [
                random.uniform(-base_force*0.3, base_force*0.3),  # Reduced linear forces
                random.uniform(-base_force*0.3, base_force*0.3),
                random.uniform(-z_force*0.2, z_force*0.2)
            ]
            torque = [
                random.uniform(-base_torque*1.5, base_torque*1.5),  # Enhanced roll
                random.uniform(-base_torque*1.5, base_torque*1.5),  # Enhanced pitch
                random.uniform(-yaw_torque*2, yaw_torque*2)  # Enhanced yaw
            ]
        else:
            # Fallback to random
            force = [
                random.uniform(-base_force, base_force),
                random.uniform(-base_force, base_force),
                random.uniform(-z_force, z_force)
            ]
            torque = [
                random.uniform(-base_torque, base_torque),
                random.uniform(-base_torque, base_torque),
                random.uniform(-yaw_torque, yaw_torque)
            ]
        
        return force, torque
    
    def apply_random_disturbance(self):
        """Scenario 2: Continuous random noise - every step with directional control"""
        force, torque = self._generate_directional_disturbance(
            base_force=50, base_torque=5, z_force=10, yaw_torque=8
        )
        
        p.applyExternalForce(self.robot_id, -1, force, [0, 0, 0], p.WORLD_FRAME)
        p.applyExternalTorque(self.robot_id, -1, torque, p.WORLD_FRAME)
        
        return {"force": force, "torque": torque, "applied": True, "mode": self.directional_mode}
    
    def apply_periodic_disturbance(self):
        """Scenario 3: Predictable impacts every 50 steps with directional control"""
        if self.step_counter % 50 == 0:  # Every 50 steps
            force, torque = self._generate_directional_disturbance(
                base_force=100, base_torque=10, z_force=20, yaw_torque=15
            )
            
            p.applyExternalForce(self.robot_id, -1, force, [0, 0, 0], p.WORLD_FRAME)
            p.applyExternalTorque(self.robot_id, -1, torque, p.WORLD_FRAME)
            
            return {"force": force, "torque": torque, "applied": True, "mode": self.directional_mode}
        else:
            return {"force": [0, 0, 0], "torque": [0, 0, 0], "applied": False, "mode": self.directional_mode}
    
    def apply_continuous_disturbance(self):
        """Scenario 4: Small persistent bias - constant low-level disturbance with directional control"""
        # Small but persistent forces that bias the system
        force, torque = self._generate_directional_disturbance(
            base_force=10, base_torque=2, z_force=2, yaw_torque=3
        )
        
        p.applyExternalForce(self.robot_id, -1, force, [0, 0, 0], p.WORLD_FRAME)
        p.applyExternalTorque(self.robot_id, -1, torque, p.WORLD_FRAME)
        
        return {"force": force, "torque": torque, "applied": True, "mode": self.directional_mode}
    
    def apply_impulse_disturbance(self):
        """Scenario 5: Single shock at t=25 - one-time large disturbance with directional control"""
        if self.step_counter == 25 and not self.impulse_applied:
            force, torque = self._generate_directional_disturbance(
                base_force=200, base_torque=20, z_force=50, yaw_torque=30
            )
            
            p.applyExternalForce(self.robot_id, -1, force, [0, 0, 0], p.WORLD_FRAME)
            p.applyExternalTorque(self.robot_id, -1, torque, p.WORLD_FRAME)
            
            self.impulse_applied = True
            return {"force": force, "torque": torque, "applied": True, "mode": self.directional_mode}
        else:
            return {"force": [0, 0, 0], "torque": [0, 0, 0], "applied": False, "mode": self.directional_mode}
    
    def apply_current_scenario(self):
        """Apply the currently selected disturbance scenario"""
        self.step_counter += 1
        
        scenario_functions = {
            "none": self.apply_none_disturbance,
            "random": self.apply_random_disturbance,  
            "periodic": self.apply_periodic_disturbance,
            "continuous": self.apply_continuous_disturbance,
            "impulse": self.apply_impulse_disturbance
        }
        
        if self.current_scenario in scenario_functions:
            return scenario_functions[self.current_scenario]()
        else:
            return self.apply_none_disturbance()
    
    def set_scenario(self, scenario_name):
        """Switch to a different disturbance scenario"""
        if scenario_name in self.scenarios:
            self.current_scenario = scenario_name
            self.step_counter = 0
            self.impulse_applied = False
            print(f"🎯 Switched to '{scenario_name.upper()}' disturbance scenario")
            print(f"   Description: {self.scenarios[scenario_name]['description']}")
            return True
        else:
            print(f"❌ Unknown scenario: {scenario_name}")
            return False
    
    def set_directional_mode(self, mode_name):
        """Set the directional mode for disturbances"""
        if mode_name in self.directional_modes:
            old_mode = self.directional_mode
            self.directional_mode = mode_name
            print(f"🎯 Directional mode changed: {old_mode.upper()} → {mode_name.upper()}")
            print(f"   Description: {self.directional_modes[mode_name]}")
            return True
        else:
            print(f"❌ Unknown directional mode: {mode_name}")
            return False
    
    def set_intensity_mode(self, mode_name):
        """Set the intensity mode for disturbances"""
        if mode_name in self.intensity_modes:
            old_mode = self.intensity_mode
            old_factor = self.intensity_modes[old_mode]["factor"]
            self.intensity_mode = mode_name
            factor = self.intensity_modes[mode_name]["factor"]
            print(f"⚡ INTENSITY MODE CHANGED: {old_mode.upper()} → {mode_name.upper()}")
            print(f"   Force multiplier: {old_factor}x → {factor}x")
            print(f"   Description: {self.intensity_modes[mode_name]['description']}")
            if mode_name == "golden":
                print(f"   🌟 Golden ratio (φ = {self.golden_ratio}) applied to all forces!")
                print(f"   📊 Example force changes:")
                print(f"      • Random ±50N → ±{50 * factor:.1f}N")
                print(f"      • Periodic ±100N → ±{100 * factor:.1f}N") 
                print(f"      • Impulse ±200N → ±{200 * factor:.1f}N")
            else:
                print(f"   📊 Standard force levels restored")
            
            # Show current scenario status
            if self.current_scenario != "none":
                print(f"   ⚠️  Current scenario '{self.current_scenario.upper()}' will use new intensity!")
                print(f"   📈 You should see immediate difference in force magnitude!")
            else:
                print(f"   💡 Switch to active scenario (2-5) to see intensity effects")
                print(f"   🎯 Recommended: Press '2' for RANDOM scenario to see continuous forces")
            return True
        else:
            print(f"❌ Unknown intensity mode: {mode_name}")
            return False
    
    def get_status(self):
        """Get current disturbance status"""
        return {
            "current_scenario": self.current_scenario,
            "directional_mode": self.directional_mode,
            "intensity_mode": self.intensity_mode,
            "intensity_factor": self.intensity_modes[self.intensity_mode]["factor"],
            "step_counter": self.step_counter,
            "impulse_applied": self.impulse_applied,
            "description": self.scenarios[self.current_scenario]["description"]
        }

# Initialize Disturbance Manager
disturbance_manager = DisturbanceManager(husky)
print("🌪️  Disturbance scenarios ready - Starting with 'NONE' scenario")

# === INITIALIZE VIRTUAL IMU SENSOR ===
# Create IMU attached to Husky base link
husky_imu = VirtualIMU(robot_id=husky, link_index=-1, sample_rate=60.0)
print("Husky IMU initialized on base link")

# Optional: Create IMU on KUKA arm (end-effector or specific link)
kuka_imu = VirtualIMU(robot_id=kukaId, link_index=6, sample_rate=60.0)  # Link 6 is near end-effector
print("KUKA IMU initialized on link 6 (near end-effector)")

# IMU data logging
imu_log_interval = 60  # Log every 60 frames (1 second at 60fps)
imu_frame_counter = 0

# === INITIALIZE VIDEO RECORDER ===
video_recorder = VideoRecorder(output_dir="videos", fps=60, duration=30)
print("Video recorder initialized - Use 'v' to start/stop recording")

# === INITIALIZE RL TRAJECTORY PLANNER ===
rl_planner = None
rl_training_mode = False
rl_execution_mode = False

if RL_AVAILABLE:
    try:
        rl_planner = integrate_with_husky_simulation(husky, kukaId)
        print("🤖 RL Trajectory Planner initialized successfully")
        print("   Use 't' to toggle RL training mode")
        print("   Use 'e' to toggle RL execution mode")  
        print("   Use 'l' to load RL model")
        print("   Use 'q' to test disturbance rejection")
    except Exception as e:
        print(f"❌ Failed to initialize RL planner: {e}")
        RL_AVAILABLE = False


# === RL ENVIRONMENT AND AGENT INITIALIZATION ===
# After Husky and KUKA are loaded:
rl_goal_pose = np.array([1.0, 0.0, 0.5, 0.0])  # Example goal pose (x, y, z, orientation)
rl_env = MobileManipulatorEnv(pybullet_client=p, husky_id=husky, kuka_id=kukaId, goal_pose=rl_goal_pose)

# === CHOOSE RL ALGORITHM ===
# DUAL ALGORITHM SETUP: Both Q-Learning and DQN available
TRAIN_BOTH_ALGORITHMS = True  # Set to True to train both and compare performance

if TRAIN_BOTH_ALGORITHMS:
    # Initialize both agents for comparison
    try:
        from rl_mission_env import DQNAgent, QLearningAgent
        rl_agent_dqn = DQNAgent(state_dim=rl_env.state_dim, action_dim=rl_env.action_dim, alpha=0.001)
        rl_agent_qlearn = QLearningAgent(state_dim=rl_env.state_dim, action_dim=rl_env.action_dim)
        
        # Start with DQN as primary agent
        rl_agent = rl_agent_dqn
        rl_current_algorithm = "DQN"
        
        print(f"🤖 DUAL ALGORITHM MODE ENABLED:")
        print(f"   ✅ Deep Q-Network (DQN) agent initialized")
        print(f"   ✅ Tabular Q-Learning agent initialized")
        print(f"   🎯 Starting with: {rl_current_algorithm}")
        print(f"   🔄 Press 'k' to switch between algorithms during training")
        
    except Exception as e:
        print(f"⚠️  Error initializing dual agents ({e}), using single DQN")
        TRAIN_BOTH_ALGORITHMS = False
        from rl_mission_env import DQNAgent
        rl_agent = DQNAgent(state_dim=rl_env.state_dim, action_dim=rl_env.action_dim, alpha=0.001)
        rl_current_algorithm = "DQN"
        print(f"✅ Using Deep Q-Network (DQN) agent")

if not TRAIN_BOTH_ALGORITHMS:
    # Single algorithm mode (original behavior)
    USE_DQN = True  # Set to False to use tabular Q-Learning instead
    
    if USE_DQN:
        try:
            from rl_mission_env import DQNAgent
            rl_agent = DQNAgent(state_dim=rl_env.state_dim, action_dim=rl_env.action_dim, alpha=0.001)
            rl_current_algorithm = "DQN"
            print(f"✅ Using Deep Q-Network (DQN) agent")
        except Exception as e:
            print(f"⚠️  DQN not available ({e}), falling back to Q-Learning")
            from rl_mission_env import QLearningAgent
            rl_agent = QLearningAgent(state_dim=rl_env.state_dim, action_dim=rl_env.action_dim)
            rl_current_algorithm = "Q-Learning"
    else:
        from rl_mission_env import QLearningAgent
        rl_agent = QLearningAgent(state_dim=rl_env.state_dim, action_dim=rl_env.action_dim)
        rl_current_algorithm = "Q-Learning"
        print(f"✅ Using Tabular Q-Learning agent")

# === RL SCENARIOS AND METRICS ===
rl_scenarios = [
  'none',
  'random',
  'periodic',
  'continuous',
  'impulse'
]
rl_metrics = {scenario: {'success': 0, 'errors': [], 'steps': [], 'energy': [], 'episodes': 0} for scenario in rl_scenarios}

# Dual algorithm metrics tracking
if TRAIN_BOTH_ALGORITHMS:
    rl_algorithm_metrics = {
        'DQN': {scenario: {'success': 0, 'errors': [], 'steps': [], 'energy': [], 'episodes': 0} for scenario in rl_scenarios},
        'Q-Learning': {scenario: {'success': 0, 'errors': [], 'steps': [], 'energy': [], 'episodes': 0} for scenario in rl_scenarios}
    }
    rl_algorithm_comparison = {'DQN': {'total_reward': 0, 'training_time': 0, 'completed': False}, 'Q-Learning': {'total_reward': 0, 'training_time': 0, 'completed': False}}
    rl_sequential_training_status = {'first_algorithm_completed': False, 'both_completed': False}

# === RL TRAINING LOOP HOOK ===
rl_training_enabled = False  # Set to True to enable automatic training on startup
rl_training_mode = False  # Toggle during simulation with 't' key

# Training Configuration Options (uncomment one):
# rl_num_episodes = 100      # TESTING: ~10 min total (all scenarios) - For debugging only
rl_num_episodes = 500      # DEVELOPMENT: ~45 min total - Initial learning visible
# rl_num_episodes = 2000     # PRODUCTION: ~3 hours total - Good performance (recommended)
# rl_num_episodes = 5000     # HIGH-PERFORMANCE: ~8 hours total - Near-optimal performance

rl_max_steps = 200         # Max steps per episode before timeout
rl_episode_counter = 0
rl_step_counter = 0
rl_state = None
rl_current_scenario_idx = 0
rl_current_episode = 0

# Note: RL training disabled on startup to allow interactive simulation
# Press 't' during simulation to start RL training mode
print("\n=== RL Training Configuration ===")
if TRAIN_BOTH_ALGORITHMS:
    print(f"RL Algorithms: DQN + Q-Learning (Sequential Training)")
    print(f"Current Algorithm: {rl_current_algorithm} (starting algorithm)")
    print(f"Training Approach: Complete one algorithm, then switch to the other")
    print(f"Algorithm Switching: Press 'k' to switch (when not training)")
else:
    print(f"RL Algorithm: {rl_agent.agent_type}")
print(f"Training scenarios: {rl_scenarios}")
print(f"Episodes per scenario: {rl_num_episodes}")
if TRAIN_BOTH_ALGORITHMS:
    print(f"Episodes per algorithm: {rl_num_episodes * len(rl_scenarios)}")
    print(f"Total episodes (both algorithms): {rl_num_episodes * len(rl_scenarios) * 2}")
    print(f"Estimated time per algorithm: ~{(rl_num_episodes * len(rl_scenarios) * 0.5 / 60):.1f} minutes")
    print(f"Total estimated time (both): ~{(rl_num_episodes * len(rl_scenarios) * 2 * 0.5 / 60):.1f} minutes")
else:
    print(f"Total episodes (all scenarios): {rl_num_episodes * len(rl_scenarios)}")
    print(f"Estimated training time: ~{(rl_num_episodes * len(rl_scenarios) * 0.5 / 60):.1f} minutes")
print(f"Max steps per episode: {rl_max_steps}")

if TRAIN_BOTH_ALGORITHMS:
    print(f"\n📋 Sequential Training Workflow:")
    print(f"  1. Train {rl_current_algorithm} completely (press 't' to start)")
    print(f"  2. After completion, switch algorithm (press 'k')")
    print(f"  3. Train the second algorithm completely")
    print(f"  4. Compare performance results")
    print(f"  5. Use 'd' key to check training status anytime")
print("\nAlgorithm Comparison:")
print("  📊 Tabular Q-Learning:")
print("     • Simple, interpretable, fast updates")
print("     • Works well for discrete states")
print("     • Limited scalability to high dimensions")
print("  🧠 Deep Q-Network (DQN):")
print("     • Powerful function approximation with neural nets")
print("     • Handles high-dimensional continuous states")
print("     • Requires more data, slower to train")
print("     • Better generalization across states")
print("\nTraining Recommendations:")
print("  • 100 episodes  = Quick test (not enough for learning)")
print("  • 500 episodes  = Development (initial learning)")
print("  • 2000 episodes = Production (recommended for good performance)")
print("  • 5000 episodes = High-performance (near-optimal)")
print("\nPress 't' during simulation to toggle RL training mode")
print("====================================\n")

baseorn = p.getQuaternionFromEuler([3.1415, 0, 0.3])
baseorn = [0, 0, 0, 1]
#[0, 0, 0.707, 0.707]

#p.resetBasePositionAndOrientation(kukaId,[0,0,0],baseorn)#[0,0,0,1])
kukaEndEffectorIndex = 6
numJoints = p.getNumJoints(kukaId)
if (numJoints != 7):
  exit()

#lower limits for null space
ll = [-.967, -2, -2.96, 0.19, -2.96, -2.09, -3.05]
#upper limits for null space
ul = [.967, 2, 2.96, 2.29, 2.96, 2.09, 3.05]
#joint ranges for null space
jr = [5.8, 4, 5.8, 4, 5.8, 4, 6]
#restposes for null space
rp = [0, 0, 0, 0.5 * math.pi, 0, -math.pi * 0.5 * 0.66, 0]
#joint damping coefficents
jd = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]

for i in range(numJoints):
  p.resetJointState(kukaId, i, rp[i])

p.setGravity(0, 0, -9.81)  # Realistic Earth gravity (was -10, causing excessive downward force)
t = 0.
prevPose = [0, 0, 0]
prevPose1 = [0, 0, 0]
hasPrevPose = 0
useNullSpace = 0

useOrientation = 0
#If we set useSimulation=0, it sets the arm pose to be the IK result directly without using dynamic control.
#This can be used to test the IK result accuracy.
useSimulation = 1
useRealTimeSimulation = 1
p.setRealTimeSimulation(useRealTimeSimulation)
#trailDuration is duration (in seconds) after debug lines will be removed automatically
#use 0 for no-removal
trailDuration = 15
basepos = [0, 0, 0]
ang = 0
ang = 0


def accurateCalculateInverseKinematics(kukaId, endEffectorId, targetPos, threshold, maxIter):
    closeEnough = False
    iter = 0
    dist2 = 1e30
    while (not closeEnough and iter < maxIter):
        jointPoses = p.calculateInverseKinematics(kukaId, endEffectorId, targetPos)
        for i in range(numJoints):
            p.resetJointState(kukaId, i, jointPoses[i])
        ls = p.getLinkState(kukaId, endEffectorId)
        newPos = ls[4]
        diff = [targetPos[0] - newPos[0], targetPos[1] - newPos[1], targetPos[2] - newPos[2]]
        dist2 = (diff[0] * diff[0] + diff[1] * diff[1] + diff[2] * diff[2])
        closeEnough = (dist2 < threshold)
        iter = iter + 1
    #print ("Num iter: "+str(iter) + "threshold: "+str(dist2))
    return jointPoses


wheels = [2, 3, 4, 5]
#(2, b'front_left_wheel', 0, 7, 6, 1, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, b'front_left_wheel_link')
#(3, b'front_right_wheel', 0, 8, 7, 1, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, b'front_right_wheel_link')
#(4, b'rear_left_wheel', 0, 9, 8, 1, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, b'rear_left_wheel_link')
#(5, b'rear_right_wheel', 0, 10, 9, 1, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, b'rear_right_wheel_link')
wheelVelocities = [0, 0, 0, 0]
wheelDeltasTurn = [1, -1, 1, -1]
wheelDeltasFwd = [1, 1, 1, 1]

# === CURRENT PATH: CIRCULAR ===
# Circular path autonomous movement parameters
autonomous_mode = True            # Enable autonomous circular path movement
circle_radius = 0.4               # Radius of circular path (0.4 meters)
circle_center = [0, 0]            # Center of circle
path_phase = 0                    # Current phase angle (0 to 2*pi)
phase_increment = 0.02            # How fast to move along circle
path_completed_laps = 0           # Number of completed circular laps
autonomous_speed = 0.8            # Speed for autonomous movement
use_waypoints = False             # Set to False for smooth circular motion, True for waypoint-based

# Optional: Waypoints around circle (for waypoint-based circular navigation)
num_waypoints = 8                 # Number of waypoints around circle
circle_waypoints = []             # Will be generated
current_waypoint = 0              # Current target waypoint
waypoint_tolerance = 0.15         # Distance tolerance to reach waypoint (meters)

# === ALTERNATIVE PATH: SQUARE (COMMENTED OUT) ===
# To switch back to square path, uncomment below and comment out circular settings above
# Square path autonomous movement parameters
# autonomous_mode = True            # Enable autonomous square path movement
# square_size = 0.8                 # Size of square path (0.8x0.8 meters)
# square_waypoints = [              # Four corners of the square
#     [-square_size/2, -square_size/2],  # Point 1: Bottom-left (-0.4, -0.4)
#     [square_size/2, -square_size/2],   # Point 2: Bottom-right (0.4, -0.4)
#     [square_size/2, square_size/2],    # Point 3: Top-right (0.4, 0.4)
#     [-square_size/2, square_size/2]    # Point 4: Top-left (-0.4, 0.4)
# ]
# current_waypoint = 0              # Current target waypoint (0-3)
# waypoint_tolerance = 0.2          # Distance tolerance to reach waypoint (meters)
# square_center = [0, 0]            # Center of square
# path_completed_laps = 0           # Number of completed square laps
# autonomous_speed = 0.8            # Speed for autonomous movement

print("===================================\n")

# === ALTERNATIVE: SQUARE PATH MARKERS (COMMENTED OUT) ===
# def add_square_path_markers():
#     """Add visual markers for square path waypoints and connections."""
#     # Add waypoint markers (small red spheres)
#     for i, waypoint in enumerate(square_waypoints):
#         world_x = waypoint[0] + square_center[0]
#         world_y = waypoint[1] + square_center[1]
#         world_z = 0.1  # Slightly above ground
#         
#         marker_id = p.createVisualShape(p.GEOM_SPHERE, radius=0.05, rgbaColor=[1, 0, 0, 0.8])
#         p.createMultiBody(baseMass=0, baseVisualShapeIndex=marker_id,
#                          basePosition=[world_x, world_y, world_z])
#         
#         # Add waypoint label
#         p.addUserDebugText(f"WP{i+1}", [world_x, world_y, world_z + 0.1], 
#                           textColorRGB=[1, 1, 1], textSize=1.0)
#     
#     # Add lines connecting waypoints (path segments)
#     for i in range(4):
#         start_wp = square_waypoints[i]
#         end_wp = square_waypoints[(i + 1) % 4]  # Next waypoint (wrapping around)
#         
#         start_pos = [start_wp[0] + square_center[0], start_wp[1] + square_center[1], 0.05]
#         end_pos = [end_wp[0] + square_center[0], end_wp[1] + square_center[1], 0.05]
#         
#         # Add debug line (blue color)
#         p.addUserDebugLine(start_pos, end_pos, lineColorRGB=[0, 0, 1], lineWidth=3.0)

# Generate waypoints around the circle
for i in range(num_waypoints):
    angle = (2 * math.pi * i) / num_waypoints
    x = circle_center[0] + circle_radius * math.cos(angle)
    y = circle_center[1] + circle_radius * math.sin(angle)
    circle_waypoints.append([x, y])

def add_circular_path_markers():
    """Add visual markers for circular path waypoints and connections."""
    if use_waypoints:
        # Add waypoint markers (small red spheres)
        for i, waypoint in enumerate(circle_waypoints):
            world_x = waypoint[0]
            world_y = waypoint[1]
            world_z = 0.1  # Slightly above ground
            
            marker_id = p.createVisualShape(p.GEOM_SPHERE, radius=0.05, rgbaColor=[1, 0, 0, 0.8])
            p.createMultiBody(baseMass=0, baseVisualShapeIndex=marker_id,
                             basePosition=[world_x, world_y, world_z])
            
            # Add waypoint label
            p.addUserDebugText(f"WP{i+1}", [world_x, world_y, world_z + 0.1], 
                              textColorRGB=[1, 1, 1], textSize=1.0)
        
        # Add lines connecting waypoints (path segments)
        for i in range(num_waypoints):
            start_wp = circle_waypoints[i]
            end_wp = circle_waypoints[(i + 1) % num_waypoints]  # Next waypoint (wrapping around)
            
            start_pos = [start_wp[0], start_wp[1], 0.05]
            end_pos = [end_wp[0], end_wp[1], 0.05]
            
            # Add debug line (blue color)
            p.addUserDebugLine(start_pos, end_pos, lineColorRGB=[0, 0, 1], lineWidth=3.0)
    else:
        # For smooth circular motion, draw a complete circle
        num_segments = 32
        for i in range(num_segments):
            angle1 = (2 * math.pi * i) / num_segments
            angle2 = (2 * math.pi * (i + 1)) / num_segments
            
            x1 = circle_center[0] + circle_radius * math.cos(angle1)
            y1 = circle_center[1] + circle_radius * math.sin(angle1)
            x2 = circle_center[0] + circle_radius * math.cos(angle2)
            y2 = circle_center[1] + circle_radius * math.sin(angle2)
            
            # Add debug line (blue color)
            p.addUserDebugLine([x1, y1, 0.05], [x2, y2, 0.05], lineColorRGB=[0, 0, 1], lineWidth=3.0)
    
    # Add center marker (green sphere)
    center_x = circle_center[0]
    center_y = circle_center[1]
    center_z = 0.05
    
    center_marker_id = p.createVisualShape(p.GEOM_SPHERE, radius=0.03, rgbaColor=[0, 1, 0, 0.8])
    p.createMultiBody(baseMass=0, baseVisualShapeIndex=center_marker_id,
                     basePosition=[center_x, center_y, center_z])
    
    p.addUserDebugText("CENTER", [center_x, center_y, center_z + 0.08], 
                      textColorRGB=[0, 1, 0], textSize=0.8)
    
    # Print path information
    print("\n=== Circular Path Configuration ===")
    print(f"Circular path: radius={circle_radius}m, center=({center_x:.2f}, {center_y:.2f})")
    if use_waypoints:
        print(f"Waypoint-based navigation: {len(circle_waypoints)} waypoints")
        for i, wp in enumerate(circle_waypoints[:4]):  # Show first 4 waypoints
            print(f"WP{i+1}: ({wp[0]:.2f}, {wp[1]:.2f})")
        if len(circle_waypoints) > 4:
            print(f"... and {len(circle_waypoints) - 4} more waypoints")
    else:
        print("Smooth circular motion: continuous path following")
    print("===================================\n")

# Add visual path markers (circular path and connections)
add_circular_path_markers()

# === ALTERNATIVE: SQUARE PATH MARKERS ===
# To switch to square path, comment out the line above and uncomment the line below
# add_square_path_markers()

print("=== Circular Path Autonomous Navigation with Virtual IMU ===")
print("Husky will follow a smooth circular path with IMU-enhanced control")
print("Manipulator trajectory will be centered in the circular path")
print("Virtual IMU sensors monitor base and arm motion with realistic noise")
print("")
print("CONTROLS:")
print("  'm' - Toggle autonomous mode on/off")
print("  'r' - Reset to start position") 
print("  'i' - Display immediate IMU readings")
print("  'p' - Apply manual perturbation (test IMU response)")
print("  'v' - Start/stop video recording (30s max)")
print("  'c' - Change camera angle (when not recording)")
print("  'x' - Quick test recording (10 seconds)")
print("  DISTURBANCE SCENARIOS:")
print("    '1' - NONE scenario (no disturbances)")
print("    '2' - RANDOM scenario (continuous noise ±50N)")
print("    '3' - PERIODIC scenario (impacts every 50 steps ±100N)")
print("    '4' - CONTINUOUS scenario (persistent bias ±10N)")
print("    '5' - IMPULSE scenario (single shock ±200N)")
print("    'd' - Display current disturbance status")
print("  DISTURBANCE DIRECTIONS:")
print("    'N/F/G/U/J' - Direction modes (raNdom/Forward/lateral/Up/Jerk)")
print("  DISTURBANCE INTENSITY:")
print("    'O' - nOrmal intensity (1.0x forces)")
print("    'W' - poWerful intensity (φ = 1.61803x forces - Golden ratio)")

if RL_AVAILABLE:
    print("  RL TRAJECTORY PLANNER:")
    print("    't' - Toggle RL training mode (Q-learning/DQN)")
    print("    'e' - Toggle RL execution mode (run learned policy)")
    print("    'l' - Load saved RL model")
    print("    'q' - Test disturbance rejection capability")
    if TRAIN_BOTH_ALGORITHMS:
        print("    'k' - Switch between DQN and Q-Learning algorithms")

print("  Arrow keys - Manual control (when autonomous off)")
print("")
print("FEATURES:")
print("  📹 VIDEO RECORDING - Records simulation as MP4 video")
print("  📊 IMU SENSORS - Accelerometer with realistic noise and bias")
print("  🎮 IMU CONTROL - Gyroscope with drift simulation") 
print("  🎯 AUTO STABILITY - Disturbance rejection using IMU feedback")
print("  �️  DISTURBANCE SIM - 5 systematic disturbance scenarios for testing")

if RL_AVAILABLE:
    print("  🤖 RL TRAJECTORY PLANNER:")
    if TRAIN_BOTH_ALGORITHMS:
        print("    • DUAL ALGORITHM MODE: DQN + Tabular Q-Learning")
        print("    • Press 'k' to switch algorithms during training")
        print("    • Automatic performance comparison and metrics")
    else:
        print("    • Q-learning & Deep Q-Networks (DQN) for adaptive control")
    print("    • End-effector trajectory following with disturbance rejection")
    print("    • Inverse kinematics integration with Jacobian control")
    print("    • Real-time performance metrics and learning visualization")

print("=============================================================")

while 1:
  # === IMU SENSOR UPDATES ===
  # Read IMU data from both sensors every frame for real-time feedback
  husky_imu_data = husky_imu.read_imu()
  kuka_imu_data = kuka_imu.read_imu()
  
  # Increment frame counter for periodic logging
  imu_frame_counter += 1
  physics_diagnostics_counter += 1
  
  # Log IMU data periodically (every 1 second)
  if imu_frame_counter % imu_log_interval == 0:
    print(f"\n=== IMU DATA UPDATE (Frame {imu_frame_counter}) ===")
    print("HUSKY BASE IMU:")
    husky_imu.print_imu_status(husky_imu_data)
    print("\nKUKA ARM IMU (Link 6):")
    kuka_imu.print_imu_status(kuka_imu_data)
    print("=" * 50)
  
  # Enhanced physics diagnostics (every 5 seconds)
  if physics_diagnostics_counter % physics_diagnostics_interval == 0:
    stability = print_physics_diagnostics()
    if not stability:
      print("🚨 PHYSICS INSTABILITY DETECTED!")
      print("   EMERGENCY ACTION: Reducing constraint force to prevent jumping")
      # Emergency constraint force reduction
      try:
        p.changeConstraint(cid, maxForce=1000)  # Emergency reduction
        print("   ✅ Constraint force reduced to 1,000N (emergency mode)")
      except:
        print("   ❌ Failed to apply emergency constraint reduction")
  
  keys = p.getKeyboardEvents()
  shift = 0.01
  wheelVelocities = [0, 0, 0, 0]
  speed = 1.0
  for k in keys:
    if ord('s') in keys:
      p.saveWorld("state.py")
    if ord('a') in keys:
      basepos = basepos = [basepos[0], basepos[1] - shift, basepos[2]]
    if ord('d') in keys:
      basepos = basepos = [basepos[0], basepos[1] + shift, basepos[2]]
    if ord('m') in keys:
      autonomous_mode = not autonomous_mode
      print(f"Autonomous square path mode: {'ENABLED' if autonomous_mode else 'DISABLED'}")
    if ord('r') in keys:
      current_waypoint = 0
      path_completed_laps = 0
      print("Reset to waypoint 1")
    if ord('x') in keys:
      # Test recording - auto start a 10 second recording
      if not video_recorder.is_recording:
        video_recorder.duration = 10  # Short test recording
        video_recorder.max_frames = video_recorder.fps * 10
        video_recorder.start_recording("test_recording")
        print("🧪 Test recording started (10 seconds) - Press 'x' key was used")
    if ord('i') in keys:
      # Toggle IMU detailed logging
      print("\n=== IMMEDIATE IMU READING ===")
      print("HUSKY BASE IMU:")
      husky_imu.print_imu_status()
      print("KUKA ARM IMU:")
      kuka_imu.print_imu_status()
      print("=" * 30)
    if ord('p') in keys:
      # Apply random perturbation to test IMU response
      perturbation_force = [
          random.uniform(-50, 50),
          random.uniform(-50, 50), 
          0
      ]
      perturbation_torque = [0, 0, random.uniform(-10, 10)]
      p.applyExternalForce(husky, -1, perturbation_force, [0, 0, 0], p.WORLD_FRAME)
      p.applyExternalTorque(husky, -1, perturbation_torque, p.WORLD_FRAME)
      print(f"Applied perturbation: Force={perturbation_force}, Torque={perturbation_torque}")
    if ord('v') in keys:
      # Toggle video recording
      print("📝 'v' key detected!")  # Debug: confirm key press
      if video_recorder.is_recording:
        video_recorder.stop_recording()
      else:
        video_recorder.start_recording()
    if ord('c') in keys:
      # Change camera angle for recording
      if not video_recorder.is_recording:
        # Cycle through different camera angles
        angles = [
          (3.5, 45, -25),   # Default view
          (5.0, 90, -35),   # Side view  
          (2.5, 0, -15),    # Front view
          (6.0, 135, -40),  # Diagonal back view
          (4.0, 180, -30)   # Back view
        ]
        # Get next angle (cycling)
        if not hasattr(video_recorder, '_angle_index'):
          video_recorder._angle_index = 0
        video_recorder._angle_index = (video_recorder._angle_index + 1) % len(angles)
        distance, yaw, pitch = angles[video_recorder._angle_index]
        video_recorder.set_camera_angle(distance, yaw, pitch)
      else:
        print("📷 Cannot change camera angle while recording")
    if ord('t') in keys and RL_AVAILABLE:
      # Toggle RL training mode
      rl_training_mode = not rl_training_mode
      if rl_training_mode:
        rl_execution_mode = False
        autonomous_mode = False  # Disable regular autonomous mode
        print("🎓 RL TRAINING MODE ENABLED - Agent will learn trajectory following")
        print("   Press 't' again to stop training")
      else:
        print("🎓 RL TRAINING MODE DISABLED")
    if ord('e') in keys and RL_AVAILABLE:
      # Toggle RL execution mode
      rl_execution_mode = not rl_execution_mode
      if rl_execution_mode:
        rl_training_mode = False
        autonomous_mode = False  # Disable regular autonomous mode
        print("🚀 RL EXECUTION MODE ENABLED - Agent will execute learned policy")
        print("   Press 'e' again to stop execution")
      else:
        print("🚀 RL EXECUTION MODE DISABLED")
    if ord('l') in keys and RL_AVAILABLE:
      # Load RL model
      try:
        rl_planner.load_model("husky_kuka_trajectory_planner")
        print("📁 RL model loaded successfully")
      except Exception as e:
        print(f"❌ Failed to load RL model: {e}")
    if ord('q') in keys and RL_AVAILABLE:
      # Test disturbance rejection
      if not rl_training_mode and not rl_execution_mode:
        print("🧪 Starting disturbance rejection test...")
        try:
          metrics = rl_planner.test_disturbance_rejection(num_tests=5)
          print("✅ Disturbance rejection test completed")
        except Exception as e:
          print(f"❌ Disturbance test failed: {e}")
      else:
        print("⚠️  Cannot run tests while training/execution active")
    if ord('k') in keys and RL_AVAILABLE and TRAIN_BOTH_ALGORITHMS:
      # Switch between DQN and Q-Learning algorithms (preferably when not training)
      if rl_training_mode:
        print("⚠️  Algorithm switching disabled during active training")
        print("   Stop training (press 't') before switching algorithms")
      else:
        if rl_current_algorithm == "DQN":
          rl_agent = rl_agent_qlearn
          rl_current_algorithm = "Q-Learning"
          print("🔄 ALGORITHM SWITCHED: DQN → Q-Learning")
          print("   ✅ Ready for sequential training of Q-Learning agent")
          print("   • Simple lookup table approach")
          print("   • Fast updates, interpretable")
          print("   • Best for discrete state spaces")
          print("   🎯 Press 't' to start Q-Learning training")
        else:
          rl_agent = rl_agent_dqn
          rl_current_algorithm = "DQN"
          print("🔄 ALGORITHM SWITCHED: Q-Learning → DQN")
          print("   ✅ Ready for sequential training of DQN agent")
          print("   • Neural network function approximation")
          print("   • Handles continuous states")
          print("   • Better generalization capability")
          print("   🎯 Press 't' to start DQN training")
    
    # === DISTURBANCE SCENARIO CONTROLS ===
    if ord('1') in keys:
      # Switch to NONE scenario
      disturbance_manager.set_scenario("none")
    if ord('2') in keys:
      # Switch to RANDOM scenario
      disturbance_manager.set_scenario("random")
    if ord('3') in keys:
      # Switch to PERIODIC scenario
      disturbance_manager.set_scenario("periodic")
    if ord('4') in keys:
      # Switch to CONTINUOUS scenario
      disturbance_manager.set_scenario("continuous")
    if ord('5') in keys:
      # Switch to IMPULSE scenario
      disturbance_manager.set_scenario("impulse")
    
    # === DIRECTIONAL MODE CONTROLS ===
    if ord('n') in keys:
      # Switch to RANDOM directional mode (N for raNdom)
      disturbance_manager.set_directional_mode("random")
    if ord('f') in keys:
      # Switch to FORWARD directional mode
      disturbance_manager.set_directional_mode("forward")
    if ord('g') in keys:
      # Switch to LATERAL directional mode (G for lateral movement)
      disturbance_manager.set_directional_mode("lateral")
    if ord('u') in keys:
      # Switch to VERTICAL directional mode (U for Up)
      disturbance_manager.set_directional_mode("vertical")
    if ord('j') in keys:
      # Switch to JERK directional mode
      disturbance_manager.set_directional_mode("jerk")
    
    # === INTENSITY MODE CONTROLS ===
    if ord('o') in keys:
      # Switch to NORMAL intensity mode (O for nOrmal)
      disturbance_manager.set_intensity_mode("normal")
    if ord('w') in keys:
      # Switch to GOLDEN intensity mode (W for poWerful/φ)  
      disturbance_manager.set_intensity_mode("golden")
    
    if ord('d') in keys:
      # Display current disturbance status and algorithm status
      status = disturbance_manager.get_status()
      print(f"\n🌪️  DISTURBANCE STATUS:")
      print(f"   Current Scenario: {status['current_scenario'].upper()}")
      print(f"   Directional Mode: {status['directional_mode'].upper()}")
      print(f"   Intensity Mode: {status['intensity_mode'].upper()} ({status['intensity_factor']}x)")
      print(f"   Description: {status['description']}")
      print(f"   Step Counter: {status['step_counter']}")
      if status['current_scenario'] == 'impulse':
        impulse_status = "APPLIED" if status['impulse_applied'] else "PENDING"
        print(f"   Impulse Status: {impulse_status}")
      print(f"   Scenario Controls: Press 1-5 to switch scenarios")
      print(f"   Direction Controls: Press N/F/G/U/J for directional modes")
      print(f"     N=raNdom, F=Forward, G=lateral, U=Up/vertical, J=Jerk")
      print(f"   Intensity Controls: Press O/W for intensity modes")
      print(f"     O=nOrmal (1.0x), W=poWerful/Golden (φ = {disturbance_manager.golden_ratio}x)")
      
      # Display RL algorithm status if dual mode enabled
      if RL_AVAILABLE and TRAIN_BOTH_ALGORITHMS:
        print(f"\n🤖 RL ALGORITHM STATUS:")
        print(f"   Current Algorithm: {rl_current_algorithm}")
        print(f"   Training Mode: {'ACTIVE' if rl_training_mode else 'INACTIVE'}")
        dqn_status = "✅ COMPLETED" if rl_algorithm_comparison['DQN']['completed'] else "⏳ PENDING"
        qlearn_status = "✅ COMPLETED" if rl_algorithm_comparison['Q-Learning']['completed'] else "⏳ PENDING"
        print(f"   DQN Training: {dqn_status}")
        print(f"   Q-Learning Training: {qlearn_status}")
        print(f"   Algorithm Controls: Press 'k' to switch algorithms (when not training)")
        if not rl_algorithm_comparison['DQN']['completed'] and not rl_algorithm_comparison['Q-Learning']['completed']:
          print(f"   💡 Recommendation: Complete {rl_current_algorithm} training first, then switch")
        elif rl_algorithm_comparison['DQN']['completed'] and not rl_algorithm_comparison['Q-Learning']['completed']:
          print(f"   💡 Next: Switch to Q-Learning (press 'k') and train")
        elif not rl_algorithm_comparison['DQN']['completed'] and rl_algorithm_comparison['Q-Learning']['completed']:
          print(f"   💡 Next: Switch to DQN (press 'k') and train")
        else:
          print(f"   🎉 Both algorithms completed! Compare results with analysis tools.")

    # Manual control (only when autonomous mode is disabled)
    if not autonomous_mode:
      if p.B3G_LEFT_ARROW in keys:
        for i in range(len(wheels)):
          wheelVelocities[i] = wheelVelocities[i] - speed * wheelDeltasTurn[i]
      if p.B3G_RIGHT_ARROW in keys:
        for i in range(len(wheels)):
          wheelVelocities[i] = wheelVelocities[i] + speed * wheelDeltasTurn[i]
      if p.B3G_UP_ARROW in keys:
        for i in range(len(wheels)):
          wheelVelocities[i] = wheelVelocities[i] + speed * wheelDeltasFwd[i]
      if p.B3G_DOWN_ARROW in keys:
        for i in range(len(wheels)):
          wheelVelocities[i] = wheelVelocities[i] - speed * wheelDeltasFwd[i]

  # === RL TRAINING IN MAIN LOOP ===
  # Run RL training step-by-step within the simulation
  if rl_training_mode and rl_current_scenario_idx < len(rl_scenarios):
    scenario = rl_scenarios[rl_current_scenario_idx]
    
    # Initialize episode if needed
    if rl_step_counter == 0:
      rl_state = rl_env.reset()
      rl_env.current_disturbance = scenario
      print(f"\n[RL][{scenario}] Starting Episode {rl_current_episode + 1}/{rl_num_episodes}")
    
    # Execute one RL step per simulation frame
    rl_action = rl_agent.select_action(rl_state)
    rl_next_state, rl_reward, rl_done = rl_env.step(rl_action)
    rl_agent.update(rl_state, rl_action, rl_reward, rl_next_state)
    rl_state = rl_next_state
    rl_step_counter += 1
    
    # Track energy
    ep_energy = rl_metrics[scenario].get('current_energy', 0)
    if rl_action >= rl_env.p.getNumJoints(rl_env.kuka):
      ep_energy += 1.0
    rl_metrics[scenario]['current_energy'] = ep_energy
    
    # Check episode completion
    if rl_done or rl_step_counter >= rl_max_steps:
      final_error = np.linalg.norm(rl_state[-4:-1] - rl_env.goal_pose[:3])
      
      if rl_done:
        rl_metrics[scenario]['success'] += 1
        print(f"[RL][{scenario}] Episode {rl_current_episode + 1} SUCCESS: steps={rl_step_counter}, error={final_error:.3f}, energy={ep_energy}")
      else:
        print(f"[RL][{scenario}] Episode {rl_current_episode + 1} TIMEOUT: steps={rl_step_counter}, error={final_error:.3f}, energy={ep_energy}")
      
      rl_metrics[scenario]['errors'].append(final_error)
      rl_metrics[scenario]['steps'].append(rl_step_counter)
      rl_metrics[scenario]['energy'].append(ep_energy)
      rl_metrics[scenario]['episodes'] += 1
      
      # Reset for next episode
      rl_step_counter = 0
      rl_current_episode += 1
      rl_metrics[scenario]['current_energy'] = 0
      
      # Save checkpoint every 100 episodes
      if rl_current_episode % 100 == 0 and rl_current_episode > 0:
        try:
          rl_agent.save(f'rl_checkpoint_{scenario}_ep{rl_current_episode}')
          print(f"💾 Checkpoint saved: {scenario} episode {rl_current_episode}")
        except Exception as e:
          print(f"⚠️  Failed to save checkpoint: {e}")
      
      # Check if scenario is complete
      if rl_current_episode >= rl_num_episodes:
        print(f"\n=== Scenario '{scenario}' Complete ===")
        m = rl_metrics[scenario]
        success_rate = 100.0 * m['success'] / m['episodes']
        avg_error = np.mean(m['errors'])
        avg_steps = np.mean(m['steps'])
        avg_energy = np.mean(m['energy'])
        print(f"Success Rate: {success_rate:5.1f}% | Avg Error: {avg_error:6.3f} | Avg Steps: {avg_steps:5.1f} | Avg Energy: {avg_energy:5.1f}\n")
        
        # Save final model for this scenario
        try:
          rl_agent.save(f'rl_final_{scenario}')
          print(f"💾 Final model saved for scenario '{scenario}'")
        except Exception as e:
          print(f"⚠️  Failed to save final model: {e}")
        
        # Move to next scenario
        rl_current_scenario_idx += 1
        rl_current_episode = 0
        
        # Check if all scenarios complete
        if rl_current_scenario_idx >= len(rl_scenarios):
          print("\n=== RL Training Complete - All Scenarios ===")
          for s in rl_scenarios:
            m = rl_metrics[s]
            success_rate = 100.0 * m['success'] / m['episodes']
            avg_error = np.mean(m['errors'])
            avg_steps = np.mean(m['steps'])
            avg_energy = np.mean(m['energy'])
            print(f"{s:10s} | Success: {success_rate:5.1f}% | Error: {avg_error:6.3f} | Steps: {avg_steps:5.1f} | Energy: {avg_energy:5.1f}")
          
          # Save metrics
          with open('rl_metrics.json', 'w') as f:
            json.dump(rl_metrics, f, indent=2)
          print('\n💾 RL metrics saved to rl_metrics.json')
          
          # Disable training mode
          rl_training_mode = False
          print("🎓 RL Training Mode AUTO-DISABLED (all scenarios complete)\n")
  
  # === RL TRAJECTORY PLANNER CONTROL (if available) ===
  if RL_AVAILABLE and rl_planner is not None:
    if rl_execution_mode:
      # RL Execution Mode - Execute learned policy
      try:
        if not hasattr(rl_planner, '_execution_state'):
          rl_planner._execution_state = rl_planner.env.reset()
          rl_planner._execution_step = 0
          print("🚀 Starting RL trajectory execution")
        
        # Execute one step
        action = rl_planner.agent.choose_action(rl_planner._execution_state)
        next_state, reward, done, info = rl_planner.env.step(action)
        
        rl_planner._execution_state = next_state
        rl_planner._execution_step += 1
        
        # Display progress every 60 steps
        if rl_planner._execution_step % 60 == 0:
          print(f"🤖 RL Execution - Step: {rl_planner._execution_step}, "
                f"Error: {info.get('ee_error', 0):.4f}m, "
                f"Progress: {info.get('trajectory_progress', 0):.1%}")
        
        # Execution completed
        if done:
          print("✅ RL trajectory execution completed")
          metrics, execution_data = rl_planner.execute_trajectory()
          print(f"📊 Final metrics: Error={metrics['mean_error']:.4f}m, "
                f"Completion={metrics['completion_rate']:.1%}")
          
          # Reset execution state
          delattr(rl_planner, '_execution_state')
          
      except Exception as e:
        print(f"❌ RL Execution error: {e}")
        rl_execution_mode = False
  
  # Autonomous circular path navigation
  if autonomous_mode and not rl_training_mode and not rl_execution_mode:
    robot_pos, robot_orn = p.getBasePositionAndOrientation(husky)
    
    if use_waypoints:
        # Waypoint-based circular navigation
        target_x = circle_waypoints[current_waypoint][0]
        target_y = circle_waypoints[current_waypoint][1]
        
        # Calculate distance to target
        dx = target_x - robot_pos[0]
        dy = target_y - robot_pos[1]
        distance_to_target = math.sqrt(dx*dx + dy*dy)
        
        # Check if we reached the current waypoint
        if distance_to_target < waypoint_tolerance:
            current_waypoint = (current_waypoint + 1) % num_waypoints
            if current_waypoint == 0:  # Completed full lap
                path_completed_laps += 1
                print(f"Circular lap {path_completed_laps} completed! Moving to waypoint 1")
            else:
                print(f"Reached waypoint {current_waypoint + 1}")
    else:
        # Smooth circular motion
        path_phase += phase_increment
        if path_phase >= 2 * math.pi:
            path_phase -= 2 * math.pi
            path_completed_laps += 1
            print(f"Circular lap {path_completed_laps} completed!")
        
        # Calculate target position on circle
        target_x = circle_center[0] + circle_radius * math.cos(path_phase)
        target_y = circle_center[1] + circle_radius * math.sin(path_phase)
        
        dx = target_x - robot_pos[0]
        dy = target_y - robot_pos[1]
        distance_to_target = math.sqrt(dx*dx + dy*dy)
    
    # Calculate angle to target
    angle_to_target = math.atan2(dy, dx)
    
    # Get current robot orientation
    current_euler = p.getEulerFromQuaternion(robot_orn)
    current_yaw = current_euler[2]
    
    # Calculate angle difference (wrapped to [-pi, pi])
    angle_diff = angle_to_target - current_yaw
    while angle_diff > math.pi:
      angle_diff -= 2 * math.pi
    while angle_diff < -math.pi:
      angle_diff += 2 * math.pi
    
    # === IMU-ENHANCED NAVIGATION CONTROL ===
    # Use IMU data for improved control stability and disturbance rejection
    husky_accel = husky_imu_data['accel']
    husky_gyro = husky_imu_data['gyro']
    
    # Detect excessive acceleration (disturbances) and adjust control
    accel_magnitude = np.linalg.norm(husky_accel)
    gyro_magnitude = np.linalg.norm(husky_gyro)
    
    # Stability thresholds (accounting for gravity ~9.81 m/s²)
    max_stable_accel = 5.0   # m/s² - above gravity indicates disturbance  
    max_stable_gyro = 0.5     # rad/s - above this indicates spinning
    
    # Adjust control gains based on IMU feedback
    if accel_magnitude > max_stable_accel:
        # Robot is experiencing disturbance - reduce gains for stability
        stability_factor = 0.5
        print(f"IMU: High acceleration detected ({accel_magnitude:.2f} m/s²) - Reducing control gains")
    elif gyro_magnitude > max_stable_gyro:
        # Robot is spinning too fast - reduce turn rate
        stability_factor = 0.3
        print(f"IMU: High rotation detected ({gyro_magnitude:.3f} rad/s) - Reducing turn rate")
    else:
        # Normal operation
        stability_factor = 1.0
    
    # Simple proportional controller for navigation with IMU feedback
    angle_threshold = 0.2  # ~11 degrees

# === ALTERNATIVE: SQUARE PATH NAVIGATION (COMMENTED OUT) ===
# To switch back to square navigation, comment out the circular section above and uncomment below:
#   # Autonomous square path navigation
#   if autonomous_mode:
#     robot_pos, robot_orn = p.getBasePositionAndOrientation(husky)
#     
#     # Get current target waypoint
#     target_x = square_waypoints[current_waypoint][0] + square_center[0]
#     target_y = square_waypoints[current_waypoint][1] + square_center[1]
#     
#     # Calculate distance and angle to target
#     dx = target_x - robot_pos[0]
#     dy = target_y - robot_pos[1]
#     distance_to_target = math.sqrt(dx*dx + dy*dy)
#     angle_to_target = math.atan2(dy, dx)
#     
#     # Get current robot orientation
#     current_euler = p.getEulerFromQuaternion(robot_orn)
#     current_yaw = current_euler[2]
#     
#     # Calculate angle difference (wrapped to [-pi, pi])
#     angle_diff = angle_to_target - current_yaw
#     while angle_diff > math.pi:
#       angle_diff -= 2 * math.pi
#     while angle_diff < -math.pi:
#       angle_diff += 2 * math.pi
#     
#     # Check if we reached the current waypoint
#     if distance_to_target < waypoint_tolerance:
#       current_waypoint = (current_waypoint + 1) % 4
#       if current_waypoint == 0:  # Completed full lap
#         path_completed_laps += 1
#         print(f"Square lap {path_completed_laps} completed! Moving to waypoint 1")
#       else:
#         print(f"Reached waypoint {current_waypoint + 1}")
    
    if abs(angle_diff) > angle_threshold:
      # Turn towards target with IMU-based stability control
      turn_direction = 1 if angle_diff > 0 else -1
      adjusted_speed = autonomous_speed * stability_factor
      for i in range(len(wheels)):
        wheelVelocities[i] = turn_direction * adjusted_speed * wheelDeltasTurn[i]
    else:
      # Move forward with steering correction and IMU stability
      forward_speed = autonomous_speed * stability_factor
      turn_correction = angle_diff * 0.3 * stability_factor  # IMU-adjusted steering
      
      for i in range(len(wheels)):
        wheelVelocities[i] = forward_speed * wheelDeltasFwd[i] + turn_correction * wheelDeltasTurn[i]

  baseorn = p.getQuaternionFromEuler([0, 0, ang])
  for i in range(len(wheels)):
    # Enhanced wheel motor control with realistic parameters
    p.setJointMotorControl2(husky,
                            wheels[i],
                            p.VELOCITY_CONTROL,
                            targetVelocity=wheelVelocities[i],
                            force=500,              # Reduced force for more realistic motion
                            positionGain=0.1,       # Lower position gain
                            velocityGain=1.0,       # Higher velocity gain for speed control
                            maxVelocity=10.0)       # Max wheel velocity (rad/s)
  
  # Display status every 5 seconds
  if autonomous_mode and int(t * 60) % 300 == 0:  # Every 300 frames at 60fps = 5 seconds
    robot_pos, _ = p.getBasePositionAndOrientation(husky)
    
    if use_waypoints:
        target_x = circle_waypoints[current_waypoint][0]
        target_y = circle_waypoints[current_waypoint][1]
        distance_to_target = math.sqrt((target_x - robot_pos[0])**2 + (target_y - robot_pos[1])**2)
        print(f"CIRCULAR PATH - Lap: {path_completed_laps}, Target: WP{current_waypoint + 1}/{num_waypoints}, Distance: {distance_to_target:.2f}m")
    else:
        target_x = circle_center[0] + circle_radius * math.cos(path_phase)
        target_y = circle_center[1] + circle_radius * math.sin(path_phase)
        distance_to_target = math.sqrt((target_x - robot_pos[0])**2 + (target_y - robot_pos[1])**2)
        phase_degrees = (path_phase * 180 / math.pi) % 360
        print(f"CIRCULAR PATH - Lap: {path_completed_laps}, Phase: {phase_degrees:.1f}°, Distance: {distance_to_target:.2f}m")
        
        # Add IMU status to periodic display
        husky_accel_mag = np.linalg.norm(husky_imu_data['accel'])
        husky_gyro_mag = np.linalg.norm(husky_imu_data['gyro']) 
        print(f"HUSKY IMU - Accel: {husky_accel_mag:.2f} m/s², Gyro: {husky_gyro_mag:.3f} rad/s")
        print(f"VIDEO STATUS - {video_recorder.get_status()}")
  
  #p.resetBasePositionAndOrientation(kukaId,basepos,baseorn)#[0,0,0,1])
  if (useRealTimeSimulation):
    t = time.time()  #(dt, micro) = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
    #t = (dt.second/60.)*2.*math.pi
  else:
    t = t + 0.001

  if (useSimulation and useRealTimeSimulation == 0):
    p.stepSimulation()
  
  # === VIDEO RECORDING UPDATE ===
  # Update video recorder frame and camera tracking
  video_recorder.update_frame(robot_id=husky)
  
  # === SYSTEMATIC DISTURBANCE SCENARIOS ===
  # Apply current disturbance scenario using the disturbance manager
  if autonomous_mode:  # Only apply disturbances during autonomous operation
    disturbance_result = disturbance_manager.apply_current_scenario()
    
    # Log disturbance application when forces are actually applied
    if disturbance_result["applied"]:
      scenario = disturbance_manager.current_scenario.upper()
      force = disturbance_result["force"]
      torque = disturbance_result["torque"]
      step = disturbance_manager.step_counter
      intensity = disturbance_manager.intensity_mode.upper()
      factor = disturbance_manager.intensity_modes[disturbance_manager.intensity_mode]["factor"]
      
      # Show intensity in the force display
      intensity_indicator = f"⚡{intensity}" if factor > 1.0 else f"📊{intensity}"
      print(f"🌪️  {scenario} disturbance applied (step {step}) {intensity_indicator}: F=[{force[0]:.2f}, {force[1]:.2f}, {force[2]:.2f}], T=[{torque[0]:.2f}, {torque[1]:.2f}, {torque[2]:.2f}]")

  for i in range(1):
    # Manipulator trajectory centered on the circular path
    # Circular trajectory around the center of the circle
    trajectory_radius = 0.2  # Radius for manipulator trajectory (smaller than path circle)
    
    pos = [
      circle_center[0] + trajectory_radius * math.cos(t),     # X: center + circular motion
      circle_center[1] + trajectory_radius * math.sin(t),     # Y: center + circular motion  
      0.7 + 0.1 * math.sin(t * 2)                           # Z: height with slight variation
    ]
    
    #end effector points down, not up (in case useOrientation==1)
    orn = p.getQuaternionFromEuler([0, -math.pi, 0])

    if (useNullSpace == 1):
      if (useOrientation == 1):
        jointPoses = p.calculateInverseKinematics(kukaId, kukaEndEffectorIndex, pos, orn, ll, ul,
                                                  jr, rp)
      else:
        jointPoses = p.calculateInverseKinematics(kukaId,
                                                  kukaEndEffectorIndex,
                                                  pos,
                                                  lowerLimits=ll,
                                                  upperLimits=ul,
                                                  jointRanges=jr,
                                                  restPoses=rp)
    else:
      if (useOrientation == 1):
        jointPoses = p.calculateInverseKinematics(kukaId,
                                                  kukaEndEffectorIndex,
                                                  pos,
                                                  orn,
                                                  jointDamping=jd)
      else:
        threshold = 0.001
        maxIter = 100
        jointPoses = accurateCalculateInverseKinematics(kukaId, kukaEndEffectorIndex, pos,
                                                        threshold, maxIter)

    if (useSimulation):
      for i in range(numJoints):
        # Enhanced KUKA joint control with realistic servo parameters
        p.setJointMotorControl2(bodyIndex=kukaId,
                                jointIndex=i,
                                controlMode=p.POSITION_CONTROL,
                                targetPosition=jointPoses[i],
                                targetVelocity=0,
                                force=300,              # Reduced max force for smoother motion
                                positionGain=0.8,       # Optimized position gain
                                velocityGain=0.3,       # Increased velocity gain for stability
                                maxVelocity=2.0)        # Realistic joint max velocity (rad/s)
    else:
      #reset the joint state (ignoring all dynamics, not recommended to use during simulation)
      for i in range(numJoints):
        p.resetJointState(kukaId, i, jointPoses[i])

  ls = p.getLinkState(kukaId, kukaEndEffectorIndex)
  if (hasPrevPose):
    p.addUserDebugLine(prevPose, pos, [0, 0, 0.3], 1, trailDuration)
    p.addUserDebugLine(prevPose1, ls[4], [1, 0, 0], 1, trailDuration)
  prevPose = pos
  prevPose1 = ls[4]
  hasPrevPose = 1
