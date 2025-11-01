# Test Scripts Directory

This directory contains all test scripts for the robust mobile manipulator control workspace.

## Directory Structure

```
test_scripts/
├── README.md                    # This file
├── cli_tests/                   # Command-line interface tests
├── simulation_tests/            # Simulation behavior tests
├── unit_tests/                  # Unit tests for specific components
├── integration_tests/           # Integration tests for system workflows
└── analysis_scripts/            # Analysis and visualization scripts
```

## Test Categories

### 1. CLI Tests (`cli_tests/`)
Tests for command-line argument parsing and configuration.

- **`test_algorithm_arguments.py`**
  - Tests RL algorithm selection (DQN, Q-Learning, both)
  - Verifies `--algorithm` flag functionality
  - Documents available algorithm options

- **`test_auto_restart.py`**
  - Tests auto-restart functionality on decoupling detection
  - Verifies `--auto-restart` flag
  - Documents restart triggers and thresholds

- **`test_auto_shutdown.py`**
  - Tests automatic shutdown after training completion
  - Verifies `--auto-shutdown` flag
  - Documents shutdown conditions

- **`test_command_line_args.py`**
  - Comprehensive test of all CLI arguments
  - Tests scenario selection, intensity modes, episode counts
  - Validates argument combinations

### 2. Simulation Tests (`simulation_tests/`)
Tests for simulation behavior and physics.

- **`test_decoupling_detection.py`**
  - Tests Husky-KUKA decoupling detection system
  - Validates constraint monitoring thresholds
  - Checks severity level classification

- **`test_gui.py`**
  - Tests GUI mode initialization and rendering
  - Validates camera controls and visualization
  - Checks keyboard event handling

- **`test_mounting.py`**
  - Tests Husky-KUKA mounting constraint
  - Validates constraint force limits
  - Checks mounting stability

- **`test_phase1_improvements.py`**
  - Tests Phase 1 implementation features
  - Validates enhanced physics parameters
  - Checks disturbance scenarios and intensity modes

### 3. Unit Tests (`unit_tests/`)
Isolated tests for individual components.

- **`test_dqn_device.py`**
  - Tests DQN agent device selection (CPU/CUDA)
  - Validates GPU availability detection
  - Checks tensor device placement

- **`test_mounting.py`**
  - Unit test for mounting constraint physics
  - Tests constraint force calculations
  - Validates mounting parameters

- **`test_waypoints.py`**
  - Tests waypoint generation and navigation
  - Validates circular and square path waypoints
  - Checks trajectory completion metrics

### 4. Integration Tests (`integration_tests/`)
End-to-end workflow tests.

- **`test_analysis.py`**
  - Tests analysis pipeline for training results
  - Validates metrics collection and visualization
  - Checks report generation

- **`test_enhanced_rl.py`**
  - Tests enhanced RL trainer functionality
  - Validates dual-algorithm training workflow
  - Checks checkpoint saving and loading

- **`test_rl_system.py`**
  - Tests complete RL training system
  - Validates environment, agent, and trainer integration
  - Checks scenario and intensity handling

### 5. Analysis Scripts (`analysis_scripts/`)
Scripts for analyzing and visualizing results.

- **`rl_training_analysis.py`**
  - Analyzes RL training metrics from saved JSON
  - Generates comparison plots and statistics
  - Produces performance reports

- **`run_analysis.py`**
  - Runs complete analysis pipeline
  - Processes all training results
  - Generates comprehensive reports

- **`simple_analysis_runner.py`**
  - Simplified analysis runner for quick checks
  - Basic metrics and visualization
  - Lightweight alternative to full analysis

## Running Tests

### Quick Test Commands

```bash
# Run all CLI tests
cd test_scripts/cli_tests
python test_command_line_args.py

# Run all unit tests
cd test_scripts/unit_tests
python -m pytest

# Run specific integration test
cd test_scripts/integration_tests
python test_rl_system.py

# Run analysis on training results
cd test_scripts/analysis_scripts
python rl_training_analysis.py
```

### Full Test Suite

```bash
# From test_scripts directory
python -m pytest unit_tests/
python -m pytest integration_tests/
```

## Test Development Guidelines

### Adding New Tests

1. **Choose the right category:**
   - CLI tests → `cli_tests/`
   - Simulation behavior → `simulation_tests/`
   - Component isolation → `unit_tests/`
   - Full workflows → `integration_tests/`
   - Result analysis → `analysis_scripts/`

2. **Naming convention:**
   - Use descriptive names: `test_<feature>.py`
   - Start with docstring explaining purpose
   - Include example usage in comments

3. **Test structure:**
   ```python
   #!/usr/bin/env python3
   """
   Test <Feature Name>
   ===================
   
   Brief description of what this test validates.
   """
   
   def test_feature():
       """Test description"""
       # Test implementation
       pass
   
   if __name__ == "__main__":
       test_feature()
   ```

### Best Practices

- Keep tests focused and atomic
- Document expected behavior clearly
- Use meaningful assertions with messages
- Clean up resources (files, processes) after tests
- Make tests reproducible (set random seeds if needed)
- Avoid hardcoded paths; use relative paths or environment variables

## Continuous Integration

Tests are organized to support CI/CD pipelines:

1. **Fast unit tests** run on every commit
2. **Integration tests** run on pull requests
3. **Full simulation tests** run nightly
4. **Analysis scripts** run after training completion

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Add project root to PYTHONPATH
export PYTHONPATH=/home/marcoreis/robust_mm_control_ws:$PYTHONPATH
```

**PyBullet GUI issues in headless environments:**
```bash
# Use DIRECT mode or Xvfb
python test.py --headless
# OR
xvfb-run python test.py
```

**CUDA/GPU tests failing:**
```bash
# Tests automatically fallback to CPU
# Check GPU availability:
python -c "import torch; print(torch.cuda.is_available())"
```

## Test Coverage

To check test coverage:

```bash
pytest --cov=. --cov-report=html unit_tests/
# View coverage report in htmlcov/index.html
```

## Contributing

When adding new features to `sim_husky_kuka.py` or related modules:

1. Add corresponding tests in appropriate category
2. Update this README with test description
3. Ensure all existing tests still pass
4. Add integration test if feature affects multiple components

## Support

For questions about tests or adding new test coverage:
- Check existing test files for examples
- Review test docstrings for usage patterns
- Refer to main project README for architecture overview
