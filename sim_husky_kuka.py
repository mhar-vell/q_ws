import pybullet as p
import time
import math
from datetime import datetime
from datetime import datetime
import pybullet_data

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

print("=== Square Path Autonomous Navigation ===")
print("Husky will travel through 4 waypoints forming a 1.5x1.5m square")
print("Manipulator trajectory will be centered in the square")
print("Press 'm' to toggle autonomous mode on/off")
print("Press 'r' to reset to waypoint 1")
print("==========================================")

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
    if ord('m') in keys:
      autonomous_mode = not autonomous_mode
      print(f"Autonomous square path mode: {'ENABLED' if autonomous_mode else 'DISABLED'}")
    if ord('r') in keys:
      current_waypoint = 0
      path_completed_laps = 0
      print("Reset to waypoint 1")

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
    
    # Simple proportional controller for navigation
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
      # Turn towards target
      turn_direction = 1 if angle_diff > 0 else -1
      for i in range(len(wheels)):
        wheelVelocities[i] = turn_direction * autonomous_speed * wheelDeltasTurn[i]
    else:
      # Move forward with steering correction
      forward_speed = autonomous_speed
      turn_correction = angle_diff * 0.3  # Gentle steering correction
      
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
  
  #p.resetBasePositionAndOrientation(kukaId,basepos,baseorn)#[0,0,0,1])
  if (useRealTimeSimulation):
    t = time.time()  #(dt, micro) = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
    #t = (dt.second/60.)*2.*math.pi
  else:
    t = t + 0.001

  if (useSimulation and useRealTimeSimulation == 0):
    p.stepSimulation()

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
