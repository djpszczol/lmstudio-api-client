#!/bin/bash
# Wrapper script to run lmcli with virtual environment

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if venv exists, create if missing
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv "$SCRIPT_DIR/venv"
    echo "Installing dependencies..."
    "$SCRIPT_DIR/venv/bin/pip" install -q --upgrade pip
    "$SCRIPT_DIR/venv/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"
    echo "Setup complete!"
    echo ""
fi

source "$SCRIPT_DIR/venv/bin/activate"
python3 "$SCRIPT_DIR/lmcli.py" "$@"
