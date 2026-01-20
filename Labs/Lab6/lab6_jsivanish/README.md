# Lab6: Scapy and HTTP Handshake

## Overview
This lab extends the earlier HTTP client work by using Scapy instead of the standard socket library. Instead of relying on the OS networking stack to manage TCP connections, the program manually:
- Builds and sends a TCP three-way handshake (SYN, SYN/ACK, ACK).
- Sends a valid HTTP GET request over that TCP connection.
- Captures the resulting network traffic in a pcap file using tcpdump.
Like Lab 4, this lab only deals with HTTP over port 80 (unencrypted). The key difference is that Scapy operates at a lower level, so the program must set things like IP/TCP headers and sequence numbers explicitly, and rely on packet captures (not program output) to verify correctness.

## Questions

1. **In lab 4 you sent a GET request using the sockets library. What did the sockets library do for you?**
   In Lab 4, the socket library handled almost all of the low-level TCP details for me. It automatically performed the three-way handshake, chose and tracked TCP sequence and acknowledgment numbers, handled retransmissions and flow control, and cleanly closed the connection when I called close(). All I had to do was send a string with sendall() and receive data with recv(), and the OS networking stack took care of building and parsing the TCP/IP packets.
   
2. **Before you submit this lab, you should check that your pcap contains the correct traffic. What program should you use to analyze your pcap?            In your pcap, did the server send you the complete HTML for the website or just a portion of the HTML? (Does the response end with a </html> tag?)**
   I used Wireshark to analyze my pcap. The server did not send any HTML at all. The response was a small plain-text file (nm-check.txt) containing the message ‘NetworkManager is online’. Since this is not an HTML document, it does not end with a </html> tag.
   
3. **Is your program guaranteed to receive a complete HTML response from the website? Why or why not.**
   No, my program is not guaranteed to receive a complete HTML response. I only send the packets needed to complete the handshake and the first GET request, and I do not fully act like a normal TCP stack (for example, I am not continuously acknowledging every data segment and handling retransmissions like the kernel would). Network latency, packet loss, server behavior, and the size of the page all affect how much of the response arrives and is captured. Since Scapy is working outside the kernel’s normal connection tracking, the server may stop sending data or only send the first segment of the response, so a full HTML document is not guaranteed.
   
4. **Can you merge the final ACK of the three-way handshake with the GET request? That is, can you merge the two packets into one? If yes, explain how such an option might be beneficial.**
   Yes, it is possible to piggyback the final ACK of the three-way handshake and the HTTP GET request in the same packet. Instead of sending an empty ACK and then a separate packet containing the GET, the last handshake packet can carry both the ACK flag and the HTTP request payload. This is beneficial because it reduces the number of round-trip times (RTTs) and total packets required before the server can start sending data, which improves latency and makes the connection feel faster.
   
5. **Can scapy be used to send other types of packets? If yes, give an example.**
   Yes, Scapy can craft and send many other types of packets. For example, it can send ICMP echo requests (like a custom ping), send ARP requests/replies to discover or spoof MAC addresses on a LAN, or build DNS queries and responses. In general, Scapy can construct and inject arbitrary packets at multiple layers (Ethernet, IP, TCP/UDP, etc.), which makes it useful for testing, scanning, and learning about network protocols.
   
## Usage

1. **Run the program:**
- To send an HTTP GET request using Scapy: sudo python3 lab6.py http://example.com/
The program does not print webpage content.
All verification is done in the packet capture.

2. **Packet Capture:**
- Record traffic on port 80 while the script runs: sudo tcpdump -i any tcp port 80 -w test.pcap

3. **URL Format:**
- Must include the full http:// scheme, for example: http://httpforever.com/

4. **RST Filtering:**
- The test script automatically handles adding and removing the iptables rule.

## Testing

To run the Bash test script which sets the firewall rule, runs the Scapy client, and records the traffic to test.pcap, use one of the following commands:
- sudo ./test.sh
- sudo bash test.sh

## Program Description

This program uses Scapy to manually create the packets needed to make an HTTP request. It builds the TCP SYN packet, completes the three-way handshake, and sends a valid HTTP GET request in a raw TCP segment. Instead of using the normal socket library, Scapy lets the program set fields like sequence numbers, flags, and payloads directly.

The program extracts the host and path from the URL, resolves the hostname, and chooses an initial sequence number based on the length of my first name. After sending the GET request, Scapy receives the server’s first response packet. The rest of the verification is done by examining test.pcap in Wireshark to confirm that the handshake, GET request, and server response all appear correctly.

Extra Credit:
After receiving the first response packet, the program closes the connection by sending a TCP FIN/ACK packet, which is visible in the pcap.
