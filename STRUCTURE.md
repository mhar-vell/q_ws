# Repository Structure Reference

## 📁 **Complete Project Organization**

```
q_ws/                                    # Mobile Manipulator RL Project
├── README.md                           # Main project documentation
├── environment.yml                     # Conda environment specification
├── .git/                              # Version control
│
├── src/                               # 🔧 Core Application Code
│   ├── simulation/
│   │   ├── sim_husky_kuka.py          # Main simulation (2,263 lines)
│   │   └── rl_mission_env.py          # RL environment with DQN/Q-Learning
│   ├── planning/
│   │   ├── rl_trajectory_planner.py   # Trajectory planning module
│   │   └── trajectory_generators.py   # Trajectory generation utilities
│   └── config/
│       └── rl_config.py               # Configuration management
│
├── tools/                             # 🛠️ Management & Automation
│   ├── training/
│   │   ├── create_training_session.py # Automated session creation
│   │   ├── query_training_sessions.py # Session querying & comparison
│   │   └── create_manifest.py         # Metadata generation
│   ├── setup/
│   │   └── organize_current_training.py # Training organization
│   └── data/
│       ├── experiment_index.json      # Project metadata index
│       └── current_training_manifest.json # Current session manifest
│
├── training_data/                     # 📊 All Training Experiments
│   ├── training_overview.md           # Master research overview
│   ├── README_TEMPLATE.md             # Session documentation template
│   ├── phase_01_baseline_testing/     # Algorithm comparison phase
│   │   ├── qlearning_baseline/        # Q-Learning baseline (41.3% success)
│   │   ├── dqn_baseline/              # DQN baseline (pending)
│   │   ├── algorithm_comparison/      # Comparison analysis
│   │   └── phase_01_summary.md        # Phase documentation
│   ├── phase_02_dual_intensity_main/  # Main thesis experiment
│   │   ├── dqn_dual_intensity/        # DQN results (79.9% success)
│   │   ├── qlearning_dual_intensity/  # Q-Learning dual (pending)
│   │   ├── algorithm_comparison/      # Algorithm comparison
│   │   └── phase_02_summary.md        # Phase documentation
│   ├── phase_03_future_experiments/   # Future research plans
│   │   ├── advanced_algorithms/       # DDPG, SAC, Rainbow DQN
│   │   ├── curriculum_learning/       # Gradual intensity progression
│   │   ├── real_world_validation/     # Hardware experiments
│   │   └── planning.md                # Future work roadmap
│   ├── consolidated_models/            # All trained models
│   │   ├── phase_01_models/           # Baseline models
│   │   ├── phase_02_models/           # Main experiment models
│   │   └── champion_models/           # Best performing models
│   └── cross_phase_analysis/          # Research-level analysis
│       ├── algorithm_evolution/       # Algorithm improvement tracking
│       ├── methodology_validation/    # Dual-intensity effectiveness
│       ├── research_timeline/         # Experimental progression
│       ├── cross_training_comparison/ # Cross-session comparisons
│       ├── publication_figures/       # Academic figures
│       └── statistical_analysis/      # Statistical validation
│
├── documentation/                     # 📚 Project Documentation
│   ├── academic/                      # Academic papers & drafts
│   ├── disturbance_system/            # Disturbance system documentation
│   ├── optimization/                  # Performance optimization guides
│   ├── project_overview/              # Project organization & summaries
│   ├── training_guides/               # Training methodology guides
│   └── trajectory_planning/           # Trajectory planning documentation
│
├── test_scripts/                      # 🧪 Testing & Validation
│   ├── analysis_scripts/              # Analysis and evaluation tools
│   ├── integration_tests/             # System integration tests
│   └── unit_tests/                    # Unit testing suite
│
└── visualization_tools/               # 📈 Plotting & Visualization
    ├── physics_diagnostics.py         # Physics system diagnostics
    ├── plot_disturbances.py          # Disturbance visualization
    ├── plot_rl_results.py            # RL results plotting
    ├── visualize_disturbances.py     # Disturbance analysis plots
    ├── visualize_trajectories.py     # Trajectory visualization
    └── screenshots/                   # Physics server screenshots
        ├── Physics Server0.png        # Simulation screenshots
        ├── Physics Server1.png        # (11 total screenshots)
        └── ...
```

## 🎯 **Key Features of This Organization**

### **Professional Structure**
- **Clean Root**: Only essential folders and files
- **Clear Separation**: Code, tools, data, docs, tests, visualization
- **Scalable**: Easy to add new modules and experiments
- **Academic Ready**: Publication-ready organization

### **Research-Oriented**
- **Phase-Based Training**: Clear experimental progression
- **Algorithm Parity**: Fair comparison structure (DQN vs Q-Learning)
- **Future-Proof**: Space for advanced experiments
- **Complete Documentation**: Every phase and component documented

### **Development-Friendly**
- **Standard Structure**: Follows Python project conventions
- **Tool Integration**: Management scripts properly organized
- **Version Control**: Clean git structure
- **Testing Support**: Comprehensive testing framework

## 📊 **Current Project Status**

### **Training Progress**
- **Phase 1**: 50% complete (Q-Learning ✅, DQN ❌)
- **Phase 2**: 50% complete (DQN ✅, Q-Learning ❌)
- **Phase 3**: Planning stage

### **Key Results**
- **DQN Dual-Intensity**: 79.9% success rate (5,000 episodes)
- **Q-Learning Baseline**: 41.3% success rate (50 episodes)
- **Performance Gap**: +93.5% improvement with DQN
- **Robustness Index**: 85.4% performance retention

### **Academic Contributions**
- **Dual-Intensity Training**: Novel φ-ratio methodology
- **IMU-Enhanced RL**: Virtual sensor integration
- **Mobile Manipulation**: Comprehensive robustness study
- **Reproducible Research**: Complete implementation package

## 🚀 **Usage Guide**

### **Running Experiments**
1. **Core Simulation**: `python src/simulation/sim_husky_kuka.py`
2. **Create Training Session**: `python tools/training/create_training_session.py`
3. **Query Results**: `python tools/training/query_training_sessions.py`

### **Analysis & Visualization**
1. **Plot Results**: `python visualization_tools/plot_rl_results.py`
2. **Analyze Training**: `python test_scripts/analysis_scripts/run_analysis.py`
3. **Generate Reports**: Check `training_data/phase_*/phase_*_summary.md`

### **Documentation**
- **Project Overview**: `README.md`
- **Training Guide**: `training_data/training_overview.md`
- **Phase Details**: `training_data/phase_*/phase_*_summary.md`
- **Technical Docs**: `documentation/`

---

**Repository**: github.com/mhar-vell/q_ws  
**Branch**: first-analysis  
**Last Updated**: October 27, 2025  
**Status**: Production-ready, academically organized