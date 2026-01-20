# Lab2: Web API
1) What is an API?

An API (application programming interface) is a set of rules or protocols that enables software applications to communicate with each other to exchange data, features, or functionality. A web API allows programs to send HTTP requests and receive structured responses, often in JSON format, to exchange data across the internet.

2) What is a RESTful API? Were the APIs we used RESTful?

A RESTful API follows Representational State Transfer principles and is stateless. It also uses resource based URLs and standard HTTP methods. Both of the APIs used follow REST conventions, so they are RESTful.

3) What is JSON? Did these APIs use JSON?

JSON is a lightweight data format that stores structered data as key-value pairs. JSON is often used when data is sent from a server to a webpage. Yes both APIs returned data in JSON format which the program parses.

4) What is Bash? Have you ever used Bash?

Bash is a Unix shell and command line language used for running commands and writing scripts on Linux. I have some minimal experience with Bash through my CTF experiences. In this lab, Bash was used to write a test script that runs the Python program with multiple domains.

## Usage
- python3 lab2.py <domain>

## Examples
- python3 lab2.py google.com
- python3 lab2.py nasa.gov
- python3 lab2.py ewu.edu

## Testing
To run Bash test script which uses the 3 domains from 'Examples' as targets, run:
- bash test.sh

## Program Description
This program retrieves and visualizes the hourly temperature forecast for a company’s registered address based on its domain name.
It performs the following steps:

1. Resolves the domain to an IP address using Python’s socket.gethostbyname.

2. Retrieves the company’s address using the whois command.

3. Converts the address to latitude and longitude using the U.S. Census Geocoder API.

4. Fetches hourly temperature data from the NOAA Weather.gov API.

5. Displays a line plot of all available hourly temperatures using Matplotlib.
