#!/usr/bin/env bash

if [ "$#" -gt 1 ]; then
    echo "Usage: $0 <input_file>"
    exit 1
elif [ "$#" -lt 1 ]; then
    input_file="transactions.csv"
else
    input_file="$1"
fi

python3 src/main.py $input_file
