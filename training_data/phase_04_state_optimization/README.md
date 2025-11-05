# Phase 04: State Optimization

**Timeline**: 4-6 weeks  
**Priority**: ⭐⭐⭐ HIGH (Foundation for all future work)  
**Status**: Planning → Implementation  
**Goal**: Enhanced state representation and trajectory integration for improved learning

---

## 📋 Overview

Phase 04 focuses on improving the state representation to enable better learning. The baseline Phase 03 DQN uses a 35-dimensional instantaneous state with no temporal information or trajectory context.

**Current Performance (Phase 03)**:
- Mean Error: 0.753m
- Success Rate: 100%
- State: 35D instantaneous

**Target Performance (Phase 04)**:
- Mean Error: < 0.65m (↓13-27% improvement)
- Success Rate: 100%
- State: Enhanced with temporal/trajectory features

---

## 🗂️ Experiment Structure

### **Phase 04.1: Temporal History**
```
temporal_history/
├── 01_baseline_35d/              # Reference (Phase 03)
├── 02_history_3step/             # 105D: [t, t-1, t-2]
├── 03_history_5step/             # 175D: [t, t-1, t-2, t-3, t-4]
├── 04_velocity_features/         # 70D: [t, velocity]
└── 05_velocity_acceleration/     # 105D: [t, v, a]
```

**Expected Impact**: ↓ 10-15% error

---

### **Phase 04.2: Trajectory Integration** ⭐ HIGHEST PRIORITY

```
trajectory_aware/
├── 01_baseline_current_only/     # Current waypoint only (35D)
├── 02_next_1_waypoint/           # +1 lookahead (41D)
├── 03_next_3_waypoints/          # +3 lookahead (53D) ⭐ START HERE
├── 04_next_5_waypoints/          # +5 lookahead (65D)
├── 05_with_progress_metrics/     # +progress features (59D)
└── 06_with_curvature/            # +geometric features (62D)
```

**Expected Impact**: ↓ 15-25% error  
**Novel Contribution**: Planning-aware state representation

---

### **Phase 04.3: Enhanced Features**

```
enhanced_features/
├── 01_baseline/
├── 02_disturbance_detection/      # +4D disturbance features
├── 03_control_quality/            # +4D control metrics
├── 04_combined/                   # +8D all features
└── 05_feature_selection/          # Best subset only
```

---

### **Phase 04.4: Recurrent Architectures**

```
recurrent/
├── 01_lstm_1layer/
├── 02_lstm_2layers/               # ⭐ Recommended
├── 03_gru_2layers/
├── 04_transformer_4heads/
└── 05_comparison_vs_feedforward/
```

**Expected Impact**: ↓ 20-30% error  
**Trade-off**: +50% training time

---

### **Phase 04.5: Hierarchical Representations**

```
hierarchical/
├── 01_flat_baseline/
├── 02_two_level/                  # Low + High
├── 03_three_level/                # Low + Mid + High
└── 04_learned_hierarchy/          # Auto-encoder
```

---

### **Phase 04.6: Architecture Variants**

```
architectures/
├── 01_baseline_128_128/
├── 02_wider_256_256_128/
├── 03_deeper_4layers/
├── 04_residual_connections/
└── 05_dueling_dqn/
```

---

### **Phase 04.7: Combined Optimal**

```
combined_optimal/
└── history3_traj3_hierarchical/   # Best from each category
```

---

## 🚀 Quick Start

### **Start with Phase 04.2 (Trajectory Integration)**

This has the highest expected impact and is easiest to implement:

```bash
# 1. Navigate to trajectory_aware directory
cd training_data/phase_04_state_optimization/trajectory_aware/03_next_3_waypoints

# 2. Run the training script
python ../../../../enhanced_rl_trainer.py \
    --state-type trajectory_aware \
    --lookahead-waypoints 3 \
    --episodes 10000 \
    --save-dir session_data

# 3. Monitor with W&B
# Dashboard will show real-time comparison with Phase 03 baseline
```

---

## 📊 Success Criteria

- [ ] Mean error < 0.65m (↓13%+ from Phase 03)
- [ ] At least 5 state variants tested
- [ ] Recurrent architecture evaluated (LSTM)
- [ ] Statistical significance established (p < 0.05)
- [ ] Best configuration documented
- [ ] Ablation study completed

---

## 📈 Expected Timeline

| Week | Task | Deliverable |
|------|------|-------------|
| 1 | Phase 04.2 implementation + baseline | Trajectory-aware state working |
| 2 | Phase 04.2 variants (1, 3, 5 waypoints) | Performance comparison |
| 3 | Phase 04.1 temporal history | History variants tested |
| 4 | Phase 04.4 recurrent (LSTM) | LSTM vs feedforward |
| 5 | Phase 04.6 architecture search | Best architecture found |
| 6 | Combined optimal + documentation | Phase 04 complete |

---

## 📝 Documentation

Each experiment should document:
- State representation details (dimension, features)
- Network architecture (layers, parameters)
- Training hyperparameters
- Results (mean error, std, success rate)
- Comparison with baseline

Use the provided Jupyter notebooks in `phase_06_monitoring_evaluation/` for analysis.

---

## 🔗 Related Files

- Implementation: `src/simulation/rl_mission_env.py`
- Training: `enhanced_rl_trainer.py`
- Analysis: `phase_06_monitoring_evaluation/comparative_analysis/`
- Planning: `phase_00_future_experiments/planning.md`

---

**Last Updated**: November 5, 2025  
**Status**: Directory structure created, ready for implementation  
**Next Action**: Implement Phase 04.2 trajectory integration
