#!/bin/bash
divider() {
  echo
  echo "---------------------------------------------"
  echo
}

echo "== address 1st =="
curl localhost:5000/address/ewu.edu
echo
echo "== address 2nd (cache) =="
curl localhost:5000/address/ewu.edu
echo
echo "== range =="
curl localhost:5000/range/ewu.edu
echo
echo "== weather 1st =="
curl localhost:5000/weather/ewu.edu
echo
echo "== weather 2nd (cache) =="
curl localhost:5000/weather/ewu.edu
divider

echo "== address 1st =="
curl localhost:5000/address/nasa.gov
echo
echo "== address 2nd (cache) =="
curl localhost:5000/address/nasa.gov
echo
echo "== range =="
curl localhost:5000/range/nasa.gov
echo
echo "== weather 1st =="
curl localhost:5000/weather/nasa.gov
echo
echo "== weather 2nd (cache) =="
curl localhost:5000/weather/nasa.gov
divider

echo "== address 1st =="
curl localhost:5000/address/google.com
echo
echo "== address 2nd (cache) =="
curl localhost:5000/address/google.com
echo
echo "== range =="
curl localhost:5000/range/google.com
echo
echo "== weather 1st =="
curl localhost:5000/weather/google.com
echo
echo "== weather 2nd (cache) =="
curl localhost:5000/weather/google.com
divider
