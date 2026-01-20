#author: Joel Sivanish

from urllib.parse import urlparse
from random import randint
from scapy.all import *
from socket import gethostbyname
from sys import argv

# Your initial TCP sequence number must be the length of your first name.
# Change "Joel" if needed.
FIRST_NAME = "Joel"
INITIAL_SEQ = len(FIRST_NAME)


def build_get_request(parsed_url):
    """
    Build a minimal valid HTTP GET request from a parsed URL.
    """
    path = parsed_url.path or "/"
    if parsed_url.query:
        path += "?" + parsed_url.query

    host_header = parsed_url.hostname

    request_lines = [
        f"GET {path} HTTP/1.1",
        f"Host: {host_header}",
        "Connection: close",
        "",
        "",
    ]
    return "\r\n".join(request_lines).encode()


def main():
    # The lab spec typically calls your script as:
    #   sudo python3 lab6.py http://example.com/
    if len(argv) != 2:
        return  # no printing allowed

    url = argv[1]
    parsed = urlparse(url)

    # Only handle plain HTTP as required by the lab
    if parsed.scheme != "http":
        return

    # Default HTTP port 80 if not specified
    dest_port = parsed.port if parsed.port is not None else 80

    # Resolve hostname to IPv4 address
    if parsed.hostname is None:
        return
    dest_ip = gethostbyname(parsed.hostname)

    # Random high source port
    src_port = randint(1024, 65535)

    # Silence Scapy's own verbose output
    conf.verb = 0

    # Initial sequence number based on your first name length
    seq = INITIAL_SEQ

    ip = IP(dst=dest_ip)

    # 1) Send SYN
    syn = TCP(sport=src_port, dport=dest_port, flags="S", seq=seq)
    synack = sr1(ip / syn, timeout=2)

    # If we didn't get a SYN/ACK back, just exit quietly
    if synack is None or not synack.haslayer(TCP):
        return

    # 2) Send ACK to complete the three-way handshake
    ack_seq = seq + 1                 # we used one sequence number for the SYN
    ack_ack = synack[TCP].seq + 1     # acknowledge server's SYN

    ack = TCP(
        sport=src_port,
        dport=dest_port,
        flags="A",
        seq=ack_seq,
        ack=ack_ack,
    )
    send(ip / ack)

    # 3) Send HTTP GET with PSH+ACK
    payload = build_get_request(parsed)

    psh_ack = TCP(
        sport=src_port,
        dport=dest_port,
        flags="PA",  # PSH + ACK
        seq=ack_seq,
        ack=ack_ack,
    )

    send(ip / psh_ack / Raw(payload))

    # No prints, no further packets required for the lab core requirements.


if __name__ == "__main__":
    main()
