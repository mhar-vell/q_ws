# RL Algorithms Implementation Summary

## Two Approaches Implemented

### 1. Tabular Q-Learning
**Class**: `QLearningAgent` in `rl_mission_env.py`

**How it works**:
- Maintains a dictionary Q-table: `{state: [Q-values for each action]}`
- Discretizes continuous states by rounding to 2 decimal places
- Updates Q-values using TD learning: `Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]`

**Hyperparameters**:
- Learning rate (α): 0.1
- Discount factor (γ): 0.99
- Exploration rate (ε): 0.2 → 0.01 (decays)

**Pros**:
- ✅ Simple and interpretable
- ✅ Fast updates per sample
- ✅ Works well for discrete/small state spaces
- ✅ No dependencies beyond NumPy

**Cons**:
- ❌ Doesn't scale to high-dimensional states
- ❌ Poor generalization (every state is independent)
- ❌ Memory grows with state space exploration

**Best for**: Testing, debugging, small state spaces

---

### 2. Deep Q-Network (DQN)
**Class**: `DQNAgent` in `rl_mission_env.py`

**How it works**:
- Neural network approximates Q-values: `Q(s,a) ≈ NN(s)[a]`
- Architecture: State → 128 → 128 → Action values
- Experience replay buffer (size: 10,000)
- Target network updated every 100 steps
- Trains on random mini-batches (size: 32)

**Hyperparameters**:
- Learning rate (α): 0.001
- Discount factor (γ): 0.99
- Exploration rate (ε): 1.0 → 0.01 (decays)
- Replay buffer: 10,000 transitions
- Batch size: 32
- Target update frequency: 100 steps

**Pros**:
- ✅ Handles high-dimensional continuous states
- ✅ Generalizes across similar states
- ✅ More sample efficient after warmup
- ✅ State-of-the-art performance

**Cons**:
- ❌ Requires PyTorch (dependency)
- ❌ Slower training initially
- ❌ More hyperparameters to tune
- ❌ Less interpretable

**Best for**: Production systems, complex environments, continuous control

---

## How to Choose

### Use **Tabular Q-Learning** if:
- State space is small/discrete
- You want fast prototyping
- Interpretability is important
- No GPU/PyTorch available
- Quick debugging needed

### Use **DQN** if:
- State space is high-dimensional (>10 dims)
- States are continuous
- Need good generalization
- Have PyTorch installed
- Want best performance

---

## Current Configuration

In `sim_husky_kuka.py`, around line 468:

```python
USE_DQN = True  # Set to False for Q-Learning
```

**Current**: DQN (if PyTorch available, else falls back to Q-Learning)

---

## Disturbance Scenarios

Both algorithms train on 5 disturbance scenarios:

1. **none** - Baseline (no disturbances)
2. **random** - Random forces every step (-50 to +50 N)
3. **periodic** - Large impulses every 50 steps (±100 N)
4. **continuous** - Constant low-level noise (-10 to +10 N)
5. **impulse** - Single large shock at step 25 (±200 N)

Agent learns robustness by training separately on each scenario.

---

## Training Process

```
For each scenario in ['none', 'random', 'periodic', 'continuous', 'impulse']:
    For each episode in [1..500]:
        Reset environment
        For each step in [1..200]:
            Select action (ε-greedy)
            Execute action
            Apply disturbance
            Observe reward & next state
            Update agent (Q-table or DQN)
            If goal reached: break (success)
        Track metrics: success rate, error, energy
    Save checkpoint every 100 episodes
    Save final model for scenario
Save all metrics to rl_metrics.json
```

---

## Model Saving

### Q-Learning
- Saves Q-table as pickle file: `rl_final_<scenario>_qtable.pkl`
- Checkpoint: `rl_checkpoint_<scenario>_ep<N>_qtable.pkl`

### DQN
- Saves neural network weights: `rl_final_<scenario>_dqn.pth`
- Includes: Q-network, target network, optimizer state, epsilon
- Checkpoint: `rl_checkpoint_<scenario>_ep<N>_dqn.pth`

---

## Expected Performance

### Tabular Q-Learning (500 episodes):
- **Success Rate**: 40-60%
- **Avg Error**: 0.05-0.10m
- **Training Time**: ~20-30 minutes
- **Q-table Size**: ~50,000-100,000 states

### DQN (500 episodes):
- **Success Rate**: 50-70%
- **Avg Error**: 0.03-0.07m
- **Training Time**: ~35-50 minutes
- **Replay Buffer**: 10,000 transitions
- **Better generalization** to unseen states

---

## Usage Examples

### Start Training (Interactive):
1. Run simulation: `python3 sim_husky_kuka.py`
2. Press **'t'** in PyBullet window
3. Training starts automatically
4. Monitor progress in terminal
5. Press **'t'** again to stop

### Switch Algorithms:
Edit line 468 in `sim_husky_kuka.py`:
```python
USE_DQN = False  # Use Tabular Q-Learning
USE_DQN = True   # Use DQN (default)
```

### Load Trained Model:
```python
# Q-Learning
rl_agent.load('rl_final_random')

# DQN
rl_agent.load('rl_final_continuous')
```

---

## Troubleshooting

### "PyTorch not available"
- DQN falls back to Q-Learning automatically
- Install PyTorch: `pip install torch`

### "Training too slow"
- Reduce episodes: `rl_num_episodes = 100`
- Use Q-Learning instead of DQN
- Reduce max_steps: `rl_max_steps = 100`

### "Agent not learning"
- Check reward function (should decrease error)
- Verify disturbances are applied correctly
- Increase episodes (try 2000+)
- Adjust learning rate
