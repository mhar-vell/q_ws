"""
Reinforcement Learning-based Trajectory Planner for Husky-KUKA System
Implements Q-learning and DQN for adaptive end-effector trajectory control
with disturbance rejection and precision optimization.
"""

import numpy as np
import random
import pickle
import time
import math
from collections import deque
from datetime import datetime
import pybullet as p
import matplotlib.pyplot as plt

# Deep Learning imports (optional - will use Q-table if not available)
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    print("PyTorch not available. Using tabular Q-learning.")
    TORCH_AVAILABLE = False

class TrajectoryEnvironment:
    """
    Environment for RL-based trajectory planning with Husky-KUKA system.
    Handles state representation, action space, rewards, and physics simulation.
    """
    
    def __init__(self, robot_id, manipulator_id, target_trajectory, dt=0.01):
        """
        Initialize trajectory planning environment.
        
        Args:
            robot_id: PyBullet ID for Husky base
            manipulator_id: PyBullet ID for KUKA arm
            target_trajectory: List of target end-effector poses [(x,y,z,rx,ry,rz), ...]
            dt: Control timestep
        """
        self.robot_id = robot_id
        self.manipulator_id = manipulator_id
        self.target_trajectory = np.array(target_trajectory)
        self.dt = dt
        
        # Environment parameters
        self.num_joints = 7  # KUKA iiwa 7-DoF
        self.ee_link = 6     # End-effector link index
        
        # State space dimensions
        self.joint_pos_dim = self.num_joints      # Joint positions
        self.joint_vel_dim = self.num_joints      # Joint velocities  
        self.ee_pose_dim = 6                      # End-effector pose (x,y,z,rx,ry,rz)
        self.base_state_dim = 6                   # Base pose and velocities
        self.imu_dim = 6                          # IMU accel + gyro
        self.trajectory_dim = 3                   # Trajectory progress info
        
        self.state_dim = (self.joint_pos_dim + self.joint_vel_dim + 
                         self.ee_pose_dim + self.base_state_dim + 
                         self.imu_dim + self.trajectory_dim)
        
        # Action space - discrete joint movements
        self.action_dim = self.num_joints
        self.actions_per_joint = 5  # [-2, -1, 0, +1, +2] * scale
        self.action_scale = 0.05    # Radians per action step
        self.total_actions = self.actions_per_joint ** self.num_joints
        
        # Episode parameters
        self.max_episode_steps = 1000
        self.current_step = 0
        self.trajectory_index = 0
        
        # Performance tracking
        self.ee_error_history = []
        self.reward_history = []
        self.disturbance_active = False
        
        # Inverse kinematics solver
        self.ik_solver = InverseKinematicsSolver(self.manipulator_id, self.ee_link)
        
        print(f"Trajectory Environment initialized:")
        print(f"  State dimension: {self.state_dim}")
        print(f"  Action space: {self.action_dim} joints × {self.actions_per_joint} levels")
        print(f"  Target trajectory: {len(self.target_trajectory)} waypoints")
        
    def reset(self):
        """Reset environment to initial state."""
        self.current_step = 0
        self.trajectory_index = 0
        self.ee_error_history.clear()
        self.reward_history.clear()
        self.disturbance_active = False
        
        # Reset robot to initial pose
        self._reset_robot_pose()
        
        # Get initial state
        state = self._get_state()
        return state
    
    def step(self, action):
        """
        Execute action and return next state, reward, done, info.
        
        Args:
            action: Action index or joint angle deltas
            
        Returns:
            tuple: (next_state, reward, done, info)
        """
        # Convert action to joint commands
        joint_deltas = self._action_to_joint_deltas(action)
        
        # Apply action to robot
        self._execute_joint_action(joint_deltas)
        
        # Step simulation
        p.stepSimulation()
        
        # Get new state
        next_state = self._get_state()
        
        # Calculate reward
        reward = self._calculate_reward()
        
        # Check if episode is done
        done = self._check_done()
        
        # Update episode info
        self.current_step += 1
        
        # Performance metrics
        ee_pos, _ = self._get_ee_pose()
        target_pos = self._get_current_target()[:3]
        ee_error = np.linalg.norm(ee_pos - target_pos)
        self.ee_error_history.append(ee_error)
        self.reward_history.append(reward)
        
        info = {
            'ee_error': ee_error,
            'trajectory_progress': self.trajectory_index / len(self.target_trajectory),
            'step': self.current_step,
            'disturbance_active': self.disturbance_active
        }
        
        return next_state, reward, done, info
    
    def _get_state(self):
        """Get current environment state vector."""
        # Joint positions and velocities
        joint_positions = []
        joint_velocities = []
        
        for i in range(self.num_joints):
            joint_state = p.getJointState(self.manipulator_id, i)
            joint_positions.append(joint_state[0])  # Position
            joint_velocities.append(joint_state[1]) # Velocity
        
        # End-effector pose
        ee_pos, ee_orn = self._get_ee_pose()
        ee_euler = p.getEulerFromQuaternion(ee_orn)
        
        # Base state (position, orientation, velocities)
        base_pos, base_orn = p.getBasePositionAndOrientation(self.robot_id)
        base_lin_vel, base_ang_vel = p.getBaseVelocity(self.robot_id)
        base_euler = p.getEulerFromQuaternion(base_orn)
        
        # IMU simulation (simplified)
        # In practice, use the VirtualIMU class from the main simulation
        accel = np.array(base_lin_vel) * 10 + np.random.normal(0, 0.1, 3)  # Approximate
        gyro = np.array(base_ang_vel) + np.random.normal(0, 0.01, 3)
        
        # Trajectory progress information
        target_pos = self._get_current_target()[:3]
        trajectory_progress = self.trajectory_index / len(self.target_trajectory)
        distance_to_target = np.linalg.norm(ee_pos - target_pos)
        
        # Combine all state components
        state = np.concatenate([
            joint_positions,           # Joint positions (7)
            joint_velocities,          # Joint velocities (7) 
            ee_pos,                    # EE position (3)
            ee_euler,                  # EE orientation (3)
            base_pos,                  # Base position (3)
            base_euler,                # Base orientation (3)
            accel,                     # IMU acceleration (3)
            gyro,                      # IMU gyroscope (3)
            [trajectory_progress, distance_to_target, self.current_step/self.max_episode_steps]  # Progress (3)
        ])
        
        return state.astype(np.float32)
    
    def _action_to_joint_deltas(self, action):
        """Convert action index to joint angle deltas."""
        if isinstance(action, (int, np.integer)):
            # Discrete action space - convert index to joint deltas
            joint_deltas = []
            action_remaining = action
            
            for i in range(self.num_joints):
                joint_action = action_remaining % self.actions_per_joint
                action_remaining //= self.actions_per_joint
                
                # Convert to delta (-2, -1, 0, +1, +2) * scale
                delta = (joint_action - 2) * self.action_scale
                joint_deltas.append(delta)
            
            return np.array(joint_deltas)
        else:
            # Continuous action space
            return np.array(action) * self.action_scale
    
    def _execute_joint_action(self, joint_deltas):
        """Execute joint movements with safety limits."""
        # Get current joint positions
        current_positions = []
        for i in range(self.num_joints):
            joint_state = p.getJointState(self.manipulator_id, i)
            current_positions.append(joint_state[0])
        
        # Apply deltas with limits
        target_positions = []
        for i, delta in enumerate(joint_deltas):
            new_pos = current_positions[i] + delta
            
            # Joint limits (approximate for KUKA iiwa)
            joint_limits = [
                (-2.97, 2.97),   # Joint 1
                (-2.09, 2.09),   # Joint 2  
                (-2.97, 2.97),   # Joint 3
                (-2.09, 2.09),   # Joint 4
                (-2.97, 2.97),   # Joint 5
                (-2.09, 2.09),   # Joint 6
                (-3.05, 3.05)    # Joint 7
            ]
            
            min_limit, max_limit = joint_limits[i]
            new_pos = np.clip(new_pos, min_limit, max_limit)
            target_positions.append(new_pos)
        
        # Send joint commands
        for i, target_pos in enumerate(target_positions):
            p.setJointMotorControl2(
                self.manipulator_id, i,
                p.POSITION_CONTROL,
                targetPosition=target_pos,
                force=500
            )
    
    def _calculate_reward(self):
        """Calculate reward based on trajectory tracking performance."""
        # Get current end-effector pose
        ee_pos, ee_orn = self._get_ee_pose()
        
        # Get target pose
        target_pose = self._get_current_target()
        target_pos = target_pose[:3]
        target_orn_euler = target_pose[3:6] if len(target_pose) > 3 else [0, 0, 0]
        
        # Position error
        pos_error = np.linalg.norm(ee_pos - target_pos)
        pos_reward = -pos_error * 10  # Penalty for position error
        
        # Orientation error (simplified)
        ee_euler = p.getEulerFromQuaternion(ee_orn)
        orn_error = np.linalg.norm(np.array(ee_euler) - np.array(target_orn_euler))
        orn_reward = -orn_error * 2  # Penalty for orientation error
        
        # Smoothness reward (penalize large joint velocities)
        joint_velocities = []
        for i in range(self.num_joints):
            joint_state = p.getJointState(self.manipulator_id, i)
            joint_velocities.append(joint_state[1])
        
        smoothness_penalty = -np.sum(np.abs(joint_velocities)) * 0.1
        
        # Stability reward (penalize excessive base motion during disturbances)
        base_lin_vel, base_ang_vel = p.getBaseVelocity(self.robot_id)
        stability_penalty = -(np.linalg.norm(base_lin_vel) + np.linalg.norm(base_ang_vel)) * 0.5
        
        # Trajectory progress reward
        progress_reward = 0
        if pos_error < 0.05:  # Within 5cm of target
            progress_reward = 10
            self._advance_trajectory()
        
        # Energy efficiency (penalize large joint movements)
        joint_positions = []
        for i in range(self.num_joints):
            joint_state = p.getJointState(self.manipulator_id, i)
            joint_positions.append(joint_state[0])
        
        if hasattr(self, '_prev_joint_positions'):
            joint_movement = np.sum(np.abs(np.array(joint_positions) - self._prev_joint_positions))
            energy_penalty = -joint_movement * 0.5
        else:
            energy_penalty = 0
        
        self._prev_joint_positions = np.array(joint_positions)
        
        # Combine rewards
        total_reward = (pos_reward + orn_reward + smoothness_penalty + 
                       stability_penalty + progress_reward + energy_penalty)
        
        # Bonus for completing trajectory
        if self.trajectory_index >= len(self.target_trajectory):
            total_reward += 100
        
        return total_reward
    
    def _get_ee_pose(self):
        """Get end-effector pose (position and orientation)."""
        link_state = p.getLinkState(self.manipulator_id, self.ee_link)
        ee_pos = np.array(link_state[0])
        ee_orn = np.array(link_state[1])
        return ee_pos, ee_orn
    
    def _get_current_target(self):
        """Get current target pose from trajectory."""
        if self.trajectory_index < len(self.target_trajectory):
            return self.target_trajectory[self.trajectory_index]
        else:
            return self.target_trajectory[-1]  # Stay at final target
    
    def _advance_trajectory(self):
        """Move to next waypoint in trajectory."""
        if self.trajectory_index < len(self.target_trajectory) - 1:
            self.trajectory_index += 1
            print(f"Advanced to trajectory waypoint {self.trajectory_index + 1}/{len(self.target_trajectory)}")
    
    def _check_done(self):
        """Check if episode should end."""
        # Episode ends if max steps reached or trajectory completed
        return (self.current_step >= self.max_episode_steps or 
                self.trajectory_index >= len(self.target_trajectory))
    
    def _reset_robot_pose(self):
        """Reset robot to initial pose."""
        # Reset KUKA arm to neutral position
        initial_joint_positions = [0, 0, 0, -1.5, 0, 1.8, 0]
        for i, pos in enumerate(initial_joint_positions):
            p.resetJointState(self.manipulator_id, i, pos)
    
    def apply_disturbance(self, force_range=(-20, 20), torque_range=(-5, 5)):
        """Apply random disturbance to base platform."""
        force = [random.uniform(*force_range), random.uniform(*force_range), 0]
        torque = [0, 0, random.uniform(*torque_range)]
        
        p.applyExternalForce(self.robot_id, -1, force, [0, 0, 0], p.WORLD_FRAME)
        p.applyExternalTorque(self.robot_id, -1, torque, p.WORLD_FRAME)
        
        self.disturbance_active = True
        print(f"Applied disturbance: Force={force}, Torque={torque}")


class InverseKinematicsSolver:
    """
    Inverse kinematics solver using Jacobian-based methods
    for KUKA iiwa 7-DoF manipulator.
    """
    
    def __init__(self, robot_id, ee_link, max_iterations=100, tolerance=1e-4):
        self.robot_id = robot_id
        self.ee_link = ee_link
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.num_joints = 7
    
    def solve_ik(self, target_pos, target_orn=None, current_joints=None):
        """
        Solve inverse kinematics for target end-effector pose.
        
        Args:
            target_pos: Target position [x, y, z]
            target_orn: Target orientation quaternion (optional)
            current_joints: Current joint positions (optional)
            
        Returns:
            np.array: Joint positions or None if no solution found
        """
        if target_orn is None:
            target_orn = [0, 0, 0, 1]  # Default orientation
        
        # Use PyBullet's built-in IK solver as baseline
        joint_positions = p.calculateInverseKinematics(
            self.robot_id,
            self.ee_link,
            target_pos,
            target_orn,
            maxNumIterations=self.max_iterations,
            residualThreshold=self.tolerance
        )
        
        return np.array(joint_positions[:self.num_joints])
    
    def jacobian_ik(self, target_pos, target_orn=None, current_joints=None, alpha=0.1):
        """
        Jacobian-based inverse kinematics solver.
        
        Args:
            target_pos: Target position [x, y, z]
            target_orn: Target orientation quaternion (optional)
            current_joints: Current joint positions (optional)
            alpha: Learning rate for iterative solution
            
        Returns:
            np.array: Joint positions or None if no solution found
        """
        if current_joints is None:
            # Get current joint positions
            current_joints = []
            for i in range(self.num_joints):
                joint_state = p.getJointState(self.robot_id, i)
                current_joints.append(joint_state[0])
            current_joints = np.array(current_joints)
        
        joints = current_joints.copy()
        
        for iteration in range(self.max_iterations):
            # Get current end-effector position
            link_state = p.getLinkState(self.robot_id, self.ee_link)
            current_pos = np.array(link_state[0])
            
            # Position error
            pos_error = np.array(target_pos) - current_pos
            
            if np.linalg.norm(pos_error) < self.tolerance:
                return joints  # Solution found
            
            # Calculate Jacobian matrix
            jacobian = self._calculate_jacobian(joints)
            
            # Jacobian pseudo-inverse
            jacobian_pinv = np.linalg.pinv(jacobian)
            
            # Update joint positions
            joint_deltas = jacobian_pinv @ pos_error
            joints += alpha * joint_deltas
            
            # Apply joint limits
            joints = self._apply_joint_limits(joints)
            
            # Update robot joints for next iteration
            for i, joint_pos in enumerate(joints):
                p.resetJointState(self.robot_id, i, joint_pos)
        
        print(f"IK solver: Max iterations reached. Final error: {np.linalg.norm(pos_error):.4f}")
        return joints
    
    def _calculate_jacobian(self, joint_positions):
        """Calculate Jacobian matrix numerically."""
        jacobian = np.zeros((3, self.num_joints))
        epsilon = 1e-6
        
        # Get current end-effector position
        for i in range(self.num_joints):
            p.resetJointState(self.robot_id, i, joint_positions[i])
        
        link_state = p.getLinkState(self.robot_id, self.ee_link)
        pos_base = np.array(link_state[0])
        
        # Numerical differentiation for each joint
        for j in range(self.num_joints):
            # Perturb joint j
            joint_positions[j] += epsilon
            p.resetJointState(self.robot_id, j, joint_positions[j])
            
            # Get new position
            link_state = p.getLinkState(self.robot_id, self.ee_link)
            pos_perturbed = np.array(link_state[0])
            
            # Calculate partial derivative
            jacobian[:, j] = (pos_perturbed - pos_base) / epsilon
            
            # Reset joint
            joint_positions[j] -= epsilon
            p.resetJointState(self.robot_id, j, joint_positions[j])
        
        return jacobian
    
    def _apply_joint_limits(self, joints):
        """Apply joint limits to prevent invalid configurations."""
        # KUKA iiwa joint limits (approximate)
        joint_limits = [
            (-2.97, 2.97),   # Joint 1
            (-2.09, 2.09),   # Joint 2
            (-2.97, 2.97),   # Joint 3
            (-2.09, 2.09),   # Joint 4
            (-2.97, 2.97),   # Joint 5
            (-2.09, 2.09),   # Joint 6
            (-3.05, 3.05)    # Joint 7
        ]
        
        for i, (min_limit, max_limit) in enumerate(joint_limits):
            joints[i] = np.clip(joints[i], min_limit, max_limit)
        
        return joints


class QLearningAgent:
    """
    Tabular Q-learning agent for discrete action spaces.
    Uses state discretization for continuous state spaces.
    """
    
    def __init__(self, state_dim, action_dim, learning_rate=0.1, 
                 discount_factor=0.95, epsilon=1.0, epsilon_decay=0.995, 
                 epsilon_min=0.01):
        """
        Initialize Q-learning agent.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Number of discrete actions
            learning_rate: Learning rate for Q-table updates
            discount_factor: Discount factor for future rewards
            epsilon: Initial exploration rate
            epsilon_decay: Decay rate for exploration
            epsilon_min: Minimum exploration rate
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Q-table (will be populated as states are encountered)
        self.q_table = {}
        
        # State discretization parameters
        self.state_bins = 10  # Number of bins per state dimension
        self.state_ranges = None  # Will be set during training
        
        print(f"Q-Learning Agent initialized:")
        print(f"  State dim: {state_dim}, Action dim: {action_dim}")
        print(f"  Learning rate: {learning_rate}, Discount: {discount_factor}")
        print(f"  Exploration: ε={epsilon} → {epsilon_min} (decay={epsilon_decay})")
    
    def discretize_state(self, state):
        """Convert continuous state to discrete state key."""
        if self.state_ranges is None:
            # Initialize state ranges based on first observation
            self.state_ranges = [(state[i] - 1, state[i] + 1) for i in range(len(state))]
        
        discrete_state = []
        for i, value in enumerate(state):
            min_val, max_val = self.state_ranges[i]
            
            # Update ranges if necessary
            if value < min_val:
                self.state_ranges[i] = (value, max_val)
                min_val = value
            elif value > max_val:
                self.state_ranges[i] = (min_val, value)
                max_val = value
            
            # Discretize
            if max_val != min_val:
                bin_idx = int((value - min_val) / (max_val - min_val) * (self.state_bins - 1))
                bin_idx = max(0, min(bin_idx, self.state_bins - 1))
            else:
                bin_idx = 0
            
            discrete_state.append(bin_idx)
        
        return tuple(discrete_state)
    
    def get_q_value(self, state, action):
        """Get Q-value for state-action pair."""
        discrete_state = self.discretize_state(state)
        if discrete_state not in self.q_table:
            self.q_table[discrete_state] = np.zeros(self.action_dim)
        return self.q_table[discrete_state][action]
    
    def set_q_value(self, state, action, value):
        """Set Q-value for state-action pair."""
        discrete_state = self.discretize_state(state)
        if discrete_state not in self.q_table:
            self.q_table[discrete_state] = np.zeros(self.action_dim)
        self.q_table[discrete_state][action] = value
    
    def choose_action(self, state):
        """Choose action using ε-greedy policy."""
        if random.random() < self.epsilon:
            # Explore: random action
            return random.randint(0, self.action_dim - 1)
        else:
            # Exploit: best known action
            discrete_state = self.discretize_state(state)
            if discrete_state not in self.q_table:
                return random.randint(0, self.action_dim - 1)
            
            q_values = self.q_table[discrete_state]
            return np.argmax(q_values)
    
    def update(self, state, action, reward, next_state, done):
        """Update Q-table using Q-learning update rule."""
        current_q = self.get_q_value(state, action)
        
        if done:
            target_q = reward
        else:
            # Find best action in next state
            next_discrete_state = self.discretize_state(next_state)
            if next_discrete_state in self.q_table:
                max_next_q = np.max(self.q_table[next_discrete_state])
            else:
                max_next_q = 0
            
            target_q = reward + self.discount_factor * max_next_q
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (target_q - current_q)
        self.set_q_value(state, action, new_q)
        
        # Decay exploration rate
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def save_model(self, filepath):
        """Save Q-table to file."""
        model_data = {
            'q_table': self.q_table,
            'state_ranges': self.state_ranges,
            'epsilon': self.epsilon
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Q-learning model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load Q-table from file."""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.q_table = model_data['q_table']
            self.state_ranges = model_data['state_ranges']
            self.epsilon = model_data.get('epsilon', self.epsilon_min)
            
            print(f"Q-learning model loaded from {filepath}")
            print(f"Q-table size: {len(self.q_table)} states")
        except FileNotFoundError:
            print(f"Model file {filepath} not found. Starting with empty Q-table.")


class DQNAgent:
    """
    Deep Q-Network agent for continuous state spaces.
    Uses neural networks to approximate Q-values.
    """
    
    def __init__(self, state_dim, action_dim, learning_rate=0.001,
                 discount_factor=0.95, epsilon=1.0, epsilon_decay=0.995,
                 epsilon_min=0.01, memory_size=10000, batch_size=32):
        """Initialize DQN agent."""
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for DQN agent")
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        
        # Neural networks
        self.q_network = DQNNetwork(state_dim, action_dim)
        self.target_network = DQNNetwork(state_dim, action_dim)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Experience replay buffer
        self.memory = deque(maxlen=memory_size)
        
        # Training parameters
        self.target_update_freq = 100
        self.update_count = 0
        
        print(f"DQN Agent initialized:")
        print(f"  Network: {state_dim} → hidden → {action_dim}")
        print(f"  Memory size: {memory_size}, Batch size: {batch_size}")
        print(f"  Target update frequency: {self.target_update_freq}")
    
    def choose_action(self, state):
        """Choose action using ε-greedy policy with neural network."""
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            q_values = self.q_network(state_tensor)
        
        return q_values.argmax().item()
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer."""
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self):
        """Train network on batch of experiences."""
        if len(self.memory) < self.batch_size:
            return
        
        # Sample batch
        batch = random.sample(self.memory, self.batch_size)
        states = torch.FloatTensor([e[0] for e in batch])
        actions = torch.LongTensor([e[1] for e in batch])
        rewards = torch.FloatTensor([e[2] for e in batch])
        next_states = torch.FloatTensor([e[3] for e in batch])
        dones = torch.BoolTensor([e[4] for e in batch])
        
        # Current Q-values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Next Q-values from target network
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (self.discount_factor * next_q_values * ~dones)
        
        # Loss and optimization
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update target network
        self.update_count += 1
        if self.update_count % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Decay exploration
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss.item()
    
    def update(self, state, action, reward, next_state, done):
        """Store experience and train if enough samples available."""
        self.remember(state, action, reward, next_state, done)
        loss = self.replay()
        return loss
    
    def save_model(self, filepath):
        """Save neural network model."""
        torch.save({
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, filepath)
        print(f"DQN model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load neural network model."""
        try:
            checkpoint = torch.load(filepath)
            self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
            self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.epsilon = checkpoint.get('epsilon', self.epsilon_min)
            print(f"DQN model loaded from {filepath}")
        except FileNotFoundError:
            print(f"Model file {filepath} not found. Starting with random weights.")


class DQNNetwork(nn.Module):
    """Neural network for Deep Q-Learning."""
    
    def __init__(self, state_dim, action_dim, hidden_dims=[256, 256]):
        super(DQNNetwork, self).__init__()
        
        layers = []
        input_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            input_dim = hidden_dim
        
        layers.append(nn.Linear(input_dim, action_dim))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)


class TrajectoryPlanner:
    """
    Main trajectory planner class that coordinates RL training and execution.
    """
    
    def __init__(self, robot_id, manipulator_id, use_dqn=True):
        """
        Initialize trajectory planner.
        
        Args:
            robot_id: PyBullet ID for Husky base
            manipulator_id: PyBullet ID for KUKA arm
            use_dqn: Whether to use DQN (True) or tabular Q-learning (False)
        """
        self.robot_id = robot_id
        self.manipulator_id = manipulator_id
        self.use_dqn = use_dqn and TORCH_AVAILABLE
        
        # Create sample trajectory (figure-8 pattern)
        self.target_trajectory = self._generate_sample_trajectory()
        
        # Initialize environment
        self.env = TrajectoryEnvironment(
            robot_id, manipulator_id, self.target_trajectory
        )
        
        # Initialize RL agent
        if self.use_dqn:
            self.agent = DQNAgent(
                state_dim=self.env.state_dim,
                action_dim=self.env.total_actions
            )
        else:
            self.agent = QLearningAgent(
                state_dim=self.env.state_dim,
                action_dim=self.env.total_actions
            )
        
        # Performance tracking
        self.training_rewards = []
        self.training_errors = []
        self.episode_count = 0
        
        print(f"Trajectory Planner initialized:")
        print(f"  Agent type: {'DQN' if self.use_dqn else 'Q-Learning'}")
        print(f"  Trajectory waypoints: {len(self.target_trajectory)}")
    
    def _generate_sample_trajectory(self):
        """Generate a sample trajectory for testing."""
        # Figure-8 pattern above the robot
        trajectory = []
        num_points = 20
        
        for i in range(num_points):
            t = 2 * np.pi * i / num_points
            
            # Figure-8 parametric equations
            x = 0.3 * np.sin(t)
            y = 0.2 * np.sin(2 * t)
            z = 0.8  # Fixed height
            
            # Simple orientation (pointing down)
            rx, ry, rz = 0, 0, 0
            
            trajectory.append([x, y, z, rx, ry, rz])
        
        return trajectory
    
    def train(self, num_episodes=1000, save_freq=100, apply_disturbances=True):
        """
        Train the RL agent on trajectory following task.
        
        Args:
            num_episodes: Number of training episodes
            save_freq: Frequency to save models and plots
            apply_disturbances: Whether to apply random disturbances
        """
        print(f"Starting training for {num_episodes} episodes...")
        
        for episode in range(num_episodes):
            state = self.env.reset()
            episode_reward = 0
            episode_errors = []
            
            while True:
                # Choose action
                action = self.agent.choose_action(state)
                
                # Execute action
                next_state, reward, done, info = self.env.step(action)
                
                # Update agent
                if self.use_dqn:
                    loss = self.agent.update(state, action, reward, next_state, done)
                else:
                    self.agent.update(state, action, reward, next_state, done)
                
                episode_reward += reward
                episode_errors.append(info['ee_error'])
                
                # Apply random disturbances during training
                if apply_disturbances and random.random() < 0.05:  # 5% chance per step
                    self.env.apply_disturbance()
                
                state = next_state
                
                if done:
                    break
            
            # Record performance
            self.training_rewards.append(episode_reward)
            self.training_errors.append(np.mean(episode_errors))
            self.episode_count += 1
            
            # Progress reporting
            if episode % 50 == 0:
                avg_reward = np.mean(self.training_rewards[-50:])
                avg_error = np.mean(self.training_errors[-50:])
                epsilon = getattr(self.agent, 'epsilon', 0)
                
                print(f"Episode {episode}: Avg Reward={avg_reward:.2f}, "
                      f"Avg Error={avg_error:.4f}m, ε={epsilon:.3f}")
            
            # Save model and plots
            if episode % save_freq == 0 and episode > 0:
                self.save_model(f"trajectory_planner_ep{episode}")
                self.plot_training_progress()
        
        print("Training completed!")
        return self.training_rewards, self.training_errors
    
    def execute_trajectory(self, trajectory=None, max_steps=1000):
        """
        Execute learned trajectory following policy.
        
        Args:
            trajectory: Custom trajectory to follow (uses default if None)
            max_steps: Maximum execution steps
            
        Returns:
            dict: Execution metrics
        """
        if trajectory is not None:
            self.env.target_trajectory = np.array(trajectory)
        
        # Reset environment
        state = self.env.reset()
        
        # Set agent to exploitation mode
        original_epsilon = getattr(self.agent, 'epsilon', 0)
        if hasattr(self.agent, 'epsilon'):
            self.agent.epsilon = 0  # No exploration during execution
        
        execution_data = {
            'ee_positions': [],
            'target_positions': [],
            'errors': [],
            'rewards': [],
            'joint_positions': [],
            'disturbances': []
        }
        
        step = 0
        while step < max_steps:
            # Record data
            ee_pos, _ = self.env._get_ee_pose()
            target_pos = self.env._get_current_target()[:3]
            
            execution_data['ee_positions'].append(ee_pos.copy())
            execution_data['target_positions'].append(target_pos.copy())
            execution_data['errors'].append(np.linalg.norm(ee_pos - target_pos))
            
            # Choose action
            action = self.agent.choose_action(state)
            
            # Execute action
            next_state, reward, done, info = self.env.step(action)
            
            execution_data['rewards'].append(reward)
            execution_data['disturbances'].append(info['disturbance_active'])
            
            # Record joint positions
            joint_positions = []
            for i in range(self.env.num_joints):
                joint_state = p.getJointState(self.manipulator_id, i)
                joint_positions.append(joint_state[0])
            execution_data['joint_positions'].append(joint_positions)
            
            state = next_state
            step += 1
            
            if done:
                break
        
        # Restore original epsilon
        if hasattr(self.agent, 'epsilon'):
            self.agent.epsilon = original_epsilon
        
        # Calculate metrics
        errors = np.array(execution_data['errors'])
        metrics = {
            'mean_error': np.mean(errors),
            'max_error': np.max(errors),
            'final_error': errors[-1] if len(errors) > 0 else float('inf'),
            'completion_rate': self.env.trajectory_index / len(self.env.target_trajectory),
            'total_reward': sum(execution_data['rewards']),
            'steps': step
        }
        
        print(f"Trajectory execution completed:")
        print(f"  Mean error: {metrics['mean_error']:.4f}m")
        print(f"  Max error: {metrics['max_error']:.4f}m")
        print(f"  Completion: {metrics['completion_rate']:.1%}")
        print(f"  Total reward: {metrics['total_reward']:.1f}")
        
        return metrics, execution_data
    
    def plot_training_progress(self, save_path="training_progress.png"):
        """Plot training progress."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Rewards plot
        ax1.plot(self.training_rewards)
        ax1.set_title('Training Rewards')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Total Reward')
        ax1.grid(True)
        
        # Errors plot
        ax2.plot(self.training_errors)
        ax2.set_title('End-Effector Errors')
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Average Error (m)')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path)
        print(f"Training progress plot saved to {save_path}")
    
    def plot_trajectory_execution(self, execution_data, save_path="trajectory_execution.png"):
        """Plot trajectory execution results."""
        fig = plt.figure(figsize=(15, 10))
        
        # 3D trajectory plot
        ax1 = fig.add_subplot(2, 3, 1, projection='3d')
        
        ee_positions = np.array(execution_data['ee_positions'])
        target_positions = np.array(execution_data['target_positions'])
        
        ax1.plot(target_positions[:, 0], target_positions[:, 1], target_positions[:, 2], 
                'r-', label='Target Trajectory', linewidth=2)
        ax1.plot(ee_positions[:, 0], ee_positions[:, 1], ee_positions[:, 2], 
                'b-', label='Actual Trajectory', linewidth=2)
        
        ax1.set_xlabel('X (m)')
        ax1.set_ylabel('Y (m)')
        ax1.set_zlabel('Z (m)')
        ax1.set_title('3D Trajectory Comparison')
        ax1.legend()
        
        # Error plot
        ax2 = fig.add_subplot(2, 3, 2)
        ax2.plot(execution_data['errors'])
        ax2.set_title('End-Effector Tracking Error')
        ax2.set_xlabel('Step')
        ax2.set_ylabel('Error (m)')
        ax2.grid(True)
        
        # Rewards plot
        ax3 = fig.add_subplot(2, 3, 3)
        ax3.plot(execution_data['rewards'])
        ax3.set_title('Step Rewards')
        ax3.set_xlabel('Step')
        ax3.set_ylabel('Reward')
        ax3.grid(True)
        
        # Joint positions
        ax4 = fig.add_subplot(2, 3, 4)
        joint_positions = np.array(execution_data['joint_positions'])
        for i in range(min(7, joint_positions.shape[1])):
            ax4.plot(joint_positions[:, i], label=f'Joint {i+1}')
        ax4.set_title('Joint Positions')
        ax4.set_xlabel('Step')
        ax4.set_ylabel('Position (rad)')
        ax4.legend()
        ax4.grid(True)
        
        # XY trajectory view
        ax5 = fig.add_subplot(2, 3, 5)
        ax5.plot(target_positions[:, 0], target_positions[:, 1], 'r-', label='Target', linewidth=2)
        ax5.plot(ee_positions[:, 0], ee_positions[:, 1], 'b-', label='Actual', linewidth=2)
        ax5.set_xlabel('X (m)')
        ax5.set_ylabel('Y (m)')
        ax5.set_title('XY Trajectory View')
        ax5.legend()
        ax5.grid(True)
        ax5.axis('equal')
        
        # Disturbances
        ax6 = fig.add_subplot(2, 3, 6)
        disturbances = np.array(execution_data['disturbances'], dtype=int)
        ax6.plot(disturbances, 'r-', linewidth=2)
        ax6.set_title('Disturbances Applied')
        ax6.set_xlabel('Step')
        ax6.set_ylabel('Disturbance Active')
        ax6.grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Trajectory execution plot saved to {save_path}")
    
    def save_model(self, filename):
        """Save trained model."""
        filepath = f"{filename}.pkl" if not self.use_dqn else f"{filename}.pth"
        self.agent.save_model(filepath)
    
    def load_model(self, filename):
        """Load trained model."""
        filepath = f"{filename}.pkl" if not self.use_dqn else f"{filename}.pth"
        self.agent.load_model(filepath)
    
    def test_disturbance_rejection(self, num_tests=10):
        """
        Test the planner's ability to reject disturbances.
        
        Args:
            num_tests: Number of disturbance tests to run
            
        Returns:
            dict: Disturbance rejection metrics
        """
        print(f"Testing disturbance rejection with {num_tests} tests...")
        
        recovery_times = []
        max_errors = []
        
        for test in range(num_tests):
            # Execute trajectory until halfway point
            state = self.env.reset()
            steps_to_disturbance = len(self.env.target_trajectory) // 2
            
            # Execute without disturbance
            for step in range(steps_to_disturbance):
                action = self.agent.choose_action(state)
                state, _, done, _ = self.env.step(action)
                if done:
                    break
            
            # Apply strong disturbance
            self.env.apply_disturbance(force_range=(-50, 50), torque_range=(-15, 15))
            
            # Monitor recovery
            errors_after_disturbance = []
            recovery_step = None
            
            for step in range(100):  # Monitor for 100 steps
                action = self.agent.choose_action(state)
                state, _, done, info = self.env.step(action)
                
                error = info['ee_error']
                errors_after_disturbance.append(error)
                
                # Consider recovered if error < 5cm for 10 consecutive steps
                if len(errors_after_disturbance) >= 10:
                    if all(e < 0.05 for e in errors_after_disturbance[-10:]):
                        if recovery_step is None:
                            recovery_step = step - 9  # First step of recovery
                        break
                
                if done:
                    break
            
            if recovery_step is not None:
                recovery_times.append(recovery_step)
            else:
                recovery_times.append(100)  # Max time if not recovered
            
            max_errors.append(max(errors_after_disturbance))
        
        metrics = {
            'mean_recovery_time': np.mean(recovery_times),
            'max_recovery_time': np.max(recovery_times),
            'mean_max_error': np.mean(max_errors),
            'recovery_rate': sum(1 for t in recovery_times if t < 100) / num_tests
        }
        
        print(f"Disturbance rejection test results:")
        print(f"  Mean recovery time: {metrics['mean_recovery_time']:.1f} steps")
        print(f"  Recovery rate: {metrics['recovery_rate']:.1%}")
        print(f"  Mean max error: {metrics['mean_max_error']:.4f}m")
        
        return metrics


# Example usage and integration function
def integrate_with_husky_simulation(husky_id, kuka_id):
    """
    Integrate RL trajectory planner with existing Husky-KUKA simulation.
    
    Args:
        husky_id: PyBullet ID for Husky robot
        kuka_id: PyBullet ID for KUKA manipulator
        
    Returns:
        TrajectoryPlanner: Initialized trajectory planner
    """
    print("Integrating RL trajectory planner with Husky-KUKA simulation...")
    
    # Initialize trajectory planner
    planner = TrajectoryPlanner(husky_id, kuka_id, use_dqn=True)
    
    # Try to load existing model
    planner.load_model("husky_kuka_trajectory_planner")
    
    print("RL Trajectory Planner integration complete!")
    print("Available methods:")
    print("  planner.train(num_episodes=500)           # Train the agent")
    print("  planner.execute_trajectory()              # Execute learned policy")
    print("  planner.test_disturbance_rejection()      # Test robustness")
    print("  planner.save_model('my_model')            # Save trained model")
    
    return planner


if __name__ == "__main__":
    print("RL Trajectory Planner for Husky-KUKA System")
    print("This module provides reinforcement learning-based trajectory planning")
    print("with disturbance rejection and precision optimization.")
    print("\nTo use with your simulation:")
    print("  from rl_trajectory_planner import integrate_with_husky_simulation")
    print("  planner = integrate_with_husky_simulation(husky_id, kuka_id)")