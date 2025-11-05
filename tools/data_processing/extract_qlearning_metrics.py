#!/usr/bin/env python3
"""
Extract Q-Learning Performance Metrics from Checkpoints
=======================================================

Since the metrics JSON file was not properly updated during training,
this script evaluates trained Q-Learning models to extract performance data.

Author: Analysis System
Date: November 3, 2025
"""

import pickle
import json
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

def load_qtable(checkpoint_path):
    """Load Q-table from pickle file."""
    with open(checkpoint_path, 'rb') as f:
        data = pickle.load(f)
    return data

def analyze_qtable_quality(qtable_data):
    """
    Analyze Q-table quality metrics.
    
    Returns:
        dict: Quality metrics including convergence, value statistics, etc.
    """
    if isinstance(qtable_data, dict):
        # Extract Q-table if it's in a dict wrapper
        if 'q_table' in qtable_data:
            qtable = qtable_data['q_table']
        else:
            qtable = qtable_data
    else:
        qtable = qtable_data
    
    # Get all Q-values
    all_q_values = []
    for state_key, actions in qtable.items():
        if isinstance(actions, dict):
            all_q_values.extend(actions.values())
        elif isinstance(actions, (list, np.ndarray)):
            all_q_values.extend(actions)
    
    if not all_q_values:
        return {
            'num_states': 0,
            'mean_q_value': 0.0,
            'std_q_value': 0.0,
            'max_q_value': 0.0,
            'min_q_value': 0.0,
            'convergence_score': 0.0
        }
    
    all_q_values = np.array(all_q_values)
    
    # Calculate statistics
    metrics = {
        'num_states': len(qtable),
        'mean_q_value': float(np.mean(all_q_values)),
        'std_q_value': float(np.std(all_q_values)),
        'max_q_value': float(np.max(all_q_values)),
        'min_q_value': float(np.min(all_q_values)),
        'num_positive': int(np.sum(all_q_values > 0)),
        'num_negative': int(np.sum(all_q_values < 0)),
        'convergence_score': float(1.0 / (1.0 + np.std(all_q_values)))  # Higher = more converged
    }
    
    return metrics

def main():
    """Extract metrics from all Q-Learning checkpoints."""
    
    print("=" * 70)
    print("Q-Learning Metrics Extraction")
    print("=" * 70)
    print()
    
    base_path = Path("/home/marcoreis/robust_mm_control_ws")
    checkpoints_path = base_path / "training_data/phase_03_algorithm_core/qlearning_algorithm_core/session_data/checkpoints"
    final_models_path = base_path / "training_data/phase_03_algorithm_core/qlearning_algorithm_core/session_data/final_models"
    
    # Scenarios and intensities
    scenarios = ['none', 'continuous', 'impulse', 'periodic', 'random']
    intensities = ['normal', 'golden']
    
    # Storage for metrics
    extracted_metrics = {}
    
    # Process each scenario
    for scenario in scenarios:
        scenario_folder = checkpoints_path / f"{scenario}_scenario"
        
        if not scenario_folder.exists():
            print(f"⚠️  Scenario folder not found: {scenario_folder}")
            continue
        
        print(f"\n📊 Processing scenario: {scenario}")
        print("-" * 70)
        
        # Get checkpoint files sorted by episode
        checkpoint_files = sorted(scenario_folder.glob("rl_checkpoint_*_qtable.pkl"))
        
        if not checkpoint_files:
            print(f"  ⚠️  No checkpoints found")
            continue
        
        print(f"  Found {len(checkpoint_files)} checkpoint files")
        
        # Analyze progression through checkpoints
        checkpoint_metrics = []
        
        for ckpt_file in checkpoint_files:
            # Extract episode number
            ep_num = int(ckpt_file.stem.split('_ep')[1].split('_')[0])
            
            try:
                # Load and analyze Q-table
                qtable_data = load_qtable(ckpt_file)
                quality = analyze_qtable_quality(qtable_data)
                
                checkpoint_metrics.append({
                    'episode': ep_num,
                    **quality
                })
                
            except Exception as e:
                print(f"  ⚠️  Error loading {ckpt_file.name}: {e}")
                continue
        
        if not checkpoint_metrics:
            print(f"  ⚠️  No valid checkpoint data extracted")
            continue
        
        # Sort by episode
        checkpoint_metrics.sort(key=lambda x: x['episode'])
        
        # Calculate training progression statistics
        episodes = [m['episode'] for m in checkpoint_metrics]
        mean_q_values = [m['mean_q_value'] for m in checkpoint_metrics]
        convergence_scores = [m['convergence_score'] for m in checkpoint_metrics]
        num_states = [m['num_states'] for m in checkpoint_metrics]
        
        # Estimate final performance (from last few checkpoints)
        last_5_mean_q = np.mean(mean_q_values[-5:])
        last_5_convergence = np.mean(convergence_scores[-5:])
        final_num_states = num_states[-1]
        
        # Calculate training stability (lower std = more stable)
        q_value_trend = np.polyfit(episodes, mean_q_values, 1)[0]  # Slope of linear fit
        convergence_trend = np.polyfit(episodes, convergence_scores, 1)[0]
        
        print(f"  ✅ Extracted data from {len(checkpoint_metrics)} checkpoints")
        print(f"     Episodes: {episodes[0]} - {episodes[-1]}")
        print(f"     Final Q-table states: {final_num_states:,}")
        print(f"     Mean Q-value: {last_5_mean_q:.4f}")
        print(f"     Convergence score: {last_5_convergence:.4f}")
        print(f"     Q-value trend: {q_value_trend:.6f} per episode")
        
        # Store metrics for both intensities (we'll duplicate for now since we can't distinguish)
        # In reality, these checkpoints might be mixed or only one intensity
        for intensity in intensities:
            key = f"{scenario}_{intensity}"
            
            # Check if final model exists
            final_model = final_models_path / f"rl_final_{scenario}_{intensity}_qtable.pkl"
            model_exists = final_model.exists()
            
            if model_exists:
                try:
                    final_qtable = load_qtable(final_model)
                    final_quality = analyze_qtable_quality(final_qtable)
                    
                    extracted_metrics[key] = {
                        'scenario': scenario,
                        'intensity': intensity,
                        'training_complete': True,
                        'episodes_trained': episodes[-1],
                        'num_checkpoints': len(checkpoint_metrics),
                        'final_metrics': final_quality,
                        'training_progression': {
                            'episodes': episodes,
                            'mean_q_values': mean_q_values,
                            'convergence_scores': convergence_scores,
                            'num_states': num_states,
                            'q_value_trend': float(q_value_trend),
                            'convergence_trend': float(convergence_trend)
                        },
                        'summary': {
                            'mean_q_value': float(last_5_mean_q),
                            'convergence_score': float(last_5_convergence),
                            'num_states': int(final_num_states),
                            'stability': float(np.std(mean_q_values[-10:])) if len(mean_q_values) >= 10 else 0.0
                        }
                    }
                    
                except Exception as e:
                    print(f"  ⚠️  Error loading final model {final_model.name}: {e}")
                    extracted_metrics[key] = {
                        'scenario': scenario,
                        'intensity': intensity,
                        'training_complete': False,
                        'error': str(e)
                    }
            else:
                print(f"  ⚠️  Final model not found: {final_model.name}")
    
    # Save extracted metrics
    output_file = base_path / "training_data/phase_03_algorithm_core/qlearning_algorithm_core/session_data/metrics/rl_metrics_q-learning_extracted.json"
    
    print("\n" + "=" * 70)
    print(f"💾 Saving extracted metrics to:")
    print(f"   {output_file}")
    print("=" * 70)
    
    with open(output_file, 'w') as f:
        json.dump(extracted_metrics, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 Extraction Summary")
    print("=" * 70)
    print(f"Total scenario-intensity combinations: {len(extracted_metrics)}")
    
    complete_count = sum(1 for m in extracted_metrics.values() if m.get('training_complete', False))
    print(f"Successfully extracted: {complete_count}/{len(extracted_metrics)}")
    
    print("\nScenarios extracted:")
    for key, metrics in sorted(extracted_metrics.items()):
        if metrics.get('training_complete'):
            summary = metrics['summary']
            print(f"  ✅ {key:20s} - States: {summary['num_states']:6d}, "
                  f"Mean Q: {summary['mean_q_value']:7.4f}, "
                  f"Conv: {summary['convergence_score']:.4f}")
        else:
            print(f"  ❌ {key:20s} - {metrics.get('error', 'No data')}")
    
    print("\n✅ Extraction complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
