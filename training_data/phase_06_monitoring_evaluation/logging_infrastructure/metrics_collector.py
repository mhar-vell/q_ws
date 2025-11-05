"""
Comprehensive Metrics Collection for RL Training
Captures all relevant metrics during training and testing

Usage:
    from metrics_collector import MetricsCollector
    
    collector = MetricsCollector()
    
    # During training episode
    collector.add_step(state, action, reward, q_values)
    metrics = collector.end_episode()
    
    # During testing
    collector.add_test_step(error, ee_pos, target_pos)
    test_metrics = collector.end_test_episode()
"""

import numpy as np
from collections import deque, defaultdict
from datetime import datetime
import json
from pathlib import Path


class MetricsCollector:
    """
    Comprehensive metrics collection for RL experiments.
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.reset()
        
    def reset(self):
        """Reset all episode metrics."""
        # Training metrics
        self.episode_rewards = []
        self.episode_actions = []
        self.episode_q_values = []
        self.episode_losses = []
        self.episode_states = []
        self.episode_errors = []
        
        # Test metrics
        self.test_errors = []
        self.test_positions = []
        self.test_targets = []
        
        # Episode info
        self.episode_start_time = datetime.now()
        
    def add_step(self, state=None, action=None, reward=None, 
                 q_values=None, loss=None, error=None):
        """
        Add metrics for a single training step.
        
        Args:
            state: State vector
            action: Action taken
            reward: Reward received
            q_values: Q-values for all actions
            loss: TD loss (if applicable)
            error: Trajectory error (if applicable)
        """
        if reward is not None:
            self.episode_rewards.append(reward)
        if action is not None:
            self.episode_actions.append(action)
        if q_values is not None:
            self.episode_q_values.append(q_values)
        if loss is not None:
            self.episode_losses.append(loss)
        if state is not None:
            self.episode_states.append(state)
        if error is not None:
            self.episode_errors.append(error)
    
    def add_test_step(self, error, ee_pos=None, target_pos=None):
        """
        Add metrics for a single test step.
        
        Args:
            error: Position error (distance to target)
            ee_pos: End-effector position (x, y, z)
            target_pos: Target position (x, y, z)
        """
        self.test_errors.append(error)
        if ee_pos is not None:
            self.test_positions.append(ee_pos)
        if target_pos is not None:
            self.test_targets.append(target_pos)
    
    def end_episode(self):
        """
        Compute episode summary metrics.
        
        Returns:
            Dictionary of episode metrics
        """
        episode_time = (datetime.now() - self.episode_start_time).total_seconds()
        
        metrics = {
            # Performance
            'reward': np.sum(self.episode_rewards) if self.episode_rewards else 0,
            'mean_error': np.mean(self.episode_errors) if self.episode_errors else None,
            'max_error': np.max(self.episode_errors) if self.episode_errors else None,
            'min_error': np.min(self.episode_errors) if self.episode_errors else None,
            'final_error': self.episode_errors[-1] if self.episode_errors else None,
            'episode_length': len(self.episode_rewards),
            
            # Learning dynamics
            'mean_loss': np.mean(self.episode_losses) if self.episode_losses else None,
            'final_loss': self.episode_losses[-1] if self.episode_losses else None,
            
            # Q-values
            'q_value_mean': np.mean(self.episode_q_values) if self.episode_q_values else None,
            'q_value_std': np.std(self.episode_q_values) if self.episode_q_values else None,
            'q_value_max': np.max(self.episode_q_values) if self.episode_q_values else None,
            'q_value_min': np.min(self.episode_q_values) if self.episode_q_values else None,
            
            # Action statistics
            'action_entropy': self._compute_action_entropy(),
            'most_common_action': self._most_common_action(),
            'action_variance': np.var(self.episode_actions) if self.episode_actions else None,
            
            # State statistics
            'state_norm_mean': self._compute_state_norm_mean(),
            
            # Computational
            'episode_time_seconds': episode_time,
        }
        
        # Reset for next episode
        self.reset()
        
        return metrics
    
    def end_test_episode(self):
        """
        Compute test episode summary metrics.
        
        Returns:
            Dictionary of test metrics
        """
        if not self.test_errors:
            return {}
        
        errors = np.array(self.test_errors)
        
        metrics = {
            # Accuracy
            'mean_error': np.mean(errors),
            'median_error': np.median(errors),
            'std_error': np.std(errors),
            'min_error': np.min(errors),
            'max_error': np.max(errors),
            'p95_error': np.percentile(errors, 95),
            'p99_error': np.percentile(errors, 99),
            
            # Success criteria (threshold: 0.1m)
            'success_rate': np.mean(errors < 0.1) * 100,
            'episode_length': len(errors),
            
            # Trajectory data (for visualization)
            'errors': errors.tolist(),
            'positions': [p.tolist() for p in self.test_positions] if self.test_positions else None,
            'targets': [t.tolist() for t in self.test_targets] if self.test_targets else None,
        }
        
        self.reset()
        return metrics
    
    def _compute_action_entropy(self):
        """Compute entropy of action distribution."""
        if not self.episode_actions:
            return None
        
        actions = np.array(self.episode_actions)
        unique, counts = np.unique(actions, return_counts=True)
        probs = counts / len(actions)
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        return entropy
    
    def _most_common_action(self):
        """Find most frequently taken action."""
        if not self.episode_actions:
            return None
        
        unique, counts = np.unique(self.episode_actions, return_counts=True)
        return int(unique[np.argmax(counts)])
    
    def _compute_state_norm_mean(self):
        """Compute mean L2 norm of states."""
        if not self.episode_states:
            return None
        
        states = np.array(self.episode_states)
        norms = np.linalg.norm(states, axis=1)
        return np.mean(norms)


class MetricsAggregator:
    """
    Aggregate metrics across multiple episodes for analysis.
    """
    
    def __init__(self):
        """Initialize aggregator."""
        self.training_history = defaultdict(list)
        self.test_history = defaultdict(lambda: defaultdict(list))
        
    def add_training_episode(self, episode, metrics):
        """
        Add training episode metrics.
        
        Args:
            episode: Episode number
            metrics: Dictionary of metrics
        """
        self.training_history['episode'].append(episode)
        for key, value in metrics.items():
            if value is not None:
                self.training_history[key].append(value)
    
    def add_test_episode(self, scenario, intensity, metrics):
        """
        Add test episode metrics.
        
        Args:
            scenario: Scenario name
            intensity: Intensity level
            metrics: Dictionary of metrics
        """
        key = f"{scenario}_{intensity}"
        for metric_name, value in metrics.items():
            if value is not None and not isinstance(value, list):
                self.test_history[key][metric_name].append(value)
    
    def get_training_summary(self, window=100):
        """
        Get summary of training progress.
        
        Args:
            window: Window size for moving average
            
        Returns:
            Dictionary of summary statistics
        """
        if not self.training_history['episode']:
            return {}
        
        summary = {}
        
        # Recent performance (last `window` episodes)
        for key in ['reward', 'mean_error', 'mean_loss']:
            if key in self.training_history and self.training_history[key]:
                recent = self.training_history[key][-window:]
                summary[f'recent_{key}_mean'] = np.mean(recent)
                summary[f'recent_{key}_std'] = np.std(recent)
        
        # Overall trends
        if 'mean_error' in self.training_history and self.training_history['mean_error']:
            errors = self.training_history['mean_error']
            summary['initial_error'] = errors[0]
            summary['final_error'] = errors[-1]
            summary['error_improvement'] = (errors[0] - errors[-1]) / errors[0] * 100
        
        # Learning progress
        summary['total_episodes'] = len(self.training_history['episode'])
        
        return summary
    
    def get_test_summary(self):
        """
        Get summary of test results across all scenarios.
        
        Returns:
            Dictionary of test summaries per scenario
        """
        summary = {}
        
        for key, metrics in self.test_history.items():
            scenario_summary = {}
            for metric_name, values in metrics.items():
                if values:
                    scenario_summary[f'{metric_name}_mean'] = np.mean(values)
                    scenario_summary[f'{metric_name}_std'] = np.std(values)
            summary[key] = scenario_summary
        
        return summary
    
    def save_to_json(self, filepath):
        """
        Save all metrics to JSON file.
        
        Args:
            filepath: Path to save JSON file
        """
        data = {
            'training_history': dict(self.training_history),
            'test_history': {k: dict(v) for k, v in self.test_history.items()},
            'training_summary': self.get_training_summary(),
            'test_summary': self.get_test_summary(),
        }
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Metrics saved to {filepath}")
    
    def load_from_json(self, filepath):
        """
        Load metrics from JSON file.
        
        Args:
            filepath: Path to JSON file
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.training_history = defaultdict(list, data['training_history'])
        self.test_history = defaultdict(
            lambda: defaultdict(list),
            {k: defaultdict(list, v) for k, v in data['test_history'].items()}
        )
        
        print(f"✅ Metrics loaded from {filepath}")


# Example usage
if __name__ == "__main__":
    print("Metrics Collector Test")
    print("=" * 50)
    
    # Test training metrics
    collector = MetricsCollector()
    
    print("\nSimulating training episode...")
    for step in range(100):
        collector.add_step(
            state=np.random.rand(35),
            action=np.random.randint(0, 10),
            reward=np.random.rand() * 10,
            q_values=np.random.rand(10),
            loss=np.random.rand(),
            error=1.0 - step * 0.01 + np.random.rand() * 0.1
        )
    
    metrics = collector.end_episode()
    print(f"Episode metrics:")
    for key, value in metrics.items():
        if value is not None:
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")
    
    # Test aggregator
    print("\nTesting aggregator...")
    aggregator = MetricsAggregator()
    
    for episode in range(1, 11):
        metrics = {
            'reward': 100 + episode * 10,
            'mean_error': 1.0 - episode * 0.05,
            'mean_loss': 0.5 - episode * 0.02,
        }
        aggregator.add_training_episode(episode, metrics)
    
    summary = aggregator.get_training_summary()
    print(f"Training summary:")
    for key, value in summary.items():
        print(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")
    
    print("\n✅ Test complete!")
