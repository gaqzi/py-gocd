#!/bin/bash

set -euo pipefail

# Find python in PATH
WHICH_PYTHON=$(which python3 || echo "")

if [ -z "$WHICH_PYTHON" ] || [ ! -x "$WHICH_PYTHON" ]; then
    echo "Python is not installed or not in PATH"
    exit 1
fi

# Check current python version
PYTHON_VERSION=$("$WHICH_PYTHON" --version 2>&1 | awk '{print $2}')

# Set Python path
PYTHON_EXEC="$WHICH_PYTHON"

PIP_CMD="$PYTHON_EXEC -m pip"
echo "Using pip: $PIP_CMD"

test_series() {
  echo "=== Recompiling all Python files (before changes) ==="
    "$PYTHON_EXEC" -m compileall . -x '.venv' || {
        echo "compileall failed"
        exit 1
    }

    echo "=== Uninstalling any existing gocd package ==="
    $PIP_CMD uninstall -y gocd || {
        echo "pip uninstall failed (probably not installed, continuing)"
        true
    }

    echo "=== Installing py-gocd requirements ==="
    $PIP_CMD install -r requirements.txt || {
        echo "Failed to install py-gocd requirements.txt"
        exit 1
    }

    echo "=== Installing test requirements ==="
    $PIP_CMD install --upgrade -r test-requirements.txt || {
        echo "Failed to install test-requirements.txt"
        exit 1
    }

    echo "=== Recompiling after installing dependencies ==="
    "$PYTHON_EXEC" -m compileall . -x '.venv' || {
        echo "Second compileall failed"
        exit 1
    }

    echo "=== Installing package in editable mode ==="
    $PIP_CMD install -e . || {
        echo "pip install -e . failed"
        exit 1
    }

    echo "=== Running tests with pytest ==="
    "$PYTHON_EXEC" -m pytest -v || {
        echo "Tests failed!"
        exit 1
    }

    echo "✅ All tests passed successfully!"
    echo "⚠️ Check and run scripts/test.py to verify integration"
}

test_series



