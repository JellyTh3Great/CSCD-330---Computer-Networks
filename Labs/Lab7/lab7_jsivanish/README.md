## Lab7: TCP Traceroute

## Overview

This lab builds on previous Scapy work by creating a custom TCP-based traceroute tool.
Instead of using ICMP or UDP, the program sends TCP SYN packets with increasing TTL values to reveal each hop in the path to a target host. After completing the trace, the program performs WHOIS lookups to extract the Autonomous System (AS) numbers associated with each hop.
(For extra credit, the program also performs reverse DNS lookups.)

## Questions

1. **Besides TCP, what other protocols can be used for a traceroute tool?**
   Traceroute is commonly implemented using ICMP (Windows tracert) or UDP (Linux traceroute). Both rely on routers returning ICMP Time Exceeded messages when a packet’s TTL reaches zero.
   
2. **When traversing to a website, does the path remain constant every time?**
   No. Internet routing is dynamic, and the path may change due to congestion, load balancing, routing policy changes, or outages.
   
3. **If a packet dies before reaching the target website, what type of packet is returned?**
   An ICMP Time Exceeded message is returned by the router where the TTL expires.
   
4. **an the whois command be used to discover the owner of an AS number?**
   Yes. WHOIS data can provide the organization that owns a specific AS number.
   
## Usage

1. **Run the program:**
- sudo python3 lab7.py <domain> <max_hops>

## Testing

To run the Bash test script:
- sudo ./test.sh

This scirpt tests 3 domains:
- google.com
- yahoo.com
- ewu.edu

## Program Description

This program performs a TCP traceroute by sending TCP SYN packets with TTL values starting at 1 and increasing until the destination is reached or the maximum hop count is exceeded. For each hop:
1. A TCP SYN packet is created with Scapy and sent using sr1 with verbose=0 and timeout=3.
2. If a response is received, the hop number and IP address are printed.
3. If no response is received within the timeout window, the program prints * * *.
4. The trace stops when a packet is returned from the destination IP.
5. After all hops are collected, the program performs WHOIS lookups to extract the AS numbers associated with each hop, removing duplicates and printing them in order.
6. (Extra credit) The program also performs reverse DNS lookups using the host command and prints hostnames when available.

## Citation

- OpenAI. ChatGPT, version 5.1, OpenAI, 2025, https://chat.openai.com/
