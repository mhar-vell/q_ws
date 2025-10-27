import numpy as np
import random

class MobileManipulatorEnv:
    """
    RL environment for Husky+KUKA mobile manipulator with PRECISE END-EFFECTOR CONTROL.
    
    MAIN OBJECTIVE: Execute precise end-effector movements despite disturbances 
    at the base caused by platform motion or external forces.
    
    KEY FEATURES for disturbance rejection training:
    - Enhanced reward function focused on end-effector precision under disturbances
    - Disturbance compensation bonus rewards maintaining precision despite base motion
    - Coordinated end-effector positioning actions for active disturbance compensation
    - Realistic disturbance injection (random forces, periodic impacts, continuous bias)
    - Success criteria requires sustained precision (10 consecutive precise steps)
    - Adaptive joint control based on disturbance magnitude
    
    This environment specifically trains the manipulator to:
    1. Detect base disturbances through IMU feedback
    2. Actively compensate with coordinated joint movements
    3. Maintain millimeter-level end-effector precision despite base motion
    4. Prioritize end-effector accuracy over base stability
    """
    def __init__(self, pybullet_client, husky_id, kuka_id, goal_pose):
        self.p = pybullet_client
        self.husky = husky_id
        self.kuka = kuka_id
        self.goal_pose = goal_pose  # Desired end-effector pose (x, y, z)
        self.state_dim = 14  # 3 base + 7 joints + 4 end-effector
        # ENHANCED ACTION SPACE for precise end-effector control:
        # 7 joints (+) + 7 joints (-) + 1 coordinated compensation + 3 base moves + 1 no-action
        num_kuka_joints = 7  # KUKA iiwa has 7 joints
        self.action_dim = 2 * num_kuka_joints + 1 + 3 + 1  # 14 + 1 + 3 + 1 = 19 actions
        self.disturbance_types = ['none', 'random', 'periodic', 'continuous', 'impulse']
        self.current_disturbance = 'none'
        
        # WAYPOINT TRAJECTORY TRACKING for circular path validation
        self.trajectory_radius = 0.2  # Same as main simulation
        self.trajectory_center = [0.0, 0.0]  # Will be updated dynamically
        self.trajectory_z_base = 0.7  # Base height for trajectory
        self.waypoints = []
        self.waypoint_tolerance = 0.03  # 3cm tolerance for waypoint passage
        self.current_waypoint_idx = 0
        self.waypoints_passed = []
        self.cycle_start_time = 0
        self.completed_cycles = 0
        self.cycle_accuracy_scores = []
        
        # TRAJECTORY ACCURACY TRACKING - Enhanced for episode-by-episode analysis
        self.episode_count = 0
        self.current_episode_trajectory = []  # Record actual training trajectory positions
        self.current_episode_start_time = 0
        self.ideal_trajectory_cache = {}  # Cache for ideal circular trajectory points
        self.episode_accuracy_history = []  # Store accuracy for each episode
        self.episode_statistics = {
            'distance_errors': [],
            'timing_errors': [],
            'waypoint_passage_rates': [],
            'cycle_completion_rates': [],
            'trajectory_similarity_scores': []
        }
        
        # Initialize timestep before reset
        self.timestep = 0
        self.done = False
        
        self.reset()

    def update_goal(self, new_goal_pose):
        """Update the goal pose dynamically during training"""
        self.goal_pose = new_goal_pose

    def generate_waypoints(self, center, num_waypoints=8):
        """Generate waypoints around the circular trajectory"""
        self.trajectory_center = [center[0], center[1]]
        self.waypoints = []
        
        for i in range(num_waypoints):
            angle = (2 * np.pi * i) / num_waypoints
            waypoint = [
                self.trajectory_center[0] + self.trajectory_radius * np.cos(angle),
                self.trajectory_center[1] + self.trajectory_radius * np.sin(angle),
                self.trajectory_z_base  # Fixed Z for waypoint checking
            ]
            self.waypoints.append(waypoint)
        
        self.current_waypoint_idx = 0
        self.waypoints_passed = [False] * num_waypoints
        print(f"🎯 Generated {num_waypoints} waypoints for circular trajectory validation")

    def check_waypoint_passage(self, ee_pos):
        """Check if end-effector has passed through the current waypoint"""
        if not self.waypoints or self.current_waypoint_idx >= len(self.waypoints):
            return False
            
        current_waypoint = self.waypoints[self.current_waypoint_idx]
        distance = np.linalg.norm(np.array(ee_pos) - np.array(current_waypoint))
        
        if distance < self.waypoint_tolerance:
            if not self.waypoints_passed[self.current_waypoint_idx]:
                self.waypoints_passed[self.current_waypoint_idx] = True
                print(f"✅ Waypoint {self.current_waypoint_idx + 1}/{len(self.waypoints)} passed! Distance: {distance:.3f}m")
                
                # Move to next waypoint
                self.current_waypoint_idx = (self.current_waypoint_idx + 1) % len(self.waypoints)
                
                # Check if completed full cycle
                if all(self.waypoints_passed):
                    return self.complete_cycle()
                    
        return False

    def complete_cycle(self):
        """Handle completion of a full circular trajectory cycle"""
        self.completed_cycles += 1
        accuracy = sum(self.waypoints_passed) / len(self.waypoints)
        self.cycle_accuracy_scores.append(accuracy)
        
        cycle_time = self.timestep - self.cycle_start_time
        avg_accuracy = np.mean(self.cycle_accuracy_scores)
        
        print(f"🎉 CYCLE {self.completed_cycles} COMPLETED!")
        print(f"   Accuracy: {accuracy:.1%} ({sum(self.waypoints_passed)}/{len(self.waypoints)} waypoints)")
        print(f"   Cycle time: {cycle_time} steps")
        print(f"   Average accuracy: {avg_accuracy:.1%}")
        
        # Reset for next cycle
        self.waypoints_passed = [False] * len(self.waypoints)
        self.current_waypoint_idx = 0
        self.cycle_start_time = self.timestep
        
        return True  # Cycle completed

    def generate_ideal_trajectory(self, num_points=100):
        """Generate ideal circular trajectory points for comparison"""
        if not self.waypoints:
            return []
            
        ideal_points = []
        for i in range(num_points):
            angle = (2 * np.pi * i) / num_points
            point = [
                self.trajectory_center[0] + self.trajectory_radius * np.cos(angle),
                self.trajectory_center[1] + self.trajectory_radius * np.sin(angle),
                self.trajectory_z_base
            ]
            ideal_points.append(point)
        
        return ideal_points

    def calculate_trajectory_similarity(self, actual_trajectory, ideal_trajectory):
        """Calculate similarity between actual and ideal trajectories using DTW-like comparison"""
        if not actual_trajectory or not ideal_trajectory:
            return 0.0
            
        # Extract positions only
        actual_positions = [point['position'] for point in actual_trajectory]
        
        # Find closest matches between actual and ideal points
        similarity_scores = []
        for actual_pos in actual_positions:
            min_distance = float('inf')
            for ideal_pos in ideal_trajectory:
                distance = np.linalg.norm(np.array(actual_pos) - np.array(ideal_pos))
                min_distance = min(min_distance, distance)
            
            # Convert distance to similarity score (0-1, where 1 is perfect)
            similarity = max(0, 1 - (min_distance / (self.trajectory_radius * 2)))
            similarity_scores.append(similarity)
        
        return np.mean(similarity_scores) if similarity_scores else 0.0

    def calculate_waypoint_timing_accuracy(self, trajectory):
        """Calculate how well the timing of waypoint passages matches ideal timing"""
        if not self.waypoints or not trajectory:
            return 0.0
            
        # Expected time between waypoints (assuming uniform circular motion)
        total_circumference = 2 * np.pi * self.trajectory_radius
        expected_speed = total_circumference / len(trajectory)  # Approximate speed
        expected_waypoint_interval = (total_circumference / len(self.waypoints)) / expected_speed
        
        # Find actual waypoint passage times
        waypoint_passage_times = []
        for i, waypoint in enumerate(self.waypoints):
            closest_time = None
            min_distance = float('inf')
            
            for point in trajectory:
                distance = np.linalg.norm(np.array(point['position']) - np.array(waypoint))
                if distance < min_distance:
                    min_distance = distance
                    closest_time = point['timestep']
            
            if closest_time is not None and min_distance < self.waypoint_tolerance * 2:
                waypoint_passage_times.append((i, closest_time))
        
        if len(waypoint_passage_times) < 2:
            return 0.0
        
        # Calculate timing errors between consecutive waypoint passages
        timing_errors = []
        for i in range(1, len(waypoint_passage_times)):
            actual_interval = waypoint_passage_times[i][1] - waypoint_passage_times[i-1][1]
            timing_error = abs(actual_interval - expected_waypoint_interval) / expected_waypoint_interval
            timing_errors.append(timing_error)
        
        # Convert error to accuracy (0-1, where 1 is perfect timing)
        avg_timing_error = np.mean(timing_errors) if timing_errors else 1.0
        timing_accuracy = max(0, 1 - avg_timing_error)
        
        return timing_accuracy

    def calculate_distance_accuracy(self, trajectory):
        """Calculate average distance accuracy from ideal circular path"""
        if not trajectory:
            return 0.0
            
        distance_errors = []
        for point in trajectory:
            pos = np.array(point['position'])
            # Calculate distance from trajectory center
            center_distance = np.linalg.norm(pos[:2] - np.array(self.trajectory_center))
            # Error is difference from ideal radius
            radius_error = abs(center_distance - self.trajectory_radius)
            distance_errors.append(radius_error)
        
        avg_distance_error = np.mean(distance_errors) if distance_errors else self.trajectory_radius
        # Convert to accuracy (0-1, where 1 is perfect)
        distance_accuracy = max(0, 1 - (avg_distance_error / self.trajectory_radius))
        
        return distance_accuracy

    def calculate_episode_accuracy(self):
        """Calculate comprehensive accuracy metrics for the completed episode"""
        if not self.current_episode_trajectory:
            return
            
        trajectory = self.current_episode_trajectory
        episode_num = self.episode_count
        
        # Generate ideal trajectory for comparison
        ideal_trajectory = self.generate_ideal_trajectory()
        
        # Calculate different accuracy metrics
        distance_accuracy = self.calculate_distance_accuracy(trajectory)
        timing_accuracy = self.calculate_waypoint_timing_accuracy(trajectory)
        similarity_score = self.calculate_trajectory_similarity(trajectory, ideal_trajectory)
        
        # Calculate waypoint passage rate
        waypoints_passed_count = sum(1 for wp in self.waypoints_passed) if self.waypoints_passed else 0
        waypoint_passage_rate = waypoints_passed_count / len(self.waypoints) if self.waypoints else 0.0
        
        # Calculate cycle completion rate (cycles per episode)
        episode_duration = len(trajectory)
        cycle_completion_rate = self.completed_cycles / max(1, episode_duration / 100)  # Normalize by episode length
        
        # Overall accuracy score (weighted combination)
        overall_accuracy = (
            0.3 * distance_accuracy +
            0.2 * timing_accuracy + 
            0.3 * similarity_score +
            0.2 * waypoint_passage_rate
        )
        
        # Store episode results
        episode_results = {
            'episode': episode_num,
            'overall_accuracy': overall_accuracy,
            'distance_accuracy': distance_accuracy,
            'timing_accuracy': timing_accuracy,
            'similarity_score': similarity_score,
            'waypoint_passage_rate': waypoint_passage_rate,
            'cycle_completion_rate': cycle_completion_rate,
            'trajectory_length': len(trajectory),
            'cycles_completed': self.completed_cycles
        }
        
        self.episode_accuracy_history.append(episode_results)
        
        # Update statistics
        self.episode_statistics['distance_errors'].append(1 - distance_accuracy)
        self.episode_statistics['timing_errors'].append(1 - timing_accuracy)
        self.episode_statistics['waypoint_passage_rates'].append(waypoint_passage_rate)
        self.episode_statistics['cycle_completion_rates'].append(cycle_completion_rate)
        self.episode_statistics['trajectory_similarity_scores'].append(similarity_score)
        
        # Print episode summary
        print(f"\n📈 EPISODE {episode_num} TRAJECTORY ACCURACY REPORT:")
        print(f"   Overall Accuracy: {overall_accuracy:.1%}")
        print(f"   Distance Accuracy: {distance_accuracy:.1%} (avg radius error: {(1-distance_accuracy)*self.trajectory_radius*100:.1f}cm)")
        print(f"   Timing Accuracy: {timing_accuracy:.1%}")
        print(f"   Trajectory Similarity: {similarity_score:.1%}")
        print(f"   Waypoint Passage Rate: {waypoint_passage_rate:.1%} ({waypoints_passed_count}/{len(self.waypoints) if self.waypoints else 0})")
        print(f"   Cycle Completion Rate: {cycle_completion_rate:.2f} cycles/episode")
        print(f"   Trajectory Points Recorded: {len(trajectory)}")
        
        # Print running statistics every 10 episodes
        if episode_num % 10 == 0:
            self.print_accuracy_statistics()

    def print_accuracy_statistics(self):
        """Print comprehensive accuracy statistics"""
        if not self.episode_accuracy_history:
            return
            
        recent_episodes = self.episode_accuracy_history[-10:]  # Last 10 episodes
        all_episodes = self.episode_accuracy_history
        
        print(f"\n📊 TRAJECTORY ACCURACY STATISTICS (Episodes {max(1, self.episode_count-9)}-{self.episode_count}):")
        print(f"   Recent Average Accuracy: {np.mean([ep['overall_accuracy'] for ep in recent_episodes]):.1%}")
        print(f"   All-Time Average Accuracy: {np.mean([ep['overall_accuracy'] for ep in all_episodes]):.1%}")
        print(f"   Best Episode Accuracy: {max([ep['overall_accuracy'] for ep in all_episodes]):.1%} (Episode {[ep['episode'] for ep in all_episodes if ep['overall_accuracy'] == max([e['overall_accuracy'] for e in all_episodes])][0]})")
        print(f"   Recent Distance Accuracy: {np.mean([ep['distance_accuracy'] for ep in recent_episodes]):.1%}")
        print(f"   Recent Timing Accuracy: {np.mean([ep['timing_accuracy'] for ep in recent_episodes]):.1%}")
        print(f"   Recent Similarity Score: {np.mean([ep['similarity_score'] for ep in recent_episodes]):.1%}")
        print(f"   Recent Waypoint Success: {np.mean([ep['waypoint_passage_rate'] for ep in recent_episodes]):.1%}")
        print(f"   Improvement Trend: {self.calculate_improvement_trend()}")

    def calculate_improvement_trend(self):
        """Calculate if accuracy is improving over recent episodes"""
        if len(self.episode_accuracy_history) < 6:
            return "Insufficient data"
            
        recent_half = self.episode_accuracy_history[-3:]
        earlier_half = self.episode_accuracy_history[-6:-3]
        
        recent_avg = np.mean([ep['overall_accuracy'] for ep in recent_half])
        earlier_avg = np.mean([ep['overall_accuracy'] for ep in earlier_half])
        
        improvement = recent_avg - earlier_avg
        if improvement > 0.05:
            return f"Improving (+{improvement:.1%})"
        elif improvement < -0.05:
            return f"Declining ({improvement:.1%})"
        else:
            return f"Stable ({improvement:+.1%})"

    def reset(self):
        # Calculate accuracy for the previous episode before resetting (only after first reset)
        if hasattr(self, 'episode_count') and self.episode_count > 0 and len(self.current_episode_trajectory) > 0:
            self.calculate_episode_accuracy()
        
        # Reset robot and environment to start state
        # Only reset joint positions, don't remove robots from simulation
        try:
            # Reset KUKA joints to default position
            num_joints = self.p.getNumJoints(self.kuka)
            default_positions = [0.0] * num_joints
            for i in range(num_joints):
                self.p.resetJointState(self.kuka, i, default_positions[i])
            
            # Reset Husky base velocity (don't reset position to avoid disrupting main simulation)
            self.p.resetBaseVelocity(self.husky, linearVelocity=[0, 0, 0], angularVelocity=[0, 0, 0])
            
            # Reset waypoint tracking for new episode
            self.current_waypoint_idx = 0
            if self.waypoints:
                self.waypoints_passed = [False] * len(self.waypoints)
            self.cycle_start_time = 0
        except Exception as e:
            print(f"Warning: RL reset error (non-fatal): {e}")
        
        # Start new episode tracking
        if not hasattr(self, 'episode_count'):
            self.episode_count = 0
        self.episode_count += 1
        self.current_episode_trajectory = []
        self.current_episode_start_time = self.timestep if hasattr(self, 'timestep') else 0
        self.timestep = 0
        self.done = False
        # Don't randomize disturbance on reset - keep current scenario
        return self.get_state()

    def step(self, action):
        # ENHANCED ACTION SPACE FOR PRECISE END-EFFECTOR CONTROL
        # Actions focused on compensating for base disturbances
        
        num_kuka_joints = self.p.getNumJoints(self.kuka)
        joint_states = [self.p.getJointState(self.kuka, i) for i in range(num_kuka_joints)]
        joint_positions = [js[0] for js in joint_states]
        
        # Adaptive joint deltas based on disturbance level
        base_vel = np.linalg.norm(self.p.getBaseVelocity(self.husky)[0])
        if base_vel > 0.1:  # High disturbance - larger corrections needed
            joint_delta = 0.08
        else:  # Low disturbance - fine adjustments
            joint_delta = 0.03
            
        # Action categories for disturbance compensation:
        if 0 <= action < num_kuka_joints:
            # Individual joint positive increments
            new_pos = joint_positions.copy()
            new_pos[action] += joint_delta
            self.p.setJointMotorControlArray(self.kuka, range(num_kuka_joints),
                                            self.p.POSITION_CONTROL, targetPositions=new_pos)
                                            
        elif num_kuka_joints <= action < 2 * num_kuka_joints:
            # Individual joint negative increments
            joint_idx = action - num_kuka_joints
            new_pos = joint_positions.copy()
            new_pos[joint_idx] -= joint_delta
            self.p.setJointMotorControlArray(self.kuka, range(num_kuka_joints),
                                            self.p.POSITION_CONTROL, targetPositions=new_pos)
                                            
        elif action == 2 * num_kuka_joints:
            # COORDINATED COMPENSATION: Move end-effector towards target
            # This is the key action for disturbance compensation
            ee_link = num_kuka_joints - 1
            ee_state = self.p.getLinkState(self.kuka, ee_link)
            ee_pos = ee_state[0]
            
            # Calculate direction to target
            target_direction = np.array(self.goal_pose[:3]) - np.array(ee_pos)
            if np.linalg.norm(target_direction) > 0:
                target_direction = target_direction / np.linalg.norm(target_direction)
                
                # Simple inverse kinematics approximation for compensation
                # Move joints to bring end-effector closer to target
                correction_scale = 0.02  # Small corrections for stability
                new_pos = joint_positions.copy()
                
                # Heuristic joint corrections for end-effector positioning
                # Joint 0 (base rotation) - for X-Y positioning
                if abs(target_direction[0]) > 0.1:
                    new_pos[0] += correction_scale * np.sign(target_direction[0])
                    
                # Joint 1 (shoulder) - for Z positioning and reach
                if target_direction[2] > 0.1:  # Need to reach higher
                    new_pos[1] -= correction_scale
                elif target_direction[2] < -0.1:  # Need to reach lower
                    new_pos[1] += correction_scale
                    
                # Joint 2 (elbow) - for reach extension/retraction
                reach_error = np.linalg.norm(target_direction[:2])
                if reach_error > 0.1:
                    new_pos[2] += correction_scale * reach_error
                
                self.p.setJointMotorControlArray(self.kuka, range(num_kuka_joints),
                                                self.p.POSITION_CONTROL, targetPositions=new_pos)
        
        # Base movements (reduced priority - focus is on arm compensation)
        elif action == 2 * num_kuka_joints + 1:
            # Minimal base movements - only for repositioning if absolutely needed
            base_speed = 0.1  # Reduced speed to minimize disturbances
            self.p.resetBaseVelocity(self.husky, linearVelocity=[base_speed, 0, 0])
        elif action == 2 * num_kuka_joints + 2:
            # Turn left (minimal)
            self.p.resetBaseVelocity(self.husky, angularVelocity=[0, 0, 0.1])
        elif action == 2 * num_kuka_joints + 3:
            # Turn right (minimal)
            self.p.resetBaseVelocity(self.husky, angularVelocity=[0, 0, -0.1])
        else:
            # No action - sometimes the best response to disturbance is to hold position
            pass

        # Apply disturbance
        self.inject_disturbance()
        obs = self.get_state()
        
        # Record trajectory point for accuracy calculation
        try:
            ee_pos = obs[-4:-1]  # End-effector position from state
            trajectory_point = {
                'timestep': self.timestep,
                'position': ee_pos.copy(),
                'goal': self.goal_pose[:3].copy() if hasattr(self.goal_pose, '__len__') else [0, 0, 0],
                'waypoint_idx': self.current_waypoint_idx if self.waypoints else -1
            }
            self.current_episode_trajectory.append(trajectory_point)
        except Exception as e:
            print(f"Warning: Trajectory recording error: {e}")
        
        rew = self.get_reward(obs, action)
        self.timestep += 1
        done_flag = self.check_done(obs)
        return obs, rew, done_flag

    def get_state(self):
        try:
            # Extract Husky base pose
            base_pos, base_orn = self.p.getBasePositionAndOrientation(self.husky)
            base_euler = self.p.getEulerFromQuaternion(base_orn)
            base_x, base_y, base_yaw = base_pos[0], base_pos[1], base_euler[2]

            # Extract Husky base velocities
            base_lin_vel, base_ang_vel = self.p.getBaseVelocity(self.husky)

            # Extract KUKA joint positions and velocities
            joint_states = [self.p.getJointState(self.kuka, i) for i in range(self.p.getNumJoints(self.kuka))]
            joint_positions = [js[0] for js in joint_states]
            joint_velocities = [js[1] for js in joint_states]

            # Extract end-effector pose (assume last joint is end-effector)
            ee_link = self.p.getNumJoints(self.kuka) - 1
            ee_state = self.p.getLinkState(self.kuka, ee_link)
            ee_pos = ee_state[0]
            ee_orn = self.p.getEulerFromQuaternion(ee_state[1])

            # IMU/odometry data (use base linear/angular velocity)
            imu_data = list(base_lin_vel) + list(base_ang_vel)

            # Compose state vector
            obs = np.array([
                base_x, base_y, base_yaw,
                *joint_positions,
                *joint_velocities,
                *ee_pos,
                *ee_orn,
                *imu_data
            ])
            # Truncate or pad to self.state_dim
            if len(obs) > self.state_dim:
                obs = obs[:self.state_dim]
            elif len(obs) < self.state_dim:
                obs = np.pad(obs, (0, self.state_dim - len(obs)), 'constant')
        except Exception as e:
            # Return zero state if robot not available
            print(f"Warning: RL get_state error (using zero state): {e}")
            obs = np.zeros(self.state_dim)
        
        return obs

    def get_reward(self, obs, action):
        # MAIN OBJECTIVE: Precise end-effector movement despite base disturbances
        
        # End-effector error (primary objective)
        ee_pos = obs[-4:-1]  # End-effector position
        ee_error = np.linalg.norm(ee_pos - self.goal_pose[:3])
        
        # WAYPOINT TRAJECTORY TRACKING REWARD
        waypoint_reward = 0.0
        trajectory_progress_reward = 0.0
        
        if self.waypoints:
            # Check waypoint passage and give completion reward
            cycle_completed = self.check_waypoint_passage(ee_pos)
            if cycle_completed:
                waypoint_reward = 50.0  # Large reward for completing full cycle
                
            # Trajectory progress reward - reward for being close to current waypoint
            if self.current_waypoint_idx < len(self.waypoints):
                current_waypoint = self.waypoints[self.current_waypoint_idx]
                waypoint_distance = np.linalg.norm(np.array(ee_pos) - np.array(current_waypoint))
                trajectory_progress_reward = -5.0 * waypoint_distance  # Reward proximity to next waypoint
        
        # Base disturbance detection (linear and angular velocities)
        base_lin_vel = obs[-6:-3]  # Base linear velocity from IMU
        base_ang_vel = obs[-3:]    # Base angular velocity from IMU
        base_disturbance = np.linalg.norm(base_lin_vel) + np.linalg.norm(base_ang_vel)
        
        # Core reward: End-effector precision reward
        precision_reward = -10.0 * ee_error  # High weight for precision
        
        # Disturbance compensation reward: Better reward when maintaining precision despite disturbances
        if base_disturbance > 0.1:  # If base is disturbed
            if ee_error < 0.05:  # But end-effector stays precise (5cm tolerance)
                disturbance_compensation_bonus = 5.0  # Large bonus for maintaining precision
            elif ee_error < 0.1:   # Moderate precision under disturbance
                disturbance_compensation_bonus = 2.0
            else:
                disturbance_compensation_bonus = 0.0  # No bonus if precision lost
        else:
            disturbance_compensation_bonus = 0.0
        
        # Stability bonus: Reward smooth joint movements (avoid jerky corrections)
        if hasattr(self, 'prev_joint_pos'):
            joint_positions = obs[3:10]  # KUKA joint positions (7 joints)
            joint_velocity = np.linalg.norm(np.array(joint_positions) - np.array(self.prev_joint_pos))
            smoothness_reward = -0.5 * joint_velocity  # Penalize large joint movements
        else:
            smoothness_reward = 0.0
        self.prev_joint_pos = obs[3:10]  # Store for next step
        
        # Success bonus for reaching target precisely
        success_bonus = 0.0
        if ee_error < 0.01:  # 1cm precision
            success_bonus = 10.0
        elif ee_error < 0.02:  # 2cm precision
            success_bonus = 5.0
        elif ee_error < 0.05:  # 5cm moderate progress
            success_bonus = 2.0
        
        # Total reward focused on PRECISE END-EFFECTOR CONTROL DESPITE DISTURBANCES
        rew = precision_reward + disturbance_compensation_bonus + smoothness_reward + success_bonus + waypoint_reward + trajectory_progress_reward
        
        return rew

    def check_done(self, obs):
        # Success criteria focused on PRECISE END-EFFECTOR POSITIONING and TRAJECTORY COMPLETION
        ee_pos = obs[-4:-1]
        ee_error = np.linalg.norm(ee_pos - self.goal_pose[:3])
        
        # Success if maintaining precision for multiple timesteps
        if not hasattr(self, 'precision_counter'):
            self.precision_counter = 0
            
        if ee_error < 0.02:  # 2cm tolerance (realistic for mobile manipulation)
            self.precision_counter += 1
        else:
            self.precision_counter = 0
            
        # Enhanced success criteria: precision AND trajectory progress
        precision_success = self.precision_counter >= 10
        
        # Additional success: completing a full cycle with high accuracy
        cycle_success = False
        if self.completed_cycles > 0 and self.cycle_accuracy_scores:
            recent_accuracy = self.cycle_accuracy_scores[-1] if self.cycle_accuracy_scores else 0
            cycle_success = recent_accuracy >= 0.8  # 80% waypoint accuracy
            
        return precision_success or cycle_success

    def inject_disturbance(self):
        # REALISTIC DISTURBANCES for testing precise end-effector control
        # These simulate real-world challenges: platform motion, external forces, etc.
        
        if self.current_disturbance == 'random':
            # Continuous random disturbances (simulating uneven terrain, wind, etc.)
            force = [random.uniform(-30, 30), random.uniform(-30, 30), 0]
            torque = [0, 0, random.uniform(-10, 10)]  # Random turning torque
            self.p.applyExternalForce(self.husky, -1, force, [0, 0, 0], self.p.WORLD_FRAME)
            self.p.applyExternalTorque(self.husky, -1, torque, self.p.WORLD_FRAME)
            
        elif self.current_disturbance == 'periodic':
            # Periodic impacts (simulating regular bumps, vibrations)
            if self.timestep % 30 == 0:  # More frequent for better training
                force = [random.choice([-80, 80]), random.choice([-80, 80]), 0]
                self.p.applyExternalForce(self.husky, -1, force, [0, 0, 0], self.p.WORLD_FRAME)
                
        elif self.current_disturbance == 'continuous':
            # Persistent bias forces (simulating slopes, constant wind)
            force = [random.uniform(-15, 15), random.uniform(-15, 15), 0]
            self.p.applyExternalForce(self.husky, -1, force, [0, 0, 0], self.p.WORLD_FRAME)
            
        elif self.current_disturbance == 'impulse':
            # Single strong impulse to test recovery
            if self.timestep == 25:
                force = [random.choice([-200, 200]), random.choice([-200, 200]), 0]
                self.p.applyExternalForce(self.husky, -1, force, [0, 0, 0], self.p.WORLD_FRAME)
        # else: no disturbance

    def get_accuracy_summary(self):
        """Get comprehensive accuracy summary for external reporting"""
        if not self.episode_accuracy_history:
            return {
                'total_episodes': 0,
                'current_accuracy': 0.0,
                'average_accuracy': 0.0,
                'best_accuracy': 0.0,
                'accuracy_trend': 'No data',
                'recent_stats': {}
            }
        
        recent_episodes = self.episode_accuracy_history[-10:] if len(self.episode_accuracy_history) >= 10 else self.episode_accuracy_history
        all_episodes = self.episode_accuracy_history
        
        return {
            'total_episodes': len(all_episodes),
            'current_accuracy': all_episodes[-1]['overall_accuracy'] if all_episodes else 0.0,
            'average_accuracy': np.mean([ep['overall_accuracy'] for ep in all_episodes]),
            'best_accuracy': max([ep['overall_accuracy'] for ep in all_episodes]),
            'best_episode': [ep['episode'] for ep in all_episodes if ep['overall_accuracy'] == max([e['overall_accuracy'] for e in all_episodes])][0],
            'accuracy_trend': self.calculate_improvement_trend(),
            'recent_stats': {
                'distance_accuracy': np.mean([ep['distance_accuracy'] for ep in recent_episodes]),
                'timing_accuracy': np.mean([ep['timing_accuracy'] for ep in recent_episodes]),
                'similarity_score': np.mean([ep['similarity_score'] for ep in recent_episodes]),
                'waypoint_success_rate': np.mean([ep['waypoint_passage_rate'] for ep in recent_episodes]),
                'average_trajectory_length': np.mean([ep['trajectory_length'] for ep in recent_episodes]),
                'total_cycles_completed': sum([ep['cycles_completed'] for ep in recent_episodes])
            }
        }

class QLearningAgent:
    """
    Tabular Q-Learning Agent for discrete state-action spaces.
    Best for: Small state spaces, interpretable learning, fast updates.
    Limitations: Doesn't scale well to high-dimensional continuous states.
    """
    def __init__(self, state_dim, action_dim, alpha=0.1, gamma=0.99, epsilon=0.2):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.q_table = dict()  # {(state_tuple): [q_values]}
        self.agent_type = "Q-Learning"

    def discretize(self, obs):
        # Discretize state for tabular Q-learning (round to 2 decimals)
        return tuple(np.round(obs, 2))

    def select_action(self, obs):
        s = self.discretize(obs)
        if s not in self.q_table:
            self.q_table[s] = np.zeros(self.action_dim)
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        return int(np.argmax(self.q_table[s]))

    def update(self, obs, action, rew, next_obs):
        s = self.discretize(obs)
        ns = self.discretize(next_obs)
        if s not in self.q_table:
            self.q_table[s] = np.zeros(self.action_dim)
        if ns not in self.q_table:
            self.q_table[ns] = np.zeros(self.action_dim)
        best_next = np.max(self.q_table[ns])
        td_target = rew + self.gamma * best_next
        td_error = td_target - self.q_table[s][action]
        self.q_table[s][action] += self.alpha * td_error
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, filepath):
        import pickle
        with open(filepath + '_qtable.pkl', 'wb') as f:
            pickle.dump(self.q_table, f)
        print(f"Q-table saved to {filepath}_qtable.pkl (size: {len(self.q_table)} states)")

    def load(self, filepath):
        import pickle
        with open(filepath + '_qtable.pkl', 'rb') as f:
            self.q_table = pickle.load(f)
        print(f"Q-table loaded from {filepath}_qtable.pkl (size: {len(self.q_table)} states)")


class DQNAgent:
    """
    Deep Q-Network Agent using neural network function approximation.
    Best for: High-dimensional continuous states, complex environments, generalization.
    Requires: PyTorch or TensorFlow.
    """
    def __init__(self, state_dim, action_dim, alpha=0.001, gamma=0.99, epsilon=1.0):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.alpha = alpha  # learning rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.agent_type = "DQN"
        
        # Try to import PyTorch
        try:
            import torch
            import torch.nn as nn
            import torch.optim as optim
            self.torch = torch
            self.nn = nn
            self.optim = optim
            self.use_dqn = True
        except ImportError:
            print("⚠️  PyTorch not available. Falling back to tabular Q-learning.")
            self.use_dqn = False
            # Fallback to tabular Q-learning
            self.q_table = dict()
            return
        
        # Neural network for Q-value approximation
        class QNetwork(nn.Module):
            def __init__(self, state_dim, action_dim):
                super(QNetwork, self).__init__()
                self.fc1 = nn.Linear(state_dim, 128)
                self.fc2 = nn.Linear(128, 128)
                self.fc3 = nn.Linear(128, action_dim)
            
            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                return self.fc3(x)
        
        # Device selection: CUDA (NVIDIA) > MPS (Apple) > CPU
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")
        
        print(f"🔧 DQN Agent using device: {self.device}")
        
        self.q_network = QNetwork(state_dim, action_dim).to(self.device)
        self.target_network = QNetwork(state_dim, action_dim).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=alpha)
        self.loss_fn = nn.MSELoss()
        
        # Experience replay buffer
        self.memory = []
        self.memory_size = 10000
        self.batch_size = 32
        self.update_target_every = 100
        self.updates = 0

    def select_action(self, obs):
        if not self.use_dqn:
            # Fallback to tabular Q-learning
            s = tuple(np.round(obs, 2))
            if s not in self.q_table:
                self.q_table[s] = np.zeros(self.action_dim)
            if random.random() < self.epsilon:
                return random.randint(0, self.action_dim - 1)
            return int(np.argmax(self.q_table[s]))
        
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        
        with self.torch.no_grad():
            state_tensor = self.torch.FloatTensor(obs).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            return int(q_values.argmax().item())

    def update(self, obs, action, rew, next_obs):
        if not self.use_dqn:
            # Fallback to tabular Q-learning
            s = tuple(np.round(obs, 2))
            ns = tuple(np.round(next_obs, 2))
            if s not in self.q_table:
                self.q_table[s] = np.zeros(self.action_dim)
            if ns not in self.q_table:
                self.q_table[ns] = np.zeros(self.action_dim)
            best_next = np.max(self.q_table[ns])
            td_target = rew + self.gamma * best_next
            td_error = td_target - self.q_table[s][action]
            self.q_table[s][action] += self.alpha * td_error
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            return
        
        # Store experience in replay buffer
        self.memory.append((obs, action, rew, next_obs))
        if len(self.memory) > self.memory_size:
            self.memory.pop(0)
        
        # Train on batch if enough samples
        if len(self.memory) < self.batch_size:
            return
        
        # Sample random batch
        batch = random.sample(self.memory, self.batch_size)
        
        # Convert to numpy arrays first (much faster than list of arrays)
        states = np.array([e[0] for e in batch], dtype=np.float32)
        actions = np.array([e[1] for e in batch], dtype=np.int64)
        rewards = np.array([e[2] for e in batch], dtype=np.float32)
        next_states = np.array([e[3] for e in batch], dtype=np.float32)
        
        # Now convert to tensors (fast!)
        states = self.torch.from_numpy(states).to(self.device)
        actions = self.torch.from_numpy(actions).to(self.device)
        rewards = self.torch.from_numpy(rewards).to(self.device)
        next_states = self.torch.from_numpy(next_states).to(self.device)
        
        # Compute Q(s,a)
        q_values = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Compute target: r + gamma * max_a' Q_target(s',a')
        with self.torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            targets = rewards + self.gamma * next_q_values
        
        # Update network
        loss = self.loss_fn(q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update target network periodically
        self.updates += 1
        if self.updates % self.update_target_every == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, filepath):
        if not self.use_dqn:
            import pickle
            with open(filepath + '_qtable.pkl', 'wb') as f:
                pickle.dump(self.q_table, f)
            print(f"Q-table saved to {filepath}_qtable.pkl")
            return
        
        self.torch.save({
            'q_network': self.q_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, filepath + '_dqn.pth')
        print(f"DQN model saved to {filepath}_dqn.pth")

    def load(self, filepath):
        if not self.use_dqn:
            import pickle
            with open(filepath + '_qtable.pkl', 'rb') as f:
                self.q_table = pickle.load(f)
            print(f"Q-table loaded from {filepath}_qtable.pkl")
            return
        
        checkpoint = self.torch.load(filepath + '_dqn.pth')
        self.q_network.load_state_dict(checkpoint['q_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint['epsilon']
        print(f"DQN model loaded from {filepath}_dqn.pth")

# Example training loop
if __name__ == "__main__":
    # ...initialize PyBullet, Husky, KUKA, goal_pose...
    env = MobileManipulatorEnv(pybullet_client=None, husky_id=0, kuka_id=1, goal_pose=np.array([1.0, 0.0, 0.5, 0.0]))
    agent = QLearningAgent(state_dim=env.state_dim, action_dim=env.action_dim)
    num_episodes = 1000
    for ep in range(num_episodes):
        state = env.reset()
        for t in range(200):
            action = agent.select_action(state)
            next_state, reward, done = env.step(action)
            agent.update(state, action, reward, next_state)
            state = next_state
            if done:
                print(f"Episode {ep} success at step {t}, final error: {np.linalg.norm(state[-4:-1] - env.goal_pose[:3]):.3f}")
                break
    print("Training complete.")
