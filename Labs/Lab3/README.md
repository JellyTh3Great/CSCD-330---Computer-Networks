# Lab3: Flask Server

## Overview
This lab builds upon Lab 2 by creating a small web API server using the **Flask** framework.
The server provides three routes that convert a domain name into:
- A physical (business) address from WHOIS data
- The current non-hourly weather forecast for that location
- The IP address range associated with the domain

To reduce repeated network calls, the server also implements an in-memory cache.
If the same request is made twice, the second response is prefixed with **“Cached:”**.

## Questions
1) **Identify the following in the URL:**
   `http://localhost:5000/weather/google.com`
- Domain: `localhost`
- Path: `/weather/google.com`
- Port: `5000`
- Protocol: `http`

2) **Identify the following in the URL:**
   `https://translate.google.com/`
- Domain: `google.com`
- Subdomain: `translate`
- TLD: `com`
- Path: `/`
- Protocol: `https`
- Port: `443`

3) **What is a Python decorator?**
A decorator is a function wrapper defined with **@name** that modifies or extends another function’s behavior without changing its code.
Flask uses decorators to register functions that handle specific web routes.

4) **Is there any problem with your cache implementation? Would it work in production?**
The cache is an in-memory Python dictionary. It resets when the server restarts, has no expiration or size limit, and is not shared across multiple processes or threads. It works fine for this lab but would need a persistent, thread-safe system in a real production environment.

## Usage
1. **Install Flask**
- On Debian/Ubuntu:
     `sudo apt-get install python3-flask`
- On Arch / Steam Deck:
     `sudo pacman -S python-flask`
- Or using pip:
     `python3 -m pip install flask`

2. **Run the server**
-python3 lab3.py

## Testing
To run Bash test script which uses: ewu.edu, nasa.gov, google.com as a targets, run either:
-./test.sh
-bash test.sh

## Program Description
This Flask server provides a lightweight API layer that utilizes the same functionality developed in Lab 2 as HTTP endpoints:

/address/<domain>
Resolves the domain’s IP address and uses whois to extract a physical address.

/weather/<domain>
Geocodes that address using the U.S. Census API, then retrieves the non-hourly weather forecast from weather.gov.

/range/<domain>
Parses WHOIS data to return the IP network range for that domain.

All endpoints return plain-text strings (not JSON), as specified in the assignment.
When an endpoint is requested again with the same domain, the cached result is returned to demonstrate request caching.


