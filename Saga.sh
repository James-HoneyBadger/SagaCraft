#!/usr/bin/env bash
# SagaCraft IDE Launcher (Rust TUI)
# Usage: ./Saga.sh

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run the Rust TUI IDE
cargo run --bin sagacraft_ide_tui
