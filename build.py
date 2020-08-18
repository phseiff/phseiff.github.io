import requests
import time

time.sleep(20)

with open("index-raw.html", "r") as f:
    content = f.read()
    essay_list = requests.get(url="https://phseiff.com/phseiff-essays/essay_list.txt").text.split("\n")
    essay_content = "\n"
    for essay in essay_list:
        essay_content += (
            " " * 4 * 3
            + '<span class="embedded-essay" id="'
            + essay.replace("/", "_") + '" '
            # + 'onload="(function(o){o.style.height=o.contentWindow.document.body.scrollHeight+\'px\';})(this)" '
            + '><div style="width: 100%; height: 200px"></div>'
            + requests.get('https://phseiff.com/phseiff-essays/' + essay + '.html').text.replace(
                'href="https://phseiff.com/phseiff-essays/LICENSE.html"',
                'href="https://phseiff.com#LICENSE"'
            )
            + '<span style="height: 300px"></span></span>\n'
        )
    content = content.replace("<! the essays content >", essay_content)

with open("index.html", "w+") as f:
    f.write(content)

# ToDo:
#  * Einen Workflow einrichten, der automatisch zu gh-pages pusht und dort build.py ausführt, wann immer gepusht wird.
#  * Beide Repos verbinden, so dass pushs in phseiff-essays auch diese Action in phseiff.github.io triggern.
#  * Online loggen, um log einfacher zu sehen.
#  * Ein to top- und einen to bottom-button unten an seite kleben.
