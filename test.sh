#!/usr/bin/env bash

if [ "$#" -gt 1 ]; then
    echo "Usage: $0 [test_pattern]"
    exit 1
elif [ "$#" -lt 1 ]; then
    pattern="test*.py"
else
    pattern="$1"
fi

python3 -m unittest discover -s tests -p "$pattern" -v
