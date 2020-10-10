import requests
import time
import sys
import os
import css_html_js_minify
from PIL import Image
from mastodon import Mastodon
import subprocess

if "called_from_gh_pages" in sys.argv:
    time.sleep(20)

description_of_myself = requests.get("https://raw.githubusercontent.com/phseiff/phseiff/master/README.md").text

# Parse RSS feed:


def extract_item(tag, text):
    text, text_within_tags = text.split("<" + tag + ">", 1)
    text_within_tags, text2 = text_within_tags.split("</" + tag + ">", 1)
    text += text2
    return text, text_within_tags


redirecting_page = """<!DOCTYPE HTML>
 
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0;url=http://phseiff.com/#{name}">
<link rel="canonical" href="https://phseiff.com/#{name}">
 
<script>
  window.location.href = "https://phseiff.com/#{name}"
</script>
 
<title>Redirection page</title>

If you see this page, it means you are being redirected to
<a href='https://phseiff.com/#{name}'>the article you requested</a>,
but your browser is too old to do so automatically. You can still follow the link manually. :)"""


essays = list()  # list of tuples of (title, anchor, content, essay_image)
essay_anchors = list()  # list of anchors used to access essays on the webpage
essay_cards = str()  # string describing the cards used for accessing all essays
rss_feed = requests.get(url="https://phseiff.com/phseiff-essays/feed.rss").text  # The RSS feed we will parse into these

descriptions_string = ""
titles_string = ""
images_string = ""
languages_string = ""

os.makedirs("e", exist_ok=True)
os.makedirs("essay", exist_ok=True)
xml_sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
   <url>
      <loc>https://phseiff.com/</loc>
      <lastmod>{update_date}</lastmod>
      <changefreq>weekly</changefreq>
      <priority>0.9</priority>
      <xhtml:link rel="alternate" hreflang="en" href="https://phseiff.com/"/>
   </url>
   <!-- Further links -->
</urlset>
"""


def fix_errors_in_date_format(date):
    date = date.split("-")
    for i in range(len(date)):
        if len(date[i]) < 2:
            date[i] = "0" + date[i]
    date = "-".join(date)
    return date


while "<item>" in rss_feed:
    rss_feed, rss_item = extract_item("item", rss_feed)
    _, description = extract_item("description", rss_item)
    _, title = extract_item("title", rss_item)
    _, link = extract_item("link", rss_item)
    _, pubDate = extract_item("pubDate", rss_item)
    _, image = extract_item("image", rss_item)
    _, language = extract_item("language", rss_item)
    essay_cards += """
                <a href="{link}" class="card-to-show-essay" style="color: #000000;">
                    <div class="col x0.5">
                        <div class="col-content">
                            <div class="zoom">
                                <div class="card">
                                    <div class="card-image">
                                        <img alt="{image}" src="{image}">
                                        <span class="badge">{creation_date} | {language}</span>
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
                            link="#" + link.rsplit("#")[-1],
                            creation_date=" ".join(pubDate.split(" ")[:4]),
                            language="🇬🇧" if language == "en" else "🇩🇪"
    )
    essay_anchor = link.split("#")[-1]
    essay_anchors.append(essay_anchor)
    essays.append((
        title,
        essay_anchor,
        requests.get("https://phseiff.com/phseiff-essays/" + essay_anchor + ".md").text,
        image
    ))
    descriptions_string += "\"" + essay_anchor + "\": \"" + description.replace("\"", "\\\"") + "\",\n    "
    titles_string += "\"" + essay_anchor + "\": \"" + title.replace("\"", "\\\"") + " - by phseiff\",\n    "
    images_string += "\"" + essay_anchor + "\": \"" + image.replace("\"", "\\\"") + "\",\n    "
    languages_string += "\"" + essay_anchor + "\": \"" + language + "\",\n    "

    for directory in ("e", "essay"):
        if not os.path.exists(directory + "/" + essay_anchor):
            os.makedirs(directory + "/" + essay_anchor)
        with open(directory + "/" + essay_anchor + "/index.html", "w+") as f:
            f.write(redirecting_page.format(name=essay_anchor))
        with open(directory + "/" + essay_anchor + "/index.html", "w") as f:
            f.write(redirecting_page.format(name=essay_anchor))

    # Save the change date:
    if "called_from_gh_pages" in sys.argv:
        command = (
            "curl -u phseiff:" + sys.argv[3]
            + " -s \"https://api.github.com/repos/phseiff/phseiff-essays/commits?path=" + essay_anchor
            + ".md&page=1&per_page=1\" | jq \".[0].commit.committer.date\""
        )
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE
        )
        print("Essay:", essay_anchor)
        output, error = process.communicate()
        last_change_date = str(output, encoding="UTF-8").split("T")[0]
        update_date = last_change_date[1:][:-1]
        print("Age:", update_date)
    else:
        update_date = "example"
    xml_sitemap_entry = """<url>
      <loc>https://phseiff.com/e/{name}</loc>
      <lastmod>{date}</lastmod>
      <changefreq>weekly</changefreq>
      <priority>0.5</priority>
      <xhtml:link rel="alternate" hreflang="{language}" href="https://phseiff.com/e/{name}"/>
   </url>
   <!-- Further links -->""".format(name=essay_anchor, language=language, date=fix_errors_in_date_format(update_date))
    xml_sitemap_content = xml_sitemap_content.replace("<!-- Further links -->", xml_sitemap_entry)

    print("essay card:", essay_cards)

# Change creation date of central index.html:

command = (
        "curl -s \"https://api.github.com/repos/phseiff/phseiff.github.io/commits?path=index.html&page=1&per_page=1\""
        + " | jq \".[0].commit.committer.date\""
)
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
output, _ = process.communicate()
last_change_date = str(output, encoding="UTF-8").split("T")[0]
update_date = last_change_date[1:][:-1]
xml_sitemap_content = xml_sitemap_content.format(update_date=fix_errors_in_date_format(update_date))

# Save xml sitemap:

with open("xml-sitemap.xml", "w") as f:
    f.write(xml_sitemap_content)
    print("xml sitemap:", xml_sitemap_content)

# Build the essays into the website

with open("index-raw.html", "r") as index_raw:
    content = index_raw.read()
    essay_list = requests.get(url="https://phseiff.com/phseiff-essays/essay_list.txt").text.split("\n")
    essay_content = "\n"
    for essay in essay_list:
        essay_content += (
            " " * 4 * 3
            + '<span '
            # style (invisible by default if the essay is not mentioned in rss feed and not the license):
            + 'style="margin-top: 200px; '
            + ("display: none;" if essay not in essay_anchors and essay != "LICENSE" else "") + '" '
            # class:
            + 'class="embedded-essay"'
            # id (essay_name):
            + 'id="' + essay.replace("/", "_") + '" '
            + '>'
            # content:
            + requests.get('https://phseiff.com/phseiff-essays/' + essay + '.html').text.replace(
                'href="https://phseiff.com/phseiff-essays/LICENSE.html"',
                'href="#LICENSE"'
            )
            + '<span style="height: 300px"></span></span>\n'
        )

content = content.replace("<! the essays content >", essay_content)
content = content.replace("{description}", description_of_myself)
content = content.replace("<! essay cards >", essay_cards)

content = content.replace("/* other descriptions */", descriptions_string)
content = content.replace("/* other titles */", titles_string)
content = content.replace("/* other images */", images_string)
content = content.replace("/* other languages */", languages_string)


# fuse three image files to create a mastodon image to share:

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
current_website_content = requests.get("https://phseiff.com/index.html").text
if "<already_tooted>" in current_website_content:
    essays_who_where_already_tooted = current_website_content.split("<already_tooted>", 1)[1].split(
        "</already_tooted>")[0].splitlines()
else:
    essays_who_where_already_tooted = list()

for (a, essay_anchor, b, c) in essays:
    if essay_anchor not in essays_who_where_already_tooted:
        new_essays.append((a, essay_anchor, b, c))
        essays_who_where_already_tooted.append(essay_anchor)
content = content.replace("</already_tooted>", "\n".join(essays_who_where_already_tooted) + "</already_tooted>")

# Finally write to index.html:

with open("index.html", "w+") as f:
    f.write(content)

# Create minimized assets:


def minify_js(file_name):
    url = 'https://javascript-minifier.com/raw'
    with open(file_name, "rb") as inp_file:
        data = {'input': inp_file.read()}
    with open(file_name.replace(".js", ".min.js"), "w+") as out_file:
        out_file.write(requests.post(url, data=data).text)


def minify_html(file_name):
    url = "https://htmlcompressor.com/compress"
    with open(file_name, "rb") as inp_file:
        data = {'code': inp_file.read()}
    with open(file_name, "w") as out_file:
        result = requests.post(url, data=data).text
        if result.startswith("<!DOCTYPE html>"):
            out_file.write(result)


for subdir, _, files in os.walk("./"):
    for file in files:
        print(subdir, file)
        if not subdir[2:].startswith("."):
            file_path = os.path.join(subdir, file)
            print("Minimizing asset:", subdir + file)
            if file.endswith(".css") and not file.endswith(".min.css"):
                css_html_js_minify.process_single_css_file(file_path, comments=True)
            elif file.endswith(".js") and not file.endswith(".min.js") and file != "materialize.js":
                minify_js(file_path)
            elif file.endswith(".html") and "called_from_gh_pages" in sys.argv:
                minify_html(file_path)
            if file_path == "./images/icon.png":
                # Convert png to jpeg
                pass
            elif file_path == "./images/44.jpeg":
                # Compress
                pass


# Toot to Mastodon:

for (essay_title, essay_anchor, essay_content_as_markdown, image) in new_essays:
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
        + '" is out and you can read it on https://phseiff.com/e/' + essay_anchor + ' !',
        media_ids=[mastodon.media_post(image_name)]
    )
    os.remove(image_name)
    """
    essay_content_as_markdown,
    spoiler_text='Small automated update using #mastodonpy: My new essay "' + essay_title
    + '" is out and you can read it on https://phseiff.com/#' + essay_name + ' or in this toot!'
    """
