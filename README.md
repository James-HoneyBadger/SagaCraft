# SagaCraft

A streamlined, text-first adventure engine and player. **Now implemented in Rust for performance and reliability.**

## Manuals

- `docs/User_Manual.md`
- `docs/Game_Designer_Manual.md`
- `docs/Technical_Reference.md`

## Community

- Code of Conduct: `CODE_OF_CONDUCT.md`

## Quickstart

Run the SagaCraft player:

```bash
./Play.sh
```

Open the SagaCraft Adventure IDE (TUI):

```bash
./Saga.sh
```

## Building

This project uses Cargo. To build all components:

```bash
cargo build --release
```

## Components

- `sagacraft_player`: Terminal-based game player
- `sagacraft_ide_tui`: Terminal UI adventure editor
- `sagacraft_ide_gui`: Graphical adventure editor (requires display)
- `sagacraft_rs`: Core library
