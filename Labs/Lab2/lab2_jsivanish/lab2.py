#! /usr/bin/env python3
# author: TODO: Joel Sivanish

from json import loads  # steps 3, 4
from requests import get  # steps 3, 4
from socket import gethostbyname  # step 1
from subprocess import getstatusoutput  # step 2
from sys import argv  # command line arguments
import matplotlib.pyplot as plt #for temp plotting function
import numpy as np #for temp plotting function

# Takes an array of temps
# and plots them.
def plot_temps(temps):
    xs = [x for x in range(len(temps))]
    plt.plot(xs, temps, label="Hourly tempatures")

    #Label the x and y
    plt.xlabel("Hour")
    plt.ylabel("Temperature F.")
    #Make sure we show the legend.
    plt.legend()
    #Show the plot
    plt.show()

# Step 1 helper: domain -> ip
def resolve_ip(domain: str) -> str:         # Defines a function where the parameter is a string
    return gethostbyname(domain)            # Returns the DNS-A record lookup result

# Step 2 helpers: whois + address extraction
def whois_lookup(ip: str) -> str:           # Calls the system whois tool and returns its raw text output
    status, output = getstatusoutput(f"whois {ip}")
    if status != 0:         # Tests for non-zero exit
        raise RuntimeError(f"whois failed for {ip}")        # Throws an exception, stopping execution
    return output

def extract_address(whois_text: str) -> str | None:
    """
    Heuristic parser for common whois fields.
    Tries Address/City/State/PostalCode/Country (Org* variants too),
    then falls back to the first 'Address:' line.
    """
    lines = [l.strip() for l in whois_text.splitlines()]    # Splits text into lines while creating a list
    addr = city = state = zipc = country = None     # Initialize these variables to None
    for l in lines:
        if ":" not in l:        # skips lines without (key: value) format
            continue
        k, v = l.split(":", 1)      # splits into 2 parts only
        key = k.strip().lower()     # Checks if key matches any of the allowed field names
        val = v.strip()
        # Builds multi-line street addresses
        if key in ("address", "street", "street address", "orgaddress"):
            addr = f"{addr} {val}".strip() if addr else val
        elif key in ("city", "orgcity"):
            city = val
        elif key in ("state", "state/province", "orgstateprov"):
            state = val
        elif key in ("postalcode", "zipcode", "zip", "orgpostalcode"):
            zipc = val
        elif key in ("country", "orgcountry"):
            country = val
    parts = [p for p in (addr, city, zipc, country) if p]
    if parts:
        return ", ".join(parts)

    for l in lines:
        low = l.lower()
        if "address:" in low:
            return l.split(":", 1)[1].strip()
        return None

# ---- Step 3 helper: Census Geocoding API ----
def geocode_address_one_line(address: str):
    url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
    params = {
        "address": address,
        "benchmark": "Public_AR_Current",  # also ok: "2020"
        "format": "json"
    }
    resp = get(url, params=params)  # <-- equals sign, not hyphen
    js = loads(resp.text)

    # Optional sanity check:
    # print(js)

    matches = js.get("result", {}).get("addressMatches", [])
    if not matches:
        return None, None

    coords = matches[0]["coordinates"]
    # Census uses x=lon, y=lat
    return coords["y"], coords["x"]

# Step 4 helper: NOAA weather.gov hourly (all available hours)
def get_hourly_temperatures(lat: float, lon: float) -> list[int]:
    # weather.gov prefers a User-Agent with contact info
    headers = {"User-Agent": "CSCD330-Lab2 (student@example.edu)"}

    # Discover the forecast endpoints for this point
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    p = get(points_url, headers=headers)
    p_js = loads(p.text)
    hourly_url = p_js["properties"]["forecastHourly"]

    # Fetch the hourly forecast
    f = get(hourly_url, headers=headers)
    f_js = loads(f.text)
    periods = f_js["properties"]["periods"]

    if not periods:
        return []

    # Collect *all* available temperatures
    temps = [period["temperature"] for period in periods]

    # Convert to F if needed (usually already F)
    unit = periods[0].get("temperatureUnit", "F")
    if unit == "C":
        temps = [round(t * 9/5 + 32) for t in temps]

    return temps


def main():
    # TODO: Look at the code below for an example of how to do
    # API calls. I would recommend first uncommenting and
    # understanding the code, and then commenting the code back
    # out. The code is, largely, step 4.
    # base API string for weather.gov
    """
    weather_s = "https://api.weather.gov/points/"

    # sys.argv[1] gives us the command line input
    # sys.argv[0] is the name of the python file
    print(weather_s + argv[1])

    # use the commandline input and the weather_s to make API call
    response = get(weather_s + argv[1])

    # convert it to json
    js = loads(response.text)

    # find the forecast URL based on the API page
    forecast_URL = js['properties']['forecast']

    # print link that we use for next API call
    print(forecast_URL)

    # call the API again to get theforecast
    final_response = get(forecast_URL)

    # parse json
    js = loads(final_response.text)

    # print the forecast
    print(js['properties']['periods'][0]['detailedForecast'])

    plot_temps([70,72,75,78,70,65,60])
    """
 # Step 1: Domain -> IP
    if len(argv) < 2:
        print(f"Usage: {argv[0]} <domain>")
        return
    domain = argv[1]
    print(f"[1] Resolving domain → IP for {domain} ...")
    ip = resolve_ip(domain)
    print(f"    IP: {ip}")

    # Step 2: IP -> Physical Address via whois
    print(f"[2] Running whois to find registrant address...")
    whois_text = whois_lookup(ip)
    address = extract_address(whois_text)
    if not address:
        print("    Could not extract a mailing address from whois output.")
        return
    print(f"    Address: {address}")

    # Step 3: Address -> Lat/Lon
    print(f"[3] Geocoding address to latitude/longitude...")
    lat, lon = geocode_address_one_line(address)
    if lat is None:
        print("    Geocoding failed (no matches).")
        return
    print(f"    Lat/Lon: {lat}, {lon}")

    # Step 4: Lat/Lon -> Hourly Weather
    print(f"[4] Fetching hourly forecast from weather.gov...")
    temps = get_hourly_temperatures(lat, lon)
    if not temps:
        print("    No hourly temperatures returned.")
        return
    print(f"    Hours returned: {len(temps)}")
    print(f"    First few temps: {temps[:6]}")


    # Step 5: Plotting
    print(f"[5] Plotting temperatures...")
    plot_temps(temps)
if __name__ == "__main__":
    main()
