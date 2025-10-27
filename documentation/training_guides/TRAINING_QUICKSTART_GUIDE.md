# Training Data Management - Quick Start Guide

## 🚀 Setup (One-Time)

### Step 1: Organize Existing Data
```bash
# Make the script executable
chmod +x organize_archives.sh

# Run the organization script
./organize_archives.sh
```

This will:
- Create the `archives/` directory structure
- Move all documentation files to proper categories
- Organize training results by session
- Separate test scripts and visualization tools

### Step 2: Create Metadata
```bash
# Generate manifest files and experiment index
python3 create_manifest.py
```

This creates:
- `archives/02_training_sessions/training_20251016_dqn_dual_intensity_500ep_v1.0/manifest.json`
- `archives/02_training_sessions/training_20251014_qlearning_test_50ep_v0.9/manifest.json`
- `experiment_index.json` (master index)

### Step 3: Add README to Training Sessions
```bash
# Copy README to main training session
cp training_session_readme_main.md \
   archives/02_training_sessions/training_20251016_dqn_dual_intensity_500ep_v1.0/README.md
```

---

## 📊 Using the System

### List All Training Sessions
```bash
python3 query_training_sessions.py --list
```

**Output:**
```
📋 Found 2 training sessions:

✅ training_20251016_dqn_dual_intensity_500ep_v1.0
   Date: 2025-10-16
   Status: completed
   Success Rate: 79.9%
   Tags: thesis-main-results, publication-ready, dual-intensity

✅ training_20251014_qlearning_test_50ep_v0.9
   Date: 2025-10-14
   Status: completed
   Success Rate: 41.3%
   Tags: baseline-comparison, algorithm-study
```

### Filter by Status
```bash
python3 query_training_sessions.py --list --status completed
```

### Filter by Tags
```bash
python3 query_training_sessions.py --list --tags thesis-main publication
```

### Compare Training Sessions
```bash
python3 query_training_sessions.py --compare \
    training_20251016_dqn_dual_intensity_500ep_v1.0 \
    training_20251014_qlearning_test_50ep_v0.9
```

**Output:**
```
📊 Training Session Comparison:

Session                              Algorithm  Episodes  Success Rate  Normal SR  Golden SR
training_20251016_dqn_dual_inte...   DQN        500       79.9         85.2       72.8
training_20251014_qlearning_tes...   Q-Learning 50        41.3         N/A        N/A
```

### Find Best Session
```bash
python3 query_training_sessions.py --best overall_success_rate
```

---

## 🎯 Creating New Training Sessions

### Future Training Example

```bash
# Create new training session structure
python3 create_training_session.py \
    --algorithm rainbow \
    --feature triple_intensity \
    --episodes 1000 \
    --version 2.0 \
    --purpose "Extended robustness study with three intensity levels" \
    --tags thesis-extension advanced-robustness
```

**This creates:**
```
archives/02_training_sessions/training_20251121_rainbow_triple_intensity_1000ep_v2.0/
├── config/
├── checkpoints/
│   ├── none_scenario/
│   ├── random_scenario/
│   ├── periodic_scenario/
│   ├── continuous_scenario/
│   └── impulse_scenario/
├── final_models/
├── metrics/
├── analysis/
├── videos/
├── manifest.json (initialized)
└── README.md (template)
```

### Update Training Code

Modify your training script to save to the new session:

```python
# In sim_husky_kuka.py or your training script

SESSION_DIR = "archives/02_training_sessions/training_20251121_rainbow_triple_intensity_1000ep_v2.0"

# Save checkpoints
checkpoint_path = f"{SESSION_DIR}/checkpoints/{scenario}_scenario/rl_checkpoint_{scenario}_ep{episode}.pth"
torch.save(agent.state_dict(), checkpoint_path)

# Save final models
final_model_path = f"{SESSION_DIR}/final_models/rl_final_{scenario}_{intensity}.pth"
torch.save(agent.state_dict(), final_model_path)

# Save metrics
metrics_path = f"{SESSION_DIR}/metrics/rl_metrics.json"
with open(metrics_path, 'w') as f:
    json.dump(metrics, f)

# Save analysis plots
plot_path = f"{SESSION_DIR}/analysis/training_analysis_{timestamp}.png"
plt.savefig(plot_path)
```

### After Training Completes

```bash
# Update manifest with results
# Edit: archives/02_training_sessions/SESSION_ID/manifest.json
# Add: results_summary section

# Update README
# Edit: archives/02_training_sessions/SESSION_ID/README.md
# Update: Results section, mark checkboxes complete

# Query to see new session
python3 query_training_sessions.py --list
```

---

## 📁 Directory Structure

```
q_ws/
│
├── archives/
│   ├── 01_documentation/          # All .md guides
│   ├── 02_training_sessions/      # Each training isolated
│   │   ├── training_20251016_dqn_dual_intensity_500ep_v1.0/
│   │   │   ├── manifest.json      # Complete metadata
│   │   │   ├── README.md          # Human-readable summary
│   │   │   ├── config/            # Hyperparameters
│   │   │   ├── checkpoints/       # By scenario
│   │   │   ├── final_models/      # Trained models
│   │   │   ├── metrics/           # JSON data
│   │   │   ├── analysis/          # Plots
│   │   │   └── videos/            # Recordings
│   │   └── training_20251121_rainbow_triple_intensity_1000ep_v2.0/
│   │       └── [same structure]
│   ├── 03_comparative_analysis/   # Cross-session comparisons
│   ├── 04_test_scripts/           # Unit/integration tests
│   ├── 05_visualization_tools/    # Plotting scripts
│   └── 06_experiment_logs/        # Timeline, lessons learned
│
├── experiment_index.json          # Master index of all trainings
├── create_training_session.py     # Create new session
├── query_training_sessions.py     # Query/compare sessions
├── create_manifest.py             # Generate metadata
├── organize_archives.sh           # Organize files
│
└── [core development files]       # Active code
    ├── sim_husky_kuka.py
    ├── rl_mission_env.py
    ├── rl_trajectory_planner.py
    └── ...
```

---

## 🔍 Finding Your Data

### "Which training was for my thesis?"
```bash
python3 query_training_sessions.py --list --tags thesis-main
```

### "Show me all DQN trainings"
```bash
# Look at experiment_index.json
cat experiment_index.json | jq '.training_sessions[] | select(.algorithm=="DQN")'
```

### "What were the exact hyperparameters?"
```bash
# Check manifest
cat archives/02_training_sessions/SESSION_ID/manifest.json | jq .algorithm
```

### "Get all analysis plots from Oct 16 training"
```bash
ls archives/02_training_sessions/training_20251016_dqn_dual_intensity_500ep_v1.0/analysis/
```

### "Compare this month vs next month training"
```bash
python3 query_training_sessions.py --compare \
    training_20251016_dqn_dual_intensity_500ep_v1.0 \
    training_20251121_rainbow_triple_intensity_1000ep_v2.0
```

---

## 📊 Workflow Examples

### Example 1: Running Extended Training (November 2025)

```bash
# 1. Create session structure
python3 create_training_session.py \
    --algorithm dqn \
    --feature extended_1000ep \
    --episodes 1000 \
    --version 1.5 \
    --purpose "Extended training for better convergence" \
    --tags thesis-extension

# 2. Update training script to use new session directory
# Edit sim_husky_kuka.py to save to:
# archives/02_training_sessions/training_20251115_dqn_extended_1000ep_v1.5/

# 3. Run training
python3 sim_husky_kuka.py

# 4. After completion, update manifest.json with results

# 5. Compare with original
python3 query_training_sessions.py --compare \
    training_20251016_dqn_dual_intensity_500ep_v1.0 \
    training_20251115_dqn_extended_1000ep_v1.5
```

### Example 2: Testing New Algorithm (December 2025)

```bash
# 1. Create session for Rainbow DQN
python3 create_training_session.py \
    --algorithm rainbow \
    --feature dueling_prioritized \
    --episodes 500 \
    --version 2.0 \
    --purpose "Test Rainbow DQN improvements" \
    --tags algorithm-comparison experimental

# 2. Implement Rainbow DQN in rl_mission_env.py

# 3. Train and save to session directory

# 4. Compare against baseline DQN
python3 query_training_sessions.py --compare \
    training_20251016_dqn_dual_intensity_500ep_v1.0 \
    training_20251205_rainbow_dueling_prioritized_500ep_v2.0
```

### Example 3: Real Hardware Validation (January 2026)

```bash
# 1. Create session for hardware experiments
python3 create_training_session.py \
    --algorithm dqn \
    --feature real_hardware \
    --episodes 300 \
    --version 3.0 \
    --purpose "Sim-to-real transfer validation" \
    --tags real-hardware sim2real validation

# 2. Transfer trained model to hardware

# 3. Record real-world performance data

# 4. Save metrics to session directory

# 5. Compare sim vs real
python3 query_training_sessions.py --compare \
    training_20251016_dqn_dual_intensity_500ep_v1.0 \
    training_20260115_dqn_real_hardware_300ep_v3.0
```

---

## ✅ Best Practices

### Before New Training
- [ ] Run `create_training_session.py`
- [ ] Update code to save to new session directory
- [ ] Commit current code and note git hash
- [ ] Document purpose in manifest

### During Training
- [ ] Save checkpoints to session `checkpoints/` folder
- [ ] Log metrics to session `metrics/` folder
- [ ] Monitor and document issues
- [ ] Save videos to session `videos/` folder

### After Training
- [ ] Update `manifest.json` with results
- [ ] Complete README.md with findings
- [ ] Generate analysis plots to `analysis/` folder
- [ ] Mark status as "completed" in manifest
- [ ] Tag as "primary" if main result
- [ ] Update `experiment_index.json`

---

## 🎯 Quick Commands Reference

```bash
# List all sessions
python3 query_training_sessions.py --list

# Filter completed sessions
python3 query_training_sessions.py --list --status completed

# Find thesis results
python3 query_training_sessions.py --list --tags thesis-main

# Compare two sessions
python3 query_training_sessions.py --compare SESSION_ID_1 SESSION_ID_2

# Find best performing
python3 query_training_sessions.py --best overall_success_rate

# Create new session
python3 create_training_session.py --algorithm ALGO --feature FEAT --episodes N --version X.Y

# View manifest
cat archives/02_training_sessions/SESSION_ID/manifest.json | jq .

# View experiment index
cat experiment_index.json | jq .

# List all training dates
ls -lt archives/02_training_sessions/ | grep training_
```

---

## 📚 Documentation Index

| Document | Location | Purpose |
|----------|----------|---------|
| This Guide | `TRAINING_DATA_MANAGEMENT_GUIDE.md` | Complete system documentation |
| Quick Start | `TRAINING_QUICKSTART_GUIDE.md` | This file |
| Archive Plan | `ARCHIVE_ORGANIZATION_PLAN_V2.md` | Directory structure design |
| Experiment Index | `experiment_index.json` | Master training list |
| Session Manifest | `archives/02_training_sessions/*/manifest.json` | Session metadata |
| Session README | `archives/02_training_sessions/*/README.md` | Session summary |

---

## 🆘 Troubleshooting

### "I can't find a training result"
1. Check `experiment_index.json` for session list
2. Use `query_training_sessions.py --list` to see all sessions
3. Search by tags: `--tags thesis-main`

### "I want to reproduce a training"
1. Find session: `query_training_sessions.py --list`
2. Check manifest: `cat archives/02_training_sessions/SESSION_ID/manifest.json`
3. Get git commit: Look for `session_info.git_commit`
4. Checkout code: `git checkout COMMIT_HASH`
5. Use hyperparameters from manifest

### "How do I know which is the main result?"
Look for `"primary": true` in `experiment_index.json` or check tags for `thesis-main`.

### "I need to add a new training"
Run `create_training_session.py` with appropriate parameters. It handles everything automatically.

---

## 🎓 Academic Use

### For Your Thesis
- Main results: `training_20251016_dqn_dual_intensity_500ep_v1.0`
- Manifest has complete configuration
- README has results summary
- All plots in `analysis/` folder

### For Your Paper
- Use data from session manifest
- Copy plots from `archives/03_comparative_analysis/publication_figures/`
- Cite specific session ID in methods

### For Reproducibility
- Share experiment_index.json
- Provide manifest files
- Include git commit hash
- List exact hyperparameters

---

**System created**: 2025-10-21  
**Current version**: 1.1.0  
**Status**: Ready to use ✅
