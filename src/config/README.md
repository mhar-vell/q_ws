# Config Module

Centralized configuration management for the Husky-KUKA RL system.

## Files

### `rl_config.py` - Configuration Manager
**Purpose**: Single source of truth for all system parameters, hyperparameters, and settings.

**Features**:
- 📋 Centralized parameter management
- 🔧 Environment-specific configurations
- 🎛️ RL hyperparameter presets
- 🌪️ Disturbance scenario definitions
- 📦 Easy parameter access and validation
- 💾 Configuration serialization/loading

---

## Configuration Structure

### 1. **System Parameters**

#### Physics Simulation
```python
PHYSICS_CONFIG = {
    'timestep': 1/240,          # PyBullet timestep (seconds)
    'gravity': [0, 0, -9.81],   # Gravity vector (m/s²)
    'num_solver_iterations': 10,
    'use_real_time': False,     # True = realtime, False = fast as possible
    'render_width': 1920,       # Screenshot width
    'render_height': 1080,      # Screenshot height
}
```

#### Robot Parameters
```python
ROBOT_CONFIG = {
    # Husky base
    'husky_max_velocity': 1.0,      # m/s
    'husky_max_angular_vel': 1.0,   # rad/s
    'husky_wheel_radius': 0.165,    # m
    'husky_wheel_separation': 0.555, # m
    
    # KUKA arm
    'kuka_num_joints': 7,
    'kuka_joint_limits': [
        [-2.96, 2.96],  # Joint 1 (rad)
        [-2.09, 2.09],  # Joint 2
        [-2.96, 2.96],  # Joint 3
        [-2.09, 2.09],  # Joint 4
        [-2.96, 2.96],  # Joint 5
        [-2.09, 2.09],  # Joint 6
        [-3.05, 3.05],  # Joint 7
    ],
    'kuka_max_joint_vel': 1.5,      # rad/s
    'kuka_max_joint_torque': 300,   # Nm
    
    # End effector
    'ee_workspace_bounds': [
        [-2.0, 2.0],   # X bounds (m)
        [-2.0, 2.0],   # Y bounds (m)
        [0.0, 2.0]     # Z bounds (m)
    ]
}
```

#### Sensor Configuration
```python
SENSOR_CONFIG = {
    'imu_count': 2,
    'imu_noise_std': 0.01,          # IMU measurement noise
    'joint_sensor_noise': 0.001,     # Joint position noise
    'velocity_sensor_noise': 0.01,   # Velocity measurement noise
    'update_frequency': 240,         # Hz
}
```

---

### 2. **RL Hyperparameters**

#### DQN Configuration
```python
DQN_CONFIG = {
    # Network architecture
    'state_dim': 35,
    'action_dim': 10,
    'hidden_layers': [128, 128],
    'activation': 'relu',
    
    # Training hyperparameters
    'learning_rate': 0.001,
    'gamma': 0.99,              # Discount factor
    'batch_size': 32,
    'replay_buffer_size': 10000,
    'target_update_freq': 100,  # Episodes
    
    # Exploration
    'epsilon_start': 1.0,
    'epsilon_end': 0.01,
    'epsilon_decay': 0.995,
    
    # Training schedule
    'num_episodes': 2000,
    'max_steps_per_episode': 200,
    'checkpoint_frequency': 100,  # Save every N episodes
    
    # Optimization
    'optimizer': 'adam',
    'loss_function': 'huber',
    'gradient_clip': 10.0,
}
```

#### Q-Learning Configuration
```python
QLEARNING_CONFIG = {
    # Learning parameters
    'learning_rate': 0.1,
    'gamma': 0.99,
    'epsilon': 0.3,  # Constant exploration
    
    # State discretization
    'position_bins': 100,        # ±5m in 0.1m bins
    'velocity_bins': 20,         # ±2m/s in 0.2m/s bins
    'angle_bins': 16,            # ±π in π/8 bins
    
    # Training schedule
    'num_episodes': 2000,
    'max_steps_per_episode': 200,
    'checkpoint_frequency': 100,
}
```

#### Preset Configurations

```python
# For stable, conservative learning
CONSERVATIVE_PRESET = {
    'learning_rate': 0.0005,
    'epsilon_decay': 0.999,  # Slower decay
    'gamma': 0.95,
    'replay_buffer_size': 20000,
}

# For fast exploration (may be unstable)
AGGRESSIVE_PRESET = {
    'learning_rate': 0.01,
    'epsilon_decay': 0.98,   # Faster decay
    'gamma': 0.99,
    'replay_buffer_size': 5000,
}

# Balanced default
DEFAULT_PRESET = DQN_CONFIG  # Use standard config
```

---

### 3. **Environment Configuration**

#### State Space
```python
STATE_CONFIG = {
    'state_dimension': 35,
    'state_components': {
        'base_pose': 3,        # x, y, yaw
        'base_velocity': 3,     # vx, vy, vyaw
        'arm_joints': 7,        # joint angles
        'ee_position': 3,       # x, y, z
        'ee_velocity': 3,       # dx, dy, dz
        'imu_1': 3,            # roll, pitch, yaw
        'imu_2': 3,            # roll, pitch, yaw
        'goal_position': 3,     # x, y, z
        'relative_position': 3, # to goal
        'metrics': 2,           # distance, timestep
    },
    'normalization': {
        'position': 5.0,        # Divide by workspace size
        'velocity': 2.0,        # Divide by max velocity
        'angle': 3.14159,       # Divide by π
    }
}
```

#### Action Space
```python
ACTION_CONFIG = {
    'action_dimension': 10,
    'action_primitives': {
        0: 'move_forward',
        1: 'move_backward',
        2: 'rotate_left',
        3: 'rotate_right',
        4: 'arm_reach_forward',
        5: 'arm_reach_backward',
        6: 'arm_move_up',
        7: 'arm_move_down',
        8: 'arm_rotate_cw',
        9: 'arm_rotate_ccw',
    },
    'action_magnitudes': {
        'linear_velocity': 0.5,   # m/s
        'angular_velocity': 0.5,  # rad/s
        'joint_velocity': 0.3,    # rad/s
    }
}
```

#### Reward Function
```python
REWARD_CONFIG = {
    'distance_weight': -10.0,   # Penalty for distance to goal
    'success_reward': 100.0,    # Reward for reaching goal
    'good_reward': 50.0,        # Reward for close approach
    'acceptable_reward': 25.0,  # Reward for acceptable distance
    
    'thresholds': {
        'excellent': 0.02,      # < 2cm
        'good': 0.03,           # < 3cm
        'acceptable': 0.05,     # < 5cm
    },
    
    'penalties': {
        'collision': -100.0,
        'timeout': -10.0,
        'workspace_violation': -50.0,
    }
}
```

---

### 4. **Disturbance Configuration**

#### Disturbance Scenarios
```python
DISTURBANCE_CONFIG = {
    'none': {
        'description': 'No disturbances (baseline)',
        'apply_force': False,
        'apply_torque': False,
    },
    
    'random': {
        'description': 'Random impulses every timestep',
        'force_range': [-50, 50],    # N
        'torque_range': [-5, 5],     # Nm
        'frequency': 'every_step',
    },
    
    'periodic': {
        'description': 'Periodic disturbances',
        'force_magnitude': 100,       # N
        'torque_magnitude': 10,       # Nm
        'period': 50,                 # timesteps
        'phase': 0,                   # timesteps offset
    },
    
    'continuous': {
        'description': 'Continuous low-level disturbances',
        'force_amplitude': 10,        # N
        'angular_frequency': 0.1,     # rad/timestep
        'force_direction': 'circular', # or 'linear'
    },
    
    'impulse': {
        'description': 'Single high-intensity impulse',
        'force_magnitude': 200,       # N
        'application_time': 25,       # timestep
        'duration': 1,                # timesteps
    }
}
```

#### Intensity Levels
```python
INTENSITY_CONFIG = {
    'normal': {
        'multiplier': 1.0,
        'description': 'Standard disturbance magnitude'
    },
    
    'golden': {
        'multiplier': 1.618,          # φ (golden ratio)
        'description': 'Enhanced disturbance using golden ratio'
    },
    
    'extreme': {
        'multiplier': 2.5,
        'description': 'Very high disturbance for stress testing'
    }
}
```

---

### 5. **Training Configuration**

#### Training Schedules
```python
TRAINING_CONFIG = {
    'curriculum_learning': {
        'enabled': True,
        'stages': [
            {
                'episodes': [0, 500],
                'difficulty': 'easy',
                'disturbance': 'none',
            },
            {
                'episodes': [500, 1000],
                'difficulty': 'medium',
                'disturbance': 'random',
                'intensity': 'normal',
            },
            {
                'episodes': [1000, 2000],
                'difficulty': 'hard',
                'disturbance': 'continuous',
                'intensity': 'golden',
            }
        ]
    },
    
    'early_stopping': {
        'enabled': True,
        'patience': 200,              # Episodes without improvement
        'min_improvement': 0.01,      # Minimum reward improvement
    },
    
    'checkpoint_strategy': {
        'save_frequency': 100,        # Episodes
        'save_best_only': False,      # Also save periodic checkpoints
        'max_checkpoints': 10,        # Keep last N checkpoints
    }
}
```

---

## Usage

### Basic Usage

```python
from config.rl_config import (
    DQN_CONFIG,
    ROBOT_CONFIG,
    DISTURBANCE_CONFIG
)

# Access parameters
learning_rate = DQN_CONFIG['learning_rate']
max_velocity = ROBOT_CONFIG['husky_max_velocity']
disturbance = DISTURBANCE_CONFIG['random']

# Use in code
agent = DQNAgent(
    state_dim=DQN_CONFIG['state_dim'],
    action_dim=DQN_CONFIG['action_dim'],
    learning_rate=DQN_CONFIG['learning_rate']
)
```

### Custom Configuration

```python
# Override specific parameters
custom_config = DQN_CONFIG.copy()
custom_config['learning_rate'] = 0.0001  # Lower learning rate
custom_config['epsilon_decay'] = 0.998   # Slower exploration decay

agent = DQNAgent(**custom_config)
```

### Configuration Manager

```python
class ConfigManager:
    """Helper class for managing configurations"""
    
    def __init__(self):
        self.configs = {
            'dqn': DQN_CONFIG,
            'qlearning': QLEARNING_CONFIG,
            'robot': ROBOT_CONFIG,
            'disturbances': DISTURBANCE_CONFIG,
        }
    
    def get(self, config_name, key=None):
        """Get configuration or specific key"""
        config = self.configs.get(config_name)
        if key:
            return config.get(key)
        return config
    
    def set(self, config_name, key, value):
        """Update configuration value"""
        self.configs[config_name][key] = value
    
    def save(self, filepath):
        """Save configurations to JSON"""
        import json
        with open(filepath, 'w') as f:
            json.dump(self.configs, f, indent=4)
    
    def load(self, filepath):
        """Load configurations from JSON"""
        import json
        with open(filepath, 'r') as f:
            self.configs = json.load(f)

# Usage
config_mgr = ConfigManager()
learning_rate = config_mgr.get('dqn', 'learning_rate')
config_mgr.set('dqn', 'learning_rate', 0.0005)
config_mgr.save('custom_config.json')
```

---

## Parameter Tuning Guidelines

### Learning Rate
- **Too high** (>0.01): Training unstable, divergence
- **Too low** (<0.0001): Training too slow
- **Recommended**: 0.001 for DQN, 0.1 for Q-Learning

### Epsilon Decay
- **Too fast** (<0.97): Premature exploitation, suboptimal policy
- **Too slow** (>0.999): Prolonged exploration, slow convergence
- **Recommended**: 0.995 for DQN

### Replay Buffer Size
- **Too small** (<5000): Correlated samples, overfitting
- **Too large** (>50000): Memory issues, slow sampling
- **Recommended**: 10000 for typical training

### Gamma (Discount Factor)
- **Low** (<0.9): Short-sighted, ignores future rewards
- **High** (>0.99): Long-term planning, slower convergence
- **Recommended**: 0.99 for long-horizon tasks

### Batch Size
- **Too small** (<16): High variance gradients
- **Too large** (>128): Slower updates, memory issues
- **Recommended**: 32 for DQN

---

## Scenario Recommendations

### Quick Testing
```python
TEST_CONFIG = {
    'num_episodes': 100,
    'disturbance': 'none',
    'checkpoint_frequency': 50,
}
```

### Robust Training
```python
ROBUST_CONFIG = {
    'num_episodes': 2000,
    'disturbance': 'continuous',
    'intensity': 'golden',
    'curriculum_learning': True,
}
```

### Benchmarking
```python
BENCHMARK_CONFIG = {
    'algorithms': ['dqn', 'qlearning'],
    'disturbances': ['none', 'random', 'periodic', 'continuous', 'impulse'],
    'intensities': ['normal', 'golden'],
    'num_episodes': 2000,
    'num_trials': 5,  # Multiple runs for statistics
}
```

---

## Configuration Validation

```python
def validate_config(config, config_schema):
    """Validate configuration against schema"""
    errors = []
    
    # Check required keys
    for key in config_schema['required']:
        if key not in config:
            errors.append(f"Missing required key: {key}")
    
    # Check value ranges
    for key, value in config.items():
        if key in config_schema['ranges']:
            min_val, max_val = config_schema['ranges'][key]
            if not (min_val <= value <= max_val):
                errors.append(f"{key}={value} out of range [{min_val}, {max_val}]")
    
    # Check types
    for key, expected_type in config_schema['types'].items():
        if key in config and not isinstance(config[key], expected_type):
            errors.append(f"{key} should be {expected_type}, got {type(config[key])}")
    
    return errors

# Example schema
DQN_SCHEMA = {
    'required': ['learning_rate', 'gamma', 'epsilon_start'],
    'ranges': {
        'learning_rate': [0.00001, 0.1],
        'gamma': [0.9, 0.999],
        'epsilon_start': [0.5, 1.0],
    },
    'types': {
        'learning_rate': float,
        'batch_size': int,
        'replay_buffer_size': int,
    }
}

# Validate
errors = validate_config(DQN_CONFIG, DQN_SCHEMA)
if errors:
    print("Configuration errors:", errors)
```

---

## Environment Variables

You can also use environment variables to override configurations:

```bash
# Set via environment
export RL_LEARNING_RATE=0.0005
export RL_NUM_EPISODES=3000
export RL_DISTURBANCE=continuous

# Use in Python
import os

learning_rate = float(os.getenv('RL_LEARNING_RATE', DQN_CONFIG['learning_rate']))
num_episodes = int(os.getenv('RL_NUM_EPISODES', DQN_CONFIG['num_episodes']))
disturbance = os.getenv('RL_DISTURBANCE', 'none')
```

---

## Related Documentation

- **Main Source README**: `../README.md`
- **Simulation Module**: `../simulation/README.md`
- **Planning Module**: `../planning/README.md`
- **Launchers**: `/home/marcoreis/robust_mm_control_ws/launchers/README.md`
- **Training Tools**: `/home/marcoreis/robust_mm_control_ws/tools/README.md`

---

**Last Updated**: November 2, 2025  
**Module**: `/home/marcoreis/robust_mm_control_ws/src/config`  
**Status**: Documented ✅
