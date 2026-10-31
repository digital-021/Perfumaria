#!/usr/bin/env python3
"""Monta o site do GitHub Pages (repo digital-021/perfumaria) a partir dos catálogos do projeto.
Uso: python3 montar.py <repo>/docs  (GitHub Pages publica a pasta /docs)
Gera <repo>/hmc/ e <repo>/c7/ (index.html + img/ + og.jpg) e <repo>/index.html.
Rodar de novo sempre que o HMC ou a C7 mudar, e depois fazer commit/push."""
import json, os, re, shutil, subprocess, sys, tempfile

P = "/mnt/project-files/"
BASE = "https://digital-021.github.io/Perfumaria/"
LOJAS = [
    dict(id="hmc", nome="HMC Perfumaria", local="Bonsucesso, RJ", dir=P + "hmc-catalogo", html=P + "hmc-catalogo/hmc-perfumaria.html"),
    dict(id="c7", nome="C7 Perfumaria", local="Bangu, RJ", dir=P + "loja2-catalogo", html=None),
]
DESCR = "Perfumes árabes 100% originais. Atacado e varejo, loja em {local}. Entrega para todo o Brasil, Rio em até 12h. Peça pelo WhatsApp."


def head(l):
    url = BASE + l["id"] + "/"
    d = DESCR.format(local=l["local"])
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{d}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{l['nome']}">
<meta property="og:title" content="{l['nome']} · Catálogo">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{url}og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="img/logo.png">
<link rel="apple-touch-icon" href="img/logo.png">
"""


def montar(l, out):
    if l["html"]:
        h = open(l["html"], encoding="utf-8").read()
    else:
        tmp = tempfile.mktemp(suffix=".html")
        subprocess.run(["sh", l["dir"] + "/gerar-c7.sh", tmp], check=True)
        h = open(tmp, encoding="utf-8").read()
        # Fora do claude.ai não existe /_blob/: as fotos da loja vêm da pasta img/.
        h = re.sub(r"const C7_ASSETS = \{.*?\};", "const C7_ASSETS = {};", h, count=1, flags=re.S)
    h = h.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    h = re.sub(r'LINK_SITE = "[^"]*"', f'LINK_SITE = "{BASE}{l["id"]}/"', h)
    d = os.path.join(out, l["id"])
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(head(l) + h.replace("</title>", "</title>\n</head>\n<body>", 1).replace("<body>", "", 0) + "\n</body>\n</html>\n")
    shutil.copytree(l["dir"] + "/img", os.path.join(d, "img"))
    shutil.copy(P + f"github-pages/og/{l['id']}.jpg", os.path.join(d, "og.jpg"))


out = sys.argv[1]
for l in LOJAS:
    montar(l, out)
open(os.path.join(out, ".nojekyll"), "w").close()
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write("""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Perfumaria</title>
<style>body{margin:0;min-height:100vh;display:grid;place-content:center;gap:16px;background:#141414;font-family:system-ui,sans-serif}
a{display:block;padding:18px 32px;border:1px solid #D7A85E;border-radius:12px;color:#D7A85E;text-decoration:none;font-size:20px;text-align:center}</style>
</head><body><a href="hmc/">HMC Perfumaria · Bonsucesso</a><a href="c7/">C7 Perfumaria · Bangu</a></body></html>
""")
print("ok:", out)
