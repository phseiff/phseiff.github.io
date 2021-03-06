(function(e) {
    var t = "github-card/response.modified.html";
    // var t = "//cdn.jsdelivr.net/github-card/1.0.2/";
    var r, i = 0;
    var a = e.getElementsByTagName("meta");
    var n, d, l, c;
    for (r = 0; r < a.length; r++) {
        var s = a[r].getAttribute("name");
        var f = a[r].getAttribute("content");
        if (s === "gc:url") {
            n = f
        } else if (s === "gc:base") {
            t = f
        } else if (s === "gc:client-id") {
            d = f
        } else if (s === "gc:client-secret") {
            l = f
        } else if (s === "gc:theme") {
            c = f
        }
    }
    console.log("t:", t);

    function u(t) {
        if (e.querySelectorAll) {
            return e.querySelectorAll("." + t)
        }
        var i = e.getElementsByTagName("div");
        var a = [];
        for (r = 0; r < i.length; r++) {
            if (~i[r].className.split(" ").indexOf(t)) {
                a.push(i[r])
            }
        }
        console.log("u(t) = a:", a);
        return a
    }

    function g(e, t) {
        console.log("g(e, t):", e.getAttribute("data-" + t));
        return e.getAttribute("data-" + t)
    }

    function h(e) {
        if (window.addEventListener) {
            window.addEventListener("message", function(t) {
                if (e.id === t.data.sender) {
                    e.height = t.data.height
                }
            }, false)
        }
    }

    function v(r, a) {
        a = a || n;
        if (!a) {
            var s = g(r, "theme") || c || "default";
            // a = t + "cards/" + s + ".html"
        }
        var f = g(r, "user");
        // var u = g(r, "repo");
        var v = g(r, "github");
        if (v) {
            v = v.split("/");
            if (v.length && !f) {
                f = v[0];
                // u = u || v[1]
            }
        }
        if (!f) {
            return
        }
        i += 1;
        var m = g(r, "height");
        /* var o = g(r, "width");
        var b = g(r, "target");
        var w = g(r, "client-id") || d;
        var p = g(r, "client-secret") || l; */
        var A = "ghcard-" + f + "-" + i;
        var y = e.createElement("iframe");
        y.setAttribute("title", "embedded GitHub visitor card");
        y.setAttribute("id", A);
        y.setAttribute("frameborder", 0);
        y.setAttribute("scrolling", 0);
        y.setAttribute("allowtransparency", true);

        /*
        var E = a + "?user=" + f + "&identity=" + A;
        if (u) {
            E += "&repo=" + u
        }
        if (b) {
            E += "&target=" + b
        }
        if (w && p) {
            E += "&client_id=" + w + "&client_secret=" + p
        }
        console.log("E:", E); */
        var E = "github-card/response.modified.html";
        y.src = E;
        y.width = o || Math.min(r.parentNode.clientWidth || 400, 400);
        if (m) {
            y.height = m
        }
        console.log("E:", E);
        console.log("y:", y);
        h(y);
        r.parentNode.replaceChild(y, r);
        return y
    }
    var o = u("github-card");
    for (r = 0; r < o.length; r++) {
        v(o[r])
    }
    if (window.githubCard) {
        window.githubCard.render = v
    }
})(document);