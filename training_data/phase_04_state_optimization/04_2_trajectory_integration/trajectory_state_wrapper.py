"""
Phase 04.2: Trajectory Integration State Wrapper

Enhances base state (35D) with trajectory-aware features (59D total):
- Next waypoints information (18D): 3 upcoming waypoints × 6D each
- Progress metrics (6D): distance to goal, completion %, velocity alignment, etc.

This wrapper adds temporal context to help the policy anticipate trajectory requirements.
"""

import numpy as np
from collections import deque


class TrajectoryStateWrapper:
    """
    Wraps the base environment to add trajectory-aware features.
    
    State dimensions:
    - Base state: 35D (from Phase 03)
    - Next waypoints: 18D (3 waypoints × [dx, dy, dz, distance, heading, elevation])
    - Progress metrics: 6D
    Total: 59D
    """
    
    def __init__(self, base_env, trajectory_waypoints, lookahead_count=3):
        """
        Initialize trajectory wrapper.
        
        Args:
            base_env: Base RL environment (rl_mission_env.py)
            trajectory_waypoints: List of (x, y, z) waypoints for current trajectory
            lookahead_count: Number of future waypoints to include in state
        """
        self.base_env = base_env
        self.trajectory_waypoints = np.array(trajectory_waypoints)
        self.lookahead_count = lookahead_count
        
        # Track current position in trajectory
        self.current_waypoint_idx = 0
        self.total_waypoints = len(trajectory_waypoints)
        
        # History for velocity estimation
        self.ee_position_history = deque(maxlen=5)
        
        # Enhanced state dimension
        self.base_state_dim = 35  # Phase 03 state size
        self.waypoint_features_dim = 6  # Features per waypoint
        self.waypoints_dim = lookahead_count * self.waypoint_features_dim  # 18D
        self.progress_dim = 6  # Progress metrics
        self.state_dim = self.base_state_dim + self.waypoints_dim + self.progress_dim  # 59D
        
        print(f"✅ Trajectory wrapper initialized:")
        print(f"   Base state: {self.base_state_dim}D")
        print(f"   Waypoints: {self.waypoints_dim}D ({lookahead_count} × {self.waypoint_features_dim})")
        print(f"   Progress: {self.progress_dim}D")
        print(f"   Total: {self.state_dim}D")
    
    def reset(self, trajectory_waypoints=None):
        """
        Reset environment and trajectory tracking.
        
        Args:
            trajectory_waypoints: Optional new trajectory waypoints
            
        Returns:
            Enhanced state vector (59D)
        """
        # Reset base environment
        base_state = self.base_env.reset()
        
        # Update trajectory if provided
        if trajectory_waypoints is not None:
            self.trajectory_waypoints = np.array(trajectory_waypoints)
            self.total_waypoints = len(trajectory_waypoints)
        
        # Reset tracking
        self.current_waypoint_idx = 0
        self.ee_position_history.clear()
        
        # Get initial end-effector position
        ee_pos = self._extract_ee_position(base_state)
        self.ee_position_history.append(ee_pos)
        
        # Compute enhanced state
        enhanced_state = self._compute_enhanced_state(base_state, ee_pos)
        
        return enhanced_state
    
    def step(self, action):
        """
        Execute action and return enhanced state.
        
        Args:
            action: Action index
            
        Returns:
            enhanced_state: 59D state vector
            reward: Scalar reward
            done: Episode termination flag
            info: Additional information
        """
        # Execute action in base environment
        base_state, reward, done, info = self.base_env.step(action)
        
        # Get current end-effector position
        ee_pos = self._extract_ee_position(base_state)
        self.ee_position_history.append(ee_pos)
        
        # Update current waypoint (if reached)
        self._update_waypoint_progress(ee_pos)
        
        # Compute enhanced state
        enhanced_state = self._compute_enhanced_state(base_state, ee_pos)
        
        # Add trajectory progress to info
        info['waypoint_idx'] = self.current_waypoint_idx
        info['trajectory_progress'] = self.current_waypoint_idx / max(self.total_waypoints - 1, 1)
        info['remaining_waypoints'] = self.total_waypoints - self.current_waypoint_idx
        
        return enhanced_state, reward, done, info
    
    def _extract_ee_position(self, base_state):
        """
        Extract end-effector position from base state.
        
        In Phase 03 state (35D):
        [0:3]   - Base pose (x, y, yaw)
        [3:10]  - Joint positions (7 joints)
        [10:17] - Joint velocities (7 joints)
        [17:20] - End-effector position (x, y, z)  ← Extract this
        [20:23] - End-effector orientation (roll, pitch, yaw)
        [23:29] - Base linear velocity (3D)
        [29:35] - Base angular velocity (3D)
        """
        return base_state[17:20]
    
    def _update_waypoint_progress(self, ee_pos, threshold=0.05):
        """
        Update current waypoint index if reached.
        
        Args:
            ee_pos: Current end-effector position
            threshold: Distance threshold to consider waypoint reached (5cm)
        """
        if self.current_waypoint_idx >= self.total_waypoints:
            return
        
        current_waypoint = self.trajectory_waypoints[self.current_waypoint_idx]
        distance = np.linalg.norm(ee_pos - current_waypoint)
        
        if distance < threshold:
            self.current_waypoint_idx += 1
    
    def _compute_enhanced_state(self, base_state, ee_pos):
        """
        Compute enhanced state with trajectory features.
        
        Args:
            base_state: Base state (35D)
            ee_pos: Current end-effector position (3D)
            
        Returns:
            Enhanced state (59D)
        """
        # 1. Base state (35D)
        state_parts = [base_state]
        
        # 2. Next waypoints features (18D)
        waypoint_features = self._compute_waypoint_features(ee_pos)
        state_parts.append(waypoint_features)
        
        # 3. Progress metrics (6D)
        progress_features = self._compute_progress_features(ee_pos)
        state_parts.append(progress_features)
        
        # Concatenate all parts
        enhanced_state = np.concatenate(state_parts)
        
        # Ensure correct dimension
        if len(enhanced_state) != self.state_dim:
            print(f"⚠️ State dimension mismatch: {len(enhanced_state)} != {self.state_dim}")
            enhanced_state = np.pad(enhanced_state, (0, max(0, self.state_dim - len(enhanced_state))))
            enhanced_state = enhanced_state[:self.state_dim]
        
        return enhanced_state
    
    def _compute_waypoint_features(self, ee_pos):
        """
        Compute features for next N waypoints.
        
        For each waypoint:
        - dx, dy, dz: Relative position
        - distance: Euclidean distance
        - heading: Horizontal angle (radians)
        - elevation: Vertical angle (radians)
        
        Returns:
            Array of shape (lookahead_count * 6,)
        """
        features = []
        
        for i in range(self.lookahead_count):
            waypoint_idx = self.current_waypoint_idx + i
            
            if waypoint_idx < self.total_waypoints:
                # Get waypoint
                waypoint = self.trajectory_waypoints[waypoint_idx]
                
                # Relative position
                delta = waypoint - ee_pos
                dx, dy, dz = delta
                
                # Distance
                distance = np.linalg.norm(delta)
                
                # Heading (azimuth angle in xy-plane)
                heading = np.arctan2(dy, dx) if distance > 1e-6 else 0.0
                
                # Elevation (angle from horizontal plane)
                elevation = np.arctan2(dz, np.sqrt(dx**2 + dy**2)) if distance > 1e-6 else 0.0
                
                features.extend([dx, dy, dz, distance, heading, elevation])
            else:
                # No more waypoints - use zeros
                features.extend([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        
        return np.array(features)
    
    def _compute_progress_features(self, ee_pos):
        """
        Compute trajectory progress metrics.
        
        Features:
        1. Distance to final goal
        2. Trajectory completion percentage
        3. Distance to current waypoint
        4. Estimated velocity magnitude
        5. Velocity alignment with trajectory direction
        6. Waypoint density (avg distance between upcoming waypoints)
        
        Returns:
            Array of shape (6,)
        """
        # 1. Distance to final goal
        final_goal = self.trajectory_waypoints[-1]
        distance_to_goal = np.linalg.norm(ee_pos - final_goal)
        
        # 2. Trajectory completion percentage
        completion = self.current_waypoint_idx / max(self.total_waypoints - 1, 1)
        
        # 3. Distance to current waypoint
        if self.current_waypoint_idx < self.total_waypoints:
            current_waypoint = self.trajectory_waypoints[self.current_waypoint_idx]
            distance_to_waypoint = np.linalg.norm(ee_pos - current_waypoint)
        else:
            distance_to_waypoint = 0.0
        
        # 4. Estimated velocity magnitude
        if len(self.ee_position_history) >= 2:
            velocity = self.ee_position_history[-1] - self.ee_position_history[-2]
            velocity_magnitude = np.linalg.norm(velocity)
        else:
            velocity_magnitude = 0.0
        
        # 5. Velocity alignment with trajectory direction
        if len(self.ee_position_history) >= 2 and self.current_waypoint_idx < self.total_waypoints:
            velocity = self.ee_position_history[-1] - self.ee_position_history[-2]
            direction_to_waypoint = current_waypoint - ee_pos
            
            if np.linalg.norm(velocity) > 1e-6 and np.linalg.norm(direction_to_waypoint) > 1e-6:
                # Cosine similarity
                velocity_alignment = np.dot(velocity, direction_to_waypoint) / (
                    np.linalg.norm(velocity) * np.linalg.norm(direction_to_waypoint)
                )
            else:
                velocity_alignment = 0.0
        else:
            velocity_alignment = 0.0
        
        # 6. Waypoint density (average distance between next 3 waypoints)
        upcoming_distances = []
        for i in range(min(3, self.total_waypoints - self.current_waypoint_idx - 1)):
            wp1 = self.trajectory_waypoints[self.current_waypoint_idx + i]
            wp2 = self.trajectory_waypoints[self.current_waypoint_idx + i + 1]
            upcoming_distances.append(np.linalg.norm(wp2 - wp1))
        
        waypoint_density = np.mean(upcoming_distances) if upcoming_distances else 0.0
        
        return np.array([
            distance_to_goal,
            completion,
            distance_to_waypoint,
            velocity_magnitude,
            velocity_alignment,
            waypoint_density
        ])
    
    def get_state_description(self):
        """
        Get human-readable description of state vector.
        
        Returns:
            Dictionary mapping state indices to descriptions
        """
        desc = {}
        idx = 0
        
        # Base state (35D)
        desc[f'{idx}:{idx+3}'] = 'Base pose (x, y, yaw)'
        idx += 3
        desc[f'{idx}:{idx+7}'] = 'Joint positions (7 joints)'
        idx += 7
        desc[f'{idx}:{idx+7}'] = 'Joint velocities (7 joints)'
        idx += 7
        desc[f'{idx}:{idx+3}'] = 'End-effector position (x, y, z)'
        idx += 3
        desc[f'{idx}:{idx+3}'] = 'End-effector orientation (roll, pitch, yaw)'
        idx += 3
        desc[f'{idx}:{idx+3}'] = 'Base linear velocity (x, y, z)'
        idx += 3
        desc[f'{idx}:{idx+3}'] = 'Base angular velocity (roll, pitch, yaw)'
        idx += 3
        
        # Waypoint features (18D)
        for i in range(self.lookahead_count):
            desc[f'{idx}:{idx+6}'] = f'Waypoint {i+1} (dx, dy, dz, dist, heading, elev)'
            idx += 6
        
        # Progress features (6D)
        desc[f'{idx}'] = 'Distance to goal'
        desc[f'{idx+1}'] = 'Completion %'
        desc[f'{idx+2}'] = 'Distance to current waypoint'
        desc[f'{idx+3}'] = 'Velocity magnitude'
        desc[f'{idx+4}'] = 'Velocity alignment'
        desc[f'{idx+5}'] = 'Waypoint density'
        
        return desc


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("Phase 04.2: Trajectory Integration State Wrapper Test")
    print("=" * 60)
    
    # Mock base environment
    class MockEnv:
        def __init__(self):
            self.state_dim = 35
        
        def reset(self):
            return np.random.rand(35)
        
        def step(self, action):
            state = np.random.rand(35)
            # Set end-effector position to move along trajectory
            state[17:20] = [0.5 + np.random.rand() * 0.1, 
                           0.5 + np.random.rand() * 0.1, 
                           0.3 + np.random.rand() * 0.05]
            return state, 10.0, False, {}
    
    # Create trajectory waypoints (simple line)
    waypoints = [
        [0.5, 0.5, 0.3],
        [0.6, 0.6, 0.35],
        [0.7, 0.7, 0.4],
        [0.8, 0.8, 0.45],
        [0.9, 0.9, 0.5],
    ]
    
    # Create wrapper
    base_env = MockEnv()
    wrapper = TrajectoryStateWrapper(base_env, waypoints, lookahead_count=3)
    
    print(f"\n✅ State dimension: {wrapper.state_dim}D")
    print(f"   Base: {wrapper.base_state_dim}D")
    print(f"   Waypoints: {wrapper.waypoints_dim}D")
    print(f"   Progress: {wrapper.progress_dim}D")
    
    # Test reset
    state = wrapper.reset()
    print(f"\n✅ Reset complete, state shape: {state.shape}")
    
    # Test step
    for step in range(5):
        state, reward, done, info = wrapper.step(action=0)
        print(f"\n📍 Step {step+1}:")
        print(f"   Waypoint: {info['waypoint_idx']}/{wrapper.total_waypoints}")
        print(f"   Progress: {info['trajectory_progress']*100:.1f}%")
        print(f"   State shape: {state.shape}")
    
    # Print state description
    print("\n📊 State Vector Description:")
    print("-" * 60)
    desc = wrapper.get_state_description()
    for indices, description in desc.items():
        print(f"  [{indices:>10}] - {description}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
