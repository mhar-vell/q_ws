#!/usr/bin/env python3
"""
RL Training Analysis Module
==========================

Comprehensive analysis and visualization of RL training data collected from the 
Husky-KUKA mobile manipulator training system.

Generates graphs for:
1. Success rates per disturbance scenario
2. Average error per episode trends
3. Energy consumption evolution
4. Trajectory accuracy metrics
5. Learning curves and convergence analysis

Author: Enhanced RL Training System
Date: October 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import seaborn as sns
from datetime import datetime
import json
import pickle
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import pandas as pd
from scipy import stats
from scipy.signal import savgol_filter

# Set style for professional-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

@dataclass
class TrainingMetrics:
    """Data structure for storing training metrics"""
    episode: int
    scenario: str
    intensity: str
    algorithm: str
    success: bool
    error: float
    steps: int
    energy: float
    reward: float
    trajectory_accuracy: float
    distance_accuracy: float
    timing_accuracy: float
    waypoint_success_rate: float
    cycles_completed: int
    timestamp: float

class RLTrainingAnalyzer:
    """
    Comprehensive analyzer for RL training data with advanced visualization capabilities
    """
    
    def __init__(self, data_source=None):
        """Initialize analyzer with optional data source"""
        self.metrics_data: List[TrainingMetrics] = []
        self.scenarios = ['NONE', 'RANDOM', 'PERIODIC', 'CONTINUOUS', 'IMPULSE']
        self.intensities = ['NORMAL', 'GOLDEN']
        self.algorithms = ['DQN', 'Q-Learning']
        
        # Color schemes for different elements
        self.scenario_colors = {
            'NONE': '#2E8B57',      # Sea Green
            'RANDOM': '#FF6347',    # Tomato
            'PERIODIC': '#4169E1',  # Royal Blue
            'CONTINUOUS': '#FF8C00', # Dark Orange
            'IMPULSE': '#9932CC'    # Dark Orchid
        }
        
        self.algorithm_colors = {
            'DQN': '#1f77b4',       # Blue
            'Q-Learning': '#ff7f0e' # Orange
        }
        
        if data_source:
            self.load_data(data_source)
    
    def load_data_from_rl_env(self, rl_env, rl_metrics, rl_algorithm_metrics=None):
        """Load data directly from running RL environment and metrics"""
        print("📊 Loading training data from RL environment...")
        
        # Load accuracy history from RL environment
        if hasattr(rl_env, 'episode_accuracy_history') and rl_env.episode_accuracy_history:
            for episode_data in rl_env.episode_accuracy_history:
                # Create metric entry from episode data
                metric = TrainingMetrics(
                    episode=episode_data['episode'],
                    scenario='NONE',  # Default, will be updated with actual scenario data
                    intensity='NORMAL',
                    algorithm='Q-Learning',  # Default
                    success=episode_data['cycle_completion_rate'] > 0,
                    error=1.0 - episode_data['overall_accuracy'],
                    steps=episode_data['trajectory_length'],
                    energy=episode_data['trajectory_length'] * 0.1,  # Approximate energy
                    reward=episode_data['overall_accuracy'] * 100,
                    trajectory_accuracy=episode_data['overall_accuracy'],
                    distance_accuracy=episode_data['distance_accuracy'],
                    timing_accuracy=episode_data['timing_accuracy'],
                    waypoint_success_rate=episode_data['waypoint_passage_rate'],
                    cycles_completed=episode_data['cycles_completed'],
                    timestamp=episode_data['episode']
                )
                self.metrics_data.append(metric)
        
        # Load scenario-specific metrics if available
        if rl_metrics:
            for combo_key, data in rl_metrics.items():
                scenario, intensity = combo_key.split('_')
                
                for i in range(len(data['errors'])):
                    if i < len(data['steps']) and i < len(data['energy']):
                        metric = TrainingMetrics(
                            episode=i + 1,
                            scenario=scenario,
                            intensity=intensity,
                            algorithm='Q-Learning',
                            success=data['success'] > 0,
                            error=data['errors'][i] if i < len(data['errors']) else 0.5,
                            steps=data['steps'][i] if i < len(data['steps']) else 100,
                            energy=data['energy'][i] if i < len(data['energy']) else 50.0,
                            reward=100 - data['errors'][i] * 100 if i < len(data['errors']) else 50,
                            trajectory_accuracy=1 - data['errors'][i] if i < len(data['errors']) else 0.5,
                            distance_accuracy=0.5,  # Approximate
                            timing_accuracy=0.5,    # Approximate
                            waypoint_success_rate=0.5,  # Approximate
                            cycles_completed=0,
                            timestamp=i + 1
                        )
                        self.metrics_data.append(metric)
        
        # Load algorithm comparison data
        if rl_algorithm_metrics:
            for algorithm, algorithm_data in rl_algorithm_metrics.items():
                for combo_key, data in algorithm_data.items():
                    scenario, intensity = combo_key.split('_')
                    
                    for i in range(len(data['errors'])):
                        if i < len(data['steps']) and i < len(data['energy']):
                            metric = TrainingMetrics(
                                episode=i + 1,
                                scenario=scenario,
                                intensity=intensity,
                                algorithm=algorithm,
                                success=data['success'] > 0,
                                error=data['errors'][i] if i < len(data['errors']) else 0.5,
                                steps=data['steps'][i] if i < len(data['steps']) else 100,
                                energy=data['energy'][i] if i < len(data['energy']) else 50.0,
                                reward=100 - data['errors'][i] * 100 if i < len(data['errors']) else 50,
                                trajectory_accuracy=1 - data['errors'][i] if i < len(data['errors']) else 0.5,
                                distance_accuracy=0.5,
                                timing_accuracy=0.5,
                                waypoint_success_rate=0.5,
                                cycles_completed=0,
                                timestamp=i + 1
                            )
                            self.metrics_data.append(metric)
        
        print(f"✅ Loaded {len(self.metrics_data)} training episodes for analysis")
        return len(self.metrics_data)
    
    def generate_synthetic_data(self, num_episodes=1000):
        """Generate synthetic training data for demonstration"""
        print(f"🎲 Generating synthetic training data ({num_episodes} episodes)...")
        
        np.random.seed(42)  # For reproducible results
        
        for episode in range(1, num_episodes + 1):
            for scenario in self.scenarios:
                for intensity in self.intensities:
                    for algorithm in self.algorithms:
                        # Simulate learning progress with noise
                        progress = min(1.0, episode / (num_episodes * 0.8))
                        
                        # Different scenarios have different baseline difficulties
                        scenario_difficulty = {
                            'NONE': 0.1,
                            'RANDOM': 0.3,
                            'PERIODIC': 0.25,
                            'CONTINUOUS': 0.2,
                            'IMPULSE': 0.4
                        }[scenario]
                        
                        # Algorithm performance differences
                        algorithm_factor = 1.1 if algorithm == 'DQN' else 1.0
                        
                        # Base error that decreases with training
                        base_error = scenario_difficulty * (1 - progress * 0.8) * algorithm_factor
                        error = max(0.05, base_error + np.random.normal(0, 0.1))
                        
                        # Success rate improves with training
                        success_prob = max(0.1, 1 - error - scenario_difficulty * 0.3)
                        success = np.random.random() < success_prob
                        
                        # Steps and energy correlate with error
                        steps = int(50 + error * 150 + np.random.normal(0, 10))
                        energy = steps * (0.5 + error + np.random.normal(0, 0.1))
                        
                        # Trajectory accuracy improves with training
                        trajectory_accuracy = max(0.1, min(1.0, progress + np.random.normal(0, 0.1)))
                        
                        metric = TrainingMetrics(
                            episode=episode,
                            scenario=scenario,
                            intensity=intensity,
                            algorithm=algorithm,
                            success=success,
                            error=error,
                            steps=max(10, steps),
                            energy=max(5.0, energy),
                            reward=100 * (1 - error) + np.random.normal(0, 5),
                            trajectory_accuracy=trajectory_accuracy,
                            distance_accuracy=trajectory_accuracy + np.random.normal(0, 0.05),
                            timing_accuracy=trajectory_accuracy + np.random.normal(0, 0.05),
                            waypoint_success_rate=trajectory_accuracy + np.random.normal(0, 0.05),
                            cycles_completed=int(max(0, (trajectory_accuracy - 0.5) * 3)),
                            timestamp=episode
                        )
                        self.metrics_data.append(metric)
        
        print(f"✅ Generated {len(self.metrics_data)} synthetic training episodes")
    
    def save_data(self, filepath):
        """Save training data to file"""
        data_dict = [asdict(metric) for metric in self.metrics_data]
        
        with open(filepath, 'w') as f:
            json.dump(data_dict, f, indent=2)
        
        print(f"💾 Training data saved to {filepath}")
    
    def load_data(self, filepath):
        """Load training data from file"""
        try:
            with open(filepath, 'r') as f:
                data_dict = json.load(f)
            
            self.metrics_data = [TrainingMetrics(**item) for item in data_dict]
            print(f"📁 Loaded {len(self.metrics_data)} training episodes from {filepath}")
        except FileNotFoundError:
            print(f"❌ File {filepath} not found. Generating synthetic data...")
            self.generate_synthetic_data()
    
    def create_success_rate_analysis(self, figsize=(15, 8)):
        """Create comprehensive success rate analysis by scenario"""
        print("📈 Creating success rate analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('Success Rate Analysis by Disturbance Scenario', fontsize=16, fontweight='bold')
        
        # Convert data to DataFrame for easier analysis
        df = pd.DataFrame([asdict(m) for m in self.metrics_data])
        
        # 1. Overall Success Rate by Scenario (Bar Chart)
        ax1 = axes[0, 0]
        scenario_success = df.groupby('scenario')['success'].mean()
        bars = ax1.bar(scenario_success.index, scenario_success.values, 
                       color=[self.scenario_colors[s] for s in scenario_success.index])
        ax1.set_title('Overall Success Rate by Scenario')
        ax1.set_ylabel('Success Rate')
        ax1.set_ylim(0, 1)
        
        # Add value labels on bars
        for bar, value in zip(bars, scenario_success.values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{value:.2%}', ha='center', va='bottom')
        
        # 2. Success Rate Trends Over Time
        ax2 = axes[0, 1]
        for scenario in self.scenarios:
            scenario_data = df[df['scenario'] == scenario]
            if len(scenario_data) > 0:
                # Calculate rolling success rate
                scenario_data_sorted = scenario_data.sort_values('episode')
                rolling_success = scenario_data_sorted['success'].rolling(window=50, min_periods=10).mean()
                ax2.plot(scenario_data_sorted['episode'], rolling_success, 
                        color=self.scenario_colors[scenario], label=scenario, linewidth=2)
        
        ax2.set_title('Success Rate Trends Over Training')
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Rolling Success Rate (50 episodes)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Success Rate by Algorithm and Scenario (Heatmap)
        ax3 = axes[1, 0]
        success_pivot = df.groupby(['scenario', 'algorithm'])['success'].mean().unstack()
        sns.heatmap(success_pivot, annot=True, fmt='.2%', cmap='RdYlGn', 
                   ax=ax3, cbar_kws={'label': 'Success Rate'})
        ax3.set_title('Success Rate: Algorithm vs Scenario')
        
        # 4. Success Rate Distribution (Box Plot)
        ax4 = axes[1, 1]
        success_by_scenario = [df[df['scenario'] == s]['success'].astype(float).values for s in self.scenarios]
        box_plot = ax4.boxplot(success_by_scenario, labels=self.scenarios, patch_artist=True)
        
        # Color the boxes
        for patch, scenario in zip(box_plot['boxes'], self.scenarios):
            patch.set_facecolor(self.scenario_colors[scenario])
            patch.set_alpha(0.7)
        
        ax4.set_title('Success Rate Distribution by Scenario')
        ax4.set_ylabel('Success Rate')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def create_error_trend_analysis(self, figsize=(15, 10)):
        """Create comprehensive error trend analysis"""
        print("📉 Creating error trend analysis...")
        
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(3, 2, figure=fig)
        fig.suptitle('Error Trend Analysis', fontsize=16, fontweight='bold')
        
        df = pd.DataFrame([asdict(m) for m in self.metrics_data])
        
        # 1. Average Error Over Time (Main Plot)
        ax1 = fig.add_subplot(gs[0, :])
        
        for scenario in self.scenarios:
            scenario_data = df[df['scenario'] == scenario].sort_values('episode')
            if len(scenario_data) > 0:
                # Smooth the error trend
                if len(scenario_data) > 20:
                    smoothed_error = savgol_filter(scenario_data['error'], 
                                                 min(51, len(scenario_data)//4*2+1), 3)
                else:
                    smoothed_error = scenario_data['error']
                
                ax1.plot(scenario_data['episode'], smoothed_error, 
                        color=self.scenario_colors[scenario], label=scenario, linewidth=2)
                
                # Add confidence intervals
                rolling_std = scenario_data['error'].rolling(window=50).std()
                rolling_mean = scenario_data['error'].rolling(window=50).mean()
                ax1.fill_between(scenario_data['episode'], 
                               rolling_mean - rolling_std, 
                               rolling_mean + rolling_std,
                               color=self.scenario_colors[scenario], alpha=0.2)
        
        ax1.set_title('Average Error Trends Over Training (Smoothed)')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Average Error')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Error Distribution by Scenario
        ax2 = fig.add_subplot(gs[1, 0])
        error_by_scenario = [df[df['scenario'] == s]['error'].values for s in self.scenarios]
        violin_parts = ax2.violinplot(error_by_scenario, positions=range(len(self.scenarios)))
        
        # Color the violins
        for i, (part, scenario) in enumerate(zip(violin_parts['bodies'], self.scenarios)):
            part.set_facecolor(self.scenario_colors[scenario])
            part.set_alpha(0.7)
        
        ax2.set_xticks(range(len(self.scenarios)))
        ax2.set_xticklabels(self.scenarios, rotation=45)
        ax2.set_title('Error Distribution by Scenario')
        ax2.set_ylabel('Error')
        
        # 3. Algorithm Comparison - Error
        ax3 = fig.add_subplot(gs[1, 1])
        for algorithm in self.algorithms:
            alg_data = df[df['algorithm'] == algorithm].sort_values('episode')
            if len(alg_data) > 0:
                rolling_error = alg_data['error'].rolling(window=100).mean()
                ax3.plot(alg_data['episode'], rolling_error, 
                        color=self.algorithm_colors[algorithm], 
                        label=algorithm, linewidth=2)
        
        ax3.set_title('Algorithm Comparison - Error Trends')
        ax3.set_xlabel('Episode')
        ax3.set_ylabel('Rolling Average Error')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Error Improvement Rate
        ax4 = fig.add_subplot(gs[2, :])
        
        for scenario in self.scenarios:
            scenario_data = df[df['scenario'] == scenario].sort_values('episode')
            if len(scenario_data) > 100:  # Need sufficient data
                # Calculate improvement rate (derivative of error)
                episodes = scenario_data['episode'].values
                errors = scenario_data['error'].values
                
                # Calculate rolling derivative
                window = 50
                improvement_rate = []
                episode_centers = []
                
                for i in range(window, len(errors) - window):
                    # Linear regression slope over window
                    x = episodes[i-window//2:i+window//2]
                    y = errors[i-window//2:i+window//2]
                    slope, _, _, _, _ = stats.linregress(x, y)
                    improvement_rate.append(-slope)  # Negative because we want improvement
                    episode_centers.append(episodes[i])
                
                if improvement_rate:
                    ax4.plot(episode_centers, improvement_rate, 
                            color=self.scenario_colors[scenario], 
                            label=f'{scenario} Improvement', linewidth=2)
        
        ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax4.set_title('Error Improvement Rate Over Training')
        ax4.set_xlabel('Episode')
        ax4.set_ylabel('Improvement Rate (Error Reduction per Episode)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_energy_consumption_analysis(self, figsize=(15, 8)):
        """Create comprehensive energy consumption analysis"""
        print("⚡ Creating energy consumption analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('Energy Consumption Analysis', fontsize=16, fontweight='bold')
        
        df = pd.DataFrame([asdict(m) for m in self.metrics_data])
        
        # 1. Energy Consumption Trends by Scenario
        ax1 = axes[0, 0]
        for scenario in self.scenarios:
            scenario_data = df[df['scenario'] == scenario].sort_values('episode')
            if len(scenario_data) > 0:
                rolling_energy = scenario_data['energy'].rolling(window=50).mean()
                ax1.plot(scenario_data['episode'], rolling_energy, 
                        color=self.scenario_colors[scenario], label=scenario, linewidth=2)
        
        ax1.set_title('Energy Consumption Trends by Scenario')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Rolling Average Energy')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Energy vs Success Rate Correlation
        ax2 = axes[0, 1]
        scenario_stats = df.groupby('scenario').agg({
            'energy': 'mean',
            'success': 'mean'
        }).reset_index()
        
        scatter = ax2.scatter(scenario_stats['energy'], scenario_stats['success'], 
                            c=[self.scenario_colors[s] for s in scenario_stats['scenario']], 
                            s=200, alpha=0.7)
        
        # Add scenario labels
        for i, row in scenario_stats.iterrows():
            ax2.annotate(row['scenario'], 
                        (row['energy'], row['success']), 
                        xytext=(5, 5), textcoords='offset points')
        
        # Add correlation line
        correlation = stats.pearsonr(scenario_stats['energy'], scenario_stats['success'])
        ax2.set_title(f'Energy vs Success Rate (r={correlation[0]:.3f})')
        ax2.set_xlabel('Average Energy Consumption')
        ax2.set_ylabel('Success Rate')
        ax2.grid(True, alpha=0.3)
        
        # 3. Energy Efficiency Over Time (Energy per Success)
        ax3 = axes[1, 0]
        for scenario in self.scenarios:
            scenario_data = df[df['scenario'] == scenario].sort_values('episode')
            if len(scenario_data) > 0:
                # Calculate energy efficiency (lower is better)
                efficiency = []
                episodes = []
                window = 100
                
                for i in range(window, len(scenario_data)):
                    window_data = scenario_data.iloc[i-window:i]
                    total_energy = window_data['energy'].sum()
                    total_successes = window_data['success'].sum()
                    
                    if total_successes > 0:
                        energy_per_success = total_energy / total_successes
                        efficiency.append(energy_per_success)
                        episodes.append(scenario_data.iloc[i]['episode'])
                
                if efficiency:
                    ax3.plot(episodes, efficiency, 
                            color=self.scenario_colors[scenario], 
                            label=scenario, linewidth=2)
        
        ax3.set_title('Energy Efficiency Trends (Energy per Success)')
        ax3.set_xlabel('Episode')
        ax3.set_ylabel('Energy per Success (lower is better)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Energy Distribution by Algorithm
        ax4 = axes[1, 1]
        energy_by_algorithm = [df[df['algorithm'] == alg]['energy'].values for alg in self.algorithms]
        box_plot = ax4.boxplot(energy_by_algorithm, labels=self.algorithms, patch_artist=True)
        
        # Color the boxes
        for patch, algorithm in zip(box_plot['boxes'], self.algorithms):
            patch.set_facecolor(self.algorithm_colors[algorithm])
            patch.set_alpha(0.7)
        
        ax4.set_title('Energy Consumption Distribution by Algorithm')
        ax4.set_ylabel('Energy Consumption')
        
        plt.tight_layout()
        return fig
    
    def create_trajectory_accuracy_analysis(self, figsize=(16, 12)):
        """Create comprehensive trajectory accuracy analysis"""
        print("🎯 Creating trajectory accuracy analysis...")
        
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(3, 3, figure=fig)
        fig.suptitle('Trajectory Accuracy Analysis', fontsize=16, fontweight='bold')
        
        df = pd.DataFrame([asdict(m) for m in self.metrics_data])
        
        # 1. Overall Accuracy Trends (Main plot spanning 2 columns)
        ax1 = fig.add_subplot(gs[0, :2])
        for scenario in self.scenarios:
            scenario_data = df[df['scenario'] == scenario].sort_values('episode')
            if len(scenario_data) > 0:
                rolling_accuracy = scenario_data['trajectory_accuracy'].rolling(window=50).mean()
                ax1.plot(scenario_data['episode'], rolling_accuracy, 
                        color=self.scenario_colors[scenario], label=scenario, linewidth=2)
        
        ax1.set_title('Trajectory Accuracy Trends by Scenario')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Rolling Average Accuracy')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1)
        
        # 2. Accuracy Components Comparison
        ax2 = fig.add_subplot(gs[0, 2])
        accuracy_components = df.groupby('scenario')[
            ['trajectory_accuracy', 'distance_accuracy', 'timing_accuracy', 'waypoint_success_rate']
        ].mean()
        
        accuracy_components.plot(kind='bar', ax=ax2, width=0.8)
        ax2.set_title('Accuracy Components by Scenario')
        ax2.set_ylabel('Average Accuracy')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend(['Overall', 'Distance', 'Timing', 'Waypoints'], bbox_to_anchor=(1.05, 1))
        
        # 3. Distance Accuracy Heatmap
        ax3 = fig.add_subplot(gs[1, 0])
        distance_pivot = df.groupby(['scenario', 'algorithm'])['distance_accuracy'].mean().unstack()
        sns.heatmap(distance_pivot, annot=True, fmt='.3f', cmap='RdYlGn', 
                   ax=ax3, cbar_kws={'label': 'Distance Accuracy'})
        ax3.set_title('Distance Accuracy:\nAlgorithm vs Scenario')
        
        # 4. Timing Accuracy Trends
        ax4 = fig.add_subplot(gs[1, 1])
        for algorithm in self.algorithms:
            alg_data = df[df['algorithm'] == algorithm].sort_values('episode')
            if len(alg_data) > 0:
                rolling_timing = alg_data['timing_accuracy'].rolling(window=100).mean()
                ax4.plot(alg_data['episode'], rolling_timing, 
                        color=self.algorithm_colors[algorithm], 
                        label=algorithm, linewidth=2)
        
        ax4.set_title('Timing Accuracy by Algorithm')
        ax4.set_xlabel('Episode')
        ax4.set_ylabel('Rolling Timing Accuracy')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Waypoint Success Rate Distribution
        ax5 = fig.add_subplot(gs[1, 2])
        waypoint_by_scenario = [df[df['scenario'] == s]['waypoint_success_rate'].values for s in self.scenarios]
        violin_parts = ax5.violinplot(waypoint_by_scenario, positions=range(len(self.scenarios)))
        
        for i, (part, scenario) in enumerate(zip(violin_parts['bodies'], self.scenarios)):
            part.set_facecolor(self.scenario_colors[scenario])
            part.set_alpha(0.7)
        
        ax5.set_xticks(range(len(self.scenarios)))
        ax5.set_xticklabels(self.scenarios, rotation=45)
        ax5.set_title('Waypoint Success Rate\nDistribution')
        ax5.set_ylabel('Success Rate')
        
        # 6. Accuracy vs Error Correlation (spanning 2 columns)
        ax6 = fig.add_subplot(gs[2, :2])
        for scenario in self.scenarios:
            scenario_data = df[df['scenario'] == scenario]
            if len(scenario_data) > 0:
                ax6.scatter(scenario_data['error'], scenario_data['trajectory_accuracy'], 
                          color=self.scenario_colors[scenario], alpha=0.5, 
                          label=scenario, s=20)
        
        # Add correlation line
        correlation = stats.pearsonr(df['error'], df['trajectory_accuracy'])
        ax6.set_title(f'Trajectory Accuracy vs Error Correlation (r={correlation[0]:.3f})')
        ax6.set_xlabel('Error')
        ax6.set_ylabel('Trajectory Accuracy')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. Cycles Completed Progress
        ax7 = fig.add_subplot(gs[2, 2])
        cycles_stats = df.groupby('scenario')['cycles_completed'].mean()
        bars = ax7.bar(cycles_stats.index, cycles_stats.values,
                      color=[self.scenario_colors[s] for s in cycles_stats.index])
        
        ax7.set_title('Average Cycles Completed')
        ax7.set_ylabel('Cycles per Episode')
        ax7.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, cycles_stats.values):
            ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{value:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def create_learning_curves_analysis(self, figsize=(16, 10)):
        """Create comprehensive learning curves and convergence analysis"""
        print("📚 Creating learning curves analysis...")
        
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(2, 3, figure=fig)
        fig.suptitle('Learning Curves and Convergence Analysis', fontsize=16, fontweight='bold')
        
        df = pd.DataFrame([asdict(m) for m in self.metrics_data])
        
        # 1. Reward Learning Curves (Main plot)
        ax1 = fig.add_subplot(gs[0, :2])
        for algorithm in self.algorithms:
            alg_data = df[df['algorithm'] == algorithm].sort_values('episode')
            if len(alg_data) > 0:
                rolling_reward = alg_data['reward'].rolling(window=100).mean()
                ax1.plot(alg_data['episode'], rolling_reward, 
                        color=self.algorithm_colors[algorithm], 
                        label=f'{algorithm} (Rolling Avg)', linewidth=2)
                
                # Add raw data with transparency
                ax1.scatter(alg_data['episode'], alg_data['reward'], 
                           color=self.algorithm_colors[algorithm], alpha=0.1, s=1)
        
        ax1.set_title('Reward Learning Curves by Algorithm')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Reward')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Convergence Analysis - Reward Variance
        ax2 = fig.add_subplot(gs[0, 2])
        for algorithm in self.algorithms:
            alg_data = df[df['algorithm'] == algorithm].sort_values('episode')
            if len(alg_data) > 100:
                variance_over_time = []
                episodes = []
                window = 100
                
                for i in range(window, len(alg_data)):
                    window_data = alg_data.iloc[i-window:i]
                    variance = window_data['reward'].var()
                    variance_over_time.append(variance)
                    episodes.append(alg_data.iloc[i]['episode'])
                
                if variance_over_time:
                    ax2.plot(episodes, variance_over_time, 
                            color=self.algorithm_colors[algorithm], 
                            label=algorithm, linewidth=2)
        
        ax2.set_title('Reward Variance\n(Convergence Indicator)')
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Reward Variance')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Performance Improvement Rate
        ax3 = fig.add_subplot(gs[1, 0])
        for scenario in self.scenarios[:3]:  # Limit to avoid clutter
            scenario_data = df[df['scenario'] == scenario].sort_values('episode')
            if len(scenario_data) > 100:
                # Calculate performance improvement (derivative of accuracy)
                episodes = scenario_data['episode'].values
                accuracy = scenario_data['trajectory_accuracy'].values
                
                window = 50
                improvement_rate = []
                episode_centers = []
                
                for i in range(window, len(accuracy) - window):
                    x = episodes[i-window//2:i+window//2]
                    y = accuracy[i-window//2:i+window//2]
                    slope, _, _, _, _ = stats.linregregression(x, y)
                    improvement_rate.append(slope)
                    episode_centers.append(episodes[i])
                
                if improvement_rate:
                    ax3.plot(episode_centers, improvement_rate, 
                            color=self.scenario_colors[scenario], 
                            label=scenario, linewidth=2)
        
        ax3.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax3.set_title('Performance Improvement Rate')
        ax3.set_xlabel('Episode')
        ax3.set_ylabel('Accuracy Improvement per Episode')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Learning Efficiency (Accuracy per Episode)
        ax4 = fig.add_subplot(gs[1, 1])
        for algorithm in self.algorithms:
            alg_data = df[df['algorithm'] == algorithm].sort_values('episode')
            if len(alg_data) > 0:
                # Calculate cumulative accuracy gain
                cumulative_accuracy = alg_data['trajectory_accuracy'].cumsum() / alg_data['episode']
                ax4.plot(alg_data['episode'], cumulative_accuracy, 
                        color=self.algorithm_colors[algorithm], 
                        label=algorithm, linewidth=2)
        
        ax4.set_title('Learning Efficiency\n(Cumulative Accuracy/Episode)')
        ax4.set_xlabel('Episode')
        ax4.set_ylabel('Average Accuracy Gained')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Final Performance Comparison
        ax5 = fig.add_subplot(gs[1, 2])
        
        # Get final performance metrics (last 100 episodes)
        final_performance = {}
        for algorithm in self.algorithms:
            alg_data = df[df['algorithm'] == algorithm]
            if len(alg_data) > 100:
                final_data = alg_data.tail(100)
                final_performance[algorithm] = {
                    'Reward': final_data['reward'].mean(),
                    'Accuracy': final_data['trajectory_accuracy'].mean(),
                    'Success Rate': final_data['success'].mean(),
                    'Efficiency': final_data['energy'].mean()
                }
        
        if final_performance:
            metrics = list(final_performance[self.algorithms[0]].keys())
            x = np.arange(len(metrics))
            width = 0.35
            
            for i, algorithm in enumerate(self.algorithms):
                if algorithm in final_performance:
                    values = list(final_performance[algorithm].values())
                    # Normalize values for comparison (scale 0-1)
                    normalized_values = []
                    for j, value in enumerate(values):
                        if metrics[j] == 'Efficiency':
                            # For efficiency, lower is better, so invert
                            max_val = max([final_performance[alg][metrics[j]] for alg in final_performance])
                            normalized_values.append(1 - (value / max_val))
                        else:
                            max_val = max([final_performance[alg][metrics[j]] for alg in final_performance])
                            normalized_values.append(value / max_val if max_val > 0 else 0)
                    
                    ax5.bar(x + i * width, normalized_values, width, 
                           color=self.algorithm_colors[algorithm], 
                           label=algorithm, alpha=0.8)
            
            ax5.set_title('Final Performance Comparison\n(Normalized, Last 100 Episodes)')
            ax5.set_xlabel('Metrics')
            ax5.set_ylabel('Normalized Performance')
            ax5.set_xticks(x + width / 2)
            ax5.set_xticklabels(metrics, rotation=45)
            ax5.legend()
            ax5.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_comprehensive_dashboard(self, save_path=None):
        """Create and display all analysis graphs"""
        print("\n🎨 Creating comprehensive training analysis dashboard...")
        print("=" * 60)
        
        if not self.metrics_data:
            print("❌ No training data available. Loading synthetic data for demonstration...")
            self.generate_synthetic_data()
        
        # Create all analysis figures
        figures = {}
        
        print("1/5 Creating success rate analysis...")
        figures['success_rates'] = self.create_success_rate_analysis()
        
        print("2/5 Creating error trend analysis...")
        figures['error_trends'] = self.create_error_trend_analysis()
        
        print("3/5 Creating energy consumption analysis...")
        figures['energy_consumption'] = self.create_energy_consumption_analysis()
        
        print("4/5 Creating trajectory accuracy analysis...")
        figures['trajectory_accuracy'] = self.create_trajectory_accuracy_analysis()
        
        print("5/5 Creating learning curves analysis...")
        figures['learning_curves'] = self.create_learning_curves_analysis()
        
        # Save figures if path provided
        if save_path:
            os.makedirs(save_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for name, fig in figures.items():
                filename = f"{save_path}/{name}_analysis_{timestamp}.png"
                fig.savefig(filename, dpi=300, bbox_inches='tight')
                print(f"💾 Saved {filename}")
        
        print("\n✅ Analysis dashboard complete!")
        print(f"📊 Analyzed {len(self.metrics_data)} training episodes")
        print(f"🎯 Scenarios: {', '.join(self.scenarios)}")
        print(f"🤖 Algorithms: {', '.join(self.algorithms)}")
        
        # Print summary statistics
        self.print_summary_statistics()
        
        return figures
    
    def print_summary_statistics(self):
        """Print comprehensive summary statistics"""
        if not self.metrics_data:
            return
        
        df = pd.DataFrame([asdict(m) for m in self.metrics_data])
        
        print("\n📈 TRAINING SUMMARY STATISTICS")
        print("=" * 50)
        
        # Overall statistics
        print(f"Total Episodes Analyzed: {len(df)}")
        print(f"Training Scenarios: {', '.join(df['scenario'].unique())}")
        print(f"Algorithms Tested: {', '.join(df['algorithm'].unique())}")
        
        # Performance statistics
        overall_success = df['success'].mean()
        overall_accuracy = df['trajectory_accuracy'].mean()
        overall_error = df['error'].mean()
        
        print(f"\n🎯 OVERALL PERFORMANCE:")
        print(f"  Success Rate: {overall_success:.1%}")
        print(f"  Average Accuracy: {overall_accuracy:.1%}")
        print(f"  Average Error: {overall_error:.3f}")
        
        # Best performing combinations
        best_combo = df.groupby(['scenario', 'algorithm']).agg({
            'success': 'mean',
            'trajectory_accuracy': 'mean',
            'error': 'mean'
        }).sort_values('trajectory_accuracy', ascending=False).head(3)
        
        print(f"\n🏆 TOP PERFORMING COMBINATIONS:")
        for (scenario, algorithm), metrics in best_combo.iterrows():
            print(f"  {algorithm} on {scenario}: {metrics['trajectory_accuracy']:.1%} accuracy, {metrics['success']:.1%} success")
        
        # Learning progress indicators
        if len(df) > 200:
            early_episodes = df.head(100)
            late_episodes = df.tail(100)
            
            accuracy_improvement = late_episodes['trajectory_accuracy'].mean() - early_episodes['trajectory_accuracy'].mean()
            error_improvement = early_episodes['error'].mean() - late_episodes['error'].mean()
            
            print(f"\n📚 LEARNING PROGRESS:")
            print(f"  Accuracy Improvement: {accuracy_improvement:+.1%}")
            print(f"  Error Reduction: {error_improvement:+.3f}")
        
        print("=" * 50)


def main():
    """Main function for standalone execution"""
    print("🚀 RL Training Analysis Module")
    print("==============================")
    
    # Create analyzer instance
    analyzer = RLTrainingAnalyzer()
    
    # Try to load real data, fallback to synthetic
    try:
        # In a real scenario, this would load from the actual RL training data
        print("📁 Attempting to load training data...")
        analyzer.load_data("rl_training_data.json")
    except:
        print("🎲 Generating synthetic demonstration data...")
        analyzer.generate_synthetic_data(num_episodes=500)
    
    # Create comprehensive analysis dashboard
    figures = analyzer.create_comprehensive_dashboard(save_path="analysis_results")
    
    # Display all figures
    plt.show()

if __name__ == "__main__":
    main()