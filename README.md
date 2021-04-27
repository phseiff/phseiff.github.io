# My web presence
My private website. Not visited it yet? Then it is time to do so :D You can find it [here](https://phseiff.com).
Feedback is greatly appreciated, though I can't guarantee I'll find time to change my site accordingly.

![Website Banner](https://phseiff.com/images/final-banner-blurred-edges.png)

The following essay can also be read [as an essay on my website](https://phseiff.com/e/why-i-like-my-website), where it is automatically embedded from this README.

---

# Why I am proud of my website
even though it gets no visitors and I don't have the time to make a lot of content for it.

![The preview image of the repository I have my website's code in](https://raw.githubusercontent.com/phseiff/phseiff.github.io/master/images/repo-preview-card.png)

As you would know if I (illegally, for obvious reasons) published tracking data for my website, I haven't really had any visitors since I created it. After all, why would I? There is barely any content on my Website, even if you count the two project cards I added recently, and every other bit of content somewhat meta-heavily resolves around the very essence of my Website.

Then why would I be proud of it?

Because I made a lot of good design decisions, lots of clever engineering, a handfull of innovative solutions, one full-fledged markdown conversion tool, loads of sophisticated optimizations and my own website builder in the process, just to create a website with barely any content yet. In a way, my biggest overkill ever.

And yet I am proud of it! Because I learned a lot in the process, and I created a lot in the process, and I can flex a lot with my Website whenever I find someone willing to listen to me. Which actually is exactly what I will be doing in this essay: Talk about the many design decisions that went into my Website, and how sophisticated it does the hosting of some none-existent essays.
Expect this essay to be a little technical, since I am a programmer type of Person, and those tend to refer to code design decisions when they talk about design decisions.

With that being said and the introduction out if our way, let's dive right in into the juicy details! I will go over them using a nestled bullet point list, but that's because these things are easier to navigate than classic paragraphs, so be prepared to read full paragraphs of text within them!

### into the rabbit hole of self-congratulation

It worth noting for all of these topics that my website is a static website, so there is no server side magic available for any of this.

* **Performant one-page website**:

  My whole website is served within one single HTML file (including some external resources like CSS, images and javascript, of course).
  Every link within my website is internal and either calls some javascript (if javascript is enabled), or scrolls to an anchor (if it isn't);
  more about this later.
  
  Why does it look like there are several pages within the website, then?
  
  In general, my website is divided into one main page, which shows an introduction sentence and a list of all of my projects and my essays, and a multitude of "subpages",  which are opened by clicking essay cards on my website, among other things.
  Each one of my essays, for example, has its own "subpage".
  When you click on an essay card (and potentially some other things, depending on how this website develops), you immediately, with no loading time save for a quick animation in which the page seems to scroll "up" towards the newly opened subpage, end up on the corresponding subpage.
  The content of the essay is shown, and a red cross in the upper-right corner appears which you can click to make the essay disappear again, returning you to the main page with another scroll animation.
  
  Opening a subpage not only displays additional content in the window, but also changes several other things associated with switching to another page.
  The URL in the URL bar changes to something like `phseiff.com/e/name-of-the-essay`, the title of the tab changes, and metadata relevant to search engines like the description of the page, the preview image of the page and even its language changes;
  and vice versa when you leave a subpage.
  Entering a subpage link like `phseiff.com/e/name-of-the-essay` into your browser, vice versa, leads to an empty dummy page that redirects to `phseiff.com/#name-of-the-essay`, which is then unfolded into `phseiff.com/e/name-of-the-essay` (the real one, not the dummy) by a bunch of javascript in `phseiff.com` that interprets the requested anchor and translates it to a subpage.
  
  You might have guessed that this is done using javascript, which is executed every time an essay card is clicked;
  however, there are some things worth noting here:
  
  * **The content of the essays is hidden until it is unhidden by javascript, but it is not *loaded* by the javascript.**
    
    This is relevant because it means that my website is indeed a single-page-website, and loaded all at once.
    This means that you can open my website, disable your internet, and still access all of its contents, without having to manually cache every single page of it.
    It also implies better performance, since having the small overhead of loading some extra kilobyte of essay text (and a bunch of images, whom I might change to javascript-loaden if this becomes too much of a burden later) is much preferable over making separate server requests for every single subpage, each of whom varies only in parts of its content rather than relevant heavy boilerplate code.
    Having everything within the page at loading time is also relevant for supporting people who disabled javascript, but we will talk some more about that later.
    
  * **Advanced as well as simple crawlers and applications find all subpages, including their metadata.**
    
    Advanced crawlers like the ones used by Google for page indexing emulate pages in a headless browser.
    This allows them to identify javascript-generated subpages, so every subpage (`phseiff.com/e/foo`, `phseiff.com/e/bar`, et cetera) is correctly recognized as its own page, including its title, description, language and contents, as indicated by the javascript-modified meta tags.
    Google Search Console confirms this works, so ideally, every page should be its own entry in the search engine.
    In practice, Google only indexes the main page, since it determines the subpages to be "content-identical" to the main page (which is an issue I will have to look into some time), but at least it seems to recognize them as separate entities, according to the Search Console ;)
    
    There are also many applications for which a lookup of the page is performed by simply loading the HTML from the page and parsing it, rather than loading the page with a headless browser, which means that these applications will receive the dummy page at `phseiff.com/e/foo` rather than the contents of the actual subpage.
    For applications like these, be it crawlers of primitive search engines or a social media platform looking up the OpenGraph protocol metadata of the page, each dummy page contain the metadata of its respective subpage, too.
    
  * **The page is fully operational even if javascript is disabled.**
    
    It might come as a surprise that all of this works if one has javascript disabled as well.
    This is implemented by serving the page as a page that works without any javascript at all, and then executing some javascript that modifies it into a page that works based on javascript.
    This modification to a javascript-based website, since it is based on javascript itself, is only executed if javascript is enabled.
    
    When served, every subpage's content is visible all at once (but below all other elements of the page rather than between the introduction and the essay cards, to ensure the essay cards remain at the top as a table of contents), and each one has its own id so it can be linked to using page-internal anchor links.
    Analogously, every essay card uses a page-internal link to link its subpage;
    for example, one essay card might link to `#foo`, where `#foo` is the ID of the subpage that is usually accessible via `phseiff.com/e/foo`.
    There are also two arrows, one scrolling to the top and one scrolling to the footer of the page if one clicks them, permanently displayed when javascript is disabled.
    All of this is obviously not the best user experience, but it allows easy navigation and accessing all the contents of the page even without js.
    The redirection dummy pages also work with javascript disabled, so even entering the domain of a subpage directly into the browser works as expected with javascript disabled.
    
    If javascript is enabled, on the other hand, all of these elements are changed directly when the page loads;
  subpages are hidden, `#subpage`-links are changed to something along the lines of `javascript:set_location("subpage");`, `#top`-links (and similar ones) are changed to something along the lines of `javascript:smooth_scroll("top");`, the to-the-top and to-the-bottom buttons are hidden unless one is far away from their intended destination, and so on.
    
    The non-javascript version of the page is also not exactly optimized for SEO, but that's okay because the biggest relevant search engines all use headless browsers with activated javascript to analyse web pages.

* **Writing my own website-builder**:

  I also wrote my own website builder from scratch in Python.
  It's a pretty simple one, but I had to do it in order to support my website's architecture.
  
  My website builder does essentially do two things:
  1. Maintain the RSS feed and the essay- and project cards on my website.
     
     Both of these things are handled by manually editing an RSS file called `feed-original.rss`, which is used for building the essay cards, and a subset of which is used for the actual RSS feed of my website, based on meta-tags that indicate whether an item is intended to be part of the final RSS feed or just a card on my website.
     
  2. Maintain the subpages of my website (which is done by manually managing a folder full of markdown files, where `foo.md` describes the contents of the `phseiff.com/e/foo` subpage, with no additional action required to be done to add them to my website other than creating them).
    
  There are, of course, some details here, in which I'd like to further dive:
  
  * **Splitting the input of the website builder and the actual website code into separate repositories:**
    
    I really want people to see my website's code and potentially profit from it, as well as get attention for it wherever possible (hehe), so my website's code and parts of its website builder are in a public GitHub repository.
    The markdown files that describe my essays, as well as the html-files immediately generated from them, as well as my RSS feed, are of course also accessible by anyone, because (a) they are embedded into my website, and (b) they are completely hosted, including every bit of code;
    however, I don't have them in a public repo, because I don't want people looking over my shoulder whilst I work on them, dig through their git history, make pull requests or view my repo out of context, plus I can't be bothered to add the context to which website it belongs to the repository in which I have my website's content.
    
    For this reason, I have my website's content in a private repository, transparent since its contents are hosted via GitHub pages, and simultaneously shielded from the uninterested public.
    Pushing changes to this repo, as well as seeing (or not seeing) the clock hit 00:00, causes the repo to run an action which builds its RSS feed, converts all markdown files to HTML, and then triggers an action in my public website repo which embeds the subpage's HTML files into the website and builds the essay- and project cards.
    The public repository also re-builds the website when I push any changes, of course.
    
  * **Maintaining the website's cards and RSS feed:**
    
    As mentioned above, I maintain a file called `feed-original.rss` within my website contents repository.
    If I add, for example, an entry like the following (
    
    ```xml
     <item>
      <image>https://phseiff.com/phseiff-essays/shadows.jpeg</image>
      <title>Why we should redeem shadows in minimalist design</title>
      <description>A rant about people who rant about shadow in minimalistic design, mainly written to defend my use of
    shadows in this blog's design and as an introduction to my blog.</description>
      <link>https://phseiff.com/#minimalist-shadows</link>
      <pubDate>Fr, 21 Aug 2020 18:00:00 +0200</pubDate>
      <language>en</language>
      <phseiff:effort>2/5</phseiff:effort>
      <phseiff:announcement>
        Here's a short essay (or should I call it a rant?) I wrote about my aversion to the idea that minimalist design
        requires the absence of shadows, or really that there is anything that context-independently contradicts minimalism.
        Check it out if you're interested!
      </phseiff:announcement>
     </item>
    ```
    
    ), it adds an essay card to my website with the appropriate title, description and sparkle-rating, as follows:
  
    ![An image of a corresponding essay card, with a fitting description, title and image](https://phseiff.com/images/writeup-illustration-essay-card.png)
  
    
    
  * **Converting markdown-files to html:**

* **Auto-generating darkmode with a headless browser**:

* **Other optimizations & Gadgets I spent way more time on than I probably should have**:

  * 404 Error page:
    
  * SEO optimization & image compression

### wrapping it up

I guess in a way, you could say this essay is me making peace with the fact that I didn't create as much content for my website as I would've liked to in the past 8 months, but it is also, at least partially, me realizing how much I've grown over the past year, both personally and professionally, and how much this website illustrates that and how much there's yet to come.

Anyways, I hope you had fun reading this, and that there were at least a handful of solutions you found interesting, be it positive or negative. :)