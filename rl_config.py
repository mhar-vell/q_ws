"""
Configuration file for RL Trajectory Planner
Adjust these parameters to optimize learning performance
"""

# RL Agent Configuration
RL_CONFIG = {
    # Agent Type Selection
    'use_dqn': True,  # True for DQN, False for tabular Q-learning
    
    # Q-Learning Parameters (if use_dqn = False)
    'q_learning': {
        'learning_rate': 0.1,
        'discount_factor': 0.95,
        'epsilon': 1.0,
        'epsilon_decay': 0.995,
        'epsilon_min': 0.01,
        'state_bins': 10  # Discretization bins per state dimension
    },
    
    # DQN Parameters (if use_dqn = True)  
    'dqn': {
        'learning_rate': 0.001,
        'discount_factor': 0.95,
        'epsilon': 1.0,
        'epsilon_decay': 0.995,
        'epsilon_min': 0.01,
        'memory_size': 10000,
        'batch_size': 32,
        'hidden_dims': [256, 256],  # Neural network architecture
        'target_update_freq': 100
    }
}

# Environment Configuration
ENV_CONFIG = {
    # Episode Parameters
    'max_episode_steps': 1000,
    'dt': 0.01,  # Control timestep
    
    # Action Space
    'actions_per_joint': 5,  # [-2, -1, 0, +1, +2] * scale
    'action_scale': 0.05,    # Radians per action step
    
    # Trajectory Parameters
    'default_trajectory_type': 'figure8',  # 'figure8', 'circle', 'spiral', 'line'
    'trajectory_points': 20,
    'trajectory_scale': 0.3,  # Size scaling factor
    'trajectory_height': 0.8, # Base height above robot
    
    # Reward Function Weights
    'rewards': {
        'position_error_weight': -10.0,      # Penalty for position error
        'orientation_error_weight': -2.0,    # Penalty for orientation error
        'smoothness_weight': -0.1,           # Penalty for joint velocity
        'stability_weight': -0.5,            # Penalty for base motion
        'progress_bonus': 10.0,              # Bonus for reaching waypoints
        'energy_weight': -0.5,               # Penalty for large movements
        'completion_bonus': 100.0,           # Bonus for completing trajectory
        'precision_threshold': 0.05          # Distance threshold for waypoint (m)
    },
    
    # Disturbance Parameters
    'disturbances': {
        'training_frequency': 0.05,    # Probability per step during training
        'force_range': (-20, 20),      # Force disturbance range (N)
        'torque_range': (-5, 5),       # Torque disturbance range (Nm)
        'test_force_range': (-50, 50), # Stronger forces for testing
        'test_torque_range': (-15, 15) # Stronger torques for testing
    }
}

# Training Configuration
TRAINING_CONFIG = {
    # Training Episodes
    'num_episodes': 1000,
    'save_frequency': 50,      # Save model every N episodes
    'plot_frequency': 100,     # Update plots every N episodes
    'progress_frequency': 50,  # Print progress every N episodes
    
    # Performance Thresholds
    'convergence_threshold': 0.02,  # Consider converged if error < this (m)
    'early_stopping_episodes': 100, # Stop if no improvement for N episodes
    'min_episodes': 200,            # Minimum episodes before early stopping
    
    # Model Saving
    'model_prefix': 'husky_kuka_trajectory_planner',
    'save_training_plots': True,
    'save_execution_videos': True
}

# Evaluation Configuration  
EVAL_CONFIG = {
    # Performance Metrics
    'evaluation_episodes': 10,
    'disturbance_tests': 10,
    'recovery_threshold': 0.05,     # Error threshold for recovery (m)
    'recovery_window': 10,          # Consecutive steps for recovery
    'max_recovery_time': 100,       # Max steps to wait for recovery
    
    # Trajectory Variants for Testing
    'test_trajectories': [
        'figure8',      # Standard figure-8
        'circle',       # Circular path
        'spiral',       # Expanding spiral
        'square',       # Square path
        'random'        # Random waypoints
    ],
    
    # Metrics to Track
    'metrics': [
        'mean_error',           # Average tracking error
        'max_error',            # Maximum tracking error  
        'completion_rate',      # Percentage of trajectory completed
        'recovery_time',        # Time to recover from disturbances
        'energy_efficiency',    # Total joint movement
        'smoothness',          # Velocity variance
        'stability'            # Base platform motion
    ]
}

# Hardware-Specific Configuration
HARDWARE_CONFIG = {
    # KUKA iiwa Joint Limits (radians)
    'joint_limits': [
        (-2.97, 2.97),   # Joint 1: ±170°
        (-2.09, 2.09),   # Joint 2: ±120°  
        (-2.97, 2.97),   # Joint 3: ±170°
        (-2.09, 2.09),   # Joint 4: ±120°
        (-2.97, 2.97),   # Joint 5: ±170°
        (-2.09, 2.09),   # Joint 6: ±120°
        (-3.05, 3.05)    # Joint 7: ±175°
    ],
    
    # Safety Limits
    'max_joint_velocity': 2.0,    # rad/s
    'max_joint_acceleration': 5.0, # rad/s²
    'workspace_limits': {
        'x': (-0.8, 0.8),  # Reachable X range (m)
        'y': (-0.8, 0.8),  # Reachable Y range (m) 
        'z': (0.2, 1.2)    # Reachable Z range (m)
    },
    
    # Control Parameters
    'control_frequency': 100,  # Hz
    'force_limit': 500,        # N (joint torque limit)
    'position_tolerance': 0.01, # Joint position tolerance (rad)
    'velocity_tolerance': 0.1   # Joint velocity tolerance (rad/s)
}

# Visualization Configuration
VIS_CONFIG = {
    # Plot Settings
    'figure_size': (12, 8),
    'dpi': 150,
    'color_scheme': {
        'target': 'red',
        'actual': 'blue', 
        'error': 'orange',
        'reward': 'green',
        'disturbance': 'purple'
    },
    
    # 3D Trajectory Visualization
    'trajectory_plot': {
        'line_width': 2,
        'marker_size': 4,
        'alpha': 0.8,
        'show_waypoints': True,
        'show_orientation': False  # Show orientation arrows (can be cluttered)
    },
    
    # Performance Plots
    'performance_plots': {
        'moving_average_window': 10,
        'show_confidence_intervals': True,
        'log_scale_rewards': False,
        'normalize_errors': True
    }
}

# Advanced Features Configuration
ADVANCED_CONFIG = {
    # Curriculum Learning
    'curriculum_learning': {
        'enabled': False,
        'start_simple': True,      # Start with simple trajectories
        'complexity_increase': 50, # Episodes between complexity increases
        'max_complexity': 1.0      # Maximum complexity multiplier
    },
    
    # Multi-Agent Training (Future Feature)
    'multi_agent': {
        'enabled': False,
        'num_agents': 2,
        'cooperative': True,  # Cooperative vs competitive
        'shared_experience': True
    },
    
    # Transfer Learning
    'transfer_learning': {
        'enabled': False,
        'pretrained_model': None,
        'freeze_layers': [],      # Which layers to freeze
        'fine_tuning_lr': 0.0001  # Lower learning rate for fine-tuning
    },
    
    # Adaptive Control
    'adaptive_control': {
        'enabled': True,
        'adaptation_rate': 0.01,  # How quickly to adapt to changes
        'uncertainty_threshold': 0.1,  # When to trigger adaptation
        'memory_length': 100      # Steps to remember for adaptation
    }
}

# Export all configurations
ALL_CONFIGS = {
    'rl': RL_CONFIG,
    'env': ENV_CONFIG, 
    'training': TRAINING_CONFIG,
    'eval': EVAL_CONFIG,
    'hardware': HARDWARE_CONFIG,
    'vis': VIS_CONFIG,
    'advanced': ADVANCED_CONFIG
}

def get_config(config_name=None):
    """
    Get configuration dictionary.
    
    Args:
        config_name: Specific config to get ('rl', 'env', etc.)
                    If None, returns all configs
    
    Returns:
        dict: Configuration parameters
    """
    if config_name is None:
        return ALL_CONFIGS
    else:
        return ALL_CONFIGS.get(config_name, {})

def print_config_summary():
    """Print a summary of all configuration parameters."""
    print("=" * 60)
    print("RL TRAJECTORY PLANNER - CONFIGURATION SUMMARY")
    print("=" * 60)
    
    for config_name, config_dict in ALL_CONFIGS.items():
        print(f"\n📋 {config_name.upper()} CONFIG:")
        
        if config_name == 'rl':
            agent_type = 'DQN' if config_dict['use_dqn'] else 'Q-Learning'
            print(f"   Agent: {agent_type}")
            if config_dict['use_dqn']:
                print(f"   Learning Rate: {config_dict['dqn']['learning_rate']}")
                print(f"   Network: {config_dict['dqn']['hidden_dims']}")
            else:
                print(f"   Learning Rate: {config_dict['q_learning']['learning_rate']}")
                print(f"   State Bins: {config_dict['q_learning']['state_bins']}")
                
        elif config_name == 'env':
            print(f"   Episode Steps: {config_dict['max_episode_steps']}")
            print(f"   Action Scale: {config_dict['action_scale']} rad")
            print(f"   Trajectory: {config_dict['default_trajectory_type']}")
            
        elif config_name == 'training':
            print(f"   Episodes: {config_dict['num_episodes']}")
            print(f"   Save Freq: {config_dict['save_frequency']}")
            
        elif config_name == 'eval':
            print(f"   Test Episodes: {config_dict['evaluation_episodes']}")
            print(f"   Recovery Threshold: {config_dict['recovery_threshold']}m")
            
        elif config_name == 'hardware':
            print(f"   Control Freq: {config_dict['control_frequency']} Hz")
            print(f"   Joint Limits: {len(config_dict['joint_limits'])} joints")
            
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print_config_summary()
    
    print("\n🔧 CONFIGURATION USAGE:")
    print("from rl_config import get_config")
    print("rl_config = get_config('rl')")
    print("env_config = get_config('env')")
    print("# Modify parameters as needed for your setup")