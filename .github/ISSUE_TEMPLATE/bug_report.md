---
name: Bug Report
about: Create a report to help us improve AI-Ticker
title: '[BUG] Brief description of the issue'
labels: ['bug', 'needs-triage']
assignees: ''

---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 🔄 To Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## ✅ Expected Behavior
A clear and concise description of what you expected to happen.

## 📸 Screenshots
If applicable, add screenshots to help explain your problem.

## 🔧 Environment
- **OS**: [e.g. Ubuntu 22.04, macOS 13.0, Windows 11]
- **Python Version**: [e.g. 3.11.5, 3.12.1, 3.13.0]
- **AI-Ticker Version**: [e.g. v1.1.0]
- **Browser** (if web interface): [e.g. Chrome 120, Firefox 121]

## 🔌 Plugin Information
- **Affected Plugins**: [e.g. OpenRouter, DeepInfra, Custom Plugin]
- **Plugin Versions**: [if applicable]
- **Plugin Configuration**: [sanitized config, remove API keys]

## 📋 Additional Context
- **Error Messages**: [paste full error messages]
- **Log Output**: [relevant log entries]
- **Configuration**: [sanitized configuration that might be relevant]

## 🔍 Debugging Information
<!-- Run the following commands and paste the output -->

<details>
<summary>System Information</summary>

```bash
# Python version
python --version

# AI-Ticker version (if installed)
python -c "import app; print(getattr(app, '__version__', 'Unknown'))"

# Plugin status
python -c "from plugins.plugin_manager import PluginManager; pm = PluginManager(); print([p.name for p in pm.get_enabled_plugins()])"
```

</details>

<details>
<summary>Error Traceback</summary>

```
Paste the full error traceback here
```

</details>

## 🎯 Impact
- [ ] Blocks core functionality
- [ ] Breaks plugin system
- [ ] UI/UX issue
- [ ] Performance degradation
- [ ] Security concern
- [ ] Documentation issue

## 💡 Possible Solution
If you have ideas on how to fix this, please describe them here.

## 📝 Additional Notes
Add any other context about the problem here.

---

### Checklist
- [ ] I have searched existing issues to avoid duplicates
- [ ] I have provided all requested information
- [ ] I have sanitized any sensitive information (API keys, etc.)
- [ ] I have tested with the latest version
- [ ] I have included relevant logs/error messages
