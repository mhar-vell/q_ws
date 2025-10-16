# 🔄 DQN Training Checkpoints

This directory contains checkpoint models saved during training progression.

## 📋 Checkpoint Schedule
- **Episode 100**: Early learning phase - Basic trajectory understanding
- **Episode 200**: Competency development - Consistent circular motion
- **Episode 300**: Performance optimization - Improved accuracy and smoothness
- **Episode 400**: Advanced learning - Enhanced disturbance handling
- **Episode 500**: Pre-convergence checkpoint - Near-optimal performance

## 🎯 Usage Guidelines

### **Development & Testing**
- Use **Episode 100-200** for quick functionality testing
- Use **Episode 300** for balanced performance evaluation
- Use **Episode 500** for maximum performance demonstration

### **Research & Analysis**
- Compare learning progression across episodes
- Analyze convergence patterns by scenario
- Study disturbance adaptation over time

### **Model Selection**
Choose based on your requirements:
- **Speed**: Episode 100-200 (faster inference)
- **Balance**: Episode 300 (good performance/speed trade-off)
- **Performance**: Episode 500 (maximum accuracy)

## 📊 Expected Performance by Episode

| Episode | Trajectory Accuracy | Disturbance Handling | Training Stability |
|---------|-------------------|---------------------|-------------------|
| 100     | 40-60%            | Basic               | Moderate          |
| 200     | 60-70%            | Improved            | Good              |
| 300     | 70-80%            | Advanced            | Stable            |
| 400     | 75-85%            | Expert              | Very Stable       |
| 500     | 80-90%            | Optimal             | Fully Converged   |

## 🔍 File Naming Convention
`rl_checkpoint_{scenario}_ep{episode}_dqn.pth`

- **scenario**: none, random, periodic, continuous, impulse
- **episode**: 100, 200, 300, 400, 500
- **dqn**: Deep Q-Network algorithm identifier