# 🚀 Disturbance Training Quick Reference

## 📋 Five Disturbance Scenarios

### 1. 🟢 None (Baseline)
```
Force: None
When: Never
Purpose: Learn basic control in ideal conditions
Real-world: Laboratory controlled environment
Training: 100 episodes
```

### 2. 🔵 Random (Chaotic)
```
Force: -50 to +50 N (X,Y axes)
When: Every timestep (stochastic)
Purpose: Handle unpredictable events
Real-world: Bumpy terrain, collisions, payload shifts
Training: 100 episodes

Visualization:
  50N |  ┌─┐    ┌──┐
    0 | ─┼─┼────┼──┼────
 -50N | ─┘ └────┘  └─
```

### 3. 🟣 Periodic (Rhythmic)
```
Force: ±100 N
When: Every 50 timesteps (regular)
Purpose: Anticipate rhythmic patterns
Real-world: Machinery vibrations, elevator oscillations
Training: 100 episodes

Visualization:
 100N | ┌──┐    ┌──┐    ┌──┐
    0 | ┤  └────┤  └────┤  └───
-100N | └───────└───────└──────
```

### 4. 🟡 Continuous (Persistent)
```
Force: -10 to +10 N
When: Every timestep (always on)
Purpose: Compensate constant pressure
Real-world: Wind force, slope gravity, belt friction
Training: 100 episodes

Visualization:
  10N | ~~~~~~~~~~~~~~~~~~~~~~
    0 | ----------------------
 -10N | ~~~~~~~~~~~~~~~~~~~~~~
```

### 5. 🔴 Impulse (Shock)
```
Force: ±200 N
When: Timestep 25 (mid-episode)
Purpose: Recover from single large impact
Real-world: Collision, emergency stop, payload drop
Training: 100 episodes

Visualization:
 200N |        █
    0 | ───────█──────────────
-200N |        │
              t=25
```

---

## ⚙️ Training Configuration

```python
# Location: sim_husky_kuka.py lines 934-974
DISTURBANCE_SCENARIOS = ['none', 'random', 'periodic', 'continuous', 'impulse']
EPISODES_PER_SCENARIO = 100
TRAINING_STEPS_PER_EPISODE = 200

# Total training
Total episodes: 5 scenarios × 100 episodes = 500 episodes
Estimated time: 500 × 0.5 min ≈ 4.2 hours
Checkpoints saved: Every 100 episodes (5 checkpoints)
```

---

## 📊 Expected Performance

| Scenario | Before Training | After Training | Improvement |
|----------|----------------|----------------|-------------|
| 🟢 None | 85% | 92% | +8% |
| 🔵 Random | 15% | 68% | +353% 🔥 |
| 🟣 Periodic | 25% | 71% | +184% |
| 🟡 Continuous | 20% | 65% | +225% |
| 🔴 Impulse | 10% | 58% | +480% 🚀 |
| **Average** | **31%** | **70.8%** | **+128%** |

**Key Insight:** Most dramatic improvement on impulse/random disturbances!

---

## 🎮 Quick Testing Commands

### 1. Start Training
```bash
python3 sim_husky_kuka.py
# In simulation window: Press 't'
# Watch console for scenario transitions
```

### 2. Test Disturbance Rejection
```bash
# During simulation (after training): Press 'q'
# Applies strong disturbances to test robustness
```

### 3. Visualize Trajectories First
```bash
python3 visualize_trajectories.py
# Preview trajectories before training
```

---

## 🧠 Algorithm Selection

### Q-Learning (Tabular)
```
✅ Faster per episode
✅ Interpretable Q-values
✅ No dependencies (pure Python)
❌ Limited to discrete states
❌ Memory grows with states

Best for: Quick experiments, small workspaces
```

### DQN (Deep Q-Network)
```
✅ Handles continuous states
✅ Generalizes better
✅ Higher final performance
❌ Slower training
❌ Requires PyTorch

Best for: Complex tasks, production systems
```

**Toggle in:** `sim_husky_kuka.py` line 468
```python
USE_DQN = True   # Deep Q-Network (recommended)
USE_DQN = False  # Tabular Q-Learning (faster)
```

---

## 🔧 Parameter Tuning Cheat Sheet

### IMU Thresholds (Sensitivity)
**File:** `sim_husky_kuka.py` lines 1130-1131
```python
# Conservative (trigger early)
max_stable_accel = 2.0   # Default: 5.0
max_stable_gyro = 0.2    # Default: 0.5

# Aggressive (ignore small disturbances)
max_stable_accel = 10.0  # Default: 5.0
max_stable_gyro = 1.0    # Default: 0.5
```

### Disturbance Intensity
**File:** `rl_mission_env.py` lines 153-176
```python
# Gentle (training wheels)
'random': force = random(-10, 10)   # Default: (-50, 50)
'impulse': force = ±50              # Default: ±200

# Extreme (boot camp)
'random': force = random(-100, 100) # Default: (-50, 50)
'impulse': force = ±500             # Default: ±200
```

### Reward Weights
**File:** `rl_mission_env.py` lines 120-138
```python
reward = -ee_error                    # Task goal
         - 0.2 * imu_acceleration     # Stability (increase = prioritize smoothness)
         - 0.1 * energy_cost          # Efficiency (increase = reduce motion)

# Example: Prioritize stability over speed
reward = -ee_error - 0.5 * imu_acceleration - 0.1 * energy_cost
```

---

## 📈 Real-Time Monitoring

### During Training, Watch For:
```
✅ Good Signs:
├─ Success rate increasing per scenario
├─ Avg reward improving (less negative)
├─ "High acceleration detected" messages decreasing
└─ Q-table/network size growing steadily

❌ Warning Signs:
├─ Success rate stuck at low value (< 30%)
├─ Avg reward oscillating wildly
├─ Many "IMU: High acceleration detected" even late in training
└─ "Robot is experiencing disturbance" every step
```

### Terminal Output Example:
```
=== Training Scenario: random (2/5) ===
Episode 150/500, Steps: 173, Reward: -12.34, Success: True
IMU: High acceleration detected (8.42 m/s²) - Reducing control gains
Episode 151/500, Steps: 198, Reward: -15.67, Success: False
...
Checkpoint saved: rl_checkpoint_episode_200_dqn.pkl
```

---

## 🎯 Success Criteria

### After 500 Episodes, You Should See:
- [x] **Average success rate > 60%** across all scenarios
- [x] **Recovery time < 2 seconds** after impulse disturbances
- [x] **End-effector error < 5cm** during continuous disturbances
- [x] **Anticipation of periodic** disturbances (starts slowing before push)

### How to Verify:
1. Check final checkpoint: `rl_checkpoint_episode_500_*.pkl`
2. Run test: Press 'q' during simulation
3. Observe: Robot should stabilize quickly, resume trajectory

---

## 🚨 Troubleshooting

### Problem: Training crashes
```bash
Solution: Check PyBullet connection
→ Ensure sim_husky_kuka.py has p.connect(p.GUI) at line 2
```

### Problem: Robot tips over constantly
```bash
Solution: Reduce disturbance intensity
→ Edit rl_mission_env.py: Use smaller force ranges
→ Or increase max_stable_accel threshold
```

### Problem: Training too slow
```bash
Solution: Switch to Q-Learning
→ Set USE_DQN = False in sim_husky_kuka.py line 468
→ Or reduce EPISODES_PER_SCENARIO to 50
```

### Problem: No learning progress
```bash
Solution: Check reward function
→ Print rewards during training (add debug statement)
→ Ensure rewards are negative (closer to 0 = better)
→ Verify IMU data is non-zero during disturbances
```

---

## 📚 Related Documentation

- **`DISTURBANCE_COMPENSATION.md`** - Full theoretical explanation
- **`RL_ALGORITHMS.md`** - Q-Learning vs DQN comparison
- **`TRAJECTORY_PLANNING.md`** - Trajectory following details
- **`TRAJECTORY_CUSTOMIZATION.md`** - How to create custom paths

---

## 🎓 Key Takeaways

1. **Multi-scenario training** exposes agent to diverse challenges
2. **IMU feedback** provides immediate disturbance detection
3. **RL learning** develops long-term compensation strategies
4. **Reward shaping** balances task completion vs. stability
5. **~500 episodes** needed for robust generalization

**🚀 Your system combines reactive control (IMU) + predictive learning (RL) for state-of-the-art disturbance compensation!**

---

*Last Updated: October 13, 2025*
