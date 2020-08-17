import requests

with open("index-raw.html", "r") as f:
    content = f.read()
    essay_list = "LICENSE\ntest".split("\n")  # requests.get(url="phseiff.com/phseiff-essays/essay_list.txt").split("\n")
    essay_content = "\n"
    for essay in essay_list:
        essay_content += (
            " " * 4 * 3
            + '<span class="embedded-essay" id="'
            + essay.replace("/", "_") + '" '
            # + 'onload="(function(o){o.style.height=o.contentWindow.document.body.scrollHeight+\'px\';})(this)" '
            + '>' + requests.get('https://phseiff.com/phseiff-essays/' + essay + '.html').text + '</span>\n'
        )
    content = content.replace("<! the essays content >", essay_content)

with open("index.html", "w+") as f:
    f.write(content)

# ToDo:
#  * phseiff-essays muss essay_list.txt erstellen, essays (ohne .html) darin speichern, darkmode in essays
#    einbetten, und einen "back to top"-button am Boden jedes Essays einbauen, der standardmäßig angezeigt ist und erst
#    dann gehidden wird, wenn js aktiviert ist. Zusätzlich anstelle von ../phseiff-essays/LICENSE.md den Link
#    ..#LICENSe benutzen.
# * Einen Workflow einrichten, der automatisch zu gh-pages pusht und dort build.py ausführt, wann immer gepusht wird.
# * Beide Repos verbinden, so dass pushs in phseiff-essays auch diese Action in phseiff.github.io triggern.
# * Online loggen, um log einfacher zu sehen.
# * Ein to top- und einen to bottom-button unten an seite kleben.