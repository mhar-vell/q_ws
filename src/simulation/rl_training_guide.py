#!/usr/bin/env python3
"""
RL Training Command-Line Usage Guide
===================================

This guide demonstrates how to use the new command-line arguments for scenario-specific
RL training with sim_husky_kuka.py.

BASIC USAGE:
-----------
python sim_husky_kuka.py --scenario <scenario> [options]

AVAILABLE SCENARIOS:
-------------------
- none         : No disturbances (baseline)
- random       : Random disturbances  
- periodic     : Periodic disturbances
- continuous   : Continuous disturbances
- impulse      : Impulse disturbances
- all          : Train all scenarios sequentially

AVAILABLE INTENSITIES:
---------------------
- normal       : Standard disturbance levels
- golden       : Enhanced disturbance levels (more challenging)
- both         : Train both intensity levels

COMMAND-LINE OPTIONS:
--------------------
--scenario     : Choose specific scenario or 'all' (default: continuous)
--intensity    : Choose intensity level (default: normal)
--episodes     : Override default episode count (default: 2000)
--headless     : Run without GUI for faster training
--auto-start   : Start training automatically on launch

PRACTICAL EXAMPLES:
==================

1. Quick Testing (Single Scenario):
   python _husky_.py --scenario continuous --episodes 100

2. Focused Training (Continuous Scenario Only):
   python _husky_.py --scenario continuous

3. Challenge Training (Golden Intensity):
   python _husky_.py --scenario continuous --intensity golden

4. Fast Training (Headless Mode):
   python _husky_.py --scenario continuous --headless --auto-start

5. Development Training (Custom Episodes):
   python _husky_.py --scenario periodic --episodes 500

6. Complete Training Session (All Scenarios):
   python _husky_.py --scenario all --intensity both --headless --auto-start

TRAINING TIME ESTIMATES:
=======================
- Single Scenario (2000 episodes): ~45-60 minutes
- Single Scenario (headless, 2000 episodes): ~30-40 minutes  
- All Scenarios (10 combinations, 2000 each): ~8-10 hours
- All Scenarios (headless): ~5-6 hours

RECOMMENDED WORKFLOW:
====================
1. Start with quick testing:
   python _husky_.py --scenario continuous --episodes 100

2. Run focused training on problematic scenarios:
   python _husky_.py --scenario continuous --intensity golden

3. For production training, use headless mode:
   python _husky_.py --scenario continuous --headless --auto-start

4. For comprehensive analysis, run all scenarios:
   python _husky_.py --scenario all --intensity both --headless --auto-start

MONITORING:
===========
- Training progress is logged to console
- Results saved in rl_results/ directory  
- Use 't' key to toggle training mode manually (when not using --auto-start)
- Press 'q' to quit simulation safely

TROUBLESHOOTING:
===============
- If training stops unexpectedly, restart with same command
- Use --episodes to reduce training time for testing
- Use --headless for faster training and reduced resource usage
- Check Python environment is properly configured with PyTorch 2.7.1
"""

def print_quick_reference():
    """Print a quick reference for common commands"""
    print("🚀 Quick Reference - RL Training Commands")
    print("=" * 50)
    
    commands = [
        ("Quick Test", "python _husky_.py --scenario continuous --episodes 100"),
        ("Single Scenario", "python _husky_.py --scenario continuous"),
        ("Challenge Mode", "python _husky_.py --scenario continuous --intensity golden"),
        ("Fast Training", "python _husky_.py --scenario continuous --headless --auto-start"),
        ("All Scenarios", "python _husky_.py --scenario all --intensity both --headless --auto-start"),
    ]
    
    for name, command in commands:
        print(f"\n📝 {name}:")
        print(f"   {command}")
    
    print(f"\n💡 Pro Tip: Use --headless --auto-start for unattended training!")

if __name__ == "__main__":
    print_quick_reference()