#!/usr/bin/env python3
"""
PHASE 1 TRAINING STATUS MONITOR
==============================
Quick status check for Phase 1 enhanced RL training progress
Shows real-time performance improvements and compares with baseline
"""

import json
import os
import time
from datetime import datetime
import numpy as np

def check_pytorch_status():
    """Check PyTorch installation status"""
    try:
        import torch
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        return True, str(device)
    except ImportError:
        return False, "Not installed"

def load_latest_results():
    """Load the most recent training results"""
    result_files = []
    for filename in os.listdir('.'):
        if filename.startswith('enhanced_rl_results_phase1_') and filename.endswith('.json'):
            result_files.append(filename)
    
    if not result_files:
        return None
    
    # Get most recent file
    latest_file = sorted(result_files)[-1]
    
    try:
        with open(latest_file, 'r') as f:
            return json.load(f), latest_file
    except Exception as e:
        print(f"Error loading {latest_file}: {e}")
        return None

def analyze_performance(results):
    """Analyze performance data and show improvements"""
    if not results:
        return
    
    print("📊 PHASE 1 PERFORMANCE ANALYSIS")
    print("=" * 40)
    
    # Calculate overall statistics
    success_rates = []
    avg_errors = []
    agent_types = set()
    
    for scenario, data in results.items():
        success_rates.append(data['success_rate'])
        avg_errors.append(data['avg_error'])
        agent_types.add(data['agent_type'])
    
    overall_success = np.mean(success_rates)
    overall_error = np.mean(avg_errors)
    
    print(f"Overall Performance: {overall_success:.1f}%")
    print(f"Average Error: {overall_error:.4f}m")
    print(f"Agent Types Used: {', '.join(agent_types)}")
    
    # Performance by scenario
    print(f"\n📈 PERFORMANCE BY SCENARIO:")
    for scenario, data in results.items():
        agent_emoji = "🧠" if data['agent_type'] == "DQN" else "📊"
        intensity = "⚡" if 'golden' in scenario else "📊"
        
        print(f"  {agent_emoji}{intensity} {scenario:20s}: {data['success_rate']:5.1f}% "
              f"(error: {data['avg_error']:.4f}m)")
    
    # Phase 1 target analysis
    print(f"\n🎯 PHASE 1 TARGET ANALYSIS:")
    baseline_performance = 25.0  # Original baseline
    
    improvement = overall_success - baseline_performance
    
    if overall_success >= 40:
        status = "✅ SUCCESS"
        message = f"Target achieved! {improvement:+.1f}% improvement"
    elif overall_success >= 35:
        status = "🟡 CLOSE"
        message = f"Nearly there! {improvement:+.1f}% improvement, need {40-overall_success:.1f}% more"
    elif improvement > 5:
        status = "📈 PROGRESS"
        message = f"Good progress! {improvement:+.1f}% improvement, need {40-overall_success:.1f}% more"
    else:
        status = "🔍 NEEDS WORK"
        message = f"Limited improvement: {improvement:+.1f}%, review implementation"
    
    print(f"  {status}: {message}")
    
    # Best and worst scenarios
    best_scenario = max(results.items(), key=lambda x: x[1]['success_rate'])
    worst_scenario = min(results.items(), key=lambda x: x[1]['success_rate'])
    
    print(f"\n🏆 BEST SCENARIO: {best_scenario[0]} ({best_scenario[1]['success_rate']:.1f}%)")
    print(f"💥 WORST SCENARIO: {worst_scenario[0]} ({worst_scenario[1]['success_rate']:.1f}%)")
    
    # DQN vs Q-Learning comparison if both present
    dqn_scenarios = {k: v for k, v in results.items() if v['agent_type'] == 'DQN'}
    qlearn_scenarios = {k: v for k, v in results.items() if v['agent_type'] == 'Q-Learning'}
    
    if dqn_scenarios and qlearn_scenarios:
        dqn_avg = np.mean([v['success_rate'] for v in dqn_scenarios.values()])
        qlearn_avg = np.mean([v['success_rate'] for v in qlearn_scenarios.values()])
        
        print(f"\n🧠 ALGORITHM COMPARISON:")
        print(f"  DQN Average: {dqn_avg:.1f}%")
        print(f"  Q-Learning Average: {qlearn_avg:.1f}%")
        print(f"  DQN Advantage: {dqn_avg - qlearn_avg:+.1f}%")

def main():
    print("🔍 PHASE 1 TRAINING STATUS MONITOR")
    print("=" * 45)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check PyTorch status
    pytorch_ok, pytorch_info = check_pytorch_status()
    print(f"PyTorch Status: {'✅ Available' if pytorch_ok else '❌ Missing'} ({pytorch_info})")
    
    # Check for training results
    results_data = load_latest_results()
    
    if results_data is None:
        print("\n📋 TRAINING STATUS:")
        print("  No training results found yet")
        print("  Start training by running: python launch_enhanced_simulation.py")
        print("  Then press 't' in the simulation to begin RL training")
        return
    
    results, filename = results_data
    print(f"\n📁 Latest Results File: {filename}")
    
    # Analyze performance
    analyze_performance(results)
    
    # Next steps recommendation
    print(f"\n💡 NEXT STEPS:")
    
    overall_success = np.mean([data['success_rate'] for data in results.values()])
    
    if overall_success >= 40:
        print("  🎉 Phase 1 complete! Ready for Phase 2 improvements")
        print("  → State representation optimization")
        print("  → Advanced curriculum learning")
        print("  → Target: 55-60% performance")
    elif overall_success >= 30:
        print("  🔧 Continue Phase 1 training or tune hyperparameters")
        print("  → Try longer training runs (5000 episodes)")
        print("  → Verify PyTorch is available for DQN")
    else:
        print("  🔍 Review Phase 1 implementation")
        print("  → Check if enhanced reward function is active")
        print("  → Verify DQN is being used (not tabular fallback)")
        print("  → Ensure curriculum learning is working")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Status check interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")