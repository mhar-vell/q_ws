#!/bin/bash
# RL Checkpoint Management Script
# Helps manage large checkpoint files that are excluded from Git

echo "🗄️  RL Checkpoint File Management"
echo "================================="

# Function to show checkpoint file sizes
show_checkpoint_sizes() {
    echo "📊 Current checkpoint file sizes:"
    echo "--------------------------------"
    
    if ls rl_checkpoint_*.pkl 1> /dev/null 2>&1; then
        echo "📦 Q-Learning checkpoints (.pkl files):"
        ls -lh rl_checkpoint_*.pkl | awk '{print "   " $9 ": " $5}'
        echo
    fi
    
    if ls rl_checkpoint_*.pth 1> /dev/null 2>&1; then
        echo "🧠 DQN checkpoints (.pth files):"
        ls -lh rl_checkpoint_*.pth | awk '{print "   " $9 ": " $5}'
        echo
    fi
    
    if ls rl_final_*.pkl 1> /dev/null 2>&1; then
        echo "🏁 Final Q-Learning models (.pkl files):"
        ls -lh rl_final_*.pkl | awk '{print "   " $9 ": " $5}'
        echo
    fi
    
    if ls rl_final_*.pth 1> /dev/null 2>&1; then
        echo "🎯 Final DQN models (.pth files - tracked in Git):"
        ls -lh rl_final_*.pth | awk '{print "   " $9 ": " $5}'
        echo
    fi
}

# Function to archive old checkpoints
archive_checkpoints() {
    echo "📦 Archiving old checkpoint files..."
    
    # Create archive directory
    mkdir -p checkpoint_archive/$(date +%Y%m%d_%H%M%S)
    archive_dir="checkpoint_archive/$(date +%Y%m%d_%H%M%S)"
    
    # Move old checkpoints (keep only every 500 episodes)
    if ls rl_checkpoint_*_ep[1-4][0-9][0-9]_*.pkl 1> /dev/null 2>&1; then
        mv rl_checkpoint_*_ep[1-4][0-9][0-9]_*.pkl "$archive_dir/"
        echo "✅ Archived intermediate Q-Learning checkpoints to $archive_dir"
    fi
    
    if ls rl_checkpoint_*_ep[1-4][0-9][0-9]_*.pth 1> /dev/null 2>&1; then
        mv rl_checkpoint_*_ep[1-4][0-9][0-9]_*.pth "$archive_dir/"
        echo "✅ Archived intermediate DQN checkpoints to $archive_dir"
    fi
    
    echo "📁 Archive created: $archive_dir"
    echo "💾 Kept: Episodes 500, 1000, 1500, 2000 + final models"
}

# Function to clean up very large files
cleanup_large_files() {
    echo "🧹 Cleaning up files larger than 200MB..."
    
    find . -name "rl_checkpoint_*.pkl" -size +200M -exec ls -lh {} \; | while read -r file; do
        echo "🗑️  Large file found: $file"
        read -p "Delete this file? [y/N]: " confirm
        if [[ $confirm == [yY] ]]; then
            rm "$file"
            echo "✅ Deleted: $file"
        fi
    done
}

# Main menu
case "${1:-menu}" in
    "show"|"list")
        show_checkpoint_sizes
        ;;
    "archive")
        show_checkpoint_sizes
        echo
        read -p "Archive old checkpoints? This will move intermediate files to archive folder [y/N]: " confirm
        if [[ $confirm == [yY] ]]; then
            archive_checkpoints
        fi
        ;;
    "clean")
        cleanup_large_files
        ;;
    "menu"|*)
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  show    - Display checkpoint file sizes"
        echo "  archive - Archive old intermediate checkpoints"
        echo "  clean   - Interactive cleanup of very large files"
        echo
        echo "💡 Note: Large checkpoint files are excluded from Git to avoid GitHub limits"
        echo "   Only rl_final_*.pth files are tracked in the repository"
        echo
        show_checkpoint_sizes
        ;;
esac