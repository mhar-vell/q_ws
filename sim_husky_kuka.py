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
from PIL import Image

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

# === HUSKY ROBOT LOADING WITH PROPER GROUND POSITIONING ===
# Load Husky at proper ground level (wheels touching ground at z=0)
# Ground plane is at z=-0.3, so Husky base should be around z=0.0 for proper wheel contact
husky_base_x = 0.0       # Center position
husky_base_y = 0.0       # Center position  
husky_base_z = 0.0       # Proper ground level (wheels will contact ground at z=-0.3)

husky = p.loadURDF("husky/husky.urdf", [husky_base_x, husky_base_y, husky_base_z],
                   [0.0, 0.0, 0.0, 1.0])  # Upright orientation

print(f"🚗 Husky mobile robot loaded at GROUND LEVEL:")
print(f"   • Position: [{husky_base_x:.3f}, {husky_base_y:.3f}, {husky_base_z:.3f}]")
print(f"   • Orientation: Upright (no rotation)")
print(f"   • Wheels will contact ground plane at z=-0.3")
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
# === KUKA ARM LOADING WITH PROPER MOUNTING POSITION ===
# Load KUKA at correct position: ON TOP of Husky base
# Husky center is now at [0.0, 0.0, 0.0]
# KUKA should be 0.5m above Husky center for proper mounting
kuka_mount_x = husky_base_x      # Same X as Husky center (0.0)
kuka_mount_y = husky_base_y      # Same Y as Husky center (0.0)
kuka_mount_z = husky_base_z + 0.5  # 0.5m above Husky center = 0.5

kukaId = p.loadURDF("kuka_iiwa/model_free_base.urdf", 
                    kuka_mount_x, kuka_mount_y, kuka_mount_z,  # Proper mounting position
                    0.0, 0.0, 0.0, 1.0)                       # Upright orientation

print(f"🦾 KUKA arm loaded at PROPER MOUNTING POSITION:")
print(f"   • Position: [{kuka_mount_x:.3f}, {kuka_mount_y:.3f}, {kuka_mount_z:.3f}]")
print(f"   • Height above Husky: 0.5m")
print(f"   • Orientation: Upright, aligned with Husky")
print(f"   • Ready for constraint-based mounting")
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

# BACK TO BASICS: Simple, proven constraint approach
print("🔧 Creating basic mounting constraint...")

# Create the most basic fixed constraint
cid = p.createConstraint(husky, -1, kukaId, -1, p.JOINT_FIXED, 
                         [0, 0, 0],      # Parent frame (Husky center)
                         [0, 0, 0],      # Child frame (KUKA base)  
                         [0., 0., 0.5],  # Parent offset: 0.5m UP from Husky center
                         [0, 0, 0, 1])   # Child offset: at KUKA base

# Use the default constraint settings (don't change maxForce)
print(f"✅ Basic constraint created (ID: {cid})")
print("   Using default PyBullet constraint parameters")

# Allow constraint to settle with several physics steps
print("🔧 Allowing constraint to settle...")
for i in range(50):  # 50 physics steps to settle
    p.stepSimulation()
    time.sleep(1./240.)  # Match simulation timestep

print("✅ Constraint settled - KUKA should be properly mounted")

# No verification - let PyBullet handle it naturally

# === SIMPLIFIED MOUNTING MONITORING SYSTEM ===
class MountingMonitor:
    def __init__(self, constraint_id):
        self.cid = constraint_id
        self.max_safe_force = 1200  # N - Warning threshold
        self.critical_force = 1400  # N - Critical threshold
        self.force_history = []
        self.last_check = 0
        
    def check_mounting_stability(self):
        """Monitor constraint forces and detect unmounting risks."""
        try:
            current_time = time.time()
            if current_time - self.last_check < 0.5:  # Check every 0.5s
                return True
            self.last_check = current_time
            
            # Check constraint force
            constraint_state = p.getConstraintState(self.cid)
            current_force = np.linalg.norm(constraint_state[0]) if constraint_state else 0
            self.force_history.append(current_force)
            
            # Keep only last 10 samples
            if len(self.force_history) > 10:
                self.force_history.pop(0)
            
            # Report constraint force
            print(f"🔧 Constraint Force: {current_force:.1f}N")
            
            # Check for dangerous force levels (higher thresholds for 50,000N constraint)
            if current_force > 25000:  # 50% of max force
                print(f"🚨 CRITICAL MOUNTING FORCE: {current_force:.1f}N - RISK OF UNMOUNTING!")
                return self.emergency_stabilize()
            elif current_force > 15000:  # 30% of max force
                print(f"⚠️  HIGH MOUNTING FORCE: {current_force:.1f}N - Monitoring closely")
            
            return True
            
        except Exception as e:
            print(f"❌ Mounting monitor error: {e}")
            return False
    
    def emergency_stabilize(self):
        """Emergency procedure to prevent unmounting."""
        try:
            print("🔧 EMERGENCY STABILIZATION - Reducing constraint force")
            p.changeConstraint(self.cid, maxForce=1000)  # Emergency reduction
            time.sleep(0.2)  # Brief pause
            p.changeConstraint(self.cid, maxForce=1300)  # Gradual restore
            print("✅ Emergency stabilization complete")
            return True
        except Exception as e:
            print(f"❌ Emergency stabilization failed: {e}")
            return False

# Initialize mounting monitor
mounting_monitor = MountingMonitor(cid)
print(f"🔍 Mounting stability monitor initialized")

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
            "lateral": "Going sideways forces (left/right Y-axis dominant)", 
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
            # Check if this is actually a scenario change
            scenario_changed = (self.current_scenario != scenario_name)
            
            self.current_scenario = scenario_name
            self.step_counter = 0
            self.impulse_applied = False
            print(f"🎯 Switched to '{scenario_name.upper()}' disturbance scenario")
            print(f"   Description: {self.scenarios[scenario_name]['description']}")
            
            # Request simulation restart when scenario changes
            if scenario_changed:
                request_simulation_restart(f"Scenario changed to {scenario_name.upper()}")
                print("   🔄 Simulation will restart to apply new scenario conditions")
            
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

# === PHOTO MANAGER CLASS ===
class PhotoManager:
    """
    Photo capture management for PyBullet simulations.
    Organizes screenshots in a dedicated folder with proper naming.
    """
    
    def __init__(self, output_dir="photos"):
        """
        Initialize photo manager.
        
        Args:
            output_dir: Directory to save photos
        """
        self.output_dir = output_dir
        self.photo_count = 0
        self.session_id = int(time.time())  # Unique session identifier
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Count existing photos to avoid conflicts
        existing_photos = [f for f in os.listdir(self.output_dir) if f.endswith('.png')]
        self.photo_count = len(existing_photos)
        
        print(f"PhotoManager initialized: {self.output_dir}/ ({self.photo_count} existing photos)")
    
    def capture_screenshot(self, filename_prefix="screenshot"):
        """
        Capture a screenshot of the current simulation view.
        
        Args:
            filename_prefix: Prefix for the filename
            
        Returns:
            str: Full path to saved screenshot, or None if failed
        """
        try:
            # Get current camera view
            width, height, rgb_img, depth_img, seg_img = p.getCameraImage(
                width=1920,
                height=1080,
                renderer=p.ER_BULLET_HARDWARE_OPENGL
            )
            
            # Convert to PIL Image
            rgb_array = np.array(rgb_img).reshape(height, width, 4)
            rgb_array = rgb_array[:, :, :3]  # Remove alpha channel
            img = Image.fromarray(rgb_array, 'RGB')
            
            # Generate filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}_{self.photo_count:04d}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save image
            img.save(filepath)
            self.photo_count += 1
            
            print(f"📸 Screenshot saved: {filename}")
            return filepath
            
        except Exception as e:
            print(f"⚠️  Failed to capture screenshot: {e}")
            return None
    
    def capture_training_screenshot(self, scenario, episode, algorithm=""):
        """
        Capture screenshot during RL training with descriptive naming.
        
        Args:
            scenario: Training scenario name
            episode: Episode number
            algorithm: Algorithm name (optional)
        """
        prefix = f"training_{algorithm}_{scenario}_ep{episode:03d}" if algorithm else f"training_{scenario}_ep{episode:03d}"
        return self.capture_screenshot(prefix)
    
    def get_photo_count(self):
        """Get current number of photos in the folder."""
        return self.photo_count
    
    def cleanup_old_photos(self, keep_count=1000):
        """
        Remove old photos, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent photos to keep
        """
        try:
            photo_files = [f for f in os.listdir(self.output_dir) if f.endswith('.png')]
            
            if len(photo_files) <= keep_count:
                return
            
            # Sort by modification time
            photo_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.output_dir, x)))
            
            # Remove oldest photos
            files_to_remove = photo_files[:-keep_count]
            removed_count = 0
            
            for filename in files_to_remove:
                filepath = os.path.join(self.output_dir, filename)
                os.remove(filepath)
                removed_count += 1
            
            print(f"🗑️  Cleaned up {removed_count} old photos (keeping {keep_count} most recent)")
            self.photo_count = keep_count
            
        except Exception as e:
            print(f"⚠️  Failed to cleanup photos: {e}")

# === INITIALIZE PHOTO MANAGER ===
photo_manager = PhotoManager(output_dir="photos")
print("Photo manager initialized - Use 'p' to capture screenshots")

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
# RL Trajectory Following Setup
from trajectory_generators import TrajectoryGenerator
rl_trajectory_generator = TrajectoryGenerator(base_height=0.8, base_center=(0.0, 0.0))
rl_trajectory_points = rl_trajectory_generator.generate_circle(num_points=20, radius=0.4, orientation='horizontal')  # Match autonomous circular path
rl_current_trajectory_idx = 0
rl_trajectory_phase = 0.0  # Phase for smooth circular trajectory (matching autonomous pattern)
rl_trajectory_update_steps = 15  # Update trajectory target every N steps (slower for easier learning)

# Key press timing control to prevent multiple triggers
last_key_press_time = {}  # Track last press time for each key
key_cooldown = 0.5  # Minimum seconds between key presses

# Initialize with first trajectory point
rl_goal_pose = np.array(rl_trajectory_points[0])  # Dynamic trajectory goal
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

# Enhanced training with intensity levels
rl_intensity_levels = ['normal', 'golden']
rl_use_dual_intensity = True  # Set to False to use only normal intensity

# Create comprehensive scenario-intensity combinations
if rl_use_dual_intensity:
    rl_training_combinations = []
    for scenario in rl_scenarios:
        for intensity in rl_intensity_levels:
            rl_training_combinations.append({'scenario': scenario, 'intensity': intensity})
    print(f"🎯 Dual-Intensity Training: {len(rl_training_combinations)} combinations")
else:
    rl_training_combinations = [{'scenario': s, 'intensity': 'normal'} for s in rl_scenarios]
    print(f"🎯 Standard Training: {len(rl_training_combinations)} scenarios")

# Metrics tracking for scenario-intensity combinations
rl_metrics = {}
for combo in rl_training_combinations:
    key = f"{combo['scenario']}_{combo['intensity']}"
    rl_metrics[key] = {'success': 0, 'errors': [], 'steps': [], 'energy': [], 'episodes': 0}

# Dual algorithm metrics tracking
if TRAIN_BOTH_ALGORITHMS:
    # Create combination keys for metrics tracking
    combo_keys = [f"{combo['scenario']}_{combo['intensity']}" for combo in rl_training_combinations]
    rl_algorithm_metrics = {
        'DQN': {combo_key: {'success': 0, 'errors': [], 'steps': [], 'energy': [], 'episodes': 0} for combo_key in combo_keys},
        'Q-Learning': {combo_key: {'success': 0, 'errors': [], 'steps': [], 'energy': [], 'episodes': 0} for combo_key in combo_keys}
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
rl_current_combination_idx = 0
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
print(f"Training combinations: {len(rl_training_combinations)} (5 scenarios × 2 intensities)")
print(f"Episodes per combination: {rl_num_episodes}")
if TRAIN_BOTH_ALGORITHMS:
    print(f"Episodes per algorithm: {rl_num_episodes * len(rl_training_combinations)}")
    print(f"Total episodes (both algorithms): {rl_num_episodes * len(rl_training_combinations) * 2}")
    print(f"Estimated time per algorithm: ~{(rl_num_episodes * len(rl_training_combinations) * 0.5 / 60):.1f} minutes")
    print(f"Total estimated time (both): ~{(rl_num_episodes * len(rl_training_combinations) * 2 * 0.5 / 60):.1f} minutes")
else:
    print(f"Total episodes (all combinations): {rl_num_episodes * len(rl_training_combinations)}")
    print(f"Estimated training time: ~{(rl_num_episodes * len(rl_training_combinations) * 0.5 / 60):.1f} minutes")
print(f"Max steps per episode: {rl_max_steps}")

if TRAIN_BOTH_ALGORITHMS:
    print(f"\n📋 Automatic Sequential Training Workflow:")
    print(f"  1. Train {rl_current_algorithm} completely (press 't' to start)")
    print(f"  2. 🔄 AUTOMATIC switch to {'Q-Learning' if rl_current_algorithm == 'DQN' else 'DQN'}")
    print(f"  3. Train the second algorithm completely (automatic)")
    print(f"  4. Compare performance results")
    print(f"  5. Use 'd' key to check training status anytime")
    print(f"  💡 No manual intervention required - fully automated!")
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
num_waypoints = 20                # Number of waypoints around circle (increased for RL precision)
circle_waypoints = []             # Will be generated
current_waypoint = 0              # Current target waypoint
waypoint_tolerance = 0.15         # Distance tolerance to reach waypoint (meters)

# Circular trajectory completion tracking
circle_completion_tracking = {
    'start_phase': 0,             # Phase when circle tracking started
    'accuracy_samples': [],       # Accuracy measurements during circle
    'error_samples': [],          # Error distance measurements during circle
    'is_tracking': False,         # Whether we're currently tracking a circle
    'completed_circles': 0,       # Number of completed circles tracked
    'last_completion_accuracy': 0, # Accuracy of last completed circle
    'best_accuracy': 0,           # Best circle accuracy achieved
    'average_accuracy': 0         # Average accuracy across all circles
}

# Episode and scenario tracking for reporting
session_tracking = {
    'episodes': [],               # List of episode data
    'current_episode': None,      # Current episode data
    'current_scenario': '',       # Current scenario name
    'scenario_start_time': 0,     # When current scenario started
    'session_start_time': 0,      # When session started
    'total_episodes': 0,          # Total episodes completed
    'scenario_episodes': 0        # Episodes in current scenario
}

# Initialize session tracking
session_tracking['session_start_time'] = time.time()

# Simulation restart control
restart_simulation = False
restart_reason = ""

# Archive management
def create_archive_directories():
    """Create archive directory structure if it doesn't exist"""
    import os
    
    archive_dirs = [
        "archives",
        "archives/episode_data", 
        "archives/scenario_reports",
        "archives/session_summaries"
    ]
    
    for dir_path in archive_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"📁 Created archive directory: {dir_path}")

def archive_existing_data():
    """Archive any existing episode/scenario data files from root directory"""
    import os
    import glob
    import shutil
    from datetime import datetime
    
    # Ensure archive directories exist
    create_archive_directories()
    
    archived_count = 0
    
    # Archive episode data files
    episode_files = glob.glob("episode_data_*.json")
    for file in episode_files:
        try:
            shutil.move(file, f"archives/episode_data/{file}")
            archived_count += 1
            print(f"📦 Archived: {file}")
        except Exception as e:
            print(f"❌ Could not archive {file}: {e}")
    
    # Archive scenario report files
    scenario_files = glob.glob("scenario_report_*.json")
    for file in scenario_files:
        try:
            shutil.move(file, f"archives/scenario_reports/{file}")
            archived_count += 1
            print(f"📦 Archived: {file}")
        except Exception as e:
            print(f"❌ Could not archive {file}: {e}")
    
    # Also clean up any stray model files in root
    model_files = glob.glob("rl_checkpoint_*.pth") + glob.glob("rl_final_*.pth")
    model_count = 0
    for file in model_files:
        try:
            if "checkpoint" in file:
                shutil.move(file, f"trained_models/checkpoints/{file}")
                model_count += 1
                print(f"🎯 Moved model: {file} → trained_models/checkpoints/")
            else:
                shutil.move(file, f"trained_models/final/{file}")
                model_count += 1
                print(f"🎯 Moved model: {file} → trained_models/final/")
        except Exception as e:
            print(f"❌ Could not move model {file}: {e}")

    total_organized = archived_count + model_count
    if total_organized > 0:
        print(f"✅ Successfully organized {total_organized} files ({archived_count} data, {model_count} models)")
        
        # Create archive summary
        summary = {
            'archive_date': datetime.now().isoformat(),
            'archived_files': archived_count,
            'moved_models': model_count,
            'episode_files': len(episode_files),
            'scenario_files': len(scenario_files),
            'model_files': len(model_files),
            'note': 'Data archived and models organized before new session'
        }
        
        summary_file = f"archives/session_summaries/archive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import json
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"📄 Archive summary saved: {summary_file}")
        except Exception as e:
            print(f"⚠️  Could not save archive summary: {e}")
    else:
        print("ℹ️  No data files or models to organize")

def list_archives():
    """List all archived data with summary statistics"""
    import os
    import json
    from datetime import datetime
    
    if not os.path.exists("archives"):
        print("📁 No archives directory found")
        return
    
    print("\n📊 ARCHIVE INVENTORY")
    
    # Count files in each archive directory
    episode_count = len([f for f in os.listdir("archives/episode_data") if f.endswith('.json')]) if os.path.exists("archives/episode_data") else 0
    scenario_count = len([f for f in os.listdir("archives/scenario_reports") if f.endswith('.json')]) if os.path.exists("archives/scenario_reports") else 0
    session_count = len([f for f in os.listdir("archives/session_summaries") if f.endswith('.json')]) if os.path.exists("archives/session_summaries") else 0
    
    print(f"   📝 Episode Data Files: {episode_count}")
    print(f"   📊 Scenario Reports: {scenario_count}")
    print(f"   📄 Session Summaries: {session_count}")
    print(f"   📁 Total Archived Files: {episode_count + scenario_count + session_count}")
    
    # Show recent session summaries
    if session_count > 0:
        print(f"\n   🕒 Recent Session Summaries:")
        session_files = sorted([f for f in os.listdir("archives/session_summaries") if f.endswith('.json')])[-3:]
        for file in session_files:
            try:
                with open(f"archives/session_summaries/{file}", 'r') as f:
                    data = json.load(f)
                    episodes = data.get('session_info', {}).get('total_episodes', 0)
                    accuracy = data.get('performance_summary', {}).get('overall_accuracy', 0)
                print(f"      • {file}: {episodes} episodes, {accuracy:.1f}% avg accuracy")
            except:
                print(f"      • {file}: (summary unavailable)")
    
    print(f"   💡 Use archives/ directory to access all historical data")

def request_simulation_restart(reason="Manual restart"):
    """Request a simulation restart with specified reason"""
    global restart_simulation, restart_reason
    restart_simulation = True
    restart_reason = reason
    print(f"🔄 Simulation restart requested: {reason}")

def reset_robot_state():
    """Reset robot to initial position and state"""
    global current_waypoint, path_completed_laps, circle_completion_tracking
    global rl_trajectory_phase, rl_start_time, rl_step_count, restart_simulation, restart_reason
    
    # Reset robot position to starting point
    # Use proper mounting positions (consistent with initial loading)
    husky_reset_pos = [0.0, 0.0, 0.0]  # Ground level position  
    start_orientation = p.getQuaternionFromEuler([0, 0, 0])  # Upright orientation
    
    try:
        # Reset Husky robot to ground level position
        p.resetBasePositionAndOrientation(husky, husky_reset_pos, start_orientation)
        print(f"✅ Husky reset to ground position: {husky_reset_pos}")
        
        # Reset KUKA arm to proper mounting position (0.5m above Husky)
        if 'kukaId' in globals():
            kuka_reset_pos = [0.0, 0.0, 0.5]  # 0.5m above Husky center
            p.resetBasePositionAndOrientation(kukaId, kuka_reset_pos, start_orientation)
            print(f"✅ KUKA reset to mounting position: {kuka_reset_pos}")
        
        # Stop all wheel movement
        for i in range(len(wheels)):
            p.setJointMotorControl2(husky, wheels[i], p.VELOCITY_CONTROL, targetVelocity=0, force=500)
        
        # Reset trajectory tracking variables
        current_waypoint = 0
        path_completed_laps = 0
        circle_completion_tracking['completed_circles'] = 0
        circle_completion_tracking['current_progress'] = 0
        circle_completion_tracking['best_accuracy'] = 0
        circle_completion_tracking['average_accuracy'] = 0
        
        # Reset RL training variables if RL is active
        if RL_AVAILABLE:
            rl_trajectory_phase = 0.0
            rl_step_count = 0
            rl_start_time = time.time()
        
        print("🔄 Robot state reset to initial position")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting robot state: {e}")
        return False

def request_simulation_restart(reason="Manual restart"):
    """Request a simulation restart with specified reason"""
    global restart_simulation, restart_reason
    restart_simulation = True
    restart_reason = reason
    print(f"🔄 Simulation restart requested: {reason}")

def complete_episode():
    """Complete current episode and generate report"""
    if session_tracking['current_episode'] is None:
        return
    
    import json
    from datetime import datetime
    
    episode = session_tracking['current_episode']
    episode['end_time'] = time.time()
    episode['duration'] = episode['end_time'] - episode['start_time']
    
    # Calculate episode statistics (overall and component-wise)
    if episode['accuracy_samples']:
        # Overall statistics
        episode['avg_accuracy'] = sum(episode['accuracy_samples']) / len(episode['accuracy_samples'])
        episode['max_accuracy'] = max(episode['accuracy_samples'])
        episode['min_accuracy'] = min(episode['accuracy_samples'])
        episode['avg_error'] = sum(episode['error_samples']) / len(episode['error_samples'])
        episode['samples_count'] = len(episode['accuracy_samples'])
        
        # Component-wise accuracy statistics
        episode['avg_accuracy_x'] = sum(episode['accuracy_x_samples']) / len(episode['accuracy_x_samples'])
        episode['avg_accuracy_y'] = sum(episode['accuracy_y_samples']) / len(episode['accuracy_y_samples'])
        episode['avg_accuracy_z'] = sum(episode['accuracy_z_samples']) / len(episode['accuracy_z_samples'])
        
        # Component-wise error statistics
        episode['avg_error_x'] = sum(episode['error_x_samples']) / len(episode['error_x_samples'])
        episode['avg_error_y'] = sum(episode['error_y_samples']) / len(episode['error_y_samples'])
        episode['avg_error_z'] = sum(episode['error_z_samples']) / len(episode['error_z_samples'])
        
        # Maximum errors per component
        episode['max_error_x'] = max(episode['error_x_samples'])
        episode['max_error_y'] = max(episode['error_y_samples'])
        episode['max_error_z'] = max(episode['error_z_samples'])
    else:
        episode['avg_accuracy'] = 0
        episode['max_accuracy'] = 0
        episode['min_accuracy'] = 0
        episode['avg_error'] = 0
        episode['samples_count'] = 0
        episode['avg_accuracy_x'] = episode['avg_accuracy_y'] = episode['avg_accuracy_z'] = 0
        episode['avg_error_x'] = episode['avg_error_y'] = episode['avg_error_z'] = 0
        episode['max_error_x'] = episode['max_error_y'] = episode['max_error_z'] = 0
    
    # Add to episodes list
    session_tracking['episodes'].append(episode)
    session_tracking['total_episodes'] += 1
    session_tracking['scenario_episodes'] += 1
    
    # Print episode report with component-wise analysis
    print(f"\n🎯 EPISODE {episode['episode_number']} COMPLETED")
    print(f"   Scenario: {episode['scenario'].upper()} | Direction: {episode['direction'].upper()} | Intensity: {episode['intensity'].upper()}")
    print(f"   Duration: {episode['duration']:.1f}s | Samples: {episode['samples_count']} | Circles: {episode['circles_completed']}")
    print(f"   📊 OVERALL PERFORMANCE:")
    print(f"      Accuracy: Avg={episode['avg_accuracy']:.1f}% | Max={episode['max_accuracy']:.1f}% | Min={episode['min_accuracy']:.1f}%")
    print(f"      3D Error: Avg={episode['avg_error']:.3f}m")
    print(f"   📍 COMPONENT-WISE ANALYSIS:")
    print(f"      X-Axis: Accuracy={episode['avg_accuracy_x']:.1f}% | Error={episode['avg_error_x']:.3f}m | Max Error={episode['max_error_x']:.3f}m")
    print(f"      Y-Axis: Accuracy={episode['avg_accuracy_y']:.1f}% | Error={episode['avg_error_y']:.3f}m | Max Error={episode['max_error_y']:.3f}m")
    print(f"      Z-Axis: Accuracy={episode['avg_accuracy_z']:.1f}% | Error={episode['avg_error_z']:.3f}m | Max Error={episode['max_error_z']:.3f}m")
    
    # Save to file
    save_episode_data(episode)
    
    # Reset for next episode
    session_tracking['current_episode'] = None

def complete_scenario():
    """Complete current scenario and generate comprehensive report"""
    if not session_tracking['episodes']:
        return
    
    import json
    from datetime import datetime
    
    scenario_episodes = [ep for ep in session_tracking['episodes'] 
                        if ep['scenario'] == session_tracking['current_scenario']]
    
    if not scenario_episodes:
        return
    
    # Calculate scenario statistics
    total_accuracy = sum(ep['avg_accuracy'] for ep in scenario_episodes)
    total_error = sum(ep['avg_error'] for ep in scenario_episodes)
    total_circles = sum(ep['circles_completed'] for ep in scenario_episodes)
    total_duration = sum(ep['duration'] for ep in scenario_episodes)
    
    # Calculate component-wise scenario statistics
    total_accuracy_x = sum(ep['avg_accuracy_x'] for ep in scenario_episodes)
    total_accuracy_y = sum(ep['avg_accuracy_y'] for ep in scenario_episodes)
    total_accuracy_z = sum(ep['avg_accuracy_z'] for ep in scenario_episodes)
    total_error_x = sum(ep['avg_error_x'] for ep in scenario_episodes)
    total_error_y = sum(ep['avg_error_y'] for ep in scenario_episodes)
    total_error_z = sum(ep['avg_error_z'] for ep in scenario_episodes)
    max_error_x = max(ep['max_error_x'] for ep in scenario_episodes)
    max_error_y = max(ep['max_error_y'] for ep in scenario_episodes)
    max_error_z = max(ep['max_error_z'] for ep in scenario_episodes)
    
    scenario_report = {
        'scenario': session_tracking['current_scenario'],
        'episodes_count': len(scenario_episodes),
        'total_duration': total_duration,
        'avg_accuracy': total_accuracy / len(scenario_episodes),
        'avg_error': total_error / len(scenario_episodes),
        'total_circles': total_circles,
        'best_episode_accuracy': max(ep['avg_accuracy'] for ep in scenario_episodes),
        'avg_accuracy_x': total_accuracy_x / len(scenario_episodes),
        'avg_accuracy_y': total_accuracy_y / len(scenario_episodes),
        'avg_accuracy_z': total_accuracy_z / len(scenario_episodes),
        'avg_error_x': total_error_x / len(scenario_episodes),
        'avg_error_y': total_error_y / len(scenario_episodes),
        'avg_error_z': total_error_z / len(scenario_episodes),
        'max_error_x': max_error_x,
        'max_error_y': max_error_y,
        'max_error_z': max_error_z,
        'completion_time': datetime.now().isoformat()
    }
    
    # Print scenario report with component-wise analysis
    print(f"\n🏆 SCENARIO '{session_tracking['current_scenario'].upper()}' COMPLETED")
    print(f"   Episodes: {scenario_report['episodes_count']} | Total Duration: {scenario_report['total_duration']:.1f}s | Total Circles: {scenario_report['total_circles']}")
    print(f"   📊 OVERALL PERFORMANCE:")
    print(f"      Average Accuracy: {scenario_report['avg_accuracy']:.1f}% | Best Episode: {scenario_report['best_episode_accuracy']:.1f}%")
    print(f"      Average 3D Error: {scenario_report['avg_error']:.3f}m")
    print(f"   📍 COMPONENT-WISE ANALYSIS:")
    print(f"      X-Axis: Accuracy={scenario_report['avg_accuracy_x']:.1f}% | Error={scenario_report['avg_error_x']:.3f}m | Max Error={scenario_report['max_error_x']:.3f}m")
    print(f"      Y-Axis: Accuracy={scenario_report['avg_accuracy_y']:.1f}% | Error={scenario_report['avg_error_y']:.3f}m | Max Error={scenario_report['max_error_y']:.3f}m")
    print(f"      Z-Axis: Accuracy={scenario_report['avg_accuracy_z']:.1f}% | Error={scenario_report['avg_error_z']:.3f}m | Max Error={scenario_report['max_error_z']:.3f}m")
    
    # Save scenario report
    save_scenario_report(scenario_report)
    
    # Reset scenario tracking
    session_tracking['scenario_episodes'] = 0

def save_episode_data(episode):
    """Save episode data to JSON file in archive directory"""
    import json
    import os
    from datetime import datetime
    
    # Ensure archive directory exists
    if not os.path.exists("archives/episode_data"):
        create_archive_directories()
    
    filename = f"archives/episode_data/episode_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(episode, f, indent=2)
        print(f"   💾 Episode data saved: {filename}")
    except Exception as e:
        print(f"   ⚠️  Could not save episode data: {e}")

def save_scenario_report(report):
    """Save scenario report to JSON file in archive directory"""
    import json
    import os
    from datetime import datetime
    
    # Ensure archive directory exists
    if not os.path.exists("archives/scenario_reports"):
        create_archive_directories()
    
    filename = f"archives/scenario_reports/scenario_report_{report['scenario']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"   💾 Scenario report saved: {filename}")
    except Exception as e:
        print(f"   ⚠️  Could not save scenario report: {e}")

def save_session_summary():
    """Save complete session summary to archive"""
    import json
    import os
    from datetime import datetime
    
    if not session_tracking['episodes']:
        print("ℹ️  No session data to archive")
        return
    
    # Ensure archive directory exists
    if not os.path.exists("archives/session_summaries"):
        create_archive_directories()
    
    # Calculate session statistics
    session_duration = time.time() - session_tracking['session_start_time']
    all_episodes = session_tracking['episodes']
    
    session_summary = {
        'session_info': {
            'total_episodes': session_tracking['total_episodes'],
            'session_duration': session_duration,
            'start_time': session_tracking['session_start_time'],
            'end_time': time.time(),
            'timestamp': datetime.now().isoformat()
        },
        'performance_summary': {
            'overall_accuracy': sum(ep['avg_accuracy'] for ep in all_episodes) / len(all_episodes),
            'overall_error': sum(ep['avg_error'] for ep in all_episodes) / len(all_episodes),
            'total_circles': sum(ep['circles_completed'] for ep in all_episodes),
            'component_analysis': {
                'avg_accuracy_x': sum(ep['avg_accuracy_x'] for ep in all_episodes) / len(all_episodes),
                'avg_accuracy_y': sum(ep['avg_accuracy_y'] for ep in all_episodes) / len(all_episodes), 
                'avg_accuracy_z': sum(ep['avg_accuracy_z'] for ep in all_episodes) / len(all_episodes),
                'avg_error_x': sum(ep['avg_error_x'] for ep in all_episodes) / len(all_episodes),
                'avg_error_y': sum(ep['avg_error_y'] for ep in all_episodes) / len(all_episodes),
                'avg_error_z': sum(ep['avg_error_z'] for ep in all_episodes) / len(all_episodes)
            }
        },
        'episodes': all_episodes
    }
    
    # Group by scenario for detailed analysis
    scenarios = {}
    for episode in all_episodes:
        scenario = episode['scenario']
        if scenario not in scenarios:
            scenarios[scenario] = []
        scenarios[scenario].append(episode)
    
    session_summary['scenario_breakdown'] = {}
    for scenario, episodes in scenarios.items():
        session_summary['scenario_breakdown'][scenario] = {
            'episode_count': len(episodes),
            'avg_accuracy': sum(ep['avg_accuracy'] for ep in episodes) / len(episodes),
            'avg_error': sum(ep['avg_error'] for ep in episodes) / len(episodes),
            'total_circles': sum(ep['circles_completed'] for ep in episodes)
        }
    
    # Save session summary
    filename = f"archives/session_summaries/session_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(session_summary, f, indent=2)
        print(f"📄 Session summary archived: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Could not save session summary: {e}")
        return None

def generate_session_summary():
    """Generate complete session summary"""
    if not session_tracking['episodes']:
        print("\n📊 SESSION SUMMARY: No episodes recorded yet")
        return
    
    print(f"\n📊 SESSION SUMMARY")
    print(f"   Total Episodes: {session_tracking['total_episodes']}")
    print(f"   Session Duration: {(time.time() - session_tracking['session_start_time']):.1f}s")
    
    # Calculate overall session statistics
    all_episodes = session_tracking['episodes']
    session_avg_accuracy = sum(ep['avg_accuracy'] for ep in all_episodes) / len(all_episodes)
    session_avg_error = sum(ep['avg_error'] for ep in all_episodes) / len(all_episodes)
    session_avg_accuracy_x = sum(ep['avg_accuracy_x'] for ep in all_episodes) / len(all_episodes)
    session_avg_accuracy_y = sum(ep['avg_accuracy_y'] for ep in all_episodes) / len(all_episodes)
    session_avg_accuracy_z = sum(ep['avg_accuracy_z'] for ep in all_episodes) / len(all_episodes)
    session_avg_error_x = sum(ep['avg_error_x'] for ep in all_episodes) / len(all_episodes)
    session_avg_error_y = sum(ep['avg_error_y'] for ep in all_episodes) / len(all_episodes)
    session_avg_error_z = sum(ep['avg_error_z'] for ep in all_episodes) / len(all_episodes)
    
    print(f"\n   📊 SESSION OVERALL PERFORMANCE:")
    print(f"      Overall Accuracy: {session_avg_accuracy:.1f}% | Overall 3D Error: {session_avg_error:.3f}m")
    print(f"   📍 SESSION COMPONENT-WISE ANALYSIS:")
    print(f"      X-Axis: Accuracy={session_avg_accuracy_x:.1f}% | Error={session_avg_error_x:.3f}m")
    print(f"      Y-Axis: Accuracy={session_avg_accuracy_y:.1f}% | Error={session_avg_error_y:.3f}m")
    print(f"      Z-Axis: Accuracy={session_avg_accuracy_z:.1f}% | Error={session_avg_error_z:.3f}m")
    
    # Group by scenario
    scenarios = {}
    for episode in session_tracking['episodes']:
        scenario = episode['scenario']
        if scenario not in scenarios:
            scenarios[scenario] = []
        scenarios[scenario].append(episode)
    
    print(f"\n   🎯 BY SCENARIO:")
    for scenario, episodes in scenarios.items():
        avg_acc = sum(ep['avg_accuracy'] for ep in episodes) / len(episodes)
        avg_acc_x = sum(ep['avg_accuracy_x'] for ep in episodes) / len(episodes)
        avg_acc_y = sum(ep['avg_accuracy_y'] for ep in episodes) / len(episodes)
        avg_acc_z = sum(ep['avg_accuracy_z'] for ep in episodes) / len(episodes)
        print(f"      {scenario.upper()}: {len(episodes)} episodes")
        print(f"         Overall: {avg_acc:.1f}% | X: {avg_acc_x:.1f}% | Y: {avg_acc_y:.1f}% | Z: {avg_acc_z:.1f}%")
    
    # Save session summary to archive
    print(f"\n📦 Archiving session summary...")
    save_session_summary()

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
    try:
        if use_waypoints:
            # Add waypoint markers (small red spheres) - use createMultiBody instead of debug items
            for i, waypoint in enumerate(circle_waypoints):
                world_x = waypoint[0]
                world_y = waypoint[1]
                world_z = 0.1  # Slightly above ground
                
                marker_id = p.createVisualShape(p.GEOM_SPHERE, radius=0.05, rgbaColor=[1, 0, 0, 0.8])
                p.createMultiBody(baseMass=0, baseVisualShapeIndex=marker_id,
                                 basePosition=[world_x, world_y, world_z])
                
                # Reduce waypoint labels to prevent debug overflow
                if i % 4 == 0:  # Only show every 4th waypoint label
                    p.addUserDebugText(f"WP{i+1}", [world_x, world_y, world_z + 0.1], 
                                      textColorRGB=[1, 1, 1], textSize=1.0)
            
            # Add fewer connecting lines to reduce debug items
            step = max(1, num_waypoints // 8)  # Show only 8 connecting lines maximum
            for i in range(0, num_waypoints, step):
                start_wp = circle_waypoints[i]
                end_wp = circle_waypoints[(i + step) % num_waypoints]
                
                start_pos = [start_wp[0], start_wp[1], 0.05]
                end_pos = [end_wp[0], end_wp[1], 0.05]
                
                p.addUserDebugLine(start_pos, end_pos, lineColorRGB=[0, 0, 1], lineWidth=2.0)
        else:
            # For smooth circular motion, draw fewer circle segments
            num_segments = 12  # Reduced from 32 to prevent debug overflow
            for i in range(num_segments):
                angle1 = (2 * math.pi * i) / num_segments
                angle2 = (2 * math.pi * (i + 1)) / num_segments
                
                x1 = circle_center[0] + circle_radius * math.cos(angle1)
                y1 = circle_center[1] + circle_radius * math.sin(angle1)
                x2 = circle_center[0] + circle_radius * math.cos(angle2)
                y2 = circle_center[1] + circle_radius * math.sin(angle2)
                
                p.addUserDebugLine([x1, y1, 0.05], [x2, y2, 0.05], lineColorRGB=[0, 0, 1], lineWidth=2.0)
    except Exception as e:
        print(f"Warning: Could not create trajectory markers: {e}")
        # Continue without trajectory visualization
    
    # Center marker removed - was confusing as it appeared near ground
    
    # Print path information
    print("\n=== Circular Path Configuration ===")
    print(f"Circular path: radius={circle_radius}m, center=({circle_center[0]:.2f}, {circle_center[1]:.2f})")
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

# === RL TRAJECTORY VISUALIZATION ===
def add_rl_trajectory_markers():
    """Add visual markers for RL training trajectory - smooth circular path."""
    if RL_AVAILABLE:
        print("Adding RL trajectory markers...")
        
        # Generate circular trajectory points for visualization
        trajectory_radius = 0.2  # Same radius as RL target and autonomous manipulator
        num_visual_points = 20   # Reasonable number of visual points
        
        smooth_points = []
        for i in range(num_visual_points):
            phase = 2 * math.pi * i / num_visual_points
            x = circle_center[0] + trajectory_radius * math.cos(phase)
            y = circle_center[1] + trajectory_radius * math.sin(phase)
            z = 0.7 + 0.1 * math.sin(phase * 2)  # Same Z pattern as RL target
            smooth_points.append([x, y, z])
        
        # Create visual markers for circular trajectory
        for i, point in enumerate(smooth_points):
            # Create small waypoint markers
            marker_id = p.createVisualShape(p.GEOM_SPHERE, radius=0.015, rgbaColor=[0, 1, 0, 0.7])
            marker_body = p.createMultiBody(baseVisualShapeIndex=marker_id, 
                                          basePosition=[point[0], point[1], point[2]])
            
            # Add line connections for smooth trajectory visualization
            if i > 0:
                prev_point = smooth_points[i-1]
                p.addUserDebugLine([prev_point[0], prev_point[1], prev_point[2]], 
                                 [point[0], point[1], point[2]], 
                                 lineColorRGB=[0, 1, 0], lineWidth=1.5)
        
        # Close the smooth trajectory loop
        if len(smooth_points) > 2:
            last_point = smooth_points[-1]
            first_point = smooth_points[0]
            p.addUserDebugLine([last_point[0], last_point[1], last_point[2]], 
                             [first_point[0], first_point[1], first_point[2]], 
                             lineColorRGB=[0, 1, 0], lineWidth=1.5)
        
        print(f"✅ Added smooth circular trajectory: {num_visual_points} visual points, radius={trajectory_radius}m")

# Add RL trajectory visualization
if RL_AVAILABLE:
    add_rl_trajectory_markers()

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
print("  'r' - Restart simulation (full reset)") 
print("  'i' - Display immediate IMU readings")
print("  'p' - Apply manual perturbation (test IMU response)")
print("  'v' - Start/stop video recording (30s max)")
print("  'p' - Capture screenshot (organized in photos/ folder)")
print("  'c' - Change camera angle (when not recording)")
print("  'x' - Quick test recording (10 seconds)")
print("  DISTURBANCE SCENARIOS (auto-restart on change):")
print("    '1' - NONE scenario (no disturbances)")
print("    '2' - RANDOM scenario (continuous noise ±50N)")
print("    '3' - PERIODIC scenario (impacts every 50 steps ±100N)")
print("    '4' - CONTINUOUS scenario (persistent bias ±10N)")
print("    '5' - IMPULSE scenario (single shock ±200N)")
print("    'd' - Display current disturbance status")
print("  DISTURBANCE DIRECTIONS:")
print("    'N/F/G/U/J' - Direction modes (raNdom/Forward/Going sideways/Up/Jerk)")
print("  DISTURBANCE INTENSITY:")
print("    'O' - nOrmal intensity (1.0x forces)")
print("    'Y' - intensitY/Golden intensity (φ = 1.61803x forces - Golden ratio)")

if RL_AVAILABLE:
    print("  RL TRAJECTORY PLANNER:")
    print("    't' - Toggle RL training mode (Circular trajectory following)")
    print("    'e' - Toggle RL execution mode (run learned policy)")
    print("    'l' - Load saved RL model")
    print("    'q' - Test disturbance rejection capability")
    if TRAIN_BOTH_ALGORITHMS:
        print("    'k' - Switch between DQN and Q-Learning algorithms")

print("  EPISODE & SCENARIO TRACKING (Auto-archived):")
print("    'z' - Complete current episode and save report")
print("    'h' - Complete current scenario and save comprehensive report") 
print("    'j' - Generate complete session summary and archive")
print("  DATA MANAGEMENT:")
print("    'a' - Display archive inventory and statistics")
print("    Archives automatically saved to archives/ directory")
print("    Episode data, scenario reports, and session summaries preserved")
print("  Arrow keys - Manual control (when autonomous off)")
print("")
print("FEATURES:")
print("  📹 VIDEO RECORDING - Records simulation as MP4 video")
print("  � PHOTO CAPTURE - Organized screenshots in photos/ folder")
print("  �📊 IMU SENSORS - Accelerometer with realistic noise and bias")
print("  🎮 IMU CONTROL - Gyroscope with drift simulation") 
print("  🎯 AUTO STABILITY - Disturbance rejection using IMU feedback")
print("  �️  DISTURBANCE SIM - 5 systematic disturbance scenarios for testing")

if RL_AVAILABLE:
    print("  🤖 RL TRAJECTORY PLANNER:")
    if TRAIN_BOTH_ALGORITHMS:
        print("    • DUAL ALGORITHM MODE: DQN + Tabular Q-Learning")
        print("    • 🔄 AUTOMATIC sequential training (no manual switching)")
        print("    • Automatic performance comparison and metrics")
    else:
        print("    • Q-learning & Deep Q-Networks (DQN) for adaptive control")
    print("    • End-effector trajectory following with disturbance rejection")
    print("    • Inverse kinematics integration with Jacobian control")
    print("    • Real-time performance metrics and learning visualization")

print("=============================================================")

while 1:
  # === SIMULATION RESTART CHECK ===
  if restart_simulation:
    print(f"\n🔄 RESTARTING SIMULATION: {restart_reason}")
    
    # Reset robot state first
    reset_robot_state()
    
    # Clear all debug items to prevent visual artifacts
    try:
      p.removeAllUserDebugItems()
      time.sleep(0.005)  # Brief delay for cleanup
    except:
      pass
    
    # Reset episode tracking if active
    if session_tracking['current_episode'] is not None:
      print("   📊 Episode tracking reset due to restart")
      session_tracking['current_episode'] = None
    
    # Reset trajectory visualization
    try:
      add_circular_path_markers()
    except:
      pass
    
    # Clear restart flag
    restart_simulation = False
    restart_reason = ""
    
    print("✅ Simulation restart completed\n")
  
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
    
    # ANTI-UNMOUNTING: Check mounting stability
    try:
      mounting_stability = mounting_monitor.check_mounting_stability()
      if not mounting_stability:
        print("🚨 MOUNTING INSTABILITY - Taking corrective action")
    except Exception as e:
      print(f"⚠️  Mounting monitor error: {e}")
  
  keys = p.getKeyboardEvents()
  
  # Debug: Show when 't' key is detected
  if ord('t') in keys:
    print(f"🔍 RAW DEBUG: 't' key detected in keys! Value: {keys[ord('t')]}")
  
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
      # Add cooldown protection for 'm' key
      current_time = time.time()
      if current_time - last_key_press_time.get('m', 0) > key_cooldown:
        last_key_press_time['m'] = current_time
        autonomous_mode = not autonomous_mode
        print(f"🔄 Mode switched: {'AUTONOMOUS' if autonomous_mode else 'MANUAL'}")
        
        # Force immediate visual status update with error handling
        try:
          p.removeAllUserDebugItems()
          time.sleep(0.002)  # Small delay to prevent conflicts
          
          if autonomous_mode:
            p.addUserDebugText("AUTONOMOUS MODE", textPosition=[0, 0, 2], textColorRGB=[1, 0.5, 0], textSize=1.5)
            p.addUserDebugText("Following circular path", textPosition=[0, 0, 1.5], textColorRGB=[1, 1, 1], textSize=1.0)
          else:
            p.addUserDebugText("MANUAL MODE", textPosition=[0, 0, 2], textColorRGB=[0.5, 0.5, 0.5], textSize=1.5)
            p.addUserDebugText("Press 't' to train or 'm' for autonomous", textPosition=[0, 0, 1.5], textColorRGB=[1, 1, 1], textSize=1.0)
        except:
          pass  # Fail silently if debug items can't be updated
    if ord('r') in keys:
      # Add cooldown protection for 'r' key
      current_time = time.time()
      if current_time - last_key_press_time.get('r', 0) > key_cooldown:
        last_key_press_time['r'] = current_time
        request_simulation_restart("Manual restart (R key)")
        print("🔄 Manual restart requested")
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
    if ord('p') in keys:
      # Capture screenshot
      print("📸 'p' key detected!")  # Debug: confirm key press
      scenario_info = f"{disturbance_manager.current_scenario}_{disturbance_manager.intensity_mode}" if hasattr(disturbance_manager, 'current_scenario') else "simulation"
      filename_prefix = f"manual_{scenario_info}"
      photo_manager.capture_screenshot(filename_prefix)
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
    if ord('z') in keys:
      # Complete current episode and generate report
      complete_episode()
    if ord('h') in keys:
      # Complete current scenario and generate comprehensive report  
      complete_scenario()
    if ord('j') in keys:
      # Generate complete session summary
      generate_session_summary()
    if ord('a') in keys:
      # Display archive inventory
      list_archives()
    if ord('t') in keys:
      print(f"🔍 DEBUG: 't' key pressed! Keys state: {keys[ord('t')]}")
      current_time = time.time()
      if current_time - last_key_press_time.get('t', 0) > key_cooldown:
        last_key_press_time['t'] = current_time
        print(f"🔍 DEBUG: 't' key detected! RL_AVAILABLE={RL_AVAILABLE}, cooldown passed")
        # Always allow built-in RL training (tabular Q-learning) regardless of external modules
        # The built-in RL system doesn't require external trajectory planner
        try:
          # ABSOLUTE MINIMAL: Just toggle the flag, change nothing else
          rl_training_mode = not rl_training_mode
          if rl_training_mode:
            print("\n" + "="*60)
            print("🎓 RL TRAINING ACTIVATED")
            print("="*60)
            print(f"📊 Current Episode: {rl_current_episode + 1}/{rl_num_episodes}")
            print(f"🎯 Algorithm: {rl_current_algorithm}")
            print(f"📈 Training Progress: {(rl_current_episode/rl_num_episodes)*100:.1f}%")
            # Check constraint integrity
            constraint_info = p.getConstraintInfo(cid)
            print(f"🔧 Constraint Status: {constraint_info}")
            print("="*60 + "\n")
            # Don't change autonomous_mode
            # Don't change rl_execution_mode  
            # Don't call any functions
            # Don't modify any robots or constraints
            
            # MINIMAL visual status update - safe version to show RL training is active
            try:
              # Clear and show RL training status (minimal to prevent GUI issues)
              p.removeAllUserDebugItems()
              time.sleep(0.005)  # Small delay
              p.addUserDebugText("🎓 RL TRAINING ACTIVE", textPosition=[0, 0, 2.5], 
                               textColorRGB=[0, 1, 0], textSize=1.8)
              p.addUserDebugText(f"Episode: {rl_current_episode + 1}/{rl_num_episodes}", 
                               textPosition=[0, 0, 2.0], textColorRGB=[1, 1, 1], textSize=1.2)
            except:
              pass  # Fail silently if visual updates cause issues
          else:
            # Stop robot movement when disabling RL training
            for i in range(len(wheels)):
              p.setJointMotorControl2(husky, wheels[i], p.VELOCITY_CONTROL, targetVelocity=0, force=500)
            print("🎓 RL TRAINING STOPPED ❌")
            
            # MINIMAL visual status update - safe version to show manual mode
            try:
              # Clear and show manual mode status
              p.removeAllUserDebugItems()
              time.sleep(0.005)  # Small delay
              p.addUserDebugText("MANUAL MODE", textPosition=[0, 0, 2.5], 
                               textColorRGB=[0.5, 0.5, 0.5], textSize=1.8)
              p.addUserDebugText("Press 't' to train or 'm' for autonomous", 
                               textPosition=[0, 0, 2.0], textColorRGB=[1, 1, 1], textSize=1.0)
            except:
              pass  # Fail silently if visual updates cause issues
        except Exception as e:
          print(f"❌ Error toggling RL training mode: {e}")
          print("   Check that RL environment is properly initialized")
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
      # Switch to NONE scenario with cooldown protection
      current_time = time.time()
      if current_time - last_key_press_time.get('1', 0) > key_cooldown:
        last_key_press_time['1'] = current_time
        disturbance_manager.set_scenario("none")
    if ord('2') in keys:
      # Switch to RANDOM scenario with cooldown protection
      current_time = time.time()
      if current_time - last_key_press_time.get('2', 0) > key_cooldown:
        last_key_press_time['2'] = current_time
        disturbance_manager.set_scenario("random")
    if ord('3') in keys:
      # Switch to PERIODIC scenario with cooldown protection
      current_time = time.time()
      if current_time - last_key_press_time.get('3', 0) > key_cooldown:
        last_key_press_time['3'] = current_time
        disturbance_manager.set_scenario("periodic")
    if ord('4') in keys:
      # Switch to CONTINUOUS scenario with cooldown protection
      current_time = time.time()
      if current_time - last_key_press_time.get('4', 0) > key_cooldown:
        last_key_press_time['4'] = current_time
        disturbance_manager.set_scenario("continuous")
    if ord('5') in keys:
      # Switch to IMPULSE scenario with cooldown protection
      current_time = time.time()
      if current_time - last_key_press_time.get('5', 0) > key_cooldown:
        last_key_press_time['5'] = current_time
        disturbance_manager.set_scenario("impulse")
    
    # === DIRECTIONAL MODE CONTROLS ===
    if ord('n') in keys:
      # Switch to RANDOM directional mode (N for raNdom)
      disturbance_manager.set_directional_mode("random")
    if ord('f') in keys:
      # Switch to FORWARD directional mode
      disturbance_manager.set_directional_mode("forward")
    if ord('g') in keys:
      # Switch to LATERAL directional mode (G for Going sideways)
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
    if ord('y') in keys:
      # Switch to GOLDEN intensity mode (Y for intensitY/φ)  
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
      print(f"   Scenario Controls: Press 1-5 to switch scenarios (triggers restart)")
      print(f"   Direction Controls: Press N/F/G/U/J for directional modes")
      print(f"     N=raNdom, F=Forward, G=Going sideways, U=Up/vertical, J=Jerk")
      print(f"   Intensity Controls: Press O/Y for intensity modes")
      print(f"     O=nOrmal (1.0x), Y=intensitY/Golden (φ = {disturbance_manager.golden_ratio}x)")
      
      # Display RL algorithm status if dual mode enabled
      if RL_AVAILABLE and TRAIN_BOTH_ALGORITHMS:
        print(f"\n🤖 RL ALGORITHM STATUS:")
        print(f"   Current Algorithm: {rl_current_algorithm}")
        print(f"   Training Mode: {'ACTIVE' if rl_training_mode else 'INACTIVE'}")
        dqn_status = "✅ COMPLETED" if rl_algorithm_comparison['DQN']['completed'] else "⏳ PENDING"
        qlearn_status = "✅ COMPLETED" if rl_algorithm_comparison['Q-Learning']['completed'] else "⏳ PENDING"
        print(f"   DQN Training: {dqn_status}")
        print(f"   Q-Learning Training: {qlearn_status}")
        print(f"   Algorithm Switching: 🔄 AUTOMATIC (seamless transition)")
        if not rl_algorithm_comparison['DQN']['completed'] and not rl_algorithm_comparison['Q-Learning']['completed']:
          print(f"   💡 Sequential Training: {rl_current_algorithm} → {'Q-Learning' if rl_current_algorithm == 'DQN' else 'DQN'} (automatic)")
        elif rl_algorithm_comparison['DQN']['completed'] and not rl_algorithm_comparison['Q-Learning']['completed']:
          print(f"   💡 Status: DQN completed, Q-Learning will start automatically")
        elif not rl_algorithm_comparison['DQN']['completed'] and rl_algorithm_comparison['Q-Learning']['completed']:
          print(f"   💡 Status: Q-Learning completed, DQN will start automatically")
        else:
          print(f"   🎉 Both algorithms completed! Compare results with analysis tools.")
      
      # Display photo management status
      print(f"\n📸 PHOTO STATUS:")
      print(f"   Total Photos: {photo_manager.get_photo_count()}")
      print(f"   Storage Location: {photo_manager.output_dir}/")
      if photo_manager.get_photo_count() > 500:
        print(f"   ⚠️  Consider cleanup: {photo_manager.get_photo_count()} photos (press Ctrl+C and run photo_manager.cleanup_old_photos())")

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
  if rl_training_mode and rl_current_combination_idx < len(rl_training_combinations):
    current_combo = rl_training_combinations[rl_current_combination_idx]
    scenario = current_combo['scenario']
    intensity = current_combo['intensity']
    
    # Initialize episode if needed
    if rl_step_counter == 0:
      # DISABLE FULL RESET to prevent unmounting - always continue from current position
      print(f"🎯 Episode {rl_current_episode + 1}/{rl_num_episodes} - Continuing from current position (reset disabled)")
      # Just get current state without any reset to avoid constraint issues
      rl_state = rl_env.get_state()
      
      # Check constraint stability without any reset operations
      try:
        constraint_state = p.getConstraintState(cid)
        if constraint_state:
          force = np.linalg.norm(constraint_state[0])
          print(f"🔧 Episode start constraint force: {force:.1f}N - {'✅ STABLE' if force < 1500 else '⚠️ HIGH'}")
      except:
        print("⚠️  Could not check constraint")
      
      rl_env.current_disturbance = scenario
      
      # Reset smooth circular trajectory tracking for new episode
      rl_trajectory_phase = 0.0
      
      # Calculate initial smooth circular target position
      trajectory_radius = 0.2  # Same radius as autonomous manipulator
      target_x = circle_center[0] + trajectory_radius * math.cos(rl_trajectory_phase)
      target_y = circle_center[1] + trajectory_radius * math.sin(rl_trajectory_phase)
      target_z = 0.7 + 0.1 * math.sin(rl_trajectory_phase * 2)
      
      rl_env.goal_pose = np.array([target_x, target_y, target_z, 0, 0, 0])
      
      # Stop any existing wheel movement for clean start
      for i in range(len(wheels)):
        p.setJointMotorControl2(husky, wheels[i], p.VELOCITY_CONTROL, targetVelocity=0, force=300)
      
      # Synchronize disturbance manager with RL training scenario and intensity
      disturbance_manager.set_scenario(scenario)
      disturbance_manager.set_intensity_mode(intensity)
      
      intensity_symbol = "⚡" if intensity == "golden" else "📊"
      intensity_factor = disturbance_manager.intensity_modes[intensity]["factor"]
      print(f"🎯 Episode {rl_current_episode + 1}/{rl_num_episodes} | Scenario: {scenario.upper()} | Intensity: {intensity_symbol}{intensity.upper()}")
    
    # Update trajectory with smooth circular motion (matching autonomous pattern)
    if rl_step_counter % rl_trajectory_update_steps == 0:
      # Increment phase for smooth circular trajectory
      rl_trajectory_phase += 0.3  # Advance phase for next target
      if rl_trajectory_phase >= 2 * math.pi:
        rl_trajectory_phase -= 2 * math.pi
        print("🔄 Completed full circular trajectory!")
      
      # Calculate smooth circular target position (matching autonomous manipulator)
      trajectory_radius = 0.2  # Same radius as autonomous manipulator
      target_x = circle_center[0] + trajectory_radius * math.cos(rl_trajectory_phase)
      target_y = circle_center[1] + trajectory_radius * math.sin(rl_trajectory_phase)
      target_z = 0.7 + 0.1 * math.sin(rl_trajectory_phase * 2)  # Same Z pattern as autonomous
      
      rl_env.goal_pose = np.array([target_x, target_y, target_z, 0, 0, 0])
      print(f"🎯 Target: Smooth circular position (phase: {rl_trajectory_phase:.2f})")
      
      # Add visual marker for current target position - DISABLED to prevent GUI panel issues
      if False:  # Disabled to prevent GUI panels from appearing
        try:
          target_pos = [target_x, target_y, target_z]
          # Add bright red sphere marker (no text to reduce debug items)
          p.addUserDebugText("●", textPosition=[target_pos[0], target_pos[1], target_pos[2]], 
                             textColorRGB=[1, 0, 0], textSize=2.0)
        except:
          pass  # Fail silently if target marker can't be added
    
    # Execute one RL step per simulation frame
    # Safety check: Initialize rl_state if None (first time RL training starts)
    if rl_state is None:
      rl_state = rl_env.get_state()
      print("🔧 RL state initialized for first training step")
    
    rl_action = rl_agent.select_action(rl_state)
    rl_next_state, rl_reward, rl_done = rl_env.step(rl_action)
    rl_agent.update(rl_state, rl_action, rl_reward, rl_next_state)
    rl_state = rl_next_state
    rl_step_counter += 1
    
    # Debug output for episode progress (every 50 steps)
    if rl_step_counter % 50 == 0:
      base_pos = rl_state[:2]
      goal_pos = rl_env.goal_pose[:2]
      base_error = np.linalg.norm(base_pos - goal_pos)
      print(f"Step {rl_step_counter}: base_error={base_error:.3f}m, done={rl_done}, reward={rl_reward:.3f}")
    
    # ANTI-UNMOUNTING: Quick mounting check every 100 steps during RL training
    if rl_step_counter % 100 == 0:
      try:
        mounting_monitor.check_mounting_stability()
      except:
        pass  # Don't interrupt training for monitoring errors
    
    # Apply RL wheel commands safely (avoids control conflicts)
    if hasattr(rl_env, 'rl_wheel_commands') and rl_env.rl_wheel_commands.get('active', False):
      rl_wheel_cmd = rl_env.rl_wheel_commands
      angle_diff = rl_wheel_cmd['angle_diff']
      forward_speed = rl_wheel_cmd['forward_speed']
      turn_speed = rl_wheel_cmd['turn_speed']
      
      # Apply RL wheel control with same logic as autonomous mode
      rl_wheelVelocities = [0] * len(wheels)
      angle_threshold = 0.2
      
      if abs(angle_diff) > angle_threshold:
        turn_direction = 1 if angle_diff > 0 else -1
        for i in range(len(wheels)):
          rl_wheelVelocities[i] = turn_direction * turn_speed * wheelDeltasTurn[i]
      else:
        turn_correction = angle_diff * 0.3
        for i in range(len(wheels)):
          rl_wheelVelocities[i] = forward_speed * wheelDeltasFwd[i] + turn_correction * wheelDeltasTurn[i]
      
      # Apply RL wheel velocities
      for i in range(len(wheels)):
        p.setJointMotorControl2(husky, wheels[i], p.VELOCITY_CONTROL,
                                targetVelocity=rl_wheelVelocities[i], force=300,  # Reduced force for stability
                                positionGain=0.1, velocityGain=1.0, maxVelocity=5.0)  # Reduced max velocity
      
      # Reset command after applying
      rl_env.rl_wheel_commands['active'] = False
    
    # Simple progress update
    if rl_step_counter % 100 == 0:  # Every 100 steps
      print(f"📈 Episode Progress: Step {rl_step_counter}/200 | Reward: {rl_reward:.2f}")
    
    # Track energy (use combined scenario-intensity key)
    combo_key = f"{scenario}_{intensity}"
    ep_energy = rl_metrics[combo_key].get('current_energy', 0)
    if rl_action >= rl_env.p.getNumJoints(rl_env.kuka):
      ep_energy += 1.0
    rl_metrics[combo_key]['current_energy'] = ep_energy
    
    # Check episode completion
    if rl_done or rl_step_counter >= rl_max_steps:
      final_error = np.linalg.norm(rl_state[-4:-1] - rl_env.goal_pose[:3])
      
      if rl_done:
        rl_metrics[combo_key]['success'] += 1
        trajectory_progress = (rl_trajectory_phase / (2 * math.pi)) * 100  # Phase-based progress
        print(f"[RL][{scenario.upper()}] {intensity_symbol}{intensity.upper()} Episode {rl_current_episode + 1} SUCCESS: steps={rl_step_counter}, error={final_error:.3f}m, trajectory={trajectory_progress:.1f}%, energy={ep_energy}")
        
        # Capture screenshot for successful episodes (every 10th success) - DISABLED during RL to avoid GUI issues
        success_count = rl_metrics[combo_key]['success']
        if False:  # Disabled to prevent GUI panel issues
          photo_manager.capture_training_screenshot(scenario, rl_current_episode + 1, rl_current_algorithm)
      else:
        trajectory_progress = (rl_trajectory_phase / (2 * math.pi)) * 100  # Phase-based progress
        print(f"[RL][{scenario.upper()}] {intensity_symbol}{intensity.upper()} Episode {rl_current_episode + 1} TIMEOUT: steps={rl_step_counter}, error={final_error:.3f}m, trajectory={trajectory_progress:.1f}%, energy={ep_energy}")
      
      rl_metrics[combo_key]['errors'].append(final_error)
      rl_metrics[combo_key]['steps'].append(rl_step_counter)
      rl_metrics[combo_key]['energy'].append(ep_energy)
      rl_metrics[combo_key]['episodes'] += 1
      
      # Reset for next episode
      rl_step_counter = 0
      rl_current_episode += 1
      rl_metrics[combo_key]['current_energy'] = 0
      
      # Save checkpoint every 100 episodes
      if rl_current_episode % 100 == 0 and rl_current_episode > 0:
        try:
          rl_agent.save(f'trained_models/checkpoints/rl_checkpoint_{scenario}_ep{rl_current_episode}')
          print(f"💾 Checkpoint saved: {scenario} episode {rl_current_episode} (Next episode will reset robot position)")
        except Exception as e:
          print(f"⚠️  Failed to save checkpoint: {e}")
      
      # Check if current combination is complete
      if rl_current_episode >= rl_num_episodes:
        print(f"\n=== Combination '{scenario.upper()}_{intensity.upper()}' Complete ===")
        m = rl_metrics[combo_key]
        success_rate = 100.0 * m['success'] / m['episodes']
        avg_error = np.mean(m['errors'])
        avg_steps = np.mean(m['steps'])
        avg_energy = np.mean(m['energy'])
        print(f"Success Rate: {success_rate:5.1f}% | Avg Error: {avg_error:6.3f} | Avg Steps: {avg_steps:5.1f} | Avg Energy: {avg_energy:5.1f}\n")
        
        # Save final model for this combination
        try:
          rl_agent.save(f'trained_models/final/rl_final_{scenario}_{intensity}')
          print(f"💾 Final model saved for combination '{scenario}_{intensity}'")
        except Exception as e:
          print(f"⚠️  Failed to save final model: {e}")
        
        # Move to next combination
        rl_current_combination_idx += 1
        rl_current_episode = 0
        
        # Prepare next combination (if available)
        if rl_current_combination_idx < len(rl_training_combinations):
          next_combo = rl_training_combinations[rl_current_combination_idx]
          next_scenario = next_combo['scenario']
          next_intensity = next_combo['intensity']
          next_symbol = "⚡" if next_intensity == "golden" else "📊"
          print(f"\n🔄 ADVANCING TO NEXT COMBINATION: {next_scenario.upper()}_{next_intensity.upper()}")
          print(f"   {next_symbol} Next: {next_scenario.upper()} scenario with {next_intensity.upper()} intensity")
          print(f"   Episodes per combination: {rl_num_episodes}")
          print(f"   Combinations remaining: {len(rl_training_combinations) - rl_current_combination_idx}")
        
        
        # Check if all combinations complete for current algorithm
        if rl_current_combination_idx >= len(rl_training_combinations):
          print(f"\n=== {rl_current_algorithm} Training Complete - All Combinations ===")
          for combo in rl_training_combinations:
            combo_key = f"{combo['scenario']}_{combo['intensity']}"
            symbol = "⚡" if combo['intensity'] == "golden" else "📊"
            display_name = f"{symbol} {combo['scenario']}_{combo['intensity']}"
            
            if combo_key in rl_metrics:
              m = rl_metrics[combo_key]
              success_rate = 100.0 * m['success'] / m['episodes']
              avg_error = np.mean(m['errors'])
              avg_steps = np.mean(m['steps'])
              avg_energy = np.mean(m['energy'])
              print(f"{display_name:<15} | Success: {success_rate:5.1f}% | Error: {avg_error:6.3f} | Steps: {avg_steps:5.1f} | Energy: {avg_energy:5.1f}")
          
          # Save metrics for current algorithm
          algorithm_metrics_file = f'rl_metrics_{rl_current_algorithm.lower()}.json'
          with open(algorithm_metrics_file, 'w') as f:
            json.dump(rl_metrics, f, indent=2)
          print(f'\n💾 {rl_current_algorithm} metrics saved to {algorithm_metrics_file}')
          
          # Mark current algorithm as completed
          if TRAIN_BOTH_ALGORITHMS and rl_current_algorithm in rl_algorithm_comparison:
            rl_algorithm_comparison[rl_current_algorithm]['completed'] = True
            rl_algorithm_comparison[rl_current_algorithm]['training_time'] = time.time() - rl_start_time
            
            # Check if we need to switch to second algorithm automatically
            if rl_current_algorithm == "DQN" and not rl_algorithm_comparison['Q-Learning']['completed']:
              print(f"\n🔄 AUTOMATIC ALGORITHM SWITCH: DQN → Q-Learning")
              print(f"   ✅ DQN completed all {len(rl_training_combinations)} combinations")
              print(f"   🚀 Automatically starting Q-Learning training...")
              
              # Switch to Q-Learning
              rl_agent = rl_agent_qlearn
              rl_current_algorithm = "Q-Learning"
              
              # Reset training state for second algorithm
              rl_current_combination_idx = 0
              rl_current_episode = 0
              rl_start_time = time.time()
              
              # Initialize fresh metrics for Q-Learning
              rl_metrics = {}
              for combo in rl_training_combinations:
                combo_key = f"{combo['scenario']}_{combo['intensity']}"
                rl_metrics[combo_key] = {'success': 0, 'errors': [], 'steps': [], 'energy': [], 'episodes': 0}
              
              print(f"   🎯 Q-Learning will now train through all {len(rl_training_combinations)} combinations")
              print(f"   📊 Estimated additional time: ~{(rl_num_episodes * len(rl_training_combinations) * 0.5 / 60):.1f} minutes")
              
            elif rl_current_algorithm == "Q-Learning" and not rl_algorithm_comparison['DQN']['completed']:
              print(f"\n🔄 AUTOMATIC ALGORITHM SWITCH: Q-Learning → DQN")
              print(f"   ✅ Q-Learning completed all {len(rl_training_combinations)} combinations")
              print(f"   🚀 Automatically starting DQN training...")
              
              # Switch to DQN
              rl_agent = rl_agent_dqn
              rl_current_algorithm = "DQN"
              
              # Reset training state for second algorithm
              rl_current_combination_idx = 0
              rl_current_episode = 0
              rl_start_time = time.time()
              
              # Initialize fresh metrics for DQN
              rl_metrics = {}
              for combo in rl_training_combinations:
                combo_key = f"{combo['scenario']}_{combo['intensity']}"
                rl_metrics[combo_key] = {'success': 0, 'errors': [], 'steps': [], 'energy': [], 'episodes': 0}
              
              print(f"   🎯 DQN will now train through all {len(rl_training_combinations)} combinations")
              print(f"   📊 Estimated additional time: ~{(rl_num_episodes * len(rl_training_combinations) * 0.5 / 60):.1f} minutes")
              
            else:
              # Both algorithms completed - final completion
              print(f"\n🎉 BOTH ALGORITHMS TRAINING COMPLETE! 🎉")
              print(f"   ✅ DQN: {len(rl_training_combinations)} combinations completed")
              print(f"   ✅ Q-Learning: {len(rl_training_combinations)} combinations completed")
              print(f"   📊 Total episodes: {rl_num_episodes * len(rl_training_combinations) * 2}")
              
              # Disable training mode
              rl_training_mode = False
              rl_sequential_training_status['both_completed'] = True
              print("🎓 RL Training Mode AUTO-DISABLED (both algorithms complete)\n")
          else:
            # Single algorithm mode - disable training
            rl_training_mode = False
            print("🎓 RL Training Mode AUTO-DISABLED (all combinations complete)\n")
  
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
  # Show training status occasionally (simplified)
  if int(t * 60) % 600 == 0:  # Every 10 seconds
    if rl_training_mode:
      print("🤖 RL Training Active - Learning trajectory following...")
    elif autonomous_mode:
      print("🔄 Autonomous Mode - Following circular path...")
    else:
      print("⏸️  Manual Mode - Robot idle")
  
  if autonomous_mode and not rl_training_mode and not rl_execution_mode:
    robot_pos, robot_orn = p.getBasePositionAndOrientation(husky)
    # Debug: This should NOT print during RL training
    if int(t * 60) % 300 == 0:  # Every 5 seconds
      print(f"🔄 DEBUG: Autonomous navigation active (condition satisfied)")
    
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
    max_stable_accel = 12.0   # m/s² - significantly above gravity indicates disturbance  
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
    
    # Double-check: Only calculate wheel velocities if truly in autonomous mode
    if not rl_training_mode and not rl_execution_mode:
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

  # Apply autonomous wheel control (RL system handles its own wheel control in the environment)
  if autonomous_mode and not rl_training_mode and not rl_execution_mode:
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
  
  # === VISUAL STATUS OVERLAY ON SIMULATION SCREEN ===
  # Add text overlays to show training status (with error handling)
  try:
    # Update every frame for immediate response to mode changes
    if True:
      # Determine current mode and status
      if rl_training_mode:
        status_text = "RL TRAINING ACTIVE"
        status_color = [0, 1, 0]  # Green
        if 'rl_current_episode' in locals() and rl_current_episode >= 0:
          episode_info = f"Episode: {rl_current_episode + 1}"
          if 'rl_step_counter' in locals():
            progress_info = f"Step: {rl_step_counter}"
          else:
            progress_info = ""
        else:
          episode_info = "Starting..."
          progress_info = ""
      elif rl_execution_mode:
        status_text = "RL EXECUTION MODE"
        status_color = [0, 0, 1]  # Blue
        episode_info = "Executing policy"
        progress_info = ""
      elif autonomous_mode:
        status_text = "AUTONOMOUS MODE"
        status_color = [1, 0.5, 0]  # Orange
        episode_info = "Circular path"
        progress_info = ""
      else:
        status_text = "MANUAL MODE"
        status_color = [0.5, 0.5, 0.5]  # Gray
        episode_info = "Press 't' to train"
        
        # Calculate trajectory accuracy for manual mode
        try:
          # Get current end-effector position
          ee_state = p.getLinkState(kukaId, kukaEndEffectorIndex)
          current_ee_pos = ee_state[0]
          
          # Calculate ideal circular trajectory position at current time
          trajectory_radius = 0.2
          ideal_pos = [
            circle_center[0] + trajectory_radius * math.cos(t),
            circle_center[1] + trajectory_radius * math.sin(t),
            0.7 + 0.1 * math.sin(t * 2)
          ]
          
          # Calculate component-wise errors (X, Y, Z)
          error_x = abs(current_ee_pos[0] - ideal_pos[0])
          error_y = abs(current_ee_pos[1] - ideal_pos[1]) 
          error_z = abs(current_ee_pos[2] - ideal_pos[2])
          
          # Calculate total 3D distance error
          distance_error = math.sqrt(
            (current_ee_pos[0] - ideal_pos[0])**2 +
            (current_ee_pos[1] - ideal_pos[1])**2 +
            (current_ee_pos[2] - ideal_pos[2])**2
          )
          
          # Calculate component-wise accuracy percentages
          max_expected_error = 0.3  # Maximum reasonable error distance
          max_expected_error_component = 0.15  # Maximum reasonable error per axis
          
          accuracy_percent = max(0, (1 - distance_error / max_expected_error) * 100)
          accuracy_x = max(0, (1 - error_x / max_expected_error_component) * 100)
          accuracy_y = max(0, (1 - error_y / max_expected_error_component) * 100)
          accuracy_z = max(0, (1 - error_z / max_expected_error_component) * 100)
          
          # Track circle completion and accuracy
          current_phase = t % (2 * math.pi)  # Current phase in the circle (0 to 2π)
          
          # Start tracking when we're at the beginning of a circle
          if not circle_completion_tracking['is_tracking'] and current_phase < 0.5:
            circle_completion_tracking['is_tracking'] = True
            circle_completion_tracking['start_phase'] = current_phase
            circle_completion_tracking['accuracy_samples'] = []
            circle_completion_tracking['error_samples'] = []
          
          # Collect samples during circle tracking
          if circle_completion_tracking['is_tracking']:
            circle_completion_tracking['accuracy_samples'].append(accuracy_percent)
            circle_completion_tracking['error_samples'].append(distance_error)
            
            # Check if we completed a full circle (phase wrapped around)
            if current_phase < 0.5 and len(circle_completion_tracking['accuracy_samples']) > 100:  # Ensure we have enough samples
              # Calculate circle completion accuracy
              avg_accuracy = sum(circle_completion_tracking['accuracy_samples']) / len(circle_completion_tracking['accuracy_samples'])
              avg_error = sum(circle_completion_tracking['error_samples']) / len(circle_completion_tracking['error_samples'])
              
              # Update tracking statistics
              circle_completion_tracking['completed_circles'] += 1
              circle_completion_tracking['last_completion_accuracy'] = avg_accuracy
              circle_completion_tracking['best_accuracy'] = max(circle_completion_tracking['best_accuracy'], avg_accuracy)
              
              # Calculate overall average accuracy
              all_circles = circle_completion_tracking['completed_circles']
              old_avg = circle_completion_tracking['average_accuracy']
              circle_completion_tracking['average_accuracy'] = ((old_avg * (all_circles - 1)) + avg_accuracy) / all_circles
              
              # Print circle completion summary
              print(f"🎯 CIRCLE COMPLETED #{circle_completion_tracking['completed_circles']}:")
              print(f"   Average Accuracy: {avg_accuracy:.1f}%")
              print(f"   Average Error: {avg_error:.3f}m")
              print(f"   Best Circle: {circle_completion_tracking['best_accuracy']:.1f}%")
              print(f"   Overall Average: {circle_completion_tracking['average_accuracy']:.1f}%")
              
              # Reset for next circle
              circle_completion_tracking['is_tracking'] = False
          
          # Store accuracy data for episode tracking
          if not autonomous_mode and not rl_training_mode:
            # Initialize episode if not already started
            if session_tracking['current_episode'] is None:
              session_tracking['current_episode'] = {
                'start_time': time.time(),
                'scenario': disturbance_manager.current_scenario,
                'direction': disturbance_manager.directional_mode,
                'intensity': disturbance_manager.intensity_mode,
                'accuracy_samples': [],
                'error_samples': [],
                'accuracy_x_samples': [],
                'accuracy_y_samples': [],
                'accuracy_z_samples': [],
                'error_x_samples': [],
                'error_y_samples': [],
                'error_z_samples': [],
                'circles_completed': 0,
                'episode_number': session_tracking['total_episodes'] + 1
              }
              session_tracking['current_scenario'] = disturbance_manager.current_scenario
              session_tracking['scenario_start_time'] = time.time()
            
            # Collect data during episode (both overall and component-wise)
            if session_tracking['current_episode'] is not None:
              session_tracking['current_episode']['accuracy_samples'].append(accuracy_percent)
              session_tracking['current_episode']['error_samples'].append(distance_error)
              session_tracking['current_episode']['accuracy_x_samples'].append(accuracy_x)
              session_tracking['current_episode']['accuracy_y_samples'].append(accuracy_y)
              session_tracking['current_episode']['accuracy_z_samples'].append(accuracy_z)
              session_tracking['current_episode']['error_x_samples'].append(error_x)
              session_tracking['current_episode']['error_y_samples'].append(error_y)
              session_tracking['current_episode']['error_z_samples'].append(error_z)
              session_tracking['current_episode']['circles_completed'] = circle_completion_tracking['completed_circles']
        except:
          pass
      
      # Clean simulation - minimal debug items to prevent warnings - DISABLED during RL training
      if not rl_training_mode and int(t * 240) % 600 == 0:  # Skip during RL to prevent GUI panel issues
        try:
          p.removeAllUserDebugItems()
          # Wait a frame before adding new items to avoid conflicts
          time.sleep(0.001)
          # Only show essential mode status
          p.addUserDebugText(status_text, textPosition=[0, 0, 2.0], textColorRGB=status_color, textSize=1.2)
          if episode_info:
            p.addUserDebugText(episode_info, textPosition=[0, 0, 1.6], textColorRGB=[0, 0, 0], textSize=0.9)
        except:
          pass
      
  except Exception as e:
    # Fail silently to avoid crashing simulation
    pass
  
  # Display autonomous status every 5 seconds (reduced console output)
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
  # Update video recorder frame and camera tracking (skip during RL training to avoid GUI issues)
  if not rl_training_mode:
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
  # Reduce trail drawing frequency to prevent debug draw warnings
  if (hasPrevPose and int(t * 240) % 12 == 0):  # Only draw trail every 0.05 seconds
    try:
      p.addUserDebugLine(prevPose, pos, [0, 0, 0.3], 1, trailDuration)
      p.addUserDebugLine(prevPose1, ls[4], [1, 0, 0], 1, trailDuration)
    except:
      pass  # Fail silently if trail drawing fails
  prevPose = pos
  prevPose1 = ls[4]
  hasPrevPose = 1
