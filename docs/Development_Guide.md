# SagaCraft Development Guide

## Contributing to SagaCraft

Welcome to the SagaCraft development community! This guide will help you get started with contributing to the project, whether you're fixing bugs, adding features, or creating documentation.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment](#development-environment)
3. [Code Style and Conventions](#code-style-and-conventions)
4. [Project Structure](#project-structure)
5. [Testing](#testing)
6. [Submitting Changes](#submitting-changes)
7. [Advanced Topics](#advanced-topics)
8. [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Rust**: Version 1.70 or later
- **Git**: Version control system
- **Text Editor**: VS Code, Vim, Emacs, or your preferred editor
- **Terminal**: Bash, Zsh, or compatible shell

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/SagaCraft.git
cd SagaCraft

# Add upstream remote
git remote add upstream https://github.com/James-HoneyBadger/SagaCraft.git

# Create a development branch
git checkout -b feature/your-feature-name
```

### Initial Setup

```bash
# Install development dependencies
cargo install cargo-watch cargo-expand cargo-flamegraph cargo-tarpaulin

# Build the project
cargo build

# Run tests
cargo test

# Verify everything works
cargo run --bin sagacraft_player
```

## Development Environment

### Recommended Tools

#### VS Code Setup
```json
// .vscode/settings.json
{
  "rust-analyzer.checkOnSave.command": "clippy",
  "rust-analyzer.cargo.features": "all",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true,
    "source.organizeImports": true
  },
  "[rust]": {
    "editor.defaultFormatter": "rust-lang.rust-analyzer"
  }
}
```

#### Essential Extensions
- **Rust Analyzer**: Language server for Rust
- **CodeLLDB**: Debugger for Rust
- **Even Better TOML**: TOML file support
- **GitLens**: Enhanced Git capabilities

### Development Workflow

```bash
# Start development server with auto-reload
cargo watch -x 'run --bin sagacraft_player'

# In another terminal, run tests on changes
cargo watch -x test

# Format code
cargo fmt

# Lint code
cargo clippy

# Generate documentation
cargo doc --open
```

## Code Style and Conventions

### Rust Style Guidelines

We follow the official Rust style guidelines:

```rust
// ✅ Good: Clear naming, proper formatting
pub fn calculate_damage(attacker: &Player, defender: &Monster) -> i32 {
    let base_damage = attacker.weapon_damage();
    let defense = defender.armor_value();
    let final_damage = (base_damage - defense).max(1);

    final_damage
}

// ❌ Bad: Unclear naming, poor formatting
pub fn dmg_calc(a: &Player, d: &Monster) -> i32 {
    let dmg = a.weapon_damage(); let def = d.armor_value();
    let fd = (dmg - def).max(1); fd
}
```

### Naming Conventions

- **Functions**: `snake_case` (e.g., `calculate_damage`)
- **Types**: `PascalCase` (e.g., `GameState`, `Adventure`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `MAX_HEALTH`)
- **Modules**: `snake_case` (e.g., `game_state.rs`)

### Documentation Standards

```rust
/// Calculates combat damage between two entities.
///
/// This function takes into account weapon damage, armor values,
/// and any special modifiers that might affect the final damage.
///
/// # Arguments
///
/// * `attacker` - The entity performing the attack
/// * `defender` - The entity being attacked
///
/// # Returns
///
/// The final damage amount (minimum 1)
///
/// # Examples
///
/// ```
/// let damage = calculate_damage(&player, &monster);
/// assert!(damage >= 1);
/// ```
pub fn calculate_damage(attacker: &Player, defender: &Monster) -> i32 {
    // Implementation...
}
```

### Error Handling

Use appropriate error types and provide context:

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum GameError {
    #[error("Invalid command: {0}")]
    InvalidCommand(String),

    #[error("Item not found: {0}")]
    ItemNotFound(String),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
}

pub fn process_command(command: &str) -> Result<(), GameError> {
    match command {
        "invalid" => Err(GameError::InvalidCommand(command.to_string())),
        _ => Ok(()),
    }
}
```

## Project Structure

### Core Library (`sagacraft_rs`)

```
src/
├── lib.rs              # Main library interface
├── adventure.rs        # Adventure loading and validation
├── command.rs          # Command parsing and handling
├── game_state.rs       # Core game state structures
└── systems/            # Game systems
    ├── mod.rs
    ├── basic_world.rs  # Room navigation
    ├── combat.rs       # Combat mechanics
    ├── inventory.rs    # Item management
    └── quests.rs       # Quest tracking
```

### Applications

```
sagacraft_player/       # CLI game player
├── src/main.rs
└── Cargo.toml

sagacraft_ide_tui/      # Terminal UI editor
├── src/main.rs
└── Cargo.toml

sagacraft_ide_gui/      # GUI editor
├── src/main.rs
└── Cargo.toml
```

### Supporting Files

```
docs/                   # Documentation
tests/                  # Integration tests
scripts/               # Build and utility scripts
Cargo.toml            # Workspace configuration
```

## Testing

### Unit Tests

Write comprehensive unit tests for all public functions:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_damage_basic() {
        let attacker = Player::new("Hero");
        let defender = Monster::new(1, "Goblin");

        let damage = calculate_damage(&attacker, &defender);
        assert!(damage >= 1);
        assert!(damage <= attacker.weapon_damage());
    }

    #[test]
    fn test_calculate_damage_with_armor() {
        let mut attacker = Player::new("Hero");
        let mut defender = Monster::new(1, "Armored Goblin");

        defender.set_armor(5);
        let damage = calculate_damage(&attacker, &defender);

        // Damage should be reduced by armor
        assert!(damage < attacker.weapon_damage());
    }
}
```

### Integration Tests

Test complete workflows in `tests/` directory:

```rust
// tests/integration_tests.rs
use sagacraft_rs::{AdventureGame, BasicWorldSystem};

#[test]
fn test_complete_adventure_flow() {
    let mut game = AdventureGame::new(Some("test_adventure.json".to_string()));
    assert!(game.load_adventure().is_ok());

    game.add_system(Box::new(BasicWorldSystem::default()));

    // Test movement
    let output = game.process_command("go north");
    assert!(!output.is_empty());

    // Test item interaction
    let output = game.process_command("take sword");
    assert!(output.iter().any(|line| line.contains("taken")));
}
```

### Running Tests

```bash
# Run all tests
cargo test

# Run specific test
cargo test test_calculate_damage

# Run with coverage
cargo tarpaulin --out Html

# Run integration tests only
cargo test --test integration

# Run tests in release mode
cargo test --release
```

### Test Organization

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete user workflows
- **Performance tests**: Benchmark critical paths

## Submitting Changes

### Commit Guidelines

Follow conventional commit format:

```bash
# Good commits
git commit -m "feat: add magic system with spell casting"
git commit -m "fix: resolve crash when loading corrupted save files"
git commit -m "docs: update installation guide for Windows"
git commit -m "refactor: simplify command parsing logic"

# Bad commits
git commit -m "fixed stuff"
git commit -m "changes"
git commit -m "update"
```

### Pull Request Process

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/add-magic-system
   ```

2. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "feat: implement basic magic system"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/add-magic-system
   ```

4. **Create a Pull Request** on GitHub with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Screenshots/videos for UI changes
   - Links to related issues

5. **Address review feedback**:
   - Make requested changes
   - Add additional commits or amend existing ones
   - Rebase if needed to keep history clean

### Code Review Checklist

**For reviewers:**
- [ ] Code compiles without warnings
- [ ] Tests pass
- [ ] Documentation is updated
- [ ] Code follows style guidelines
- [ ] No security vulnerabilities
- [ ] Performance impact is acceptable

**For contributors:**
- [ ] All tests pass locally
- [ ] Code is formatted with `cargo fmt`
- [ ] Clippy warnings are resolved
- [ ] Documentation is updated
- [ ] Commit messages are clear

## Advanced Topics

### Performance Optimization

```rust
// Use efficient data structures
use std::collections::HashMap;

// Cache expensive operations
lazy_static::lazy_static! {
    static ref COMMAND_CACHE: Mutex<HashMap<String, Command>> = Mutex::new(HashMap::new());
}

// Profile performance-critical code
#[cfg(feature = "profiling")]
fn expensive_operation() {
    // Implementation with profiling
}
```

### Memory Management

```rust
// Use arena allocation for game objects
use typed_arena::Arena;

struct GameArena {
    players: Arena<Player>,
    monsters: Arena<Monster>,
    items: Arena<Item>,
}

// Avoid unnecessary allocations
impl GameState {
    pub fn get_player(&self, id: i32) -> Option<&Player> {
        self.players.get(&id)
    }
}
```

### Concurrency

```rust
use tokio::sync::RwLock;

// Thread-safe game state
pub struct ThreadSafeGameState {
    state: RwLock<GameState>,
}

impl ThreadSafeGameState {
    pub async fn process_command(&self, command: Command) -> Vec<String> {
        let mut state = self.state.write().await;
        // Process command with exclusive access
        process_command_impl(&mut state, command)
    }
}
```

### Plugin System Architecture

```rust
// Plugin trait
pub trait Plugin: Send + Sync {
    fn name(&self) -> &str;
    fn version(&self) -> &str;
    fn initialize(&mut self, game: &mut AdventureGame) -> Result<(), PluginError>;
    fn get_systems(&self) -> Vec<Box<dyn System>>;
    fn handle_command(&self, command: &str, game: &mut AdventureGame) -> Option<Vec<String>>;
}

// Plugin loading
pub struct PluginManager {
    plugins: HashMap<String, Box<dyn Plugin>>,
}

impl PluginManager {
    pub fn load_plugin(&mut self, path: &Path) -> Result<(), PluginError> {
        // Dynamic library loading logic
        // ...
        Ok(())
    }
}
```

### Serialization Strategies

```rust
use serde::{Serialize, Deserialize};

// Versioned serialization
#[derive(Serialize, Deserialize)]
#[serde(tag = "version")]
enum SaveFormat {
    #[serde(rename = "1.0")]
    V1_0(GameStateV1),
    #[serde(rename = "2.0")]
    V2_0(GameStateV2),
}

// Migration support
impl SaveFormat {
    fn migrate_to_latest(self) -> GameState {
        match self {
            SaveFormat::V1_0(old) => old.migrate(),
            SaveFormat::V2_0(state) => state,
        }
    }
}
```

## Community Guidelines

### Code of Conduct

We follow a code of conduct to ensure a welcoming environment:

- **Be respectful**: Treat all contributors with respect
- **Be collaborative**: Work together to improve the project
- **Be patient**: Everyone is learning and growing
- **Be inclusive**: Welcome contributors from all backgrounds

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and ideas
- **Pull Request Comments**: For code review discussions
- **Discord/Slack**: For real-time communication (when available)

### Getting Help

- **Documentation**: Check existing docs first
- **Search Issues**: Look for similar problems
- **Ask Questions**: Don't hesitate to ask for clarification
- **Share Knowledge**: Help others when you can

### Recognition

Contributors are recognized through:
- **GitHub Contributors**: Listed in repository contributors
- **Changelog**: Mentioned in release notes
- **Credits**: Special thanks in documentation
- **Badges**: Recognition for significant contributions

## Development Roadmap

### Current Priorities

1. **Performance**: Optimize memory usage and loading times
2. **Features**: Add requested community features
3. **Platforms**: Expand platform support
4. **Documentation**: Improve and expand documentation
5. **Testing**: Increase test coverage

### Contributing to the Roadmap

- **Propose Features**: Use GitHub Discussions
- **Vote on Issues**: Use reactions to show support
- **Submit PRs**: Implement features you care about
- **Report Bugs**: Help improve stability

### Long-term Vision

- **Multiplayer**: Real-time collaborative adventures
- **3D Support**: Integration with 3D rendering
- **Mobile Apps**: iOS and Android versions
- **Web Version**: Browser-based adventures
- **Mod Ecosystem**: Community plugin marketplace

---

**Thank you for contributing to SagaCraft!** Your efforts help make text-based adventures more accessible and enjoyable for everyone. Whether you're fixing a small bug or implementing a major feature, every contribution matters.

For questions or help getting started, don't hesitate to reach out through GitHub Issues or Discussions.