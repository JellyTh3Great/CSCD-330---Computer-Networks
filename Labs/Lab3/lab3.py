#!/usr/bin/env python3
# author: Joel Sivanish

from flask import Flask
from json import loads
from requests import get
from socket import gethostbyname
from subprocess import getstatusoutput

app = Flask(__name__)

# simple in-memory cache: keys are (route_name, domain)
cache = {}

########################################
# Helper functions (adapted from lab2) #
########################################

def resolve_ip(domain: str) -> str:
    """Domain -> IPv4 string using DNS A lookup."""
    return gethostbyname(domain)

def whois_lookup(ip: str) -> str:
    """Run whois on an IP and return raw text output."""
    status, output = getstatusoutput(f"whois {ip}")
    # if whois fails for some reason, still return whatever we got
    return output

def extract_address(whois_text: str) -> str:
    """
    Try to build a nice one-line physical/business address
    from common whois fields.
    We'll attempt something like:
    street + city + state + postalCode
    If we can't build a nice structured one, we fallback to the first Address: line.
    """
    lines = [l.strip() for l in whois_text.splitlines()]

    street = None
    city = None
    state = None
    postal = None

    for l in lines:
        if ":" not in l:
            continue
        k, v = l.split(":", 1)
        key = k.strip().lower()
        val = v.strip()

        if key in ("address", "street", "street address", "orgaddress"):
            street = (street + " " + val).strip() if street else val
        elif key in ("city", "orgcity"):
            city = val
        elif key in ("state", "state/province", "orgstateprov"):
            state = val
        elif key in ("postalcode", "zipcode", "zip", "orgpostalcode"):
            postal = val

    # Best-case formatted address
    parts = []
    if street:
        parts.append(street)
    # If we have city/state/postal, format like "City, ST, ZIP"
    city_state_zip_parts = []
    if city:
        city_state_zip_parts.append(city)
    if state:
        city_state_zip_parts.append(state)
    if postal:
        city_state_zip_parts.append(postal)

    if city_state_zip_parts:
        # join that sub-block with ", "
        parts.append(", ".join(city_state_zip_parts))

    if parts:
        return ", ".join(parts)

    # fallback: grab first line with 'Address:' in it
    for l in lines:
        low = l.lower()
        if "address:" in low:
            return l.split(":", 1)[1].strip()

    return "Address not found"

def geocode_address_one_line(address: str):
    """
    Use the Census geocoder API to get (lat, lon) for a one-line address.
    Returns (lat, lon) as floats or (None, None) if no match.
    """
    url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "format": "json"
    }
    resp = get(url, params=params)
    js = loads(resp.text)

    matches = js.get("result", {}).get("addressMatches", [])
    if not matches:
        return None, None

    coords = matches[0]["coordinates"]
    # note: API returns x=lon, y=lat
    lat = coords["y"]
    lon = coords["x"]
    return lat, lon

def get_forecast_text(lat: float, lon: float) -> str:
    """
    Use weather.gov API:
    1. GET /points/<lat>,<lon>
    2. Follow 'forecast' URL (NOT hourly)
    3. Return periods[0]['detailedForecast']
    """
    headers = {"User-Agent": "CSCD330-Lab3 (student@example.edu)"}

    # Discover forecast endpoint
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    p = get(points_url, headers=headers)
    p_js = loads(p.text)

    forecast_url = p_js["properties"]["forecast"]

    # Fetch forecast
    f = get(forecast_url, headers=headers)
    f_js = loads(f.text)
    periods = f_js["properties"]["periods"]
    if not periods:
        return "Forecast not found"

    return periods[0].get("detailedForecast", "Forecast not found")

def extract_range(whois_text: str):
    """
    Parse the whois text for an IP range.
    We'll first look for 'NetRange:' (ARIN style)
    Example: NetRange:       142.250.0.0 - 142.251.255.255
    We'll also try 'inetnum:' (RIPE/APNIC style)
    """
    lines = whois_text.splitlines()
    for l in lines:
        if ":" not in l:
            continue
        k, v = l.split(":", 1)
        key = k.strip().lower()
        val = v.strip()
        if key == "netrange":
            return val  # already "start - end"
        if key == "inetnum":
            return val  # often "start - end"

    return "Range not found"

#####################
# Flask Endpoints   #
#####################

@app.route("/address/<domain>")
def address_route(domain):
    # check cache first
    key = ("address", domain)
    if key in cache:
        return "Cached: " + cache[key]

    # compute fresh
    ip = resolve_ip(domain)
    wtxt = whois_lookup(ip)
    addr = extract_address(wtxt)

    cache[key] = addr
    return addr

@app.route("/weather/<domain>")
def weather_route(domain):
    # check cache first
    key = ("weather", domain)
    if key in cache:
        return "Cached: " + cache[key]

    # domain -> ip -> whois -> address
    ip = resolve_ip(domain)
    wtxt = whois_lookup(ip)
    addr = extract_address(wtxt)

    # address -> lat/lon
    lat, lon = geocode_address_one_line(addr)
    if lat is None or lon is None:
        forecast_text = "Forecast not found"
    else:
        # lat/lon -> forecast text
        forecast_text = get_forecast_text(lat, lon)

    cache[key] = forecast_text
    return forecast_text

@app.route("/range/<domain>")
def range_route(domain):
    # check cache first
    key = ("range", domain)
    if key in cache:
        return "Cached: " + cache[key]

    ip = resolve_ip(domain)
    wtxt = whois_lookup(ip)
    rng = extract_range(wtxt)

    # match assignment's output style exactly:
    # "Network range for google.com is 142.250.0.0 - 142.251.255.255"
    msg = f"Network range for {domain} is {rng}"

    cache[key] = msg
    return msg

@app.route("/")
def root():
    return "CSCD330 Lab3 server running."

if __name__ == "__main__":
    # default: localhost:5000
    app.run()
