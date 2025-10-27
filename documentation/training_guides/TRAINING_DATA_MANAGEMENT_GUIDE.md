# Training Data Management Strategy - Future-Proof System

## 🎯 **Problem Statement**

As your project evolves, you'll have:
- Multiple training runs with different configurations
- Experiments with various hyperparameters
- Tests on different hardware
- Iterations with code improvements
- Comparison studies
- Ablation studies

**Challenge**: How to keep them organized and easily identifiable?

---

## 📋 **Solution: Structured Naming & Metadata System**

### **1. Training Session Naming Convention**

Use this standardized format:

```
training_[DATE]_[ALGORITHM]_[KEY_FEATURE]_[EPISODES]ep_v[VERSION]
```

**Examples:**

```bash
# Current training
training_20251015_dqn_dual_intensity_500ep_v1.0

# Future trainings
training_20251118_dqn_triple_intensity_1000ep_v2.0
training_20251201_rainbow_real_hardware_300ep_v2.1
training_20260115_sac_continuous_actions_500ep_v3.0
training_20260220_ppo_sim2real_1000ep_v3.5
```

**Format Breakdown:**
- `DATE`: YYYYMMDD (sortable chronologically)
- `ALGORITHM`: dqn, qlearning, rainbow, sac, ppo, td3, etc.
- `KEY_FEATURE`: What makes this training unique
- `EPISODES`: Total episode count per scenario
- `VERSION`: Semantic versioning tied to code version

---

## 🏷️ **2. Metadata System**

### **A) Training Manifest File**

Each training session MUST have a `manifest.json`:

```json
{
  "session_info": {
    "session_id": "training_20251015_dqn_dual_intensity_500ep_v1.0",
    "date_started": "2025-10-15T14:30:00Z",
    "date_completed": "2025-10-15T15:12:00Z",
    "duration_minutes": 42,
    "status": "completed",
    "git_commit": "a3f5c2d",
    "code_version": "1.0.0",
    "python_version": "3.11.5",
    "pytorch_version": "2.8.0"
  },
  
  "hardware": {
    "device": "Apple M2 Pro",
    "gpu": "MPS (Metal Performance Shaders)",
    "ram_gb": 16,
    "cpu_cores": 10
  },
  
  "algorithm": {
    "name": "Deep Q-Network (DQN)",
    "implementation": "rl_mission_env.py::DQNAgent",
    "network_architecture": [35, 128, 128, 10],
    "optimizer": "Adam",
    "learning_rate": 0.001,
    "discount_factor": 0.99,
    "epsilon_start": 1.0,
    "epsilon_end": 0.01,
    "epsilon_decay": 0.995,
    "replay_buffer_size": 10000,
    "batch_size": 32,
    "target_update_frequency": 100
  },
  
  "training_config": {
    "episodes_per_scenario": 500,
    "max_steps_per_episode": 200,
    "scenarios": ["none", "random", "periodic", "continuous", "impulse"],
    "intensities": ["normal", "golden"],
    "golden_multiplier": 1.61803398874989,
    "total_combinations": 10,
    "total_episodes": 5000,
    "checkpoint_frequency": 100
  },
  
  "environment": {
    "simulator": "PyBullet",
    "simulator_version": "202010061",
    "robot_base": "Husky",
    "robot_arm": "KUKA LBR iiwa 7 R800",
    "imu_noise_enabled": true,
    "imu_accel_noise_std": 0.02,
    "imu_gyro_noise_std": 0.01,
    "physics_timestep": 0.004167,
    "control_frequency": 60
  },
  
  "results_summary": {
    "overall_success_rate": 79.9,
    "normal_intensity_success_rate": 85.2,
    "golden_intensity_success_rate": 72.8,
    "robustness_index": 0.854,
    "best_scenario": "none_normal",
    "best_success_rate": 92.4,
    "worst_scenario": "impulse_golden",
    "worst_success_rate": 67.9,
    "average_episode_length": 156.4,
    "convergence_episode": 35
  },
  
  "files": {
    "checkpoints_count": 25,
    "final_models_count": 10,
    "metrics_files": ["rl_metrics_dqn.json"],
    "analysis_plots": [
      "rl_training_analysis_20251016_093606.png",
      "real_rl_training_analysis_20251016_093735.png",
      "rl_performance_summary_20251016_093910.png",
      "accuracy_drop_analysis.png"
    ],
    "videos_count": 15,
    "total_size_mb": 487
  },
  
  "notes": {
    "purpose": "Main thesis experiment - dual-intensity robustness training",
    "key_findings": [
      "DQN achieves 79.9% average success rate across all combinations",
      "Golden intensity training improves robustness (85.4% retention)",
      "IMU integration provides 27.8pp improvement over no-IMU baseline",
      "Periodic disturbances most predictable (86.3% normal, 73.8% golden)"
    ],
    "issues_encountered": [
      "Initial key conflict bug (t key) - fixed",
      "PyTorch tensor creation performance warning - optimized",
      "Early timeout messages normal during exploration phase"
    ],
    "improvements_for_next_time": [
      "Increase episodes to 1000 per scenario",
      "Try curriculum learning for intensity progression",
      "Add more IMU sensor positions",
      "Test with real hardware noise profiles"
    ]
  },
  
  "tags": [
    "thesis-main-results",
    "dual-intensity",
    "dqn",
    "robustness-study",
    "imu-enhanced",
    "publication-ready"
  ]
}
```

### **B) Experiment Index File**

Create a master index at workspace root: `experiment_index.json`

```json
{
  "project_name": "Robust Mobile Manipulator Control via Deep RL",
  "project_start_date": "2025-10-10",
  "code_repository": "https://github.com/mhar-vell/q_ws",
  "current_version": "1.0.0",
  
  "training_sessions": [
    {
      "session_id": "training_20251015_dqn_dual_intensity_500ep_v1.0",
      "date": "2025-10-15",
      "status": "completed",
      "primary": true,
      "tags": ["thesis-main", "publication"],
      "success_rate": 79.9,
      "notes": "Main results for thesis and paper"
    },
    {
      "session_id": "training_20251014_qlearning_test_50ep_v0.9",
      "date": "2025-10-14",
      "status": "completed",
      "primary": false,
      "tags": ["baseline-comparison", "algorithm-study"],
      "success_rate": 41.3,
      "notes": "Q-Learning baseline for comparison"
    },
    {
      "session_id": "training_20251013_legacy_single_intensity_v0.8",
      "date": "2025-10-13",
      "status": "completed",
      "primary": false,
      "tags": ["legacy", "pre-dual-intensity"],
      "success_rate": 52.8,
      "notes": "Before dual-intensity implementation"
    }
  ],
  
  "milestones": [
    {
      "date": "2025-10-10",
      "version": "0.5.0",
      "description": "Initial RL integration",
      "git_commit": "1a2b3c4"
    },
    {
      "date": "2025-10-13",
      "version": "0.8.0",
      "description": "Single intensity training working",
      "git_commit": "5d6e7f8"
    },
    {
      "date": "2025-10-14",
      "version": "0.9.0",
      "description": "Dual-intensity system implemented",
      "git_commit": "9a0b1c2"
    },
    {
      "date": "2025-10-15",
      "version": "1.0.0",
      "description": "Production training completed",
      "git_commit": "a3f5c2d"
    }
  ]
}
```

---

## 🔧 **3. Automated Session Initialization**

### **Create Training Session Script**

Save as `create_training_session.py`:

```python
#!/usr/bin/env python3
"""
Automated training session initialization script.
Creates proper directory structure and metadata files.
"""

import json
import os
from datetime import datetime
import subprocess
import sys

def get_git_commit():
    """Get current git commit hash."""
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD']
        ).decode('ascii').strip()
    except:
        return "unknown"

def create_training_session(
    algorithm: str,
    feature: str,
    episodes: int,
    version: str,
    purpose: str = "",
    tags: list = None
):
    """
    Create a new training session with proper structure.
    
    Args:
        algorithm: e.g., "dqn", "qlearning", "rainbow"
        feature: e.g., "dual_intensity", "curriculum_learning"
        episodes: Episodes per scenario
        version: Semantic version (e.g., "1.0")
        purpose: Brief description of training purpose
        tags: List of tags for categorization
    """
    
    # Generate session ID
    date_str = datetime.now().strftime("%Y%m%d")
    session_id = f"training_{date_str}_{algorithm}_{feature}_{episodes}ep_v{version}"
    
    # Create directory structure
    base_path = f"archives/02_training_sessions/{session_id}"
    dirs = [
        f"{base_path}/config",
        f"{base_path}/checkpoints/none_scenario",
        f"{base_path}/checkpoints/random_scenario",
        f"{base_path}/checkpoints/periodic_scenario",
        f"{base_path}/checkpoints/continuous_scenario",
        f"{base_path}/checkpoints/impulse_scenario",
        f"{base_path}/final_models",
        f"{base_path}/metrics",
        f"{base_path}/analysis",
        f"{base_path}/videos"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Created: {dir_path}")
    
    # Create manifest.json
    manifest = {
        "session_info": {
            "session_id": session_id,
            "date_started": datetime.now().isoformat(),
            "date_completed": None,
            "duration_minutes": None,
            "status": "in_progress",
            "git_commit": get_git_commit(),
            "code_version": version,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        "algorithm": {
            "name": algorithm.upper(),
        },
        "training_config": {
            "episodes_per_scenario": episodes,
            "scenarios": ["none", "random", "periodic", "continuous", "impulse"],
            "intensities": ["normal", "golden"],
        },
        "notes": {
            "purpose": purpose,
        },
        "tags": tags or []
    }
    
    manifest_path = f"{base_path}/manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"✓ Created: {manifest_path}")
    
    # Create README template
    readme_content = f"""# Training Session: {session_id}

## Status
🟡 **IN PROGRESS** - Started {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Overview
- **Algorithm**: {algorithm.upper()}
- **Key Feature**: {feature.replace('_', ' ').title()}
- **Episodes**: {episodes} per scenario
- **Version**: {version}
- **Git Commit**: {get_git_commit()}

## Purpose
{purpose or "TODO: Add purpose description"}

## Configuration
TODO: Add detailed hyperparameters

## Progress
- [ ] none_normal
- [ ] none_golden
- [ ] random_normal
- [ ] random_golden
- [ ] periodic_normal
- [ ] periodic_golden
- [ ] continuous_normal
- [ ] continuous_golden
- [ ] impulse_normal
- [ ] impulse_golden

## Results
TODO: Update as training progresses

## Notes
- Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    readme_path = f"{base_path}/README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    print(f"✓ Created: {readme_path}")
    
    # Update experiment index
    index_path = "experiment_index.json"
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            index = json.load(f)
    else:
        index = {
            "project_name": "Robust Mobile Manipulator Control via Deep RL",
            "project_start_date": datetime.now().strftime("%Y-%m-%d"),
            "training_sessions": []
        }
    
    # Add new session to index
    index["training_sessions"].append({
        "session_id": session_id,
        "date": date_str,
        "status": "in_progress",
        "primary": False,
        "tags": tags or [],
        "notes": purpose
    })
    
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    print(f"✓ Updated: {index_path}")
    
    print(f"\n✅ Training session created: {session_id}")
    print(f"📁 Location: {base_path}")
    print(f"\n🚀 Next steps:")
    print(f"   1. Update config in: {base_path}/config/")
    print(f"   2. Run training and save to: {base_path}/")
    print(f"   3. Update manifest.json when complete")
    print(f"   4. Generate analysis plots")
    
    return session_id, base_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create new training session")
    parser.add_argument("--algorithm", required=True, help="Algorithm name (dqn, rainbow, etc.)")
    parser.add_argument("--feature", required=True, help="Key feature (dual_intensity, etc.)")
    parser.add_argument("--episodes", type=int, required=True, help="Episodes per scenario")
    parser.add_argument("--version", required=True, help="Code version (e.g., 1.0)")
    parser.add_argument("--purpose", default="", help="Training purpose")
    parser.add_argument("--tags", nargs="+", default=[], help="Tags for categorization")
    
    args = parser.parse_args()
    
    create_training_session(
        algorithm=args.algorithm,
        feature=args.feature,
        episodes=args.episodes,
        version=args.version,
        purpose=args.purpose,
        tags=args.tags
    )
```

**Usage:**

```bash
# Future training example
python create_training_session.py \
    --algorithm rainbow \
    --feature triple_intensity \
    --episodes 1000 \
    --version 2.0 \
    --purpose "Extended robustness study with triple intensity levels" \
    --tags thesis-extension advanced-robustness

# Output:
# ✓ Created: archives/02_training_sessions/training_20251118_rainbow_triple_intensity_1000ep_v2.0/
# ✓ Created manifest, README, directory structure
# ✅ Ready for training!
```

---

## 🔍 **4. Query and Comparison System**

### **Training Session Query Script**

Save as `query_training_sessions.py`:

```python
#!/usr/bin/env python3
"""
Query and compare training sessions.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd

class TrainingSessionManager:
    def __init__(self, base_path="archives/02_training_sessions"):
        self.base_path = base_path
        self.sessions = self._load_sessions()
    
    def _load_sessions(self):
        """Load all training session manifests."""
        sessions = []
        
        if not os.path.exists(self.base_path):
            return sessions
        
        for session_dir in os.listdir(self.base_path):
            if not session_dir.startswith("training_"):
                continue
            
            manifest_path = f"{self.base_path}/{session_dir}/manifest.json"
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    manifest['session_dir'] = session_dir
                    sessions.append(manifest)
        
        return sessions
    
    def list_sessions(self, status=None, tags=None):
        """List training sessions with filters."""
        filtered = self.sessions
        
        if status:
            filtered = [s for s in filtered if s['session_info']['status'] == status]
        
        if tags:
            filtered = [
                s for s in filtered 
                if any(tag in s.get('tags', []) for tag in tags)
            ]
        
        print(f"\n📋 Found {len(filtered)} training sessions:\n")
        
        for session in filtered:
            info = session['session_info']
            results = session.get('results_summary', {})
            
            status_icon = {
                'completed': '✅',
                'in_progress': '🟡',
                'failed': '❌'
            }.get(info['status'], '❓')
            
            print(f"{status_icon} {info['session_id']}")
            print(f"   Date: {info['date_started'][:10]}")
            print(f"   Status: {info['status']}")
            print(f"   Success Rate: {results.get('overall_success_rate', 'N/A')}%")
            print(f"   Tags: {', '.join(session.get('tags', []))}")
            print()
    
    def compare_sessions(self, session_ids):
        """Compare multiple training sessions."""
        sessions_data = []
        
        for session_id in session_ids:
            session = next((s for s in self.sessions 
                          if s['session_info']['session_id'] == session_id), None)
            
            if session:
                sessions_data.append({
                    'Session': session_id[:40] + "...",
                    'Algorithm': session['algorithm']['name'],
                    'Episodes': session['training_config']['episodes_per_scenario'],
                    'Success Rate': session.get('results_summary', {}).get('overall_success_rate', 'N/A'),
                    'Normal SR': session.get('results_summary', {}).get('normal_intensity_success_rate', 'N/A'),
                    'Golden SR': session.get('results_summary', {}).get('golden_intensity_success_rate', 'N/A'),
                    'Robustness Index': session.get('results_summary', {}).get('robustness_index', 'N/A'),
                    'Duration (min)': session['session_info'].get('duration_minutes', 'N/A')
                })
        
        df = pd.DataFrame(sessions_data)
        print("\n📊 Training Session Comparison:\n")
        print(df.to_string(index=False))
    
    def get_best_session(self, metric='overall_success_rate'):
        """Find best performing session."""
        completed = [s for s in self.sessions 
                    if s['session_info']['status'] == 'completed']
        
        if not completed:
            print("No completed sessions found")
            return None
        
        best = max(completed, 
                  key=lambda s: s.get('results_summary', {}).get(metric, 0))
        
        print(f"\n🏆 Best session by {metric}:")
        print(f"   {best['session_info']['session_id']}")
        print(f"   {metric}: {best['results_summary'][metric]}")
        
        return best

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Query training sessions")
    parser.add_argument("--list", action="store_true", help="List all sessions")
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--tags", nargs="+", help="Filter by tags")
    parser.add_argument("--compare", nargs="+", help="Compare sessions")
    parser.add_argument("--best", help="Find best session by metric")
    
    args = parser.parse_args()
    
    manager = TrainingSessionManager()
    
    if args.list:
        manager.list_sessions(status=args.status, tags=args.tags)
    elif args.compare:
        manager.compare_sessions(args.compare)
    elif args.best:
        manager.get_best_session(metric=args.best)
```

**Usage:**

```bash
# List all completed sessions
python query_training_sessions.py --list --status completed

# List sessions with specific tags
python query_training_sessions.py --list --tags thesis-main publication

# Compare two training sessions
python query_training_sessions.py --compare \
    training_20251015_dqn_dual_intensity_500ep_v1.0 \
    training_20251118_rainbow_triple_intensity_1000ep_v2.0

# Find best session by success rate
python query_training_sessions.py --best overall_success_rate
```

---

## 📊 **5. Version Control Integration**

### **Git Tagging for Major Trainings**

```bash
# Tag important training milestones
git tag -a v1.0-main-training -m "Main DQN dual-intensity training (thesis results)"
git tag -a v2.0-extended-training -m "Extended training with 1000 episodes"
git push origin --tags

# Later, checkout code state at specific training
git checkout v1.0-main-training
```

### **.gitignore Configuration**

```gitignore
# In your .gitignore

# Large model files (use Git LFS or external storage)
*.pth
*.pkl
*.h5
*.ckpt

# But keep manifest files
!*/manifest.json

# Videos are large
videos/
*.mp4
*.avi

# Metrics are small, keep them
!*/metrics/*.json

# Analysis plots are medium, maybe keep
# !*/analysis/*.png  # Uncomment if you want to track
```

### **Git LFS for Large Files** (Optional)

```bash
# Install Git LFS
git lfs install

# Track model files
git lfs track "*.pth"
git lfs track "*.pkl"

# Commit .gitattributes
git add .gitattributes
git commit -m "Configure Git LFS for model files"
```

---

## 🎯 **6. Decision Tree: "Which Training is This?"**

```
START: Found a model file or result
│
├─ Check manifest.json
│  ├─ session_id → Unique identifier
│  ├─ date_started → When it ran
│  ├─ git_commit → Code version
│  ├─ tags → Purpose categories
│  └─ results_summary → Performance metrics
│
├─ Check experiment_index.json
│  ├─ Find session in list
│  ├─ Check "primary" flag → Is this the main result?
│  └─ Read notes → Why this training exists
│
├─ Check directory name
│  └─ training_[DATE]_[ALGO]_[FEATURE]_[EP]ep_v[VER]
│
└─ Check README.md
   └─ Human-readable summary

RESULT: Full training context identified!
```

---

## ✅ **7. Best Practices Checklist**

### **Before Starting New Training:**
- [ ] Create new session with `create_training_session.py`
- [ ] Update `manifest.json` with configuration
- [ ] Commit current code and note git hash
- [ ] Document purpose and expected outcomes

### **During Training:**
- [ ] Save checkpoints to session directory
- [ ] Log metrics to session metrics folder
- [ ] Update progress in README.md
- [ ] Monitor for issues and document them

### **After Training:**
- [ ] Complete `manifest.json` results_summary
- [ ] Generate analysis plots to session analysis folder
- [ ] Update status to "completed"
- [ ] Tag as primary if it's main result
- [ ] Add to experiment_index.json
- [ ] Git tag for major milestones

### **Documentation:**
- [ ] Write key findings in manifest notes
- [ ] Document issues encountered
- [ ] List improvements for next time
- [ ] Update cross-session comparisons

---

## 🚀 **8. Future Training Example**

### **Scenario: You want to run extended training in November 2025**

```bash
# Step 1: Create new training session
python create_training_session.py \
    --algorithm rainbow \
    --feature triple_intensity \
    --episodes 1000 \
    --version 2.0 \
    --purpose "Extended robustness with φ, φ², φ³ intensity levels" \
    --tags thesis-extension advanced-robustness long-training

# Output:
# ✅ Created: archives/02_training_sessions/training_20251118_rainbow_triple_intensity_1000ep_v2.0/

# Step 2: Update training code to save to new session directory
SESSION_DIR = "archives/02_training_sessions/training_20251118_rainbow_triple_intensity_1000ep_v2.0"

# Step 3: Run training
python sim_husky_kuka.py  # Your training code

# Step 4: After completion, query results
python query_training_sessions.py --compare \
    training_20251015_dqn_dual_intensity_500ep_v1.0 \
    training_20251118_rainbow_triple_intensity_1000ep_v2.0

# Output:
# 📊 Training Session Comparison:
# 
# Session                              Algorithm  Episodes  Success Rate  Normal SR  Golden SR
# training_20251015_dqn_dual_inte...   DQN        500       79.9         85.2       72.8
# training_20251118_rainbow_triple...  RAINBOW    1000      87.3         91.1       85.4
```

---

## 📚 **9. Quick Reference Commands**

```bash
# List all training sessions
python query_training_sessions.py --list

# Find thesis-main results
python query_training_sessions.py --list --tags thesis-main

# Compare two sessions
python query_training_sessions.py --compare SESSION_ID_1 SESSION_ID_2

# Find best performing session
python query_training_sessions.py --best overall_success_rate

# Create new training session
python create_training_session.py --algorithm ALGO --feature FEATURE --episodes N --version X.Y

# Check current session details
cat archives/02_training_sessions/SESSION_ID/manifest.json | jq .

# List all completed trainings by date
ls -lt archives/02_training_sessions/ | grep training_
```

---

## 💡 **Summary: How to Separate Training Data**

### **The Answer:**

1. **Unique Session ID**: `training_[DATE]_[ALGO]_[FEATURE]_[EP]ep_v[VER]`
2. **Isolated Directories**: Each session in separate folder
3. **Rich Metadata**: `manifest.json` with complete configuration
4. **Master Index**: `experiment_index.json` tracks all sessions
5. **Tags & Flags**: Mark primary results, categorize by purpose
6. **Git Integration**: Tag important training milestones
7. **Automated Tools**: Scripts to create, query, compare sessions

### **Result:**
✅ **Never lose track of which training is which**  
✅ **Easy comparison across training runs**  
✅ **Complete reproducibility**  
✅ **Clear timeline of project evolution**  
✅ **Publication-ready organization**

---

Would you like me to:
1. ✅ **Generate these scripts for your current project?**
2. ✅ **Create manifest.json for your existing training?**
3. ✅ **Set up the experiment index?**
4. ✅ **Create the query/comparison tools?**
