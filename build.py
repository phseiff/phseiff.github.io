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

# Parse RSS feed:


def extract_item(tag, text):
    text, text_within_tags = text.split("<" + tag + ">", 1)
    text_within_tags, text2 = text_within_tags.split("</" + tag + ">", 1)
    text += text2
    return text, text_within_tags


rss_feed = requests.get(url="https://phseiff.com/phseiff-essays/feed.rss").text
essay_content = str()
while "<item>" in rss_feed:
    rss_feed, rss_item = extract_item("item", rss_feed)
    _, description = extract_item("description", rss_item)
    _, title = extract_item("title", rss_item)
    _, link = extract_item("link", rss_item)
    _, pubDate = extract_item("pubDate", rss_item)
    _, image = extract_item("image", rss_item)
    essay_content += """
                <div class="col x0.5">
                    <div class="col-content">
                        <div class="zoom">
                            <div class="card">
                                <div class="card-image">
                                    <img src="{image}">
                                    <span class="card-title">{title}</span>
                                </div>
                                <div class="card-content">
                                    {description}
                                </div>
                                <div class="card-action">
                                    <a href="{link}">Read here!</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>""".format(
                            image=image,
                            title=title,
                            description=description,
                            link=link
    )
    print("essay content:", essay_content)

content = content.replace("<! essay cards >", essay_content)

# Mastodon:

new_essays = list()
for (essay_title, essay_name, essay_content_as_markdown) in new_essays:
    # ToDo: Find a way to determine if our essay is new by storing essays in a file after they where first embedded
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

# Finally write to index.html:

with open("index.html", "w+") as f:
    f.write(content)
