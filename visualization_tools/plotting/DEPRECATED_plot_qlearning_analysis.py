#!/usr/bin/env python3
"""
Q-Learning Training Analysis
Generates visualizations for Q-Learning performance with training status warnings
Matches findings in QLEARNING_DETAILED_ANALYSIS.md
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path
from datetime import datetime

# Set style
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        pass  # Use default style
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
METRICS_PATH = BASE_DIR / 'training_data/phase_03_algorithm_core/qlearning_algorithm_core/session_data/metrics/rl_metrics_q-learning.json'
OUTPUT_DIR = BASE_DIR / 'training_data/phase_03_algorithm_core/algorithm_analysis/plots'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("="*70)
print("Q-Learning Training Analysis")
print("="*70)

# Load metrics
print(f"\nLoading Q-Learning metrics from: {METRICS_PATH}")
with open(METRICS_PATH, 'r') as f:
    ql_metrics = json.load(f)

print(f"⚠️  WARNING: Only {len(ql_metrics)} scenario(s) trained (expected 10)")
print(f"Available data: {list(ql_metrics.keys())}")

# =============================================================================
# FIGURE 1: Q-Learning Training Progress (none/normal scenario only)
# =============================================================================
print("\n📊 Creating Q-Learning Training Progress...")

fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

# Get none_normal data
if 'none_normal' in ql_metrics:
    data = ql_metrics['none_normal']
    episodes = list(range(1, len(data['errors']) + 1))
    
    # Panel 1: Error progression
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(episodes, data['errors'], 'o-', color='#e74c3c', linewidth=2, 
             markersize=6, markeredgecolor='black', markeredgewidth=0.5, label='Error per episode')
    
    # Add trend line
    z = np.polyfit(episodes, data['errors'], 1)
    p = np.poly1d(z)
    ax1.plot(episodes, p(episodes), "--", color='blue', linewidth=2, alpha=0.7, label=f'Trend (slope={z[0]:.5f})')
    
    # Add mean line
    mean_error = np.mean(data['errors'])
    ax1.axhline(mean_error, color='green', linestyle='--', linewidth=2, label=f'Mean: {mean_error:.3f}m')
    
    ax1.set_xlabel('Episode', fontweight='bold')
    ax1.set_ylabel('Final Error (meters)', fontweight='bold')
    ax1.set_title('Q-Learning Error Progression\nNone/Normal Scenario (10 Episodes)',
                  fontsize=12, fontweight='bold', pad=10)
    ax1.legend(framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim(0, len(episodes) + 1)
    
    # Add value labels on points
    for i, (ep, err) in enumerate(zip(episodes, data['errors'])):
        if i % 2 == 0:  # Label every other point to avoid crowding
            ax1.text(ep, err + 0.001, f'{err:.3f}', ha='center', fontsize=7, 
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))
    
    # Panel 2: Energy consumption
    ax2 = fig.add_subplot(gs[0, 1])
    colors = ['green' if e < 20 else 'orange' if e < 50 else 'red' for e in data['energy']]
    bars = ax2.bar(episodes, data['energy'], color=colors, alpha=0.7, 
                   edgecolor='black', linewidth=0.5)
    
    # Add value labels on bars
    for bar, energy in zip(bars, data['energy']):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{int(energy)}',
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    mean_energy = np.mean(data['energy'])
    median_energy = np.median(data['energy'])
    ax2.axhline(mean_energy, color='blue', linestyle='--', linewidth=2, 
                label=f'Mean: {mean_energy:.1f}')
    ax2.axhline(median_energy, color='purple', linestyle=':', linewidth=2, 
                label=f'Median: {median_energy:.1f}')
    
    # Highlight outlier
    max_energy_idx = np.argmax(data['energy'])
    ax2.annotate('⚠️ Outlier', xy=(max_energy_idx + 1, data['energy'][max_energy_idx]),
                xytext=(max_energy_idx + 1, data['energy'][max_energy_idx] + 15),
                fontsize=10, fontweight='bold', color='red',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->', color='red', lw=2))
    
    ax2.set_xlabel('Episode', fontweight='bold')
    ax2.set_ylabel('Energy Consumption (units)', fontweight='bold')
    ax2.set_title('Q-Learning Energy Efficiency\nHigh Variance with Outlier (Episode 7)',
                  fontsize=12, fontweight='bold', pad=10)
    ax2.legend(framealpha=0.9)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_xlim(0, len(episodes) + 1)
    
    # Panel 3: Cumulative statistics
    ax3 = fig.add_subplot(gs[1, 0])
    
    # Running statistics
    running_mean_error = [np.mean(data['errors'][:i+1]) for i in range(len(data['errors']))]
    running_std_error = [np.std(data['errors'][:i+1]) for i in range(len(data['errors']))]
    
    ax3.plot(episodes, running_mean_error, 'o-', color='#3498db', linewidth=2, 
             markersize=6, label='Running mean error')
    ax3.fill_between(episodes, 
                     np.array(running_mean_error) - np.array(running_std_error),
                     np.array(running_mean_error) + np.array(running_std_error),
                     alpha=0.3, color='#3498db', label='±1 std dev')
    
    ax3.set_xlabel('Episode', fontweight='bold')
    ax3.set_ylabel('Error (meters)', fontweight='bold')
    ax3.set_title('Q-Learning Convergence Analysis\nRunning Mean with Standard Deviation',
                  fontsize=12, fontweight='bold', pad=10)
    ax3.legend(framealpha=0.9)
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.set_xlim(0, len(episodes) + 1)
    
    # Panel 4: Performance summary box
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis('off')
    ax4.set_title('Q-Learning Performance Summary\nNone/Normal Scenario Only',
                  fontsize=12, fontweight='bold', pad=20)
    
    # Calculate statistics
    stats = [
        ['Metric', 'Value', 'Status'],
        ['─'*20, '─'*15, '─'*10],
        ['Episodes Trained', f'{data["episodes"]}', '⚠️ Limited'],
        ['Success Rate', '100%', '✅ Perfect'],
        ['Mean Error', f'{mean_error:.3f}m', '✅ Excellent'],
        ['Std Error', f'{np.std(data["errors"]):.4f}m', '✅ Very Low'],
        ['Best Error', f'{min(data["errors"]):.3f}m', '⭐ Best'],
        ['Worst Error', f'{max(data["errors"]):.3f}m', '✅ Good'],
        ['Mean Energy', f'{mean_energy:.1f} units', '⭐⭐⭐⭐⭐'],
        ['Energy Std Dev', f'{np.std(data["energy"]):.1f} units', '⚠️ High'],
        ['Energy Range', f'{min(data["energy"])}-{max(data["energy"])} units', '⚠️ Variable'],
        ['─'*20, '─'*15, '─'*10],
        ['Training Status', '1/10 scenarios', '❌ Incomplete'],
    ]
    
    table = ax4.table(cellText=stats, cellLoc='left', loc='center',
                      colWidths=[0.45, 0.3, 0.25])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.2)
    
    # Style header
    for i in range(3):
        table[(0, i)].set_facecolor('#e74c3c')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Color rows
    for i in range(2, len(stats)):
        for j in range(3):
            if i == len(stats) - 1:  # Last row (incomplete status)
                table[(i, j)].set_facecolor('#fadbd8')
            else:
                table[(i, j)].set_facecolor('#ecf0f1' if i % 2 == 0 else 'white')

# Add warning banner
fig.text(0.5, 0.95, '⚠️ LIMITED DATA: Only 1 of 10 scenarios trained (10% complete)',
         ha='center', fontsize=12, fontweight='bold', color='red',
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8, pad=0.7))

fig.suptitle('Q-Learning Training Analysis - None/Normal Scenario\n' +
             'Preliminary Results from Limited Training',
             fontsize=14, fontweight='bold', y=0.92)

plt.savefig(OUTPUT_DIR / 'qlearning_training_progress.png', bbox_inches='tight', dpi=300)
print(f"✅ Saved: qlearning_training_progress.png")
plt.close()

# =============================================================================
# FIGURE 2: Training Status and Comparison Need
# =============================================================================
print("\n📊 Creating Training Status Visualization...")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Panel 1: Training completion status
ax1.set_title('Q-Learning Training Completion Status\n10% Complete - 9 Scenarios Remaining',
              fontsize=12, fontweight='bold', pad=10)

scenarios = ['None\nNormal', 'None\nGolden', 'Random\nNormal', 'Random\nGolden',
             'Periodic\nNormal', 'Periodic\nGolden', 'Continuous\nNormal', 
             'Continuous\nGolden', 'Impulse\nNormal', 'Impulse\nGolden']
status = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 1 = complete, 0 = not trained
colors_status = ['#2ecc71' if s == 1 else '#e74c3c' for s in status]

bars = ax1.barh(scenarios, [1]*len(scenarios), color=colors_status, alpha=0.7,
                edgecolor='black', linewidth=1)

# Add status labels
for i, (bar, s) in enumerate(zip(bars, status)):
    label = '✅ COMPLETE' if s == 1 else '❌ NOT TRAINED'
    color = 'white' if s == 1 else 'yellow'
    ax1.text(0.5, i, label, ha='center', va='center', 
             fontweight='bold', fontsize=9, color='black',
             bbox=dict(boxstyle='round', facecolor=color, alpha=0.9))

ax1.set_xlim(0, 1)
ax1.set_xticks([])
ax1.set_xlabel('Training Status', fontweight='bold')
ax1.grid(axis='x', alpha=0.3, linestyle='--')

# Add completion percentage
completion = sum(status) / len(status) * 100
ax1.text(0.5, -1.5, f'Overall Completion: {completion:.0f}%', 
         ha='center', fontsize=14, fontweight='bold',
         bbox=dict(boxstyle='round', facecolor='red', alpha=0.7, pad=0.8),
         color='white')

# Panel 2: What's missing - scenario breakdown
ax2.set_title('Missing Training Data\nScenarios Needing Completion',
              fontsize=12, fontweight='bold', pad=10)

missing_scenarios = ['None/Golden', 'Random/Normal', 'Random/Golden',
                    'Periodic/Normal', 'Periodic/Golden', 'Continuous/Normal',
                    'Continuous/Golden', 'Impulse/Normal', 'Impulse/Golden']
importance = [4, 5, 5, 5, 5, 5, 5, 5, 5]  # Importance rating

colors_importance = plt.cm.Reds(np.array(importance) / 5)
bars = ax2.barh(missing_scenarios, importance, color=colors_importance, 
                edgecolor='black', linewidth=0.5)

# Add labels
for bar, imp in zip(bars, importance):
    ax2.text(imp + 0.2, bar.get_y() + bar.get_height()/2,
            f'Priority: {imp}/5', va='center', fontweight='bold', fontsize=9)

ax2.set_xlabel('Priority Level', fontweight='bold')
ax2.set_xlim(0, 6)
ax2.grid(axis='x', alpha=0.3, linestyle='--')

# Panel 3: Estimated training time
ax3.set_title('Training Time Estimation\nFor Complete Coverage',
              fontsize=12, fontweight='bold', pad=10)

training_estimates = {
    'Current (1 scenario)': 0.33,
    'Remaining (9 scenarios)': 3.0,
    'Total (10 scenarios)': 3.33
}

colors_time = ['#2ecc71', '#f39c12', '#3498db']
bars = ax3.bar(training_estimates.keys(), training_estimates.values(), 
               color=colors_time, alpha=0.7, edgecolor='black', linewidth=1)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
            f'{height:.1f}h',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

ax3.set_ylabel('Estimated Time (hours)', fontweight='bold')
ax3.set_ylim(0, max(training_estimates.values()) * 1.3)
ax3.grid(axis='y', alpha=0.3, linestyle='--')

# Add note
ax3.text(0.5, -0.5, '⚠️ Based on ~20 minutes per scenario with 2000 episodes',
         ha='center', fontsize=9, style='italic',
         transform=ax3.transData, bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# Panel 4: Recommendations
ax4.axis('off')
ax4.set_title('Recommendations for Complete Analysis',
              fontsize=12, fontweight='bold', pad=20)

recommendations = [
    ['Priority', 'Action', 'Impact'],
    ['─'*8, '─'*30, '─'*15],
    ['🔴 HIGH', 'Complete all 9 remaining scenarios', 'Enable full comparison'],
    ['🟠 HIGH', 'Train 2000 episodes per scenario', 'Ensure convergence'],
    ['🟡 MED', 'Collect epsilon decay data', 'Analyze exploration'],
    ['🟡 MED', 'Track loss values', 'Monitor learning'],
    ['🟢 LOW', 'Generate learning curves', 'Visualize progress'],
    ['🟢 LOW', 'Compare with DQN fully', 'Scientific validation'],
]

table = ax4.table(cellText=recommendations, cellLoc='left', loc='center',
                  colWidths=[0.15, 0.6, 0.25])
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2.5)

# Style
for i in range(3):
    table[(0, i)].set_facecolor('#e74c3c')
    table[(0, i)].set_text_props(weight='bold', color='white')

for i in range(2, len(recommendations)):
    for j in range(3):
        table[(i, j)].set_facecolor('#ecf0f1' if i % 2 == 0 else 'white')

fig.suptitle('Q-Learning Training Status - Incomplete Coverage Analysis\n' +
             'Comprehensive Training Required for Full Algorithm Comparison',
             fontsize=14, fontweight='bold', y=0.98)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'qlearning_training_status.png', bbox_inches='tight', dpi=300)
print(f"✅ Saved: qlearning_training_status.png")
plt.close()

print("\n" + "="*70)
print("✅ Q-Learning visualizations generated successfully!")
print(f"📁 Output directory: {OUTPUT_DIR}")
print("="*70)
print("\nGenerated files:")
print("  1. qlearning_training_progress.png - Episode-by-episode analysis")
print("  2. qlearning_training_status.png - Training completion status")
print("\n⚠️  Note: Limited visualizations due to incomplete training (1/10 scenarios)")
print("    Complete remaining scenarios for comprehensive analysis")
print("="*70)
