# SagaCraft

[![Rust](https://img.shields.io/badge/Rust-1.70%2B-orange)](https://www.rust-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-green.svg)]()
[![Documentation](https://img.shields.io/badge/Docs-Complete-blue.svg)](docs/)
[![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)]()

> A high-performance, text-based adventure game engine and development suite written in Rust. Create, edit, and play interactive fiction adventures with a focus on simplicity, extensibility, and performance.

## ✨ Key Features

### 🚀 Performance & Reliability
- **High Performance**: Written in Rust for maximum speed and memory safety
- **Cross-Platform**: Native binaries for Linux, macOS, and Windows
- **Memory Safe**: Zero-cost abstractions with compile-time guarantees
- **Concurrent**: Multi-threaded architecture for smooth gameplay

### 🎮 Game Development Suite
- **Multiple Interfaces**: CLI player, Terminal UI editor, and GUI editor
- **Modular Architecture**: Plugin system for custom game mechanics
- **JSON Format**: Human-readable adventure file format
- **Live Editing**: Edit adventures while playing with hot-reload

### ⚔️ Rich Gameplay Systems
- **Advanced Combat**: Turn-based combat with tactical depth
- **Dynamic Inventory**: Full item system with equipment and crafting
- **Quest Framework**: Branching narratives with multiple endings
- **NPC Interactions**: Dialogue trees and character relationships
- **World Building**: Procedural generation and custom content

### 🔧 Developer Experience
- **Comprehensive Documentation**: Complete guides for all use cases
- **Testing Framework**: Extensive unit and integration tests
- **Code Quality**: Automated linting and formatting
- **Plugin Ecosystem**: Community-driven extensions and mods

## 📦 Quick Start

### For Players

```bash
# Download and play (Linux/macOS)
curl -L https://github.com/James-HoneyBadger/SagaCraft/releases/latest/download/sagacraft_player -o sagacraft_player
chmod +x sagacraft_player
./sagacraft_player

# Or download from releases page for your platform
```

### For Developers

```bash
# Clone and build
git clone https://github.com/James-HoneyBadger/SagaCraft.git
cd SagaCraft
cargo build --release

# Run the CLI player
./target/release/sagacraft_player

# Run the TUI editor
./target/release/sagacraft_ide_tui

# Run the GUI editor
./target/release/sagacraft_ide_gui
```

### For Game Designers

```bash
# Create your first adventure
./target/release/sagacraft_ide_tui
# Follow the in-app tutorial or check the Game Designer Manual
```

## 📚 Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [📖 User Manual](docs/User_Manual.md) | Complete gameplay guide with commands and features | Players |
| [🎨 Game Designer Manual](docs/Game_Designer_Manual.md) | Create and design adventures with examples | Content Creators |
| [🔧 Technical Reference](docs/Technical_Reference.md) | Architecture, systems, and implementation details | Developers |
| [⚙️ Installation Guide](docs/Installation_Guide.md) | Detailed setup for all platforms and use cases | Everyone |
| [🚀 Development Guide](docs/Development_Guide.md) | Contributing, code style, and extending SagaCraft | Contributors |
| [📋 API Reference](docs/API_Reference.md) | Complete API documentation with examples | Developers |

## 🏗️ Project Structure

```
SagaCraft/
├── sagacraft_rs/           # Core game engine (Rust library)
│   ├── src/
│   │   ├── lib.rs         # Main library interface
│   │   ├── adventure.rs   # Adventure loading & validation
│   │   ├── command.rs     # Command parsing system
│   │   ├── game_state.rs  # Core game state structures
│   │   └── systems/       # Game systems (combat, inventory, etc.)
├── sagacraft_player/       # Command-line game player
├── sagacraft_ide_tui/      # Terminal UI adventure editor
├── sagacraft_ide_gui/      # Graphical adventure editor
├── docs/                   # Comprehensive documentation
├── config/                 # Configuration files
├── saves/                  # Save game data
├── mods/                   # Modding support & examples
├── plugins/                # Plugin system
├── tests/                  # Test suite
└── scripts/               # Build and utility scripts
```

## 🎯 Game Features

### Core Mechanics
- **🌍 World Navigation**: Explore interconnected rooms with rich descriptions
- **🎒 Item Management**: Collect, equip, and use items with persistent effects
- **💬 NPC Interactions**: Dialogue systems with branching conversations
- **⚔️ Combat System**: Strategic turn-based battles with equipment and abilities
- **📜 Quest Tracking**: Dynamic objectives with rewards and story progression

### Advanced Features
- **🎲 Procedural Generation**: Infinite replayability with randomized content
- **🤖 AI Companions**: Personality-driven companions with unique behaviors
- **🏪 Trading System**: Marketplace mechanics with economy simulation
- **🌤️ Seasonal Events**: Dynamic content based on time and player actions
- **☁️ Cloud Saves**: Cross-device synchronization and backup
- **🎧 Audio System**: Immersive sound design with spatial audio
- **♿ Accessibility**: Screen reader support and keyboard navigation
- **🌐 Multiplayer**: Co-op adventures and PvP combat (planned)

### Item System
- **Weapons**: Swords, axes, bows, clubs, spears with unique properties
- **Armor**: Helmets, chest plates, shields with defense calculations
- **Consumables**: Potions, food, scrolls with temporary effects
- **Tools**: Keys, lockpicks, crafting materials
- **Treasure**: Collectibles, currency, rare artifacts

### Command Examples
```bash
look                    # Examine current room
inventory               # View carried items
take sword              # Pick up items
equip sword             # Equip weapons/armor
go north                # Navigate between rooms
talk to merchant        # Interact with NPCs
attack goblin           # Engage in combat
use health potion       # Consume items
save game               # Save progress
help                    # Show available commands
```

## 🤝 Contributing

We welcome contributions from developers, game designers, writers, and enthusiasts! See our [Development Guide](docs/Development_Guide.md) for:

- **🚀 Getting Started**: Development environment setup
- **📝 Code Style**: Rust conventions and best practices
- **🧪 Testing**: Unit tests, integration tests, and benchmarks
- **🔄 Pull Requests**: Contribution workflow and review process
- **📚 Documentation**: Writing and maintaining docs

### Quick Development Setup

```bash
# Install development tools
cargo install cargo-watch cargo-expand cargo-flamegraph cargo-tarpaulin

# Run tests continuously
cargo watch -x test

# Run with debug logging
RUST_LOG=debug cargo run --bin sagacraft_player

# Generate documentation
cargo doc --open

# Format and lint
cargo fmt && cargo clippy
```

### Areas for Contribution
- **Core Engine**: Performance optimizations and new systems
- **Game Content**: Adventure creation and story writing
- **Tools**: Editor improvements and development utilities
- **Documentation**: Tutorials, guides, and API documentation
- **Testing**: Additional test cases and quality assurance
- **Platforms**: Porting to new operating systems

## 📄 License & Legal

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **Rust Standard Library**: Dual licensed under MIT/Apache-2.0
- **Dependencies**: See `Cargo.lock` for full license information
- **Assets**: Content created for SagaCraft follows CC-BY-SA 4.0

## 🙏 Acknowledgments

### Technology Stack
- **[Rust](https://www.rust-lang.org/)**: Systems programming language for performance and safety
- **Cargo**: Excellent package management and build system
- **Serde**: Serialization framework for data persistence

### Inspiration
- **Classic Text Adventures**: Zork, Colossal Cave Adventure, and Infocom games
- **Modern IF Engines**: Twine, Inform 7, and Ren'Py
- **Open Source Community**: Countless contributors to the Rust ecosystem

### Special Thanks
- **Beta Testers**: Early adopters providing valuable feedback
- **Contributors**: Everyone who has helped improve SagaCraft
- **Rust Community**: Exceptional tooling, documentation, and support

## 📞 Community & Support

### Getting Help
- 🐛 **[Issues](https://github.com/James-HoneyBadger/SagaCraft/issues)**: Bug reports and feature requests
- 💬 **[Discussions](https://github.com/James-HoneyBadger/SagaCraft/discussions)**: General questions and ideas
- 📧 **Email**: For security issues or private matters
- 📖 **[Documentation](docs/)**: Comprehensive guides and references

### Community Guidelines
- **Be Respectful**: Treat all community members with kindness
- **Be Constructive**: Provide helpful feedback and suggestions
- **Be Patient**: We're all learning and growing together
- **Be Inclusive**: Welcome contributors from all backgrounds

### Roadmap & Vision
- **Short-term**: Enhanced multiplayer, mobile support, web version
- **Medium-term**: 3D rendering, advanced AI, plugin marketplace
- **Long-term**: Cross-platform ecosystem, professional tooling

---

## 🎮 Ready to Start Your Adventure?

**For Players**: Download the latest release and start playing immediately!

**For Creators**: Read the [Game Designer Manual](docs/Game_Designer_Manual.md) to create your first adventure!

**For Developers**: Check the [Development Guide](docs/Development_Guide.md) to contribute to the engine!

**📈 Version 1.0.0** - Production Ready • Fully Documented • Community Driven

---

*Made with ❤️ in Rust • MIT Licensed • Cross-Platform • Open Source*
