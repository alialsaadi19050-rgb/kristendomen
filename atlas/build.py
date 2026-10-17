# Bygger Kristendomen.html av kapitelfilerna i kapitel/ och mallen i mall/.
# Kör: python -I atlas/build.py
import json, re, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(ROOT), "Kristendomen.html")
ORDER = ["jesus", "treenighet", "kyrkan", "leva", "vetenskap"]


def read(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


VAX = read("mall/vaxtcell.html").split("\n")
L = lambda a, b: "\n".join(VAX[a - 1:b])
FONTS = L(3, 5)
BASE_CSS_FX = L(6, 383)          # grund-CSS + fx-css + fx-js
HELPERS = L(810, 864)            # $, store, el, esc, shuffled, explorer, stepper, sorter
TAIL_JS = L(1063, 1160).replace("<span>s. ${esc(p)}</span>", "<span>${/^\d/.test(p)?\"s. \"+esc(p):esc(p)}</span>")  # ordlista, flashcards, quiz, aktiv länk i menyn
FLASH_STYLE = VAX[771]
KORT = L(773, 795)
CLICK = VAX[1162]

PALETTE = """
:root{--bg:#EEE7DB;--paper:#F7F2E8;--ink:#2A211B;--muted:#5C4F45;--line:#DACFBE;
  --membrane:#A8771A;--membrane-soft:#EFDDB6;--protein:#3A5699;--protein-soft:#D9DEEC;
  --mito:#A8382C;--mito-soft:#EFD5CE;--good:#2C7550;--good-soft:#D3E6D6;--bad:#B03A3A;--bad-soft:#F0D6D3;
  --purple:#6643B5;--purple-soft:#E2D9EE;--good-btn:#24724A;--mito-btn:#A8352A;--btn-ink:#FFFFFF;color-scheme:light}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#15110E;--paper:#1F1915;--ink:#EFE7DD;--muted:#B9AC9F;--line:#3A2F27;
  --membrane:#E2B54E;--membrane-soft:#3A2F1C;--protein:#8FA8EA;--protein-soft:#1F2A45;
  --mito:#EB7F70;--mito-soft:#402320;--good:#5CC28A;--good-soft:#1D3528;--bad:#EC7C7C;--bad-soft:#3F2323;
  --purple:#B49AF0;--purple-soft:#2C2342;--good-btn:#5CC28A;--mito-btn:#EB7F70;--btn-ink:#14100D;color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#15110E;--paper:#1F1915;--ink:#EFE7DD;--muted:#B9AC9F;--line:#3A2F27;
  --membrane:#E2B54E;--membrane-soft:#3A2F1C;--protein:#8FA8EA;--protein-soft:#1F2A45;
  --mito:#EB7F70;--mito-soft:#402320;--good:#5CC28A;--good-soft:#1D3528;--bad:#EC7C7C;--bad-soft:#3F2323;
  --purple:#B49AF0;--purple-soft:#2C2342;--good-btn:#5CC28A;--mito-btn:#EB7F70;--btn-ink:#14100D;color-scheme:dark}
"""

SHARED_CSS = PALETTE + """
header.hero h1 em{color:var(--acc)}
[hidden]{display:none!important}
.org.sel text{stroke:none!important}
.org:focus-visible>*{outline:none}
svg text{font-family:var(--f-body)}
/* bokens frågor med svarsförslag */
.qbook{list-style:none;padding:0;margin:10px 0;counter-reset:qb;display:grid;gap:10px}
.qbook>li{counter-increment:qb;background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:12px 16px 12px 52px;position:relative}
.qbook>li::before{content:counter(qb);position:absolute;left:14px;top:12px;width:26px;height:26px;border-radius:50%;background:var(--acc);color:var(--paper);font-family:var(--f-display);font-weight:800;display:grid;place-items:center;font-size:.9rem}
.qbook>li>b{display:block;font-family:var(--f-display);font-size:1.05rem;line-height:1.35}
.qbook details{margin-top:6px}
.qbook summary{cursor:pointer;color:var(--acc);font-weight:700;font-size:.95rem;list-style:none;display:inline-flex;gap:6px;align-items:center}
.qbook summary::-webkit-details-marker{display:none}
.qbook summary::before{content:"▸";transition:transform .2s}
.qbook details[open] summary::before{transform:rotate(90deg)}
.qbook details>div{margin-top:6px;padding:10px 14px;border-radius:10px;background:var(--bg);font-size:.98rem}
.qbook details>div p:first-child{margin-top:0}.qbook details>div p:last-child{margin-bottom:0}
/* två kort bredvid varandra */
.duo{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin:14px 0}
.duo>div{background:var(--paper);border:1px solid var(--line);border-top:5px solid var(--c,var(--acc));border-radius:12px;padding:14px 18px}
.duo>div h3{margin-top:0;font-size:1.15rem}
.duo>div .mono{display:block;margin-bottom:2px}
.duo>div p{margin:.4rem 0}
/* citat ur trosbekännelser m.m. */
.creed{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px 20px;font-size:.98rem;line-height:1.7}
.creed h3{margin-top:0}
.creed p{margin:.5rem 0}
.creed span{border-radius:4px;transition:background-color .3s var(--ease-out),color .3s}
.creed span.hl{background:var(--membrane-soft);box-shadow:0 0 0 2px var(--membrane-soft)}
.creed button.ln{all:unset;cursor:pointer;border-radius:4px;padding:0 2px}
.creed button.ln:hover,.creed button.ln:focus-visible{background:var(--protein-soft)}
.creed button.ln.on{background:var(--membrane-soft);outline:2px solid var(--membrane)}
.pill{display:inline-block;font-family:var(--f-mono);font-size:.72rem;letter-spacing:.04em;text-transform:uppercase;border:1px solid var(--line);border-radius:999px;padding:1px 9px;color:var(--muted);vertical-align:2px}
.pill.ppt{border-color:var(--purple);color:var(--purple)}
.pill.extra{border-color:var(--mito);color:var(--mito)}
.extrabox{border:2px dashed color-mix(in srgb,var(--mito) 45%,transparent);border-radius:14px;padding:4px 14px;margin:14px 0;font-size:.92rem;color:var(--muted)}
.note{font-size:.92rem;color:var(--muted)}
.big2{font-family:var(--f-display);font-weight:800;font-size:clamp(1.6rem,4vw,2.3rem);line-height:1.1;letter-spacing:-.01em}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:14px 0}
.stats>div{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.stats b{display:block;font-family:var(--f-display);font-weight:800;font-size:1.6rem;line-height:1.1;color:var(--acc)}
.stats span{font-size:.92rem}
input[type=range]{width:100%;accent-color:var(--acc)}
.recall input{width:100%;font:inherit;font-size:1rem;padding:10px 14px;border-radius:10px;border:1px solid var(--line);background:var(--paper);color:var(--ink)}
.recall .chips span{font-size:.9rem;border:1px dashed var(--line);border-radius:999px;padding:4px 12px;color:var(--muted);transition:all .3s var(--ease-out)}
.recall .chips span.got{border-style:solid;border-color:var(--good);background:var(--good-soft);color:var(--ink);font-weight:700}
"""


THEME_JS = """<style id="theme-css">
.themebtn{font:inherit;font-size:.92rem;border:1px solid var(--line);background:var(--paper);color:var(--ink);border-radius:999px;padding:7px 14px;cursor:pointer;display:inline-flex;gap:7px;align-items:center;white-space:nowrap;transition:background-color .25s,color .25s,transform .2s}
.themebtn:active{transform:scale(.95)}
.themebtn:focus-visible{outline:2px solid var(--protein);outline-offset:2px}
.themebtn span{font-size:1.05rem;line-height:1}
@media (max-width:760px){.themebtn{order:2;margin-left:auto}}
</style>
<script id="theme-js">
(function(){
  var KEY="kristatlas_theme",root=document.documentElement;
  var t=null;try{t=localStorage.getItem(KEY)}catch(e){}
  if(t!=="light"&&t!=="dark")t=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";
  window.__kt=t;
  function setDoc(d){try{if(d&&d.documentElement)d.documentElement.setAttribute("data-theme",t)}catch(e){}}
  function hook(f){f.addEventListener("load",function(){setDoc(f.contentDocument)});setDoc(f.contentDocument)}
  function label(){var b=document.getElementById("themeBtn");if(!b)return;
    b.innerHTML=t==="dark"?'<span aria-hidden="true">☀</span>Ljust läge':'<span aria-hidden="true">☾</span>Mörkt läge';
    b.setAttribute("aria-label",t==="dark"?"Byt till ljust läge":"Byt till mörkt läge")}
  function apply(){window.__kt=t;setDoc(document);document.querySelectorAll("#main iframe").forEach(function(f){setDoc(f.contentDocument)});label()}
  setDoc(document);
  document.addEventListener("DOMContentLoaded",function(){
    var b=document.getElementById("themeBtn");
    b.onclick=function(){t=t==="dark"?"light":"dark";try{localStorage.setItem(KEY,t)}catch(e){}apply()};
    document.querySelectorAll("#main iframe").forEach(hook);
    new MutationObserver(function(ms){ms.forEach(function(m){m.addedNodes.forEach(function(n){if(n.tagName==="IFRAME")hook(n)})})}).observe(document.getElementById("main"),{childList:true});
    label();
  });
})();
</script>"""


def parse_chapter(cid):
    raw = read("kapitel/%s.html" % cid)
    parts = dict(re.findall(r"<!--@(\w+)-->\n?(.*?)(?=<!--@\w+-->|\Z)", raw, re.S))
    meta = json.loads(parts["meta"])
    meta["id"] = cid
    return meta, parts


def chapter_page(meta, parts):
    rail = parts["rail"].rstrip() + '\n  <a href="#ord"><span>▶</span>Ordlista</a>\n  <a href="#kort"><span>▶</span>Flashcards</a>\n  <a href="#quiz"><span>▶</span>Quiz</a>'
    acc = ":root{--acc:%s}" % meta["accent"]
    return "\n".join([
        '<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',
        "<title>%s</title>" % html.escape(meta["title"]),
        FONTS,
        BASE_CSS_FX,
        '<style id="krist-css">' + SHARED_CSS + acc + "</style>",
        '<style id="page-css">\n' + parts.get("css", "").strip() + "\n</style>",
        "</head><body>",
        '<div class="wrap">',
        '<nav class="rail" id="rail" aria-label="Kapitel">\n' + rail + "\n</nav>",
        "<main>",
        parts["main"].strip(),
        "",
        "<!-- ============ ORDLISTA ============ -->",
        '<section class="ch" id="ord">',
        '  <div class="head"><h2>Ordlista</h2><span class="mono" id="glCount"></span></div>',
        '  <input type="search" id="glSearch" class="gl-search" placeholder="%s" aria-label="Sök i ordlistan">' % html.escape(meta.get("glph", "Sök ett ord")),
        '  <dl class="gl" id="glList"></dl>',
        "</section>",
        "",
        "<!-- ============ FLASHCARDS ============ -->",
        FLASH_STYLE,
        KORT,
        "",
        "<!-- ============ QUIZ ============ -->",
        '<section class="ch quiz" id="quiz">',
        '  <div class="head"><h2>Quiz</h2><span class="mono">provfrågor</span></div>',
        '  <div class="row"><span class="score" id="qScore">0 / 0</span><button class="btn ghost" id="qReset" type="button">Gör om quizet</button></div>',
        '  <div id="qList"></div>',
        "</section>",
        "",
        "<footer>%s</footer>" % parts["footer"].strip(),
        "</main>",
        "</div>",
        "",
        "<script>",
        "(function(){",
        HELPERS,
        "",
        'const KEY="kristatlas_%s_known";' % meta["id"],
        parts["js"].strip(),
        "",
        TAIL_JS,
        "})();",
        "</script>",
        CLICK,
        "</body></html>",
    ])


def strip_text(s):
    s = re.sub(r"<(svg|script|style)\b.*?</\1>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def gloss_of(parts):
    m = re.search(r"const GLOSS=(\[.*?\n\]);", parts["js"], re.S)
    return json.loads(m.group(1))


def search_entries(cid, page):
    out = []
    for sid, body in re.findall(r'<section class="ch[^"]*" id="([^"]+)">(.*?)</section>', page, re.S):
        if sid in ("ord", "kort", "quiz"):
            continue
        h = re.search(r"<h2>(.*?)</h2>", body, re.S)
        out.append({"t": cid, "s": sid, "h": strip_text(h.group(1)) if h else sid, "x": strip_text(body)})
    return out


def begrepp_page(rows, metas):
    t = read("mall/begrepp.html")
    t = re.sub(r"<title>.*?</title>", "<title>Alla begrepp</title>", t, count=1)
    page_css = ('<style id="krist-css">' + SHARED_CSS + ":root{--acc:var(--membrane)}</style>\n"
                '<style id="page-css">\n.wrapseg{max-width:100%}\n</style>')
    t = re.sub(r'<style id="page-css">.*?</style>', lambda m: page_css, t, count=1, flags=re.S)
    t = re.sub(r'<div class="mono">Biologi · alla flikar · \d+ begrepp</div>',
               '<div class="mono">Kristendom &amp; livsfrågor · alla flikar · %d begrepp</div>' % len(rows), t)
    t = t.replace("Varje begrepp från ordlistorna i hela Biologiatlas", "Varje begrepp från alla kapitlens ordlistor")
    counts = {}
    for r in rows:
        counts[r[3]] = counts.get(r[3], 0) + 1
    cheat = '<div class="cheat">' + "".join("<div><b>%s</b>%d begrepp</div>" % (html.escape(m["title"]), counts.get(m["title"], 0)) for m in metas) + "</div>"
    t = re.sub(r'<div class="cheat">.*?</div>\n</header>', lambda m: cheat + "\n</header>", t, count=1, flags=re.S)
    btns = '<button type="button" data-v="" aria-pressed="true">Alla kapitel</button>' + "".join(
        '<button type="button" data-v="%s" aria-pressed="false">%s</button>' % (html.escape(m["title"]), html.escape(m["title"])) for m in metas)
    t = re.sub(r'(<div class="seg wrapseg" id="deckType">).*?(</div>)', lambda m: m.group(1) + btns + m.group(2), t, count=1, flags=re.S)
    t = re.sub(r"const ROWS=\[.*?\];\n", lambda m: "const ROWS=" + json.dumps(rows, ensure_ascii=False) + ";\n", t, count=1, flags=re.S)
    t = t.replace('const KEY="allabegrepp_known";', 'const KEY="kristatlas_begrepp_known";')
    t = re.sub(r"<footer>.*?</footer>", "<footer>Samlar ordlistorna från alla kapitel.</footer>", t, count=1, flags=re.S)
    return t


def js_json(o):
    return json.dumps(o, ensure_ascii=False).replace("<", "\\u003c")


def build():
    metas, pages, sidx, rows = [], {}, [], []
    for cid in ORDER:
        if not os.path.exists(os.path.join(ROOT, "kapitel", cid + ".html")):
            print("  (saknas än:", cid + ")")
            continue
        meta, parts = parse_chapter(cid)
        page = chapter_page(meta, parts)
        pages[cid] = page
        metas.append(meta)
        sidx += search_entries(cid, page)
        for term, pg, d in gloss_of(parts):
            rows.append([term, "%s · %s" % (meta["title"], ("s. " + pg) if pg[:1].isdigit() else pg), d, meta["title"]])
    bmeta = {"id": "begrepp", "title": "Alla begrepp", "sub": "Flashcards · alla kapitel",
             "desc": "Alla begrepp från alla flikars ordlistor som flashcards, quiz och sökbar ordlista. Välj kapitel eller kör allt.",
             "color": "#A0522D"}
    pages["begrepp"] = begrepp_page(rows, metas)
    for r in rows:
        sidx.append({"t": "begrepp", "s": "ord", "h": r[0], "x": r[2], "g": "1", "c": r[3]})
    META = [{k: m[k] for k in ("id", "title", "sub", "desc", "color")} for m in metas] + [bmeta]
    stitles = {m["id"]: m["title"] for m in META}
    shell = read("mall/skal.html")
    rep = {
        "@@META@@": json.dumps(META, ensure_ascii=False),
        "@@PAGES@@": js_json(pages),
        "@@SIDX@@": js_json(sidx),
        "@@STITLES@@": js_json(stitles),
    }
    shell = shell.replace("<title>Biologiatlas</title>", "<title>Kristendomen</title>")
    shell = shell.replace(">Biologiatlas</button>", ">Kristendomen</button>")
    shell = shell.replace("bioatlas_tab", "kristatlas_tab").replace("Sök i hela atlasen", "Sök på alla sidor")
    shell = shell.replace('<div class="mono">Biologi · alla dina studiesidor på ett ställe</div>',
                          '<div class="mono">Religion · kristendom, tro och vetande · alla dina studiesidor på ett ställe</div>')
    shell = shell.replace("<h1>Biologi<em>atlas</em></h1>", "<h1><em>Kristendomen</em></h1>")
    shell = re.sub(r'<p class="lead">.*?</p>',
                   '<p class="lead">Fem kapitel och alla begrepp, en sida. Välj ett kapitel nedan eller i flikarna högst upp. Varje kapitel har sin egen meny, klickbara bilder, bokens frågor med svarsförslag, flashcards och quiz.</p>',
                   shell, count=1, flags=re.S)
    # färger: samma palett som kapitlen, med kristendomens accent
    shell = re.sub(r":root\{--bg:#F2F5F7;.*?--leaf:#4C8A2C;", ":root{--bg:#EEE7DB;--paper:#F7F2E8;--ink:#2A211B;--muted:#5C4F45;--line:#DACFBE;--membrane:#A8771A;--protein:#3A5699;--good:#2C7550;--mito:#A8382C;--leaf:#6643B5;", shell, count=1, flags=re.S)
    dark = "--bg:#15110E;--paper:#1F1915;--ink:#EFE7DD;--muted:#B9AC9F;--line:#3A2F27;--membrane:#E2B54E;--protein:#8FA8EA;--good:#5CC28A;--mito:#EB7F70;--leaf:#B49AF0;color-scheme:dark"
    shell = re.sub(r"--bg:#10171D;.*?color-scheme:dark", dark, shell, flags=re.S)
    shell = shell.replace(":root{--muted:#4A5966;", ":root{--muted:#5C4F45;").replace("--muted:#AAB9C4", "--muted:#B9AC9F")
    shell = shell.replace("h1 em{font-style:normal;color:var(--protein)}", "h1 em{font-style:normal;color:var(--mito)}")
    shell = shell.replace("*{box-sizing:border-box}", "*{box-sizing:border-box}\n[hidden]:not([hidden=until-found i]){display:none!important}", 1)
    shell = shell.replace('<div class="gsearch" role="search">', '<button class="themebtn" id="themeBtn" type="button"></button>\n  <div class="gsearch" role="search">', 1)
    shell = shell.replace("f.srcdoc=PAGES[id]", "f.srcdoc=PAGES[id].replace('<html lang=\"sv\">','<html lang=\"sv\" data-theme=\"'+(window.__kt||'light')+'\">')", 1)
    shell = shell.replace("<script>\n(function(){\n  const META=", THEME_JS + "\n<script>\n(function(){\n  const META=", 1)
    for k, v in rep.items():
        shell = shell.replace(k, v)
    open(OUT, "w", encoding="utf-8").write(shell)
    print("skrev", OUT, len(shell) // 1024, "kB;", len(rows), "begrepp;", len(sidx), "sökposter")
    for cid, p in pages.items():
        print("  ", cid, len(p) // 1024, "kB")


if __name__ == "__main__":
    build()
