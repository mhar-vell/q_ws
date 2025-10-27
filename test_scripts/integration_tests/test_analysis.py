#!/usr/bin/env python3
"""
Simple test script for RL training analysis without GUI dependencies
"""

import numpy as np
import json
from datetime import datetime

def create_simple_analysis_data():
    """Create and analyze training data without complex visualizations"""
    
    print("🎯 RL Training Analysis - Console Mode")
    print("=" * 50)
    
    # Generate sample training data
    scenarios = ['NONE', 'RANDOM', 'PERIODIC', 'CONTINUOUS', 'IMPULSE']
    algorithms = ['DQN', 'Q-Learning']
    
    training_data = []
    episode_count = 0
    
    print("📊 Generating training analysis data...")
    
    for scenario in scenarios:
        for algorithm in algorithms:
            scenario_results = {
                'scenario': scenario,
                'algorithm': algorithm,
                'episodes': [],
                'success_rates': [],
                'errors': [],
                'energy_consumption': [],
                'trajectory_accuracy': [],
                'learning_progress': []
            }
            
            # Simulate 100 episodes per scenario-algorithm combination
            for episode in range(1, 101):
                episode_count += 1
                
                # Simulate learning progress (improvement over time)
                progress = min(1.0, episode / 80.0)  # Learning curve
                
                # Different difficulty for each scenario
                base_difficulty = {
                    'NONE': 0.1,
                    'RANDOM': 0.3,
                    'PERIODIC': 0.25,
                    'CONTINUOUS': 0.2,
                    'IMPULSE': 0.4
                }[scenario]
                
                # Algorithm performance factor
                alg_factor = 1.1 if algorithm == 'DQN' else 1.0
                
                # Calculate metrics with realistic learning curves
                error = max(0.05, base_difficulty * (1 - progress * 0.8) * alg_factor + np.random.normal(0, 0.05))
                success_rate = max(0.1, min(1.0, progress * 0.9 + (1 - base_difficulty) * 0.3))
                energy = 50 + error * 100 + np.random.normal(0, 10)
                accuracy = max(0.1, min(1.0, progress * 0.85 + np.random.normal(0, 0.1)))
                
                scenario_results['episodes'].append(episode)
                scenario_results['success_rates'].append(success_rate)
                scenario_results['errors'].append(error)
                scenario_results['energy_consumption'].append(max(10, energy))
                scenario_results['trajectory_accuracy'].append(accuracy)
                scenario_results['learning_progress'].append(progress)
            
            training_data.append(scenario_results)
    
    print(f"✅ Generated data for {episode_count} episodes")
    print(f"🎯 Scenarios: {len(scenarios)}")
    print(f"🤖 Algorithms: {len(algorithms)}")
    
    # Analysis 1: Success Rates per Scenario
    print("\n📈 ANALYSIS 1: SUCCESS RATES PER SCENARIO")
    print("-" * 45)
    
    for scenario in scenarios:
        scenario_data = [d for d in training_data if d['scenario'] == scenario]
        total_success = sum(np.mean(d['success_rates']) for d in scenario_data) / len(scenario_data)
        print(f"  {scenario:12}: {total_success:.1%} average success rate")
    
    # Analysis 2: Average Error per Episode Trends
    print("\n📉 ANALYSIS 2: ERROR TRENDS BY SCENARIO")
    print("-" * 40)
    
    for scenario in scenarios:
        scenario_data = [d for d in training_data if d['scenario'] == scenario]
        early_error = np.mean([np.mean(d['errors'][:20]) for d in scenario_data])
        late_error = np.mean([np.mean(d['errors'][-20:]) for d in scenario_data])
        improvement = early_error - late_error
        
        print(f"  {scenario:12}: {early_error:.3f} → {late_error:.3f} (Δ{-improvement:+.3f})")
    
    # Analysis 3: Energy Consumption Trends
    print("\n⚡ ANALYSIS 3: ENERGY CONSUMPTION EFFICIENCY")
    print("-" * 45)
    
    for scenario in scenarios:
        scenario_data = [d for d in training_data if d['scenario'] == scenario]
        early_energy = np.mean([np.mean(d['energy_consumption'][:20]) for d in scenario_data])
        late_energy = np.mean([np.mean(d['energy_consumption'][-20:]) for d in scenario_data])
        efficiency_gain = (early_energy - late_energy) / early_energy * 100
        
        print(f"  {scenario:12}: {early_energy:.1f} → {late_energy:.1f} ({efficiency_gain:+.1f}% efficiency)")
    
    # Analysis 4: Trajectory Accuracy Progress
    print("\n🎯 ANALYSIS 4: TRAJECTORY ACCURACY IMPROVEMENT")
    print("-" * 48)
    
    for scenario in scenarios:
        scenario_data = [d for d in training_data if d['scenario'] == scenario]
        early_accuracy = np.mean([np.mean(d['trajectory_accuracy'][:20]) for d in scenario_data])
        late_accuracy = np.mean([np.mean(d['trajectory_accuracy'][-20:]) for d in scenario_data])
        improvement = late_accuracy - early_accuracy
        
        print(f"  {scenario:12}: {early_accuracy:.1%} → {late_accuracy:.1%} (+{improvement:.1%})")
    
    # Analysis 5: Learning Curves Comparison
    print("\n📚 ANALYSIS 5: ALGORITHM COMPARISON")
    print("-" * 35)
    
    for algorithm in algorithms:
        alg_data = [d for d in training_data if d['algorithm'] == algorithm]
        avg_final_accuracy = np.mean([np.mean(d['trajectory_accuracy'][-20:]) for d in alg_data])
        avg_final_success = np.mean([np.mean(d['success_rates'][-20:]) for d in alg_data])
        avg_final_energy = np.mean([np.mean(d['energy_consumption'][-20:]) for d in alg_data])
        
        print(f"  {algorithm:12}")
        print(f"    Final Accuracy: {avg_final_accuracy:.1%}")
        print(f"    Final Success:  {avg_final_success:.1%}")
        print(f"    Final Energy:   {avg_final_energy:.1f}")
    
    # Best performing combinations
    print("\n🏆 BEST PERFORMING COMBINATIONS")
    print("-" * 32)
    
    best_combinations = []
    for data in training_data:
        final_performance = np.mean(data['trajectory_accuracy'][-20:])
        best_combinations.append((
            f"{data['algorithm']} on {data['scenario']}", 
            final_performance
        ))
    
    best_combinations.sort(key=lambda x: x[1], reverse=True)
    
    for i, (combo, performance) in enumerate(best_combinations[:5]):
        print(f"  {i+1}. {combo:25}: {performance:.1%}")
    
    # Save analysis data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rl_analysis_data_{timestamp}.json"
    
    analysis_summary = {
        'timestamp': timestamp,
        'total_episodes': episode_count,
        'scenarios': scenarios,
        'algorithms': algorithms,
        'training_data': training_data,
        'best_combinations': best_combinations[:5]
    }
    
    with open(filename, 'w') as f:
        json.dump(analysis_summary, f, indent=2)
    
    print(f"\n💾 Analysis data saved to: {filename}")
    print(f"📊 Total episodes analyzed: {episode_count}")
    print("✅ Analysis complete!")
    
    return analysis_summary

if __name__ == "__main__":
    create_simple_analysis_data()