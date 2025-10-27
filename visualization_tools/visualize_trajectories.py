"""
Trajectory Visualization Tool

Visualize different trajectories before training.
Shows 3D plot of waypoints and path.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from trajectory_generators import TrajectoryGenerator

def plot_trajectory(trajectory, title="Trajectory", show_arrows=False):
    """
    Plot a 3D trajectory.
    
    Args:
        trajectory: List of waypoints [(x,y,z,rx,ry,rz), ...]
        title: Plot title
        show_arrows: Whether to show orientation arrows
    """
    trajectory = np.array(trajectory)
    
    fig = plt.figure(figsize=(12, 5))
    
    # 3D view
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], 
             'b-', linewidth=2, label='Path')
    ax1.scatter(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], 
                c=range(len(trajectory)), cmap='viridis', s=50, label='Waypoints')
    
    # Mark start and end
    ax1.scatter(trajectory[0, 0], trajectory[0, 1], trajectory[0, 2], 
                c='green', s=200, marker='o', label='Start')
    ax1.scatter(trajectory[-1, 0], trajectory[-1, 1], trajectory[-1, 2], 
                c='red', s=200, marker='X', label='End')
    
    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Y (m)')
    ax1.set_zlabel('Z (m)')
    ax1.set_title(f'{title} - 3D View')
    ax1.legend()
    ax1.grid(True)
    
    # Top-down view (XY plane)
    ax2 = fig.add_subplot(122)
    ax2.plot(trajectory[:, 0], trajectory[:, 1], 'b-', linewidth=2)
    ax2.scatter(trajectory[:, 0], trajectory[:, 1], 
                c=range(len(trajectory)), cmap='viridis', s=50)
    ax2.scatter(trajectory[0, 0], trajectory[0, 1], 
                c='green', s=200, marker='o', label='Start')
    ax2.scatter(trajectory[-1, 0], trajectory[-1, 1], 
                c='red', s=200, marker='X', label='End')
    
    # Add waypoint numbers
    for i in range(0, len(trajectory), max(1, len(trajectory)//10)):
        ax2.annotate(f'{i}', (trajectory[i, 0], trajectory[i, 1]), 
                    fontsize=8, ha='center')
    
    ax2.set_xlabel('X (m)')
    ax2.set_ylabel('Y (m)')
    ax2.set_title(f'{title} - Top View (XY)')
    ax2.legend()
    ax2.grid(True)
    ax2.axis('equal')
    
    plt.tight_layout()
    plt.show()

def compare_trajectories(trajectories, titles):
    """
    Compare multiple trajectories side by side.
    
    Args:
        trajectories: List of trajectory arrays
        titles: List of trajectory names
    """
    fig = plt.figure(figsize=(15, 5))
    
    for idx, (traj, title) in enumerate(zip(trajectories, titles)):
        traj = np.array(traj)
        ax = fig.add_subplot(1, len(trajectories), idx+1, projection='3d')
        
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 'b-', linewidth=2)
        ax.scatter(traj[:, 0], traj[:, 1], traj[:, 2], 
                  c=range(len(traj)), cmap='viridis', s=30)
        ax.scatter(traj[0, 0], traj[0, 1], traj[0, 2], 
                  c='green', s=100, marker='o')
        ax.scatter(traj[-1, 0], traj[-1, 1], traj[-1, 2], 
                  c='red', s=100, marker='X')
        
        ax.set_xlabel('X (m)', fontsize=8)
        ax.set_ylabel('Y (m)', fontsize=8)
        ax.set_zlabel('Z (m)', fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.grid(True)
    
    plt.tight_layout()
    plt.show()

def print_trajectory_stats(trajectory, name="Trajectory"):
    """Print statistics about a trajectory."""
    trajectory = np.array(trajectory)
    
    print(f"\n{'='*60}")
    print(f"{name} Statistics")
    print(f"{'='*60}")
    print(f"Number of waypoints: {len(trajectory)}")
    print(f"\nPosition ranges:")
    print(f"  X: [{trajectory[:, 0].min():.3f}, {trajectory[:, 0].max():.3f}] m")
    print(f"  Y: [{trajectory[:, 1].min():.3f}, {trajectory[:, 1].max():.3f}] m")
    print(f"  Z: [{trajectory[:, 2].min():.3f}, {trajectory[:, 2].max():.3f}] m")
    
    # Calculate path length
    distances = np.linalg.norm(np.diff(trajectory[:, :3], axis=0), axis=1)
    total_length = np.sum(distances)
    print(f"\nTotal path length: {total_length:.3f} m")
    print(f"Average segment length: {np.mean(distances):.3f} m")
    print(f"Max segment length: {np.max(distances):.3f} m")
    
    # Check workspace limits (safe zone)
    safe_x = (-0.5, 0.8)
    safe_y = (-0.5, 0.5)
    safe_z = (0.3, 1.2)
    
    x_ok = np.all((trajectory[:, 0] >= safe_x[0]) & (trajectory[:, 0] <= safe_x[1]))
    y_ok = np.all((trajectory[:, 1] >= safe_y[0]) & (trajectory[:, 1] <= safe_y[1]))
    z_ok = np.all((trajectory[:, 2] >= safe_z[0]) & (trajectory[:, 2] <= safe_z[1]))
    
    print(f"\nWorkspace check:")
    print(f"  X within safe zone {safe_x}: {'✅' if x_ok else '❌'}")
    print(f"  Y within safe zone {safe_y}: {'✅' if y_ok else '❌'}")
    print(f"  Z within safe zone {safe_z}: {'✅' if z_ok else '❌'}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    print("\n🎨 Trajectory Visualization Tool\n")
    
    # Create generator
    traj_gen = TrajectoryGenerator(base_height=0.8, base_center=(0.0, 0.0))
    
    # ========================================
    # OPTION 1: Visualize single trajectory
    # ========================================
    print("Generating Figure-8 trajectory...")
    traj = traj_gen.generate_figure8(num_points=20, scale_x=0.3, scale_y=0.2)
    print_trajectory_stats(traj, "Figure-8")
    plot_trajectory(traj, "Figure-8 Trajectory")
    
    # ========================================
    # OPTION 2: Compare multiple trajectories
    # ========================================
    print("\nGenerating multiple trajectories for comparison...")
    
    trajectories = [
        traj_gen.generate_figure8(num_points=20),
        traj_gen.generate_circle(num_points=20, radius=0.3),
        traj_gen.generate_square(num_points=20, side_length=0.4),
        traj_gen.generate_helix(num_points=30, radius=0.25, height_range=0.4, turns=2),
    ]
    
    titles = ["Figure-8", "Circle", "Square", "Helix"]
    
    compare_trajectories(trajectories, titles)
    
    # ========================================
    # OPTION 3: Test your custom trajectory
    # ========================================
    # Uncomment to test your own trajectory:
    # custom_waypoints = [
    #     (0.3, 0.0, 0.7),
    #     (0.4, 0.1, 0.8),
    #     (0.3, 0.2, 0.9),
    #     (0.2, 0.1, 0.8),
    #     (0.3, 0.0, 0.7),
    # ]
    # custom_traj = traj_gen.generate_custom(custom_waypoints)
    # print_trajectory_stats(custom_traj, "Custom Trajectory")
    # plot_trajectory(custom_traj, "Custom Trajectory")
    
    print("\n✅ Visualization complete!")
    print("\nNext steps:")
    print("1. Choose a trajectory you like")
    print("2. Update rl_trajectory_planner.py line ~861")
    print("3. Run training: python3 sim_husky_kuka.py")
    print("4. Press 't' to start RL training\n")
