#!/bin/bash
# Council AI - Mac Launch Script
# Double-click to launch or run: ./launch-council-mac.sh

cd "$(dirname "$0")" || exit

echo "🏛️  Launching Council AI..."
python3 launch-council.py --open
