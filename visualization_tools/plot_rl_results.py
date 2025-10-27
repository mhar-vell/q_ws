import matplotlib.pyplot as plt
import numpy as np
import pickle

# Example: Load metrics from a saved file (replace with your actual metrics source)
# with open('rl_metrics.pkl', 'rb') as f:
#     rl_metrics = pickle.load(f)

# For demonstration, use dummy data (replace with your real metrics)
rl_scenarios = ['none', 'random', 'periodic', 'continuous', 'impulse']
rl_metrics = {
    'none':      {'success': 95, 'episodes': 100, 'errors': np.random.normal(0.005, 0.002, 100), 'energy': np.random.normal(10, 2, 100)},
    'random':    {'success': 85, 'episodes': 100, 'errors': np.random.normal(0.02, 0.01, 100), 'energy': np.random.normal(15, 3, 100)},
    'periodic':  {'success': 80, 'episodes': 100, 'errors': np.random.normal(0.03, 0.01, 100), 'energy': np.random.normal(18, 4, 100)},
    'continuous':{'success': 75, 'episodes': 100, 'errors': np.random.normal(0.04, 0.015, 100), 'energy': np.random.normal(20, 5, 100)},
    'impulse':   {'success': 65, 'episodes': 100, 'errors': np.random.normal(0.05, 0.02, 100), 'energy': np.random.normal(25, 6, 100)},
}

# Success Rate Plot
success_rates = [100.0 * rl_metrics[sc]['success'] / rl_metrics[sc]['episodes'] for sc in rl_scenarios]
plt.figure(figsize=(8,4))
plt.bar(rl_scenarios, success_rates, color='skyblue')
plt.ylabel('Success Rate (%)')
plt.title('RL Success Rate by Scenario')
plt.ylim(0, 110)
plt.grid(axis='y')
plt.tight_layout()
plt.show()

# Average Error Plot
avg_errors = [np.mean(rl_metrics[sc]['errors']) for sc in rl_scenarios]
plt.figure(figsize=(8,4))
plt.bar(rl_scenarios, avg_errors, color='salmon')
plt.ylabel('Average Final Error (m)')
plt.title('RL Precision by Scenario')
plt.grid(axis='y')
plt.tight_layout()
plt.show()

# Average Energy Plot
avg_energy = [np.mean(rl_metrics[sc]['energy']) for sc in rl_scenarios]
plt.figure(figsize=(8,4))
plt.bar(rl_scenarios, avg_energy, color='lightgreen')
plt.ylabel('Average Energy (arbitrary units)')
plt.title('RL Energy Use by Scenario')
plt.grid(axis='y')
plt.tight_layout()
plt.show()

print('Done! Replace dummy data with your real metrics for actual results.')
