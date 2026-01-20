# author: TODO:

from flask import Flask
from json import loads
from requests import get
from socket import gethostbyname
from subprocess import getstatusoutput


app = Flask(__name__)


@app.route("/upper/<echo_string>")
def upper(echo_string):
    return echo_string.upper()


@app.route("/callwhois")
def whois(IPA):
    status, output = getstatusoutput(f"whois 8.8.8.8")
    return output


@app.route('/')
def hello():
    return 'Hello, World!'


if __name__ == "__main__":
    app.run()
