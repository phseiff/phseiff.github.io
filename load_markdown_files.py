"""Contains code to load markdown files stored on github (in a repository) as html whenever I push, so I don't need to
worry about that, and I don't need to embed stuff from GitHub."""

import requests
from subprocess import Popen, PIPE

files = [
    "test",
]

file_paths = [
    "https://raw.githubusercontent.com/phseiff/phseiff-essays/master/" + file + ".md"
    for file in files
]

file_tuples = zip(files, file_paths)


with open("github-essays/prototype.html", "r") as prototype:
    prototype_content = prototype.read()
    for file, file_path in file_tuples:
        text_md = requests.get(url=file_path).text
        process = Popen(["curl", "https://api.github.com/markdown/raw", "-X", "POST", "-H", "Content-Type: text/plain",
                         "-d", text_md], stdout=PIPE)
        (text_html, err) = process.communicate()
        if process.wait() != 0:
            raise Exception("An error happened - error:", err)
        with open("github-essays/essays/" + file + ".html", "w+") as f:
            f.write(prototype_content.format(str(text_html, encoding="UTF-8").replace("\\n", "")))
