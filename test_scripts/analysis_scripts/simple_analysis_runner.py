#!/usr/bin/env python3
"""
Simple RL Training Analysis Runner for Conda Environment
========================================================

This script runs the complete RL training analysis using the conda environment.
It works with the pybullet_env conda environment and generates comprehensive
analysis graphs from the collected training data.

Usage:
    python3 simple_analysis_runner.py
"""

import subprocess
import sys
import os

def run_analysis():
    """Run the comprehensive RL training analysis"""
    
    print("🚀 RL Training Analysis System")
    print("=" * 40)
    print("🐍 Using conda environment: pybullet_env")
    
    # Python code for analysis
    analysis_code = '''
import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

print("📊 Comprehensive RL Training Analysis")
print("=" * 45)

# Load real training metrics
try:
    with open('rl_metrics_dqn.json', 'r') as f:
        rl_data = json.load(f)
    print("✅ Successfully loaded RL training metrics")
    print(f"📈 Data size: {len(rl_data)} scenario combinations")
    
    # Quick analysis summary
    total_episodes = 0
    scenarios = set()
    
    for key, data in rl_data.items():
        if 'errors' in data:
            total_episodes += len(data['errors'])
            scenario = key.split('_')[0].upper()
            scenarios.add(scenario)
    
    print(f"🎯 Total episodes: {total_episodes}")
    print(f"🔬 Scenarios analyzed: {', '.join(sorted(scenarios))}")
    
    # Create a simple summary chart
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    scenario_performance = {}
    for key, data in rl_data.items():
        scenario = key.split('_')[0].upper()
        if 'errors' in data and len(data['errors']) > 0:
            success_rate = 1 - np.mean(data['errors'])
            if scenario not in scenario_performance:
                scenario_performance[scenario] = []
            scenario_performance[scenario].append(success_rate)
    
    # Plot scenario performance
    scenario_names = list(scenario_performance.keys())
    avg_performance = [np.mean(scenario_performance[s]) for s in scenario_names]
    
    colors = ['#2E8B57', '#FF6347', '#4169E1', '#FF8C00', '#9932CC']
    bars = ax.bar(scenario_names, avg_performance, 
                  color=colors[:len(scenario_names)])
    
    ax.set_title('RL Training Performance by Disturbance Scenario', 
                fontsize=14, fontweight='bold')
    ax.set_ylabel('Success Rate')
    ax.set_ylim(0, 1)
    
    # Add value labels
    for bar, value in zip(bars, avg_performance):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{value:.1%}', ha='center', va='bottom', fontweight='bold')
    
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save the figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rl_performance_summary_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    
    print(f"✅ Performance summary saved as: {filename}")
    
    # Print detailed statistics
    print("\\n📊 DETAILED PERFORMANCE ANALYSIS")
    print("=" * 40)
    
    for scenario, performances in scenario_performance.items():
        avg_perf = np.mean(performances)
        std_perf = np.std(performances)
        print(f"{scenario:12}: {avg_perf:.1%} ± {std_perf:.1%}")
    
    best_scenario = max(scenario_performance.items(), key=lambda x: np.mean(x[1]))
    worst_scenario = min(scenario_performance.items(), key=lambda x: np.mean(x[1]))
    
    print(f"\\n🏆 Best Scenario: {best_scenario[0]} ({np.mean(best_scenario[1]):.1%})")
    print(f"🔻 Most Challenging: {worst_scenario[0]} ({np.mean(worst_scenario[1]):.1%})")
    
    print(f"\\n💾 Analysis complete! Graph saved as {filename}")
    
except FileNotFoundError:
    print("❌ RL metrics file not found. Generating demo analysis...")
    
    # Generate demo data
    scenarios = ['NONE', 'RANDOM', 'PERIODIC', 'CONTINUOUS', 'IMPULSE']
    performance = [0.85, 0.45, 0.65, 0.70, 0.40]
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    colors = ['#2E8B57', '#FF6347', '#4169E1', '#FF8C00', '#9932CC']
    bars = ax.bar(scenarios, performance, color=colors)
    
    ax.set_title('RL Training Performance (Demo Data)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Success Rate')
    ax.set_ylim(0, 1)
    
    for bar, value in zip(bars, performance):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{value:.1%}', ha='center', va='bottom', fontweight='bold')
    
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rl_demo_analysis_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    
    print(f"✅ Demo analysis saved as: {filename}")
    print("\\n📊 DEMO ANALYSIS RESULTS:")
    for scenario, perf in zip(scenarios, performance):
        print(f"  {scenario:12}: {perf:.1%}")

print("\\n🎯 Analysis complete!")
'''
    
    # Write the analysis code to a temporary file
    with open('temp_analysis.py', 'w') as f:
        f.write(analysis_code)
    
    try:
        # Run the analysis
        print("🔄 Running analysis...")
        result = subprocess.run([sys.executable, 'temp_analysis.py'], 
                              capture_output=True, text=True, cwd='.')
        
        print("📄 Analysis output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Warnings/Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Analysis completed successfully!")
        else:
            print(f"❌ Analysis failed with exit code: {result.returncode}")
        
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
    
    finally:
        # Clean up temporary file
        if os.path.exists('temp_analysis.py'):
            os.remove('temp_analysis.py')

if __name__ == "__main__":
    run_analysis()