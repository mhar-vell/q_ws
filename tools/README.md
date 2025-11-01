# Development Tools

This directory contains utility scripts for diagnostics, training, and maintenance of the robust mobile manipulator control system.

## Directory Structure

```
tools/
├── README.md                          # This file
├── diagnostics/                       # System monitoring and analysis tools
│   ├── check_phase1_status.py        # Phase 1 training progress monitor
│   └── physics_diagnostics.py        # Physics constraint analysis
├── training/                          # Training systems and utilities
│   └── enhanced_rl_trainer.py        # Enhanced RL training system
├── checkpoint_management/             # Model checkpoint utilities
│   └── manage_checkpoints.sh         # Checkpoint backup and cleanup
├── setup/                             # Setup and installation utilities
└── data/                              # Data processing and analysis tools
```

## Quick Reference

| Tool | Purpose | Usage |
|------|---------|-------|
| `check_phase1_status.py` | Monitor training progress | `python tools/diagnostics/check_phase1_status.py` |
| `physics_diagnostics.py` | Analyze physics issues | `python tools/diagnostics/physics_diagnostics.py` |
| `enhanced_rl_trainer.py` | Advanced RL training | Used by simulation scripts |
| `manage_checkpoints.sh` | Clean up checkpoints | `bash tools/checkpoint_management/manage_checkpoints.sh` |

---

## Diagnostics Tools

### 1. `check_phase1_status.py` - Phase 1 Training Status Monitor

**Purpose:** Real-time monitoring of Phase 1 RL training progress and performance analysis.

**Features:**
- ✅ PyTorch installation verification
- 📊 Training results analysis from JSON files
- 📈 Performance metrics by scenario
- 🎯 Phase 1 target progress (25% → 40% improvement)
- 🧠 DQN vs Q-Learning comparison
- 💡 Next steps recommendations

**Usage:**
```bash
python tools/diagnostics/check_phase1_status.py
```

**Output Includes:**
- Overall success rate across all scenarios
- Performance breakdown by disturbance type and intensity
- Best/worst performing scenarios
- Algorithm comparison (DQN vs Q-Learning)
- Phase 1 target achievement status
- Actionable next steps

**Example Output:**
```
🔍 PHASE 1 TRAINING STATUS MONITOR
=============================================
Timestamp: 2025-11-01 04:20:00
PyTorch Status: ✅ Available (cuda)

📁 Latest Results File: enhanced_rl_results_phase1_20251101_042000.json

📊 PHASE 1 PERFORMANCE ANALYSIS
========================================
Overall Performance: 42.3%
Average Error: 0.0234m
Agent Types Used: DQN, Q-Learning

📈 PERFORMANCE BY SCENARIO:
  🧠📊 none_normal          :  65.2% (error: 0.0145m)
  🧠⚡ continuous_golden   :  38.7% (error: 0.0289m)
  🧠⚡ impulse_high        :  28.4% (error: 0.0367m)

🎯 PHASE 1 TARGET ANALYSIS:
  ✅ SUCCESS: Target achieved! +17.3% improvement

💡 NEXT STEPS:
  🎉 Phase 1 complete! Ready for Phase 2 improvements
  → State representation optimization
  → Advanced curriculum learning
  → Target: 55-60% performance
```

**When to Use:**
- After training sessions to check progress
- To verify Phase 1 improvements are working
- To compare algorithm performance
- Before starting Phase 2 development
- For debugging training issues

---

### 2. `physics_diagnostics.py` - Physics Constraint Analyzer

**Purpose:** Diagnose physics instability issues in the Husky-KUKA coupling system.

**Features:**
- 🔍 URDF loading analysis
- ⚠️ Constraint force evaluation
- 📊 Physics instability indicators
- 🎯 Root cause identification
- 💡 Solution recommendations

**Usage:**
```bash
python tools/diagnostics/physics_diagnostics.py
```

**Analysis Includes:**
- URDF configuration review
- Constraint force analysis
- Mass distribution assessment
- Solver stability checks
- Recommended parameter adjustments

**Example Output:**
```
=== PHYSICS DIAGNOSTICS ANALYSIS ===

🔍 URDF LOADING ANALYSIS:
   1. Husky Robot: 'husky/husky.urdf' - SEPARATE URDF
   2. KUKA Arm: 'kuka_iiwa/model_free_base.urdf' - SEPARATE URDF
   3. Ground Plane: 'plane.urdf' - SEPARATE URDF
   → VERDICT: Multiple separate URDFs connected via constraints

⚠️  CONSTRAINT FORCE ANALYSIS:
   Current Max Force: 50,000N
   Recommended Force: 1,000N
   Ratio: 50.0x TOO HIGH

🎯 JUMPING ROOT CAUSES:
   1. CONSTRAINT OVER-FORCE: 50kN creates explosive corrections
   2. RIGID CONNECTION: No damping between bodies
   3. SOLVER INSTABILITY: High forces overwhelm physics solver

💡 RECOMMENDED SOLUTIONS:
   IMMEDIATE: Reduce constraint maxForce from 50,000N to 1,000-5,000N
   STABILITY: Add constraint damping and spring parameters
   COMPLIANCE: Use 6DOF constraint with limited forces
```

**When to Use:**
- Robot jumping or bouncing issues
- Constraint breaking/disconnection
- Physics instability during training
- Before adjusting constraint parameters
- For understanding coupling dynamics

---

## Training Tools

### 3. `enhanced_rl_trainer.py` - Enhanced RL Training System

**Purpose:** Phase 1 implementation of improved RL training with enhanced rewards and curriculum learning.

**Features:**
- 🧠 DQN forcing with PyTorch integration
- 📈 Progressive reward system with multiple tiers
- 🎓 Curriculum learning with graduated success criteria
- 🔄 Dynamic goal updates (circular trajectories)
- 💾 Automatic checkpoint saving
- 📊 Comprehensive performance reporting

**Integration:**
This script is imported and used by the main simulation scripts. Not typically run standalone.

**Usage in Code:**
```python
from tools.training.enhanced_rl_trainer import EnhancedRLTrainer

# Initialize trainer
trainer = EnhancedRLTrainer(
    pybullet_client=p,
    husky_id=husky,
    kuka_id=kuka
)

# Run full training
trained_agents = trainer.run_full_training()
```

**Key Improvements:**
- **Enhanced Reward Function**: Multi-tier progressive rewards
- **Relaxed Success Criteria**: 5cm → 3cm → 2cm progression
- **DQN Architecture**: Improved neural network design
- **Curriculum Learning**: Adaptive difficulty adjustment
- **Golden Ratio Intensity**: 1.618x multiplier for challenging scenarios

**Training Scenarios:**
- `none` - No disturbances (baseline)
- `random` - Random impulses
- `periodic` - Periodic disturbances
- `continuous` - Continuous sinusoidal
- `impulse` - High-intensity impulses

**Intensity Levels:**
- `normal` - Standard training intensity
- `golden` - 1.618x intensity multiplier

**Output Files:**
- `enhanced_rl_results_phase1_<timestamp>.json` - Training metrics
- `enhanced_agent_<scenario>.pth` - Saved agent models

**Performance Targets:**
- Baseline: ~25% success rate
- Phase 1 Target: 40-45% success rate
- Phase 2 Target: 55-60% success rate

---

## Checkpoint Management Tools

### 4. `manage_checkpoints.sh` - Checkpoint Management Script

**Purpose:** Backup, cleanup, and organization of RL training checkpoints.

**Features:**
- 📦 Automatic checkpoint backup with timestamps
- 🧹 Cleanup of old/intermediate checkpoints
- 📊 Checkpoint size analysis
- 🔍 Latest checkpoint identification
- 💾 Compression and archiving

**Usage:**
```bash
# Basic usage
bash tools/checkpoint_management/manage_checkpoints.sh

# With specific operations (edit script to customize)
# - backup: Create timestamped backup
# - cleanup: Remove intermediate checkpoints
# - analyze: Show checkpoint statistics
```

**Typical Cleanup Strategy:**
- Keep final checkpoints (ep2000)
- Keep milestone checkpoints (every 500 episodes)
- Archive intermediate checkpoints to backup directory
- Remove duplicate or corrupted files

**Example Workflow:**
```bash
# Before long training run
bash tools/checkpoint_management/manage_checkpoints.sh backup

# After training completion
bash tools/checkpoint_management/manage_checkpoints.sh cleanup

# Check checkpoint status
ls -lh rl_checkpoint_*.pth | wc -l
```

**Checkpoint Naming Convention:**
- `rl_checkpoint_<scenario>_ep<number>_<algorithm>.pth` - Training checkpoints
- `rl_final_<scenario>_<intensity>_<algorithm>.pth` - Final trained models
- `rl_checkpoint_<scenario>_ep<number>_qtable.pkl` - Q-Learning tables

---

## Common Workflows

### Development Workflow

```bash
# 1. Check training status
python tools/diagnostics/check_phase1_status.py

# 2. If physics issues occur
python tools/diagnostics/physics_diagnostics.py

# 3. Run training (via launcher)
python launchers/launch_enhanced_simulation.py

# 4. Check progress periodically
watch -n 60 python tools/diagnostics/check_phase1_status.py

# 5. After training, clean up checkpoints
bash tools/checkpoint_management/manage_checkpoints.sh cleanup
```

### Debugging Physics Issues

```bash
# 1. Analyze current physics configuration
python tools/diagnostics/physics_diagnostics.py

# 2. Review output recommendations
# 3. Adjust constraint parameters in sim_husky_kuka.py
# 4. Test with GUI launcher
python launchers/launch_gui_simulation.py

# 5. Verify improvements
python tools/diagnostics/physics_diagnostics.py
```

### Training Progress Monitoring

```bash
# Continuous monitoring during long training runs
watch -n 30 python tools/diagnostics/check_phase1_status.py

# Or set up in separate terminal
while true; do
    clear
    python tools/diagnostics/check_phase1_status.py
    sleep 60
done
```

### Checkpoint Management

```bash
# Before starting new experiments
bash tools/checkpoint_management/manage_checkpoints.sh backup

# Analyze checkpoint storage
du -sh rl_checkpoint_*.pth | sort -h

# Keep only latest 5 checkpoints per scenario
# (customize manage_checkpoints.sh for this)
bash tools/checkpoint_management/manage_checkpoints.sh cleanup
```

---

## Configuration and Customization

### Customizing `check_phase1_status.py`

Edit the script to adjust:
- **Baseline performance**: Change from 25% if needed
- **Target thresholds**: Adjust Phase 1 target (40%)
- **Status messages**: Customize recommendations
- **Metric calculations**: Add custom performance metrics

### Customizing `enhanced_rl_trainer.py`

Key parameters to adjust:
```python
# Training episodes
self.episodes_per_scenario = 2000

# Maximum steps per episode
self.max_steps_per_episode = 200

# DQN hyperparameters
alpha=0.0003   # Learning rate
gamma=0.99     # Discount factor
epsilon=1.0    # Initial exploration rate

# Curriculum parameters (in rl_mission_env.py)
tolerance_levels = [0.05, 0.03, 0.02]  # Success criteria progression
```

### Customizing `manage_checkpoints.sh`

Edit the script to:
- Change backup directory location
- Adjust retention policy (keep every N episodes)
- Add compression options
- Set up automatic cleanup schedules

---

## Integration with Project Structure

### With Launchers
```bash
# Use launchers to start training
python launchers/launch_enhanced_simulation.py

# Use tools to monitor and analyze
python tools/diagnostics/check_phase1_status.py
```

### With Tests
```bash
# Run tests first
cd test_scripts
pytest unit_tests/
pytest integration_tests/

# Then use diagnostic tools
cd ..
python tools/diagnostics/check_phase1_status.py
```

### With Main Simulation
```python
# Import training system in sim_husky_kuka.py
import sys
sys.path.append('tools/training')
from enhanced_rl_trainer import EnhancedRLTrainer

# Use diagnostic tools after training
os.system('python tools/diagnostics/check_phase1_status.py')
```

---

## Troubleshooting

### "No training results found"
**Cause:** Training hasn't been run or results file doesn't exist  
**Solution:**
```bash
# Run training first
python launchers/launch_enhanced_simulation.py
# Press 't' to start RL training
# Wait for results file to be generated
```

### "PyTorch not available"
**Cause:** PyTorch not installed  
**Solution:**
```bash
# Install PyTorch
conda install pytorch torchvision torchaudio -c pytorch

# Verify installation
python -c "import torch; print(torch.__version__)"
```

### "Import error: rl_mission_env"
**Cause:** Missing Python path or environment  
**Solution:**
```bash
# Add project root to Python path
export PYTHONPATH=/home/marcoreis/robust_mm_control_ws:$PYTHONPATH

# Or run from project root
cd /home/marcoreis/robust_mm_control_ws
python tools/diagnostics/check_phase1_status.py
```

### Checkpoint files taking too much space
**Solution:**
```bash
# Use checkpoint management tool
bash tools/checkpoint_management/manage_checkpoints.sh cleanup

# Or manually remove intermediate checkpoints
rm rl_checkpoint_*_ep[1-9]00_*.pth  # Keep only x000 episodes
```

---

## Performance Benchmarks

### Expected Diagnostic Run Times
- `check_phase1_status.py`: < 1 second
- `physics_diagnostics.py`: < 1 second
- `enhanced_rl_trainer.py`: 2-8 hours (full training)

### Training Performance
| Scenario | Episodes | Time (GPU) | Time (CPU) |
|----------|----------|------------|------------|
| Single scenario | 2000 | ~20 min | ~60 min |
| All scenarios | 20000 | ~3-4 hours | ~10-12 hours |
| Full Phase 1 | 20000 | ~3-4 hours | ~10-12 hours |

### Checkpoint Storage
| Type | Size per File | Total (all scenarios) |
|------|--------------|---------------------|
| DQN checkpoints | ~1-2 MB | ~200-400 MB |
| Q-tables | ~500 KB | ~50-100 MB |
| Full training set | - | ~500 MB - 1 GB |

---

## Adding New Tools

### Creating a New Diagnostic Tool

1. **Choose appropriate subdirectory** (`diagnostics/`, `training/`, etc.)
2. **Follow naming convention**: `<purpose>_<function>.py`
3. **Include comprehensive docstring**:
   ```python
   #!/usr/bin/env python3
   """
   Tool Name - Brief Description
   =============================
   Detailed explanation of purpose and functionality
   
   Features:
   - Feature 1
   - Feature 2
   
   Usage:
       python tools/<category>/<tool_name>.py [options]
   """
   ```
4. **Add to this README** in appropriate section
5. **Include in Quick Reference table**
6. **Document dependencies** and installation

### Tool Development Best Practices

- **Clear output**: Use emojis and formatting for readability
- **Error handling**: Graceful failures with helpful messages
- **Documentation**: Comprehensive docstrings and usage examples
- **Dependencies**: Minimal external dependencies when possible
- **Testing**: Add tests in `test_scripts/unit_tests/`
- **Logging**: Use consistent logging format
- **Exit codes**: Return meaningful exit codes (0=success, 1=error)

---

## Related Documentation

- **Main README**: `/home/marcoreis/robust_mm_control_ws/README.md`
- **Phase 1 Documentation**: `/home/marcoreis/robust_mm_control_ws/PHASE1_IMPLEMENTATION_COMPLETE.md`
- **Launcher Documentation**: `/home/marcoreis/robust_mm_control_ws/launchers/README.md`
- **Test Documentation**: `/home/marcoreis/robust_mm_control_ws/test_scripts/README.md`

---

## Support and Contribution

### Getting Help
1. Check this README for tool documentation
2. Review tool docstrings (`--help` or read source)
3. Check related documentation in `documentation/`
4. Review test examples in `test_scripts/`

### Contributing New Tools
1. Create tool in appropriate subdirectory
2. Follow project conventions and style
3. Add comprehensive documentation
4. Include tests if applicable
5. Update this README
6. Add usage examples

### Reporting Issues
- Document the issue clearly
- Include command that failed
- Provide error messages and logs
- Note environment details (OS, Python version, etc.)

---

**Last Updated:** November 1, 2025  
**Workspace:** `/home/marcoreis/robust_mm_control_ws`  
**Project:** Robust Mobile Manipulator Control System
