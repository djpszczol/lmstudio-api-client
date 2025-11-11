#!/bin/bash
# Wrapper script to run lmcli with virtual environment

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/venv/bin/activate"
python3 "$SCRIPT_DIR/lmcli.py" "$@"
