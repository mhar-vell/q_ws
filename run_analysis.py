#!/usr/bin/env python3
"""
Integration script to run RL training analysis on collected data
================================================================

This script integrates the analysis system with the actual RL training data
collected from the Husky-KUKA mobile manipulator system.

Usage:
  python3 run_analysis.py [--synthetic] [--save-path PATH]
  
Options:
  --synthetic    Use synthetic data for demonstration
  --save-path    Directory to save analysis graphs (default: analysis_results)
"""

import sys
import os
import argparse
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rl_training_analysis import RLTrainingAnalyzer
import matplotlib.pyplot as plt

def load_from_simulation_data():
    """Attempt to load data from running simulation"""
    try:
        # Try to import and access the simulation data
        import sim_husky_kuka as sim
        from rl_mission_env import MobileManipulatorEnv
        
        print("🔍 Checking for active simulation data...")
        
        # Check if simulation is running and has data
        # This would need to be adapted based on how the simulation stores data
        if hasattr(sim, 'rl_env') and hasattr(sim.rl_env, 'episode_accuracy_history'):
            print("✅ Found active RL environment with training data")
            return sim.rl_env, getattr(sim, 'rl_metrics', {}), getattr(sim, 'rl_algorithm_metrics', {})
        else:
            print("❌ No active simulation data found")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Could not access simulation data: {e}")
        return None, None, None

def create_sample_data_from_files():
    """Create sample data from any existing log files or saved data"""
    try:
        # Check for any existing training logs or data files
        data_files = [
            'rl_training_data.json',
            'training_logs.txt',
            'husky_kuka_trajectory_planner.pkl'
        ]
        
        for file in data_files:
            if os.path.exists(file):
                print(f"📁 Found data file: {file}")
                # Process file based on type
                # This would be implemented based on actual file formats
        
        print("ℹ️  No existing data files found for processing")
        return None
        
    except Exception as e:
        print(f"❌ Error processing data files: {e}")
        return None

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='RL Training Analysis')
    parser.add_argument('--synthetic', action='store_true', 
                       help='Use synthetic data for demonstration')
    parser.add_argument('--save-path', default='analysis_results',
                       help='Directory to save analysis graphs')
    parser.add_argument('--episodes', type=int, default=1000,
                       help='Number of synthetic episodes to generate')
    
    args = parser.parse_args()
    
    print("🎨 RL Training Analysis System")
    print("=" * 40)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💾 Save Path: {args.save_path}")
    
    # Create analyzer
    analyzer = RLTrainingAnalyzer()
    
    # Load data
    if args.synthetic:
        print("🎲 Using synthetic demonstration data...")
        analyzer.generate_synthetic_data(num_episodes=args.episodes)
    else:
        print("🔍 Attempting to load real training data...")
        
        # Try to load from active simulation
        rl_env, rl_metrics, rl_algorithm_metrics = load_from_simulation_data()
        
        if rl_env and (rl_metrics or rl_algorithm_metrics):
            print("✅ Loading data from active simulation...")
            data_count = analyzer.load_data_from_rl_env(rl_env, rl_metrics, rl_algorithm_metrics)
            
            if data_count == 0:
                print("⚠️  No training episodes found in simulation data")
                print("🎲 Falling back to synthetic data...")
                analyzer.generate_synthetic_data(num_episodes=args.episodes)
        else:
            # Try to load from files
            sample_data = create_sample_data_from_files()
            
            if not sample_data:
                print("🎲 No real data available. Generating synthetic data for demonstration...")
                analyzer.generate_synthetic_data(num_episodes=args.episodes)
    
    # Create analysis dashboard
    print("\n🎨 Creating comprehensive analysis dashboard...")
    figures = analyzer.create_comprehensive_dashboard(save_path=args.save_path)
    
    # Display results
    print(f"\n📊 Analysis complete! Generated {len(figures)} analysis graphs:")
    for name in figures.keys():
        print(f"  ✅ {name.replace('_', ' ').title()} Analysis")
    
    if args.save_path:
        print(f"\n💾 Graphs saved to: {args.save_path}/")
        print("📁 Files:")
        if os.path.exists(args.save_path):
            for file in os.listdir(args.save_path):
                if file.endswith('.png'):
                    print(f"  📈 {file}")
    
    # Show interactive plots
    print("\n🖼️  Displaying interactive analysis graphs...")
    print("   Close graph windows to continue...")
    plt.show()
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()