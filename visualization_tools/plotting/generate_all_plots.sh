#!/bin/bash
# Generate all analysis visualizations for phase_algorithm_core

echo "=========================================="
echo "Generating Analysis Visualizations"
echo "=========================================="

# Navigate to workspace root
cd "$(dirname "$0")/../.."

echo ""
echo "1. Generating DQN analysis visualizations..."
python3 visualization_tools/plotting/plot_dqn_analysis.py
if [ $? -eq 0 ]; then
    echo "✅ DQN visualizations complete"
else
    echo "❌ DQN visualization failed"
fi

echo ""
echo "2. Generating Q-Learning analysis visualizations..."
python3 visualization_tools/plotting/plot_qlearning_analysis.py
if [ $? -eq 0 ]; then
    echo "✅ Q-Learning visualizations complete"
else
    echo "❌ Q-Learning visualization failed"
fi

echo ""
echo "3. Algorithm comparison already generated"
echo "   (plot_algorithm_comparison.py)"

echo ""
echo "=========================================="
echo "Visualization Generation Complete!"
echo "=========================================="
echo ""
echo "Output directory: training_data/phase_algorithm_core/algorithm_analysis/plots/"
echo ""
echo "Generated files:"
ls -lh training_data/phase_algorithm_core/algorithm_analysis/plots/*.png 2>/dev/null || echo "  (Check for errors above)"
echo ""
