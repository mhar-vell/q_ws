import numpy as np
import random

class MobileManipulatorEnv:
    """
    RL environment for Husky+KUKA mobile manipulator trajectory planning in PyBullet.
    Models state, action, reward, and disturbances for Q-learning.
    """
    def __init__(self, pybullet_client, husky_id, kuka_id, goal_pose):
        self.p = pybullet_client
        self.husky = husky_id
        self.kuka = kuka_id
        self.goal_pose = goal_pose  # Desired end-effector pose (x, y, z)
        self.state_dim = 14  # Example: 3 base + 7 joints + 4 end-effector
        self.action_dim = 10 # Example: 7 joints + 3 base moves
        self.disturbance_types = ['none', 'random', 'periodic', 'continuous', 'impulse']
        self.current_disturbance = 'none'
        self.reset()

    def reset(self):
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
        except Exception as e:
            print(f"Warning: RL reset error (non-fatal): {e}")
        
        self.timestep = 0
        self.done = False
        # Don't randomize disturbance on reset - keep current scenario
        return self.get_state()

    def step(self, action):
        # Map actions to robot commands
        # Actions 0-6: KUKA joint increments
        # Actions 7: Husky forward, 8: turn left, 9: turn right
        joint_delta = 0.05  # radians per step
        base_speed = 0.2    # meters per step
        base_turn = 0.2     # radians per step

        num_kuka_joints = self.p.getNumJoints(self.kuka)
        # Get current joint positions
        joint_states = [self.p.getJointState(self.kuka, i) for i in range(num_kuka_joints)]
        joint_positions = [js[0] for js in joint_states]

        # Apply joint action
        if 0 <= action < num_kuka_joints:
            # Increment joint i
            new_pos = joint_positions.copy()
            new_pos[action] += joint_delta
            self.p.setJointMotorControlArray(self.kuka, range(num_kuka_joints),
                                            self.p.POSITION_CONTROL, targetPositions=new_pos)
        elif action == num_kuka_joints:
            # Husky forward
            self.p.resetBaseVelocity(self.husky, linearVelocity=[base_speed, 0, 0])
        elif action == num_kuka_joints + 1:
            # Husky turn left
            self.p.resetBaseVelocity(self.husky, angularVelocity=[0, 0, base_turn])
        elif action == num_kuka_joints + 2:
            # Husky turn right
            self.p.resetBaseVelocity(self.husky, angularVelocity=[0, 0, -base_turn])

        # Apply disturbance
        self.inject_disturbance()
        obs = self.get_state()
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
        # End-effector error (distance to goal)
        ee_error = np.linalg.norm(obs[-4:-1] - self.goal_pose[:3])

        # IMU instability penalty (base linear acceleration)
        # Assume IMU data is last 6 elements: [vx, vy, vz, wx, wy, wz]
        imu_accel = np.linalg.norm(obs[-6:-3])
        instability_penalty = 0.2 * imu_accel  # Weight for instability

        # Energy/smoothness penalty (large joint/base movements)
        # Penalize if action is a base move or large joint change
        energy_penalty = 0.0
        if action >= self.p.getNumJoints(self.kuka):
            energy_penalty = 0.1  # Penalize base moves

        # Total reward: negative error, minus penalties
        rew = -ee_error - instability_penalty - energy_penalty
        return rew

    def check_done(self, obs):
        # Success if end-effector is close to goal
        error = np.linalg.norm(obs[-4:-1] - self.goal_pose[:3])
        return error < 0.01  # 1cm tolerance

    def inject_disturbance(self):
        # Simulate disturbances based on current scenario
        if self.current_disturbance == 'random':
            force = [random.uniform(-50, 50), random.uniform(-50, 50), 0]
            self.p.applyExternalForce(self.husky, -1, force, [0, 0, 0], self.p.WORLD_FRAME)
        elif self.current_disturbance == 'periodic':
            if self.timestep % 50 == 0:
                force = [random.choice([-100, 100]), random.choice([-100, 100]), 0]
                self.p.applyExternalForce(self.husky, -1, force, [0, 0, 0], self.p.WORLD_FRAME)
        elif self.current_disturbance == 'continuous':
            force = [random.uniform(-10, 10), random.uniform(-10, 10), 0]
            self.p.applyExternalForce(self.husky, -1, force, [0, 0, 0], self.p.WORLD_FRAME)
        elif self.current_disturbance == 'impulse':
            if self.timestep == 25:
                force = [random.choice([-200, 200]), random.choice([-200, 200]), 0]
                self.p.applyExternalForce(self.husky, -1, force, [0, 0, 0], self.p.WORLD_FRAME)
        # else: no disturbance

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
