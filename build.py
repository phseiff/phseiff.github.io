

with open("index.html", "r") as f:
    content = f.read()
    content.replace("<! the essays content >", essay_co)