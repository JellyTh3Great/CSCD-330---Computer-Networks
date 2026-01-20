#!/bin/bash
# CSCD 330 - Lab 4 Test Script
# author: Joel Sivanish
#
# This script runs lab4.py with three sample test cases as required by the lab.
# Each section is labeled for clarity.

# Stop on error
set -e

# Ensure Python script exists
if [ ! -f lab4.py ]; then
  echo "Error: lab4.py not found in current directory."
  exit 1
fi

# Test 1: Retrieve root page and print to STDOUT
echo "== Test 1: Root page (print to STDOUT) =="
python3 lab4.py -p 80 http://httpforever.com/

echo

# Test 2: Retrieve a non-existent page (expect 404)
echo "== Test 2: Non-existent page =="
python3 lab4.py -p 80 http://httpforever.com/login

echo

# Test 3: Retrieve and save to file
echo "== Test 3: Save to output.txt =="
python3 lab4.py -f 80 http://httpforever.com/

if [ -f output.txt ]; then
  echo "Output successfully saved to output.txt"
else
  echo "Error: output.txt not found!"
fi

echo "\nAll tests completed."
