#!/usr/bin/env python3
"""
ENHANCED SIMULATION STARTUP SCRIPT
=================================
Quick launcher for Phase 1 enhanced RL training with sim_husky_kuka.py

This script:
1. Checks PyTorch installation
2. Launches enhanced simulation 
3. Provides instructions for RL training
4. Shows expected performance improvements
"""

import subprocess
import sys
import os

def check_pytorch():
    """Check if PyTorch is available"""
    try:
        import torch
        print("✅ PyTorch available - DQN will work properly")
        print(f"   Device: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
        return True
    except ImportError:
        print("❌ PyTorch not available!")
        print("🔧 Install with: conda install pytorch torchvision torchaudio -c pytorch")
        print("⚠️  Without PyTorch, performance will be limited to ~25%")
        return False

def check_phase1_files():
    """Check if Phase 1 improvement files exist"""
    required_files = [
        'rl_mission_env.py',
        'enhanced_rl_trainer.py', 
        'PHASE1_IMPLEMENTATION_COMPLETE.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing Phase 1 files: {missing_files}")
        return False
    else:
        print("✅ Phase 1 improvement files present")
        return True

def main():
    print("🚀 ENHANCED RL SIMULATION LAUNCHER")
    print("=" * 40)
    print("Phase 1 Improvements: 25% → 40-45% Performance Target")
    print()
    
    # Check prerequisites
    pytorch_ok = check_pytorch()
    files_ok = check_phase1_files()
    
    if not files_ok:
        print("\n❌ Cannot start - missing required files")
        return False
    
    if not pytorch_ok:
        print("\n⚠️  Warning: PyTorch missing - performance will be limited")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            return False
    
    print("\n🎯 EXPECTED IMPROVEMENTS:")
    print("  • Enhanced reward function with progressive tiers")
    print("  • DQN with optimized neural network architecture")
    print("  • Curriculum learning: 5cm → 3cm → 2cm tolerance")
    print("  • Better hyperparameters for stable training")
    print("  • Expected performance jump: 25% → 40-45%")
    
    print(f"\n🎮 CONTROLS AFTER LAUNCH:")
    print("  • 't' - Start RL training mode")
    print("  • 'd' - Check training status")
    print("  • 'k' - Switch between DQN/Q-Learning")
    print("  • 'Esc' - Exit simulation")
    
    print(f"\n📊 TRAINING CONFIGURATION:")
    print("  • Episodes per scenario: 2000 (Phase 1 optimized)")
    print("  • Max steps per episode: 200 (curriculum friendly)")
    print("  • Total combinations: 10 (5 scenarios × 2 intensities)")
    print("  • Estimated time: ~3 hours for complete training")
    
    input("\nPress Enter to launch enhanced simulation...")
    
    # Launch the main simulation
    try:
        print("\n🚀 Launching sim_husky_kuka.py with Phase 1 enhancements...")
        result = subprocess.run([sys.executable, 'sim_husky_kuka.py'], 
                              cwd='/home/marcoreis/q_ws')
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n👋 simulation interrupted by user")
        return True
    except Exception as e:
        print(f"\n❌ Error launching simulation: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ simulation completed successfully")
    else:
        print("\n❌ simulation encountered errors")
    
    sys.exit(0 if success else 1)