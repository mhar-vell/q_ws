# Integration Guide for enhanced_rl_trainer.py

**File Location:** `/home/marcoreis/robust_mm_control_ws/tools/training/enhanced_rl_trainer.py`

This guide shows exactly what to add to integrate Phase 04.2 trajectory wrapper and Phase 06 W&B logging.

---

## Step 1: Add Imports (at top of file, after existing imports)

Add after the existing imports (around line 20):

```python
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Phase 04.2: Trajectory wrapper
from training_data.phase_04_state_optimization.04_2_trajectory_integration.trajectory_state_wrapper import TrajectoryStateWrapper

# Phase 06: W&B logging
from training_data.phase_06_monitoring_evaluation.logging_infrastructure.wandb_integration import WandBLogger
from training_data.phase_06_monitoring_evaluation.logging_infrastructure.metrics_collector import MetricsCollector, MetricsAggregator
```

---

## Step 2: Modify `__init__` Method

Find the `__init__` method (around line 29) and add these parameters and initializations:

**FIND:**
```python
def __init__(self, pybullet_client=None, husky_id=None, _id=None):
    self.p = pybullet_client
    self.husky_id = husky_id  
    self._id = _id
    
    # Training configuration
    self.scenarios = ['none', 'random', 'periodic', 'continuous', 'impulse']
    self.intensities = ['normal', 'golden']
    
    # Enhanced training parameters
    self.episodes_per_scenario = 2000  # Increased from 500
    self.max_steps_per_episode = 200
    
    # Results storage
    self.results = {}
    
    print("🚀 Enhanced RL Trainer initialized with Phase 1 improvements")
```

**REPLACE WITH:**
```python
def __init__(self, pybullet_client=None, husky_id=None, _id=None, 
             use_trajectory_wrapper=False, use_wandb=False, experiment_name=None):
    self.p = pybullet_client
    self.husky_id = husky_id  
    self._id = _id
    
    # Phase integration flags
    self.use_trajectory_wrapper = use_trajectory_wrapper
    self.use_wandb = use_wandb
    self.experiment_name = experiment_name or f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Training configuration
    self.scenarios = ['none', 'random', 'periodic', 'continuous', 'impulse']
    self.intensities = ['normal', 'golden']
    
    # Enhanced training parameters
    self.episodes_per_scenario = 2000  # Increased from 500
    self.max_steps_per_episode = 200
    
    # Results storage
    self.results = {}
    
    # Phase 06: Initialize W&B logger if requested
    if self.use_wandb:
        try:
            self.wandb_logger = WandBLogger(
                project="robust-mm-control",
                experiment_name=self.experiment_name,
                config={
                    'episodes_per_scenario': self.episodes_per_scenario,
                    'max_steps': self.max_steps_per_episode,
                    'use_trajectory_wrapper': use_trajectory_wrapper,
                },
                log_dir=f"wandb_logs/{self.experiment_name}"
            )
            self.metrics_collector = MetricsCollector()
            self.metrics_aggregator = MetricsAggregator()
            print("✅ W&B logging enabled")
        except Exception as e:
            print(f"⚠️  W&B initialization failed: {e}")
            self.use_wandb = False
    
    print(f"🚀 Enhanced RL Trainer initialized")
    print(f"   Trajectory wrapper: {'✅ Enabled' if use_trajectory_wrapper else '❌ Disabled'}")
    print(f"   W&B logging: {'✅ Enabled' if self.use_wandb else '❌ Disabled'}")
```

---

## Step 3: Add Waypoint Generation Method

Add this new method to the `EnhancedRLTrainer` class (anywhere after `__init__`):

```python
def _generate_trajectory_waypoints(self, start_pos, goal_pos, num_waypoints=5):
    """
    Generate trajectory waypoints between start and goal.
    
    Args:
        start_pos: Starting end-effector position [x, y, z]
        goal_pos: Goal position [x, y, z]
        num_waypoints: Number of intermediate waypoints
        
    Returns:
        List of waypoint positions
    """
    waypoints = []
    start = np.array(start_pos)
    goal = np.array(goal_pos)
    
    # Linear interpolation for now (can be enhanced later)
    for i in range(num_waypoints + 1):
        alpha = i / num_waypoints
        waypoint = start * (1 - alpha) + goal * alpha
        waypoints.append(waypoint.tolist())
    
    return waypoints
```

---

## Step 4: Modify `train_scenario` Method

Find the `train_scenario` method and wrap the environment creation:

**FIND (around line 76):**
```python
# Initialize environment with first trajectory point
env = MobileManipulatorEnv(
    pybullet_client=self.p,
    husky_id=self.husky_id,
    _id=self._id,
    goal_pose=trajectory[0]
)
env.current_disturbance = disturbance_type
```

**REPLACE WITH:**
```python
# Initialize environment with first trajectory point
base_env = MobileManipulatorEnv(
    pybullet_client=self.p,
    husky_id=self.husky_id,
    _id=self._id,
    goal_pose=trajectory[0]
)
base_env.current_disturbance = disturbance_type

# Phase 04.2: Wrap with trajectory state if enabled
if self.use_trajectory_wrapper:
    # Get initial EE position (extract from state)
    initial_state = base_env.get_state()
    start_pos = initial_state[17:20]  # EE position in Phase 03 state
    goal_pos = trajectory[0][:3]
    
    waypoints = self._generate_trajectory_waypoints(start_pos, goal_pos, num_waypoints=5)
    env = TrajectoryStateWrapper(base_env, waypoints, lookahead_count=3)
    print(f"✅ Using trajectory wrapper: {env.state_dim}D state")
else:
    env = base_env
    print(f"📊 Using base state: {env.state_dim}D")
```

---

## Step 5: Add Logging to Training Loop

Find the training loop in `train_scenario` (where episodes are executed) and add logging:

**FIND (the episode loop, around line 100+):**
```python
for episode in range(self.episodes_per_scenario):
    state = env.reset()
    # ... training code ...
    
    # After episode completes
    episode_reward = sum(episode_rewards)
    episode_results.append({
        'episode': episode,
        'reward': episode_reward,
        'steps': step,
        # ... other metrics ...
    })
```

**ADD after episode completes:**
```python
    # Phase 06: Log metrics to W&B
    if self.use_wandb and episode % 10 == 0:  # Log every 10 episodes
        episode_metrics = {
            'episode': episode,
            'reward': episode_reward,
            'steps': step,
            'epsilon': agent.epsilon if hasattr(agent, 'epsilon') else 0,
            'scenario': scenario_name,
        }
        
        # Add more metrics if available
        if hasattr(env, 'base_env'):
            # Get final error from wrapped env
            final_state = env.base_env.get_state()
            ee_pos = final_state[17:20]
            error = np.linalg.norm(ee_pos - trajectory[0][:3])
            episode_metrics['final_error'] = error
        
        self.wandb_logger.log_training_step(**episode_metrics)
```

---

## Step 6: Add Test Logging

If you have test episodes, add logging there too:

```python
# After test episode
if self.use_wandb:
    test_metrics = {
        'episode': current_episode,
        'scenario': scenario_name,
        'intensity': intensity_type,
        'mean_error': np.mean(test_errors),
        'success_rate': success_rate,
    }
    self.wandb_logger.log_test_results(**test_metrics)
```

---

## Step 7: Test the Integration

Create a test script `test_integration.py` in `/home/marcoreis/robust_mm_control_ws/`:

```python
#!/usr/bin/env python3
"""Test integration of Phase 04.2 + Phase 06"""

import sys
sys.path.insert(0, 'tools/training')

from enhanced_rl_trainer import EnhancedRLTrainer

# Test with trajectory wrapper only
print("Test 1: Trajectory wrapper only")
trainer1 = EnhancedRLTrainer(use_trajectory_wrapper=True, use_wandb=False)

# Test with W&B only  
print("\nTest 2: W&B logging only")
trainer2 = EnhancedRLTrainer(use_trajectory_wrapper=False, use_wandb=True, 
                            experiment_name="test_integration")

# Test with both
print("\nTest 3: Both enabled")
trainer3 = EnhancedRLTrainer(use_trajectory_wrapper=True, use_wandb=True,
                            experiment_name="test_full")

print("\n✅ Integration test complete!")
```

Run it:
```bash
cd /home/marcoreis/robust_mm_control_ws
python test_integration.py
```

---

## Usage Examples

### Train with Phase 04.2 trajectory wrapper:
```bash
cd /home/marcoreis/robust_mm_control_ws
python tools/training/enhanced_rl_trainer.py --use_trajectory_wrapper
```

### Train with W&B logging:
```bash
python tools/training/enhanced_rl_trainer.py --use_wandb --experiment_name phase_04_2_test
```

### Train with both:
```bash
python tools/training/enhanced_rl_trainer.py \
    --use_trajectory_wrapper \
    --use_wandb \
    --experiment_name phase_04_2_full
```

---

## Verification Checklist

After integration:

- [ ] File imports successfully (no ImportError)
- [ ] EnhancedRLTrainer initializes with new parameters
- [ ] Trajectory wrapper creates 59D state (when enabled)
- [ ] W&B logger initializes (when enabled)
- [ ] Test run completes without errors
- [ ] W&B dashboard shows data (visit wandb.ai)

---

## Troubleshooting

### Import Error: "No module named 'training_data'"
**Solution:** The path setup should handle this, but verify you're running from workspace root:
```bash
cd /home/marcoreis/robust_mm_control_ws
python tools/training/enhanced_rl_trainer.py
```

### State dimension mismatch
**Solution:** Verify wrapper is enabled:
```python
print(f"State dim: {env.state_dim}")  # Should be 59 with wrapper, 35 without
```

### W&B not logging
**Solution:** 
1. Install: `pip install wandb`
2. Login: `wandb login`
3. Check initialization didn't fail (look for error messages)

---

## Summary

**Files Modified:** 
- `/home/marcoreis/robust_mm_control_ws/tools/training/enhanced_rl_trainer.py`

**Changes:**
1. ✅ Added imports for trajectory wrapper and W&B
2. ✅ Added parameters to `__init__`
3. ✅ Added waypoint generation method
4. ✅ Wrapped environment creation
5. ✅ Added training logging
6. ✅ Added test logging

**Result:** Ready for Phase 04.2 experiments with comprehensive logging!
