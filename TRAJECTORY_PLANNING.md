# Trajectory Planning in RL-based Mobile Manipulator Control

## Overview

Your system implements **RL-based trajectory planning** for a Husky mobile base + KUKA manipulator system. The goal is to learn optimal control policies that enable precise end-effector trajectory following despite:
- Base motion disturbances
- Uncertain dynamics
- Environmental forces
- Sensor noise (IMU)

---

## What is Trajectory Planning?

**Trajectory planning** is the process of determining:
1. **Path** - Sequence of waypoints from start to goal
2. **Timing** - When to reach each waypoint (velocity profile)
3. **Controls** - Motor commands to execute the trajectory

### Traditional vs RL-based Approach

| Traditional Trajectory Planning | RL-based Trajectory Planning |
|--------------------------------|------------------------------|
| Pre-computed paths (A*, RRT) | Learned policies from experience |
| Fixed velocity profiles | Adaptive speed based on state |
| Open-loop control | Closed-loop feedback control |
| Requires accurate model | Model-free (learns from data) |
| Brittle to disturbances | Robust through training |
| No learning | Improves with experience |

---

## Your Implementation Architecture

### 1. **Trajectory Representation**

Your system defines trajectories as sequences of waypoints:

```python
target_trajectory = [
    (x1, y1, z1, rx1, ry1, rz1),  # Waypoint 1
    (x2, y2, z2, rx2, ry2, rz2),  # Waypoint 2
    ...
    (xn, yn, zn, rxn, ryn, rzn)   # Waypoint N
]
```

**Where**:
- `(x, y, z)` = End-effector position in world frame
- `(rx, ry, rz)` = End-effector orientation (Euler angles)

**Current setup**: 20 waypoints defining a circular or custom path

---

### 2. **State Space** (35 dimensions)

The RL agent observes a comprehensive state vector:

```
State = [
    Joint Positions (7)      # Current KUKA joint angles
    Joint Velocities (7)     # Joint angular velocities
    EE Position (3)          # End-effector (x, y, z)
    EE Orientation (3)       # End-effector (roll, pitch, yaw)
    Base Position (3)        # Husky base (x, y, z)
    Base Orientation (3)     # Husky (roll, pitch, yaw)
    IMU Accel (3)           # Accelerometer readings
    IMU Gyro (3)            # Gyroscope readings
    Trajectory Progress (3)  # [progress%, distance_to_target, time%]
]
Total: 35 dimensions
```

**Why this state?**
- **Joint states**: Current configuration
- **EE pose**: Know where we are
- **Base state**: Mobile platform affects arm
- **IMU data**: Detect disturbances early
- **Progress**: Know where in trajectory

---

### 3. **Action Space**

Two implementations available:

#### Option A: Discrete Joint Actions (Current)
```
Actions: 7 joints × 5 levels = 35 possible actions
Levels: [-2Δ, -Δ, 0, +Δ, +2Δ] where Δ = 0.05 radians

Example:
- Action 0: Joint 0 → -0.10 rad
- Action 1: Joint 0 → -0.05 rad
- Action 2: Joint 0 → 0.00 rad (hold)
- Action 3: Joint 0 → +0.05 rad
- Action 4: Joint 0 → +0.10 rad
...
- Action 34: Joint 6 → +0.10 rad
```

#### Option B: Continuous Joint Actions (Alternative)
```
Actions: Δθ = [Δθ1, Δθ2, ..., Δθ7]
Each Δθi ∈ [-π/36, π/36] radians
Requires policy gradient methods (PPO, SAC)
```

---

### 4. **Reward Function**

The reward guides learning toward desired behavior:

```python
reward = -distance_to_target          # Primary: reach target
         - 0.1 * action_magnitude     # Penalty: energy efficiency
         - 5.0 * collision            # Penalty: avoid collisions
         + 100.0 * waypoint_reached   # Bonus: reach waypoint
         - 0.5 * base_instability     # Penalty: smooth base motion
```

**Components**:

1. **Distance error** (`-distance_to_target`):
   - Euclidean distance from EE to current waypoint
   - Encourages approaching target
   - Dense reward (every step)

2. **Action cost** (`-0.1 * |action|`):
   - Penalizes large joint movements
   - Encourages energy-efficient paths
   - Promotes smooth trajectories

3. **Collision penalty** (`-5.0 if collision`):
   - Negative reward for self-collision
   - Negative reward for environment collision
   - Safety-critical

4. **Waypoint bonus** (`+100.0 if reached`):
   - Large positive reward for reaching waypoint
   - Moves to next waypoint
   - Sparse reward (critical moments)

5. **Base stability** (`-0.5 * IMU_magnitude`):
   - Penalizes excessive base acceleration
   - Promotes stable mobile base behavior
   - Uses IMU feedback

---

### 5. **Training Process**

#### Episode Structure:
```
1. Reset environment
   ├─ Robot returns to initial pose
   ├─ Trajectory index = 0
   └─ Clear history

2. For each step (max 200):
   ├─ Observe current state (35D)
   ├─ Select action (ε-greedy or network)
   ├─ Execute action (move joints)
   ├─ Apply disturbance (if scenario active)
   ├─ Step physics simulation
   ├─ Calculate reward
   ├─ Store experience (for DQN)
   ├─ Update agent (Q-table or network)
   └─ Check if done:
       ├─ Success: reached all waypoints
       ├─ Failure: timeout or collision
       └─ Continue otherwise

3. Log metrics
   ├─ Success rate
   ├─ Final error
   ├─ Steps taken
   └─ Energy consumed
```

#### Multi-Scenario Training:
```
For each disturbance scenario ['none', 'random', 'periodic', 'continuous', 'impulse']:
    Train for 500 episodes
    Agent learns scenario-specific strategies
    Save model checkpoint
```

---

### 6. **Trajectory Following Strategies**

The RL agent learns different strategies:

#### A. **Sequential Waypoint Following**
```
Current strategy: Move to waypoints in order
- Focus on current waypoint
- When within threshold (0.01m), advance to next
- Track progress through trajectory
- Success = reaching final waypoint
```

#### B. **Predictive Following** (Advanced)
```
Look ahead to next waypoints
- Anticipate upcoming trajectory changes
- Pre-adjust joint velocities
- Smoother transitions
- Requires additional state info
```

#### C. **Disturbance Compensation**
```
Learn from IMU feedback
- Detect base acceleration (disturbance)
- Adjust joint positions to compensate
- Maintain EE accuracy despite base motion
- Critical for mobile manipulation
```

---

### 7. **Key Challenges Addressed**

#### Challenge 1: **Mobile Base Coupling**
**Problem**: Mobile base motion affects arm end-effector position
**Solution**: 
- Include base state in observations
- Use IMU to detect base disturbances
- Learn coordinated base-arm control

#### Challenge 2: **High-Dimensional State**
**Problem**: 35D state space is large
**Solution**:
- DQN with neural network function approximation
- Experience replay for sample efficiency
- Target network for stability

#### Challenge 3: **Sparse Rewards**
**Problem**: Only get reward when reaching waypoints
**Solution**:
- Dense distance-based reward every step
- Shaping reward to guide toward waypoints
- Balance exploration vs exploitation

#### Challenge 4: **Disturbance Rejection**
**Problem**: External forces push robot off trajectory
**Solution**:
- Train on multiple disturbance scenarios
- IMU feedback in state vector
- Stability penalty in reward function

---

### 8. **Comparison with Alternatives**

#### vs Classical Control:
| Method | Pros | Cons |
|--------|------|------|
| **PID Control** | Simple, fast | Requires tuning, poor with disturbances |
| **MPC** | Optimal, predictive | Requires model, computationally expensive |
| **Jacobian Control** | Direct EE control | Singularities, no learning |
| **RL (Yours)** | Learns from data, robust | Needs training, slower convergence |

#### vs Motion Planning:
| Method | Pros | Cons |
|--------|------|------|
| **RRT/A*** | Complete, optimal | Offline, no adaptation |
| **Trajectory Optimization** | Smooth paths | Local optima, slow |
| **RL (Yours)** | Online adaptation | Requires exploration |

---

### 9. **Current Implementation Status**

✅ **Implemented**:
- Trajectory environment class
- State representation (35D)
- Action space (discrete joint control)
- Reward function with multiple components
- Q-learning agent
- DQN agent with experience replay
- Multi-scenario disturbance training
- Model checkpointing and saving

🚧 **Areas for Enhancement**:
- Velocity control (currently position-based)
- Continuous action space (PPO/SAC)
- Multi-step lookahead
- Hierarchical RL (base + arm policies)
- Sim-to-real transfer

---

### 10. **How It Works in Practice**

#### Example Trajectory Execution:

```
Initial State:
├─ EE at (0.5, 0.0, 0.3)
├─ Target waypoint 1 at (0.6, 0.1, 0.4)
└─ Distance = 0.14m

Step 1:
├─ Agent observes state (joints, EE, base, IMU)
├─ DQN outputs: Action 15 (move joint 3 by +0.05 rad)
├─ Execute action → EE moves to (0.52, 0.02, 0.32)
├─ Distance = 0.11m
├─ Reward = -0.11 - 0.005 = -0.115
└─ Update network

Step 2:
├─ Disturbance applied: Force = [10, -5, 0] N
├─ IMU detects: accel = [0.5, -0.25, 0] m/s²
├─ Agent selects compensating action
├─ EE stays near trajectory despite disturbance
└─ Reward = -0.09 - 0.5*0.56 = -0.37

...

Step 45:
├─ EE reaches waypoint 1 (distance < 0.01m)
├─ Reward = +100 (bonus!)
├─ Advance to waypoint 2
└─ Continue...

Episode End:
├─ All 20 waypoints reached
├─ Success! Save trajectory
└─ Metrics: error=0.008m, steps=890, energy=12.5
```

---

### 11. **Performance Metrics**

Your system tracks:

1. **Success Rate**: % of episodes reaching all waypoints
2. **Final Error**: Distance from EE to final target (meters)
3. **Steps Taken**: Episode length (efficiency)
4. **Energy**: Sum of action magnitudes (smoothness)
5. **Trajectory Error**: Average distance from path

**Target Performance** (after 2000 episodes):
- Success Rate: >80%
- Final Error: <0.01m (1cm precision)
- Energy: Minimal joint movements

---

### 12. **Visualization & Analysis**

After training, you can visualize:

```bash
python plot_rl_results.py
```

**Plots**:
- Success rate per scenario
- Average error vs episodes
- Energy consumption trends
- Trajectory tracking accuracy
- Learning curves (reward over time)

---

## Summary

Your **RL-based trajectory planner** learns to:
1. ✅ Follow end-effector trajectories accurately
2. ✅ Compensate for mobile base disturbances
3. ✅ Handle multiple disturbance scenarios
4. ✅ Optimize for energy efficiency
5. ✅ Generalize across different trajectories

**Key Innovation**: Unlike traditional planners, your system **adapts and improves** through experience, learning robust control policies that handle real-world uncertainties.

The combination of:
- **DQN** for high-dimensional control
- **IMU feedback** for disturbance detection
- **Multi-scenario training** for robustness
- **Mobile manipulation** for practical applicability

...makes this a sophisticated and practical trajectory planning system! 🚀
