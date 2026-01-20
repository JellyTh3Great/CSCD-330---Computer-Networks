# lab7.py
# author: Joel Sivanish

from scapy.all import IP, TCP, sr1
from socket import gethostbyname
from subprocess import getstatusoutput
from sys import argv


def usage():
    print(f"Usage: {argv[0]} <target host> <max hops>")


def lookup_as_number(ip_addr):
    """
    Look up the AS number for a given IP address using whois.

    First tries Team Cymru whois (nice AS output); if that fails,
    falls back to a generic whois and searches for an origin/AS line.
    Returns a string like 'AS15169' or None if not found.
    """
    # Try Team Cymru whois (if available on the system)
    # Example command:
    #   whois -h whois.cymru.com " -v 8.8.8.8"
    cymru_cmd = f'whois -h whois.cymru.com " -v {ip_addr}"'
    status, output = getstatusoutput(cymru_cmd)

    if status == 0:
        for line in output.splitlines():
            line = line.strip()
            # Skip headers, look for first data line starting with digit(s)
            if line and line[0].isdigit():
                # Expected format: "15169 | 8.8.8.8 | ..."
                fields = [f.strip() for f in line.split("|")]
                if fields:
                    as_num = fields[0]
                    if as_num.isdigit():
                        return "AS" + as_num
                break  # don't keep searching if format is weird

    # Fallback: generic whois
    generic_cmd = f"whois {ip_addr}"
    status, output = getstatusoutput(generic_cmd)

    if status != 0:
        return None

    for line in output.splitlines():
        lower = line.lower()
        if "origin" in lower or "originas" in lower or "origin as" in lower:
            # Try to extract something that looks like an AS number
            cleaned = line.replace(":", " ")
            for token in cleaned.split():
                token_upper = token.upper()
                if token_upper.startswith("AS") and token_upper[2:].isdigit():
                    return token_upper
                if token.isdigit():
                    return "AS" + token

    return None


def reverse_dns(ip_addr):
    """
    Extra credit (Step 3): Do a reverse DNS lookup using the 'host' command.

    Returns a hostname like 'example.com' or None if lookup fails.
    """
    cmd = f"host {ip_addr}"
    status, output = getstatusoutput(cmd)

    if status != 0:
        return None

    # Typical output:
    #   8.8.8.8.in-addr.arpa domain name pointer dns.google.
    parts = output.split()
    if "pointer" in parts:
        idx = parts.index("pointer")
        if idx + 1 < len(parts):
            hostname = parts[idx + 1].rstrip(".")
            return hostname

    return None


def tcp_traceroute(target_host, max_hops):
    """
    Step 1 & 2:
      - Send TCP packets with increasing TTLs using sr1 (verbose=0, timeout=3).
      - Print hop number and IP, or '* * *' if no response.
      - Stop when reaching the destination IP or max hops.
      - After the hops, print traversed AS numbers with duplicates removed.
    """
    try:
        dest_ip = gethostbyname(target_host)
    except Exception as e:
        print(f"Error resolving {target_host}: {e}")
        return

    print(f"route to {target_host} ({dest_ip}), {max_hops} hops max")

    hop_ips = []  # list of IPs seen at each hop (None for timeouts)

    for ttl in range(1, max_hops + 1):
        # Build TCP SYN packet toward destination, with given TTL
        ip_layer = IP(dst=dest_ip, ttl=ttl)
        tcp_layer = TCP(dport=80, flags="S")
        packet = ip_layer / tcp_layer

        resp = sr1(packet, verbose=0, timeout=3)

        if resp is None:
            # No response from this hop
            print(f"{ttl} - * * *")
            hop_ips.append(None)
            continue

        # Extract IP of the responding router/host
        hop_ip = resp[IP].src
        hop_ips.append(hop_ip)

        # Extra credit: reverse DNS lookup (can comment this out if you don't want it)
        hostname = reverse_dns(hop_ip)
        if hostname:
            print(f"{ttl} - {hop_ip} ({hostname})")
        else:
            print(f"{ttl} - {hop_ip}")

        # Stop if we reached the destination
        if hop_ip == dest_ip:
            break

    # Step 2: Look up AS numbers for each unique IP in the path
    as_chain = []
    seen_as = set()

    for ip in hop_ips:
        if ip is None:
            continue  # skip timeouts

        as_num = lookup_as_number(ip)
        if as_num is None:
            continue

        if as_num not in seen_as:
            seen_as.add(as_num)
            as_chain.append(as_num)

    if as_chain:
        print("Traversed AS numbers: " + " -> ".join(as_chain))
    else:
        print("Traversed AS numbers: (none found)")


def main():
    if len(argv) != 3:
        usage()
        return

    target_host = argv[1]
    try:
        max_hops = int(argv[2])
        if max_hops <= 0:
            raise ValueError
    except ValueError:
        print("Error: <max hops> must be a positive integer.")
        usage()
        return

    tcp_traceroute(target_host, max_hops)


if __name__ == "__main__":
    main()
