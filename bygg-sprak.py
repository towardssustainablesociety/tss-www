#!/usr/bin/env python3
"""Bygger språksidorna på www (site/<kod>/index.html) ur sprak/<språk>.html.

Varje fil i sprak/ har ett huvud i en HTML-kommentar (nyckel: värde, en per rad)
och sedan sidans innehåll. {choice} i innehållet ersätts med knapparna English/Svenska.
Skriptet skriver också språkraden och hreflang i site/index.html (mellan markeringarna)
och site/sitemap.xml. Kör: python3 bygg-sprak.py   (Python 3.8 eller senare)

Nytt språk: lägg till en fil i sprak/ och lägg in koden i ORDNING nedan.
"""
import html, os, re, sys

ROT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROT, 'site')
WWW = 'https://www.towardssustainablesociety.org/'
EN = 'https://en.towardssustainablesociety.org/'
SV = 'https://sv.towardssustainablesociety.org/'
LICENS = 'https://creativecommons.org/licenses/by-sa/4.0/'
GITHUB = 'https://github.com/towardssustainablesociety'

# Visningsordning i språkraden (språkkod enligt BCP 47).
ORDNING = ['es', 'fr', 'de', 'pt', 'zh-Hans', 'ar', 'hi', 'ru', 'ja', 'id']
NYCKLAR = ['lang', 'dir', 'name', 'title', 'description', 'choose', 'en', 'sv',
           'ai', 'other', 'home', 'licence']

problem = []

def mapp(kod):          # adressen: /es/, /zh/ ...
    return kod.split('-')[0].lower()

def las(kod):
    with open(os.path.join(ROT, 'sprak', kod + '.html'), encoding='utf-8') as f:
        txt = f.read()
    m = re.match(r'\s*<!--(.*?)-->\s*', txt, re.S)
    if not m:
        sys.exit(f'sprak/{kod}.html saknar huvud')
    hd = {}
    for rad in m.group(1).strip().splitlines():
        k, _, v = rad.partition(':')
        hd[k.strip()] = v.strip()
    for k in NYCKLAR:
        if not hd.get(k):
            problem.append(f'{kod}: "{k}" saknas i huvudet')
    if hd.get('lang') != kod:
        problem.append(f'{kod}: lang i huvudet är "{hd.get("lang")}"')
    kropp = txt[m.end():]
    if kropp.count('{choice}') != 1:
        problem.append(f'{kod}: {{choice}} ska stå en gång')
    return hd, kropp

sprak = {k: las(k) for k in ORDNING}
for f in os.listdir(os.path.join(ROT, 'sprak')):
    if f.endswith('.html') and f[:-5] not in ORDNING:
        problem.append(f'sprak/{f} finns men står inte i ORDNING')

def hreflang():
    rader = [f'<link rel="alternate" hreflang="x-default" href="{WWW}">',
             f'<link rel="alternate" hreflang="en" href="{EN}">',
             f'<link rel="alternate" hreflang="sv" href="{SV}">']
    rader += [f'<link rel="alternate" hreflang="{k}" href="{WWW}{mapp(k)}/">' for k in ORDNING]
    return '\n'.join(rader)

def sprakrad(aktuell=None):
    delar = []
    for k in ORDNING:
        namn = html.escape(sprak[k][0]['name'])
        if k == aktuell:
            delar.append(f'<li><span aria-current="page" lang="{k}">{namn}</span></li>')
        else:
            delar.append(f'<li><a href="/{mapp(k)}/" hreflang="{k}" lang="{k}">{namn}</a></li>')
    return '<ul class="langs">\n' + '\n'.join(delar) + '\n</ul>'

MALL = '''<!doctype html>
<html lang="{lang}" dir="{dir}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
{hreflang}
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="/stil.css">
</head>
<body>
<header class="top"><a href="/">Towards Sustainable Society – TSS</a> <span>· {home}</span></header>
<main>
{kropp}
<p class="ai">{ai}</p>
</main>
<footer>
<nav aria-label="{other}">
<p class="langs-title">{other}</p>
{rad}
</nav>
<p>{licence} <a rel="license" href="{licens}">CC BY-SA 4.0</a> · <a href="{github}">GitHub</a></p>
</footer>
</body>
</html>
'''

def knappar(hd):
    return (f'<nav class="choice" aria-label="{html.escape(hd["choose"])}">\n'
            f'<a href="{EN}" hreflang="en" lang="en" dir="ltr">English<small lang="{hd["lang"]}" dir="{hd["dir"]}">{html.escape(hd["en"])}</small></a>\n'
            f'<a href="{SV}" hreflang="sv" lang="sv" dir="ltr">Svenska<small lang="{hd["lang"]}" dir="{hd["dir"]}">{html.escape(hd["sv"])}</small></a>\n'
            f'</nav>')

for k in ORDNING:
    hd, kropp = sprak[k]
    url = f'{WWW}{mapp(k)}/'
    sida = MALL.format(lang=k, dir=hd['dir'], title=html.escape(hd['title']),
                       description=html.escape(hd['description'], quote=True), url=url,
                       hreflang=hreflang(), home=html.escape(hd['home']),
                       kropp=kropp.strip().replace('{choice}', knappar(hd)),
                       ai=html.escape(hd['ai']), other=html.escape(hd['other']),
                       rad=sprakrad(k), licence=html.escape(hd['licence']),
                       licens=LICENS, github=GITHUB)
    ut = os.path.join(SITE, mapp(k))
    os.makedirs(ut, exist_ok=True)
    with open(os.path.join(ut, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(sida)

# ---- startsidan: hreflang och språkraden mellan markeringarna ----
idx = os.path.join(SITE, 'index.html')
with open(idx, encoding='utf-8') as f:
    s = f.read()
for namn, innehall in (('hreflang', hreflang()), ('sprak', sprakrad())):
    m = re.search(rf'(<!-- {namn} -->\n).*?(<!-- /{namn} -->)', s, re.S)
    if not m:
        problem.append(f'site/index.html saknar markeringen <!-- {namn} -->')
        continue
    s = s[:m.end(1)] + innehall + '\n' + s[m.start(2):]
with open(idx, 'w', encoding='utf-8') as f:
    f.write(s)

# ---- sitemap ----
with open(os.path.join(SITE, 'sitemap.xml'), 'w', encoding='utf-8') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in [WWW] + [f'{WWW}{mapp(k)}/' for k in ORDNING]:
        f.write(f'<url><loc>{u}</loc></url>\n')
    f.write('</urlset>\n')

print(f'{len(ORDNING)} språksidor byggda.')
if problem:
    print('Problem:')
    for p in problem:
        print(' -', p)
    sys.exit(1)
