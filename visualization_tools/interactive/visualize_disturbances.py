"""
Disturbance Pattern Visualizer

Visualize the five disturbance scenarios to understand
what forces your robot will experience during training.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def generate_random_disturbance(timesteps):
    """Random forces at each timestep."""
    forces = np.random.uniform(-50, 50, timesteps)
    return forces

def generate_periodic_disturbance(timesteps):
    """Large impulses every 50 timesteps."""
    forces = np.zeros(timesteps)
    for i in range(0, timesteps, 50):
        forces[i] = np.random.choice([-100, 100])
    return forces

def generate_continuous_disturbance(timesteps):
    """Small continuous forces."""
    forces = np.random.uniform(-10, 10, timesteps)
    return forces

def generate_impulse_disturbance(timesteps):
    """Single large shock at timestep 25."""
    forces = np.zeros(timesteps)
    forces[25] = np.random.choice([-200, 200])
    return forces

def visualize_all_disturbances():
    """Create comprehensive disturbance visualization."""
    timesteps = 200
    time = np.arange(timesteps)
    
    # Generate all disturbance patterns
    none = np.zeros(timesteps)
    random_dist = generate_random_disturbance(timesteps)
    periodic = generate_periodic_disturbance(timesteps)
    continuous = generate_continuous_disturbance(timesteps)
    impulse = generate_impulse_disturbance(timesteps)
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # Define colors and labels
    scenarios = [
        (none, "1. None (Baseline)", "green", gs[0, 0]),
        (random_dist, "2. Random (Chaotic)", "blue", gs[0, 1]),
        (periodic, "3. Periodic (Rhythmic)", "purple", gs[1, 0]),
        (continuous, "4. Continuous (Persistent)", "orange", gs[1, 1]),
        (impulse, "5. Impulse (Shock)", "red", gs[2, 0]),
    ]
    
    for forces, title, color, position in scenarios:
        ax = fig.add_subplot(position)
        ax.plot(time, forces, color=color, linewidth=2, alpha=0.7)
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.3)
        ax.fill_between(time, forces, 0, alpha=0.3, color=color)
        
        ax.set_xlabel('Timestep', fontsize=10)
        ax.set_ylabel('Force (Newtons)', fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-250, 250)
        
        # Add statistics
        rms = np.sqrt(np.mean(forces**2))
        max_force = np.max(np.abs(forces))
        ax.text(0.02, 0.98, f'RMS: {rms:.1f}N\nMax: {max_force:.1f}N',
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=9)
    
    # Add comparison plot
    ax_compare = fig.add_subplot(gs[2, 1])
    ax_compare.plot(time, random_dist, label='Random', color='blue', alpha=0.6, linewidth=1)
    ax_compare.plot(time, periodic, label='Periodic', color='purple', alpha=0.6, linewidth=1)
    ax_compare.plot(time, continuous, label='Continuous', color='orange', alpha=0.6, linewidth=1)
    ax_compare.plot(time, impulse, label='Impulse', color='red', alpha=0.8, linewidth=2)
    ax_compare.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.3)
    ax_compare.set_xlabel('Timestep', fontsize=10)
    ax_compare.set_ylabel('Force (Newtons)', fontsize=10)
    ax_compare.set_title('All Disturbances Overlaid', fontsize=12, fontweight='bold')
    ax_compare.legend(loc='upper right', fontsize=9)
    ax_compare.grid(True, alpha=0.3)
    ax_compare.set_ylim(-250, 250)
    
    plt.suptitle('🌊 Disturbance Scenarios - Force Profiles Over Time', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.show()

def analyze_disturbance_statistics():
    """Print statistical analysis of disturbances."""
    timesteps = 200
    num_runs = 100
    
    print("\n" + "="*70)
    print("📊 DISTURBANCE STATISTICS (100 simulated episodes)")
    print("="*70 + "\n")
    
    scenarios = {
        'None': lambda: np.zeros(timesteps),
        'Random': lambda: generate_random_disturbance(timesteps),
        'Periodic': lambda: generate_periodic_disturbance(timesteps),
        'Continuous': lambda: generate_continuous_disturbance(timesteps),
        'Impulse': lambda: generate_impulse_disturbance(timesteps)
    }
    
    for name, generator in scenarios.items():
        # Run multiple times to get statistics
        all_forces = [generator() for _ in range(num_runs)]
        all_forces = np.array(all_forces)
        
        # Calculate statistics
        rms_values = np.sqrt(np.mean(all_forces**2, axis=1))
        max_values = np.max(np.abs(all_forces), axis=1)
        mean_rms = np.mean(rms_values)
        mean_max = np.mean(max_values)
        
        # Count significant disturbances (> 20N)
        significant_count = np.mean(np.sum(np.abs(all_forces) > 20, axis=1))
        
        # Estimate impact on robot (F = ma, Husky mass ~50kg)
        acceleration = mean_max / 50.0  # m/s²
        
        print(f"🔹 {name:12s}")
        print(f"   RMS Force:           {mean_rms:.1f} ± {np.std(rms_values):.1f} N")
        print(f"   Max Force:           {mean_max:.1f} ± {np.std(max_values):.1f} N")
        print(f"   Significant events:  {significant_count:.1f} / 200 timesteps")
        print(f"   Expected accel:      {acceleration:.2f} m/s²")
        
        # Difficulty assessment
        if mean_rms < 1:
            difficulty = "TRIVIAL ⭐"
        elif mean_rms < 10:
            difficulty = "EASY ⭐⭐"
        elif mean_rms < 30:
            difficulty = "MODERATE ⭐⭐⭐"
        elif mean_rms < 50:
            difficulty = "HARD ⭐⭐⭐⭐"
        else:
            difficulty = "EXTREME ⭐⭐⭐⭐⭐"
        
        print(f"   Difficulty:          {difficulty}")
        print()
    
    print("="*70)
    print("\n💡 Interpretation:")
    print("   • RMS (Root Mean Square): Average 'energy' of disturbance")
    print("   • Max Force: Peak disturbance magnitude")
    print("   • Significant events: Timesteps with forces > 20N")
    print("   • Expected accel: Husky acceleration if force fully applied")
    print("   • Difficulty: Estimated challenge for RL agent\n")

def visualize_robot_response():
    """Simulate and visualize robot response to disturbances."""
    timesteps = 200
    dt = 0.01  # 10ms per timestep
    
    # Robot parameters (Husky UGV)
    mass = 50.0  # kg
    damping = 10.0  # N⋅s/m (wheel friction + air resistance)
    
    # Generate disturbance
    force = generate_random_disturbance(timesteps)
    
    # Simulate dynamics: F - damping*v = m*a
    velocity = np.zeros(timesteps)
    position = np.zeros(timesteps)
    
    for i in range(1, timesteps):
        # Net force = applied force - damping
        net_force = force[i] - damping * velocity[i-1]
        acceleration = net_force / mass
        
        # Update velocity and position (Euler integration)
        velocity[i] = velocity[i-1] + acceleration * dt
        position[i] = position[i-1] + velocity[i] * dt
    
    # Plot response
    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    time = np.arange(timesteps) * dt
    
    # Force
    axes[0].plot(time, force, color='red', linewidth=2)
    axes[0].axhline(y=0, color='black', linestyle='--', alpha=0.3)
    axes[0].set_ylabel('Force (N)', fontsize=11)
    axes[0].set_title('External Disturbance Force', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].fill_between(time, force, 0, alpha=0.3, color='red')
    
    # Acceleration
    acceleration_profile = (force - damping * velocity) / mass
    axes[1].plot(time, acceleration_profile, color='orange', linewidth=2)
    axes[1].axhline(y=0, color='black', linestyle='--', alpha=0.3)
    axes[1].axhline(y=5.0, color='red', linestyle=':', alpha=0.5, label='IMU Threshold')
    axes[1].axhline(y=-5.0, color='red', linestyle=':', alpha=0.5)
    axes[1].set_ylabel('Acceleration (m/s²)', fontsize=11)
    axes[1].set_title('Robot Acceleration (what IMU measures)', fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].fill_between(time, acceleration_profile, 0, alpha=0.3, color='orange')
    
    # Velocity
    axes[2].plot(time, velocity, color='blue', linewidth=2)
    axes[2].axhline(y=0, color='black', linestyle='--', alpha=0.3)
    axes[2].set_ylabel('Velocity (m/s)', fontsize=11)
    axes[2].set_title('Robot Velocity', fontsize=12, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    axes[2].fill_between(time, velocity, 0, alpha=0.3, color='blue')
    
    # Position
    axes[3].plot(time, position, color='green', linewidth=2)
    axes[3].axhline(y=0, color='black', linestyle='--', alpha=0.3, label='Desired path')
    axes[3].set_xlabel('Time (seconds)', fontsize=11)
    axes[3].set_ylabel('Deviation (m)', fontsize=11)
    axes[3].set_title('Robot Position Deviation from Path', fontsize=12, fontweight='bold')
    axes[3].legend()
    axes[3].grid(True, alpha=0.3)
    axes[3].fill_between(time, position, 0, alpha=0.3, color='green')
    
    # Add statistics
    max_deviation = np.max(np.abs(position))
    max_velocity = np.max(np.abs(velocity))
    fig.text(0.02, 0.98, 
             f'Max deviation: {max_deviation:.3f} m\nMax velocity: {max_velocity:.3f} m/s',
             transform=fig.transFigure, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3),
             fontsize=10)
    
    plt.suptitle('🤖 Robot Response to Random Disturbances (Simulated Physics)', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.show()
    
    print(f"\n📊 Simulation Results:")
    print(f"   Max position deviation: {max_deviation:.3f} m")
    print(f"   Max velocity: {max_velocity:.3f} m/s")
    print(f"   RMS position error: {np.sqrt(np.mean(position**2)):.3f} m")
    print(f"\n💡 Without compensation, robot deviates by {max_deviation*100:.1f} cm from path!")
    print(f"   RL training teaches robot to counteract these deviations.\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🌊 DISTURBANCE PATTERN VISUALIZER")
    print("="*70)
    print("\nThis tool helps you understand the disturbances your robot faces")
    print("during training. Choose an option:\n")
    print("  1. Visualize all disturbance patterns")
    print("  2. Show statistical analysis")
    print("  3. Simulate robot response to disturbances")
    print("  4. All of the above")
    print()
    
    choice = input("Enter choice (1-4) or press Enter for default [4]: ").strip()
    
    if not choice:
        choice = "4"
    
    print("\n" + "="*70 + "\n")
    
    if choice in ["1", "4"]:
        print("📈 Generating disturbance visualizations...\n")
        visualize_all_disturbances()
    
    if choice in ["2", "4"]:
        analyze_disturbance_statistics()
    
    if choice in ["3", "4"]:
        print("🤖 Simulating robot dynamics...\n")
        visualize_robot_response()
    
    print("\n✅ Visualization complete!")
    print("\nNext steps:")
    print("1. Review the disturbance patterns above")
    print("2. Adjust parameters in rl_mission_env.py if needed")
    print("3. Start training: python3 sim_husky_kuka.py")
    print("4. Press 't' to begin RL training with disturbances\n")
