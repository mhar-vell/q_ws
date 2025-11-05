#!/usr/bin/env python3
"""
Complete Q-Learning Analysis Visualizations
===========================================

Generates comprehensive visualizations for Q-Learning performance
across all 10 trained scenario-intensity combinations.

Uses extracted metrics from Q-table checkpoints.

Author: Analysis System
Date: November 3, 2025
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import json
from pathlib import Path

# Try to use seaborn style, fall back to default if not available
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('default')

# Configuration
BASE_PATH = Path("/home/marcoreis/robust_mm_control_ws")
METRICS_FILE = BASE_PATH / "training_data/phase_03_algorithm_core/qlearning_algorithm_core/session_data/metrics/rl_metrics_q-learning_extracted.json"
OUTPUT_DIR = BASE_PATH / "training_data/phase_03_algorithm_core/algorithm_analysis/plots"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_metrics():
    """Load extracted Q-Learning metrics."""
    with open(METRICS_FILE, 'r') as f:
        data = json.load(f)
    return data

def create_training_dashboard(metrics_data):
    """
    Create comprehensive training dashboard showing all scenarios.
    
    Panels:
    1. Mean Q-Values by Scenario
    2. Convergence Scores Comparison
    3. Q-table Size Growth
    4. Training Stability
    """
    print("📊 Creating Q-Learning Training Dashboard...")
    
    fig = plt.figure(figsize=(20, 12))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # Prepare data
    scenarios = []
    mean_q_values = []
    convergence_scores = []
    num_states = []
    stability_scores = []
    colors_by_intensity = []
    
    for key in sorted(metrics_data.keys()):
        m = metrics_data[key]
        if not m.get('training_complete'):
            continue
            
        scenarios.append(key)
        mean_q_values.append(m['summary']['mean_q_value'])
        convergence_scores.append(m['summary']['convergence_score'])
        num_states.append(m['summary']['num_states'])
        stability_scores.append(m['summary']['stability'])
        
        # Color code by intensity
        if 'golden' in key:
            colors_by_intensity.append('#FFD700')  # Gold
        else:
            colors_by_intensity.append('#4169E1')  # Royal Blue
    
    x_pos = np.arange(len(scenarios))
    
    # Panel 1: Mean Q-Values
    ax1 = fig.add_subplot(gs[0, 0])
    bars1 = ax1.bar(x_pos, mean_q_values, color=colors_by_intensity, alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Scenario-Intensity', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Mean Q-Value', fontsize=12, fontweight='bold')
    ax1.set_title('Mean Q-Values by Scenario (Last 5 Checkpoints)', fontsize=14, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(scenarios, rotation=45, ha='right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars1, mean_q_values)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.4f}',
                ha='center', va='bottom', fontsize=8)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#4169E1', label='Normal Intensity'),
                      Patch(facecolor='#FFD700', label='Golden Ratio Intensity')]
    ax1.legend(handles=legend_elements, loc='upper left')
    
    # Panel 2: Convergence Scores
    ax2 = fig.add_subplot(gs[0, 1])
    bars2 = ax2.bar(x_pos, convergence_scores, color=colors_by_intensity, alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Scenario-Intensity', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Convergence Score', fontsize=12, fontweight='bold')
    ax2.set_title('Training Convergence by Scenario', fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(scenarios, rotation=45, ha='right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([min(convergence_scores) * 0.95, max(convergence_scores) * 1.02])
    
    # Add value labels
    for bar, val in zip(bars2, convergence_scores):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.4f}',
                ha='center', va='bottom', fontsize=8)
    
    # Panel 3: Q-table Size
    ax3 = fig.add_subplot(gs[1, 0])
    bars3 = ax3.bar(x_pos, num_states, color=colors_by_intensity, alpha=0.7, edgecolor='black')
    ax3.set_xlabel('Scenario-Intensity', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Number of States', fontsize=12, fontweight='bold')
    ax3.set_title('Q-Table Size (Final)', fontsize=14, fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(scenarios, rotation=45, ha='right', fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars3, num_states):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:,}',
                ha='center', va='bottom', fontsize=8, rotation=90)
    
    # Panel 4: Training Stability
    ax4 = fig.add_subplot(gs[1, 1])
    bars4 = ax4.bar(x_pos, stability_scores, color=colors_by_intensity, alpha=0.7, edgecolor='black')
    ax4.set_xlabel('Scenario-Intensity', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Stability (Std Dev of Last 10 Checkpoints)', fontsize=12, fontweight='bold')
    ax4.set_title('Training Stability by Scenario', fontsize=14, fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(scenarios, rotation=45, ha='right', fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars4, stability_scores):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.6f}',
                ha='center', va='bottom', fontsize=8)
    
    # Add note: Lower stability = more stable
    ax4.text(0.98, 0.98, '⚠️ Lower values = More stable training',
             transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle('Q-Learning Training Dashboard - All Scenarios',
                 fontsize=16, fontweight='bold', y=0.995)
    
    output_file = OUTPUT_DIR / "qlearning_complete_training_dashboard.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_file.name}")

def create_convergence_analysis(metrics_data):
    """
    Create detailed convergence analysis showing training progression.
    
    Panels:
    1-4. Selected scenarios showing Q-value evolution
    5. Comparison of convergence trends
    6. State space growth comparison
    """
    print("📈 Creating Convergence Analysis...")
    
    fig = plt.figure(figsize=(20, 15))
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # Select representative scenarios for detailed plots
    selected_scenarios = ['none_normal', 'continuous_golden', 'impulse_normal', 'periodic_golden']
    
    for idx, scenario_key in enumerate(selected_scenarios):
        if scenario_key not in metrics_data:
            continue
            
        m = metrics_data[scenario_key]
        if not m.get('training_complete'):
            continue
        
        row = idx // 2
        col = idx % 2
        ax = fig.add_subplot(gs[row, col])
        
        episodes = m['training_progression']['episodes']
        mean_q_values = m['training_progression']['mean_q_values']
        
        # Plot Q-value evolution
        ax.plot(episodes, mean_q_values, 'o-', linewidth=2, markersize=4,
                label='Mean Q-value')
        
        # Fit trend line
        z = np.polyfit(episodes, mean_q_values, 2)  # Quadratic fit
        p = np.polyval(z, episodes)
        ax.plot(episodes, p, '--', linewidth=2, alpha=0.7, label='Trend (quadratic)')
        
        ax.set_xlabel('Episode', fontsize=11, fontweight='bold')
        ax.set_ylabel('Mean Q-Value', fontsize=11, fontweight='bold')
        ax.set_title(f'{scenario_key.replace("_", " ").title()}',
                    fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        # Add statistics box
        final_q = mean_q_values[-1]
        trend_slope = m['training_progression']['q_value_trend']
        stats_text = f'Final: {final_q:.6f}\nTrend: {trend_slope:.2e}/ep'
        ax.text(0.02, 0.98, stats_text,
                transform=ax.transAxes, fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Panel 5: Convergence comparison (all scenarios)
    ax5 = fig.add_subplot(gs[2, 0])
    
    for key in sorted(metrics_data.keys()):
        m = metrics_data[key]
        if not m.get('training_complete'):
            continue
        
        episodes = m['training_progression']['episodes']
        conv_scores = m['training_progression']['convergence_scores']
        
        linestyle = '-' if 'golden' in key else '--'
        ax5.plot(episodes, conv_scores, linestyle, linewidth=1.5,
                label=key, alpha=0.7)
    
    ax5.set_xlabel('Episode', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Convergence Score', fontsize=12, fontweight='bold')
    ax5.set_title('Convergence Score Evolution - All Scenarios',
                 fontsize=13, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    ax5.legend(loc='best', fontsize=8, ncol=2)
    
    # Panel 6: State space growth
    ax6 = fig.add_subplot(gs[2, 1])
    
    for key in sorted(metrics_data.keys()):
        m = metrics_data[key]
        if not m.get('training_complete'):
            continue
        
        episodes = m['training_progression']['episodes']
        num_states = m['training_progression']['num_states']
        
        linestyle = '-' if 'golden' in key else '--'
        ax6.plot(episodes, num_states, linestyle, linewidth=1.5,
                label=key, alpha=0.7)
    
    ax6.set_xlabel('Episode', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Number of States', fontsize=12, fontweight='bold')
    ax6.set_title('Q-Table State Space Growth',
                 fontsize=13, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    ax6.legend(loc='best', fontsize=8, ncol=2)
    
    plt.suptitle('Q-Learning Convergence Analysis - Training Progression',
                 fontsize=16, fontweight='bold', y=0.995)
    
    output_file = OUTPUT_DIR / "qlearning_complete_convergence_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_file.name}")

def create_scenario_comparison(metrics_data):
    """
    Create scenario-by-scenario comparison analysis.
    
    Panels:
    1. Normal vs Golden ratio comparison
    2. Scenario performance heatmap
    3. Distribution of Q-values
    4. Summary statistics table
    """
    print("📊 Creating Scenario Comparison...")
    
    fig = plt.figure(figsize=(20, 12))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # Separate data by intensity
    normal_data = {}
    golden_data = {}
    
    for key, m in metrics_data.items():
        if not m.get('training_complete'):
            continue
        
        scenario = m['scenario']
        if m['intensity'] == 'normal':
            normal_data[scenario] = m['summary']
        else:
            golden_data[scenario] = m['summary']
    
    scenarios_list = sorted(normal_data.keys())
    
    # Panel 1: Normal vs Golden Q-values
    ax1 = fig.add_subplot(gs[0, 0])
    
    x_pos = np.arange(len(scenarios_list))
    width = 0.35
    
    normal_q_vals = [normal_data[s]['mean_q_value'] for s in scenarios_list]
    golden_q_vals = [golden_data[s]['mean_q_value'] for s in scenarios_list]
    
    bars1 = ax1.bar(x_pos - width/2, normal_q_vals, width,
                    label='Normal', color='#4169E1', alpha=0.7, edgecolor='black')
    bars2 = ax1.bar(x_pos + width/2, golden_q_vals, width,
                    label='Golden', color='#FFD700', alpha=0.7, edgecolor='black')
    
    ax1.set_xlabel('Scenario', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Mean Q-Value', fontsize=12, fontweight='bold')
    ax1.set_title('Normal vs Golden Ratio Intensity', fontsize=14, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([s.capitalize() for s in scenarios_list], rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
    
    # Panel 2: Heatmap of metrics
    ax2 = fig.add_subplot(gs[0, 1])
    
    # Prepare heatmap data
    heatmap_data = []
    heatmap_labels = []
    
    for scenario in scenarios_list:
        for intensity, data_dict in [('normal', normal_data), ('golden', golden_data)]:
            heatmap_data.append([
                data_dict[scenario]['mean_q_value'],
                data_dict[scenario]['convergence_score'],
                data_dict[scenario]['stability']
            ])
            heatmap_labels.append(f"{scenario}_{intensity}")
    
    # Normalize columns for better visualization
    heatmap_array = np.array(heatmap_data)
    heatmap_normalized = (heatmap_array - heatmap_array.min(axis=0)) / (heatmap_array.max(axis=0) - heatmap_array.min(axis=0) + 1e-10)
    
    im = ax2.imshow(heatmap_normalized.T, cmap='RdYlGn', aspect='auto')
    
    ax2.set_xticks(np.arange(len(heatmap_labels)))
    ax2.set_yticks(np.arange(3))
    ax2.set_xticklabels(heatmap_labels, rotation=90, fontsize=8)
    ax2.set_yticklabels(['Mean Q-Value', 'Convergence', 'Stability'], fontsize=10)
    ax2.set_title('Performance Metrics Heatmap (Normalized)', fontsize=13, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax2)
    cbar.set_label('Normalized Score', rotation=270, labelpad=20)
    
    # Panel 3: Distribution comparison
    ax3 = fig.add_subplot(gs[1, 0])
    
    all_normal_q = [normal_data[s]['mean_q_value'] for s in scenarios_list]
    all_golden_q = [golden_data[s]['mean_q_value'] for s in scenarios_list]
    
    bp = ax3.boxplot([all_normal_q, all_golden_q],
                      labels=['Normal', 'Golden'],
                      patch_artist=True,
                      notch=True)
    
    # Color boxes
    colors = ['#4169E1', '#FFD700']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax3.set_ylabel('Mean Q-Value', fontsize=12, fontweight='bold')
    ax3.set_title('Q-Value Distribution by Intensity', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
    
    # Add statistics
    normal_mean = np.mean(all_normal_q)
    golden_mean = np.mean(all_golden_q)
    diff_pct = ((golden_mean - normal_mean) / abs(normal_mean)) * 100 if normal_mean != 0 else 0
    
    stats_text = f'Normal: {normal_mean:.6f}\nGolden: {golden_mean:.6f}\nDiff: {diff_pct:+.2f}%'
    ax3.text(0.98, 0.02, stats_text,
            transform=ax3.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    # Panel 4: Summary table
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis('off')
    
    # Prepare table data
    table_data = []
    table_data.append(['Scenario', 'Intensity', 'Mean Q', 'Convergence', 'States', 'Stability'])
    
    for key in sorted(metrics_data.keys()):
        m = metrics_data[key]
        if not m.get('training_complete'):
            continue
        
        s = m['summary']
        table_data.append([
            m['scenario'],
            m['intensity'],
            f"{s['mean_q_value']:.4f}",
            f"{s['convergence_score']:.4f}",
            f"{s['num_states']:,}",
            f"{s['stability']:.2e}"
        ])
    
    table = ax4.table(cellText=table_data, cellLoc='center',
                     loc='center', bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Style header row
    for i in range(6):
        cell = table[(0, i)]
        cell.set_facecolor('#4682B4')
        cell.set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(table_data)):
        for j in range(6):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#E8F4F8')
    
    ax4.set_title('Complete Training Summary', fontsize=13, fontweight='bold', pad=20)
    
    plt.suptitle('Q-Learning Scenario Comparison Analysis',
                 fontsize=16, fontweight='bold', y=0.995)
    
    output_file = OUTPUT_DIR / "qlearning_complete_scenario_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_file.name}")

def main():
    """Generate all Q-Learning visualizations."""
    
    print("=" * 70)
    print("Q-Learning Complete Analysis Visualization")
    print("=" * 70)
    print()
    print(f"Loading metrics from: {METRICS_FILE}")
    
    # Load metrics
    metrics_data = load_metrics()
    
    complete_count = sum(1 for m in metrics_data.values() if m.get('training_complete', False))
    print(f"Loaded data for {complete_count}/{len(metrics_data)} complete scenario-intensity combinations")
    print()
    
    # Generate visualizations
    create_training_dashboard(metrics_data)
    print()
    
    create_convergence_analysis(metrics_data)
    print()
    
    create_scenario_comparison(metrics_data)
    print()
    
    print("=" * 70)
    print("✅ All Q-Learning visualizations generated successfully!")
    print()
    print("Generated files:")
    print("  1. qlearning_complete_training_dashboard.png - 4-panel training overview")
    print("  2. qlearning_complete_convergence_analysis.png - Training progression analysis")
    print("  3. qlearning_complete_scenario_comparison.png - Scenario-by-scenario comparison")
    print()
    print(f"Output location: {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
