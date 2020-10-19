#!//usr/bin/python3

import os
from flask import Flask
from flask import Response
import requests
import mimetypes

app = Flask(__name__)
print("starting to host flask app!")
with open("test.test", "w") as f:
    f.write("os.")


@app.route('/')
def hello_world():
    return open("index.html", "r").read()


@app.route('/<path:file_name>')
def run_flask(file_name: str):
    if file_name.startswith("phseiff-essays"):
        return_value = requests.get("https://phseiff.com/" + file_name).text
    else:
        return_value = open(file_name, "r").read()
    return Response(return_value, mimetype=mimetypes.guess_type(file_name)[0])


if __name__ == "__main__":
    app.run(port=5687)
