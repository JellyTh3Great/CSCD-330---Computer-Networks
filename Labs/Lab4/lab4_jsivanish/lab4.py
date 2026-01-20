# CSCD 330 - Lab 4: HTTP and Sockets
# author: Joel Sivanish
#
# A minimal HTTP client (HTTP/1.1 over TCP) that retrieves a webpage and either
# prints the response body to STDOUT (-p) or writes it to output.txt (-f).
# Only the following imports are used per the lab requirements.

# Assistance and code review provided by OpenAI ChatGPT (GPT-5), October 2025.
# ChatGPT was used to clarify lab requirements, structure code, and ensure
# compliance with allowed libraries and socket programming conventions.
# OpenAI. ChatGPT (GPT-5), version October 2025, https://chat.openai.com/

from sys import argv, exit
from socket import *
from urllib.parse import urlparse


def usage(msg: str = ""):
    if msg:
        print(f"Error: {msg}")
    print("Usage: python3 lab4.py (-p | -f) <port> <url>")
    print("  -p : print response body to STDOUT")
    print("  -f : write response body to output.txt")
    print("  <port> : destination TCP port (e.g., 80)")
    print("  <url> : absolute http URL (e.g., http://example.com/ or http://host/path)")
    exit(1)


def build_request(hostname: str, path_query: str) -> bytes:
    """Craft a minimal HTTP/1.1 GET request with headers that avoid compression.

    We include 'Connection: close' so the server will close the TCP connection
    after sending the response, letting us detect end-of-stream cleanly without
    waiting for a timeout. We also request identity encoding to avoid gzip.
    """
    request_lines = [
        f"GET {path_query} HTTP/1.1",
        f"Host: {hostname}",
        "User-Agent: cscd330-lab4-client/1.0",
        "Accept: */*",
        "Accept-Encoding: identity",
        "Connection: close",
        "",
        "",
    ]
    return ("\r\n".join(request_lines)).encode("ascii")


def recv_all(sock: socket) -> bytes:
    """Receive until the server closes the connection (Connection: close)."""
    chunks = []
    while True:
        data = sock.recv(4096)
        if not data:
            break
        chunks.append(data)
    return b"".join(chunks)


def parse_headers_and_body(raw: bytes):
    """Split HTTP response into (headers_text, body_bytes).

    Returns headers as a lowercase string (for simple searching) and raw body bytes.
    If there are no headers delimiter, headers_text becomes an empty string.
    """
    sep = b"\r\n\r\n"
    if sep in raw:
        head, body = raw.split(sep, 1)
    else:
        # Fallback: treat everything as body
        head, body = b"", raw
    try:
        headers_text = head.decode("iso-8859-1", errors="replace")
    except Exception:
        headers_text = ""
    return headers_text.lower(), body


def dechunk(body: bytes) -> bytes:
    """Decode a 'Transfer-Encoding: chunked' body.

    Implements a simple chunked transfer coding parser without extra imports.
    Reference: RFC 7230 §4.1. Trailer headers (if present) are discarded.
    """
    i = 0
    out = bytearray()
    # Helper to read a line terminated by CRLF starting at i
    def read_line(b, start):
        j = b.find(b"\r\n", start)
        if j == -1:
            return None, start
        return b[start:j], j + 2

    while True:
        # Read chunk size line (hex possibly with extensions)
        line, i = read_line(body, i)
        if line is None:
            # Malformed; return what we have
            return bytes(out)
        # Strip any chunk extensions after ';'
        semi = line.find(b";")
        size_hex = line if semi == -1 else line[:semi]
        try:
            size = int(size_hex.strip(), 16)
        except ValueError:
            # Malformed size; return what we have
            return bytes(out)
        if size == 0:
            # Read final CRLF after the 0-size chunk data (there is none), then optional trailers
            # Consume the trailing CRLF after size line already handled; now consume trailer section
            # which ends with an empty line (CRLF)
            # Read lines until empty line
            while True:
                trailer_line, i = read_line(body, i)
                if trailer_line is None:
                    break
                if trailer_line == b"":
                    break
            return bytes(out)
        # Read 'size' bytes of chunk data
        if i + size > len(body):
            # Incomplete; return what we have
            out.extend(body[i:])
            return bytes(out)
        out.extend(body[i:i + size])
        i += size
        # Consume the CRLF after the chunk data
        if i + 2 <= len(body) and body[i:i + 2] == b"\r\n":
            i += 2
        else:
            # Malformed; best-effort return
            return bytes(out)


def pick_charset(headers_text_lower: str) -> str:
    """Try to extract charset from headers; default to utf-8 if not found."""
    # Simple manual search to keep within allowed imports
    # Example: 'content-type: text/html; charset=utf-8'
    ct_pos = headers_text_lower.find("content-type:")
    if ct_pos != -1:
        # Extract the header line
        end = headers_text_lower.find("\n", ct_pos)
        if end == -1:
            end = len(headers_text_lower)
        line = headers_text_lower[ct_pos:end]
        cs_key = "charset="
        cs_pos = line.find(cs_key)
        if cs_pos != -1:
            charset = line[cs_pos + len(cs_key):].strip()
            # Trim potential trailing params
            for sep in [";", " ", "\t", "\r"]:
                idx = charset.find(sep)
                if idx != -1:
                    charset = charset[:idx]
            # Basic sanity
            if charset:
                return charset
    return "utf-8"


def main():
    if len(argv) != 4:
        usage()

    flag = argv[1]
    if flag not in ("-p", "-f"):
        usage("First argument must be -p or -f")

    try:
        port = int(argv[2])
        if not (0 < port < 65536):
            raise ValueError
    except ValueError:
        usage("Port must be an integer between 1 and 65535")

    raw_url = argv[3]
    parsed = urlparse(raw_url)
    if parsed.scheme.lower() != "http":
        usage("URL must be an http URL (HTTPS is not supported in this lab)")

    hostname = parsed.hostname
    if not hostname:
        usage("Invalid URL: missing hostname")

    # Build path + query
    path = parsed.path if parsed.path else "/"
    if parsed.query:
        path += f"?{parsed.query}"

    # Establish TCP connection
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.settimeout(10)
        sock.connect((hostname, port))
        # Send request
        request_bytes = build_request(hostname, path)
        sock.sendall(request_bytes)
        # Receive response
        raw = recv_all(sock)
    finally:
        try:
            sock.close()
        except Exception:
            pass

    # Separate headers and body
    headers_text_lower, body = parse_headers_and_body(raw)

    # Handle chunked transfer if present
    if "transfer-encoding:" in headers_text_lower and "chunked" in headers_text_lower:
        body = dechunk(body)

    # Convert body bytes to text for output
    charset = pick_charset(headers_text_lower)
    try:
        body_text = body.decode(charset, errors="replace")
    except LookupError:
        # Unknown charset; fall back to utf-8
        body_text = body.decode("utf-8", errors="replace")

    if flag == "-p":
        print(body_text, end="")
    else:
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(body_text)


if __name__ == "__main__":
    main()
