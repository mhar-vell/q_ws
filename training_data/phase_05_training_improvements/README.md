# Phase 05: Training Improvements

**Timeline**: 6-8 weeks  
**Priority**: ⭐⭐⭐ HIGH (Maximize Phase 04 performance)  
**Status**: Planning (starts after Phase 04)  
**Goal**: Optimize training methodology through curriculum learning and hyperparameter tuning

---

## 📋 Overview

Phase 05 focuses on improving *how* we train the agent (using the best state representation from Phase 04).

**Starting Point (Phase 04 best)**:
- Mean Error: ~0.55-0.65m
- State: Best from Phase 04
- Training: Fixed golden intensity, 10K episodes

**Target Performance (Phase 05)**:
- Mean Error: < 0.55m (↓27-34% from Phase 03)
- Training: Optimized curriculum + hyperparameters
- Convergence: Faster and more stable

---

## 🗂️ Experiment Structure

### **Phase 05.1: Intensity Curriculum** ⭐ HIGHEST PRIORITY

```
intensity_curriculum/
├── 01_baseline_fixed_golden/     # Phase 03-04 approach
├── 02_linear_progression/        # normal → golden linearly
├── 03_exponential_rampup/        # Slow start, fast end
├── 04_stepwise_plateaus/         # Discrete levels
├── 05_adaptive_performance/      # ⭐ Novel: Self-paced learning
└── 06_comparison_analysis/
```

**Expected Impact**: 20-30% faster convergence + better final performance

---

### **Phase 05.2: Scenario Curriculum**

```
scenario_curriculum/
├── 01_baseline_mixed/            # Phase 03: All scenarios mixed
├── 02_easy_to_hard/              # none → continuous → periodic → random → impulse
├── 03_grouped_by_type/           # Predictable first, then stochastic
├── 04_reverse_curriculum/        # Hard first (counter-intuitive test)
└── 05_comparison/
```

---

### **Phase 05.3: Hyperparameter Optimization**

```
hyperparameter_tuning/
├── 01_baseline_hyperparams/      # Current config
├── 02_grid_search/               # Exhaustive (use Ray Tune)
├── 03_bayesian_optimization/     # Smart search (Optuna)
├── 04_pbt/                       # Population-based training
└── 05_best_config/               # Final recommendation
```

**Search Space**:
- Learning rate: [1e-4, 5e-4, 1e-3, 5e-3]
- Gamma: [0.95, 0.97, 0.99]
- Batch size: [32, 64, 128, 256]
- Buffer size: [10K, 50K, 100K]
- Network: [[128,128], [256,256], [512,256]]

---

### **Phase 05.4: Extended Training**

```
extended_training/
├── 01_standard_10k/              # Phase 03-04 baseline
├── 02_extended_25k/              # Check for late improvements
├── 03_very_long_50k/             # Find asymptote
├── 04_multi_seed_5x10k/          # Reliability validation
└── 05_learning_curves/
```

**Question**: Does more training help, or do we plateau?

---

### **Phase 05.5: Advanced Techniques**

```
advanced_techniques/
├── 01_baseline_uniform_replay/
├── 02_prioritized_replay/        # PER - sample important transitions
├── 03_hindsight_replay/          # HER - learn from failures
├── 04_n_step_returns/            # Better credit assignment
└── 05_combined/
```

---

## 🚀 Quick Start

### **Start with Phase 05.1 (Adaptive Curriculum)**

This is our **novel contribution**:

```bash
# 1. Navigate to adaptive curriculum directory
cd training_data/phase_05_training_improvements/intensity_curriculum/05_adaptive_performance

# 2. Run training with adaptive curriculum
python ../../../../enhanced_rl_trainer.py \
    --state-type trajectory_aware \
    --curriculum adaptive \
    --episodes 15000 \
    --save-dir session_data

# Curriculum adapts based on performance:
# - High success (>85%) → increase intensity
# - Low success (<60%) → decrease intensity
# - Agent controls its own difficulty!
```

---

## 📊 Success Criteria

- [ ] Mean error < 0.55m (↓27%+ from Phase 03)
- [ ] Curriculum strategies compared (≥3)
- [ ] Hyperparameter optimization completed
- [ ] Extended training tested (25K+ episodes)
- [ ] Optimal training protocol documented
- [ ] Multi-seed validation performed

---

## 📈 Expected Timeline

| Week | Task | Deliverable |
|------|------|-------------|
| 1-2 | Phase 05.1 curriculum variants | Best curriculum identified |
| 3-4 | Phase 05.2 scenario ordering | Scenario strategy selected |
| 5 | Phase 05.3 hyperparameter search | Optimal config found |
| 6-7 | Phase 05.4 extended training | Long-term performance |
| 8 | Documentation + comparison | Phase 05 complete |

---

## 💡 Key Innovations

### **Adaptive Curriculum Learning** (Novel)

Traditional curriculum: Fixed schedule (episode 0 → N)
```python
intensity = 0.05 + (episode / 10000) * (0.128 - 0.05)
```

**Our adaptive curriculum**: Performance-based
```python
if recent_success_rate > 0.85:
    intensity *= 1.1  # Agent mastered → increase
elif recent_success_rate < 0.60:
    intensity *= 0.9  # Agent struggling → decrease
```

**Benefits**:
- Self-paced learning
- No manual tuning of schedule
- Adapts to agent's learning speed
- **Novel for robotic RL**

---

## 📝 Documentation

Each experiment should document:
- Curriculum strategy (if applicable)
- Hyperparameters tested
- Training duration (episodes, wall-clock time)
- Learning curves (error over episodes)
- Final performance metrics
- Convergence analysis

---

## 🔗 Related Files

- Implementation: `enhanced_rl_trainer.py`
- Curriculum logic: `src/simulation/rl_mission_env.py`
- Analysis: `phase_06_monitoring_evaluation/comparative_analysis/`
- Planning: `phase_00_future_experiments/planning.md`

---

**Last Updated**: November 5, 2025  
**Status**: Directory structure created, awaiting Phase 04 completion  
**Next Action**: After Phase 04, implement adaptive curriculum
