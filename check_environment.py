#!/usr/bin/env python3
"""
Quick environment checker and tester
Run this to verify your setup is ready for Phase 06
"""

import sys
import os
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_environment():
    """Check Python environment and location"""
    print_header("Environment Check")
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Detect environment type
    if 'pybullet_env' in sys.executable:
        print("✅ Running in pybullet_env (conda)")
    elif '.venv' in sys.executable:
        print("✅ Running in .venv (virtual environment)")
    else:
        print("⚠️  Running in unknown environment")
    
    return True

def check_packages():
    """Check if required packages are installed"""
    print_header("Package Check")
    
    required_packages = {
        'wandb': 'W&B logging',
        'matplotlib': 'Plotting',
        'numpy': 'Numerical computing',
        'torch': 'PyTorch (optional)',
    }
    
    optional_packages = {
        'seaborn': 'Statistical plots',
        'scipy': 'Scientific computing',
        'sklearn': 'Machine learning',
        'pandas': 'Data analysis',
    }
    
    missing_required = []
    missing_optional = []
    
    print("\nRequired packages:")
    for package, description in required_packages.items():
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"  ✅ {package:12} v{version:12} - {description}")
        except ImportError:
            print(f"  ❌ {package:12} {'NOT FOUND':12} - {description}")
            missing_required.append(package)
    
    print("\nOptional packages:")
    for package, description in optional_packages.items():
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"  ✅ {package:12} v{version:12} - {description}")
        except ImportError:
            print(f"  ⚠️  {package:12} {'NOT FOUND':12} - {description}")
            missing_optional.append(package)
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing_required)}")
        return False
    elif missing_optional:
        print(f"\n⚠️  Missing optional packages: {', '.join(missing_optional)}")
        print("  (These are nice to have but not critical)")
        return True
    else:
        print("\n✅ All packages available!")
        return True

def check_workspace_structure():
    """Check if workspace directories exist"""
    print_header("Workspace Structure Check")
    
    workspace_root = Path(__file__).parent.parent.parent
    
    required_dirs = [
        'training_data/phase_06_monitoring_evaluation/logging_infrastructure',
        'training_data/phase_04_state_optimization/04_2_trajectory_integration',
        'tools/training',
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = workspace_root / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} - NOT FOUND")
            all_exist = False
    
    return all_exist

def test_wandb():
    """Test wandb functionality"""
    print_header("W&B Test (Offline Mode)")
    
    try:
        # Set offline mode
        os.environ["WANDB_MODE"] = "offline"
        
        import wandb
        print(f"✅ wandb imported successfully (v{wandb.__version__})")
        
        # Initialize
        print("\nTesting initialization...")
        run = wandb.init(
            project="test-project",
            name="quick-test",
            mode="offline",
            dir="/tmp/wandb_test"
        )
        print("✅ W&B initialized (offline mode)")
        
        # Log test metrics
        print("Testing metric logging...")
        wandb.log({"test_metric": 42, "test_error": 0.5})
        print("✅ Metrics logged successfully")
        
        # Finish
        run.finish()
        print("✅ W&B test complete!")
        
        print("\n💡 W&B is working in offline mode")
        print("   To use online features:")
        print("   1. Create account: https://wandb.ai/signup")
        print("   2. Run: wandb login")
        
        return True
        
    except Exception as e:
        print(f"❌ W&B test failed: {e}")
        return False

def test_trajectory_wrapper():
    """Test if trajectory wrapper can be imported"""
    print_header("Trajectory Wrapper Test")
    
    try:
        # Add to path
        workspace_root = Path(__file__).parent
        sys.path.insert(0, str(workspace_root))
        
        from training_data.phase_04_state_optimization.04_2_trajectory_integration.trajectory_state_wrapper import TrajectoryStateWrapper
        
        print("✅ TrajectoryStateWrapper imported successfully")
        print(f"   Location: {TrajectoryStateWrapper.__module__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        print("\n💡 Make sure you're running from workspace root:")
        print("   cd /home/marcoreis/robust_mm_control_ws")
        print("   python tools/testing/environment_checker.py")
        return False

def main():
    """Run all checks"""
    print("\n" + "🚀" * 30)
    print("  Phase 06 Environment Checker")
    print("🚀" * 30)
    
    results = {
        'Environment': check_environment(),
        'Packages': check_packages(),
        'Workspace': check_workspace_structure(),
        'W&B': test_wandb(),
        'Trajectory Wrapper': test_trajectory_wrapper(),
    }
    
    # Summary
    print_header("Summary")
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test:20} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("  ✅ ALL CHECKS PASSED - Ready for Phase 06!")
    else:
        print("  ⚠️  SOME CHECKS FAILED - See above for details")
    print("=" * 60)
    
    print("\n📚 Next steps:")
    if not all_passed:
        print("  1. Fix failing checks (see details above)")
        print("  2. Run this script again to verify")
    else:
        print("  1. Review: INTEGRATION_GUIDE.md")
        print("  2. Modify: tools/training/enhanced_rl_trainer.py")
        print("  3. Train: python tools/training/enhanced_rl_trainer.py --use_wandb")
    
    print("\n📖 Documentation:")
    print("  - ENVIRONMENT_GUIDE.md - Environment setup")
    print("  - INTEGRATION_GUIDE.md - Code integration")
    print("  - QUICK_START.md - Getting started")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
