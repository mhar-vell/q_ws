# Simulation Module

Core simulation system for Husky-KUKA mobile manipulator with RL training capabilities.

## Files

### `sim_husky_kuka.py` - Main Simulation Script
**Purpose**: Primary entry point for running PyBullet simulation with RL training.

**Features**:
- 🎮 PyBullet physics simulation (GUI or headless)
- 🤖 Husky mobile base + KUKA LBR iiwa 7 arm
- 🧠 Dual RL agents (DQN and Q-Learning)
- 🌪️ Disturbance injection system (5 types)
- 📊 Real-time metrics and visualization
- ⌨️ Interactive keyboard controls
- 💾 Automatic checkpoint saving

**Usage**:
```bash
# GUI mode with auto-start training
python src/simulation/sim_husky_kuka.py --auto-start

# Headless mode for faster training
python src/simulation/sim_husky_kuka.py --headless --episodes 2000

# Specific scenario and intensity
python src/simulation/sim_husky_kuka.py --scenario continuous --intensity golden
```

**Command-Line Arguments**:
- `--headless`: Run without GUI (faster training)
- `--auto-start`: Start RL training immediately
- `--scenario`: Disturbance type (none, random, periodic, continuous, impulse)
- `--episodes`: Number of training episodes (default: 2000)
- `--algorithm`: RL algorithm (dqn, qlearning, both)

**Keyboard Controls** (GUI mode):
- `t` - Toggle RL training on/off
- `u` - Apply test perturbation (updated from 'p')
- `d` - Display diagnostics
- `p` - Take screenshot
- `Esc` - Safe exit with checkpoint save

---

### `rl_mission_env.py` - RL Environment and Agents
**Purpose**: Defines the RL environment, DQN agent, and Q-Learning agent.

**Key Classes**:

#### `MobileManipulatorEnv`
RL environment wrapper for the Husky-KUKA system.

**Features**:
- State space: 35-dimensional (base pose, arm joints, IMU data, goal)
- Action space: 10 discrete actions (movement primitives)
- Reward function: Distance-based with success bonuses
- Curriculum learning: Progressive difficulty adjustment

**State Representation**:
```python
state = [
    base_x, base_y, base_yaw,          # Base position (3)
    base_vx, base_vy, base_vyaw,       # Base velocity (3)
    joint_1, ..., joint_7,              # Arm joints (7)
    ee_x, ee_y, ee_z,                   # End effector pos (3)
    ee_dx, ee_dy, ee_dz,                # EE velocity (3)
    imu1_roll, imu1_pitch, imu1_yaw,    # IMU 1 (3)
    imu2_roll, imu2_pitch, imu2_yaw,    # IMU 2 (3)
    goal_x, goal_y, goal_z,             # Goal position (3)
    rel_x, rel_y, rel_z,                # Relative to goal (3)
    dist_to_goal, timestep              # Metrics (2)
]  # Total: 35 dimensions
```

**Action Space**:
```python
actions = {
    0: move_forward,
    1: move_backward,
    2: rotate_left,
    3: rotate_right,
    4: arm_reach_forward,
    5: arm_reach_backward,
    6: arm_move_up,
    7: arm_move_down,
    8: arm_rotate_cw,
    9: arm_rotate_ccw
}
```

**Reward Structure**:
```python
# Progressive reward tiers
if error < 0.02:
    reward = +100  # Excellent
elif error < 0.03:
    reward = +50   # Good
elif error < 0.05:
    reward = +25   # Acceptable
else:
    reward = -distance * 10  # Proportional penalty
```

---

#### `DQNAgent`
Deep Q-Network agent with experience replay.

**Architecture**:
```
Input (35) → Dense(128, ReLU) → Dense(128, ReLU) → Output(10)
```

**Features**:
- Experience replay buffer (10,000 transitions)
- Target network for stable learning
- ε-greedy exploration (1.0 → 0.01)
- Huber loss for robustness
- Adam optimizer (lr=0.001)
- GPU acceleration (if available)

**Hyperparameters**:
```python
learning_rate: 0.001
gamma: 0.99
epsilon_start: 1.0
epsilon_end: 0.01
epsilon_decay: 0.995
batch_size: 32
replay_buffer_size: 10000
target_update_frequency: 100
```

**Training Loop**:
```python
# Select action
action = agent.select_action(state)

# Environment step
next_state, reward, done = env.step(action)

# Store transition
agent.update(state, action, reward, next_state)

# Update target network periodically
if step % 100 == 0:
    agent.update_target_network()
```

**Checkpoint Format** (.pth):
```python
{
    'model_state_dict': q_network.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'epsilon': current_epsilon,
    'episode': episode_number,
    'replay_buffer': buffer_state
}
```

---

#### `QLearningAgent`
Tabular Q-Learning agent (baseline).

**Features**:
- State discretization (continuous → discrete)
- Q-table: Dictionary{(state, action): Q-value}
- ε-greedy exploration (constant 0.3)
- No experience replay needed
- Works without GPU/PyTorch

**Hyperparameters**:
```python
learning_rate: 0.1
gamma: 0.99
epsilon: 0.3 (constant)
```

**Update Rule**:
```python
Q(s,a) ← Q(s,a) + α[r + γ·max_a'Q(s',a') - Q(s,a)]
```

**State Discretization**:
- Position: ±5m in 0.1m bins (100 bins)
- Velocity: ±2m/s in 0.2m/s bins (20 bins)
- Angles: ±π in π/8 bins (16 bins)

**Checkpoint Format** (.pkl):
```python
{
    'q_table': dict_of_state_action_values,
    'epsilon': current_epsilon,
    'episode': episode_number,
    'state_visits': visit_counts
}
```

---

### `rl_training_guide.py` - Training Utilities
**Purpose**: Helper functions and guides for RL training.

**Features**:
- Training progress tracking
- Hyperparameter suggestions
- Common training patterns
- Debugging utilities

**Functions**:
```python
def track_training_progress(metrics):
    """Track and visualize training metrics"""
    
def suggest_hyperparameters(performance):
    """Suggest hyperparameter adjustments"""
    
def debug_agent_behavior(agent, env, episodes):
    """Debug agent decision-making"""
```

---

## Simulation Flow

```
┌─────────────────────────────────────────────┐
│         sim_husky_kuka.py                   │
│  Main Simulation Loop                       │
└────────┬────────────────────────────────────┘
         │
         ├──→ PyBullet Initialization
         │    - Load robot URDFs
         │    - Setup physics
         │    - Create constraint
         │
         ├──→ RL Environment Setup
         │    └──→ MobileManipulatorEnv
         │         - Define state space
         │         - Define actions
         │         - Setup reward function
         │
         ├──→ Agent Creation
         │    ├──→ DQNAgent (if PyTorch available)
         │    └──→ QLearningAgent (fallback)
         │
         └──→ Training Loop
              ├──→ Select action
              ├──→ Apply disturbance
              ├──→ Step environment
              ├──→ Update agent
              ├──→ Save checkpoints
              └──→ Log metrics
```

---

## Disturbance System

### Types

1. **None** - No disturbances (baseline)
2. **Random** - Random force impulses every timestep
3. **Periodic** - Periodic forces (50 timestep period)
4. **Continuous** - Continuous low-level disturbances
5. **Impulse** - High-intensity impulse at timestep 25

### Intensity Levels

- **Normal**: Standard magnitude
  - Forces: ±10N to ±100N (type-dependent)
  - Torques: ±5Nm to ±50Nm
  
- **Golden**: φ ≈ 1.618 multiplier
  - Forces: ±16.18N to ±161.8N
  - Torques: ±8.09Nm to ±80.9Nm

### Implementation

```python
def apply_disturbance(robot_id, disturbance_type, intensity, timestep):
    """Apply disturbance based on type and intensity"""
    
    if disturbance_type == 'random':
        force = np.random.uniform(-50, 50, 2) * intensity
        torque = np.random.uniform(-5, 5) * intensity
        
    elif disturbance_type == 'periodic':
        if timestep % 50 == 0:
            force = [100 * intensity, 0]
            torque = 0
            
    elif disturbance_type == 'continuous':
        force = [10 * np.sin(timestep/10), 10 * np.cos(timestep/10)]
        force *= intensity
        
    elif disturbance_type == 'impulse':
        if timestep == 25:
            force = [200 * intensity, 0]
            
    p.applyExternalForce(robot_id, -1, [force[0], force[1], 0], ...)
    p.applyExternalTorque(robot_id, -1, [0, 0, torque], ...)
```

---

## Performance Metrics

### Tracked Metrics

```python
metrics = {
    'episode': int,
    'success': bool,
    'error': float,           # Final distance to goal (m)
    'reward': float,          # Total episode reward
    'steps': int,             # Episode length
    'epsilon': float,         # Current exploration rate
    'disturbance': str,       # Disturbance type
    'intensity': str          # Intensity level
}
```

### Saved Files

- **Checkpoints**: `rl_checkpoint_{scenario}_ep{num}_{algo}.pth|.pkl`
- **Final Models**: `rl_final_{scenario}_{intensity}_{algo}.pth|.pkl`
- **Metrics**: `rl_metrics_{algo}.json`
- **Screenshots**: `training_{scenario}_ep{num}.png`

---

## Usage Examples

### Basic Training

```python
from rl_mission_env import MobileManipulatorEnv, DQNAgent

# Create environment
env = MobileManipulatorEnv(
    pybullet_client=p,
    husky_id=husky,
    kuka_id=kuka,
    goal_pose=[1.0, 0.0, 0.5]
)

# Create agent
agent = DQNAgent(state_dim=35, action_dim=10)

# Training loop
for episode in range(2000):
    state = env.reset()
    episode_reward = 0
    
    for step in range(200):
        action = agent.select_action(state)
        next_state, reward, done = env.step(action)
        agent.update(state, action, reward, next_state)
        
        state = next_state
        episode_reward += reward
        
        if done:
            break
    
    # Save checkpoint every 100 episodes
    if episode % 100 == 0:
        agent.save(f'checkpoint_ep{episode}.pth')
```

### Loading Trained Model

```python
# Load DQN checkpoint
agent = DQNAgent(state_dim=35, action_dim=10)
checkpoint = torch.load('rl_checkpoint_continuous_ep2000_dqn.pth')
agent.q_network.load_state_dict(checkpoint['model_state_dict'])
agent.epsilon = 0.0  # No exploration for evaluation

# Use for evaluation
state = env.reset()
for step in range(200):
    action = agent.select_action(state)
    state, reward, done = env.step(action)
    if done:
        break
```

---

## Troubleshooting

### PyTorch Not Available

**Issue**: DQN falls back to Q-Learning  
**Solution**:
```bash
conda install pytorch torchvision torchaudio -c pytorch
```

### Memory Overflow

**Issue**: Replay buffer too large  
**Solution**: Reduce buffer size in DQNAgent
```python
agent = DQNAgent(state_dim=35, action_dim=10, buffer_size=5000)
```

### Slow Training

**Issue**: GUI rendering slows training  
**Solution**: Use headless mode
```bash
python src/simulation/sim_husky_kuka.py --headless
```

### NaN Rewards

**Issue**: Reward calculation error  
**Solution**: Check state validity and distance calculations

---

## Related Documentation

- **Main Simulation README**: `../README.md`
- **Planning Module**: `../planning/README.md`
- **Config Module**: `../config/README.md`
- **Training Guides**: `/home/marcoreis/robust_mm_control_ws/documentation/training_guides/`
- **Launchers**: `/home/marcoreis/robust_mm_control_ws/launchers/README.md`

---

**Last Updated**: November 2, 2025  
**Module**: `/home/marcoreis/robust_mm_control_ws/src/simulation`  
**Status**: Documented ✅
