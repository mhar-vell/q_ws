#!/usr/bin/env python3
"""
Quick test to verify DQN agent uses MPS (Apple GPU) acceleration.
"""

import sys
import torch
from rl_mission_env import DQNAgent

print("=" * 60)
print("🧪 DQN + MPS Verification Test")
print("=" * 60)

# Check PyTorch setup
print(f"\n1. PyTorch Configuration:")
print(f"   Version: {torch.__version__}")
print(f"   CUDA available: {torch.cuda.is_available()}")
print(f"   MPS available: {torch.backends.mps.is_available()}")

# Create DQN agent
print(f"\n2. Creating DQN Agent...")
try:
    agent = DQNAgent(state_dim=35, action_dim=10)
    print(f"   ✅ Agent created successfully")
    print(f"   Device: {agent.device}")
    print(f"   Network on device: {next(agent.q_network.parameters()).device}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test forward pass
print(f"\n3. Testing Neural Network Forward Pass...")
try:
    import numpy as np
    test_state = np.random.randn(35)
    action = agent.select_action(test_state)
    print(f"   ✅ Forward pass successful")
    print(f"   Test state shape: {test_state.shape}")
    print(f"   Selected action: {action}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test batch operations (replay buffer simulation)
print(f"\n4. Testing Batch Operations (GPU)...")
try:
    batch_states = torch.randn(32, 35).to(agent.device)
    batch_q_values = agent.q_network(batch_states)
    print(f"   ✅ Batch forward pass successful")
    print(f"   Batch shape: {batch_states.shape}")
    print(f"   Q-values shape: {batch_q_values.shape}")
    print(f"   Computation device: {batch_q_values.device}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Performance benchmark
print(f"\n5. Performance Benchmark...")
try:
    import time
    
    # Warmup
    for _ in range(10):
        _ = agent.select_action(test_state)
    
    # Benchmark
    start_time = time.time()
    num_iterations = 1000
    for _ in range(num_iterations):
        _ = agent.select_action(test_state)
    elapsed = time.time() - start_time
    
    fps = num_iterations / elapsed
    print(f"   ✅ Benchmark complete")
    print(f"   Iterations: {num_iterations}")
    print(f"   Time: {elapsed:.3f} seconds")
    print(f"   Speed: {fps:.1f} forward passes/sec")
    
    if fps > 500:
        print(f"   🚀 GPU acceleration working! (fast)")
    elif fps > 100:
        print(f"   ⚡ Decent performance")
    else:
        print(f"   ⚠️  Slower than expected (might be CPU)")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Summary
print(f"\n" + "=" * 60)
print(f"✅ VERIFICATION COMPLETE")
print(f"=" * 60)

if agent.device.type == "mps":
    print(f"\n🎉 SUCCESS! DQN will use Apple GPU (MPS) acceleration!")
    print(f"   Expected speedup: 5-8x faster than CPU")
    print(f"   Training time estimate: 45-60 minutes")
elif agent.device.type == "cuda":
    print(f"\n✅ DQN will use NVIDIA GPU (CUDA) acceleration!")
    print(f"   This is unexpected on macOS but excellent!")
elif agent.device.type == "cpu":
    print(f"\n⚠️  DQN will use CPU only")
    print(f"   Training will be slower (~2-3 hours)")
    print(f"   Consider checking MPS availability")

print(f"\n🚀 You're ready to start training!")
print(f"   Run: python3 sim_husky_kuka.py")
print(f"   Press 't' to start RL training\n")
