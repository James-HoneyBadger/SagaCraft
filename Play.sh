#!/usr/bin/env bash
# SagaCraft Game Player Launcher (Rust)
# Usage: ./Play.sh [adventure_file.json]

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run the Rust game player
cargo run --bin sagacraft_player -- "$@"
