#!/bin/bash
# Setup Script for Phase 06 Monitoring & Evaluation
# Installs all required packages in pybullet_env

set -e  # Exit on error

echo "================================================"
echo "Phase 06 Setup Script"
echo "================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ Conda not found${NC}"
    echo "Please initialize conda:"
    echo "  source ~/anaconda3/etc/profile.d/conda.sh"
    exit 1
fi

echo -e "${GREEN}✅ Conda found${NC}"

# Check if pybullet_env exists
if conda env list | grep -q "pybullet_env"; then
    echo -e "${GREEN}✅ pybullet_env found${NC}"
else
    echo -e "${RED}❌ pybullet_env not found${NC}"
    echo "Please create it or use a different environment"
    exit 1
fi

# Activate pybullet_env
echo ""
echo "🔄 Activating pybullet_env..."
eval "$(conda shell.bash hook)"
conda activate pybullet_env

# Check current environment
if [[ $CONDA_DEFAULT_ENV == "pybullet_env" ]]; then
    echo -e "${GREEN}✅ pybullet_env activated${NC}"
else
    echo -e "${YELLOW}⚠️  Using environment: $CONDA_DEFAULT_ENV${NC}"
fi

# Show Python location
echo ""
echo "📍 Python location:"
which python

# Install packages
echo ""
echo "📦 Installing required packages..."
echo ""

packages=(
    "wandb"
    "matplotlib"
    "seaborn"
    "scipy"
    "scikit-learn"
    "jupyter"
    "pandas"
)

for package in "${packages[@]}"; do
    echo "  Installing $package..."
    pip install -q "$package" || echo -e "${YELLOW}⚠️  Warning: $package installation had issues${NC}"
done

echo ""
echo "🔍 Verifying installations..."

# Test imports
python << 'EOF'
import sys

packages = {
    'wandb': 'W&B logging',
    'matplotlib': 'Plotting',
    'seaborn': 'Statistical plots',
    'scipy': 'Scientific computing',
    'sklearn': 'Machine learning',
    'jupyter': 'Jupyter notebooks',
    'pandas': 'Data analysis',
    'numpy': 'Numerical computing',
    'torch': 'PyTorch (optional)',
}

print("\n📊 Package Status:")
print("-" * 50)

all_good = True
for module, description in packages.items():
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✅ {module:15} {version:12} - {description}")
    except ImportError:
        print(f"❌ {module:15} {'not found':12} - {description}")
        all_good = False

print("-" * 50)
if all_good:
    print("\n✅ All required packages available!")
else:
    print("\n⚠️  Some packages missing (see above)")

sys.exit(0 if all_good else 1)
EOF

status=$?

echo ""
if [ $status -eq 0 ]; then
    echo "================================================"
    echo -e "${GREEN}✅ Phase 06 setup complete!${NC}"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo "  1. Login to W&B: wandb login"
    echo "  2. Test: python training_data/phase_06_monitoring_evaluation/logging_infrastructure/test_wandb_simple.py"
    echo "  3. Follow: INTEGRATION_GUIDE.md"
    echo ""
else
    echo "================================================"
    echo -e "${YELLOW}⚠️  Setup completed with warnings${NC}"
    echo "================================================"
    echo ""
    echo "You may need to install missing packages manually:"
    echo "  pip install <package_name>"
    echo ""
fi

# Save environment
echo "💾 Saving environment to environment_phase06.yml..."
conda env export > environment_phase06.yml
echo -e "${GREEN}✅ Environment saved${NC}"

echo ""
echo "Environment info:"
conda info
