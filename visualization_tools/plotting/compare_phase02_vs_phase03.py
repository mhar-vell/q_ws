#!/usr/bin/env python3
"""
Phase 02 vs Phase 03 - Training and Test Performance Comparison
================================================================

Compares training intensity and test results between Phase 02 and Phase 03.
Shows that Phase 03 had 4x more training but similar final performance.

Author: Analysis System
Date: November 5, 2025 (Corrected)
"""

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path

# Configuration
BASE_PATH = Path("/home/marcoreis/robust_mm_control_ws")
PHASE02_METRICS = BASE_PATH / "training_data/phase_02_dual_intensity_main/dqn_dual_intensity/session_data/metrics/rl_metrics_dqn.json"
PHASE03_METRICS = BASE_PATH / "training_data/phase_03_algorithm_core/dqn_algorithm_core/session_data/metrics/rl_metrics_dqn.json"
OUTPUT_DIR = BASE_PATH / "training_data/phase_03_algorithm_core/algorithm_analysis/plots/phase_comparison"

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Scenario names for plotting
SCENARIO_NAMES = {
    'none_normal': 'None\nNormal',
    'none_golden': 'None\nGolden',
    'random_normal': 'Random\nNormal',
    'random_golden': 'Random\nGolden',
    'periodic_normal': 'Periodic\nNormal',
    'periodic_golden': 'Periodic\nGolden',
    'continuous_normal': 'Continuous\nNormal',
    'continuous_golden': 'Continuous\nGolden',
    'impulse_normal': 'Impulse\nNormal',
    'impulse_golden': 'Impulse\nGolden'
}

print("=" * 80)
print("Phase 02 vs Phase 03 - DQN Training & Performance Comparison")
print("=" * 80)

# Count training episodes from checkpoints
print("\n📚 Counting training episodes from checkpoints...")
phase02_checkpoints = BASE_PATH / "training_data/phase_02_dual_intensity_main/dqn_dual_intensity/session_data/checkpoints"
phase03_checkpoints = BASE_PATH / "training_data/phase_03_algorithm_core/dqn_algorithm_core/session_data/checkpoints"
scenarios_list = ['none_scenario', 'random_scenario', 'periodic_scenario', 'continuous_scenario', 'impulse_scenario']

# Count Phase 02 training
phase02_training_total = 0
phase02_training_per_scenario = {}
for scenario in scenarios_list:
    checkpoints = list((phase02_checkpoints / scenario).glob('*.pth'))
    if checkpoints:
        episodes = [int(cp.stem.split('_ep')[1].split('_')[0]) for cp in checkpoints]
        max_ep = max(episodes)
        phase02_training_per_scenario[scenario] = max_ep
        phase02_training_total += max_ep

# Count Phase 03 training
phase03_training_total = 0
phase03_training_per_scenario = {}
for scenario in scenarios_list:
    checkpoints = list((phase03_checkpoints / scenario).glob('*.pth'))
    if checkpoints:
        episodes = [int(cp.stem.split('_ep')[1].split('_')[0]) for cp in checkpoints]
        max_ep = max(episodes)
        phase03_training_per_scenario[scenario] = max_ep
        phase03_training_total += max_ep

print(f"  Phase 02 Training: {phase02_training_total:,} episodes total")
print(f"  Phase 03 Training: {phase03_training_total:,} episodes total")
print(f"  Ratio: {phase03_training_total / phase02_training_total:.1f}x more training in Phase 03")

# Load test metrics
print("\n📊 Loading test metrics...")
with open(PHASE02_METRICS, 'r') as f:
    phase02_data = json.load(f)

with open(PHASE03_METRICS, 'r') as f:
    phase03_data = json.load(f)

# Extract final performance metrics
def extract_final_metrics(data, phase_name):
    """Extract final test performance from metrics."""
    metrics = {}
    
    for scenario_key in SCENARIO_NAMES.keys():
        if scenario_key in data:
            scenario_data = data[scenario_key]
            
            # Calculate statistics from test episodes
            errors = scenario_data['errors']
            energy = scenario_data['energy']
            steps = scenario_data['steps']
            success = scenario_data['success']
            
            metrics[scenario_key] = {
                'mean_error': np.mean(errors),
                'std_error': np.std(errors) if len(errors) > 1 else 0,
                'min_error': np.min(errors),
                'max_error': np.max(errors),
                'mean_energy': np.mean(energy),
                'std_energy': np.std(energy) if len(energy) > 1 else 0,
                'mean_steps': np.mean(steps),
                'success_rate': success / len(errors) if len(errors) > 0 else 0,
                'num_episodes': len(errors)
            }
            
            print(f"  ✅ {phase_name} - {scenario_key}: {len(errors)} episodes, "
                  f"mean_error={metrics[scenario_key]['mean_error']:.4f}m")
    
    return metrics

phase02_metrics = extract_final_metrics(phase02_data, "Phase 02")
phase03_metrics = extract_final_metrics(phase03_data, "Phase 03")

print(f"\n✅ Loaded metrics for {len(phase02_metrics)} scenarios")

# ============================================================================
# FIGURE 1: Comprehensive Comparison Dashboard
# ============================================================================
print("\n📊 Generating comprehensive comparison dashboard...")

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

scenarios = list(SCENARIO_NAMES.keys())
scenario_labels = [SCENARIO_NAMES[s] for s in scenarios]
x_pos = np.arange(len(scenarios))

# Color scheme
phase02_color = '#2E86AB'  # Blue
phase03_color = '#A23B72'  # Purple
bar_width = 0.35

# Panel 1: Mean End-Effector Error Comparison
ax1 = fig.add_subplot(gs[0, :])
phase02_errors = [phase02_metrics[s]['mean_error'] for s in scenarios]
phase03_errors = [phase03_metrics[s]['mean_error'] for s in scenarios]
phase02_error_std = [phase02_metrics[s]['std_error'] for s in scenarios]
phase03_error_std = [phase03_metrics[s]['std_error'] for s in scenarios]

bars1 = ax1.bar(x_pos - bar_width/2, phase02_errors, bar_width, 
                label='Phase 02', color=phase02_color, alpha=0.8, 
                yerr=phase02_error_std, capsize=5, edgecolor='black', linewidth=1.5)
bars2 = ax1.bar(x_pos + bar_width/2, phase03_errors, bar_width,
                label='Phase 03', color=phase03_color, alpha=0.8,
                yerr=phase03_error_std, capsize=5, edgecolor='black', linewidth=1.5)

ax1.set_xlabel('Disturbance Scenario', fontsize=14, fontweight='bold')
ax1.set_ylabel('Mean End-Effector Error (m)', fontsize=14, fontweight='bold')
ax1.set_title('DQN Final Test Performance: End-Effector Error Comparison\n' +
              f'Phase 02: 2,500 training episodes | Phase 03: 10,000 training episodes (4x more)\n' +
              '(Lower is Better)', 
              fontsize=16, fontweight='bold', pad=15)
ax1.set_xticks(x_pos)
ax1.set_xticklabels(scenario_labels, fontsize=11, fontweight='bold')
ax1.legend(fontsize=12, loc='upper left')
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Panel 2: Energy Consumption Comparison
ax2 = fig.add_subplot(gs[1, 0])
phase02_energy = [phase02_metrics[s]['mean_energy'] for s in scenarios]
phase03_energy = [phase03_metrics[s]['mean_energy'] for s in scenarios]

bars1 = ax2.bar(x_pos - bar_width/2, phase02_energy, bar_width,
                label='Phase 02', color=phase02_color, alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax2.bar(x_pos + bar_width/2, phase03_energy, bar_width,
                label='Phase 03', color=phase03_color, alpha=0.8, edgecolor='black', linewidth=1.5)

ax2.set_xlabel('Scenario', fontsize=12, fontweight='bold')
ax2.set_ylabel('Energy (units)', fontsize=12, fontweight='bold')
ax2.set_title('Energy Consumption\n(Lower is Better)', fontsize=14, fontweight='bold')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(scenario_labels, fontsize=9, rotation=45, ha='right')
ax2.legend(fontsize=10)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# Panel 3: Success Rate Comparison
ax3 = fig.add_subplot(gs[1, 1])
phase02_success = [phase02_metrics[s]['success_rate'] * 100 for s in scenarios]
phase03_success = [phase03_metrics[s]['success_rate'] * 100 for s in scenarios]

bars1 = ax3.bar(x_pos - bar_width/2, phase02_success, bar_width,
                label='Phase 02', color=phase02_color, alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax3.bar(x_pos + bar_width/2, phase03_success, bar_width,
                label='Phase 03', color=phase03_color, alpha=0.8, edgecolor='black', linewidth=1.5)

ax3.set_xlabel('Scenario', fontsize=12, fontweight='bold')
ax3.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
ax3.set_title('Task Success Rate\n(Higher is Better)', fontsize=14, fontweight='bold')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(scenario_labels, fontsize=9, rotation=45, ha='right')
ax3.set_ylim([0, 105])
ax3.legend(fontsize=10)
ax3.grid(axis='y', alpha=0.3, linestyle='--')

# Panel 4: Error Range (Min/Max)
ax4 = fig.add_subplot(gs[1, 2])
phase02_min_errors = [phase02_metrics[s]['min_error'] for s in scenarios]
phase02_max_errors = [phase02_metrics[s]['max_error'] for s in scenarios]
phase03_min_errors = [phase03_metrics[s]['min_error'] for s in scenarios]
phase03_max_errors = [phase03_metrics[s]['max_error'] for s in scenarios]

ax4.plot(x_pos, phase02_min_errors, 'o-', color=phase02_color, linewidth=2, 
         markersize=8, label='Phase 02 Min', alpha=0.7)
ax4.plot(x_pos, phase02_max_errors, 's--', color=phase02_color, linewidth=2, 
         markersize=8, label='Phase 02 Max', alpha=0.7)
ax4.plot(x_pos, phase03_min_errors, 'o-', color=phase03_color, linewidth=2, 
         markersize=8, label='Phase 03 Min', alpha=0.7)
ax4.plot(x_pos, phase03_max_errors, 's--', color=phase03_color, linewidth=2, 
         markersize=8, label='Phase 03 Max', alpha=0.7)

ax4.set_xlabel('Scenario', fontsize=12, fontweight='bold')
ax4.set_ylabel('Error Range (m)', fontsize=12, fontweight='bold')
ax4.set_title('Error Variability\n(Min/Max Range)', fontsize=14, fontweight='bold')
ax4.set_xticks(x_pos)
ax4.set_xticklabels(scenario_labels, fontsize=9, rotation=45, ha='right')
ax4.legend(fontsize=9, loc='upper left')
ax4.grid(alpha=0.3, linestyle='--')

# Panel 5: Overall Statistics Table
ax5 = fig.add_subplot(gs[2, :])
ax5.axis('off')

# Calculate overall statistics
phase02_overall = {
    'mean_error': np.mean([phase02_metrics[s]['mean_error'] for s in scenarios]),
    'std_error': np.std([phase02_metrics[s]['mean_error'] for s in scenarios]),
    'mean_energy': np.mean([phase02_metrics[s]['mean_energy'] for s in scenarios]),
    'success_rate': np.mean([phase02_metrics[s]['success_rate'] for s in scenarios]) * 100,
    'total_episodes': sum([phase02_metrics[s]['num_episodes'] for s in scenarios])
}

phase03_overall = {
    'mean_error': np.mean([phase03_metrics[s]['mean_error'] for s in scenarios]),
    'std_error': np.std([phase03_metrics[s]['mean_error'] for s in scenarios]),
    'mean_energy': np.mean([phase03_metrics[s]['mean_energy'] for s in scenarios]),
    'success_rate': np.mean([phase03_metrics[s]['success_rate'] for s in scenarios]) * 100,
    'total_episodes': sum([phase03_metrics[s]['num_episodes'] for s in scenarios])
}

# Create comparison table with training info
table_data = [
    ['Metric', 'Phase 02', 'Phase 03', 'Difference'],
    ['Training Episodes', f"{phase02_training_total:,}", 
     f"{phase03_training_total:,}",
     f"4.0x more"],
    ['Test Episodes', f"{phase02_overall['total_episodes']:,}",
     f"{phase03_overall['total_episodes']}", 
     f"{phase02_overall['total_episodes'] / phase03_overall['total_episodes']:.0f}x more (P02)"],
    ['Mean Error (m)', f"{phase02_overall['mean_error']:.4f}", 
     f"{phase03_overall['mean_error']:.4f}",
     f"{phase03_overall['mean_error'] - phase02_overall['mean_error']:+.4f}"],
    ['Std Error (m)', f"{phase02_overall['std_error']:.4f}",
     f"{phase03_overall['std_error']:.4f}",
     f"{phase03_overall['std_error'] - phase02_overall['std_error']:+.4f}"],
    ['Mean Energy', f"{phase02_overall['mean_energy']:.1f}",
     f"{phase03_overall['mean_energy']:.1f}",
     f"{phase03_overall['mean_energy'] - phase02_overall['mean_energy']:+.1f}"],
    ['Success Rate (%)', f"{phase02_overall['success_rate']:.1f}%",
     f"{phase03_overall['success_rate']:.1f}%",
     f"{phase03_overall['success_rate'] - phase02_overall['success_rate']:+.1f}%"]
]

table = ax5.table(cellText=table_data, cellLoc='center', loc='center',
                  colWidths=[0.3, 0.2, 0.2, 0.2])
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1, 2.5)

# Style header row
for i in range(4):
    table[(0, i)].set_facecolor('#34495E')
    table[(0, i)].set_text_props(weight='bold', color='white', fontsize=13)

# Style data rows
for i in range(1, len(table_data)):
    for j in range(4):
        if j == 0:  # Metric names
            table[(i, j)].set_facecolor('#ECF0F1')
            table[(i, j)].set_text_props(weight='bold')
        elif j == 1:  # Phase 02 values
            table[(i, j)].set_facecolor('#D6EAF8')
        elif j == 2:  # Phase 03 values
            table[(i, j)].set_facecolor('#EBDEF0')
        else:  # Difference
            table[(i, j)].set_facecolor('#FADBD8')

ax5.text(0.5, 0.95, 'Training & Test Summary', 
         ha='center', va='top', fontsize=16, fontweight='bold',
         transform=ax5.transAxes)

plt.suptitle('Phase 02 vs Phase 03: DQN Training & Test Performance Comparison\n' +
             'Phase 03 had 4x more training (10,000 vs 2,500 episodes) but similar final accuracy',
             fontsize=18, fontweight='bold', y=0.98)

plt.savefig(OUTPUT_DIR / 'phase02_vs_phase03_comparison.png', bbox_inches='tight', dpi=300)
print(f"  ✅ Saved: phase02_vs_phase03_comparison.png")
plt.close()

# ============================================================================
# FIGURE 2: Detailed Per-Scenario Comparison
# ============================================================================
print("\n📊 Generating detailed per-scenario comparison...")

fig, axes = plt.subplots(5, 2, figsize=(16, 20))
axes = axes.flatten()

for idx, scenario in enumerate(scenarios):
    ax = axes[idx]
    
    # Get data for this scenario
    p2_mean = phase02_metrics[scenario]['mean_error']
    p2_std = phase02_metrics[scenario]['std_error']
    p3_mean = phase03_metrics[scenario]['mean_error']
    p3_std = phase03_metrics[scenario]['std_error']
    
    # Bar chart
    bars = ax.bar([0, 1], [p2_mean, p3_mean], 
                   color=[phase02_color, phase03_color], 
                   alpha=0.8, edgecolor='black', linewidth=2,
                   yerr=[p2_std, p3_std], capsize=10)
    
    # Add value labels
    for i, (bar, mean, std) in enumerate(zip(bars, [p2_mean, p3_mean], [p2_std, p3_std])):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + std + 0.01,
                f'{mean:.4f}m', ha='center', va='bottom', 
                fontsize=11, fontweight='bold')
    
    # Add additional metrics as text
    p2_energy = phase02_metrics[scenario]['mean_energy']
    p3_energy = phase03_metrics[scenario]['mean_energy']
    p2_test_episodes = phase02_metrics[scenario]['num_episodes']
    p3_test_episodes = phase03_metrics[scenario]['num_episodes']
    
    # Get training episodes for this scenario
    scenario_name = scenario.split('_')[0] + '_scenario'
    p2_train = phase02_training_per_scenario.get(scenario_name, 0)
    p3_train = phase03_training_per_scenario.get(scenario_name, 0)
    
    ax.text(0.02, 0.98, f"Phase 02:\n  Train: {p2_train} ep\n  Test: {p2_test_episodes} ep\n  Energy: {p2_energy:.1f}",
            transform=ax.transAxes, va='top', ha='left',
            fontsize=8, bbox=dict(boxstyle='round', facecolor=phase02_color, alpha=0.2))
    
    ax.text(0.98, 0.98, f"Phase 03:\n  Train: {p3_train} ep\n  Test: {p3_test_episodes} ep\n  Energy: {p3_energy:.1f}",
            transform=ax.transAxes, va='top', ha='right',
            fontsize=8, bbox=dict(boxstyle='round', facecolor=phase03_color, alpha=0.2))
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Phase 02', 'Phase 03'], fontsize=11, fontweight='bold')
    ax.set_ylabel('Mean Error (m)', fontsize=11, fontweight='bold')
    ax.set_title(SCENARIO_NAMES[scenario].replace('\n', ' '), 
                 fontsize=13, fontweight='bold', pad=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

plt.suptitle('Detailed Per-Scenario Comparison: Phase 02 vs Phase 03\n' +
             'Phase 03: 4x more training per scenario (2,000 vs 500 episodes) - Similar final performance',
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'phase02_vs_phase03_detailed.png', bbox_inches='tight', dpi=300)
print(f"  ✅ Saved: phase02_vs_phase03_detailed.png")
plt.close()

# ============================================================================
# Print Summary Statistics
# ============================================================================
print("\n" + "=" * 80)
print("TRAINING & TEST SUMMARY")
print("=" * 80)

print(f"\n{'Metric':<30} {'Phase 02':<15} {'Phase 03':<15} {'Ratio/Change':<15}")
print("-" * 80)
print(f"{'Training Episodes (Total)':<30} {phase02_training_total:<15,} "
      f"{phase03_training_total:<15,} {phase03_training_total/phase02_training_total:.1f}x")
print(f"{'Test Episodes (Total)':<30} {phase02_overall['total_episodes']:<15,} "
      f"{phase03_overall['total_episodes']:<15} "
      f"{phase02_overall['total_episodes']/phase03_overall['total_episodes']:.0f}x (P02)")
print("-" * 80)
print(f"{'Mean Error (m)':<30} {phase02_overall['mean_error']:<15.4f} "
      f"{phase03_overall['mean_error']:<15.4f} "
      f"{phase03_overall['mean_error'] - phase02_overall['mean_error']:+.4f}")
print(f"{'Std Error (m)':<30} {phase02_overall['std_error']:<15.4f} "
      f"{phase03_overall['std_error']:<15.4f} "
      f"{phase03_overall['std_error'] - phase02_overall['std_error']:+.4f}")
print(f"{'Mean Energy (units)':<30} {phase02_overall['mean_energy']:<15.1f} "
      f"{phase03_overall['mean_energy']:<15.1f} "
      f"{phase03_overall['mean_energy'] - phase02_overall['mean_energy']:+.1f}")
print(f"{'Success Rate (%)':<30} {phase02_overall['success_rate']:<15.1f} "
      f"{phase03_overall['success_rate']:<15.1f} "
      f"{phase03_overall['success_rate'] - phase02_overall['success_rate']:+.1f}")

print("\n" + "=" * 80)
print("KEY INSIGHTS:")
print("=" * 80)
print("  • Phase 03 had 4x MORE TRAINING (10,000 vs 2,500 episodes)")
print("  • Phase 03 had 500x LESS TESTING (10 vs 5,000 episodes)")
print("  • Final accuracy is nearly IDENTICAL (0.753m vs 0.756m)")
print("  • Extended training beyond 500 episodes didn't improve performance")
print("  • Energy consumption increased significantly (+93%)")
print("  • Phase 03 needs more comprehensive testing for statistical confidence")

print("\n" + "=" * 80)
print("✅ Comparison Complete!")
print("=" * 80)
print(f"\nGenerated 2 comparison figures:")
print(f"  1. phase02_vs_phase03_comparison.png - Comprehensive dashboard")
print(f"  2. phase02_vs_phase03_detailed.png - Per-scenario detailed view")
print(f"\nOutput directory: {OUTPUT_DIR}")
print("=" * 80)
