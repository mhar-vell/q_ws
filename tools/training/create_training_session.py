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
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=os.path.dirname(__file__)
        ).decode('ascii').strip()
    except:
        return "unknown"

def get_git_branch():
    """Get current git branch."""
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=os.path.dirname(__file__)
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
            "git_branch": get_git_branch(),
            "code_version": version,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        "hardware": {
            "device": "Unknown",
            "gpu": "Unknown",
            "ram_gb": None,
            "cpu_cores": None
        },
        "algorithm": {
            "name": algorithm.upper(),
            "implementation": "rl_mission_env.py",
            "network_architecture": [],
            "optimizer": None,
            "learning_rate": None,
            "discount_factor": None,
            "epsilon_start": None,
            "epsilon_end": None,
            "epsilon_decay": None,
            "replay_buffer_size": None,
            "batch_size": None,
            "target_update_frequency": None
        },
        "training_config": {
            "episodes_per_scenario": episodes,
            "max_steps_per_episode": 200,
            "scenarios": ["none", "random", "periodic", "continuous", "impulse"],
            "intensities": ["normal", "golden"],
            "golden_multiplier": 1.61803398874989,
            "total_combinations": 10,
            "total_episodes": episodes * 10,
            "checkpoint_frequency": 100
        },
        "environment": {
            "simulator": "PyBullet",
            "simulator_version": "202010061",
            "robot_base": "Husky",
            "robot_arm": "KUKA LBR iiwa 7 R800",
            "imu_noise_enabled": True,
            "imu_accel_noise_std": 0.02,
            "imu_gyro_noise_std": 0.01,
            "physics_timestep": 0.004167,
            "control_frequency": 60
        },
        "results_summary": {
            "overall_success_rate": None,
            "normal_intensity_success_rate": None,
            "golden_intensity_success_rate": None,
            "robustness_index": None,
            "best_scenario": None,
            "best_success_rate": None,
            "worst_scenario": None,
            "worst_success_rate": None,
            "average_episode_length": None,
            "convergence_episode": None
        },
        "files": {
            "checkpoints_count": 0,
            "final_models_count": 0,
            "metrics_files": [],
            "analysis_plots": [],
            "videos_count": 0,
            "total_size_mb": 0
        },
        "notes": {
            "purpose": purpose,
            "key_findings": [],
            "issues_encountered": [],
            "improvements_for_next_time": []
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
- **Total Episodes**: {episodes * 10}
- **Version**: {version}
- **Git Commit**: {get_git_commit()}
- **Git Branch**: {get_git_branch()}

## Purpose
{purpose or "TODO: Add purpose description"}

## Configuration
TODO: Add detailed hyperparameters

## Progress
- [ ] none_normal (0/{episodes})
- [ ] none_golden (0/{episodes})
- [ ] random_normal (0/{episodes})
- [ ] random_golden (0/{episodes})
- [ ] periodic_normal (0/{episodes})
- [ ] periodic_golden (0/{episodes})
- [ ] continuous_normal (0/{episodes})
- [ ] continuous_golden (0/{episodes})
- [ ] impulse_normal (0/{episodes})
- [ ] impulse_golden (0/{episodes})

## Results
TODO: Update as training progresses

## Files
- Checkpoints: 0
- Final Models: 0
- Metrics: 0
- Analysis Plots: 0
- Videos: 0

## Notes
- Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Purpose: {purpose or "Not specified"}
- Tags: {', '.join(tags or [])}

## Updates Log
### {datetime.now().strftime("%Y-%m-%d %H:%M")}
- Training session created
- Directory structure initialized
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
            "code_repository": "https://github.com/mhar-vell/q_ws",
            "current_version": version,
            "training_sessions": [],
            "milestones": []
        }
    
    # Add new session to index
    index["training_sessions"].append({
        "session_id": session_id,
        "date": date_str,
        "status": "in_progress",
        "primary": False,
        "tags": tags or [],
        "success_rate": None,
        "notes": purpose
    })
    
    # Update current version if newer
    if not index.get("current_version") or version > index.get("current_version", "0.0.0"):
        index["current_version"] = version
    
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
