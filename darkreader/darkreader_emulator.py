from selenium import webdriver
import geckodriver_autoinstaller
import subprocess


geckodriver_autoinstaller.install()


def main():
    p = subprocess.Popen(["darkreader/start_flask.sh"])

    driver = webdriver.Firefox()
    js = """
    var callback = arguments[0];
    DarkReader.exportGeneratedCSS().then(function(result){callback(result);});
    """

    # Generate darkreader css for index.html:
    driver.get("http://127.0.0.1:5000/")
    darkreader_generated_css = driver.execute_async_script(js).replace("http://127.0.0.1:5000", "https://phseiff.com")
    with open("index.html.darkreader.css", "w") as f:
        f.write(darkreader_generated_css)
    with open("index.html", "r") as f:
        content = f.read()
        content = content.replace("""
    <script type="text/javascript" src="darkreader/darkreader.min.js"></script>
    <script>
        DarkReader.setFetchMethod(window.fetch);
        DarkReader.enable({ // <-- always use darkmode instead of, like previously, adapting to the system.
            brightness: 100,
            contrast: 90,
            sepia: 10
        });
    </script>""", """<link type="text/css" rel="stylesheet" href="/index.html.darkreader.min.css">""")
        content = content.replace("""
    <! Ensure dark reader is executed again after we updated the essays using javascript. >
    <script>
        DarkReader.disable();
        DarkReader.enable({ // <-- always use darkmode instead of, like previously, adapting to the system.
            brightness: 100,
            contrast: 90,
            sepia: 10
        });
    </script>""", """<link type="text/css" rel="stylesheet" href="/index.html.darkreader.min.css">""")
    with open("index.html", "w") as f:
        f.write(content)

    # Generate darkreader css for github card:
    driver.get("http://127.0.0.1:5000//github-card/response.html")
    darkreader_generated_css = driver.execute_async_script(js).replace("http://127.0.0.1:5000", "https://phseiff.com")
    with open("github-card/response.html.darkreader.css", "w") as f:
        f.write(darkreader_generated_css.split("/* Modified CSS */")[1])
    with open("github-card/response.html", "r+") as f:
        content = f.read()
        content = content.replace("""
<script type="text/javascript" src="../darkreader/darkreader.min.js"></script>
<script>
    DarkReader.setFetchMethod(window.fetch)
    DarkReader.enable({
        brightness: 100,
        contrast: 90,
        sepia: 10
    });
</script>""", """<link type="text/css" rel="stylesheet" href="/github-card/response.html.darkreader.min.css">""")
    with open("github-card/response.modified.html", "w") as f:
        f.write(content)

    driver.get("http://127.0.0.1:5000/404.html")
    darkreader_generated_css = driver.execute_async_script(js).replace("http://127.0.0.1:5000", "https://phseiff.com")


    p.kill()
    driver.close()
