# Training Session: Q-Learning Algorithm Core

## Status
✅ **COMPLETED**

## Overview
- **Session ID**: `algorithm_core_qlearning_2000ep`
- **Algorithm**: Tabular Q-Learning
- **Phase**: Algorithm Core Development
- **Episodes**: 2000 per scenario
- **Total Episodes**: 10,000 (5 scenarios × 2 intensities)
- **Branch**: phase-algorithm-core

## Purpose
Tabular Q-Learning baseline training for algorithm comparison with DQN. Provides classical RL performance benchmarks and validates discretization strategies.

## Configuration

### Algorithm Parameters
- **Algorithm**: Tabular Q-Learning
- **State Space**: Discretized (grid-based)
- **Action Space**: Discrete (10 actions)
- **Learning Rate**: α = 0.1
- **Discount Factor**: γ = 0.99
- **Exploration**: ε-greedy (0.3 constant or decaying)
- **Q-Table**: Dictionary-based state-action values
- **Update Rule**: Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') - Q(s,a)]

### State Representation
- **State Dimension**: 35 continuous features
- **Discretization**: Binning into discrete ranges
- **State Space Size**: Large (product of discretization bins)

### Action Space
10 discrete actions controlling:
- Base velocity (forward/backward/rotate)
- Arm joint movements
- Combined base-arm coordination

### Training Scenarios
All scenarios trained at two intensity levels:

#### 1. **None** (Baseline)
- No external disturbances
- Clean environment for optimal learning
- **Episodes**: 2000

#### 2. **Random**
- Random force impulses
- Tests adaptability to unpredictable events
- **Episodes**: 2000

#### 3. **Periodic**
- Periodic disturbance pattern
- Tests learning of recurring patterns
- **Episodes**: 2000

#### 4. **Continuous**
- Continuous low-level disturbances
- Tests sustained adaptation
- **Episodes**: 2000

#### 5. **Impulse**
- High-intensity impulse disturbances
- Tests extreme event recovery
- **Episodes**: 2000

### Intensity Levels
- **Normal**: Standard disturbance magnitude
- **Golden**: Golden ratio multiplier (φ ≈ 1.618)

## Directory Structure

```
qlearning_algorithm_core/
└── session_data/
    ├── README.md                              # This file
    ├── checkpoints/                           # Q-table checkpoints
    │   ├── continuous_scenario/               # 20 checkpoints (ep100-2000)
    │   │   ├── rl_checkpoint_continuous_ep100_qtable.pkl
    │   │   ├── rl_checkpoint_continuous_ep200_qtable.pkl
    │   │   ├── ...
    │   │   └── rl_checkpoint_continuous_ep2000_qtable.pkl
    │   ├── impulse_scenario/                  # 20 checkpoints
    │   ├── none_scenario/                     # 20 checkpoints
    │   ├── periodic_scenario/                 # 20 checkpoints
    │   └── random_scenario/                   # 20 checkpoints
    ├── final_models/                          # Final Q-tables
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
    └── metrics/                               # Performance metrics
        └── rl_metrics_q-learning.json        # Training metrics
```

## Training Progress

✅ **none_normal** (2000 episodes) - Checkpoints: ep100-ep2000  
✅ **none_golden** (2000 episodes) - Checkpoints: ep100-ep2000  
✅ **random_normal** (2000 episodes) - Checkpoints: ep100-ep2000  
✅ **random_golden** (2000 episodes) - Checkpoints: ep100-ep2000  
✅ **periodic_normal** (2000 episodes) - Checkpoints: ep100-ep2000  
✅ **periodic_golden** (2000 episodes) - Checkpoints: ep100-ep2000  
✅ **continuous_normal** (2000 episodes) - Checkpoints: ep100-ep2000  
✅ **continuous_golden** (2000 episodes) - Checkpoints: ep100-ep2000  
✅ **impulse_normal** (2000 episodes) - Checkpoints: ep100-ep2000  
✅ **impulse_golden** (2000 episodes) - Checkpoints: ep100-ep2000  

## Checkpoint Information

### Checkpoint Frequency
Checkpoints saved every **100 episodes** (ep100, ep200, ..., ep2000)

### Checkpoint Contents
Each `.pkl` file contains:
- `q_table`: Dictionary of state-action values
- `epsilon`: Current exploration rate
- `episode`: Episode number
- `state_visits`: (optional) State visit counts
- `learning_rate`: (optional) Current learning rate

### File Size
- **Per checkpoint**: ~500 KB - 2 MB (depending on Q-table size)
- **Total checkpoints**: 100 files (5 scenarios × 20 checkpoints)
- **Total size**: ~50-200 MB

## Final Models

### Model Information
Final Q-tables represent the learned state-action values after 2000 episodes of training for each scenario-intensity combination.

### Usage
```python
import pickle
from rl_mission_env import QLearningAgent

# Initialize agent
agent = QLearningAgent(state_dim=35, action_dim=10)

# Load final Q-table
with open('final_models/rl_final_continuous_normal_qtable.pkl', 'rb') as f:
    data = pickle.load(f)

agent.q_table = data['q_table']
agent.epsilon = data['epsilon']

# Use for evaluation
agent.epsilon = 0.0  # No exploration during evaluation
```

## Q-Learning Characteristics

### Advantages
- **Simple Implementation**: No neural network required
- **Guaranteed Convergence**: Under certain conditions
- **Interpretable**: Q-values directly visible
- **No Replay Buffer**: Updates immediate

### Challenges
- **State Space Explosion**: Large continuous spaces difficult
- **Discretization**: Loss of precision
- **Memory**: Large Q-tables for complex domains
- **Generalization**: Poor for unseen states

## Metrics

### Available Metrics
- **Success Rate**: Task completion percentage
- **Average Error**: Mean distance to target
- **Episode Length**: Steps per episode
- **Q-Table Size**: Number of state-action pairs learned
- **Convergence**: Episode at which Q-values stabilize

### Metrics Files
- `rl_metrics_q-learning.json`: Detailed training metrics

## Comparison with DQN

### Expected Differences
| Metric | Q-Learning | DQN | Reason |
|--------|-----------|-----|--------|
| Success Rate | Lower | Higher | DQN generalizes better |
| Training Speed | Slower | Faster | Large state space |
| Memory Usage | Variable | Fixed | Q-table grows dynamically |
| Convergence | Slower | Faster | DQN uses experience replay |

### Running Comparison
```bash
cd /home/marcoreis/robust_mm_control_ws/test_scripts/analysis_scripts
python compare_algorithms.py \
    --dqn ../../training_data/phase_03_algorithm_core/dqn_algorithm_core/session_data/metrics/rl_metrics_dqn.json \
    --qlearning ../../training_data/phase_03_algorithm_core/qlearning_algorithm_core/session_data/metrics/rl_metrics_q-learning.json
```

## Algorithm Details

### Q-Value Update
```
Q(s,a) ← Q(s,a) + α[r + γ·max_a' Q(s',a') - Q(s,a)]

Where:
- s: current state
- a: action taken
- r: reward received
- s': next state
- α: learning rate (0.1)
- γ: discount factor (0.99)
```

### Exploration Strategy
```python
# ε-greedy policy
if random() < epsilon:
    action = random_action()  # Explore
else:
    action = argmax_a Q(s,a)  # Exploit
```

### State Discretization
Continuous state features binned into discrete ranges:
- Position: ±5m in 0.1m bins
- Velocity: ±2m/s in 0.2m/s bins
- Orientation: ±π in π/8 bins
- IMU data: Scaled and binned appropriately

## Related Sessions

- **DQN Algorithm Core**: `../dqn_algorithm_core/`
- **Phase 01 Q-Learning Baseline**: `../../phase_01_baseline_testing/qlearning_baseline/`

## Analysis Tools

```bash
# Check Q-Learning training status
python tools/diagnostics/check_phase1_status.py

# Analyze Q-table statistics
python tools/data/analyze_qtable.py \
    --qtable training_data/phase_03_algorithm_core/qlearning_algorithm_core/session_data/final_models/rl_final_continuous_normal_qtable.pkl

# Compare with DQN
python test_scripts/analysis_scripts/rl_training_analysis.py
```

## Performance Notes

- **Best Performance**: None scenario (no disturbances)
- **Challenging**: Golden intensity scenarios
- **Limitation**: State space discretization affects precision
- **Strength**: Works without GPU/PyTorch dependencies

## Future Improvements

Potential enhancements for Q-Learning performance:
1. **Finer Discretization**: More bins for better precision
2. **Function Approximation**: Tile coding or coarse coding
3. **Adaptive Learning Rate**: Decay α over time
4. **Eligibility Traces**: Q(λ) for faster learning
5. **Prioritized Sweeping**: Focus updates on important states

---

**Session Branch**: phase-algorithm-core  
**Training Date**: 2025  
**Status**: Completed and Archived ✅  
**Last Updated**: November 2, 2025
