#!/usr/bin/env python3
"""
CRASH-RESISTANT SIMULATION LAUNCHER
==================================
Enhanced launcher that handles common issues and provides recovery options
"""

import subprocess
import sys
import os
import traceback

def main():
    print("🛡️  CRASH-RESISTANT SIMULATION LAUNCHER")
    print("=" * 45)
    
    try:
        print("🔧 Pre-flight checks...")
        
        # Check PyTorch
        try:
            import torch
            print(f"✅ PyTorch {torch.__version__} available")
        except ImportError:
            print("❌ PyTorch not available - performance will be limited")
        
        # Check our enhanced files
        if not os.path.exists('rl_mission_env.py'):
            print("❌ Missing rl_mission_env.py")
            return False
            
        print("✅ Enhanced RL files present")
        
        # Test DQN agent creation
        from rl_mission_env import DQNAgent
        test_agent = DQNAgent(state_dim=14, action_dim=19)
        print("✅ DQN agent creation test passed")
        
        print("\n🚀 Launching enhanced simulation...")
        print("📝 Instructions:")
        print("   • Press 't' to start RL training")
        print("   • Press 'd' to check status")
        print("   • Press 'Esc' to exit safely")
        print("   • If it crashes, rerun this script")
        
        input("\nPress Enter to launch...")
        
        # Launch with error handling
        result = subprocess.run([
            sys.executable, 
            'sim_husky_kuka.py'
        ], cwd='/home/marcoreis/q_ws')
        
        if result.returncode == 0:
            print("✅ simulation completed successfully")
        else:
            print(f"⚠️  simulation exited with code {result.returncode}")
            
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Launcher interrupted by user")
        return True
        
    except Exception as e:
        print(f"\n❌ Launcher error: {e}")
        print("\n🔍 Error details:")
        traceback.print_exc()
        
        print(f"\n🛠️  RECOVERY OPTIONS:")
        print("1. Check that you're in the correct conda environment")
        print("2. Try: conda activate pybullet_env")
        print("3. Verify PyTorch: python -c 'import torch; print(torch.__version__)'")
        print("4. If issues persist, run: python test_phase1_improvements.py")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)