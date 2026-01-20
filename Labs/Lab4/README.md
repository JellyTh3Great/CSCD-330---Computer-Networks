# Lab4: HTTP and Sockets

## Overview

This lab builds upon previous network programming exercises by creating a lightweight **HTTP client** using Python’s built-in **socket** library. The program mimics the functionality of basic tools like `curl` or `wget`, allowing you to retrieve web pages over HTTP (unencrypted). The client establishes a TCP connection, sends an HTTP GET request, and displays or saves the response body.

The program supports two output modes:

* **-p** → Print the webpage contents to STDOUT.
* **-f** → Save the webpage contents to a file named `output.txt`.

The client works only with **HTTP (port 80)**, not HTTPS, and demonstrates low-level interaction with web servers via TCP sockets.

## Questions

1. **Why did you have to encode() your request and decode() the response(s)? What do these functions do?**
   The `encode()` function converts the HTTP request string into bytes, which is necessary because sockets transmit binary data. The `decode()` function converts the received bytes back into a readable string so the response can be printed or written to a file.

2. **What changes would you have to make to create a UDP socket?**
   You would replace the TCP socket type `SOCK_STREAM` with `SOCK_DGRAM`. UDP does not use a connection, so you would remove `connect()` and instead use `sendto()` and `recvfrom()` for data transmission.

3. **If you wanted to create a TCP server, what would you have to change?**
   A TCP server must first bind to an address and port using `bind()`, then listen for incoming connections using `listen()`. It uses `accept()` to establish each client connection and communicates using the socket returned by `accept()`.

4. **Can your TCP client create or process HTTPS traffic? What happens if you send a request to port 443?**
   No, this client cannot handle HTTPS. HTTPS requires SSL/TLS encryption, which involves an encrypted handshake before sending any HTTP data. Sending a plain-text HTTP request to port 443 will result in errors or unreadable output since the server expects encrypted communication.

## Usage

1. **Run the program:**

   * To print a webpage to STDOUT:

     ```bash
     python3 lab4.py -p 80 http://httpforever.com/
     ```
   * To save the webpage to a file:

     ```bash
     python3 lab4.py -f 80 http://httpforever.com/
     ```

2. **Flags:**

   * `-p`: Print response to terminal
   * `-f`: Save response to `output.txt`

3. **Port:**

   * Typically 80 for HTTP.

4. **URL Format:**

   * Must include the full `http://` scheme, for example:
     `http://example.com/`

## Testing

To run the Bash test script which performs three test cases (root page, 404 page, and file output), use one of the following commands:

* `./test.sh`
* `bash test.sh`

Ensure the script has execute permissions first:

```bash
chmod +x test.sh
```

## Program Description

This Python client connects to a web server using a TCP socket and constructs a valid HTTP/1.1 GET request containing the required **Host** header and `Connection: close`. It receives data in chunks until the server closes the connection, ensuring the full page is retrieved.

Once received, the program strips off the HTTP headers and outputs only the response body. The client also supports chunked transfer decoding, basic charset detection from the `Content-Type` header, and proper encoding of text output.

This lab reinforces understanding of the relationship between the **TCP transport layer** and the **HTTP application layer**, showing how standard web requests can be manually implemented without relying on external libraries or fr
