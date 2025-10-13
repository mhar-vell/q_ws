"""
Custom Trajectory Generators for RL-based Mobile Manipulator

This module provides various trajectory patterns for end-effector path planning.
Each trajectory is defined as a list of waypoints: [(x, y, z, rx, ry, rz), ...]
"""

import numpy as np
import math

class TrajectoryGenerator:
    """Generate various end-effector trajectories for mobile manipulator."""
    
    def __init__(self, base_height=0.8, base_center=(0.0, 0.0)):
        """
        Initialize trajectory generator.
        
        Args:
            base_height: Default Z height for trajectories (meters)
            base_center: Center point for trajectories (x, y) in meters
        """
        self.base_height = base_height
        self.base_center = base_center
    
    def generate_figure8(self, num_points=20, scale_x=0.3, scale_y=0.2):
        """
        Generate figure-8 (infinity symbol) trajectory.
        
        Args:
            num_points: Number of waypoints
            scale_x: Width of figure-8 (meters)
            scale_y: Height of figure-8 (meters)
            
        Returns:
            list: Waypoints [(x, y, z, rx, ry, rz), ...]
        """
        trajectory = []
        
        for i in range(num_points):
            t = 2 * np.pi * i / num_points
            
            # Figure-8 parametric equations
            x = self.base_center[0] + scale_x * np.sin(t)
            y = self.base_center[1] + scale_y * np.sin(2 * t)
            z = self.base_height
            
            # Orientation (pointing down)
            rx, ry, rz = 0, 0, 0
            
            trajectory.append([x, y, z, rx, ry, rz])
        
        print(f"✅ Generated Figure-8 trajectory: {num_points} waypoints, {scale_x}m × {scale_y}m")
        return trajectory
    
    def generate_circle(self, num_points=20, radius=0.3, orientation='horizontal'):
        """
        Generate circular trajectory.
        
        Args:
            num_points: Number of waypoints
            radius: Circle radius (meters)
            orientation: 'horizontal' (XY plane) or 'vertical' (XZ or YZ plane)
            
        Returns:
            list: Waypoints [(x, y, z, rx, ry, rz), ...]
        """
        trajectory = []
        
        for i in range(num_points):
            angle = 2 * np.pi * i / num_points
            
            if orientation == 'horizontal':
                # Circle in XY plane (horizontal)
                x = self.base_center[0] + radius * np.cos(angle)
                y = self.base_center[1] + radius * np.sin(angle)
                z = self.base_height
            elif orientation == 'vertical_xz':
                # Circle in XZ plane (vertical)
                x = self.base_center[0] + radius * np.cos(angle)
                y = self.base_center[1]
                z = self.base_height + radius * np.sin(angle)
            elif orientation == 'vertical_yz':
                # Circle in YZ plane (vertical)
                x = self.base_center[0]
                y = self.base_center[1] + radius * np.cos(angle)
                z = self.base_height + radius * np.sin(angle)
            
            # Orientation
            rx, ry, rz = 0, 0, 0
            
            trajectory.append([x, y, z, rx, ry, rz])
        
        print(f"✅ Generated Circular trajectory: {num_points} waypoints, radius={radius}m, {orientation}")
        return trajectory
    
    def generate_line(self, start_point, end_point, num_points=20):
        """
        Generate straight line trajectory.
        
        Args:
            start_point: Starting position (x, y, z)
            end_point: Ending position (x, y, z)
            num_points: Number of waypoints
            
        Returns:
            list: Waypoints [(x, y, z, rx, ry, rz), ...]
        """
        trajectory = []
        
        start = np.array(start_point)
        end = np.array(end_point)
        
        for i in range(num_points):
            t = i / (num_points - 1)  # 0 to 1
            
            # Linear interpolation
            point = start + t * (end - start)
            x, y, z = point
            
            # Orientation
            rx, ry, rz = 0, 0, 0
            
            trajectory.append([x, y, z, rx, ry, rz])
        
        print(f"✅ Generated Line trajectory: {num_points} waypoints from {start_point} to {end_point}")
        return trajectory
    
    def generate_square(self, num_points=20, side_length=0.4):
        """
        Generate square trajectory.
        
        Args:
            num_points: Number of waypoints (distributed along perimeter)
            side_length: Length of square sides (meters)
            
        Returns:
            list: Waypoints [(x, y, z, rx, ry, rz), ...]
        """
        trajectory = []
        half = side_length / 2
        
        # Four corners of square
        corners = [
            (self.base_center[0] - half, self.base_center[1] - half),  # Bottom-left
            (self.base_center[0] + half, self.base_center[1] - half),  # Bottom-right
            (self.base_center[0] + half, self.base_center[1] + half),  # Top-right
            (self.base_center[0] - half, self.base_center[1] + half),  # Top-left
        ]
        
        points_per_side = num_points // 4
        
        for side in range(4):
            start_corner = corners[side]
            end_corner = corners[(side + 1) % 4]
            
            for i in range(points_per_side):
                t = i / points_per_side
                
                x = start_corner[0] + t * (end_corner[0] - start_corner[0])
                y = start_corner[1] + t * (end_corner[1] - start_corner[1])
                z = self.base_height
                
                rx, ry, rz = 0, 0, 0
                
                trajectory.append([x, y, z, rx, ry, rz])
        
        print(f"✅ Generated Square trajectory: {len(trajectory)} waypoints, {side_length}m sides")
        return trajectory
    
    def generate_helix(self, num_points=30, radius=0.25, height_range=0.4, turns=2):
        """
        Generate helical (spiral) trajectory.
        
        Args:
            num_points: Number of waypoints
            radius: Helix radius (meters)
            height_range: Total vertical range (meters)
            turns: Number of complete rotations
            
        Returns:
            list: Waypoints [(x, y, z, rx, ry, rz), ...]
        """
        trajectory = []
        
        for i in range(num_points):
            t = i / (num_points - 1)  # 0 to 1
            
            # Helix equations
            angle = turns * 2 * np.pi * t
            x = self.base_center[0] + radius * np.cos(angle)
            y = self.base_center[1] + radius * np.sin(angle)
            z = self.base_height + height_range * t
            
            # Orientation
            rx, ry, rz = 0, 0, 0
            
            trajectory.append([x, y, z, rx, ry, rz])
        
        print(f"✅ Generated Helix trajectory: {num_points} waypoints, {turns} turns, height range={height_range}m")
        return trajectory
    
    def generate_sine_wave(self, num_points=20, amplitude=0.2, wavelength=0.6, axis='x'):
        """
        Generate sine wave trajectory.
        
        Args:
            num_points: Number of waypoints
            amplitude: Wave amplitude (meters)
            wavelength: Wave length (meters)
            axis: 'x' (wave in XZ) or 'y' (wave in YZ)
            
        Returns:
            list: Waypoints [(x, y, z, rx, ry, rz), ...]
        """
        trajectory = []
        
        for i in range(num_points):
            t = i / (num_points - 1)  # 0 to 1
            
            if axis == 'x':
                # Sine wave along X axis
                x = self.base_center[0] + wavelength * (t - 0.5)
                y = self.base_center[1]
                z = self.base_height + amplitude * np.sin(4 * np.pi * t)
            else:  # axis == 'y'
                # Sine wave along Y axis
                x = self.base_center[0]
                y = self.base_center[1] + wavelength * (t - 0.5)
                z = self.base_height + amplitude * np.sin(4 * np.pi * t)
            
            # Orientation
            rx, ry, rz = 0, 0, 0
            
            trajectory.append([x, y, z, rx, ry, rz])
        
        print(f"✅ Generated Sine Wave trajectory: {num_points} waypoints, amplitude={amplitude}m, axis={axis}")
        return trajectory
    
    def generate_star(self, num_points=25, outer_radius=0.3, inner_radius=0.15, num_tips=5):
        """
        Generate star-shaped trajectory.
        
        Args:
            num_points: Number of waypoints
            outer_radius: Distance to star tips (meters)
            inner_radius: Distance to star valleys (meters)
            num_tips: Number of star points (typically 5)
            
        Returns:
            list: Waypoints [(x, y, z, rx, ry, rz), ...]
        """
        trajectory = []
        
        for i in range(num_points):
            angle = 2 * np.pi * i / num_points
            
            # Alternate between outer (tips) and inner (valleys) radius
            tip_index = (i * num_tips * 2) / num_points
            if int(tip_index) % 2 == 0:
                radius = outer_radius
            else:
                radius = inner_radius
            
            # Smooth transition between radii
            smooth_factor = (tip_index % 1) * 2 - 1  # -1 to 1
            radius = inner_radius + (outer_radius - inner_radius) * (1 + smooth_factor) / 2
            
            x = self.base_center[0] + radius * np.cos(angle)
            y = self.base_center[1] + radius * np.sin(angle)
            z = self.base_height
            
            # Orientation
            rx, ry, rz = 0, 0, 0
            
            trajectory.append([x, y, z, rx, ry, rz])
        
        print(f"✅ Generated Star trajectory: {num_points} waypoints, {num_tips} points")
        return trajectory
    
    def generate_custom(self, waypoint_list):
        """
        Generate custom trajectory from explicit waypoint list.
        
        Args:
            waypoint_list: List of waypoints [(x, y, z), ...] or [(x, y, z, rx, ry, rz), ...]
            
        Returns:
            list: Waypoints [(x, y, z, rx, ry, rz), ...]
        """
        trajectory = []
        
        for waypoint in waypoint_list:
            if len(waypoint) == 3:
                # Position only, add default orientation
                x, y, z = waypoint
                rx, ry, rz = 0, 0, 0
            elif len(waypoint) == 6:
                # Full pose
                x, y, z, rx, ry, rz = waypoint
            else:
                raise ValueError(f"Invalid waypoint format: {waypoint}. Expected (x,y,z) or (x,y,z,rx,ry,rz)")
            
            trajectory.append([x, y, z, rx, ry, rz])
        
        print(f"✅ Generated Custom trajectory: {len(trajectory)} waypoints")
        return trajectory
    
    def generate_pick_and_place(self, pick_pos, place_pos, approach_height=0.2):
        """
        Generate pick-and-place trajectory with approach and retract.
        
        Args:
            pick_pos: Pick position (x, y, z)
            place_pos: Place position (x, y, z)
            approach_height: Height above objects for approach/retract (meters)
            
        Returns:
            list: Waypoints [(x, y, z, rx, ry, rz), ...]
        """
        trajectory = []
        
        # Phase 1: Move to approach position above pick
        trajectory.append([pick_pos[0], pick_pos[1], pick_pos[2] + approach_height, 0, 0, 0])
        
        # Phase 2: Descend to pick position
        trajectory.append([pick_pos[0], pick_pos[1], pick_pos[2], 0, 0, 0])
        
        # Phase 3: Grasp (stay at pick position)
        trajectory.append([pick_pos[0], pick_pos[1], pick_pos[2], 0, 0, 0])
        
        # Phase 4: Lift object
        trajectory.append([pick_pos[0], pick_pos[1], pick_pos[2] + approach_height, 0, 0, 0])
        
        # Phase 5: Move to approach position above place
        trajectory.append([place_pos[0], place_pos[1], place_pos[2] + approach_height, 0, 0, 0])
        
        # Phase 6: Descend to place position
        trajectory.append([place_pos[0], place_pos[1], place_pos[2], 0, 0, 0])
        
        # Phase 7: Release (stay at place position)
        trajectory.append([place_pos[0], place_pos[1], place_pos[2], 0, 0, 0])
        
        # Phase 8: Retract
        trajectory.append([place_pos[0], place_pos[1], place_pos[2] + approach_height, 0, 0, 0])
        
        print(f"✅ Generated Pick-and-Place trajectory: 8 waypoints from {pick_pos} to {place_pos}")
        return trajectory


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Create trajectory generator
    traj_gen = TrajectoryGenerator(base_height=0.8, base_center=(0.0, 0.0))
    
    print("\n" + "="*60)
    print("TRAJECTORY GENERATOR EXAMPLES")
    print("="*60 + "\n")
    
    # Example 1: Figure-8
    traj1 = traj_gen.generate_figure8(num_points=20, scale_x=0.3, scale_y=0.2)
    
    # Example 2: Horizontal circle
    traj2 = traj_gen.generate_circle(num_points=20, radius=0.3, orientation='horizontal')
    
    # Example 3: Straight line
    traj3 = traj_gen.generate_line(start_point=(0.2, 0.0, 0.6), 
                                     end_point=(0.5, 0.3, 1.0), 
                                     num_points=15)
    
    # Example 4: Square
    traj4 = traj_gen.generate_square(num_points=20, side_length=0.4)
    
    # Example 5: Helix
    traj5 = traj_gen.generate_helix(num_points=30, radius=0.25, height_range=0.4, turns=2)
    
    # Example 6: Sine wave
    traj6 = traj_gen.generate_sine_wave(num_points=20, amplitude=0.15, wavelength=0.6, axis='x')
    
    # Example 7: Star
    traj7 = traj_gen.generate_star(num_points=25, outer_radius=0.3, inner_radius=0.15, num_tips=5)
    
    # Example 8: Custom waypoints
    custom_waypoints = [
        (0.3, 0.0, 0.7),
        (0.4, 0.1, 0.8),
        (0.3, 0.2, 0.9),
        (0.2, 0.1, 0.8),
        (0.3, 0.0, 0.7),
    ]
    traj8 = traj_gen.generate_custom(custom_waypoints)
    
    # Example 9: Pick and place
    traj9 = traj_gen.generate_pick_and_place(pick_pos=(0.4, 0.2, 0.5),
                                              place_pos=(0.4, -0.2, 0.5),
                                              approach_height=0.15)
    
    print("\n" + "="*60)
    print("All trajectories generated successfully!")
    print("="*60)
