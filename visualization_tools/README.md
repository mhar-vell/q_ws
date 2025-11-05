# Visualization Tools

Comprehensive visualization and plotting utilities for analyzing training results, trajectories, disturbances, and system behavior.

## Directory Structure

```
visualization_tools/
├── README.md                          # This file
├── plotting/                          # Static plot generation
│   ├── plot_disturbances.py          # Plot disturbance force/torque data
│   └── plot_rl_results.py            # Plot RL training metrics
├── interactive/                       # Interactive visualizations
│   ├── visualize_disturbances.py     # Interactive disturbance visualization
│   └── visualize_trajectories.py     # Interactive trajectory visualization
└── outputs/                           # Generated outputs
    ├── plots/                         # Static plot images (.png, .pdf)
    ├── videos/                        # Video recordings (.mp4, .avi)
    └── images/                        # Screenshots and diagrams
        └── screenshots/               # Simulation screenshots
```

---

## Quick Reference

| Tool | Purpose | Output Location | Usage |
|------|---------|-----------------|-------|
| `plot_disturbances.py` | Static disturbance plots | `outputs/plots/` | Generate publication-ready plots |
| `plot_rl_results.py` | Static RL metrics plots | `outputs/plots/` | Analyze training performance |
| `visualize_disturbances.py` | Interactive disturbance viewer | Display window | Real-time disturbance exploration |
| `visualize_trajectories.py` | Interactive trajectory viewer | Display window | Trajectory path visualization |

---

## Plotting Tools

### 1. `plotting/plot_disturbances.py`
**Purpose**: Generate static plots of disturbance forces and torques applied during training.

**Features**:
- Time-series plots of force (Fx, Fy) and torque (τz)
- Comparison across disturbance types (random, periodic, continuous, impulse)
- Intensity level comparison (normal vs golden)
- Publication-quality figures

**Usage**:
```bash
cd visualization_tools/plotting
python plot_disturbances.py --scenario continuous --intensity normal
```

**Arguments**:
- `--scenario`: Disturbance type (none, random, periodic, continuous, impulse)
- `--intensity`: Intensity level (normal, golden)
- `--output`: Output directory (default: `../outputs/plots/`)
- `--format`: Output format (png, pdf, svg)

**Output**:
- `outputs/plots/disturbances_<scenario>_<intensity>.png`
- Force vs time plot
- Torque vs time plot
- Combined multi-panel figure

**Example Output**:
```
Force Profile - Continuous Disturbance (Normal Intensity)
- Fx: ±10N sinusoidal
- Fy: ±10N sinusoidal (90° phase shift)
- τz: ±5Nm random impulses
```

---

### 2. `plotting/plot_rl_results.py`
**Purpose**: Generate static plots of RL training metrics and performance analysis.

**Features**:
- Success rate over episodes
- Average error over episodes
- Reward curves
- Convergence analysis
- Algorithm comparison (DQN vs Q-Learning)
- Scenario comparison

**Usage**:
```bash
cd visualization_tools/plotting
python plot_rl_results.py --metrics ../../training_data/phase_03_algorithm_core/dqn_algorithm_core/session_data/metrics/rl_metrics_dqn.json
```

**Arguments**:
- `--metrics`: Path to metrics JSON file
- `--compare`: Path to second metrics file for comparison
- `--scenarios`: Specific scenarios to plot (default: all)
- `--output`: Output directory (default: `../outputs/plots/`)

**Output**:
- `outputs/plots/success_rate_over_episodes.png`
- `outputs/plots/error_over_episodes.png`
- `outputs/plots/reward_curves.png`
- `outputs/plots/algorithm_comparison.png`

**Supported Metrics**:
- Success rate (%)
- Average error (m)
- Episode reward
- Episode length
- Convergence episode
- Q-value statistics

---

## Interactive Visualization Tools

### 3. `interactive/visualize_disturbances.py`
**Purpose**: Interactive visualization of disturbance forces and torques with real-time exploration.

**Features**:
- Real-time disturbance generation preview
- Adjustable intensity sliders
- Multiple disturbance type comparison
- Time window controls
- Export capability

**Usage**:
```bash
cd visualization_tools/interactive
python visualize_disturbances.py
```

**Interactive Controls**:
- **Intensity Slider**: Adjust disturbance magnitude
- **Type Selector**: Switch between disturbance types
- **Time Window**: Zoom in/out on time axis
- **Pause/Play**: Control animation
- **Export**: Save current view as image

**Display**:
- Top panel: Force components (Fx, Fy)
- Bottom panel: Torque component (τz)
- Side panel: Configuration controls

---

### 4. `interactive/visualize_trajectories.py`
**Purpose**: Interactive 3D visualization of robot trajectories and waypoints.

**Features**:
- 3D trajectory path visualization
- Waypoint markers
- Goal position indicators
- Trajectory comparison (planned vs actual)
- Rotation controls

**Usage**:
```bash
cd visualization_tools/interactive
python visualize_trajectories.py --trajectory circular --radius 0.3
```

**Arguments**:
- `--trajectory`: Trajectory type (circular, square, lemniscate, custom)
- `--radius`: Trajectory radius (for circular)
- `--waypoints`: Number of waypoints
- `--actual`: Path to actual trajectory data

**Interactive Controls**:
- **Mouse Drag**: Rotate 3D view
- **Scroll**: Zoom in/out
- **Arrow Keys**: Pan view
- **Space**: Reset view
- **'s'**: Save screenshot

**Display**:
- Blue line: Planned trajectory
- Red line: Actual trajectory (if provided)
- Green markers: Waypoints
- Yellow marker: Goal position

---

## Output Management

### Directory Organization

#### `outputs/plots/`
**Purpose**: Static plot images for publications and reports

**Contents**:
- PNG files (300 DPI for publications)
- PDF files (vector graphics for papers)
- SVG files (editable graphics)

**Naming Convention**:
- `<metric>_<scenario>_<intensity>_<date>.png`
- Example: `success_rate_continuous_normal_20251102.png`

#### `outputs/videos/`
**Purpose**: Video recordings of simulations and training

**Contents**:
- MP4 files (simulation recordings)
- AVI files (high-quality captures)
- GIF files (animated summaries)

**Naming Convention**:
- `<type>_<scenario>_<episode>_<date>.mp4`
- Example: `training_continuous_ep1000_20251102.mp4`

#### `outputs/images/`
**Purpose**: Screenshots and diagrams

**Subdirectories**:
- `screenshots/`: Simulation snapshots
- `diagrams/`: System diagrams and schematics
- `results/`: Result images and comparisons

---

## Common Workflows

### Generate Publication Plots

```bash
cd visualization_tools/plotting

# 1. Plot all RL results
python plot_rl_results.py \
    --metrics ../../training_data/phase_03_algorithm_core/dqn_algorithm_core/session_data/metrics/rl_metrics_dqn.json \
    --output ../outputs/plots/ \
    --format pdf

# 2. Plot disturbances for each scenario
for scenario in none random periodic continuous impulse; do
    python plot_disturbances.py \
        --scenario $scenario \
        --intensity normal \
        --output ../outputs/plots/
done

# 3. Compare algorithms
python plot_rl_results.py \
    --metrics ../../training_data/phase_03_algorithm_core/dqn_algorithm_core/session_data/metrics/rl_metrics_dqn.json \
    --compare ../../training_data/phase_03_algorithm_core/qlearning_algorithm_core/session_data/metrics/rl_metrics_q-learning.json \
    --output ../outputs/plots/algorithm_comparison.png
```

### Interactive Exploration

```bash
cd visualization_tools/interactive

# 1. Explore disturbances
python visualize_disturbances.py

# 2. Visualize trajectory
python visualize_trajectories.py --trajectory circular --radius 0.3

# 3. Compare planned vs actual trajectory
python visualize_trajectories.py \
    --trajectory circular \
    --actual ../../training_data/phase_03_algorithm_core/dqn_algorithm_core/session_data/trajectories/episode_1000.json
```

### Batch Processing

```bash
# Generate all plots for a training session
cd visualization_tools/plotting

SESSION_DIR="../../training_data/phase_03_algorithm_core/dqn_algorithm_core/session_data"

# Plot all metrics
python plot_rl_results.py \
    --metrics ${SESSION_DIR}/metrics/rl_metrics_dqn.json \
    --output ../outputs/plots/ \
    --format png pdf

# Plot all scenarios
for scenario in continuous impulse none periodic random; do
    for intensity in normal golden; do
        python plot_disturbances.py \
            --scenario $scenario \
            --intensity $intensity \
            --output ../outputs/plots/
    done
done

echo "✅ All plots generated in outputs/plots/"
```

---

## Customization

### Matplotlib Style

All plotting tools use a consistent style defined in plot settings:

```python
# Custom plot style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams.update({
    'figure.figsize': (12, 8),
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'legend.fontsize': 12,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'lines.linewidth': 2,
    'grid.alpha': 0.3
})
```

### Color Schemes

**Disturbance Types**:
- None: Gray (#808080)
- Random: Blue (#1f77b4)
- Periodic: Orange (#ff7f0e)
- Continuous: Green (#2ca02c)
- Impulse: Red (#d62728)

**Intensity Levels**:
- Normal: Blue (#1f77b4)
- Golden: Gold (#FFD700)

**Algorithms**:
- DQN: Navy (#000080)
- Q-Learning: Teal (#008080)

---

## Dependencies

### Required Packages

```bash
# Core plotting
pip install matplotlib>=3.5.0
pip install numpy>=1.21.0
pip install pandas>=1.3.0

# Interactive visualization
pip install matplotlib
pip install mpl_toolkits

# Data processing
pip install json
pip install scipy
```

### Installation

```bash
# Install all dependencies
conda activate pybullet_env
pip install -r requirements_viz.txt
```

---

## Troubleshooting

### Plot Not Displaying

**Issue**: Plots generated but not showing  
**Solution**:
```bash
# Add to script
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg'
```

### Out of Memory for Large Datasets

**Issue**: Memory error when plotting 10,000+ episodes  
**Solution**:
```python
# Subsample data
episodes = episodes[::10]  # Every 10th episode
```

### Font Rendering Issues

**Issue**: Fonts not displaying correctly  
**Solution**:
```bash
# Rebuild font cache
rm ~/.cache/matplotlib -rf
python -c "import matplotlib.pyplot as plt; plt.plot([1,2,3]); plt.savefig('test.png')"
```

### Interactive Window Not Responding

**Issue**: Interactive visualization freezes  
**Solution**:
```python
# Add in interactive tools
plt.ion()  # Enable interactive mode
```

---

## Integration with Training Pipeline

### Automatic Visualization During Training

```python
# In sim_husky_kuka.py
if episode % 100 == 0:
    # Generate progress plots
    os.system('python visualization_tools/plotting/plot_rl_results.py \
               --metrics rl_metrics_dqn.json \
               --output visualization_tools/outputs/plots/')
```

### Post-Training Analysis

```bash
# After training completes
cd visualization_tools/plotting

# Generate all analysis plots
python plot_rl_results.py \
    --metrics ../../training_data/phase_03_algorithm_core/dqn_algorithm_core/session_data/metrics/rl_metrics_dqn.json \
    --output ../outputs/plots/ \
    --format png pdf svg
```

---

## Related Documentation

- **Training Data**: `/home/marcoreis/robust_mm_control_ws/training_data/`
- **Analysis Scripts**: `/home/marcoreis/robust_mm_control_ws/test_scripts/analysis_scripts/`
- **Diagnostic Tools**: `/home/marcoreis/robust_mm_control_ws/tools/diagnostics/`
- **Main README**: `/home/marcoreis/robust_mm_control_ws/README.md`

---

**Last Updated**: November 2, 2025  
**Workspace**: `/home/marcoreis/robust_mm_control_ws/visualization_tools`  
**Status**: Reorganized and Documented ✅
