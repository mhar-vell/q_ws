# Archive Organization Plan v2 - Split by Training Sessions

## 🎯 **Key Improvement: Training-Session-Based Organization**

Instead of mixing all training results, we organize by **specific training runs** with timestamps and configurations.

---

## 📁 Enhanced Directory Structure

```
q_ws/
│
├── 📂 archives/
│   │
│   ├── 📂 01_documentation/
│   │   ├── 📂 disturbance_system/
│   │   │   ├── DISTURBANCE_COMPENSATION.md
│   │   │   ├── DISTURBANCE_EXPLANATION_CORRECTED.md
│   │   │   ├── DISTURBANCE_FINDINGS.md
│   │   │   ├── DISTURBANCE_QUICK_REF.md
│   │   │   └── DISTURBANCE_REVIEW.md
│   │   │
│   │   ├── 📂 training_guides/
│   │   │   ├── DUAL_INTENSITY_TRAINING_SUMMARY.md
│   │   │   ├── TRAINING_CHECKLIST.md
│   │   │   ├── TRAINING_EPISODES_CONFIG.md
│   │   │   ├── TRAINING_WORKFLOW.md
│   │   │   ├── TIMEOUT_EXPLANATION.md
│   │   │   └── AUTOMATIC_TRAINING_COMPLETE.md
│   │   │
│   │   ├── 📂 optimization/
│   │   │   ├── PERFORMANCE_OPTIMIZATION.md
│   │   │   ├── PYTORCH_COMPATIBILITY_REPORT.md
│   │   │   └── PYTORCH_PYBULLET_READY.md
│   │   │
│   │   ├── 📂 trajectory_planning/
│   │   │   ├── TRAJECTORY_CUSTOMIZATION.md
│   │   │   ├── TRAJECTORY_PLANNING.md
│   │   │   └── RL_ALGORITHMS.md
│   │   │
│   │   ├── 📂 project_overview/
│   │   │   ├── PROJECT_TITLE_SUGGESTIONS.md
│   │   │   └── DOCUMENTATION_INDEX.md
│   │   │
│   │   └── 📂 academic/
│   │       ├── ACADEMIC_PAPER_DRAFT.md
│   │       └── Marco Reis - Robust Mobile Manipulator Control.pdf
│   │
│   ├── 📂 02_training_sessions/
│   │   │
│   │   ├── 📂 training_20251015_initial_dqn_500ep/
│   │   │   ├── 📂 config/
│   │   │   │   ├── training_config.json
│   │   │   │   ├── hyperparameters.txt
│   │   │   │   └── README.md
│   │   │   │
│   │   │   ├── 📂 checkpoints/
│   │   │   │   ├── 📂 none_scenario/
│   │   │   │   │   ├── rl_checkpoint_none_ep100_dqn.pth
│   │   │   │   │   ├── rl_checkpoint_none_ep200_dqn.pth
│   │   │   │   │   ├── rl_checkpoint_none_ep300_dqn.pth
│   │   │   │   │   ├── rl_checkpoint_none_ep400_dqn.pth
│   │   │   │   │   └── rl_checkpoint_none_ep500_dqn.pth
│   │   │   │   │
│   │   │   │   ├── 📂 random_scenario/
│   │   │   │   │   ├── rl_checkpoint_random_ep100_dqn.pth
│   │   │   │   │   ├── rl_checkpoint_random_ep200_dqn.pth
│   │   │   │   │   ├── rl_checkpoint_random_ep300_dqn.pth
│   │   │   │   │   ├── rl_checkpoint_random_ep400_dqn.pth
│   │   │   │   │   └── rl_checkpoint_random_ep500_dqn.pth
│   │   │   │   │
│   │   │   │   ├── 📂 periodic_scenario/
│   │   │   │   │   └── [5 checkpoints]
│   │   │   │   │
│   │   │   │   ├── 📂 continuous_scenario/
│   │   │   │   │   └── [5 checkpoints]
│   │   │   │   │
│   │   │   │   └── 📂 impulse_scenario/
│   │   │   │       └── [5 checkpoints]
│   │   │   │
│   │   │   ├── 📂 final_models/
│   │   │   │   ├── rl_final_none_normal_dqn.pth
│   │   │   │   ├── rl_final_random_normal_dqn.pth
│   │   │   │   ├── rl_final_periodic_normal_dqn.pth
│   │   │   │   ├── rl_final_continuous_normal_dqn.pth
│   │   │   │   ├── rl_final_impulse_normal_dqn.pth
│   │   │   │   ├── rl_final_none_golden_dqn.pth
│   │   │   │   ├── rl_final_random_golden_dqn.pth
│   │   │   │   ├── rl_final_periodic_golden_dqn.pth
│   │   │   │   ├── rl_final_continuous_golden_dqn.pth
│   │   │   │   └── rl_final_impulse_golden_dqn.pth
│   │   │   │
│   │   │   ├── 📂 metrics/
│   │   │   │   ├── rl_metrics_dqn.json
│   │   │   │   ├── training_log.txt
│   │   │   │   └── performance_summary.json
│   │   │   │
│   │   │   ├── 📂 analysis/
│   │   │   │   ├── rl_training_analysis_20251016_093606.png
│   │   │   │   ├── real_rl_training_analysis_20251016_093735.png
│   │   │   │   ├── rl_performance_summary_20251016_093910.png
│   │   │   │   ├── accuracy_drop_analysis.png
│   │   │   │   └── rl_analysis_data_20251016_093241.json
│   │   │   │
│   │   │   ├── 📂 videos/
│   │   │   │   ├── training_none_normal.mp4
│   │   │   │   ├── training_random_golden.mp4
│   │   │   │   └── [other training videos]
│   │   │   │
│   │   │   └── README.md
│   │   │       # Training session summary:
│   │   │       # - Date: 2025-10-15
│   │   │       # - Algorithm: DQN only
│   │   │       # - Episodes: 500 per scenario
│   │   │       # - Dual-intensity: Yes (normal + golden)
│   │   │       # - Results: 79.9% avg success rate
│   │   │
│   │   ├── 📂 training_20251014_qlearning_test_50ep/
│   │   │   ├── 📂 config/
│   │   │   │   └── training_config.json
│   │   │   │
│   │   │   ├── 📂 checkpoints/
│   │   │   │   └── 📂 none_scenario/
│   │   │   │       └── rl_checkpoint_none_ep100_qtable.pkl
│   │   │   │
│   │   │   ├── 📂 final_models/
│   │   │   │   └── rl_final_none_qtable.pkl
│   │   │   │
│   │   │   ├── 📂 metrics/
│   │   │   │   └── rl_metrics.json
│   │   │   │
│   │   │   ├── 📂 analysis/
│   │   │   │   └── rl_test_results.png
│   │   │   │
│   │   │   └── README.md
│   │   │       # Training session summary:
│   │   │       # - Date: 2025-10-14
│   │   │       # - Algorithm: Q-Learning (tabular)
│   │   │       # - Episodes: 50 (test run)
│   │   │       # - Single scenario: none
│   │   │       # - Results: 41.3% success rate
│   │   │
│   │   ├── 📂 training_20251013_legacy_single_intensity/
│   │   │   ├── 📂 final_models/
│   │   │   │   ├── rl_final_none_dqn.pth
│   │   │   │   ├── rl_final_random_dqn.pth
│   │   │   │   ├── rl_final_periodic_dqn.pth
│   │   │   │   └── rl_final_impulse_dqn.pth
│   │   │   │
│   │   │   ├── 📂 metrics/
│   │   │   │   └── rl_metrics.json
│   │   │   │
│   │   │   └── README.md
│   │   │       # Legacy training (before dual-intensity)
│   │   │       # - Single intensity only
│   │   │       # - Reference baseline
│   │   │
│   │   └── 📂 _template_training_session/
│   │       ├── 📂 config/
│   │       ├── 📂 checkpoints/
│   │       ├── 📂 final_models/
│   │       ├── 📂 metrics/
│   │       ├── 📂 analysis/
│   │       ├── 📂 videos/
│   │       └── README.md
│   │
│   ├── 📂 03_comparative_analysis/
│   │   │
│   │   ├── 📂 cross_training_comparison/
│   │   │   ├── algorithm_comparison.png
│   │   │   ├── intensity_comparison.png
│   │   │   ├── scenario_performance.png
│   │   │   └── comparative_metrics.json
│   │   │
│   │   ├── 📂 publication_figures/
│   │   │   ├── Figure_1.png  # Main results
│   │   │   ├── Figure_2.png  # Robustness analysis
│   │   │   └── figure_sources.txt
│   │   │
│   │   ├── 📂 statistical_analysis/
│   │   │   ├── significance_tests.csv
│   │   │   ├── statistical_report.md
│   │   │   └── data_tables.xlsx
│   │   │
│   │   └── README.md
│   │       # Cross-training analysis combining all sessions
│   │       # - Multi-session comparisons
│   │       # - Statistical significance
│   │       # - Publication-ready figures
│   │
│   ├── 📂 04_test_scripts/
│   │   ├── 📂 unit_tests/
│   │   │   ├── test_dqn_device.py
│   │   │   ├── test_mounting.py
│   │   │   └── test_waypoints.py
│   │   │
│   │   ├── 📂 integration_tests/
│   │   │   ├── test_enhanced_rl.py
│   │   │   ├── test_rl_system.py
│   │   │   └── test_analysis.py
│   │   │
│   │   └── 📂 analysis_scripts/
│   │       ├── rl_training_analysis.py
│   │       ├── run_analysis.py
│   │       └── simple_analysis_runner.py
│   │
│   ├── 📂 05_visualization_tools/
│   │   ├── plot_rl_results.py
│   │   ├── plot_disturbances.py
│   │   ├── visualize_disturbances.py
│   │   ├── visualize_trajectories.py
│   │   └── physics_diagnostics.py
│   │
│   └── 📂 06_experiment_logs/
│       ├── experiment_index.json
│       ├── training_timeline.md
│       └── lessons_learned.md
│
├── 📂 core/ (Active development)
│   ├── sim_husky_kuka.py
│   ├── rl_mission_env.py
│   ├── rl_trajectory_planner.py
│   ├── trajectory_generators.py
│   ├── rl_config.py
│   └── environment.yml
│
└── 📂 photos/ (Keep as-is)

```

---

## 🎯 **Key Improvements in v2**

### **1. Training Session Organization**
Each training run gets its own dated folder with:
- ✅ **Complete isolation** - No mixing of different training runs
- ✅ **Self-contained** - Everything for that session in one place
- ✅ **Traceable** - Easy to see what was done when
- ✅ **Comparable** - Side-by-side session comparison

### **2. Session Folder Structure**
Every training session includes:
```
training_YYYYMMDD_description_config/
├── config/           # Hyperparameters, settings
├── checkpoints/      # Organized by scenario
├── final_models/     # All final trained models
├── metrics/          # JSON metrics, logs
├── analysis/         # Generated plots and data
├── videos/           # Training recordings
└── README.md         # Session summary
```

### **3. Comparative Analysis Section**
New dedicated section for cross-training comparisons:
- Compare multiple training sessions
- Statistical analysis across runs
- Publication-ready figures
- Combined metrics

---

## 📋 **Training Session Examples**

### **Session 1: Main DQN Training (Current)**
```
training_20251015_initial_dqn_500ep/
├── config/
│   ├── training_config.json
│   │   {
│   │     "algorithm": "DQN",
│   │     "episodes_per_scenario": 500,
│   │     "scenarios": ["none", "random", "periodic", "continuous", "impulse"],
│   │     "intensities": ["normal", "golden"],
│   │     "learning_rate": 0.001,
│   │     "epsilon_decay": 0.995,
│   │     "batch_size": 32,
│   │     "replay_buffer": 10000
│   │   }
│   └── README.md
│       Algorithm: DQN
│       Date: 2025-10-15
│       Episodes: 500 per scenario
│       Total Training Time: ~42 minutes
│       Success Rate: 79.9% average
│       GPU: Apple MPS (M2 Pro)
│
├── checkpoints/
│   ├── none_scenario/      [5 checkpoints]
│   ├── random_scenario/    [5 checkpoints]
│   ├── periodic_scenario/  [5 checkpoints]
│   ├── continuous_scenario/[5 checkpoints]
│   └── impulse_scenario/   [5 checkpoints]
│
├── final_models/
│   ├── rl_final_none_normal_dqn.pth
│   ├── rl_final_none_golden_dqn.pth
│   └── [8 more models...]
│
├── metrics/
│   ├── rl_metrics_dqn.json
│   └── training_log.txt
│
├── analysis/
│   ├── rl_training_analysis_20251016_093606.png
│   ├── real_rl_training_analysis_20251016_093735.png
│   ├── rl_performance_summary_20251016_093910.png
│   ├── accuracy_drop_analysis.png
│   └── rl_analysis_data_20251016_093241.json
│
└── videos/
    └── [training recordings]
```

### **Session 2: Q-Learning Test**
```
training_20251014_qlearning_test_50ep/
├── config/
│   └── training_config.json
│       {
│         "algorithm": "Q-Learning",
│         "episodes": 50,
│         "scenario": "none",
│         "purpose": "baseline comparison"
│       }
│
├── checkpoints/
│   └── none_scenario/
│       └── rl_checkpoint_none_ep100_qtable.pkl
│
├── final_models/
│   └── rl_final_none_qtable.pkl
│
├── metrics/
│   └── rl_metrics.json
│
├── analysis/
│   └── rl_test_results.png
│
└── README.md
```

### **Session 3: Legacy Single-Intensity**
```
training_20251013_legacy_single_intensity/
├── final_models/
│   ├── rl_final_none_dqn.pth
│   ├── rl_final_random_dqn.pth
│   ├── rl_final_periodic_dqn.pth
│   └── rl_final_impulse_dqn.pth
│
├── metrics/
│   └── rl_metrics.json
│
└── README.md
    # Legacy training before dual-intensity implementation
    # Used as baseline comparison
```

---

## 📊 **Comparative Analysis Structure**

### **cross_training_comparison/**
Compare results across all training sessions:
```
cross_training_comparison/
├── algorithm_comparison.png
│   # DQN vs Q-Learning across sessions
│
├── intensity_comparison.png
│   # Normal vs Golden performance trends
│
├── scenario_performance.png
│   # How each scenario performs across trainings
│
├── convergence_comparison.png
│   # Learning curves from different sessions
│
└── comparative_metrics.json
    {
      "sessions": [
        {
          "id": "training_20251015_initial_dqn_500ep",
          "success_rate": 79.9,
          "training_time": "42 min",
          "best_scenario": "none_normal"
        },
        {
          "id": "training_20251014_qlearning_test_50ep",
          "success_rate": 41.3,
          "training_time": "8 min",
          "notes": "Limited episodes"
        }
      ]
    }
```

### **publication_figures/**
Final polished figures for papers:
```
publication_figures/
├── Figure_1.png
│   # Main results: Success rates across scenarios
│
├── Figure_2.png
│   # Robustness analysis: Normal vs Golden
│
├── Figure_3_convergence.png
│   # Learning curves (may need to generate)
│
├── Figure_4_ablation.png
│   # IMU contribution analysis
│
└── figure_sources.txt
    Figure 1: From training_20251015_initial_dqn_500ep/analysis/
    Figure 2: From 03_comparative_analysis/cross_training_comparison/
    ...
```

---

## 🔍 **Search & Access Examples**

### **"Show me the latest DQN training results"**
```bash
→ archives/02_training_sessions/training_20251015_initial_dqn_500ep/analysis/
```

### **"Compare DQN vs Q-Learning performance"**
```bash
→ archives/03_comparative_analysis/cross_training_comparison/algorithm_comparison.png
```

### **"What were the checkpoints for periodic disturbances?"**
```bash
→ archives/02_training_sessions/training_20251015_initial_dqn_500ep/checkpoints/periodic_scenario/
```

### **"Get all training configurations"**
```bash
→ archives/02_training_sessions/*/config/training_config.json
```

### **"Find publication-ready figures"**
```bash
→ archives/03_comparative_analysis/publication_figures/
```

---

## 📝 **Training Session README Template**

Each training session should include:

```markdown
# Training Session: [Name]

## Overview
- **Date**: YYYY-MM-DD
- **Algorithm**: DQN / Q-Learning / Both
- **Episodes**: N per scenario
- **Duration**: X minutes
- **Hardware**: Apple M2 Pro / MPS GPU

## Configuration
- Learning rate: 0.001
- Epsilon decay: 0.995
- Batch size: 32
- Replay buffer: 10,000
- Target update: Every 100 steps

## Scenarios Trained
- ✅ none (normal + golden)
- ✅ random (normal + golden)
- ✅ periodic (normal + golden)
- ✅ continuous (normal + golden)
- ✅ impulse (normal + golden)

## Results Summary
- **Average Success Rate**: 79.9%
- **Best Combination**: none_normal (92.4%)
- **Most Challenging**: impulse_golden (67.9%)
- **Robustness Index**: 0.854

## Key Findings
1. DQN significantly outperforms Q-Learning
2. Golden intensity reduces success by ~15%
3. IMU integration provides 28pp improvement
4. Periodic disturbances most predictable

## Files
- Checkpoints: `checkpoints/` (25 files)
- Final models: `final_models/` (10 files)
- Metrics: `metrics/rl_metrics_dqn.json`
- Analysis: `analysis/` (5 figures)

## Next Steps
- [ ] Extended training (1000 episodes)
- [ ] Real hardware validation
- [ ] Additional disturbance types
```

---

## 🚀 **Benefits of This Structure**

### **1. Clear Training History**
✅ Each session is timestamped and isolated  
✅ Easy to track what changed between sessions  
✅ Simple to revert or reference old trainings  
✅ Complete reproducibility information

### **2. Better Comparisons**
✅ Dedicated comparative analysis section  
✅ Cross-session metrics easily accessible  
✅ Side-by-side configuration comparison  
✅ Statistical significance testing

### **3. Academic Use**
✅ Publication figures in dedicated folder  
✅ Complete experimental methodology preserved  
✅ Easy to cite specific training runs  
✅ Reproducibility guaranteed

### **4. Scalability**
✅ Template for future training sessions  
✅ Unlimited sessions without confusion  
✅ Consistent structure across experiments  
✅ Easy automation of organization

### **5. Maintainability**
✅ Self-documenting with README files  
✅ Clear naming conventions  
✅ No file conflicts between sessions  
✅ Clean workspace

---

## 💡 **Implementation Strategy**

### **Phase 1: Identify Training Sessions**
Based on your files, I can see at least **3 distinct training sessions**:

1. **Main DQN Training** (Oct 15-16)
   - 500 episodes per scenario
   - Dual-intensity (normal + golden)
   - All 5 scenarios
   - Complete analysis

2. **Q-Learning Test** (Earlier)
   - Limited episodes
   - Single scenario (none)
   - Baseline comparison

3. **Legacy Single-Intensity** (Before dual-intensity)
   - Old model format
   - Reference baseline

### **Phase 2: Create Structure**
```bash
# Create training session folders
mkdir -p archives/02_training_sessions/training_20251015_initial_dqn_500ep/{config,checkpoints,final_models,metrics,analysis,videos}

# Create comparative analysis
mkdir -p archives/03_comparative_analysis/{cross_training_comparison,publication_figures,statistical_analysis}
```

### **Phase 3: Move Files by Session**
Organize checkpoints, models, metrics, and analysis by their training session.

### **Phase 4: Create README Files**
Document each session with configuration and results.

### **Phase 5: Generate Comparative Analysis**
Run cross-session comparisons and create publication figures.

---

## 🎯 **Quick Decision Matrix**

| File Type | Organize By | Location |
|-----------|-------------|----------|
| Checkpoint (ep100-500) | Training session + scenario | `02_training_sessions/SESSION/checkpoints/SCENARIO/` |
| Final model | Training session + intensity | `02_training_sessions/SESSION/final_models/` |
| Training metrics | Training session | `02_training_sessions/SESSION/metrics/` |
| Analysis plots | Training session | `02_training_sessions/SESSION/analysis/` |
| Training videos | Training session | `02_training_sessions/SESSION/videos/` |
| Cross-session comparison | Comparative analysis | `03_comparative_analysis/cross_training_comparison/` |
| Publication figures | Comparative analysis | `03_comparative_analysis/publication_figures/` |
| Documentation | Documentation type | `01_documentation/CATEGORY/` |

---

## ✅ **Next Steps - What Would You Like?**

1. **Auto-organize files into this structure?**
2. **Generate README files for each training session?**
3. **Create comparative analysis plots?**
4. **Build experiment index/timeline?**
5. **Generate shell script to review first?**

This structure will make your thesis/paper work much easier - every experiment is traceable, comparable, and well-documented!
