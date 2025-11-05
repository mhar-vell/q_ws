#!/usr/bin/env python3
"""
Simple test to verify wandb installation without requiring login
"""

import os
import sys

# Set wandb to offline mode (no login required)
os.environ["WANDB_MODE"] = "offline"

try:
    import wandb
    print("✅ wandb imported successfully")
    print(f"   Version: {wandb.__version__}")
    
    # Test basic initialization (offline mode)
    print("\n🔧 Testing offline initialization...")
    run = wandb.init(
        project="test-project",
        name="test-run",
        mode="offline"
    )
    print("✅ wandb initialized successfully (offline mode)")
    
    # Test logging
    print("\n📊 Testing metric logging...")
    wandb.log({"test_metric": 42, "test_error": 0.5})
    print("✅ Metrics logged successfully")
    
    # Finish
    run.finish()
    print("\n✅ All tests passed!")
    print("\n💡 To use wandb online:")
    print("   1. Create account at https://wandb.ai")
    print("   2. Run: wandb login")
    print("   3. Remove WANDB_MODE=offline from your code")
    
except ImportError as e:
    print(f"❌ Error: {e}")
    print("\n🔧 To install wandb:")
    print("   pip install wandb")
    sys.exit(1)
except Exception as e:
    print(f"⚠️  Warning: {e}")
    print("   wandb is installed but test failed")
    sys.exit(1)
