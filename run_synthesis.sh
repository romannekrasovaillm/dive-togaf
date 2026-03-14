#!/usr/bin/env bash
# =====================================================================
# DIVE-TOGAF Phase 2: Evidence-Driven Synthesis — Launch Script
#
# Usage:
#   ./run_synthesis.sh                    # default: 3 cycles, 3 iterations
#   ./run_synthesis.sh --batch-size 5     # 5 cycles
#   ./run_synthesis.sh --seed-category bian_service_domain  # banking only
#   ./run_synthesis.sh --verbose          # debug logging
#
# Environment:
#   KIMI_API_KEY or MOONSHOT_API_KEY — required
#
# =====================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Check API key ---
if [ -z "${KIMI_API_KEY:-}" ] && [ -z "${MOONSHOT_API_KEY:-}" ]; then
    echo "ERROR: Set KIMI_API_KEY or MOONSHOT_API_KEY environment variable."
    echo "  Get your key at https://platform.moonshot.ai/"
    echo ""
    echo "  export KIMI_API_KEY=your-api-key-here"
    echo "  ./run_synthesis.sh"
    exit 1
fi

# --- Install dependencies if needed ---
if ! python3 -c "from openai import OpenAI" 2>/dev/null; then
    echo "Installing required dependency: openai..."
    pip install openai --quiet
fi

# --- Ensure pools are built ---
if [ ! -f "pools/tools/tool_pool.json" ] || \
   [ ! -f "pools/seeds/seed_pool.json" ] || \
   [ ! -f "pools/exemplars/exemplar_pool.json" ]; then
    echo "Building resource pools..."
    python3 build_pools.py
fi

# --- Run synthesis ---
echo ""
echo "Launching DIVE-TOGAF Phase 2 synthesis..."
echo ""
python3 run_synthesis.py "$@"
