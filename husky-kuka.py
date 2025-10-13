import pybullet as p
import time
import math
import random
import numpy as np
from datetime import datetime
from datetime import datetime 
import pybullet_data

clid = p.connect(p.SHARED_MEMORY)


if (clid < 0):
  p.connect(p.GUI)

p.setPhysicsEngineParameter(enableConeFriction=0)
# Improve simulation stability
p.setPhysicsEngineParameter(numSolverIterations=50)
p.setPhysicsEngineParameter(fixedTimeStep=1./240.)
p.setPhysicsEngineParameter(numSubSteps=1)
p.setPhysicsEngineParameter(contactBreakingThreshold=0.001)

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

# Perturbation parameters
enable_perturbations = False      # Start with perturbations disabled
perturbation_magnitude_pos = 0.005 # Much smaller perturbations
perturbation_magnitude_ang = 0.01  # Much smaller angular perturbations  
perturbation_frequency = 0.01      # Much lower frequency
base_damping = 1.5                # Higher damping for more stability
angular_damping = 1.5             # Higher angular damping

# Autonomous movement parameters
autonomous_mode = False           # Start in manual mode for stability
autonomous_speed = 0.2            # Reduced base speed for smoother movements
movement_change_frequency = 0.005 # Much lower frequency - change less often
current_movement_pattern = 0      # Current movement pattern (0-4)
movement_duration = 0             # How long to maintain current movement
max_movement_duration = 600       # Longer duration for each movement pattern
movement_patterns = [
    "stop",           # 0: No movement
    "forward",        # 1: Move forward
    "backward",       # 2: Move backward  
    "turn_left",      # 3: Turn left
    "turn_right",     # 4: Turn right
    "circle_left",    # 5: Move in left circle
    "circle_right",   # 6: Move in right circle
    "figure_eight"    # 7: Figure-8 pattern
]
figure_eight_phase = 0            # Phase for figure-8 movement

# IMU sensor parameters
enable_imu = True                 # Enable IMU sensor readings
imu_noise_level = 0.005          # Reduced noise level
imu_sample_rate = 240            # IMU sample rate (Hz) - matches simulation rate
previous_velocity = [0, 0, 0]    # Previous velocity for acceleration calculation
previous_angular_velocity = [0, 0, 0]  # Previous angular velocity
imu_data_history = []            # Store recent IMU readings for filtering
max_imu_history = 10             # Number of recent readings to store
show_imu_data = False            # Toggle IMU data display

# Add damping to the base to prevent excessive oscillations
p.changeDynamics(husky, -1, linearDamping=base_damping, angularDamping=angular_damping)
perturbation_magnitude_pos = 0.02  # Maximum position perturbation (meters)
perturbation_magnitude_ang = 0.05  # Maximum angular perturbation (radians)
perturbation_frequency = 0.1       # Probability of perturbation per timestep (0-1)
base_perturbation = [0, 0, 0]     # Current base position perturbation
ang_perturbation = 0              # Current angular perturbation


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

print("=== Controls ===")
print("m: Toggle Autonomous/Manual mode")
print("Arrow keys: Move Husky (Manual mode only)")
print("a/d: Move target left/right")
print("s: Save world state")
print("p: Toggle perturbations on/off")
print("1/2: Decrease/increase perturbation frequency")
print("3/4: Decrease/increase force perturbation magnitude")
print("5/6: Decrease/increase torque perturbation magnitude")
print("7/8: Decrease/increase base damping")
print("9/0: Decrease/increase autonomous speed")
print("i: Toggle IMU data display")
print("u: Toggle IMU sensor on/off")
print("================")
print(f"Starting in {'AUTONOMOUS' if autonomous_mode else 'MANUAL'} mode")
print(f"Perturbations: {'ENABLED' if enable_perturbations else 'DISABLED (press p to enable)'}")
print(f"IMU sensor: {'ENABLED' if enable_imu else 'DISABLED'}")
if enable_imu:
  print(f"IMU sample rate: {imu_sample_rate} Hz, Noise level: {imu_noise_level}")
print("Tip: Press 'm' to toggle autonomous mode, 'p' to enable gentle perturbations")
print("Autonomous movement patterns:", ", ".join(movement_patterns))
print("================")

while 1:
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
    
    # Mode and perturbation controls
    if ord('m') in keys:
      autonomous_mode = not autonomous_mode
      print(f"Switched to {'AUTONOMOUS' if autonomous_mode else 'MANUAL'} mode")
      if not autonomous_mode:
        wheelVelocities = [0, 0, 0, 0]  # Stop when switching to manual
    if ord('p') in keys:
      enable_perturbations = not enable_perturbations
      print(f"Perturbations {'enabled' if enable_perturbations else 'disabled'}")
    if ord('1') in keys:
      perturbation_frequency = max(0.01, perturbation_frequency - 0.01)
      print(f"Perturbation frequency: {perturbation_frequency:.2f}")
    if ord('2') in keys:
      perturbation_frequency = min(1.0, perturbation_frequency + 0.01)
      print(f"Perturbation frequency: {perturbation_frequency:.2f}")
    if ord('3') in keys:
      perturbation_magnitude_pos = max(0.001, perturbation_magnitude_pos - 0.005)
      print(f"Position perturbation magnitude: {perturbation_magnitude_pos:.3f}")
    if ord('4') in keys:
      perturbation_magnitude_pos = min(0.1, perturbation_magnitude_pos + 0.005)
      print(f"Position perturbation magnitude: {perturbation_magnitude_pos:.3f}")
    if ord('5') in keys:
      perturbation_magnitude_ang = max(0.01, perturbation_magnitude_ang - 0.01)
      print(f"Angular perturbation magnitude: {perturbation_magnitude_ang:.3f}")
    if ord('6') in keys:
      perturbation_magnitude_ang = min(0.2, perturbation_magnitude_ang + 0.01)
      print(f"Angular perturbation magnitude: {perturbation_magnitude_ang:.3f}")
    if ord('7') in keys:
      base_damping = max(0.1, base_damping - 0.1)
      angular_damping = max(0.1, angular_damping - 0.1)
      p.changeDynamics(husky, -1, linearDamping=base_damping, angularDamping=angular_damping)
      print(f"Damping decreased: linear={base_damping:.1f}, angular={angular_damping:.1f}")
    if ord('8') in keys:
      base_damping = min(2.0, base_damping + 0.1)
      angular_damping = min(2.0, angular_damping + 0.1)
      p.changeDynamics(husky, -1, linearDamping=base_damping, angularDamping=angular_damping)
      print(f"Damping increased: linear={base_damping:.1f}, angular={angular_damping:.1f}")
    if ord('9') in keys:
      autonomous_speed = max(0.1, autonomous_speed - 0.1)
      print(f"Autonomous speed: {autonomous_speed:.1f}")
    if ord('0') in keys:
      autonomous_speed = min(2.0, autonomous_speed + 0.1)
      print(f"Autonomous speed: {autonomous_speed:.1f}")
    if ord('i') in keys:
      show_imu_data = not show_imu_data
      print(f"IMU data display: {'ON' if show_imu_data else 'OFF'}")
    if ord('u') in keys:
      enable_imu = not enable_imu
      print(f"IMU sensor: {'ENABLED' if enable_imu else 'DISABLED'}")

    # Manual control (only active when not in autonomous mode)
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

  # Autonomous movement logic
  if autonomous_mode:
    # Update movement duration and potentially change pattern
    movement_duration += 1
    
    # Randomly change movement pattern
    if (random.random() < movement_change_frequency or 
        movement_duration > max_movement_duration):
      current_movement_pattern = random.randint(0, len(movement_patterns) - 1)
      movement_duration = 0
      figure_eight_phase = 0  # Reset phase for figure-8
      print(f"Autonomous movement: {movement_patterns[current_movement_pattern]}")
    
    # Execute current movement pattern
    pattern = movement_patterns[current_movement_pattern]
    
    if pattern == "stop":
      wheelVelocities = [0, 0, 0, 0]
    elif pattern == "forward":
      for i in range(len(wheels)):
        wheelVelocities[i] = autonomous_speed * wheelDeltasFwd[i]
    elif pattern == "backward":
      for i in range(len(wheels)):
        wheelVelocities[i] = -autonomous_speed * wheelDeltasFwd[i]
    elif pattern == "turn_left":
      for i in range(len(wheels)):
        wheelVelocities[i] = -autonomous_speed * wheelDeltasTurn[i]
    elif pattern == "turn_right":
      for i in range(len(wheels)):
        wheelVelocities[i] = autonomous_speed * wheelDeltasTurn[i]
    elif pattern == "circle_left":
      # Gentle forward + left turn
      for i in range(len(wheels)):
        wheelVelocities[i] = autonomous_speed * (0.8 * wheelDeltasFwd[i] - 0.2 * wheelDeltasTurn[i])
    elif pattern == "circle_right":
      # Gentle forward + right turn
      for i in range(len(wheels)):
        wheelVelocities[i] = autonomous_speed * (0.8 * wheelDeltasFwd[i] + 0.2 * wheelDeltasTurn[i])
    elif pattern == "figure_eight":
      # Gentler figure-8 pattern
      figure_eight_phase += 0.01  # Slower phase change
      turn_amount = math.sin(figure_eight_phase) * 0.2  # Smaller turning radius
      for i in range(len(wheels)):
        wheelVelocities[i] = autonomous_speed * (0.8 * wheelDeltasFwd[i] + turn_amount * wheelDeltasTurn[i])

  baseorn = p.getQuaternionFromEuler([0, 0, ang])
  for i in range(len(wheels)):
    p.setJointMotorControl2(husky,
                            wheels[i],
                            p.VELOCITY_CONTROL,
                            targetVelocity=wheelVelocities[i],
                            force=1000)
  
  # IMU Sensor Reading
  if enable_imu:
    # Get current position and orientation
    current_pos, current_orn = p.getBasePositionAndOrientation(husky)
    current_vel, current_ang_vel = p.getBaseVelocity(husky)
    
    # Add realistic sensor noise
    def add_noise(value_list, noise_level):
      return [v + random.gauss(0, noise_level) for v in value_list]
    
    # Calculate acceleration (change in velocity)
    dt = 1.0 / imu_sample_rate
    linear_acceleration = [(current_vel[i] - previous_velocity[i]) / dt for i in range(3)]
    angular_acceleration = [(current_ang_vel[i] - previous_angular_velocity[i]) / dt for i in range(3)]
    
    # Add noise to simulate realistic IMU
    noisy_linear_accel = add_noise(linear_acceleration, imu_noise_level * 10)  # Accelerometer noise
    noisy_angular_vel = add_noise(current_ang_vel, imu_noise_level)           # Gyroscope noise
    noisy_orientation = add_noise(p.getEulerFromQuaternion(current_orn), imu_noise_level * 0.1)  # Magnetometer/orientation
    
    # Store IMU data
    imu_reading = {
      'timestamp': t,
      'linear_acceleration': noisy_linear_accel,
      'angular_velocity': noisy_angular_vel,
      'orientation': noisy_orientation,
      'raw_linear_accel': linear_acceleration,
      'raw_angular_vel': current_ang_vel,
      'raw_orientation': p.getEulerFromQuaternion(current_orn)
    }
    
    # Maintain IMU history for filtering
    imu_data_history.append(imu_reading)
    if len(imu_data_history) > max_imu_history:
      imu_data_history.pop(0)
    
    # Display IMU data if requested
    if show_imu_data and int(t * 60) % 180 == 0:  # Every 3 seconds
      print(f"IMU Data - Time: {t:.2f}s")
      print(f"  Linear Accel: [{noisy_linear_accel[0]:.3f}, {noisy_linear_accel[1]:.3f}, {noisy_linear_accel[2]:.3f}] m/s²")
      print(f"  Angular Vel:  [{noisy_angular_vel[0]:.3f}, {noisy_angular_vel[1]:.3f}, {noisy_angular_vel[2]:.3f}] rad/s")
      print(f"  Orientation:  [{noisy_orientation[0]:.3f}, {noisy_orientation[1]:.3f}, {noisy_orientation[2]:.3f}] rad")
      
      # Show magnitude of disturbances
      accel_magnitude = math.sqrt(sum(a*a for a in noisy_linear_accel))
      angular_magnitude = math.sqrt(sum(w*w for w in noisy_angular_vel))
      print(f"  Disturbance Magnitudes - Linear: {accel_magnitude:.3f} m/s², Angular: {angular_magnitude:.3f} rad/s")
    
    # Update previous values for next iteration
    previous_velocity = current_vel
    previous_angular_velocity = current_ang_vel
    
    # Simple disturbance detection based on IMU readings
    accel_magnitude = math.sqrt(sum(a*a for a in linear_acceleration))
    angular_magnitude = math.sqrt(sum(w*w for w in current_ang_vel))
    
    # Thresholds for disturbance detection
    accel_threshold = 2.0   # m/s²
    angular_threshold = 1.0  # rad/s
    
    if accel_magnitude > accel_threshold or angular_magnitude > angular_threshold:
      if show_imu_data:
        print(f"*** DISTURBANCE DETECTED *** Accel: {accel_magnitude:.2f}, Angular: {angular_magnitude:.2f}")
      
      # Here you could add compensation logic, such as:
      # - Adjusting manipulator control gains
      # - Triggering replanning of trajectory
      # - Activating stabilization control
      
    # Store current IMU reading in global variable for use by manipulator control
    globals()['current_imu_data'] = imu_reading
  
  # Apply random perturbations to the base using forces (smooth movement)
  if enable_perturbations and random.random() < perturbation_frequency:
    # Generate random force perturbations
    force_magnitude = perturbation_magnitude_pos * 1000  # Scale to force units
    torque_magnitude = perturbation_magnitude_ang * 100  # Scale to torque units
    
    perturbation_force = [
      random.uniform(-force_magnitude, force_magnitude),
      random.uniform(-force_magnitude, force_magnitude),
      0  # No vertical force to maintain stability
    ]
    
    perturbation_torque = [
      0,  # No roll perturbation
      0,  # No pitch perturbation
      random.uniform(-torque_magnitude, torque_magnitude)  # Only yaw perturbation
    ]
    
    # Apply external forces and torques to the base
    p.applyExternalForce(husky, -1, perturbation_force, [0, 0, 0], p.LINK_FRAME)
    p.applyExternalTorque(husky, -1, perturbation_torque, p.LINK_FRAME)
    
    print(f"Applied force perturbation: force={perturbation_force}, torque={perturbation_torque}")
  
  # Add trail visualization for the robot base (optional)
  if autonomous_mode and int(t * 60) % 10 == 0:  # Every 10 frames in autonomous mode
    base_pos, _ = p.getBasePositionAndOrientation(husky)
    if 'prev_base_pos' in globals():
      p.addUserDebugLine(prev_base_pos, base_pos, [0, 1, 0], 2, 10)  # Green trail for base
    prev_base_pos = base_pos
  
  # IMU visualization - show acceleration vectors
  if enable_imu and show_imu_data and 'current_imu_data' in globals() and int(t * 60) % 20 == 0:
    imu = globals()['current_imu_data']
    base_pos, _ = p.getBasePositionAndOrientation(husky)
    
    # Scale factors for visualization
    accel_scale = 0.1
    angular_scale = 0.05
    
    # Linear acceleration vector (red)
    accel_end = [
      base_pos[0] + imu['linear_acceleration'][0] * accel_scale,
      base_pos[1] + imu['linear_acceleration'][1] * accel_scale,
      base_pos[2] + 0.5 + imu['linear_acceleration'][2] * accel_scale
    ]
    p.addUserDebugLine(base_pos, accel_end, [1, 0, 0], 3, 1)  # Red arrow for acceleration
    
    # Angular velocity vector (blue)
    angular_end = [
      base_pos[0] + imu['angular_velocity'][0] * angular_scale,
      base_pos[1] + imu['angular_velocity'][1] * angular_scale,
      base_pos[2] + 0.8 + imu['angular_velocity'][2] * angular_scale
    ]
    p.addUserDebugLine([base_pos[0], base_pos[1], base_pos[2] + 0.3], angular_end, [0, 0, 1], 3, 1)  # Blue arrow for angular velocity
  
  #p.resetBasePositionAndOrientation(kukaId,basepos,baseorn)#[0,0,0,1])
  if (useRealTimeSimulation):
    t = time.time()  #(dt, micro) = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
    #t = (dt.second/60.)*2.*math.pi
  else:
    t = t + 0.001

  if (useSimulation and useRealTimeSimulation == 0):
    p.stepSimulation()
    
  # Display status every 300 frames (about every 5 seconds at 60fps)
  if int(t * 300) % 300 == 0 and autonomous_mode:
    print(f"Status - Mode: AUTONOMOUS, Pattern: {movement_patterns[current_movement_pattern]}, "
          f"Duration: {movement_duration}/{max_movement_duration}, Speed: {autonomous_speed:.1f}")

  for i in range(1):
    #pos = [-0.4,0.2*math.cos(t),0.+0.2*math.sin(t)]
    base_pos = [0.2 * math.cos(t), 0, 0. + 0.2 * math.sin(t) + 0.7]
    
    # IMU-based trajectory compensation (if IMU is enabled and data is available)
    if enable_imu and 'current_imu_data' in globals():
      imu = globals()['current_imu_data']
      
      # Simple predictive compensation based on base acceleration
      # Predict where the base will be in the next timestep
      compensation_factor = 0.02  # Much smaller compensation factor
      
      accel_compensation = [
        -imu['linear_acceleration'][0] * compensation_factor,
        -imu['linear_acceleration'][1] * compensation_factor,
        -imu['linear_acceleration'][2] * compensation_factor * 0.1  # Less Z compensation
      ]
      
      pos = [
        base_pos[0] + accel_compensation[0],
        base_pos[1] + accel_compensation[1], 
        base_pos[2] + accel_compensation[2]
      ]
      
      if show_imu_data and int(t * 60) % 60 == 0:  # Every second
        print(f"IMU Compensation: [{accel_compensation[0]:.4f}, {accel_compensation[1]:.4f}, {accel_compensation[2]:.4f}]")
    else:
      pos = base_pos
    
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
