"""Write index.csv, index.md and index.html for the built schematics.

Usage:  python gen/make_index.py [--out DIR]   (DIR defaults to the repository root)
"""
import argparse, csv, html, importlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reg import REG
for m in ['c_basic', 'c_gen', 'c_proc1', 'c_proc2', 'c_proc3', 'c_proc4', 'c_fund']:
    importlib.import_module(m)
ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument('--out', default=os.path.dirname(HERE))
OUT = os.path.abspath(ap.parse_args().out)
nums = sorted(REG)
SECTIONS = ['Basic Circuits', 'Signal Generation', 'Signal Processing', 'Fundamentals']
CREDIT = ("Circuit topologies for circuits 1–88 follow National Semiconductor AN-31, 'Op Amp Circuit Collection'. "
          "The drawings, titles and notes are new work. "
          "Circuits 89–103 (Fundamentals) are original drawings of standard textbook topologies, not taken from AN-31.")
SEE_ALSO = CREDIT + ' No endorsement is implied.'
# ---- index.csv / index.md / index.html
with open(f'{OUT}/index.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['number', 'title', 'section', 'svg', 'png'])
    for n in nums:
        w.writerow([f'{n:02d}', REG[n]['title'], REG[n]['section'], f'svg/{n:02d}.svg', f'png/{n:02d}.png'])
md = ['# Op Amp Circuits — Index', '',
      f'{len(nums)} op-amp circuit schematics drawn with generic parts. Each number has `svg/NN.svg` and `png/NN.png` (300 DPI).', '',
      SEE_ALSO, '', 'License: CC BY 4.0, © 2026 Stephen B. Johnson; see [LICENSE](LICENSE).', '']
for sec in SECTIONS:
    md += [f'## {sec}', '', '| # | Circuit |', '|---|---|']
    md += [f'| {n:02d} | [{REG[n]["title"]}](png/{n:02d}.png) |' for n in nums if REG[n]['section'] == sec]
    md.append('')
open(f'{OUT}/index.md', 'w', encoding='utf-8').write('\n'.join(md))

CSS = ''':root{--bg:#f6f5f2;--card:#fff;--ink:#1b2733;--mute:#66707a;--line:#dcdad4;--acc:#2f5d8a}
@media (prefers-color-scheme:dark){:root{--bg:#15191d;--card:#1f252b;--ink:#e6e9ec;--mute:#98a2ab;--line:#2e363d;--acc:#8db4dc}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
header,main,footer{max-width:1240px;margin:0 auto;padding:16px}h1{margin:16px 0 4px;font-size:26px;font-weight:650}
header p,footer p{margin:0 0 12px;color:var(--mute)}input{width:100%;max-width:360px;padding:9px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);font:inherit}
h2{font-size:17px;font-weight:600;margin:28px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}
.card{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;color:inherit;text-decoration:none}
.card:hover{border-color:var(--acc)}figure{margin:0;background:#fff;height:210px;display:flex;align-items:center;justify-content:center;padding:8px}
img{max-width:100%;max-height:100%}.cap{padding:8px 10px;font-size:13.5px}.cap b{color:var(--acc);margin-right:6px}
.tag{display:inline-block;font-size:11px;padding:1px 6px;margin:4px 4px 0 0;border-radius:6px;border:1px solid var(--line);color:var(--mute)}'''
def page(title, intro, base, tags=None, extra=''):
    h = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{CSS}</style></head><body>',
         f'<header><h1>{html.escape(title)}</h1>{intro}<input id="q" placeholder="Filter by number or title" oninput="f(this.value)"></header><main>']
    for sec in SECTIONS:
        h.append(f'<h2>{sec}</h2><div class="grid">')
        for n in nums:
            if REG[n]['section'] != sec: continue
            t = html.escape(REG[n]['title']); tg = ''.join(f'<span class="tag">{x}</span>' for x in (tags(n) if tags else []))
            h.append(f'<a class="card" href="{base}svg/{n:02d}.svg" data-k="{n:02d} {t.lower()}"><figure><img loading="lazy" src="{base}png/{n:02d}.png" alt="{t}"></figure><div class="cap"><b>{n:02d}</b>{t}<br>{tg}</div></a>')
        h.append('</div>')
    h.append(f'</main><footer>{extra}</footer><script>function f(v){{v=v.toLowerCase();document.querySelectorAll(".card").forEach(c=>c.style.display=c.dataset.k.includes(v)?"":"none")}}</script></body></html>')
    return ''.join(h)
open(f'{OUT}/index.html', 'w', encoding='utf-8').write(page('Op Amp Circuits',
    f'<p>{len(nums)} op-amp circuit schematics drawn with generic parts. Click a card for the SVG.</p>', '',
    extra=f'<p>{html.escape(SEE_ALSO)}</p><p>License: CC BY 4.0, © 2026 Stephen B. Johnson. See LICENSE.</p>'))

print('wrote index.csv, index.md, index.html')
