import requests
import time
import sys
import os
from PIL import Image
from mastodon import Mastodon

time.sleep(20)

description = requests.get("https://raw.githubusercontent.com/phseiff/phseiff/master/README.md").text

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
    content = content.replace("<! the essays content >", essay_content).replace("{description}", description)

# Parse RSS feed:


def extract_item(tag, text):
    text, text_within_tags = text.split("<" + tag + ">", 1)
    text_within_tags, text2 = text_within_tags.split("</" + tag + ">", 1)
    text += text2
    return text, text_within_tags


essays = list()
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
                <a href="{link}" style="color: #e5e0d8;">
                    <div class="col x0.5">
                        <div class="col-content">
                            <div class="zoom">
                                <div class="card">
                                    <div class="card-image">
                                        <img src="{image}">
                                    </div>
                                    <div class="card-content">
                                        <span class="card-title">{title}</span>
                                        {description}
                                    </div>
                                    <div class="card-action">
                                        <a href="{link}">Read here!</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </a>""".format(
                            image=image,
                            title=title,
                            description=description,
                            link=link
    )
    essay_name = link.split("#")[-1]
    essays.append((
        title,
        essay_name,
        requests.get("https://phseiff.com/phseiff-essays/" + essay_name + ".md").text,
        image
    ))
    print("essay content:", essay_content)

content = content.replace("<! essay cards >", essay_content)


# fuse three image files:

def frame_image(left, middle, right):
    images = [Image.open(x) for x in [left, middle, right]]
    images[1].thumbnail((images[0].size[1], images[0].size[1]), Image.ANTIALIAS)
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    new_im.save(middle)


# Determine what essays are new and store the new essays in a file to see that they are not new the next time:

new_essays = list()
essays_who_will_be_tooted_this_time = list()
current_website_content = requests.get("https://phseiff.com/index.html").text
if "<already_tooted>" in current_website_content:
    essays_who_where_already_tooted = current_website_content.split("<already_tooted>", 1)[1].split(
        "</already_tooted>")[0].splitlines()
else:
    essays_who_where_already_tooted = list()
print("essays_who_where_already_tooted:", essays_who_where_already_tooted)

for (a, essay_name, b, c) in essays:
    if essay_name not in essays_who_where_already_tooted:
        new_essays.append((a, essay_name, b, c))
        essays_who_will_be_tooted_this_time.append(essay_name)
content = content.replace("</already_tooted>", "\n".join(essays_who_will_be_tooted_this_time) + "</already_tooted>")

# Finally write to index.html:

with open("index.html", "w+") as f:
    f.write(content)

# Mastodon:

for (essay_title, essay_name, essay_content_as_markdown, image) in new_essays:
    mastodon = Mastodon(
        access_token=sys.argv[1],
        api_base_url='https://toot.phseiff.com'
    )
    image_name = "throw_away_image." + image.rsplit(".", 1)[-1]
    with open(image_name, "wb") as image_file:
        image_file.write(requests.get(image).content)
    frame_image("images/left.png", image_name, "images/right.png")
    mastodon.status_post(
        'Small automated update on my essays: My new essay "' + essay_title
        + '" is out and you can read it on https://phseiff.com/#' + essay_name + ' !',
        media_ids=[mastodon.media_post(image_name)]
    )
    os.remove(image_name)
    """
    essay_content_as_markdown,
    spoiler_text='Small automated update using #mastodonpy: My new essay "' + essay_title
    + '" is out and you can read it on https://phseiff.com/#' + essay_name + ' or in this toot!'
    """
