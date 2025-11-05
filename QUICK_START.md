# Quick Start: Next Steps

**Date:** November 5, 2025  
**Status:** Infrastructure ready, proceed with integration

---

## 🎯 What's Done

✅ **Phase 06:** Monitoring infrastructure (W&B logging, metrics, analysis notebooks)  
✅ **Phase 04.2:** Trajectory state wrapper (35D → 59D enhancement)  
✅ **Documentation:** Complete guides for both phases  

---

## 🚀 What to Do Next

### Option 1: Quick Integration Test (30 min)

**Goal:** Verify everything works together

```bash
# 1. Install W&B
pip install wandb
wandb login

# 2. Test trajectory wrapper
cd training_data/phase_04_state_optimization/04_2_trajectory_integration
python trajectory_state_wrapper.py

# 3. Test W&B logger
cd ../../phase_06_monitoring_evaluation/logging_infrastructure
python wandb_integration.py
python metrics_collector.py
```

**Success:** All tests pass without errors

---

### Option 2: Full Integration (1-2 hours)

**Goal:** Integrate wrapper + logging into training code

**Follow:** `training_data/phase_06_monitoring_evaluation/SETUP.md`

**Key Changes to `/home/marcoreis/robust_mm_control_ws/tools/training/enhanced_rl_trainer.py`:**

1. Add imports:
```python
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from training_data.phase_04_state_optimization.04_2_trajectory_integration.trajectory_state_wrapper import TrajectoryStateWrapper
from training_data.phase_06_monitoring_evaluation.logging_infrastructure.wandb_integration import WandBLogger
from training_data.phase_06_monitoring_evaluation.logging_infrastructure.metrics_collector import MetricsCollector
```

2. Wrap environment:
```python
# In __init__
if args.use_trajectory_wrapper:
    waypoints = self._generate_trajectory_waypoints()
    self.env = TrajectoryStateWrapper(self.env, waypoints)
```

3. Initialize logger:
```python
if args.use_wandb:
    self.logger = WandBLogger("robust-mm-control", experiment_name)
    self.metrics = MetricsCollector()
```

4. Log in training loop:
```python
# After episode
metrics = self.metrics.end_episode()
self.logger.log_training_step(episode, **metrics)
```

---

### Option 3: Run Phase 04.2 Experiment (4-6 hours)

**Goal:** Get first Phase 04.2 results

```bash
# After integration is complete
python enhanced_rl_trainer.py \
    --experiment_name phase_04_2_trajectory \
    --episodes 2000 \
    --use_trajectory_wrapper \
    --use_wandb \
    --scenarios continuous,impulse \
    --intensities low,medium,high
```

**Monitor:** Visit W&B dashboard (link shown at start)

**Result:** Phase 04.2 training data + checkpoints

---

### Option 4: Analyze Results (30 min)

**Goal:** Statistical comparison with Phase 03

```bash
# After training completes
jupyter notebook training_data/phase_06_monitoring_evaluation/comparative_analysis/statistical_tests.ipynb
```

**Actions in notebook:**
1. Load Phase 03 baseline results
2. Load Phase 04.2 results
3. Run statistical tests
4. Generate comparison tables

---

## 📊 Expected Outcomes

### Phase 04.2 vs Phase 03
- **Hypothesis:** Trajectory features → better anticipatory control
- **Target:** ↓13-27% error reduction
- **Phase 03:** 0.753m mean error
- **Phase 04.2 Goal:** <0.65m mean error
- **Statistical test:** p < 0.05 for significance

---

## 📁 Key Files

### Implementation
- `training_data/phase_04_state_optimization/04_2_trajectory_integration/trajectory_state_wrapper.py`
- `training_data/phase_06_monitoring_evaluation/logging_infrastructure/wandb_integration.py`
- `tools/training/enhanced_rl_trainer.py` (needs modification)

### Documentation
- `training_data/phase_06_monitoring_evaluation/SETUP.md` - Integration guide
- `training_data/phase_04_state_optimization/04_2_trajectory_integration/README.md` - Phase 04.2 details
- `IMPLEMENTATION_PROGRESS.md` - Full status report

### Analysis
- `training_data/phase_06_monitoring_evaluation/comparative_analysis/statistical_tests.ipynb`
- `training_data/phase_06_monitoring_evaluation/failure_analysis/failure_classifier.ipynb`

---

## ⚡ Fastest Path to Results

```bash
# 1. Quick tests (5 min)
cd training_data/phase_06_monitoring_evaluation/logging_infrastructure
python wandb_integration.py

# 2. Integrate code (1-2 hours)
# - Follow SETUP.md instructions
# - Modify enhanced_rl_trainer.py

# 3. Test integration (15 min)
python enhanced_rl_trainer.py --episodes 10 --use_trajectory_wrapper --use_wandb

# 4. Full training (4-6 hours)
python enhanced_rl_trainer.py --experiment_name phase_04_2_full --episodes 2000 \
    --use_trajectory_wrapper --use_wandb

# 5. Analyze (30 min)
jupyter notebook training_data/phase_06_monitoring_evaluation/comparative_analysis/statistical_tests.ipynb
```

**Total time to Phase 04.2 results:** ~1-2 days

---

## 🆘 Troubleshooting

### Import errors
```bash
# Ensure Python path includes workspace
export PYTHONPATH=/home/marcoreis/robust_mm_control_ws:$PYTHONPATH
```

### W&B login fails
```bash
# Get API key from https://wandb.ai/settings
wandb login YOUR_API_KEY
```

### State dimension mismatch
```python
# Verify wrapper is active
print(f"State dim: {env.state_dim}")  # Should be 59 with wrapper
```

### No improvement seen
- Try more training episodes (3000 instead of 2000)
- Check waypoint generation is working
- Verify network accepts 59D input

---

## 📞 Help Resources

- **Phase 06 Setup:** `training_data/phase_06_monitoring_evaluation/SETUP.md`
- **Phase 04.2 Guide:** `training_data/phase_04_state_optimization/04_2_trajectory_integration/README.md`
- **Full Status:** `IMPLEMENTATION_PROGRESS.md`
- **W&B Docs:** https://docs.wandb.ai/

---

**Recommendation:** Start with Option 1 (Quick Test) to verify everything works, then proceed to Option 2 (Integration).

Good luck! 🚀
