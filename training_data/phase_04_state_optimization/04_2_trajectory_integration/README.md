# Phase 04.2: Trajectory Integration

**Status:** ✅ State wrapper implemented, ready for training integration  
**Priority:** HIGH (identified as highest ROI experiment)  
**Expected Improvement:** 13-27% error reduction vs Phase 03

---

## Overview

Enhances the RL agent's state representation with **trajectory-aware features** to provide temporal context about the path ahead.

### State Enhancement

**Phase 03 Baseline:** 35D state
- Base pose, joint states, end-effector pose, IMU data

**Phase 04.2 Enhanced:** 59D state (35D + 24D)
- **Base state:** 35D (unchanged)
- **Next waypoints:** 18D (3 upcoming waypoints × 6 features each)
- **Progress metrics:** 6D (completion %, velocity alignment, etc.)

---

## Implementation

### ✅ Completed

1. **Trajectory State Wrapper** (`trajectory_state_wrapper.py`)
   - Wraps base environment to add trajectory features
   - Tracks waypoint progress automatically
   - Computes lookahead features for next 3 waypoints
   - Includes velocity estimation and alignment metrics

### Key Features Per Waypoint (6D)
1. **dx, dy, dz** - Relative position to waypoint
2. **distance** - Euclidean distance
3. **heading** - Horizontal angle (radians)
4. **elevation** - Vertical angle (radians)

### Progress Metrics (6D)
1. **Distance to goal** - Total remaining distance
2. **Completion %** - How far through trajectory
3. **Distance to current waypoint** - Next target distance
4. **Velocity magnitude** - Current motion speed
5. **Velocity alignment** - How well aligned with trajectory direction
6. **Waypoint density** - Average spacing of upcoming waypoints

---

## Next Steps

### Step 2: Integrate with Enhanced RL Trainer (1-2 hours)

Modify `/home/marcoreis/robust_mm_control_ws/tools/training/enhanced_rl_trainer.py` to use the wrapper:

```python
from training_data.phase_04_state_optimization.04_2_trajectory_integration.trajectory_state_wrapper import TrajectoryStateWrapper

class EnhancedRLTrainer:
    def __init__(self, ...):
        # ... existing code ...
        
        # Wrap environment with trajectory features
        if use_trajectory_wrapper:
            # Define trajectory waypoints (e.g., from goal sequence)
            waypoints = self._generate_trajectory_waypoints()
            self.env = TrajectoryStateWrapper(
                base_env=self.env,
                trajectory_waypoints=waypoints,
                lookahead_count=3
            )
            print(f"✅ Using Phase 04.2 state: {self.env.state_dim}D")
```

### Step 2: Generate Trajectory Waypoints

Add method to create waypoints from goals:

```python
def _generate_trajectory_waypoints(self, num_waypoints=5):
    """
    Generate intermediate waypoints between start and goal.
    
    For training: Can be simple linear interpolation
    For advanced: Use curved paths or learned trajectory generators
    """
    start_pos = self.env.base_env.get_state()[17:20]  # Current EE pos
    goal_pos = self.env.base_env.goal_pose[:3]
    
    # Linear interpolation
    waypoints = []
    for i in range(num_waypoints + 1):
        alpha = i / num_waypoints
        waypoint = start_pos * (1 - alpha) + goal_pos * alpha
        waypoints.append(waypoint)
    
    return waypoints
```

### Step 3: Update Network Architecture

The DQN network needs to handle 59D input instead of 35D:

```python
# In enhanced_rl_trainer.py, DQN class
class DQN(nn.Module):
    def __init__(self, state_dim=59, action_dim=19):  # ← Changed from 35
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_dim, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 128)
        self.fc4 = nn.Linear(128, action_dim)
```

### Step 4: Training Script

Create training script with W&B logging:

```bash
python enhanced_rl_trainer.py \
    --experiment_name phase_04_2_trajectory \
    --state_version v2 \
    --state_dim 59 \
    --episodes 2000 \
    --use_trajectory_wrapper \
    --use_wandb
```

### Step 5: Evaluation

After training, compare with Phase 03:

```python
# In comparative_analysis/statistical_tests.ipynb
phase03_results = load_test_results('phase_03/test_results.json')
phase04_results = load_test_results('phase_04_2/test_results.json')

comparison = compare_experiments(
    phase03_results['continuous_low'],
    phase04_results['continuous_low'],
    'Phase 03 Baseline (35D)',
    'Phase 04.2 Trajectory (59D)'
)

print(f"Improvement: {comparison['percent_improvement']:.1f}%")
print(f"Statistical significance: p={comparison['primary_test']['p_value']:.4f}")
```

---

## Expected Results

### Success Criteria

**Target:** ↓13-27% error reduction compared to Phase 03

**Phase 03 Baseline:**
- Mean error: 0.753m
- Success rate: 100%

**Phase 04.2 Target:**
- Mean error: <0.65m (↓13.7%)
- Success rate: ≥100%

### Why This Should Work

1. **Anticipatory Control:** Agent can "see" upcoming waypoints and plan ahead
2. **Velocity Alignment:** Explicit feedback about motion direction correctness
3. **Progress Awareness:** Knows how far along trajectory (early vs late adjustments)
4. **Trajectory Difficulty:** Waypoint density indicates complexity ahead

---

## Troubleshooting

### Issue: State dimension mismatch
**Solution:** Verify wrapper is being used:
```python
print(f"State dim: {env.state_dim}")  # Should be 59, not 35
```

### Issue: Wrapper slows down training
**Solution:** Trajectory features are lightweight (pure numpy), shouldn't impact speed

### Issue: No improvement over baseline
**Potential causes:**
1. Waypoints not informative (too few or too simple)
2. Network capacity insufficient for 59D input
3. Need more training episodes (try 3000 instead of 2000)
4. Trajectory features not properly normalized

---

## File Structure

```
phase_04_state_optimization/04_2_trajectory_integration/
├── README.md                          ✅ This file
├── trajectory_state_wrapper.py        ✅ State wrapper implementation
├── train_phase_04_2.py                📝 TODO: Training script
├── session_data/                      📝 Training outputs will go here
│   ├── checkpoints/
│   ├── test_results.json
│   └── training_log.json
└── experiments/                       📝 Experiment variations
    ├── linear_waypoints/
    ├── curved_waypoints/
    └── adaptive_waypoints/
```

---

## Timeline

**Estimated Time to Complete:**

- ✅ State wrapper implementation: **2 hours** (DONE)
- 🔄 Integration with trainer: **1-2 hours** (NEXT)
- 🔄 Initial training run (2000 ep): **4-6 hours**
- 🔄 Evaluation and comparison: **1 hour**
- 🔄 Statistical analysis: **30 min**

**Total:** ~1-2 days from now to Phase 04.2 results

---

## References

**Related Experiments:**
- Phase 03: Baseline (35D state, 2,500 training episodes)
- Phase 04.1: Temporal history (state history augmentation)
- Phase 04.3: Enhanced features (force/torque sensors)

**Key Papers:**
- Trajectory-aware RL for robotic manipulation
- Predictive state representations in continuous control
- Lookahead policies for sequential decision making

---

**Status Summary:**
- ✅ Wrapper implemented and tested
- 🔄 Ready for integration with training code
- ⏳ Waiting for training run to generate results
- ⏳ Statistical comparison pending

**Next Action:** Integrate wrapper into `enhanced_rl_trainer.py` and run training!
