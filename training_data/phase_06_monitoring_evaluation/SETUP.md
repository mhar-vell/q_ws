# Phase 06: Monitoring & Evaluation Setup Guide

**Time Required:** ~30 minutes  
**Prerequisites:** Working Python environment, Phase 03 training code

---

## Quick Start

### 1. Install Dependencies (2 min)

```bash
# Activate your conda environment
conda activate robust_mm_control

# Install Weights & Biases
pip install wandb

# Login to W&B (requires free account)
wandb login
```

### 2. Test W&B Integration (5 min)

```bash
cd training_data/phase_06_monitoring_evaluation/logging_infrastructure

# Run test script
python wandb_integration.py
```

Expected output:
```
✅ WandBLogger initialized
✅ Logged training step
✅ Test complete!
```

### 3. Verify Metrics Collector (2 min)

```bash
python metrics_collector.py
```

Expected output:
```
✅ Episode metrics collected
✅ Training summary computed
✅ Test complete!
```

---

## Integration with Training Code

### Step 1: Import Required Classes

Add to `/home/marcoreis/robust_mm_control_ws/tools/training/enhanced_rl_trainer.py`:

```python
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from training_data.phase_06_monitoring_evaluation.logging_infrastructure.wandb_integration import WandBLogger
from training_data.phase_06_monitoring_evaluation.logging_infrastructure.metrics_collector import MetricsCollector, MetricsAggregator
```

### Step 2: Initialize Logger

In `EnhancedRLTrainer.__init__()`:

```python
def __init__(self, ...):
    # ... existing code ...
    
    # Initialize W&B logger
    self.wandb_logger = WandBLogger(
        project="robust-mm-control",
        experiment_name=self.experiment_name,
        config={
            'algorithm': 'DQN',
            'learning_rate': self.learning_rate,
            'gamma': self.gamma,
            'epsilon_start': self.epsilon_start,
            'batch_size': self.batch_size,
            'replay_buffer_size': self.replay_buffer_size,
            'phase': 'Phase_04.2',  # Update per experiment
        },
        log_dir=f"wandb_logs/{self.experiment_name}"
    )
    
    # Initialize metrics collector
    self.metrics_collector = MetricsCollector()
    self.metrics_aggregator = MetricsAggregator()
```

### Step 3: Log Training Steps

In your training loop:

```python
def train_episode(self, episode):
    state = self.env.reset()
    done = False
    
    while not done:
        action = self.select_action(state)
        next_state, reward, done, info = self.env.step(action)
        
        # Get Q-values
        with torch.no_grad():
            q_values = self.policy_net(torch.FloatTensor(state).unsqueeze(0))
            q_values = q_values.squeeze().numpy()
        
        # Collect step metrics
        self.metrics_collector.add_step(
            state=state,
            action=action,
            reward=reward,
            q_values=q_values,
            error=info.get('position_error', None)
        )
        
        # Train network
        loss = self.update_network()
        if loss is not None:
            self.metrics_collector.add_step(loss=loss)
        
        state = next_state
    
    # End episode and log metrics
    episode_metrics = self.metrics_collector.end_episode()
    
    # Log to W&B
    self.wandb_logger.log_training_step(
        episode=episode,
        **episode_metrics
    )
    
    # Add to aggregator for later analysis
    self.metrics_aggregator.add_training_episode(episode, episode_metrics)
```

### Step 4: Log Test Results

In your test loop:

```python
def test_policy(self, episode, num_test_episodes=10):
    for test_ep in range(num_test_episodes):
        scenario, intensity = self._select_test_scenario()
        state = self.env.reset(scenario=scenario, intensity=intensity)
        done = False
        
        while not done:
            action = self.select_action(state, exploit=True)
            state, reward, done, info = self.env.step(action)
            
            # Collect test metrics
            self.metrics_collector.add_test_step(
                error=info['position_error'],
                ee_pos=info.get('ee_position', None),
                target_pos=info.get('target_position', None)
            )
        
        # End test episode
        test_metrics = self.metrics_collector.end_test_episode()
        
        # Log to W&B
        self.wandb_logger.log_test_results(
            episode=episode,
            scenario=scenario,
            intensity=intensity,
            **test_metrics
        )
        
        # Add to aggregator
        self.metrics_aggregator.add_test_episode(scenario, intensity, test_metrics)
```

### Step 5: Log Visualizations

Add after test runs:

```python
# Generate and log trajectory plot
if test_metrics.get('positions') and test_metrics.get('targets'):
    fig = self.wandb_logger.log_trajectory_plot(
        positions=test_metrics['positions'],
        targets=test_metrics['targets'],
        errors=test_metrics['errors'],
        episode=episode,
        scenario=scenario
    )
    plt.close(fig)

# Log error distribution
errors_all_tests = self.metrics_aggregator.test_history[f"{scenario}_{intensity}"]['mean_error']
if len(errors_all_tests) >= 10:
    fig = self.wandb_logger.log_error_distribution(
        errors=errors_all_tests,
        episode=episode
    )
    plt.close(fig)

# Log learning curve every 100 episodes
if episode % 100 == 0:
    training_errors = self.metrics_aggregator.training_history['mean_error']
    if len(training_errors) >= 10:
        fig = self.wandb_logger.log_learning_curve(
            episodes=list(range(len(training_errors))),
            metrics={'error': training_errors},
            episode=episode
        )
        plt.close(fig)
```

### Step 6: Save Checkpoints to W&B

Modify checkpoint saving:

```python
def save_checkpoint(self, episode):
    checkpoint_path = f"checkpoints/rl_checkpoint_ep{episode}.pth"
    torch.save({
        'episode': episode,
        'model_state_dict': self.policy_net.state_dict(),
        'optimizer_state_dict': self.optimizer.state_dict(),
        'epsilon': self.epsilon,
        'metrics': self.metrics_aggregator.get_training_summary(),
    }, checkpoint_path)
    
    # Log to W&B
    self.wandb_logger.log_model_checkpoint(
        model_path=checkpoint_path,
        episode=episode,
        metrics=self.metrics_aggregator.get_training_summary()
    )
    
    print(f"✅ Checkpoint saved and logged to W&B: {checkpoint_path}")
```

---

## W&B Dashboard Features

Once integrated, you'll have access to:

### 1. Real-time Training Metrics
- Reward progression
- Error reduction curves
- Loss dynamics
- Q-value statistics
- Action entropy

### 2. Test Performance Tracking
- Per-scenario accuracy
- Success rates over time
- Error distributions
- Trajectory visualizations

### 3. Comparative Analysis
- Compare multiple experiments side-by-side
- Phase 03 baseline vs Phase 04 experiments
- Ablation study comparisons

### 4. Model Management
- All checkpoints automatically versioned
- Easy rollback to best-performing models
- Training configuration stored with each model

---

## Testing the Integration

### Minimal Test Script

Create `test_wandb_integration.py`:

```python
import sys
sys.path.append('training_data/phase_06_monitoring_evaluation/logging_infrastructure')

from wandb_integration import WandBLogger
from metrics_collector import MetricsCollector
import numpy as np

# Initialize logger
logger = WandBLogger(
    project="robust-mm-control",
    experiment_name="integration_test",
    config={'test': True}
)

# Simulate training episode
collector = MetricsCollector()
for step in range(50):
    collector.add_step(
        action=np.random.randint(0, 10),
        reward=np.random.rand() * 10,
        q_values=np.random.rand(10),
        error=1.0 - step * 0.02
    )

metrics = collector.end_episode()
logger.log_training_step(episode=1, **metrics)

print("✅ Integration test complete!")
print(f"   View dashboard at: {logger.run.url}")
```

Run: `python test_wandb_integration.py`

---

## Troubleshooting

### Issue: wandb login fails
**Solution:** Create free account at https://wandb.ai/site, get API key from settings

### Issue: Too much disk space used
**Solution:** W&B stores data in `wandb/` folder. Clear old runs:
```bash
wandb sync --clean
```

### Issue: Slow logging during training
**Solution:** Log less frequently - every 10 episodes instead of every episode:
```python
if episode % 10 == 0:
    self.wandb_logger.log_training_step(...)
```

### Issue: Import errors
**Solution:** Verify Python path:
```python
import sys
print(sys.path)
# Ensure training_data/phase_06_monitoring_evaluation/logging_infrastructure is accessible
```

---

## Next Steps

After setup is complete:

1. ✅ Run integration test
2. ✅ Verify dashboard shows data
3. 🔄 Integrate into `enhanced_rl_trainer.py`
4. 🔄 Run Phase 03 baseline with logging (sanity check)
5. 🔄 Begin Phase 04.2 experiments with full logging

**Estimated Time for Full Integration:** 1-2 hours

---

## Success Criteria

Phase 06 setup is complete when:

- ✅ W&B account created and API key configured
- ✅ Test scripts run successfully
- ✅ Integration test shows data in W&B dashboard
- ✅ Training code modified to include logging
- ✅ One full training run (even 10 episodes) logs successfully

**Result:** Ready to begin Phase 04 experiments with comprehensive metric tracking!
