import requests
import time
import sys
from mastodon import Mastodon

time.sleep(20)

with open("index-raw.html", "r") as f:
    content = f.read()
    essay_list = requests.get(url="https://phseiff.com/phseiff-essays/essay_list.txt").text.split("\n")
    essay_content = "\n"
    for essay in essay_list:
        essay_content += (
            " " * 4 * 3
            # + '<p><p><p><div style="width: 100%; height: 200px"></div>'
            + '<span style="margin-top: 200px" class="embedded-essay" id="'
            + essay.replace("/", "_") + '" '
            # + 'onload="(function(o){o.style.height=o.contentWindow.document.body.scrollHeight+\'px\';})(this)" '
            + '>'
            + requests.get('https://phseiff.com/phseiff-essays/' + essay + '.html').text.replace(
                'href="https://phseiff.com/phseiff-essays/LICENSE.html"',
                'href="#LICENSE"'
            )
            + '<span style="height: 300px"></span></span>\n'
        )
    content = content.replace("<! the essays content >", essay_content)

with open("index.html", "w+") as f:
    f.write(content)

# Mastodon:

new_essays = list()
for (essay_title, essay_name, essay_content_as_markdown) in new_essays:
    # ToDo: Find a wa to determine if our essay is new by storing essays in a file after they where first embedded
    #  into the rss feed. Oh, and before doing that, write the rss-feed-to-html-content-overview-parser!
    mastodon = Mastodon(
        access_token=sys.argv[1],
        api_base_url='https://toot.phseiff.com'
    )
    mastodon.status_post(
        essay_content_as_markdown,
        spoiler_text='Small automated update using #mastodonpy: My new essay "' + essay_title
        + '" is out and you can read it on https://phseiff.com/#' + essay_name + ' or in this toot!'
    )


# ToDo:
#  * Beide Repos verbinden, so dass pushs in phseiff-essays auch diese Action in phseiff.github.io triggern.
#  * Online loggen, um log einfacher zu sehen.

