# SagaCraft: Python → Rust Comprehensive Port

This repo contains a full-featured Python implementation under `src/sagacraft/`.
The goal of the Rust rewrite is to replace **every Python runtime component** with Rust equivalents, while keeping behavior parity and adding Rust-native tooling.

## Scope ("the whole thing")

Python surface area to port (current count):
- ~75 Python modules in `src/sagacraft/**`
- 24 Python tests in `tests/` (these are parity targets)

Major areas:
- Core runtime: engine, extended engine, event bus, parser, services, registries, validators
- Data layer: config/data/io services, save/load, adventure loader
- Systems: achievements, combat, crafting, dialogue, difficulty, procedural, quests, persistence, cloud, etc.
- Tools: command helpers, modding support
- UI/IDE: player UI + the existing Python IDE (`src/sagacraft/ui/ide.py`)

## Port strategy

1. **Mirror the Python architecture in Rust** under `rust/sagacraft_rs/src/pyport/`.
2. Keep the existing small Rust demo engine working, but port subsystem-by-subsystem.
3. Use tests as parity gates: port behavior + add Rust tests mirroring the Python ones.
4. Only then delete/retire Python runtime.

## Current status

Implemented (Rust):
- Minimal playable Rust CLI game (`sagacraft_player`)
- Adventure JSON model + load/save (`sagacraft_rs::adventure`)
- Minimal Rust TUI editor (`sagacraft_ide_tui`)
- Initial Python-parity scaffolding in `sagacraft_rs::pyport`:
  - `core/priorities` (Priority scale)
  - `core/event_bus` (subscribe/publish/history)
  - `core/system_registry` (configs, dependencies, factory)
  - `core/adventure_loader` (JSON adventure file loading)
  - `data/config_service` (JSON config + dotted-key get/set + plugin configs)
  - `data/data_service` (CRUD operations for game entities)
  - `data/io_service` (file I/O, adventure/save management)

## Mapping guide

Python → Rust (initial skeleton; will expand):
- `src/sagacraft/core/priorities.py` → `rust/sagacraft_rs/src/pyport/core/priorities.rs`
- `src/sagacraft/core/event_bus.py` → `rust/sagacraft_rs/src/pyport/core/event_bus.rs`
- `src/sagacraft/core/system_registry.py` + `system_base.py` → `rust/sagacraft_rs/src/pyport/core/system_registry.rs`
- `src/sagacraft/data/config_service.py` → `rust/sagacraft_rs/src/pyport/data/config_service.rs`

## Next milestones

- Port `adventure_loader`, `io_service`, `data_service` (file formats + persistence)
- Port the Python engine loop into a Rust-first engine with systems/plugins
- Port each `systems/*.py` module as a Rust system and build parity tests
- Replace Python IDE with a full Rust IDE (TUI now; GUI later if required)
