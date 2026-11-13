"""
Build the Peano notebook site.

    python3 build.py

Sources you edit:
    site-data.json             what the home page lists (diagrams and tutorials)
    content/<slug>.<lang>.md   tutorials, one file per language (zh-CN, en)
    diagrams/src/*.json        Archify diagram sources; render them with Archify into diagrams/<id>.<lang>.html
    diagrams/static/*.png      still images of the Archify diagrams, used only by the claude.ai copy
    site.css, i18n.js          look and language switch

Generated (do not edit by hand):
    index.html, view.html, tutorial-<slug>.html, site-data.js     local site (Archify diagrams)
    _artifact/                                                   claude.ai copy (still images of the diagrams)
"""

import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = ["zh-CN", "en"]
DEFAULT_LANG = "en"  # language shown until the reader picks one; must match i18n.js

SITE_TITLE = {"zh-CN": "Peano 学习图册", "en": "Peano Notebook"}
SITE_LEDE = {
    "zh-CN": "学习 Peano 框架时写的教程和画的流程图。例子都是 CCZ4 gauge wave：FD4 空间离散，RK4 时间积分，周期边界。",
    "en": "Tutorials and diagrams made while learning the Peano framework. The running example is the CCZ4 gauge wave: FD4 in space, RK4 in time, periodic boundaries.",
}
GROUP = {
    "diagrams": {"zh-CN": "流程图", "en": "Diagrams"},
    "tutorials": {"zh-CN": "教程", "en": "Tutorials"},
}
BACK = {"zh-CN": "← Peano 学习图册", "en": "← Peano Notebook"}
TUTORIAL_EYEBROW = {"zh-CN": "教程", "en": "Tutorial"}
TOC = {"zh-CN": "目录", "en": "Contents"}

FONTS = (
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@500;600;700&display=swap">'
)
MARKED_CDN = "https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"
MATHJAX_CDN = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg.min.js"

TOGGLE = (
    '<div class="lang-switch" role="group" aria-label="Language / 语言">'
    '<button type="button" data-lang-btn="en" aria-pressed="true">EN</button>'
    '<button type="button" data-lang-btn="zh-CN" aria-pressed="false">中文</button>'
    "</div>"
)


def esc(s):
    return html.escape(s, quote=True)


def both(obj, tag="span", cls=""):
    """One element per language; CSS shows the one that matches <html lang>."""
    c = f' class="{cls}"' if cls else ""
    return "".join(f'<{tag}{c} data-lang="{l}">{esc(obj[l])}</{tag}>' for l in LANGS)


def head(title, fragment, extra=""):
    """fragment=True: claude.ai main page (the host adds <html>/<head>/<body>)."""
    common = (
        f"<title>{esc(title)}</title>\n"
        f"{FONTS}\n"
        '<link rel="stylesheet" href="site.css">\n'
        '<script src="i18n.js"></script>\n'
        f"{extra}"
    )
    if fragment:
        return '<meta name="claude:viewport-fit-sides" content="cover">\n' + common
    return (
        f'<!doctype html>\n<html lang="{DEFAULT_LANG}"{{cls}}>\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        + common
        + "</head>\n<body>\n"
    )


def tail(fragment):
    return "" if fragment else "</body>\n</html>\n"


# ---------------------------------------------------------------- pages


def index_page(data, fragment):
    rows = {"diagrams": [], "tutorials": []}
    for d in data["diagrams"]:
        rows["diagrams"].append((f"view.html#{d['id']}", d))
    for t in data["tutorials"]:
        rows["tutorials"].append((f"tutorial-{t['slug']}.html", t))

    groups = []
    for key in ["tutorials", "diagrams"]:
        items = []
        for href, e in rows[key]:
            items.append(
                f'      <li><a class="entry" href="{href}">'
                f'<span class="entry-title">{both(e["title"])}</span>'
                f'<span class="entry-meta">{esc(e["date"])}</span>'
                f'<span class="entry-desc">{both(e["desc"])}'
                f'<span class="entry-src">{esc(e["source"])}</span></span>'
                f"</a></li>"
            )
        groups.append(
            f'  <section class="group" aria-labelledby="g-{key}">\n'
            f'    <h2 id="g-{key}">{both(GROUP[key])}</h2>\n'
            f'    <ul class="entries">\n' + "\n".join(items) + "\n    </ul>\n  </section>"
        )

    body = (
        '<main class="wrap">\n'
        f'  <div class="topbar"><p class="eyebrow" style="margin:0">Peano · ExaHyPE 2 · ExaGRyPE</p>{TOGGLE}</div>\n'
        f"  <h1>{both(SITE_TITLE)}</h1>\n"
        f"  {both(SITE_LEDE, 'p', 'lede')}\n"
        + "\n".join(groups)
        + "\n</main>\n"
        "<style>.entry-src{margin-left:8px}</style>\n"
        "<script>\n"
        "  document.addEventListener('langchange', function (e) {\n"
        f"    document.title = {json.dumps(SITE_TITLE, ensure_ascii=False)}[e.detail];\n"
        "  });\n"
        "</script>\n"
    )
    return head(SITE_TITLE[DEFAULT_LANG], fragment).replace("{cls}", "") + body + tail(fragment)


def view_page(mode, back_href):
    """mode 'archify': interactive Archify diagram in a frame. mode 'static': still image."""
    body = f"""<header class="viewer-bar">
  <div class="left">
    <a class="back" href="{back_href}">{both(BACK)}</a>
    <h1 id="v-title"></h1>
  </div>
  {TOGGLE}
</header>
<iframe class="viewer-frame" id="v-frame" title="" hidden></iframe>
<div class="viewer-plain" id="v-plain" hidden>
  <div class="plate"><img id="v-img" alt=""></div>
  <p class="caption" id="v-cap"></p>
</div>
<p class="viewer-missing" id="v-missing" hidden></p>
<script src="site-data.js"></script>
<script>
  var MODE = {json.dumps(mode)};
  var SITE_TITLE = {json.dumps(SITE_TITLE, ensure_ascii=False)};
  var shown = "";

  function show() {{
    var lang = SiteLang.get();
    var id = location.hash.replace(/^#/, "") || SITE_DATA.diagrams[0].id;
    var d = SITE_DATA.diagrams.filter(function (x) {{ return x.id === id; }})[0];
    var missing = document.getElementById("v-missing");
    if (!d) {{
      missing.textContent = lang === "en" ? "No diagram called \\"" + id + "\\"." : "没有名为 “" + id + "” 的流程图。";
      missing.hidden = false;
      return;
    }}
    missing.hidden = true;
    var title = d.title[lang];
    document.getElementById("v-title").textContent = title;
    document.title = title + " · " + SITE_TITLE[lang];

    var key = id + "." + lang;
    if (key === shown) return;
    shown = key;
    if (MODE === "archify") {{
      var frame = document.getElementById("v-frame");
      frame.title = title;
      frame.src = "diagrams/" + key + ".html";
      frame.hidden = false;
    }} else {{
      var img = document.getElementById("v-img");
      img.src = "diagrams/static/" + key + ".png";
      img.alt = title;
      document.getElementById("v-cap").textContent = d.caption[lang];
      document.getElementById("v-plain").hidden = false;
    }}
  }}
  document.addEventListener("langchange", show);
  window.addEventListener("hashchange", show);
  show();
</script>
"""
    return head(SITE_TITLE[DEFAULT_LANG], False).replace("{cls}", ' class="viewer"') + body + tail(False)


def tutorial_page(t, marked_src, mathjax_src, back_href):
    sources = []
    for lang in LANGS:
        path = os.path.join(HERE, "content", f"{t['slug']}.{lang}.md")
        with open(path, encoding="utf-8") as f:
            md = f.read()
        if "</script" in md.lower():
            raise SystemExit(f"{path}: contains '</script', which would break the page")
        sources.append(f'<script type="text/markdown" id="md-{lang}">\n{md}</script>')

    body = f"""<main class="wrap">
  <div class="topbar"><a class="back" href="{back_href}">{both(BACK)}</a>{TOGGLE}</div>
  <p class="eyebrow">{both(TUTORIAL_EYEBROW)} · {esc(t['source'])} · {esc(t['date'])}</p>
  <nav class="toc" id="toc" hidden aria-label="contents"><p>{both(TOC)}</p><ol id="toc-list"></ol></nav>
  <article class="article" id="article"></article>
</main>
{chr(10).join(sources)}
<script>
  // Formulas: $...$ inline and $$...$$ display, rendered by MathJax as SVG (no fonts or stylesheets needed).
  window.MathJax = {{
    tex: {{ inlineMath: [["\\\\(", "\\\\)"]], displayMath: [["\\\\[", "\\\\]"]] }},
    svg: {{ fontCache: "global" }},
    startup: {{ typeset: false }}
  }};
</script>
<script src="{mathjax_src}"></script>
<script src="{marked_src}"></script>
<script>
  var SITE_TITLE = {json.dumps(SITE_TITLE, ensure_ascii=False)};
  var TITLES = {json.dumps(t['title'], ensure_ascii=False)};

  function render() {{
    var lang = SiteLang.get();
    var article = document.getElementById("article");
    var toc = document.getElementById("toc");
    var list = document.getElementById("toc-list");
    document.title = TITLES[lang] + " · " + SITE_TITLE[lang];
    if (!window.marked) {{
      article.innerHTML = "<p class='status'>" + (lang === "en" ? "Could not load the Markdown renderer. Check the network connection and reload." : "Markdown 渲染器没有载入。请检查网络后刷新页面。") + "</p>";
      return;
    }}
    // Take the formulas out before Markdown sees them (it would eat _ and \\), outside code only.
    var maths = [];
    var parts = document.getElementById("md-" + lang).textContent.split(/(```[\\s\\S]*?```|`[^`\\n]*`)/);
    function keep(open, close) {{
      return function (m, tex) {{ maths.push(open + tex + close); return "@@MATH" + (maths.length - 1) + "@@"; }};
    }}
    for (var i = 0; i < parts.length; i += 2) {{
      parts[i] = parts[i].replace(/\\$\\$([\\s\\S]+?)\\$\\$/g, keep("\\\\[", "\\\\]"))
                         .replace(/\\$([^$\\n]+?)\\$/g, keep("\\\\(", "\\\\)"));
    }}
    var html = marked.parse(parts.join(""));
    article.innerHTML = html.replace(/@@MATH(\\d+)@@/g, function (m, k) {{
      return maths[+k].replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }});

    // Wide tables scroll inside their own box instead of widening the page.
    article.querySelectorAll("table").forEach(function (tb) {{
      var box = document.createElement("div");
      box.className = "table-scroll";
      tb.replaceWith(box);
      box.appendChild(tb);
    }});

    // A copy button in the top-right corner of every code block.
    article.querySelectorAll("pre").forEach(function (pre) {{
      var box = document.createElement("div");
      box.className = "code-box";
      pre.replaceWith(box);
      box.appendChild(pre);
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "copy-btn";
      box.appendChild(btn);
      label(btn, false);
      btn.addEventListener("click", function () {{
        var code = pre.querySelector("code") || pre;
        copyText(code.textContent.replace(/\\n$/, "")).then(function (ok) {{
          label(btn, ok ? "done" : "fail");
          setTimeout(function () {{ label(btn, false); }}, 1600);
        }});
      }});
    }});

    // Contents list from the h2 headings, placed after the title and opening paragraphs.
    list.innerHTML = "";
    article.querySelectorAll("h2").forEach(function (h, i) {{
      h.id = "s" + (i + 1);
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = "#" + h.id;
      a.textContent = h.textContent.replace(/^\\d+\\.\\s*/, "");
      li.appendChild(a);
      list.appendChild(li);
    }});
    toc.hidden = !list.children.length;
    var anchor = article.querySelector("h1");
    while (anchor && anchor.nextElementSibling && anchor.nextElementSibling.tagName === "P") anchor = anchor.nextElementSibling;
    if (anchor) anchor.after(toc);
    typeset(article);
  }}

  var COPY = {{
    "zh-CN": {{ idle: "复制", done: "已复制", fail: "复制失败" }},
    "en": {{ idle: "Copy", done: "Copied", fail: "Copy failed" }}
  }};
  function label(btn, state) {{
    var words = COPY[SiteLang.get()] || COPY.en;
    btn.textContent = words[state || "idle"];
    btn.setAttribute("aria-label", words[state || "idle"]);
    btn.classList.toggle("done", state === "done");
  }}
  function copyText(text) {{
    function fallback() {{
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed"; area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      var ok = false;
      try {{ ok = document.execCommand("copy"); }} catch (e) {{}}
      area.remove();
      return ok;
    }}
    if (navigator.clipboard && window.isSecureContext) {{
      return navigator.clipboard.writeText(text).then(function () {{ return true; }}, function () {{ return fallback(); }});
    }}
    return Promise.resolve(fallback());
  }}
  document.addEventListener("langchange", function () {{
    document.querySelectorAll(".copy-btn").forEach(function (b) {{ label(b, false); }});
  }});

  function typeset(el) {{
    if (!window.MathJax || !MathJax.startup || !MathJax.startup.promise) return;
    MathJax.startup.promise = MathJax.startup.promise
      .then(function () {{ return MathJax.typesetPromise([el]); }})
      .catch(function (e) {{ console.warn(e); }});
  }}
  document.addEventListener("langchange", render);
  render();
</script>
"""
    return head(t["title"][DEFAULT_LANG], False).replace("{cls}", "") + body + tail(False)


# ---------------------------------------------------------------- build


def write(rel, text):
    path = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote", rel)


def main():
    with open(os.path.join(HERE, "site-data.json"), encoding="utf-8") as f:
        data = json.load(f)

    # Check that every listed file exists before writing anything.
    missing = []
    for d in data["diagrams"]:
        for lang in LANGS:
            for rel in [f"diagrams/{d['id']}.{lang}.html", f"diagrams/static/{d['id']}.{lang}.png"]:
                if not os.path.exists(os.path.join(HERE, rel)):
                    missing.append(rel)
    for t in data["tutorials"]:
        for lang in LANGS:
            rel = f"content/{t['slug']}.{lang}.md"
            if not os.path.exists(os.path.join(HERE, rel)):
                missing.append(rel)
    if missing:
        print("warning: these files are listed in site-data.json but missing:")
        for m in missing:
            print("   ", m)

    site_data_js = (
        "// Generated by build.py from site-data.json. Do not edit.\n"
        "window.SITE_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    )

    # Local site: Archify diagrams, Markdown renderer from vendor/.
    write("site-data.js", site_data_js)
    write("index.html", index_page(data, fragment=False))
    write("view.html", view_page("archify", "index.html"))
    for t in data["tutorials"]:
        write(f"tutorial-{t['slug']}.html", tutorial_page(t, "vendor/marked.min.js", "vendor/mathjax-tex-svg.min.js", "index.html"))

    # claude.ai copy: still images of the diagrams, Markdown renderer from cdnjs.
    write("_artifact/site-data.js", site_data_js)
    write("_artifact/index.html", index_page(data, fragment=True))
    write("_artifact/view.html", view_page("static", "./"))
    for t in data["tutorials"]:
        write(f"_artifact/tutorial-{t['slug']}.html", tutorial_page(t, MARKED_CDN, MATHJAX_CDN, "./"))


if __name__ == "__main__":
    main()
