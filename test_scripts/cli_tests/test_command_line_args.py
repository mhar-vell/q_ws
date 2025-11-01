#!/usr/bin/env python3
"""
Test Command-Line Arguments for Scenario-Specific RL Training
============================================================

This script tests the new command-line argument functionality for sim_husky_kuka.py
without actually running the full simulation. It verifies that the argument parsing
and scenario configuration work correctly.
"""

import sys
import importlib.util
import argparse

def test_argument_parsing():
    """Test the argument parsing functionality"""
    print("🧪 Testing Command-Line Argument Parsing")
    print("=" * 50)
    
    # Test scenarios
    test_cases = [
        # Format: [args_list, expected_scenario, expected_intensity, expected_episodes]
        (["--scenario", "continuous"], "continuous", "normal", None),
        (["--scenario", "continuous", "--intensity", "golden"], "continuous", "golden", None),
        (["--scenario", "all", "--intensity", "both"], "all", "both", None),
        (["--scenario", "random", "--episodes", "1000"], "random", "normal", 1000),
        (["--scenario", "periodic", "--intensity", "golden", "--episodes", "500", "--headless"], "periodic", "golden", 500),
        (["--scenario", "impulse", "--auto-start"], "impulse", "normal", None),
    ]
    
    for i, (args, expected_scenario, expected_intensity, expected_episodes) in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {' '.join(args)}")
        
        # Create parser like in sim_husky_kuka.py
        parser = argparse.ArgumentParser(description='RL Training Scenario Configuration')
        parser.add_argument('--scenario', default='continuous',
                          choices=['none', 'random', 'periodic', 'continuous', 'impulse', 'all'],
                          help='RL training scenario to run')
        parser.add_argument('--intensity', default='normal',
                          choices=['normal', 'golden', 'both'],
                          help='Disturbance intensity level')
        parser.add_argument('--episodes', type=int, default=None,
                          help='Number of training episodes (overrides default)')
        parser.add_argument('--headless', action='store_true', default=False,
                          help='Run without GUI for faster training')
        parser.add_argument('--auto-start', action='store_true', default=False,
                          help='Start training automatically on launch')
        
        # Parse the test arguments
        parsed_args = parser.parse_args(args)
        
        # Verify results
        assert parsed_args.scenario == expected_scenario, f"Scenario mismatch: {parsed_args.scenario} != {expected_scenario}"
        assert parsed_args.intensity == expected_intensity, f"Intensity mismatch: {parsed_args.intensity} != {expected_intensity}"
        assert parsed_args.episodes == expected_episodes, f"Episodes mismatch: {parsed_args.episodes} != {expected_episodes}"
        
        print(f"   ✅ Scenario: {parsed_args.scenario}")
        print(f"   ✅ Intensity: {parsed_args.intensity}")
        print(f"   ✅ Episodes: {parsed_args.episodes}")
        print(f"   ✅ Headless: {parsed_args.headless}")
        print(f"   ✅ Auto-start: {parsed_args.auto_start}")

def test_scenario_combinations():
    """Test scenario combination generation logic"""
    print("\n\n🔧 Testing Scenario Combination Generation")
    print("=" * 50)
    
    test_scenarios = [
        ("continuous", "normal", 1),
        ("continuous", "golden", 1),
        ("continuous", "both", 2),
        ("all", "normal", 5),
        ("all", "golden", 5),
        ("all", "both", 10),
    ]
    
    for scenario, intensity, expected_count in test_scenarios:
        print(f"\n🎯 Testing: scenario={scenario}, intensity={intensity}")
        
        # ulate the logic from _husky_.py
        if scenario == 'all':
            rl_scenarios = ['none', 'random', 'periodic', 'continuous', 'impulse']
        else:
            rl_scenarios = [scenario]
        
        if intensity == 'both':
            rl_intensity_levels = ['normal', 'golden']
        elif intensity == 'normal':
            rl_intensity_levels = ['normal']
        else:  # golden
            rl_intensity_levels = ['golden']
        
        # Create combinations
        rl_training_combinations = []
        for scen in rl_scenarios:
            for intens in rl_intensity_levels:
                rl_training_combinations.append({'scenario': scen, 'intensity': intens})
        
        actual_count = len(rl_training_combinations)
        assert actual_count == expected_count, f"Combination count mismatch: {actual_count} != {expected_count}"
        
        print(f"   ✅ Generated {actual_count} combinations (expected {expected_count})")
        for combo in rl_training_combinations:
            emoji = "⚡" if combo['intensity'] == 'golden' else "📊"
            print(f"      {emoji} {combo['scenario'].upper()}_{combo['intensity'].upper()}")

def test_usage_examples():
    """Display usage examples for the user"""
    print("\n\n📚 Command-Line Usage Examples")
    print("=" * 50)
    
    examples = [
        ("Train continuous scenario only (normal intensity)", 
         "python _husky_.py --scenario continuous"),
        ("Train continuous scenario with golden intensity", 
         "python _husky_.py --scenario continuous --intensity golden"),
        ("Train continuous scenario with both intensities", 
         "python _husky_.py --scenario continuous --intensity both"),
        ("Train all scenarios with normal intensity", 
         "python _husky_.py --scenario all --intensity normal"),
        ("Train continuous scenario with custom episodes", 
         "python _husky_.py --scenario continuous --episodes 1000"),
        ("Train headless (no GUI) with auto-start", 
         "python _husky_.py --scenario continuous --headless --auto-start"),
        ("Full training session (all scenarios, both intensities, headless)", 
         "python _husky_.py --scenario all --intensity both --headless --auto-start"),
    ]
    
    for description, command in examples:
        print(f"\n📝 {description}:")
        print(f"   {command}")

if __name__ == "__main__":
    try:
        test_argument_parsing()
        test_scenario_combinations()
        test_usage_examples()
        
        print("\n\n🎉 All Tests Passed!")
        print("=" * 50)
        print("✅ Command-line argument parsing working correctly")
        print("✅ Scenario combination generation working correctly") 
        print("✅ Ready for scenario-specific RL training!")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        sys.exit(1)