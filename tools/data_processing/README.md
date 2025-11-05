# Data Processing Tools

This directory contains scripts for extracting, processing, and analyzing training data.

## Scripts

### extract_qlearning_metrics.py

**Purpose**: Extract performance metrics from Q-Learning checkpoint files

**Description**: Since the Q-Learning metrics JSON was not fully populated during training (only contained 1/10 scenarios), this script loads all Q-table checkpoint files and extracts comprehensive performance metrics.

**Input**: 
- Q-table checkpoint files from: `training_data/phase_03_algorithm_core/qlearning_algorithm_core/checkpoints/*/`
- Processes 100 checkpoint files across 5 scenario types × 2 intensities

**Output**:
- `rl_metrics_q-learning_extracted.json` - Complete metrics for all 10 scenarios
- Contains: Q-value statistics, convergence scores, state space growth, training progression

**Usage**:
```bash
python3 tools/data_processing/extract_qlearning_metrics.py
```

**Features**:
- Analyzes Q-table quality (convergence, stability, value distribution)
- Tracks state space growth over training
- Calculates convergence scores using temporal difference
- Extracts mean/std/min/max Q-values for each checkpoint
- Generates comprehensive training progression data

**Output Stats**:
- Total scenarios: 10 (5 disturbance types × 2 intensities)
- Episodes per scenario: 2000
- Checkpoints per scenario: 19-20
- Final metrics include: convergence scores (0.55-0.97), Q-table sizes (42-330K states)

---

## Directory Purpose

This directory centralizes all data extraction and processing scripts to maintain a clean separation between:
- **Data processing** (this directory)
- **Visualization** (visualization_tools/plotting/)
- **Analysis documentation** (training_data/.../algorithm_analysis/)
