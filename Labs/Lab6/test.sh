#!/bin/bash
# Test script for Lab 6 - Scapy introduction

# You must run this script with sudo, since it modifies iptables and uses raw sockets.

set -e  # exit on first error

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo ./test.sh"
  exit 1
fi

# Step 0: Prevent the kernel from sending TCP RST packets for our Scapy-crafted connection.
# This makes sure the OS doesn't immediately kill the connection when it sees
# traffic it doesn't recognize as belonging to a normal socket.
iptables -I OUTPUT -p tcp --tcp-flags ALL RST -j DROP

# Run lab6.py with at least 3 different test URLs (as required by the lab).
# You can change these if your instructor suggested specific ones.
python3 lab6.py http://httpforever.com/
python3 lab6.py http://www.cs.sjsu.edu/~pearce/modules/lectures/web/html/HTTP.htm
python3 lab6.py http://example.com/

# Restore the default behavior (remove our RST-dropping rule).
iptables -D OUTPUT -p tcp --tcp-flags ALL RST -j DROP
