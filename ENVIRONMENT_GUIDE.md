# Python Environment Guide

This workspace uses multiple Python environments. Here's how to work with them.

---

## 📦 Available Environments

### 1. **pybullet_env** (Conda - Main Training Environment)
- **Location:** `/home/marcoreis/anaconda3/envs/pybullet_env`
- **Python:** 3.12.3
- **Use for:** Running simulations, training, PyBullet code
- **Packages:** PyBullet, numpy, torch (if installed)

### 2. **.venv** (Virtual Environment - Analysis Environment)
- **Location:** `/home/marcoreis/robust_mm_control_ws/.venv`
- **Python:** 3.12.3
- **Use for:** Analysis, notebooks, W&B logging
- **Packages:** wandb (✅ installed), matplotlib, pandas

---

## 🔄 How to Switch Environments

### Switch to pybullet_env (for training):
```bash
conda activate pybullet_env
```

### Switch to .venv (for analysis):
```bash
# Deactivate conda first
conda deactivate

# Activate .venv
source /home/marcoreis/robust_mm_control_ws/.venv/bin/activate
```

### Check which environment is active:
```bash
which python
```

Expected outputs:
- pybullet_env: `/home/marcoreis/anaconda3/envs/pybullet_env/bin/python`
- .venv: `/home/marcoreis/robust_mm_control_ws/.venv/bin/python`

---

## 📦 Installing Packages

### In pybullet_env (conda):
```bash
conda activate pybullet_env

# Using conda (preferred)
conda install package_name

# Using pip
pip install package_name
```

### In .venv (virtual environment):
```bash
source /home/marcoreis/robust_mm_control_ws/.venv/bin/activate
pip install package_name
```

### Install wandb in pybullet_env:
```bash
conda activate pybullet_env
pip install wandb

# Verify
python -c "import wandb; print(wandb.__version__)"
```

---

## 🎯 Recommended Setup

### For Phase 04-06 Work:

**Option A: Use pybullet_env for everything** (RECOMMENDED)
```bash
conda activate pybullet_env

# Install missing packages
pip install wandb matplotlib seaborn jupyter scipy scikit-learn

# Now you can:
# - Run training scripts
# - Use W&B logging
# - Run Jupyter notebooks
# - Do statistical analysis
```

**Option B: Use both environments**
- **pybullet_env:** Training scripts only
- **.venv:** Analysis, notebooks, W&B dashboard

---

## 🚀 Quick Start Commands

### Check what's installed:
```bash
# In pybullet_env
conda activate pybullet_env
pip list | grep -E "wandb|torch|pybullet|matplotlib"

# In .venv
source .venv/bin/activate
pip list | grep -E "wandb|matplotlib|pandas"
```

### Install all Phase 06 requirements in pybullet_env:
```bash
conda activate pybullet_env
pip install wandb matplotlib seaborn scipy scikit-learn jupyter
```

### Verify installations:
```bash
python -c "import wandb, matplotlib, seaborn, scipy, sklearn; print('✅ All packages available')"
```

---

## 🔧 Troubleshooting

### "No module named 'wandb'"
**Solution:** Install in current environment:
```bash
# Check which env you're in
which python

# Install wandb
pip install wandb
```

### "conda: command not found"
**Solution:** Initialize conda:
```bash
source ~/anaconda3/etc/profile.d/conda.sh
conda init zsh
```

### Packages installed but not found
**Solution:** Make sure you're using the right environment:
```bash
# See what's active
conda env list  # * shows active environment

# Deactivate all
conda deactivate
conda deactivate  # Sometimes need to run twice

# Activate the one you want
conda activate pybullet_env
```

---

## 📝 Environment Management

### Create new conda environment:
```bash
conda create -n new_env_name python=3.12
conda activate new_env_name
```

### Clone pybullet_env:
```bash
conda create -n pybullet_env_backup --clone pybullet_env
```

### Export environment:
```bash
conda activate pybullet_env
conda env export > environment_backup.yml
```

### Restore from export:
```bash
conda env create -f environment_backup.yml
```

---

## 🎯 For Phase 04.2 + Phase 06 Integration

**Recommended approach:** Use pybullet_env for everything

```bash
# 1. Activate environment
conda activate pybullet_env

# 2. Install Phase 06 requirements
pip install wandb matplotlib seaborn scipy scikit-learn

# 3. Test
python training_data/phase_06_monitoring_evaluation/logging_infrastructure/test_wandb_simple.py

# 4. Run training with logging
cd tools/training
python enhanced_rl_trainer.py --use_trajectory_wrapper --use_wandb
```

---

## 💡 Best Practices

1. **Use pybullet_env as primary** - Install everything you need there
2. **Check active environment** - Before running scripts: `which python`
3. **Keep .venv as backup** - For isolating experiments
4. **Document dependencies** - Export environment after major changes

---

**Last Updated:** November 5, 2025
