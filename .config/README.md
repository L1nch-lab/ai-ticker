# Configuration Files

This folder contains configuration files that are relevant for the project but don't need to be in the root directory.

## Included Files

- `.editorconfig` - Editor settings for consistent formatting
- `.flake8` - Python linting rules
- `.gitignore` - Patterns for files that should be ignored in the .config folder

## Usage

Most tools will automatically find these configurations. If not, they can be specified explicitly:

```bash
# Flake8 with custom configuration
flake8 --config=.config/.flake8
```
