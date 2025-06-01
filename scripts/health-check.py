#!/usr/bin/env python3
"""
Repository Health Check Script
Analyzes repository health metrics and generates reports
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

def run_command(cmd: str) -> Tuple[str, int]:
    """Run a shell command and return output and exit code."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=False
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def check_file_health() -> Dict:
    """Check health of important files."""
    health = {"status": "healthy", "issues": []}
    
    important_files = [
        "README.md",
        "requirements.txt",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        ".github/workflows/test-coverage.yml",
        "plugins/__init__.py",
        "tests/__init__.py"
    ]
    
    for file_path in important_files:
        if not Path(file_path).exists():
            health["issues"].append(f"Missing important file: {file_path}")
            health["status"] = "warning"
    
    # Check if requirements.txt is reasonable size
    try:
        with open("requirements.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            if len(lines) > 100:
                health["issues"].append(f"requirements.txt has {len(lines)} packages - consider optimization")
                health["status"] = "warning"
    except Exception:
        pass
    
    return health

def check_code_quality() -> Dict:
    """Check code quality metrics."""
    health = {"status": "healthy", "issues": [], "metrics": {}}
    
    # Count Python files
    python_files = list(Path(".").rglob("*.py"))
    health["metrics"]["python_files"] = len([f for f in python_files if ".git" not in str(f)])
    
    # Check for __pycache__ directories
    pycache_dirs = list(Path(".").rglob("__pycache__"))
    if len(pycache_dirs) > 0:
        health["issues"].append(f"Found {len(pycache_dirs)} __pycache__ directories - should be in .gitignore")
        health["status"] = "warning"
    
    # Check for .pyc files
    pyc_files = list(Path(".").rglob("*.pyc"))
    if len(pyc_files) > 0:
        health["issues"].append(f"Found {len(pyc_files)} .pyc files - should be in .gitignore")
        health["status"] = "warning"
    
    # Check test coverage
    try:
        test_files = list(Path("tests").rglob("test_*.py"))
        health["metrics"]["test_files"] = len(test_files)
        
        if len(test_files) < 3:
            health["issues"].append("Low test coverage - consider adding more tests")
            health["status"] = "warning"
    except Exception:
        health["issues"].append("Tests directory structure issue")
        health["status"] = "warning"
    
    return health

def check_plugin_health() -> Dict:
    """Check plugin system health."""
    health = {"status": "healthy", "issues": [], "metrics": {}}
    
    try:
        # Count builtin plugins
        builtin_plugins = list(Path("plugins/builtin").glob("*_provider.py"))
        health["metrics"]["builtin_plugins"] = len(builtin_plugins)
        
        # Count custom plugins
        custom_plugins = list(Path("plugins/custom").rglob("*.py"))
        custom_plugins = [p for p in custom_plugins if p.name != "__init__.py"]
        health["metrics"]["custom_plugins"] = len(custom_plugins)
        
        # Check plugin structure
        required_plugin_files = [
            "plugins/__init__.py",
            "plugins/base_provider.py",
            "plugins/plugin_manager.py",
            "plugins/registry.py"
        ]
        
        for file_path in required_plugin_files:
            if not Path(file_path).exists():
                health["issues"].append(f"Missing plugin file: {file_path}")
                health["status"] = "critical"
        
        # Check if there are any plugins at all
        if len(builtin_plugins) == 0:
            health["issues"].append("No builtin plugins found")
            health["status"] = "warning"
    
    except Exception as e:
        health["issues"].append(f"Plugin system check failed: {e}")
        health["status"] = "critical"
    
    return health

def check_dependencies() -> Dict:
    """Check dependency health."""
    health = {"status": "healthy", "issues": [], "metrics": {}}
    
    try:
        # Check requirements.txt
        if Path("requirements.txt").exists():
            with open("requirements.txt", "r") as f:
                deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                health["metrics"]["total_dependencies"] = len(deps)
                
                # Check for version pinning
                pinned = [dep for dep in deps if "==" in dep]
                health["metrics"]["pinned_dependencies"] = len(pinned)
                
                pin_ratio = len(pinned) / len(deps) if deps else 0
                if pin_ratio < 0.8:
                    health["issues"].append(f"Only {pin_ratio:.1%} of dependencies are pinned")
                    health["status"] = "warning"
        
        # Check for security issues (if safety is available)
        safety_output, safety_code = run_command("safety check --json")
        if safety_code == 0:
            health["metrics"]["security_issues"] = 0
        else:
            try:
                safety_data = json.loads(safety_output)
                if isinstance(safety_data, list) and len(safety_data) > 0:
                    health["metrics"]["security_issues"] = len(safety_data)
                    health["issues"].append(f"Found {len(safety_data)} security vulnerabilities")
                    health["status"] = "critical"
            except:
                health["issues"].append("Could not parse safety check results")
                health["status"] = "warning"
    
    except Exception as e:
        health["issues"].append(f"Dependency check failed: {e}")
        health["status"] = "warning"
    
    return health

def check_git_health() -> Dict:
    """Check git repository health."""
    health = {"status": "healthy", "issues": [], "metrics": {}}
    
    try:
        # Check if we're in a git repo
        _, git_code = run_command("git status")
        if git_code != 0:
            health["issues"].append("Not in a git repository")
            health["status"] = "critical"
            return health
        
        # Check for uncommitted changes
        diff_output, _ = run_command("git diff --name-only")
        if diff_output:
            staged_files = diff_output.split('\n')
            health["metrics"]["uncommitted_files"] = len(staged_files)
            if len(staged_files) > 10:
                health["issues"].append(f"Many uncommitted files: {len(staged_files)}")
                health["status"] = "warning"
        
        # Check recent commit activity
        commits_output, _ = run_command("git log --oneline --since='30 days ago'")
        recent_commits = len(commits_output.split('\n')) if commits_output else 0
        health["metrics"]["recent_commits"] = recent_commits
        
        if recent_commits == 0:
            health["issues"].append("No commits in the last 30 days")
            health["status"] = "warning"
        
        # Check branch protection (if on GitHub)
        current_branch, _ = run_command("git branch --show-current")
        health["metrics"]["current_branch"] = current_branch
    
    except Exception as e:
        health["issues"].append(f"Git health check failed: {e}")
        health["status"] = "warning"
    
    return health

def generate_report(health_data: Dict) -> str:
    """Generate a markdown health report."""
    report = []
    report.append("# Repository Health Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("")
    
    # Overall status
    critical_issues = sum(1 for check in health_data.values() if check.get("status") == "critical")
    warning_issues = sum(1 for check in health_data.values() if check.get("status") == "warning")
    
    if critical_issues > 0:
        report.append("## 🔴 Overall Status: CRITICAL")
        report.append(f"Found {critical_issues} critical issues that need immediate attention.")
    elif warning_issues > 0:
        report.append("## 🟡 Overall Status: WARNING")
        report.append(f"Found {warning_issues} issues that should be addressed.")
    else:
        report.append("## 🟢 Overall Status: HEALTHY")
        report.append("All health checks passed!")
    
    report.append("")
    
    # Detailed results
    for check_name, check_data in health_data.items():
        status_emoji = {
            "healthy": "🟢",
            "warning": "🟡", 
            "critical": "🔴"
        }.get(check_data.get("status", "unknown"), "❓")
        
        report.append(f"## {status_emoji} {check_name.replace('_', ' ').title()}")
        
        if check_data.get("metrics"):
            report.append("### Metrics")
            for metric, value in check_data["metrics"].items():
                report.append(f"- **{metric.replace('_', ' ').title()}**: {value}")
            report.append("")
        
        if check_data.get("issues"):
            report.append("### Issues")
            for issue in check_data["issues"]:
                report.append(f"- {issue}")
            report.append("")
        else:
            report.append("No issues found.")
            report.append("")
    
    # Recommendations
    report.append("## 🎯 Recommendations")
    
    if critical_issues > 0:
        report.append("### Critical Actions Needed")
        for check_name, check_data in health_data.items():
            if check_data.get("status") == "critical":
                for issue in check_data.get("issues", []):
                    report.append(f"- **{check_name}**: {issue}")
        report.append("")
    
    if warning_issues > 0:
        report.append("### Improvements Suggested")
        for check_name, check_data in health_data.items():
            if check_data.get("status") == "warning":
                for issue in check_data.get("issues", []):
                    report.append(f"- **{check_name}**: {issue}")
        report.append("")
    
    if critical_issues == 0 and warning_issues == 0:
        report.append("- Continue with current practices")
        report.append("- Regular monitoring is working well")
        report.append("- Consider adding more automated checks")
    
    return "\n".join(report)

def main():
    """Run all health checks and generate report."""
    print("🔍 Running repository health checks...")
    
    # Run all health checks
    health_data = {
        "file_health": check_file_health(),
        "code_quality": check_code_quality(),
        "plugin_health": check_plugin_health(),
        "dependencies": check_dependencies(),
        "git_health": check_git_health()
    }
    
    # Generate report
    report = generate_report(health_data)
    
    # Write report to file
    with open("health-results.md", "w") as f:
        f.write(report)
    
    # Print summary
    critical_issues = sum(1 for check in health_data.values() if check.get("status") == "critical")
    warning_issues = sum(1 for check in health_data.values() if check.get("status") == "warning")
    
    print(f"Health check complete!")
    print(f"Critical issues: {critical_issues}")
    print(f"Warning issues: {warning_issues}")
    
    # Set GitHub Actions output
    if os.environ.get("GITHUB_ACTIONS"):
        with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as f:
            f.write(f"critical_issues={'true' if critical_issues > 0 else 'false'}\n")
            f.write(f"warning_issues={warning_issues}\n")
    
    # Exit with appropriate code
    if critical_issues > 0:
        sys.exit(1)
    elif warning_issues > 0:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
