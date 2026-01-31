#!/bin/bash
# Run a debate with 1Password secret injection
#
# Usage:
#   ./scripts/run.sh                           # Run with default topic
#   ./scripts/run.sh "Resolved: Custom topic"  # Run with custom topic
#
# Requires:
#   - 1Password CLI (op) installed and signed in
#   - .env file with op:// references for API keys

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

exec op run --env-file=.env -- uv run python scripts/run_debate.py "$@"
