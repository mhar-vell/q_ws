# Source Code Modules

This directory contains the core source code for the robust mobile manipulator control system, including simulation, RL environments, trajectory planning, and configuration.

## Directory Structure

```
src/
├── README.md                    # This file
├── simulation/                  # Simulation and RL training
│   ├── README.md
│   ├── sim_husky_kuka.py       # Main simulation script
│   ├── rl_mission_env.py       # RL environment and agents
│   └── rl_training_guide.py    # Training guide utilities
├── planning/                    # Trajectory planning
│   ├── README.md
│   ├── rl_trajectory_planner.py    # RL-integrated planner
│   └── trajectory_generators.py    # Trajectory generation
└── config/                      # Configuration
    ├── README.md
    └── rl_config.py            # RL hyperparameters
```

## Module Overview

### 🎮 **simulation/** - Core Simulation System
The heart of the system, handling PyBullet simulation, RL training, and real-time control.

**Key Components**:
- Main simulation loop with PyBullet physics
- RL agent training (DQN and Q-Learning)
- Disturbance injection system
- Real-time visualization and control
- Performance metrics collection

**Entry Point**: `sim_husky_kuka.py`

---

### 🎯 **planning/** - Trajectory Planning
Generates and manages robot trajectories for mission execution.

**Key Components**:
- Circular, square, and lemniscate trajectories
- RL-integrated trajectory following
- Waypoint generation and management
- Goal pose updates

**Main Module**: `rl_trajectory_planner.py`

---

### ⚙️ **config/** - Configuration Management
Centralized configuration for RL hyperparameters and system settings.

**Key Components**:
- DQN hyperparameters
- Q-Learning parameters
- Training configuration
- Scenario definitions

**Main Module**: `rl_config.py`

---

## Quick Start

### Running the Simulation

```bash
# From workspace root
python src/simulation/sim_husky_kuka.py

# Or use a launcher
python launchers/launch_gui_simulation.py
```

### Training with RL

```bash
# Start simulation
python src/simulation/sim_husky_kuka.py

# In simulation window:
# Press 't' to start RL training
# Press 'd' for diagnostics
# Press 'Esc' to exit
```

### Generating Trajectories

```python
from src.planning.trajectory_generators import generate_circular_trajectory

# Generate 50-point circular trajectory
trajectory = generate_circular_trajectory(
    center=[1.0, 0.0, 0.5],
    radius=0.3,
    num_points=50
)
```

## Module Dependencies

```
simulation/
├── Requires: PyBullet, NumPy, PyTorch (optional)
├── Uses: planning/, config/
└── Outputs: Checkpoints, metrics, videos

planning/
├── Requires: NumPy
├── Uses: config/
└── Outputs: Trajectory waypoints

config/
├── Requires: None (pure configuration)
└── Provides: Hyperparameters for all modules
```

## Integration Flow

```
┌─────────────────┐
│  sim_husky_kuka │  Main simulation entry point
└────────┬────────┘
         │
         ├──→ rl_mission_env     (RL agents and environment)
         │
         ├──→ rl_trajectory_planner  (Trajectory following)
         │
         └──→ rl_config          (Hyperparameters)
```

## Development Guidelines

### Adding New Features

1. **New RL Agent**: Extend `rl_mission_env.py`
2. **New Trajectory**: Add to `trajectory_generators.py`
3. **New Scenario**: Update `sim_husky_kuka.py` disturbance system
4. **New Hyperparameters**: Add to `rl_config.py`

### Code Style

- **Python**: PEP 8 compliant
- **Docstrings**: NumPy style
- **Type Hints**: Encouraged for new code
- **Comments**: Explain why, not what

### Testing

```bash
# Unit tests
python test_scripts/unit_tests/test_waypoints.py

# Integration tests
python test_scripts/integration_tests/test_rl_system.py

# Full simulation test
python test_scripts/simulation_tests/test_phase1_improvements.py
```

## Performance Considerations

### PyBullet Optimization
- Physics timestep: 1/240 Hz
- Control frequency: 60 Hz
- Use DIRECT mode for faster training (no GUI)

### RL Training Optimization
- **DQN**: Requires PyTorch, ~2-3x faster than Q-Learning
- **Q-Learning**: No GPU needed, but slower convergence
- **Batch Size**: 32 for DQN (balance memory/speed)
- **Replay Buffer**: 10,000 transitions (adjust for memory)

### Memory Management
- Clear replay buffer after training session
- Save checkpoints periodically (every 100 episodes)
- Use `.pth` for DQN, `.pkl` for Q-Learning

## Common Tasks

### Modifying RL Hyperparameters

```python
# Edit src/config/rl_config.py
RL_CONFIG = {
    'learning_rate': 0.001,      # Adjust learning speed
    'gamma': 0.99,                # Discount factor
    'epsilon_start': 1.0,         # Initial exploration
    'epsilon_end': 0.01,          # Final exploration
    'epsilon_decay': 0.995        # Exploration decay rate
}
```

### Adding Custom Trajectory

```python
# In src/planning/trajectory_generators.py
def generate_custom_trajectory(params):
    """Generate custom trajectory pattern"""
    waypoints = []
    # Your trajectory logic here
    return waypoints
```

### Creating New Disturbance Type

```python
# In src/simulation/sim_husky_kuka.py
def apply_custom_disturbance(timestep):
    """Apply custom disturbance pattern"""
    if disturbance_type == 'custom':
        force = calculate_custom_force(timestep)
        p.applyExternalForce(...)
```

## Troubleshooting

### Import Errors

```bash
# Ensure Python path includes workspace root
export PYTHONPATH=/home/marcoreis/robust_mm_control_ws:$PYTHONPATH

# Or add at top of script
import sys
sys.path.insert(0, '/home/marcoreis/robust_mm_control_ws')
```

### PyBullet Connection Issues

```python
# Use explicit GUI mode
p.connect(p.GUI)

# Or DIRECT mode for headless
p.connect(p.DIRECT)
```

### GPU/CUDA Issues

```python
# Check device availability
import torch
print(f"CUDA available: {torch.cuda.is_available()}")

# Force CPU if GPU issues
device = torch.device('cpu')
```

## Related Documentation

- **Main README**: `/home/marcoreis/robust_mm_control_ws/README.md`
- **Training Guides**: `/home/marcoreis/robust_mm_control_ws/documentation/training_guides/`
- **Launchers**: `/home/marcoreis/robust_mm_control_ws/launchers/README.md`
- **Tests**: `/home/marcoreis/robust_mm_control_ws/test_scripts/README.md`
- **Tools**: `/home/marcoreis/robust_mm_control_ws/tools/README.md`

## Contributing

### Code Review Checklist
- [ ] Code follows PEP 8 style
- [ ] Docstrings added for new functions
- [ ] Tests added/updated
- [ ] No hardcoded paths
- [ ] Error handling implemented
- [ ] Performance impact assessed

### Pull Request Process
1. Create feature branch from `phase-algorithm-core`
2. Implement changes in appropriate module
3. Add tests for new functionality
4. Update relevant README files
5. Submit PR with clear description

---

**Last Updated**: November 2, 2025  
**Workspace**: `/home/marcoreis/robust_mm_control_ws/src`  
**Status**: Documented ✅
