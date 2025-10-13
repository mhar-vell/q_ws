# 🎯 Custom Trajectory Guide

## Quick Start: Change Your Trajectory

### Step 1: Open the trajectory planner
```bash
code rl_trajectory_planner.py
```

### Step 2: Find line ~861 (the `_generate_sample_trajectory` method)

### Step 3: Uncomment the trajectory you want!

```python
# Option 1: Figure-8 (DEFAULT - currently active)
trajectory = traj_gen.generate_figure8(num_points=20, scale_x=0.3, scale_y=0.2)

# Option 2: Circle
# trajectory = traj_gen.generate_circle(num_points=20, radius=0.3, orientation='horizontal')

# Option 3: Square
# trajectory = traj_gen.generate_square(num_points=20, side_length=0.4)

# ... etc
```

**Just comment out the current one and uncomment another!**

---

## Available Trajectories

### 1. 🔄 Figure-8 (Infinity Symbol)
```python
trajectory = traj_gen.generate_figure8(
    num_points=20,      # Number of waypoints
    scale_x=0.3,        # Width (meters)
    scale_y=0.2         # Height (meters)
)
```

**Visualization:**
```
     ∞
   ←→ 0.3m
   ↕ 0.2m
   
Good for: Testing smooth curves, continuous motion
```

---

### 2. ⭕ Circle
```python
trajectory = traj_gen.generate_circle(
    num_points=20,
    radius=0.3,
    orientation='horizontal'  # or 'vertical_xz', 'vertical_yz'
)
```

**Orientations:**
- `'horizontal'`: Circle in XY plane (like looking down at a plate)
- `'vertical_xz'`: Circle in XZ plane (like a ferris wheel facing you)
- `'vertical_yz'`: Circle in YZ plane (like a ferris wheel from the side)

**Visualization:**
```
horizontal:        vertical_xz:       vertical_yz:
    ●●●                 ●               ●●●
  ●     ●             ●   ●           ●     ●
 ●       ●           ●     ●         ●       ●
  ●     ●             ●   ●           ●     ●
    ●●●                 ●               ●●●

Good for: Circular inspection, uniform velocity testing
```

---

### 3. ⬛ Square
```python
trajectory = traj_gen.generate_square(
    num_points=20,
    side_length=0.4
)
```

**Visualization:**
```
  0.4m
  ←→
  ●―――●
  │   │
  │   │ 0.4m
  ●―――●

Good for: Testing sharp corners, position accuracy
```

---

### 4. 🌀 Helix (Spiral)
```python
trajectory = traj_gen.generate_helix(
    num_points=30,
    radius=0.25,
    height_range=0.4,
    turns=2
)
```

**Visualization:**
```
      ●
     ●  ●    ← 0.4m height
    ●    ●
   ●      ●
  ●        ●
 ●          ●
●            ● ← Start

Good for: 3D motion, vertical reach testing
```

---

### 5. ─ Straight Line
```python
trajectory = traj_gen.generate_line(
    start_point=(0.2, 0.0, 0.6),
    end_point=(0.5, 0.3, 1.0),
    num_points=15
)
```

**Visualization:**
```
                  ● End (0.5, 0.3, 1.0)
                 /
                /
               /
              /
             ● Start (0.2, 0.0, 0.6)

Good for: Point-to-point motion, speed testing
```

---

### 6. 〰️ Sine Wave
```python
trajectory = traj_gen.generate_sine_wave(
    num_points=20,
    amplitude=0.15,
    wavelength=0.6,
    axis='x'  # or 'y'
)
```

**Visualization:**
```
       ●
      ● ●
     ●   ●
    ●     ●
   ●       ●     
  ●         ●
 ●           ●
●             ●

Good for: Smooth periodic motion, tracking accuracy
```

---

### 7. ⭐ Star
```python
trajectory = traj_gen.generate_star(
    num_points=25,
    outer_radius=0.3,
    inner_radius=0.15,
    num_tips=5
)
```

**Visualization:**
```
       ●
      ● ●
     ●   ●
  ●   ●●●   ●
 ● ●       ● ●
●   ●●● ●●●   ●

Good for: Complex shapes, variable radius motion
```

---

### 8. 📦 Pick and Place
```python
trajectory = traj_gen.generate_pick_and_place(
    pick_pos=(0.4, 0.2, 0.5),
    place_pos=(0.4, -0.2, 0.5),
    approach_height=0.15
)
```

**Visualization:**
```
Approach → ●     ● ← Approach
           ↓     ↑
   Pick → ●       ● ← Place
         (0.4,0.2) (0.4,-0.2)

Sequence:
1. Move above pick
2. Descend to pick
3. Grasp object
4. Lift object
5. Move above place
6. Descend to place
7. Release object
8. Retract

Good for: Manipulation tasks, real-world applications
```

---

### 9. ✏️ Custom Waypoints
```python
custom_waypoints = [
    (0.3, 0.0, 0.7),    # Point 1
    (0.4, 0.1, 0.8),    # Point 2
    (0.3, 0.2, 0.9),    # Point 3
    (0.2, 0.1, 0.8),    # Point 4
    (0.3, 0.0, 0.7),    # Back to start
]
trajectory = traj_gen.generate_custom(custom_waypoints)
```

**Good for: Your own specific paths!**

---

## 🎨 Combining Trajectories

You can create multi-phase trajectories:

```python
from trajectory_generators import TrajectoryGenerator

traj_gen = TrajectoryGenerator(base_height=0.8)

# Phase 1: Circle
traj1 = traj_gen.generate_circle(num_points=10, radius=0.2)

# Phase 2: Move to new location
traj_gen.base_center = (0.3, 0.3)  # Change center

# Phase 3: Square at new location
traj2 = traj_gen.generate_square(num_points=12, side_length=0.3)

# Combine
full_trajectory = traj1 + traj2
```

---

## 🔧 Parameter Tuning Guide

### Number of Waypoints
- **Few (10-15)**: Faster training, less precise
- **Medium (20-30)**: Balanced (recommended)
- **Many (40+)**: High precision, slower training

### Size/Scale
- **Small (0.1-0.2m)**: Fine motor control, high precision
- **Medium (0.3-0.4m)**: Standard reach, good balance
- **Large (0.5m+)**: Tests workspace limits

### Height
- **Low (0.5-0.6m)**: Easy to reach, less arm extension
- **Medium (0.7-0.9m)**: Standard working height
- **High (1.0m+)**: Tests vertical reach

---

## 🚀 Quick Examples

### Example 1: Large Circle for Speed Testing
```python
trajectory = traj_gen.generate_circle(
    num_points=30,
    radius=0.5,  # Large radius
    orientation='horizontal'
)
```

### Example 2: Tight Figure-8 for Precision
```python
trajectory = traj_gen.generate_figure8(
    num_points=40,      # Many waypoints
    scale_x=0.15,       # Small width
    scale_y=0.10        # Small height
)
```

### Example 3: Vertical Inspection Path
```python
trajectory = traj_gen.generate_helix(
    num_points=50,
    radius=0.2,
    height_range=0.6,   # Large vertical range
    turns=3             # Multiple rotations
)
```

### Example 4: Fast Pick-Place Test
```python
trajectory = traj_gen.generate_pick_and_place(
    pick_pos=(0.5, 0.3, 0.4),
    place_pos=(0.5, -0.3, 0.4),
    approach_height=0.1  # Low approach for speed
)
```

---

## 📊 Testing Your Trajectory

After changing the trajectory:

1. **Visualize it** (optional):
```bash
python3 trajectory_generators.py
```

2. **Run the simulation**:
```bash
python3 sim_husky_kuka.py
```

3. **Start training**:
   - Press **'t'** in the PyBullet window
   - Watch the robot follow your new trajectory!

4. **Check metrics**:
   - Success rate (should be >70% after 2000 episodes)
   - Final error (should be <0.01m)
   - Steps taken (fewer = more efficient)

---

## 💡 Tips for Creating Good Trajectories

### ✅ Do:
- Start simple (circle, line) before complex shapes
- Keep waypoints within robot's reachable workspace
- Use ~20 waypoints for balanced learning
- Test trajectory without disturbances first
- Gradually increase difficulty

### ❌ Don't:
- Create trajectories too far from robot (>0.8m reach)
- Use too few waypoints (<10) - makes learning hard
- Put waypoints below workspace (z < 0.3m)
- Make sudden large jumps between waypoints
- Forget to test in simulation first

---

## 🎯 Workspace Limits

Safe working zone for Husky+KUKA:

```
X: -0.5 to +0.8m (forward/back from base)
Y: -0.5 to +0.5m (left/right from base)
Z: +0.3 to +1.2m (height above ground)

Recommended zone (easier to reach):
X: 0.0 to +0.6m
Y: -0.4 to +0.4m
Z: 0.5 to 1.0m
```

---

## Need Help?

1. **Trajectory not reachable?**
   - Reduce size/scale
   - Move center closer to (0, 0)
   - Lower/raise height

2. **Training not converging?**
   - Simplify trajectory (fewer waypoints)
   - Increase training episodes
   - Check reward function

3. **Want to create a custom shape?**
   - Use the `generate_custom()` function
   - Define your waypoints manually
   - Or combine existing trajectories

Happy trajectory planning! 🎉
