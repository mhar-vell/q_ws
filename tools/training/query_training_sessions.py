#!/usr/bin/env python3
"""
Query and compare training sessions.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class TrainingSessionManager:
    def __init__(self, base_path="archives/02_training_sessions"):
        self.base_path = base_path
        self.sessions = self._load_sessions()
    
    def _load_sessions(self):
        """Load all training session manifests."""
        sessions = []
        
        if not os.path.exists(self.base_path):
            print(f"⚠️  Training sessions directory not found: {self.base_path}")
            return sessions
        
        for session_dir in os.listdir(self.base_path):
            if not session_dir.startswith("training_"):
                continue
            
            manifest_path = f"{self.base_path}/{session_dir}/manifest.json"
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    manifest['session_dir'] = session_dir
                    sessions.append(manifest)
        
        # Sort by date (most recent first)
        sessions.sort(key=lambda s: s['session_info']['date_started'], reverse=True)
        
        return sessions
    
    def list_sessions(self, status: Optional[str] = None, tags: Optional[List[str]] = None):
        """List training sessions with filters."""
        filtered = self.sessions
        
        if status:
            filtered = [s for s in filtered if s['session_info']['status'] == status]
        
        if tags:
            filtered = [
                s for s in filtered 
                if any(tag in s.get('tags', []) for tag in tags)
            ]
        
        if not filtered:
            print("\n📋 No training sessions found matching criteria.")
            return
        
        print(f"\n📋 Found {len(filtered)} training session(s):\n")
        print("=" * 100)
        
        for session in filtered:
            info = session['session_info']
            results = session.get('results_summary', {})
            
            status_icon = {
                'completed': '✅',
                'in_progress': '🟡',
                'failed': '❌'
            }.get(info['status'], '❓')
            
            print(f"\n{status_icon} {info['session_id']}")
            print(f"   📅 Date: {info['date_started'][:10]}")
            print(f"   🔧 Status: {info['status'].upper()}")
            print(f"   🎯 Algorithm: {session['algorithm']['name']}")
            print(f"   📊 Episodes: {session['training_config']['episodes_per_scenario']} per scenario")
            
            sr = results.get('overall_success_rate')
            if sr is not None:
                print(f"   ✨ Success Rate: {sr}%")
            else:
                print(f"   ✨ Success Rate: N/A (training in progress or not completed)")
            
            if session.get('tags'):
                print(f"   🏷️  Tags: {', '.join(session.get('tags', []))}")
            
            if session.get('notes', {}).get('purpose'):
                print(f"   📝 Purpose: {session['notes']['purpose']}")
        
        print("\n" + "=" * 100 + "\n")
    
    def compare_sessions(self, session_ids: List[str]):
        """Compare multiple training sessions."""
        if not session_ids:
            print("⚠️  No session IDs provided for comparison")
            return
        
        sessions_data = []
        
        for session_id in session_ids:
            session = next((s for s in self.sessions 
                          if s['session_info']['session_id'] == session_id), None)
            
            if session:
                info = session['session_info']
                results = session.get('results_summary', {})
                
                sessions_data.append({
                    'Session ID': session_id,
                    'Date': info['date_started'][:10],
                    'Algorithm': session['algorithm']['name'],
                    'Episodes/Scenario': session['training_config']['episodes_per_scenario'],
                    'Status': info['status'],
                    'Overall SR (%)': results.get('overall_success_rate', 'N/A'),
                    'Normal SR (%)': results.get('normal_intensity_success_rate', 'N/A'),
                    'Golden SR (%)': results.get('golden_intensity_success_rate', 'N/A'),
                    'Robustness Index': results.get('robustness_index', 'N/A'),
                    'Duration (min)': info.get('duration_minutes', 'N/A')
                })
            else:
                print(f"⚠️  Session not found: {session_id}")
        
        if not sessions_data:
            print("❌ No valid sessions found for comparison")
            return
        
        print("\n📊 Training Session Comparison:\n")
        print("=" * 120)
        
        # Print header
        if sessions_data:
            headers = list(sessions_data[0].keys())
            header_line = " | ".join(f"{h:20}" for h in headers)
            print(header_line)
            print("-" * 120)
            
            # Print data
            for row in sessions_data:
                data_line = " | ".join(f"{str(row[h]):20}" for h in headers)
                print(data_line)
        
        print("=" * 120 + "\n")
    
    def get_best_session(self, metric: str = 'overall_success_rate'):
        """Find best performing session."""
        completed = [s for s in self.sessions 
                    if s['session_info']['status'] == 'completed']
        
        if not completed:
            print("⚠️  No completed sessions found")
            return None
        
        # Filter sessions that have the metric
        with_metric = [s for s in completed 
                      if s.get('results_summary', {}).get(metric) is not None]
        
        if not with_metric:
            print(f"⚠️  No sessions found with metric: {metric}")
            return None
        
        best = max(with_metric, 
                  key=lambda s: s.get('results_summary', {}).get(metric, 0))
        
        print(f"\n🏆 Best session by {metric}:")
        print(f"   Session: {best['session_info']['session_id']}")
        print(f"   {metric}: {best['results_summary'][metric]}")
        print(f"   Date: {best['session_info']['date_started'][:10]}")
        print(f"   Algorithm: {best['algorithm']['name']}")
        print()
        
        return best
    
    def get_session_details(self, session_id: str):
        """Get detailed information about a specific session."""
        session = next((s for s in self.sessions 
                       if s['session_info']['session_id'] == session_id), None)
        
        if not session:
            print(f"❌ Session not found: {session_id}")
            return None
        
        print(f"\n📋 Training Session Details:\n")
        print("=" * 100)
        print(json.dumps(session, indent=2))
        print("=" * 100 + "\n")
        
        return session
    
    def get_primary_session(self):
        """Get the primary/main training session."""
        # Check experiment index for primary flag
        if os.path.exists("experiment_index.json"):
            with open("experiment_index.json", 'r') as f:
                index = json.load(f)
                primary_sessions = [s for s in index.get('training_sessions', []) 
                                   if s.get('primary', False)]
                if primary_sessions:
                    session_id = primary_sessions[0]['session_id']
                    return self.get_session_details(session_id)
        
        print("⚠️  No primary session marked in experiment_index.json")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Query training sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all sessions
  python query_training_sessions.py --list
  
  # List completed sessions only
  python query_training_sessions.py --list --status completed
  
  # List sessions with specific tags
  python query_training_sessions.py --list --tags thesis-main publication
  
  # Compare two sessions
  python query_training_sessions.py --compare training_20251015_dqn_dual_intensity_500ep_v1.0 training_20251118_rainbow_triple_intensity_1000ep_v2.0
  
  # Find best session
  python query_training_sessions.py --best overall_success_rate
  
  # Get session details
  python query_training_sessions.py --details training_20251015_dqn_dual_intensity_500ep_v1.0
  
  # Get primary session
  python query_training_sessions.py --primary
        """
    )
    parser.add_argument("--list", action="store_true", help="List all sessions")
    parser.add_argument("--status", help="Filter by status (completed, in_progress, failed)")
    parser.add_argument("--tags", nargs="+", help="Filter by tags")
    parser.add_argument("--compare", nargs="+", help="Compare sessions by ID")
    parser.add_argument("--best", help="Find best session by metric (e.g., overall_success_rate)")
    parser.add_argument("--details", help="Get detailed info for a specific session")
    parser.add_argument("--primary", action="store_true", help="Show primary training session")
    
    args = parser.parse_args()
    
    manager = TrainingSessionManager()
    
    if args.list:
        manager.list_sessions(status=args.status, tags=args.tags)
    elif args.compare:
        manager.compare_sessions(args.compare)
    elif args.best:
        manager.get_best_session(metric=args.best)
    elif args.details:
        manager.get_session_details(args.details)
    elif args.primary:
        manager.get_primary_session()
    else:
        parser.print_help()
