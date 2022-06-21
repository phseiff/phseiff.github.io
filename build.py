import requests
import time
import sys
import os
import css_html_js_minify
from PIL import Image
from mastodon import Mastodon
import subprocess
import bs4
import minify_html as minify_html_module
from darkreader import darkreader_emulator

if "called_from_gh_pages" in sys.argv:
    time.sleep(20)

description_of_myself = "Hello! I'm Phii, and I'm an avid non-commercial developer, manga-binge-reader, \
vegetarian, programmer, writer and denglish-speaker."

#requests.get("https://raw.githubusercontent.com/phseiff/phseiff/master/README.md").text

# Parse RSS feed:


def extract_item(tag, text):
    text, text_within_tags = text.split("<" + tag + ">", 1)
    text_within_tags, text2 = text_within_tags.split("</" + tag + ">", 1)
    text += text2
    return text, text_within_tags


redirecting_page = """<!DOCTYPE HTML>

<html lang="{language}">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="0;url=http://phseiff.com/#{name}">
        <link rel="canonical" href="https://phseiff.com/#{name}">
        
        <title>{title} - by phseiff</title>
        <meta name="description" content="{description}"/>
        <meta property="og:title" content="{title} - by phseiff"/>
        <meta property="og:type" content="website"/>
        <meta property="og:image" content="{image}"/>
        <meta property="og:url" content="https://phseiff.com/e/{name}"/>
        <meta property="og:description" content="{description}"/>
        <meta name="twitter:card" content="summary_large_image"/>
        <meta name="twitter:site" content="@phseiff"/>
        <meta name="twitter:creator" content="@phseiff"/>
        <meta name="twitter:image" content="{image}"/>
        <meta name="twitter:title" content="{title} - by phseiff"/>
        <meta name="twitter:description" content="{description}"/>
    </head>
    <body>
        <script>
          window.location.href = "https://phseiff.com/#{name}";
        </script>
     
        <title>Redirection page</title>
        
        If you see this page, it means you are being redirected to
        <a href='https://phseiff.com/#{name}'>the article you requested</a>,
        but your browser is too old to do so automatically. You can still follow the link manually. :)
    </body>
</html>
"""

# Initialize items for sitemap and redirection pages:

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


# Initialize items for RSS feed parsing:

essays_to_toot_about = list()  # list of tuples of (title, anchor, content, essay_image)
visible_essay_anchors = list()  # list of anchors used to access essays on the webpage
essay_cards = ""  # string describing the cards used for accessing all essays
project_cards = ""  # the same thing, but for projects

# RSS feed parsing:

rss_feed = requests.get(url="https://phseiff.com/phseiff-essays/feed-original.rss").text
rss_feed_soup = bs4.BeautifulSoup(rss_feed, "xml")
for rss_item_soup in rss_feed_soup.find_all("item"):

    # iterate over all data fields of the item and extract their data:
    description = str(rss_item_soup.find("description").string)
    title = str(rss_item_soup.find("title").string)
    link = str(rss_item_soup.find("link").string)
    pubDate = str(rss_item_soup.find("pubDate").string)
    image = str(rss_item_soup.find("image").string)
    is_project = True if rss_item_soup.has_attr("project") else False
    if not is_project:
        language = str(rss_item_soup.find("language").string)
        announcement = " ".join(str(rss_item_soup.find("announcement").string).split())
        effort = int(str(rss_item_soup.find("effort").string).split("/")[0].strip())
    else:
        language = "en"
        announcement = "None"
        effort = 5.0  # because why not, it isn't needed anyway :)
        # get stars:
        repo_name = image.split("/")[-1].split(".jpeg")[0]
        effort_string = ""
        try:
            repo_data = requests.get("https://api.github.com/repos/phseiff/" + repo_name).json()
            star_count = repo_data['stargazers_count']
            effort_string = str(star_count) + " <span class=\"yellow-emoji\">⭐</span> on GitHub"
        except:
            pass

    essay_anchor = link.split("#")[-1]

    # render the new essay card:
    new_card = """
                <a {link_data} class="card-to-show-essay standard-text-color">
                    <div class="essay-card">
                        <div class="col-content">
                            <div class="zoom">
                                <div class="card orange-backdrop">
                                    <div class="card-image">
                                        <img alt="{image}" src="{image}">
                                        <span class="left-badge">{stars}</span>
                                        <span class="badge">{creation_date} {language}</span>
                                    </div>
                                    <div class="card-content">
                                        <span class="card-title">{title}</span>
                                        {description}
                                    </div>
                                    <div class="card-action">
                                        <a {link_data}>{invitation}</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </a>""".format(
                            image=image.rsplit(".", 1)[0] + ".jpeg",
                            title=title,
                            description=description,
                            link_data=(
                                ('href="#%s"' % essay_anchor)
                                if not is_project
                                else ('href="%s" target="_blank" rel="noopener noreferrer"' % link)
                            ),
                            creation_date=" ".join(pubDate.split(" ")[:4]),
                            language=(
                                ("| 🇬🇧" if language == "en" else "| 🇩🇪")
                                if not is_project
                                else ""
                            ),
                            invitation=(("View on GitHub! "
                                         + "<img"
                                         + " style=\"height: 1em;\""
                                         + " src=\"/external-links/external-link-yellow.svg\""
                                         + " alt=\"external link symbol\">")
                                        if is_project else "Read here!"),
                            stars=(
                                ("<span class=\"yellow-emoji\">" + "".join(["✨"] * effort) + "</span>"
                                 + "<span class=\"gray-emoji\">" + "".join(["✨"] * (5 - effort)) + "</span>")
                                if not is_project
                                else effort_string
                            )
    )

    # add the nw card to the proper set of cards:
    if is_project:
        project_cards += new_card
    else:
        essay_cards += new_card

    # do things related to the essay sub-page if it's an essay rather than a project:
    if not is_project:

        # accumulate data for later:
        visible_essay_anchors.append(essay_anchor)
        essays_to_toot_about.append((
            title,
            essay_anchor,
            requests.get("https://phseiff.com/phseiff-essays/" + essay_anchor + ".md").text,
            image,
            announcement
        ))

        # accumulate descriptions, titles and images for individual essay pages,
        #  so they can be changed via javascript when someone navigates to a subpage:
        descriptions_string += "\"" + essay_anchor + "\": \"" + description.replace("\"", "\\\"") + "\",\n    "
        titles_string += "\"" + essay_anchor + "\": \"" + title.replace("\"", "\\\"") + " - by phseiff\",\n    "
        images_string += "\"" + essay_anchor + "\": \"" + image.replace("\"", "\\\"") + "\",\n    "
        languages_string += "\"" + essay_anchor + "\": \"" + language + "\",\n    "

        # build redirection pages for essays:
        for directory in ("e", "essay"):
            if not os.path.exists(directory + "/" + essay_anchor):
                os.makedirs(directory + "/" + essay_anchor)
            with open(directory + "/" + essay_anchor + "/index.html", "w") as f:
                f.write(redirecting_page.format(
                    name=essay_anchor,
                    description=description,
                    image=image,
                    title=title,
                    language=language,
                ))

        # Save the change date of the essay, so we can build our sitemap from it:
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
            print("output from asking for last change:", output)
            last_change_date = str(output, encoding="UTF-8").split("T")[0]
            update_date = last_change_date[1:][:-1]
            print("Age:", update_date)
        else:
            update_date = "example"

        # accumulate data for our sitemap into a string that we will later save:
        xml_sitemap_entry = """<url>
          <loc>https://phseiff.com/e/{name}</loc>
          <lastmod>{date}</lastmod>
          <changefreq>weekly</changefreq>
          <priority>0.5</priority>
          <xhtml:link rel="alternate" hreflang="{language}" href="https://phseiff.com/e/{name}"/>
       </url>
       <!-- Further links -->""".format(name=essay_anchor, language=language, date=fix_errors_in_date_format(update_date))
        xml_sitemap_content = xml_sitemap_content.replace("<!-- Further links -->", xml_sitemap_entry)

print("essay cards:", essay_cards)
print("project cards:", project_cards)

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
            + ("display: none;" if essay not in visible_essay_anchors and essay != "LICENSE" else "") + '" '
            # class:
            + 'class="embedded-essay" '
            # id (essay_name):
            + 'id="' + essay.replace("/", "_") + '" '
            + '>'
            # content:
            + requests.get('https://phseiff.com/phseiff-essays/' + essay + '.html').text.replace(
                'href="https://phseiff.com/phseiff-essays/LICENSE.html"',
                'href="#LICENSE"'
            ).replace('<link href="/phseiff-essays/css/github-css.css" rel="stylesheet"/>', '')
            + '<span style="height: 300px"></span></span>\n'
        )

content = content.replace("<!-- the essays content -->", essay_content)
content = content.replace("{description}", description_of_myself)
content = content.replace("<!-- essay cards -->", essay_cards)
content = content.replace("<!-- project cards -->", project_cards)
with open("handle_tables/handle-tables.html", "r") as f:
    content = content.replace("<!-- small table content -->", f.read().split("<!-- ~~~separator~~~ -->")[1])

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

current_website_content = requests.get("https://phseiff.com/index.html").text
if "<already_tooted>" in current_website_content:
    tag_name = "already_tooted"
elif "<already-tooted>" in current_website_content:
    tag_name = "already-tooted"
else:
    raise Exception()
if "<already_tooted>" in content:
    current_tag_name = "already_tooted"
elif "<already-tooted>" in content:
    current_tag_name = "already-tooted"
else:
    raise Exception()

new_essays = list()

assert "<" + tag_name + ">" in current_website_content
assert "</" + tag_name + ">" in current_website_content.split("<" + tag_name + ">")[1]
assert "<" + current_tag_name + ">" in content
assert "</" + current_tag_name + ">" in content.split("<" + current_tag_name + ">")[1]

essays_who_where_already_tooted = current_website_content.split("<" + tag_name + ">", 1)[1].split(
    "</" + tag_name + ">")[0].split()
print("already tooted:\n" + "\n".join(essays_who_where_already_tooted))

for (a, essay_anchor, b, c, d) in essays_to_toot_about:
    if essay_anchor not in essays_who_where_already_tooted:
        new_essays.append((a, essay_anchor, b, c, d))
        essays_who_where_already_tooted.append(essay_anchor)
        print("new essay:", essay_anchor)

content = content.replace("</" + current_tag_name + ">",
                          "\n".join(essays_who_where_already_tooted) + "</already-tooted>")
content = content.replace("<" + current_tag_name + ">",
                          "<already-tooted>")

# Make sure all images have an alt text:

content_soup = bs4.BeautifulSoup(content, "html.parser")
imgs_without_alt_text = content_soup.find_all("img", alt=False)
if imgs_without_alt_text:
    raise Exception("Found images without alt text:\n" + "\n".join([str(img) for img in imgs_without_alt_text]))

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
    with open(file_name, "r") as in_file:
        content = in_file.read()
    print(file_name, "size:", len(content))
    minified_content = minify_html_module.minify(content, minify_js=False, minify_css=True)
    print(file_name, "new size:", len(minified_content))
    print(file_name, "gain:", str((len(minified_content)/len(content)*100).__round__(2)) + "%")
    with open(file_name, "w") as out_file:
        out_file.write(minified_content)
    """url = "https://htmlcompressor.com/compress"
    with open(file_name, "rb") as inp_file:
        data = {'code': inp_file.read()}
    with open(file_name, "r") as out_file:
        old_content = out_file.read()
    with open(file_name, "w") as out_file:
        result = requests.post(url, data=data).text
        if result.startswith("<!DOCTYPE html>"):
            out_file.write(result)
        else:
            out_file.write(old_content)"""


def compress_icon(file_name, height, bg_color, quality):
    thumbnail = Image.open(file_name)
    size = (int(thumbnail.size[0] * height/thumbnail.size[1]), height)
    thumbnail.thumbnail(size, Image.ANTIALIAS)

    offset_x = max((size[0] - thumbnail.size[0]) / 2, 0)
    offset_y = max((size[1] - thumbnail.size[1]) / 2, 0)
    offset_tuple = (int(offset_x), int(offset_y))

    final_thumb_rgba = Image.new(mode='RGBA', size=size, color=bg_color+(255,))
    final_thumb_rgba.paste(thumbnail, offset_tuple, thumbnail.convert('RGBA'))

    final_thumb = Image.new(mode='RGB', size=size, color=bg_color)
    final_thumb.paste(final_thumb_rgba, offset_tuple)

    final_thumb.save(file_name.replace(".png", ".jpeg"), 'JPEG', quality=quality, optimize=True, progressive=True)


def compress_all_files(with_html=True):
    """This will be called twice, once before the darkreader js is baked (to provide the nessesary files), and once
    afterwars (to compress the newly compressed files)"""
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
                elif (file.endswith(".html") and not file.endswith("-raw.html") and with_html
                      and os.path.exists(file.rsplit(".html", 1)[0] + "-raw.html")
                      and os.path.isfile(file.rsplit(".html", 1)[0] + "-raw.html")):
                    minify_html(file_path)
                if file_path in ("./images/icon.png", "./images/404.png"):
                    compress_icon(file_path, height=400, bg_color=(205, 122, 0), quality=70)

# Bake darkreader & compress files:


compress_all_files(with_html=False)  # <- to make sure darkreader.min.js exists for the darkreader emulator
darkreader_emulator.main()
compress_all_files()


# Toot to Mastodon:

for (essay_title, essay_anchor, essay_content_as_markdown, image, announcement) in new_essays:
    mastodon = Mastodon(
        access_token=sys.argv[1],
        api_base_url='https://toot.phseiff.com'
    )
    # image_name = "throw_away_image." + image.rsplit(".", 1)[-1]
    # with open(image_name, "wb") as image_file:
    #     image_file.write(requests.get(image).content)
    # frame_image("images/left.png", image_name, "images/right.png")
    mastodon.status_post(
        announcement + "\n\n -> https://phseiff.com/e/" + essay_anchor + "/ <-"
        # 'Small automated update on my essays: My new essay "' + essay_title
        # + '" is out and you can read it on https://phseiff.com/e/' + essay_anchor + ' !',
        # media_ids=[mastodon.media_post(image_name)]  # <-- No need to add an image, when the preview already has one.
    )
    # os.remove(image_name)
    """
    essay_content_as_markdown,
    spoiler_text='Small automated update using #mastodonpy: My new essay "' + essay_title
    + '" is out and you can read it on https://phseiff.com/#' + essay_name + ' or in this toot!'
    """
