# 📦 Archive System - Episode & Session Data

This directory contains all historical training and simulation data, automatically organized and preserved.

## 📁 Directory Structure

```
archives/
├── episode_data/           # Individual episode performance data
├── scenario_reports/       # Completed scenario summaries  
├── session_summaries/      # Complete session archives
└── README.md              # This file
```

## 🔄 Automatic Archiving System

### **When Archiving Happens**
- **Training Start**: All existing root-level data files automatically archived
- **Session Summary**: Complete session data archived when pressing 'j'
- **Scenario Completion**: Scenario reports saved directly to archives
- **Episode Completion**: Episode data saved directly to archives

### **What Gets Archived**
- **Episode Data**: Individual trajectory performance with component-wise analysis
- **Scenario Reports**: Comprehensive disturbance scenario completion statistics
- **Session Summaries**: Complete training session performance and statistics
- **Archive Metadata**: Timestamps, file counts, and organization information

## 📊 Data Structure

### **Episode Data Files** (`episode_data/`)
Each episode contains:
```json
{
  "episode_number": 1,
  "scenario": "random",
  "direction": "random", 
  "intensity": "normal",
  "duration": 45.2,
  "samples_count": 1087,
  "circles_completed": 2.3,
  "avg_accuracy": 78.5,
  "avg_error": 0.245,
  "avg_accuracy_x": 82.1,
  "avg_accuracy_y": 77.8,
  "avg_accuracy_z": 75.6,
  "avg_error_x": 0.198,
  "avg_error_y": 0.267,
  "avg_error_z": 0.289,
  "completion_time": "2025-10-15T20:05:30"
}
```

### **Scenario Reports** (`scenario_reports/`)
Scenario completion summaries:
```json
{
  "scenario": "random",
  "episodes_count": 5,
  "total_duration": 248.7,
  "avg_accuracy": 76.4,
  "avg_error": 0.278,
  "total_circles": 11.8,
  "best_episode_accuracy": 85.2,
  "component_analysis": {
    "avg_accuracy_x": 79.1,
    "avg_accuracy_y": 75.3,
    "avg_accuracy_z": 74.8
  }
}
```

### **Session Summaries** (`session_summaries/`)
Complete training session archives:
```json
{
  "session_info": {
    "total_episodes": 25,
    "session_duration": 1247.8,
    "start_time": 1697385930.123,
    "end_time": 1697387177.945
  },
  "performance_summary": {
    "overall_accuracy": 78.9,
    "overall_error": 0.256,
    "total_circles": 57.8,
    "component_analysis": {
      "avg_accuracy_x": 81.2,
      "avg_accuracy_y": 78.1,
      "avg_accuracy_z": 77.4
    }
  },
  "scenario_breakdown": {
    "none": {"episode_count": 5, "avg_accuracy": 89.2},
    "random": {"episode_count": 5, "avg_accuracy": 76.4},
    "periodic": {"episode_count": 5, "avg_accuracy": 79.1},
    "continuous": {"episode_count": 5, "avg_accuracy": 74.7},
    "impulse": {"episode_count": 5, "avg_accuracy": 74.7}
  },
  "episodes": [/* all episode data */]
}
```

## 🎯 Benefits of Archive System

### **Data Preservation**
- **No Data Loss**: All training data permanently preserved
- **Version Control**: Timestamped files prevent overwrites
- **Session Isolation**: Each training session clearly separated
- **Progressive Tracking**: Complete history of performance improvements

### **Analysis Capabilities**
- **Performance Trends**: Track accuracy improvements over time
- **Scenario Comparison**: Compare disturbance scenario performance
- **Component Analysis**: Detailed X,Y,Z trajectory following analysis
- **Training Efficiency**: Duration and convergence rate tracking

### **Research & Development**
- **Baseline Comparison**: Compare new training approaches against historical data
- **Algorithm Evaluation**: Performance metrics across different scenarios
- **Hyperparameter Tuning**: Archive results from different configurations
- **Publication Data**: Complete datasets for research publications

## 🚀 Usage Examples

### **Analyzing Recent Performance**
```bash
# View latest session summary
cat archives/session_summaries/session_summary_20251015_*.json | jq '.performance_summary'

# Check episode progression
ls -la archives/episode_data/ | tail -10
```

### **Scenario Performance Comparison**
```bash
# Compare scenario completion rates
grep -l "random" archives/scenario_reports/*.json
grep -l "impulse" archives/scenario_reports/*.json
```

### **Historical Analysis**
```bash
# Find best performing episodes
grep -h "avg_accuracy" archives/episode_data/*.json | sort -n | tail -5
```

## 📈 Archive Statistics

- **Storage Format**: JSON (human-readable, analysis-friendly)
- **File Naming**: Timestamp-based (YYYYMMDD_HHMMSS)
- **Data Integrity**: Each file self-contained and complete
- **Compression**: Optional compression available for large datasets

## 🛠️ Maintenance

### **Archive Management**
- **Automatic Cleanup**: No manual intervention required
- **Size Monitoring**: Archives grow with training data
- **Backup Friendly**: Standard JSON format for easy backup
- **Version Safe**: No file overwrites or data corruption risk

### **Data Export**
Archives can be easily exported for:
- **Research Analysis**: Import into Python/MATLAB/R
- **Visualization**: Create performance charts and graphs
- **Reporting**: Generate training progress reports
- **Sharing**: Transfer data between systems

---

**Archive System Features**: ✅ Automatic ✅ Timestamped ✅ Comprehensive ✅ Analysis-Ready

**Total Data Preserved**: Episodes + Scenarios + Sessions + Metadata  
**Storage Format**: JSON (human-readable)  
**Organization**: Chronological with categorical separation