"""
Weights & Biases Integration for Robust MM Control
Provides comprehensive logging and monitoring for RL experiments

Usage:
    from wandb_integration import WandBLogger
    
    logger = WandBLogger(
        project="robust_mm_control",
        phase="phase_04",
        experiment="trajectory_aware_3waypoints"
    )
    
    # In training loop
    logger.log_training_step(episode, metrics_dict)
    
    # After testing
    logger.log_test_results(scenario, intensity, results_dict)
"""

import wandb
import numpy as np
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import torch


class WandBLogger:
    """
    Comprehensive logging for RL experiments using Weights & Biases.
    """
    
    def __init__(self, project="robust_mm_control", phase="phase_04", 
                 experiment="baseline", config=None, tags=None):
        """
        Initialize W&B logger.
        
        Args:
            project: W&B project name
            phase: Current phase (e.g., "phase_04", "phase_05")
            experiment: Experiment name (e.g., "trajectory_aware_3waypoints")
            config: Dictionary of hyperparameters and configuration
            tags: List of tags for organizing runs
        """
        self.project = project
        self.phase = phase
        self.experiment = experiment
        
        # Generate run name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"{phase}_{experiment}_{timestamp}"
        
        # Default tags
        if tags is None:
            tags = [phase, experiment]
        
        # Initialize W&B
        wandb.init(
            project=project,
            name=run_name,
            config=config or {},
            tags=tags,
            reinit=True  # Allow multiple runs in same script
        )
        
        print(f"✅ W&B initialized: {project}/{run_name}")
        print(f"📊 Dashboard: {wandb.run.get_url()}")
        
    def log_training_step(self, episode, metrics):
        """
        Log metrics for a single training episode.
        
        Args:
            episode: Episode number
            metrics: Dictionary of metrics to log
                Expected keys:
                - reward: Episode total reward
                - mean_error: Mean trajectory error
                - max_error: Maximum error
                - episode_length: Number of steps
                - loss: TD loss (if available)
                - q_value_mean: Average Q-value
                - epsilon: Exploration rate
                - ... (any additional metrics)
        """
        log_dict = {'train/episode': episode}
        
        # Add all metrics with train/ prefix
        for key, value in metrics.items():
            if value is not None:
                log_dict[f'train/{key}'] = value
        
        wandb.log(log_dict, step=episode)
    
    def log_test_results(self, scenario, intensity, results):
        """
        Log test results for a specific scenario and intensity.
        
        Args:
            scenario: Scenario name (e.g., "none", "random", "periodic")
            intensity: Intensity type (e.g., "normal", "golden")
            results: Dictionary of test metrics
                Expected keys:
                - mean_error: Mean error across episodes
                - std_error: Standard deviation
                - max_error: Worst case error
                - success_rate: Percentage of successful episodes
                - ... (any additional metrics)
        """
        prefix = f'test/{scenario}_{intensity}'
        log_dict = {}
        
        for key, value in results.items():
            if value is not None:
                log_dict[f'{prefix}/{key}'] = value
        
        wandb.log(log_dict)
    
    def log_phase_summary(self, phase_results):
        """
        Log summary statistics across all scenarios.
        
        Args:
            phase_results: Dictionary with overall phase statistics
                Expected keys:
                - overall_mean_error
                - overall_success_rate
                - best_scenario
                - worst_scenario
                - ... (aggregated metrics)
        """
        log_dict = {}
        for key, value in phase_results.items():
            log_dict[f'summary/{key}'] = value
        
        wandb.log(log_dict)
    
    def log_trajectory_plot(self, actual_trajectory, target_trajectory, 
                           episode, scenario=""):
        """
        Log a 3D trajectory visualization.
        
        Args:
            actual_trajectory: Nx3 array of actual positions
            target_trajectory: Mx3 array of target positions
            episode: Episode number
            scenario: Scenario name (for title)
        """
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot trajectories
        ax.plot(target_trajectory[:, 0], target_trajectory[:, 1], 
                target_trajectory[:, 2], 'g-', label='Target', linewidth=2)
        ax.plot(actual_trajectory[:, 0], actual_trajectory[:, 1], 
                actual_trajectory[:, 2], 'r--', label='Actual', linewidth=1.5)
        
        # Start and end points
        ax.scatter(*target_trajectory[0], c='g', s=100, marker='o', label='Start')
        ax.scatter(*target_trajectory[-1], c='r', s=100, marker='X', label='Goal')
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(f'Trajectory - Episode {episode} - {scenario}')
        ax.legend()
        ax.grid(True)
        
        # Log to W&B
        wandb.log({
            f'trajectory/{scenario}_ep{episode}': wandb.Image(fig)
        })
        plt.close(fig)
    
    def log_error_distribution(self, errors, episode, scenario=""):
        """
        Log error distribution histogram.
        
        Args:
            errors: Array of errors
            episode: Episode number
            scenario: Scenario name
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(errors, bins=30, alpha=0.7, color='blue', edgecolor='black')
        ax.axvline(np.mean(errors), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(errors):.3f}m')
        ax.axvline(np.median(errors), color='green', linestyle='--', 
                   label=f'Median: {np.median(errors):.3f}m')
        ax.set_xlabel('Error (m)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Error Distribution - {scenario}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        wandb.log({
            f'error_dist/{scenario}': wandb.Image(fig)
        })
        plt.close(fig)
    
    def log_q_value_heatmap(self, q_values, actions, episode):
        """
        Log Q-value heatmap across actions.
        
        Args:
            q_values: Array of Q-values for each action
            actions: List of action names
            episode: Episode number
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        im = ax.imshow([q_values], aspect='auto', cmap='RdYlGn')
        ax.set_xticks(range(len(actions)))
        ax.set_xticklabels(actions, rotation=45)
        ax.set_yticks([0])
        ax.set_yticklabels([f'Episode {episode}'])
        plt.colorbar(im, ax=ax, label='Q-value')
        ax.set_title(f'Q-values Across Actions - Episode {episode}')
        
        wandb.log({
            f'q_values/heatmap_ep{episode}': wandb.Image(fig)
        })
        plt.close(fig)
    
    def log_learning_curve(self, episodes, errors, window=100):
        """
        Log smoothed learning curve.
        
        Args:
            episodes: Array of episode numbers
            errors: Array of mean errors per episode
            window: Moving average window size
        """
        # Compute moving average
        if len(errors) >= window:
            smoothed = np.convolve(errors, np.ones(window)/window, mode='valid')
            smooth_episodes = episodes[window-1:]
        else:
            smoothed = errors
            smooth_episodes = episodes
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(episodes, errors, alpha=0.3, color='blue', label='Raw')
        ax.plot(smooth_episodes, smoothed, color='red', linewidth=2, 
                label=f'Moving Avg (window={window})')
        ax.set_xlabel('Episode')
        ax.set_ylabel('Mean Error (m)')
        ax.set_title('Learning Curve')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        wandb.log({
            'learning_curve': wandb.Image(fig)
        })
        plt.close(fig)
    
    def log_model_checkpoint(self, model, episode, metrics=None):
        """
        Save model checkpoint to W&B.
        
        Args:
            model: PyTorch model or path to checkpoint file
            episode: Episode number
            metrics: Dictionary of metrics for this checkpoint
        """
        if isinstance(model, (str, Path)):
            # Path to checkpoint file
            artifact = wandb.Artifact(
                name=f'model_ep{episode}',
                type='model',
                metadata=metrics or {}
            )
            artifact.add_file(str(model))
        else:
            # PyTorch model
            checkpoint_path = f'checkpoint_ep{episode}.pth'
            torch.save(model.state_dict(), checkpoint_path)
            
            artifact = wandb.Artifact(
                name=f'model_ep{episode}',
                type='model',
                metadata=metrics or {}
            )
            artifact.add_file(checkpoint_path)
        
        wandb.log_artifact(artifact)
        print(f"✅ Model checkpoint saved to W&B (episode {episode})")
    
    def finish(self):
        """Finish W&B run."""
        wandb.finish()
        print("✅ W&B run finished")


# Convenience function for quick setup
def setup_wandb(phase, experiment, config=None):
    """
    Quick setup for W&B logging.
    
    Args:
        phase: Phase name (e.g., "phase_04")
        experiment: Experiment name (e.g., "trajectory_3waypoints")
        config: Configuration dictionary
        
    Returns:
        WandBLogger instance
    """
    return WandBLogger(
        project="robust_mm_control",
        phase=phase,
        experiment=experiment,
        config=config,
        tags=[phase, experiment]
    )


# Example usage
if __name__ == "__main__":
    print("W&B Integration Test")
    print("=" * 50)
    
    # Test setup
    config = {
        'state_dim': 59,
        'action_dim': 10,
        'learning_rate': 0.001,
        'gamma': 0.99,
        'episodes': 10000,
        'state_type': 'trajectory_aware',
        'lookahead_waypoints': 3,
    }
    
    logger = WandBLogger(
        phase="phase_04",
        experiment="test_run",
        config=config,
        tags=["test", "trajectory_aware"]
    )
    
    # Simulate training
    print("\nSimulating training...")
    for episode in range(1, 11):
        metrics = {
            'reward': np.random.rand() * 100,
            'mean_error': 1.0 - episode * 0.05 + np.random.rand() * 0.1,
            'max_error': 1.5 - episode * 0.03,
            'episode_length': 150 + np.random.randint(-20, 20),
            'loss': np.random.rand() * 0.5,
            'q_value_mean': 10 + np.random.rand() * 5,
            'epsilon': 1.0 - episode * 0.09,
        }
        logger.log_training_step(episode, metrics)
        print(f"  Episode {episode}: error={metrics['mean_error']:.3f}m")
    
    # Simulate testing
    print("\nSimulating testing...")
    test_results = {
        'mean_error': 0.65,
        'std_error': 0.08,
        'max_error': 0.95,
        'success_rate': 100.0,
    }
    logger.log_test_results('none', 'normal', test_results)
    
    logger.finish()
    print("\n✅ Test complete! Check your W&B dashboard.")
