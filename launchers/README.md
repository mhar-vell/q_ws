# Simulation Launchers

This directory contains launcher scripts for the robust mobile manipulator control simulation. Each launcher is designed for specific use cases and environments.

## Quick Start

```bash
# For quick GUI testing/demos
python launchers/launch_gui_simulation.py

# For development with enhanced RL training
python launchers/launch_enhanced_simulation.py

# For production runs with error recovery
python launchers/launch_safe_simulation.py
```

## Available Launchers

### 1. `launch_gui_simulation.py` - Basic GUI Launcher
**Purpose:** Quick testing, demos, and visual debugging

**Features:**
- Simple GUI visualization setup
- Pre-configured for short test runs (5 episodes)
- Display environment configuration for GUI compatibility
- Interactive camera controls documentation
- Minimal configuration for quick starts

**Best For:**
- Quick visual checks of robot behavior
- Demonstrating the simulation to others
- Debugging physics interactions visually
- Testing new scenarios interactively

**Usage:**
```bash
python launchers/launch_gui_simulation.py
```

**Default Settings:**
- Scenario: `none` (no disturbances)
- Episodes: 5
- Intensity: `normal`
- Display: `:1` (configured for GUI)

**What You'll See:**
- PyBullet 3D visualization window
- Husky mobile base with KUKA arm
- Circular trajectory navigation
- Real-time IMU data in console
- Interactive camera controls (mouse drag/scroll)

---

### 2. `launch_enhanced_simulation.py` - Development Launcher
**Purpose:** Enhanced RL training with dependency checks and performance monitoring

**Features:**
- PyTorch availability check (DQN support)
- GPU/CPU device detection and reporting
- Phase 1 improvement file validation
- Performance expectations guidance
- Pre-flight checks before launch
- Detailed RL training instructions

**Best For:**
- RL algorithm development and testing
- Performance optimization experiments
- Training with dual algorithms (DQN + Q-Learning)
- Development environment validation
- Tracking Phase 1 improvements

**Usage:**
```bash
python launchers/launch_enhanced_simulation.py
```

**Pre-Flight Checks:**
1. ✅ PyTorch installation and device availability
2. ✅ Phase 1 improvement files existence
3. ✅ Enhanced RL trainer availability
4. ✅ Configuration file validation

**Performance Indicators:**
- With PyTorch (DQN): ~75-85% success rate
- Without PyTorch: ~25% success rate (Q-Learning only)
- GPU acceleration: 2-3x faster training

**Training Workflow:**
1. Launch simulation
2. Press `t` to start RL training
3. Monitor performance metrics
4. Checkpoints saved every 100 episodes
5. Press `d` for diagnostics
6. Press `Esc` for safe exit

---

### 3. `launch_safe_simulation.py` - Production Launcher
**Purpose:** Crash-resistant production runs with error handling and recovery

**Features:**
- Comprehensive pre-flight system checks
- DQN agent creation validation test
- Crash recovery and restart capabilities
- Detailed error reporting and diagnostics
- Safe shutdown procedures
- Fallback mechanisms for missing dependencies

**Best For:**
- Long training runs (1000+ episodes)
- Unattended batch experiments
- Production deployments
- Automated testing pipelines
- Continuous integration environments
- Critical experiments that can't fail silently

**Usage:**
```bash
python launchers/launch_safe_simulation.py
```

**Safety Features:**
1. **Pre-flight validation:** Checks all dependencies before launch
2. **Agent creation test:** Validates DQN initialization
3. **Error recovery:** Automatic restart on crashes
4. **Safe exit:** Proper cleanup on interrupt
5. **Diagnostic logging:** Detailed error traces
6. **Fallback modes:** Graceful degradation if PyTorch unavailable

**Error Handling:**
- Catches and logs all exceptions
- Provides recovery instructions
- Saves state before crash
- Restarts from last checkpoint
- Reports missing dependencies clearly

**Controls:**
- `t` → Start/resume RL training
- `d` → Display diagnostics and status
- `Esc` → Safe exit with cleanup
- `Ctrl+C` → Emergency stop (handled gracefully)

---

## Choosing the Right Launcher

| Use Case | Recommended Launcher | Why |
|----------|---------------------|-----|
| Quick test | `launch_gui_simulation.py` | Fast startup, visual feedback |
| Development | `launch_enhanced_simulation.py` | Checks dependencies, shows performance |
| Long training | `launch_safe_simulation.py` | Error recovery, safe for unattended runs |
| Demo/presentation | `launch_gui_simulation.py` | Clean GUI, easy to understand |
| CI/CD pipeline | `launch_safe_simulation.py` | Robust error handling |
| Debugging | `launch_gui_simulation.py` | Visual inspection of behavior |
| Batch experiments | `launch_safe_simulation.py` | Handles crashes, continues training |

## Common Workflows

### Development Cycle
```bash
# 1. Quick visual check
python launchers/launch_gui_simulation.py

# 2. Develop and test RL improvements
python launchers/launch_enhanced_simulation.py

# 3. Run long training with new algorithm
python launchers/launch_safe_simulation.py
```

### Production Training
```bash
# Use safe launcher for long unattended runs
python launchers/launch_safe_simulation.py

# Monitor logs in another terminal
tail -f training_logs.txt

# Check saved checkpoints
ls -lh rl_checkpoint_*.pth
```

### Testing New Features
```bash
# 1. Test with GUI to see visual behavior
python launchers/launch_gui_simulation.py

# 2. Validate with enhanced checks
python launchers/launch_enhanced_simulation.py

# 3. Run stress test with safe launcher
python launchers/launch_safe_simulation.py
```

## Configuration

### Environment Variables
```bash
# Set display for GUI (already configured in GUI launcher)
export DISPLAY=:1
export LIBGL_ALWAYS_INDIRECT=1

# For headless servers
export PYBULLET_MODE=DIRECT

# Set PyTorch device
export CUDA_VISIBLE_DEVICES=0  # Use GPU 0
```

### Custom Launch Parameters

All launchers use `sim_husky_kuka.py` under the hood. You can modify them to pass custom arguments:

```python
# Edit launcher file to customize:
cmd = [
    'python', 'sim_husky_kuka.py',
    '--scenario', 'continuous',      # or 'impulse', 'none'
    '--episodes', '2000',             # number of training episodes
    '--intensity', 'high',            # or 'normal', 'low'
    '--headless',                     # for no GUI
    '--auto-start',                   # start training immediately
    '--algorithm', 'both'             # 'dqn', 'qlearning', or 'both'
]
```

## Scenarios and Intensity Modes

### Scenarios
- **`none`**: No disturbances (baseline testing)
- **`continuous`**: Continuous sinusoidal disturbances
- **`impulse`**: Random impulse disturbances

### Intensity Modes
- **`low`**: Gentle disturbances (force: ±5N, torque: ±2Nm)
- **`normal`**: Moderate disturbances (force: ±10N, torque: ±5Nm)
- **`high`**: Severe disturbances (force: ±20N, torque: ±10Nm)

## Troubleshooting

### GUI Not Appearing
```bash
# Check display
echo $DISPLAY

# Test with explicit display setting
DISPLAY=:1 python launchers/launch_gui_simulation.py

# For remote systems, use X11 forwarding
ssh -X user@host
```

### PyTorch Not Found
```bash
# Install PyTorch
conda install pytorch torchvision torchaudio -c pytorch

# Or with pip
pip install torch torchvision torchaudio

# Verify installation
python -c "import torch; print(torch.__version__)"
```

### Simulation Crashes
```bash
# Use safe launcher with error recovery
python launchers/launch_safe_simulation.py

# Check logs for error details
cat simulation_errors.log

# Verify all dependencies
python check_phase1_status.py
```

### Performance Issues
```bash
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Run with CPU only if GPU issues
export CUDA_VISIBLE_DEVICES=-1
python launchers/launch_safe_simulation.py

# Monitor resource usage
htop  # or top
```

### Import Errors
```bash
# Add workspace to Python path
export PYTHONPATH=/home/marcoreis/robust_mm_control_ws:$PYTHONPATH

# Or add to launcher script permanently
import sys
sys.path.insert(0, '/home/marcoreis/robust_mm_control_ws')
```

## Advanced Usage

### Running Multiple Parallel Experiments
```bash
# Terminal 1: Continuous scenario
python launchers/launch_safe_simulation.py --scenario continuous

# Terminal 2: Impulse scenario
python launchers/launch_safe_simulation.py --scenario impulse

# Terminal 3: No disturbances baseline
python launchers/launch_safe_simulation.py --scenario none
```

### Automated Batch Training
```bash
#!/bin/bash
# batch_training.sh

scenarios=("none" "continuous" "impulse")
intensities=("low" "normal" "high")

for scenario in "${scenarios[@]}"; do
    for intensity in "${intensities[@]}"; do
        echo "Training: $scenario - $intensity"
        python launchers/launch_safe_simulation.py \
            --scenario $scenario \
            --intensity $intensity \
            --episodes 1000 \
            --headless
    done
done
```

### Checkpoint Management
```bash
# List all checkpoints
ls -lh rl_checkpoint_*.pth

# Find latest checkpoint
ls -t rl_checkpoint_*.pth | head -1

# Resume from specific checkpoint
python launchers/launch_safe_simulation.py --checkpoint rl_checkpoint_ep2000_dqn.pth
```

## Integration with Tests

The launchers work seamlessly with the test suite:

```bash
# Test launcher functionality
cd test_scripts/cli_tests
python test_command_line_args.py

# Test simulation behavior
cd test_scripts/simulation_tests
python test_phase1_improvements.py

# Run integration tests
cd test_scripts/integration_tests
python test_rl_system.py
```

## Creating Custom Launchers

To create a new launcher for specific needs:

1. **Copy an existing launcher:**
   ```bash
   cp launchers/launch_safe_simulation.py launchers/launch_custom.py
   ```

2. **Modify launch parameters:**
   ```python
   cmd = [
       'python', 'sim_husky_kuka.py',
       '--scenario', 'your_scenario',
       '--custom-flag', 'value'
   ]
   ```

3. **Add custom checks:**
   ```python
   def check_custom_requirements():
       # Your validation logic
       pass
   ```

4. **Document in this README:**
   - Add entry to "Available Launchers" section
   - Update "Choosing the Right Launcher" table
   - Add example workflow

## Performance Benchmarks

Expected training performance by launcher configuration:

| Configuration | Success Rate | Training Speed | GPU Usage |
|--------------|--------------|----------------|-----------|
| DQN + GPU | 75-85% | ~100 eps/min | 40-60% |
| DQN + CPU | 75-85% | ~30 eps/min | N/A |
| Q-Learning | 20-30% | ~50 eps/min | N/A |
| Both (DQN+QL) | 80-90% | ~80 eps/min | 30-50% |

*Benchmarks run on: Intel i7, 16GB RAM, NVIDIA GTX 1660*

## Support and Contributing

### Getting Help
- Check existing test scripts: `test_scripts/`
- Review Phase 1 documentation: `PHASE1_IMPLEMENTATION_COMPLETE.md`
- Examine main simulation: `sim_husky_kuka.py`

### Contributing New Launchers
1. Follow naming convention: `launch_<purpose>.py`
2. Include comprehensive docstring
3. Add pre-flight checks
4. Document in this README
5. Add corresponding tests in `test_scripts/cli_tests/`

### Best Practices
- Always validate dependencies before launch
- Provide clear user feedback during startup
- Handle errors gracefully with recovery options
- Document expected behavior and performance
- Include safety controls (Esc for exit, etc.)

---

**Last Updated:** November 1, 2025  
**Workspace:** `/home/marcoreis/robust_mm_control_ws`  
**Main Simulation:** `sim_husky_kuka.py`
