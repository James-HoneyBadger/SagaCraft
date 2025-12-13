# Contributing to SagaCraft

**Thank you for your interest in contributing!**

Copyright © 2025 Honey Badger Universe  
License: MIT

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contribution Guidelines](#contribution-guidelines)
5. [Code Style](#code-style)
6. [Testing](#testing)
7. [Pull Request Process](#pull-request-process)
8. [Project Structure](#project-structure)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Our Standards

**Positive Behavior**:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards others

**Unacceptable Behavior**:
- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct inappropriate in a professional setting

### Enforcement

Violations may be reported to: support@honeybadgeruniverse.com

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git for version control
- Text editor or IDE (VS Code, PyCharm recommended)
- Basic understanding of Python

### First Contribution

1. **Find an Issue**
   - Browse [GitHub Issues](../../issues)
   - Look for "good first issue" label
   - Comment to claim the issue

2. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub
    git clone https://github.com/YOUR_USERNAME/SagaCraft.git
    cd SagaCraft
   ```

3. **Create Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

5. **Submit Pull Request**
   - Push to your fork
   - Open PR on main repository
   - Wait for review

---

## Development Setup

### Local Environment

```bash
# Clone repository
git clone https://github.com/James-HoneyBadger/SagaCraft.git
cd SagaCraft

# (Optional) Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Install development tooling (pytest, flake8, etc.) if not available globally
python -m pip install pytest flake8

# Run tests
python -m pytest tests/

# Launch IDE
python -m src.acs.ui.ide
```

### Development Tools

**Recommended**:
- **Editor**: VS Code with Python extension
- **Linter**: pylint, flake8
- **Formatter**: black, autopep8
- **Testing**: pytest
- **Git**: Pre-commit hooks

**VS Code Setup**:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

---

## Contribution Guidelines

### Types of Contributions

#### 🐛 Bug Reports

**Before Submitting**:
- Check existing issues
- Test on latest version
- Verify it's reproducible

**Issue Template**:
```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: Linux/Mac/Windows
- Python Version: 3.x
- Version: 2.0

**Additional Context**
Screenshots, error logs, etc.
```

#### ✨ Feature Requests

**Before Submitting**:
- Check existing requests
- Ensure it aligns with project goals
- Consider if it could be a plugin

**Request Template**:
```markdown
**Feature Description**
What feature do you want?

**Use Case**
Why is this useful?

**Proposed Solution**
How could it work?

**Alternatives Considered**
Other approaches

**Additional Context**
Mockups, examples, etc.
```

#### 📝 Documentation

**Always Welcome**:
- Fixing typos
- Clarifying explanations
- Adding examples
- Translating to other languages

#### 🔌 Plugins

**Plugin Contributions**:
- Follow plugin API
- Include documentation
- Add example usage
- Write tests

#### 🎨 Themes

**Theme Contributions**:
- Follow theme structure
- Test readability
- Include screenshot
- Consider accessibility

---

## Code Style

### Python Style Guide

Follow **PEP 8** with these specifics:

#### Indentation
```python
# Use 4 spaces (no tabs)
def my_function():
    if condition:
        do_something()
```

#### Naming Conventions
```python
# Classes: PascalCase
class GameEngine:
    pass

# Functions/Variables: snake_case
def parse_command(input_text):
    player_name = "Hero"

# Constants: UPPER_SNAKE_CASE
MAX_INVENTORY_SIZE = 50

# Private: Leading underscore
def _internal_helper():
    pass
```

#### Imports
```python
# Standard library first
import os
import sys

# Third-party second
import requests

# Local last
from acs_parser import parse_sentence
from acs_engine import GameEngine
```

#### Docstrings
```python
def parse_sentence(sentence):
    """
    Parse natural language command into structured action.
    
    Args:
        sentence (str): Raw player input
        
    Returns:
        dict: Parsed command structure with 'action' and 'target'
        
    Example:
        >>> parse_sentence("go north")
        {"action": "move", "direction": "north"}
    """
    pass
```

#### Comments
```python
# Good: Explain WHY, not WHAT
# Use cached value to avoid expensive recalculation
result = cache.get(key)

# Bad: States the obvious
# Set x to 5
x = 5
```

### File Structure

```python
"""
Module docstring explaining purpose.

Copyright © 2025 Honey Badger Universe
License: MIT
"""

# Imports
import standard_library
from local_module import something

# Constants
DEFAULT_VALUE = 100

# Classes
class MyClass:
    """Class docstring."""
    pass

# Functions
def my_function():
    """Function docstring."""
    pass

# Main execution
if __name__ == "__main__":
    main()
```

---

## Testing

### Writing Tests

**Test Files**: `tests/test_*.py`

**Test Structure**:
```python
import pytest
from acs_parser import parse_sentence

class TestParser:
    """Test suite for command parser."""
    
    def test_movement_command(self):
        """Test basic movement parsing."""
        result = parse_sentence("go north")
        assert result['action'] == 'move'
        assert result['direction'] == 'north'
        
    def test_invalid_input(self):
        """Test handling of invalid input."""
        result = parse_sentence("")
        assert result['action'] == 'unknown'
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_parser_detailed.py

# Run with coverage
python -m pytest --cov=. tests/

# Run specific test
python -m pytest tests/test_parser.py::TestParser::test_movement
```

### Test Coverage

**Requirements**:
- New features: 80%+ coverage
- Bug fixes: Add regression test
- Parser changes: Update parser tests
- Critical code: 100% coverage

**Check Coverage**:
```bash
python -m pytest --cov=. --cov-report=html tests/
# Open htmlcov/index.html
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guide
- [ ] Tests pass locally
- [ ] Added tests for new features
- [ ] Updated documentation
- [ ] Commits are clean and descriptive
- [ ] No merge conflicts

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes

## Related Issues
Fixes #123
```

### Review Process

1. **Automated Checks**
   - Tests must pass
   - Linting must pass
   - No conflicts

2. **Code Review**
   - At least one approval required
   - Address all comments
   - Keep discussion constructive

3. **Merge**
   - Squash commits if needed
   - Update changelog
   - Thank contributor!

### Commit Messages

**Format**:
```
type(scope): Brief description

Longer description if needed.

Fixes #123
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples**:
```
feat(parser): Add support for pronoun resolution

Adds basic "it" and "them" pronoun support by tracking
the last mentioned object or NPC.

Fixes #456
```

```
fix(combat): Correct damage calculation

Armor was being applied twice. Now correctly subtracts
armor rating once from damage.

Fixes #789
```

---

## Project Structure

### Core Components

```
core/
├── engine.py         # Main game engine
├── state.py          # Game state management
└── events.py         # Event system

systems/
├── combat.py         # Combat mechanics
├── npc_context.py    # NPC AI
├── environment.py    # Environmental effects
├── journal.py        # Quest tracking
└── achievements.py   # Achievement system

utils/
├── parser.py         # Command parser
├── validator.py      # Data validation
└── helpers.py        # Helper functions

ui/
└── ide.py            # IDE interface

plugins/
├── base.py           # Plugin base class
└── examples/         # Example plugins
```

### Adding New Features

#### 1. New Command

**Parser** (`acs_parser.py`):
```python
verb_map["dance"] = ["dance", "boogie", "groove"]
```

**Handler** (`acs_engine_enhanced.py`):
```python
def handle_dance(command):
    """Handle dance command."""
    return "You dance merrily!"

command_handlers["dance"] = handle_dance
```

**Test** (`tests/test_commands.py`):
```python
def test_dance_command():
    result = parse_sentence("dance")
    assert result['action'] == 'dance'
```

#### 2. New System

**Create Module** (`systems/new_system.py`):
```python
"""New system description."""

class NewSystem:
    def __init__(self, engine):
        self.engine = engine
        
    def initialize(self):
        """Set up system."""
        pass
        
    def update(self, state):
        """Update each turn."""
        pass
```

**Register** (`acs_engine_enhanced.py`):
```python
from systems.new_system import NewSystem

self.systems.append(NewSystem(self))
```

**Test** (`tests/test_new_system.py`):
```python
def test_new_system():
    system = NewSystem(mock_engine)
    system.initialize()
    # Test functionality
```

#### 3. New Plugin

**Create Plugin** (`plugins/my_plugin.py`):
```python
from plugins.base import Plugin

class MyPlugin(Plugin):
    def __init__(self, engine):
        super().__init__(engine)
        self.name = "My Plugin"
        
    def initialize(self):
        """Set up plugin."""
        pass
```

**Documentation** (`plugins/my_plugin/README.md`):
- What it does
- How to use
- Configuration options
- Examples

---

## Documentation

### Updating Docs

**When to Update**:
- New features → User Manual
- API changes → Technical Reference
- New commands → Command Reference
- Architecture changes → Architecture doc

**Markdown Style**:
- Use headers properly (h1, h2, h3)
- Code blocks with language tags
- Tables for comparisons
- Examples for clarity

### Documentation Files

```
docs/
├── USER_MANUAL.md          # For players and creators
├── TECHNICAL_REFERENCE.md  # For developers
├── CONTRIBUTING.md         # This file
├── QUICKSTART.md           # 5-minute guide
├── COMMANDS.md             # Command reference
├── PLUGIN_GUIDE.md         # Plugin development
└── ARCHITECTURE.md         # System design
```

---

## Getting Help

### Resources

- **User Manual**: `docs/USER_MANUAL.md`
- **Technical Reference**: `docs/TECHNICAL_REFERENCE.md`
- **API Docs**: `docs/TECHNICAL_REFERENCE.md#api-reference`
- **Examples**: `plugins/examples/`

### Communication

- **GitHub Issues**: Bug reports, features
- **GitHub Discussions**: Questions, ideas
- **Discord**: Real-time chat (link in README)
- **Email**: support@honeybadgeruniverse.com

### Mentorship

New to open source? We can help!

- Tag issues with "good first issue"
- Provide guidance on PRs
- Answer questions promptly
- Pair programming available

---

## Recognition

### Contributors

All contributors are recognized in:
- `CONTRIBUTORS.md`
- GitHub contributors page
- Release notes

### Types of Contribution

We value all contributions:
- Code contributions
- Bug reports
- Documentation
- Testing
- Design
- Community support

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

See [LICENSE](../LICENSE) for full text.

---

## Questions?

**Don't hesitate to ask!**

- Open a GitHub issue
- Join our Discord
- Email: support@honeybadgeruniverse.com

**Thank you for contributing to SagaCraft!** 🎮
