#!/usr/bin/env python3
"""
AI-Ticker Workflow Status Dashboard
Quick status check for GitHub Actions workflows
"""

import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("❌ requests package not found. Install with: pip install requests")
    sys.exit(1)

class WorkflowDashboard:
    """GitHub Actions workflow status dashboard."""
    
    def __init__(self, repo: str, token: Optional[str] = None):
        self.repo = repo  # format: owner/repo
        self.token = token
        self.api_base = "https://api.github.com"
        
    def get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Ticker-Dashboard"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
    
    def get_workflows(self) -> List[Dict]:
        """Get all workflows for the repository."""
        url = f"{self.api_base}/repos/{self.repo}/actions/workflows"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json().get("workflows", [])
        except requests.RequestException as e:
            print(f"❌ Error fetching workflows: {e}")
            return []
    
    def get_workflow_runs(self, workflow_id: int, limit: int = 5) -> List[Dict]:
        """Get recent runs for a specific workflow."""
        url = f"{self.api_base}/repos/{self.repo}/actions/workflows/{workflow_id}/runs"
        params = {"per_page": limit}
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            return response.json().get("workflow_runs", [])
        except requests.RequestException as e:
            print(f"❌ Error fetching workflow runs: {e}")
            return []
    
    def format_status(self, status: str, conclusion: str) -> str:
        """Format workflow status with emoji."""
        if status == "completed":
            if conclusion == "success":
                return "✅ Success"
            elif conclusion == "failure":
                return "❌ Failed"
            elif conclusion == "cancelled":
                return "⏹️  Cancelled"
            elif conclusion == "skipped":
                return "⏭️  Skipped"
            else:
                return f"❓ {conclusion}"
        elif status == "in_progress":
            return "🔄 Running"
        elif status == "queued":
            return "⏳ Queued"
        else:
            return f"❓ {status}"
    
    def format_duration(self, start_time: str, end_time: Optional[str]) -> str:
        """Calculate and format workflow duration."""
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if end_time:
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration = end - start
                minutes = int(duration.total_seconds() // 60)
                seconds = int(duration.total_seconds() % 60)
                return f"{minutes}m {seconds}s"
            else:
                # Still running
                now = datetime.now(start.tzinfo)
                duration = now - start
                minutes = int(duration.total_seconds() // 60)
                return f"{minutes}m+ (running)"
        except Exception:
            return "Unknown"
    
    def display_dashboard(self):
        """Display the workflow dashboard."""
        print("🔧 AI-Ticker Workflow Dashboard")
        print("=" * 50)
        print(f"Repository: {self.repo}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        workflows = self.get_workflows()
        if not workflows:
            print("❌ No workflows found or API error")
            return
        
        # Filter relevant workflows
        relevant_workflows = [
            w for w in workflows 
            if w['name'] in [
                'Test Coverage',
                'Code Quality', 
                'Security Check',
                'Plugin Validation',
                'Performance Monitoring',
                'Python Package CI',
                'Docker Build',
                'Release'
            ]
        ]
        
        for workflow in relevant_workflows:
            print(f"📊 {workflow['name']}")
            print(f"   File: {workflow['path']}")
            
            runs = self.get_workflow_runs(workflow['id'], 3)
            if runs:
                for i, run in enumerate(runs):
                    status_str = self.format_status(run['status'], run.get('conclusion'))
                    duration = self.format_duration(
                        run['created_at'], 
                        run.get('updated_at')
                    )
                    branch = run.get('head_branch', 'unknown')
                    
                    prefix = "   └─" if i == len(runs) - 1 else "   ├─"
                    print(f"{prefix} {status_str} | {duration} | {branch}")
            else:
                print("   └─ No recent runs")
            print()
        
        # Summary
        success_count = 0
        failed_count = 0
        running_count = 0
        
        for workflow in relevant_workflows:
            runs = self.get_workflow_runs(workflow['id'], 1)
            if runs:
                run = runs[0]
                if run['status'] == 'completed' and run.get('conclusion') == 'success':
                    success_count += 1
                elif run['status'] == 'completed' and run.get('conclusion') == 'failure':
                    failed_count += 1
                elif run['status'] == 'in_progress':
                    running_count += 1
        
        print("📈 Summary")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   🔄 Running: {running_count}")
        print(f"   📊 Total Workflows: {len(relevant_workflows)}")
        
        # Health score
        total = success_count + failed_count
        if total > 0:
            health_score = (success_count / total) * 100
            if health_score >= 90:
                health_emoji = "🟢"
            elif health_score >= 70:
                health_emoji = "🟡"
            else:
                health_emoji = "🔴"
            print(f"   {health_emoji} Health Score: {health_score:.1f}%")

def main():
    """Main function to run the dashboard."""
    import os
    
    # Try to get repo from git remote
    repo = None
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            check=True
        )
        remote_url = result.stdout.strip()
        if 'github.com' in remote_url:
            # Extract owner/repo from URL
            if remote_url.startswith('https://'):
                repo = remote_url.split('github.com/')[-1].replace('.git', '')
            elif remote_url.startswith('git@'):
                repo = remote_url.split(':')[-1].replace('.git', '')
    except subprocess.CalledProcessError:
        pass
    
    # Fallback to default
    if not repo:
        repo = "your-username/ai-ticker"  # Update this with actual repo
    
    # Get GitHub token from environment
    token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        print("💡 Tip: Set GITHUB_TOKEN environment variable for higher rate limits")
        print("   export GITHUB_TOKEN=your_token_here")
        print()
    
    dashboard = WorkflowDashboard(repo, token)
    dashboard.display_dashboard()

if __name__ == "__main__":
    main()
