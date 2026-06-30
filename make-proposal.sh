#!/bin/bash
# Drop a file in brand/inbox/, then run: ./make-proposal.sh
cd "$(dirname "$0")/python" && python3 make.py proposal "$@"
