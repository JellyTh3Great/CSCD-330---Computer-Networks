#!/bin/bash
# Lab 7 - TCP Traceroute

# Require root (Scapy needs raw sockets)
if [[ "$EUID" -ne 0 ]]; then
  echo "This script must be run as root."
  echo "Usage: sudo $0"
  exit 1
fi

echo "== google.com =="
python3 lab7.py google.com 30
echo

echo "== yahoo.com =="
python3 lab7.py yahoo.com 30
echo

echo "== ewu.edu =="
python3 lab7.py ewu.edu 30
echo
