import pybullet as p
import time
import math
from datetime import datetime
import pybullet_data
import numpy as np
import random

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

clid = p.connect(p.SHARED_MEMORY)


if (clid < 0):
  p.connect(p.GUI)

p.setPhysicsEngineParameter(enableConeFriction=0)

p.setAdditionalSearchPath(pybullet_data.getDataPath())


p.loadURDF("plane.urdf", [0, 0, -0.3])
husky = p.loadURDF("husky/husky.urdf", [0.290388, 0.329902, -0.310270],
                   [0.002328, -0.000984, 0.996491, 0.083659])
for i in range(p.getNumJoints(husky)):
  print(p.getJointInfo(husky, i))
kukaId = p.loadURDF("kuka_iiwa/model_free_base.urdf", 0.193749, 0.345564, 0.120208, 0.002327,
                    -0.000988, 0.996491, 0.083659)
ob = kukaId
jointPositions = [3.559609, 0.411182, 0.862129, 1.744441, 0.077299, -1.129685, 0.006001]
for jointIndex in range(p.getNumJoints(ob)):
  p.resetJointState(ob, jointIndex, jointPositions[jointIndex])

#put kuka on top of husky

cid = p.createConstraint(husky, -1, kukaId, -1, p.JOINT_FIXED, [0, 0, 0], [0, 0, 0], [0., 0., -.5],
                         [0, 0, 0, 1])

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

p.setGravity(0, 0, -10)
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
    jointPoses = p.calculateInverseKinematics(kukaId, kukaEndEffectorIndex, targetPos)
    for i in range(numJoints):
      p.resetJointState(kukaId, i, jointPoses[i])
    ls = p.getLinkState(kukaId, kukaEndEffectorIndex)
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
print("  Arrow keys - Manual control (when autonomous off)")
print("")
print("IMU FEATURES:")
print("  - Accelerometer with realistic noise and bias")
print("  - Gyroscope with drift simulation") 
print("  - Automatic disturbance rejection using IMU feedback")
print("  - Periodic terrain disturbances for testing")
print("=============================================================")

while 1:
  # === IMU SENSOR UPDATES ===
  # Read IMU data from both sensors every frame for real-time feedback
  husky_imu_data = husky_imu.read_imu()
  kuka_imu_data = kuka_imu.read_imu()
  
  # Increment frame counter for periodic logging
  imu_frame_counter += 1
  
  # Log IMU data periodically (every 1 second)
  if imu_frame_counter % imu_log_interval == 0:
    print(f"\n=== IMU DATA UPDATE (Frame {imu_frame_counter}) ===")
    print("HUSKY BASE IMU:")
    husky_imu.print_imu_status(husky_imu_data)
    print("\nKUKA ARM IMU (Link 6):")
    kuka_imu.print_imu_status(kuka_imu_data)
    print("=" * 50)
  
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

  # Autonomous circular path navigation
  if autonomous_mode:
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
    p.setJointMotorControl2(husky,
                            wheels[i],
                            p.VELOCITY_CONTROL,
                            targetVelocity=wheelVelocities[i],
                            force=1000)
  
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
  
  #p.resetBasePositionAndOrientation(kukaId,basepos,baseorn)#[0,0,0,1])
  if (useRealTimeSimulation):
    t = time.time()  #(dt, micro) = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
    #t = (dt.second/60.)*2.*math.pi
  else:
    t = t + 0.001

  if (useSimulation and useRealTimeSimulation == 0):
    p.stepSimulation()
  
  # === AUTOMATIC TERRAIN DISTURBANCES (IMU Testing) ===
  # Apply periodic disturbances to test IMU response and control stability
  if autonomous_mode and (imu_frame_counter % 400 == 0):  # Every ~6.7 seconds at 60fps
    # Random terrain-like disturbances
    terrain_force = [
        random.uniform(-20, 20),   # X-axis push/pull
        random.uniform(-20, 20),   # Y-axis push/pull  
        random.uniform(-5, 5)      # Small vertical bump
    ]
    terrain_torque = [
        random.uniform(-5, 5),     # Roll disturbance
        random.uniform(-5, 5),     # Pitch disturbance 
        random.uniform(-3, 3)      # Yaw disturbance
    ]
    
    p.applyExternalForce(husky, -1, terrain_force, [0, 0, 0], p.WORLD_FRAME)
    p.applyExternalTorque(husky, -1, terrain_torque, p.WORLD_FRAME)
    
    print(f"Applied terrain disturbance: F={terrain_force}, T={terrain_torque}")

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
        p.setJointMotorControl2(bodyIndex=kukaId,
                                jointIndex=i,
                                controlMode=p.POSITION_CONTROL,
                                targetPosition=jointPoses[i],
                                targetVelocity=0,
                                force=500,
                                positionGain=1,
                                velocityGain=0.1)
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
