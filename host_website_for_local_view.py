#!//usr/bin/python3

import os
from flask import Flask
from flask import Response
import requests
import mimetypes

app = Flask(__name__)


@app.route('/')
def hello_world():
    return open("index.html", "r").read()


@app.route('/<path:file_name>')
def run_flask(file_name: str):
    if file_name.startswith("phseiff-essays"):
        return_value = requests.get("https://phseiff.com/" + file_name).content
    else:
        if not (os.path.exists(file_name) and os.path.isfile(file_name)):
            file_name = file_name.rstrip("/") + "/index.html"
        return_value = open(file_name, "r", encoding="latin-1").read()
    return Response(return_value, mimetype=mimetypes.guess_type(file_name)[0])


if __name__ == "__main__":
    app.run(port=5687)
