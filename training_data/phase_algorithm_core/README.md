# Phase: Algorithm Core

## Overview
This phase contains training data from the **algorithm-core** branch development, focusing on algorithm-specific improvements and comparative analysis between DQN and Q-Learning approaches.

## Purpose
- Test and validate algorithm implementations (DQN vs Q-Learning)
- Establish algorithm-specific baselines
- Compare neural network vs tabular Q-learning performance
- Collect training metrics for algorithm comparison

## Branch Information
- **Branch**: `phase-algorithm-core`
- **Base**: `first-analysis`
- **Status**: Active Development

## Training Sessions

### 1. DQN Algorithm Core
**Directory**: `dqn_algorithm_core/`

- **Algorithm**: Deep Q-Network (DQN) with PyTorch
- **Episodes**: 2000 per scenario
- **Total Episodes**: 10,000 (5 scenarios)
- **Network Architecture**: Neural network with experience replay
- **Status**: ✅ Completed

**Results**:
- Comprehensive checkpoint files (ep100 - ep2000)
- Final models for all scenario-intensity combinations
- Performance metrics in JSON format

### 2. Q-Learning Algorithm Core
**Directory**: `qlearning_algorithm_core/`

- **Algorithm**: Tabular Q-Learning
- **Episodes**: 2000 per scenario
- **Total Episodes**: 10,000 (5 scenarios)
- **State Representation**: Discretized state space
- **Status**: ✅ Completed

**Results**:
- Q-table checkpoints at regular intervals
- Final Q-tables for all combinations
- Comparative performance metrics

## Directory Structure

```
phase_algorithm_core/
├── README.md                                  # This file
├── dqn_algorithm_core/
│   └── session_data/
│       ├── README.md                         # DQN session details
│       ├── checkpoints/                      # Training checkpoints
│       │   ├── continuous_scenario/          # 20 checkpoints (ep100-ep2000)
│       │   ├── impulse_scenario/             # 20 checkpoints
│       │   ├── none_scenario/                # 20 checkpoints
│       │   ├── periodic_scenario/            # 20 checkpoints
│       │   └── random_scenario/              # 20 checkpoints
│       ├── final_models/                     # Final trained models
│       │   ├── rl_final_continuous_golden_dqn.pth
│       │   ├── rl_final_continuous_normal_dqn.pth
│       │   ├── rl_final_impulse_golden_dqn.pth
│       │   ├── rl_final_impulse_normal_dqn.pth
│       │   ├── rl_final_none_golden_dqn.pth
│       │   ├── rl_final_none_normal_dqn.pth
│       │   ├── rl_final_periodic_golden_dqn.pth
│       │   ├── rl_final_periodic_normal_dqn.pth
│       │   ├── rl_final_random_golden_dqn.pth
│       │   └── rl_final_random_normal_dqn.pth
│       └── metrics/                          # Performance metrics
│           ├── rl_metrics_dqn.json
│           └── rl_final_metrics_shutdown_*.json
└── qlearning_algorithm_core/
    └── session_data/
        ├── README.md                         # Q-Learning session details
        ├── checkpoints/                      # Q-table checkpoints
        │   ├── continuous_scenario/          # 20 Q-table checkpoints
        │   ├── impulse_scenario/             # 20 Q-table checkpoints
        │   ├── none_scenario/                # 20 Q-table checkpoints
        │   ├── periodic_scenario/            # 20 Q-table checkpoints
        │   └── random_scenario/              # 20 Q-table checkpoints
        ├── final_models/                     # Final Q-tables
        │   ├── rl_final_continuous_golden_qtable.pkl
        │   ├── rl_final_continuous_normal_qtable.pkl
        │   ├── rl_final_impulse_golden_qtable.pkl
        │   ├── rl_final_impulse_normal_qtable.pkl
        │   ├── rl_final_none_golden_qtable.pkl
        │   ├── rl_final_none_normal_qtable.pkl
        │   ├── rl_final_periodic_golden_qtable.pkl
        │   ├── rl_final_periodic_normal_qtable.pkl
        │   ├── rl_final_random_golden_qtable.pkl
        │   └── rl_final_random_normal_qtable.pkl
        └── metrics/                          # Performance metrics
            └── rl_metrics_q-learning.json
```

## Training Scenarios

All scenarios trained at two intensity levels:

### Scenarios
1. **none** - No disturbances (baseline)
2. **random** - Random force impulses
3. **periodic** - Periodic disturbances
4. **continuous** - Continuous disturbances
5. **impulse** - High-intensity impulse disturbances

### Intensity Levels
- **normal** - Standard disturbance magnitude
- **golden** - Golden ratio multiplier (φ ≈ 1.618)

### Combinations
Total: 10 combinations (5 scenarios × 2 intensities)

## Key Differences from Phase 02

| Aspect | Phase 02 (dual_intensity_main) | Phase Algorithm Core |
|--------|--------------------------------|---------------------|
| **Purpose** | Thesis experiment | Algorithm development |
| **Episodes** | 500 per scenario | 2000 per scenario |
| **Focus** | Dual-intensity validation | Algorithm comparison |
| **Checkpoints** | Every 100 episodes (5 total) | Every 100 episodes (20 total) |
| **Branch** | `main` | `phase-algorithm-core` |
| **Status** | Production/Published | Development |

## Usage

### Loading DQN Models
```python
import torch
from rl_mission_env import DQNAgent

# Load a final model
agent = DQNAgent(state_dim=35, action_dim=10)
checkpoint = torch.load('training_data/phase_algorithm_core/dqn_algorithm_core/session_data/final_models/rl_final_continuous_normal_dqn.pth')
agent.q_network.load_state_dict(checkpoint['model_state_dict'])
agent.epsilon = checkpoint['epsilon']

# Load a specific checkpoint
checkpoint = torch.load('training_data/phase_algorithm_core/dqn_algorithm_core/session_data/checkpoints/continuous_scenario/rl_checkpoint_continuous_ep1000_dqn.pth')
```

### Loading Q-Learning Models
```python
import pickle
from rl_mission_env import QLearningAgent

# Load a final Q-table
with open('training_data/phase_algorithm_core/qlearning_algorithm_core/session_data/final_models/rl_final_continuous_normal_qtable.pkl', 'rb') as f:
    data = pickle.load(f)
    
agent = QLearningAgent(state_dim=35, action_dim=10)
agent.q_table = data['q_table']
agent.epsilon = data['epsilon']
```

### Analyzing Metrics
```python
import json

# Load DQN metrics
with open('training_data/phase_algorithm_core/dqn_algorithm_core/session_data/metrics/rl_metrics_dqn.json', 'r') as f:
    dqn_metrics = json.load(f)

# Load Q-Learning metrics
with open('training_data/phase_algorithm_core/qlearning_algorithm_core/session_data/metrics/rl_metrics_q-learning.json', 'r') as f:
    qlearning_metrics = json.load(f)

# Compare performance
print(f"DQN Success Rate: {dqn_metrics['overall_success_rate']:.1f}%")
print(f"Q-Learning Success Rate: {qlearning_metrics['overall_success_rate']:.1f}%")
```

## File Naming Conventions

### Checkpoints
- **DQN**: `rl_checkpoint_{scenario}_ep{episode}_dqn.pth`
- **Q-Learning**: `rl_checkpoint_{scenario}_ep{episode}_qtable.pkl`

### Final Models
- **DQN**: `rl_final_{scenario}_{intensity}_dqn.pth`
- **Q-Learning**: `rl_final_{scenario}_{intensity}_qtable.pkl`

### Metrics
- **DQN**: `rl_metrics_dqn.json`
- **Q-Learning**: `rl_metrics_q-learning.json`

## Related Documentation

- **Main README**: `/home/marcoreis/robust_mm_control_ws/README.md`
- **Training Guide**: `/home/marcoreis/robust_mm_control_ws/documentation/training_guides/`
- **Phase 02 Data**: `/home/marcoreis/robust_mm_control_ws/training_data/phase_02_dual_intensity_main/`
- **Tools**: `/home/marcoreis/robust_mm_control_ws/tools/`

## Analysis Tools

Use the following tools to analyze this phase's data:

```bash
# Check training status
python tools/diagnostics/check_phase1_status.py

# Analyze specific metrics
cd test_scripts/analysis_scripts
python rl_training_analysis.py

# Compare algorithms
python tools/data/compare_algorithms.py \
    --dqn training_data/phase_algorithm_core/dqn_algorithm_core/session_data/metrics/rl_metrics_dqn.json \
    --qlearning training_data/phase_algorithm_core/qlearning_algorithm_core/session_data/metrics/rl_metrics_q-learning.json
```

---

**Last Updated**: November 2, 2025  
**Branch**: phase-algorithm-core  
**Status**: Organized and Documented ✅
