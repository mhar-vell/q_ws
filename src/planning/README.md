# Planning Module

Trajectory planning and generation for Husky-KUKA mobile manipulator navigation.

## Files

### `rl_trajectory_planner.py` - Main Trajectory Planner
**Purpose**: High-level trajectory planning interface with multiple planning strategies.

**Features**:
- 🗺️ Multiple planning algorithms (RRT, A*, gradient descent)
- 🔄 Adaptive replanning on failure
- 🛡️ Obstacle avoidance integration
- 📈 Path smoothing and optimization
- 🎯 Goal-oriented motion primitives
- 📊 Performance metrics tracking

**Usage**:
```python
from planning.rl_trajectory_planner import TrajectoryPlanner

# Create planner
planner = TrajectoryPlanner(
    workspace_bounds=[[-5, 5], [-5, 5], [0, 2]],
    planning_algorithm='rrt'
)

# Plan trajectory
start = [0.0, 0.0, 0.5]  # [x, y, z]
goal = [2.0, 1.5, 0.5]
trajectory = planner.plan(start, goal, obstacles)

# Execute trajectory
for waypoint in trajectory:
    robot.move_to(waypoint)
```

**Key Classes**:

#### `TrajectoryPlanner`
Main planning interface.

**Methods**:
```python
def plan(start, goal, obstacles=None):
    """Generate trajectory from start to goal"""
    
def replan(current_pos, goal, failed_trajectory):
    """Replan when original trajectory fails"""
    
def smooth_path(waypoints):
    """Apply smoothing to reduce jerkiness"""
    
def validate_trajectory(trajectory, obstacles):
    """Check trajectory for collisions"""
```

**Planning Algorithms**:
1. **RRT (Rapidly-exploring Random Tree)**
   - Best for: Complex obstacle environments
   - Speed: Medium (adaptive sampling)
   - Optimality: Suboptimal (can use RRT*)
   
2. **A* (A-Star)**
   - Best for: Grid-based planning, known maps
   - Speed: Fast (with good heuristic)
   - Optimality: Optimal (with admissible heuristic)
   
3. **Gradient Descent**
   - Best for: Simple environments, local planning
   - Speed: Very fast
   - Optimality: Local optimum only

**Example - RRT Planning**:
```python
planner = TrajectoryPlanner(planning_algorithm='rrt')
planner.set_rrt_params(
    max_iterations=5000,
    step_size=0.1,
    goal_bias=0.1
)

trajectory = planner.plan(start, goal, obstacles)
```

---

### `trajectory_generators.py` - Motion Primitives
**Purpose**: Low-level trajectory generation using motion primitives.

**Features**:
- 🎯 Goal-directed motion primitives
- 🌀 Smooth interpolation (cubic splines)
- ⚙️ Velocity profile generation
- 🔧 Time-optimal trajectories
- 📐 Minimum-jerk trajectories

**Key Functions**:

#### Motion Primitives

```python
def generate_straight_line(start, goal, steps=100):
    """Generate straight-line trajectory"""
    waypoints = np.linspace(start, goal, steps)
    return waypoints

def generate_circular_arc(center, radius, start_angle, end_angle, steps=100):
    """Generate circular arc trajectory"""
    angles = np.linspace(start_angle, end_angle, steps)
    waypoints = center + radius * [np.cos(angles), np.sin(angles)]
    return waypoints

def generate_bezier_curve(control_points, steps=100):
    """Generate smooth Bezier curve"""
    t = np.linspace(0, 1, steps)
    waypoints = compute_bezier(control_points, t)
    return waypoints
```

#### Interpolation Methods

```python
def cubic_spline_interpolation(waypoints, num_samples=1000):
    """Smooth trajectory using cubic splines"""
    from scipy.interpolate import CubicSpline
    
    # Create spline for each dimension
    cs_x = CubicSpline(range(len(waypoints)), waypoints[:, 0])
    cs_y = CubicSpline(range(len(waypoints)), waypoints[:, 1])
    cs_z = CubicSpline(range(len(waypoints)), waypoints[:, 2])
    
    # Sample smooth trajectory
    t = np.linspace(0, len(waypoints)-1, num_samples)
    smooth_traj = np.column_stack([cs_x(t), cs_y(t), cs_z(t)])
    return smooth_traj

def minimum_jerk_trajectory(start, goal, duration, timestep=0.01):
    """Generate minimum-jerk trajectory (human-like motion)"""
    t = np.arange(0, duration, timestep)
    tau = t / duration  # Normalized time
    
    # Minimum-jerk profile
    s = 10*tau**3 - 15*tau**4 + 6*tau**5
    
    # Apply to each dimension
    trajectory = start + (goal - start) * s[:, np.newaxis]
    return trajectory
```

#### Velocity Profiles

```python
def trapezoidal_velocity_profile(distance, max_vel, max_accel):
    """Generate trapezoidal velocity profile"""
    # Acceleration phase
    t_accel = max_vel / max_accel
    d_accel = 0.5 * max_accel * t_accel**2
    
    # Check if we reach max velocity
    if 2*d_accel <= distance:
        # Cruise phase exists
        d_cruise = distance - 2*d_accel
        t_cruise = d_cruise / max_vel
        t_decel = t_accel
    else:
        # Triangle profile (no cruise)
        t_accel = np.sqrt(distance / max_accel)
        t_cruise = 0
        t_decel = t_accel
        max_vel = max_accel * t_accel
    
    return {
        'accel_time': t_accel,
        'cruise_time': t_cruise,
        'decel_time': t_decel,
        'max_velocity': max_vel
    }

def generate_velocity_profile(trajectory, max_vel=1.0, max_accel=0.5):
    """Generate velocity profile for trajectory"""
    distances = np.linalg.norm(np.diff(trajectory, axis=0), axis=1)
    total_distance = np.sum(distances)
    
    profile = trapezoidal_velocity_profile(total_distance, max_vel, max_accel)
    
    # Sample velocities at waypoints
    velocities = []
    # ... (implementation)
    
    return velocities
```

#### Time Parameterization

```python
def time_optimal_parameterization(waypoints, vel_limits, accel_limits):
    """Find time-optimal parameterization respecting constraints"""
    # Use dynamic programming or convex optimization
    # to find fastest feasible parameterization
    
    # For each segment
    for i in range(len(waypoints) - 1):
        segment_length = np.linalg.norm(waypoints[i+1] - waypoints[i])
        
        # Compute minimum time for segment
        min_time = compute_min_time(
            segment_length,
            vel_limits,
            accel_limits
        )
        
        # Add timestamps
        times.append(current_time + min_time)
        current_time += min_time
    
    return times
```

---

## Planning Strategies

### 1. Sampling-Based Planning (RRT)

**When to Use**:
- Complex obstacle environments
- High-dimensional state spaces
- No prior map knowledge

**Implementation**:
```python
class RRTPlanner:
    def __init__(self, start, goal, obstacles, bounds):
        self.tree = Tree(start)
        self.goal = goal
        self.obstacles = obstacles
        self.bounds = bounds
        
    def plan(self, max_iterations=5000, step_size=0.1):
        for i in range(max_iterations):
            # Sample random point
            random_point = self.sample_random_point()
            
            # Find nearest node in tree
            nearest = self.tree.find_nearest(random_point)
            
            # Extend towards random point
            new_node = self.extend(nearest, random_point, step_size)
            
            # Check collision
            if not self.collides(nearest, new_node):
                self.tree.add_node(new_node, parent=nearest)
                
                # Check if goal reached
                if self.distance(new_node, self.goal) < threshold:
                    return self.extract_path(new_node)
        
        return None  # Planning failed
```

### 2. Graph Search (A*)

**When to Use**:
- Grid-based environments
- Known maps
- Optimal paths required

**Implementation**:
```python
def astar_plan(start, goal, grid, heuristic='euclidean'):
    open_set = PriorityQueue()
    open_set.put((0, start))
    
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    
    while not open_set.empty():
        current = open_set.get()[1]
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for neighbor in get_neighbors(current, grid):
            tentative_g = g_score[current] + distance(current, neighbor)
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                open_set.put((f_score[neighbor], neighbor))
    
    return None  # No path found
```

### 3. Optimization-Based Planning

**When to Use**:
- Smooth trajectories required
- Known dynamics
- Real-time replanning

**Implementation**:
```python
def gradient_descent_plan(start, goal, obstacles, learning_rate=0.01):
    trajectory = initialize_trajectory(start, goal)
    
    for iteration in range(max_iterations):
        # Compute gradient of cost function
        gradient = compute_gradient(trajectory, goal, obstacles)
        
        # Update trajectory
        trajectory -= learning_rate * gradient
        
        # Project to constraints
        trajectory = project_to_constraints(trajectory)
        
        # Check convergence
        if np.linalg.norm(gradient) < tolerance:
            break
    
    return trajectory
```

---

## Integration with RL

### RL-Assisted Planning

The planner can use RL to learn better heuristics or adapt to disturbances:

```python
class RLTrajectoryPlanner:
    def __init__(self, rl_agent):
        self.agent = rl_agent
        self.planner = TrajectoryPlanner()
        
    def plan_with_rl(self, start, goal, environment_state):
        # Get RL agent's suggested waypoints
        rl_waypoints = self.agent.suggest_waypoints(
            start, goal, environment_state
        )
        
        # Use traditional planner to connect waypoints
        trajectory = []
        for i in range(len(rl_waypoints) - 1):
            segment = self.planner.plan(
                rl_waypoints[i],
                rl_waypoints[i+1]
            )
            trajectory.extend(segment)
        
        return trajectory
```

### Dynamic Replanning

When disturbances occur, use RL to decide whether to replan:

```python
def adaptive_execution(trajectory, rl_agent):
    for i, waypoint in enumerate(trajectory):
        # Execute waypoint
        actual_pos = robot.move_to(waypoint)
        
        # Check deviation
        error = np.linalg.norm(actual_pos - waypoint)
        
        # Use RL to decide: continue or replan?
        state = get_current_state()
        should_replan = rl_agent.decide_replan(state, error)
        
        if should_replan:
            # Replan from current position
            new_trajectory = planner.plan(actual_pos, goal)
            trajectory = new_trajectory
            i = 0  # Restart from beginning of new plan
```

---

## Usage Examples

### Example 1: Simple Point-to-Point

```python
from planning.trajectory_generators import generate_straight_line

start = [0.0, 0.0, 0.5]
goal = [2.0, 1.5, 0.5]

trajectory = generate_straight_line(start, goal, steps=100)

# Execute
for waypoint in trajectory:
    robot.move_to(waypoint)
```

### Example 2: Smooth Curved Path

```python
from planning.trajectory_generators import (
    generate_bezier_curve,
    cubic_spline_interpolation
)

# Define control points
control_points = [
    [0.0, 0.0, 0.5],  # Start
    [1.0, 1.0, 0.7],  # Intermediate
    [2.0, 0.5, 0.5]   # Goal
]

# Generate Bezier curve
coarse_traj = generate_bezier_curve(control_points, steps=20)

# Smooth with splines
smooth_traj = cubic_spline_interpolation(coarse_traj, num_samples=200)
```

### Example 3: RRT in Obstacle Environment

```python
from planning.rl_trajectory_planner import TrajectoryPlanner

# Define obstacles (list of [center, radius])
obstacles = [
    ([1.0, 0.5, 0.5], 0.3),
    ([1.5, 1.0, 0.5], 0.4)
]

planner = TrajectoryPlanner(
    workspace_bounds=[[-2, 3], [-2, 3], [0, 2]],
    planning_algorithm='rrt'
)

trajectory = planner.plan(start, goal, obstacles)

if trajectory:
    print(f"Found path with {len(trajectory)} waypoints")
else:
    print("Planning failed - no collision-free path")
```

### Example 4: Time-Optimal Execution

```python
from planning.trajectory_generators import (
    generate_velocity_profile,
    time_optimal_parameterization
)

# Generate geometric path
waypoints = generate_straight_line(start, goal, steps=50)

# Compute time-optimal parameterization
vel_limits = [1.0, 1.0, 0.5]  # [vx_max, vy_max, vz_max]
accel_limits = [0.5, 0.5, 0.3]

times = time_optimal_parameterization(waypoints, vel_limits, accel_limits)

# Execute with timing
for waypoint, time in zip(waypoints, times):
    robot.move_to(waypoint, arrival_time=time)
```

---

## Troubleshooting

### Planning Fails Frequently

**Issue**: RRT cannot find path  
**Solution**: Increase max_iterations or adjust step_size
```python
planner.set_rrt_params(max_iterations=10000, step_size=0.05)
```

### Trajectory Too Jerky

**Issue**: Large velocity changes between waypoints  
**Solution**: Apply smoothing and velocity profiling
```python
smooth_traj = cubic_spline_interpolation(trajectory, num_samples=500)
velocities = generate_velocity_profile(smooth_traj, max_vel=0.8)
```

### Collisions During Execution

**Issue**: Trajectory intersects obstacles  
**Solution**: Validate trajectory and increase safety margin
```python
if not planner.validate_trajectory(trajectory, obstacles, margin=0.1):
    trajectory = planner.replan(current_pos, goal)
```

### Slow Planning Time

**Issue**: A* takes too long on large grids  
**Solution**: Use coarser grid or switch to RRT
```python
# Reduce grid resolution
planner = TrajectoryPlanner(
    planning_algorithm='astar',
    grid_resolution=0.2  # Instead of 0.05
)
```

---

## Related Documentation

- **Main Source README**: `../README.md`
- **Simulation Module**: `../simulation/README.md`
- **Config Module**: `../config/README.md`
- **RL Training Guides**: `/home/marcoreis/robust_mm_control_ws/documentation/training_guides/`

---

**Last Updated**: November 2, 2025  
**Module**: `/home/marcoreis/robust_mm_control_ws/src/planning`  
**Status**: Documented ✅
