#!/usr/bin/env bash
# Quick start script for Adventure Construction Set

cat << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         ADVENTURE CONSTRUCTION SET                        ║
║         Quick Start                                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

What would you like to do?

1. Launch IDE (create/edit/play adventures)
2. Run tests
3. View documentation

EOF

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "Launching IDE..."
        python3 -m src.acs.ui.ide
        ;;
    2)
        echo "Running tests..."
        python3 -m pytest tests/ -v
        ;;
    3)
        echo "Documentation is in docs/"
        echo "Start with: docs/QUICKSTART.md"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
