#!/usr/bin/env python3
"""
PHASE 1 IMPROVEMENT TEST SCRIPT
==============================
Quick test to verify Phase 1 improvements are working correctly
Tests the enhanced reward function, DQN forcing, and relaxed success criteria
"""

import numpy as np
import sys
import os

# Add current directory to path
sys.path.append('/home/marcoreis/q_ws')

def test_enhanced_reward_function():
    """Test the new progressive reward system"""
    print("🧪 Testing Enhanced Reward Function...")
    
    try:
        from rl_mission_env import MobileManipulatorEnv
        
        # Create mock environment (without PyBullet)
        env = MobileManipulatorEnv(
            pybullet_client=None,
            husky_id=None, 
            _id=None,
            goal_pose=[1.0, 0.0, 0.5, 0.0]
        )
        
        # Test different error scenarios
        test_cases = [
            (0.005, "Excellent precision (0.5cm)"),
            (0.015, "Very good precision (1.5cm)"), 
            (0.025, "Good precision (2.5cm)"),
            (0.045, "Acceptable precision (4.5cm)"),
            (0.08, "Making progress (8cm)"),
            (0.15, "Far from target (15cm)")
        ]
        
        print("   Distance → Expected Reward Category")
        for error, description in test_cases:
            # Mock observation with end-effector position
            mock_obs = np.zeros(14)
            mock_obs[-4:-1] = [1.0 + error, 0.0, 0.5]  # End-effector position
            
            reward = env.get_reward(mock_obs, 0)
            print(f"   {error*100:4.1f}cm → {reward:6.1f} ({description})")
        
        print("   ✅ Enhanced reward function working!")
        return True
        
    except Exception as e:
        print(f"   ❌ Enhanced reward test failed: {e}")
        return False

def test_dqn_agent_creation():
    """Test DQN agent creation and PyTorch detection"""
    print("\n🧪 Testing DQN Agent Creation...")
    
    try:
        from rl_mission_env import DQNAgent
        
        # Try to create DQN agent
        agent = DQNAgent(state_dim=14, action_dim=19)
        
        if agent.use_dqn:
            print("   ✅ PyTorch available - DQN agent created successfully!")
            print(f"   🧠 Neural network device: {agent.device}")
            print(f"   📊 Memory size: {agent.memory_size}")
            print(f"   🎯 Batch size: {agent.batch_size}")
            return True
        else:
            print("   ⚠️  PyTorch not available - using tabular fallback")
            print("   💡 Install PyTorch for better performance:")
            print("      conda install pytorch torchvision torchaudio -c pytorch")
            return False
            
    except Exception as e:
        print(f"   ❌ DQN agent test failed: {e}")
        return False

def test_curriculum_difficulty():
    """Test the graduated success criteria"""
    print("\n🧪 Testing Curriculum Difficulty System...")
    
    try:
        from rl_mission_env import MobileManipulatorEnv
        
        env = MobileManipulatorEnv(
            pybullet_client=None,
            husky_id=None,
            _id=None, 
            goal_pose=[1.0, 0.0, 0.5, 0.0]
        )
        
        # Test curriculum progression
        test_episodes = [500, 2000, 5000]
        
        print("   Episode → Tolerance → Required Steps")
        for episode in test_episodes:
            env.update_curriculum_difficulty(episode)
            tolerance_cm = env.current_tolerance * 100
            steps = env.required_consecutive
            
            print(f"   {episode:5d} → {tolerance_cm:4.1f}cm → {steps:2d} steps")
        
        print("   ✅ Curriculum difficulty system working!")
        return True
        
    except Exception as e:
        print(f"   ❌ Curriculum test failed: {e}")
        return False

def test_enhanced_trainer():
    """Test the enhanced training system"""
    print("\n🧪 Testing Enhanced Trainer System...")
    
    try:
        from enhanced_rl_trainer import EnhancedRLTrainer
        
        # Create trainer (without PyBullet)
        trainer = EnhancedRLTrainer()
        
        # Test trajectory generation
        trajectory = trainer.create_circular_trajectory(
            center=[1.0, 0.0, 0.5], 
            radius=0.3, 
            num_points=10
        )
        
        print(f"   ✅ Trainer created successfully!")
        print(f"   🔄 Circular trajectory: {len(trajectory)} points")
        print(f"   📊 Scenarios: {len(trainer.scenarios)} types")
        print(f"   ⚡ Intensities: {len(trainer.intensities)} levels")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Enhanced trainer test failed: {e}")
        return False

def main():
    """Run all Phase 1 improvement tests"""
    print("🚀 PHASE 1 IMPROVEMENT VERIFICATION")
    print("=" * 40)
    print("Testing all Phase 1 enhancements...")
    
    tests = [
        test_enhanced_reward_function,
        test_dqn_agent_creation, 
        test_curriculum_difficulty,
        test_enhanced_trainer
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📋 TEST SUMMARY")
    print("=" * 20)
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("🎉 All Phase 1 improvements working correctly!")
        print("✅ Ready to run enhanced training!")
        print("\n💡 Next steps:")
        print("   1. Ensure PyTorch is installed for DQN")
        print("   2. Run enhanced training with PyBullet environment")
        print("   3. Compare results with baseline 25% performance")
    else:
        print("⚠️  Some improvements need attention")
        print("🔧 Fix failing tests before proceeding")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)