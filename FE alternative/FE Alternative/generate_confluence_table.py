#!/usr/bin/env python3
import re, html as htmllib, os

src = open(os.path.join(os.path.dirname(__file__), 'fe-alternatives-comparison.html'), encoding='utf-8').read()

# ── resolve string constants ──────────────────────────────────────────────────
consts = {}
for m in re.finditer(r"const\s+(\w+)\s*=\s*'([^']*)'", src):
    consts[m.group(1)] = m.group(2)

def resolve(val):
    val = val.strip().strip("'\"")
    return consts.get(val, val)

# ── parse v(s,c) / AV / PA / NA / UN calls ───────────────────────────────────
STATUS = {'av':'✅ Available','pa':'⚠️ Partially','na':'❌ Not Available','un':'❓ No data'}
COLOR  = {'av':'#e8f5e9','pa':'#fff3e0','na':'#ffebee','un':'#f5f5f5'}

def parse_v(raw):
    raw = raw.strip()
    m = re.match(r"(?:AV|v\('av')\s*\(([^)]*)\)", raw, re.I)
    if m: return ('av', m.group(1).strip("'\" "))
    m = re.match(r"(?:PA|v\('pa')\s*\(([^)]*)\)", raw, re.I)
    if m: return ('pa', m.group(1).strip("'\" "))
    m = re.match(r"(?:NA|v\('na')\s*\(([^)]*)\)", raw, re.I)
    if m: return ('na', m.group(1).strip("'\" "))
    m = re.match(r"UN\s*\(\)", raw, re.I)
    if m: return ('un', '')
    if raw.startswith('AV'): return ('av','')
    if raw.startswith('PA'): return ('pa','')
    if raw.startswith('NA'): return ('na','')
    return ('un','')

def cell_html(raw):
    s,c = parse_v(raw)
    bg = COLOR[s]
    label = STATUS[s]
    comment = f'<br><small style="color:#666">{htmllib.escape(c)}</small>' if c else ''
    return f'<td style="background:{bg};padding:6px 10px;font-size:13px;vertical-align:top">{label}{comment}</td>'

# ── extract section-1 data rows ───────────────────────────────────────────────
data_block = re.search(r'const data=\[(.*?)\];\s*\n\s*const ALL_VENDORS', src, re.DOTALL)
rows1 = []
if data_block:
    block = data_block.group(1)
    # split on object boundaries
    items = re.split(r'\},\s*\n\s*\{', block)
    for item in items:
        item = item.strip().lstrip('{').rstrip('}').rstrip(',')
        def gf(key):
            m = re.search(rf"{key}\s*:\s*'([^']*)'", item)
            if m: return m.group(1)
            m = re.search(rf"{key}\s*:\s*(\w+)", item)
            if m: return resolve(m.group(1))
            return ''
        def gv(key):
            m = re.search(rf"{key}\s*:\s*((?:AV|PA|NA|UN)\([^)]*\))", item)
            if m: return m.group(1)
            m = re.search(rf"{key}\s*:\s*(AV|PA|NA|UN)\b", item)
            if m: return m.group(1)+'()'
            return 'UN()'
        rows1.append({
            'mod': gf('mod'), 'feat': gf('feat'), 'prio': gf('prio'),
            'plat': gf('plat'),
            'wiztivi': gv('wiztivi'), 'applicaster': gv('applicaster'),
            'magycal': gv('magycal'), 'kux': gv('kux'), 'ksp': gv('ksp'),
        })

# ── extract section-2 (True Vision) data ─────────────────────────────────────
tv_block = re.search(r'const tvData = \[(.*?)\];\s*\n\s*\(function', src, re.DOTALL)
rows2 = []
if tv_block:
    block = tv_block.group(1)
    items = re.split(r'\},\s*\n\s*\{', block)
    for item in items:
        item = item.strip().lstrip('{').rstrip('}').rstrip(',')
        def gf2(key):
            m = re.search(rf"{key}\s*:\s*'([^']*)'", item)
            if m: return m.group(1)
            return ''
        def gvc(key):
            m = re.search(rf"{key}\s*:\s*\['([^']*)',\s*'([^']*)'\]", item)
            if m: return (m.group(1), m.group(2))
            return ('','')
        def tvcell(status, comment):
            s = status.strip().lower()
            if not s: return '<td style="padding:6px 10px;font-size:13px"></td>'
            if s.startswith('compliant') and 'partial' not in s and 'not' not in s:
                bg,label = '#e8f5e9','✅ Available'
            elif 'partial' in s:
                bg,label = '#fff3e0','⚠️ Partially'
            elif s.startswith('roadmap'):
                bg,label = '#e3f2fd','🔵 Roadmap'
            elif s.startswith('not') or s.startswith('not available'):
                bg,label = '#ffebee','❌ Not Available'
            elif s == 'n/a':
                bg,label = '#f5f5f5','N/A'
            elif 'backend' in s:
                bg,label = '#f3e5f5','🟣 Backend'
            else:
                bg,label = '#f5f5f5', htmllib.escape(status)
            cmt = f'<br><small style="color:#666">{htmllib.escape(comment)}</small>' if comment.strip() else ''
            return f'<td style="background:{bg};padding:6px 10px;font-size:13px;vertical-align:top">{label}{cmt}</td>'
        ws,wc = gvc('wiztivi'); aps,apc = gvc('applicaster'); ks,kc = gvc('ksp')
        rows2.append({
            'mod': gf2('mod'), 'id': gf2('id'), 'feat': gf2('feat'), 'prio': gf2('prio'),
            'wiztivi': tvcell(ws,wc), 'applicaster': tvcell(aps,apc), 'ksp': tvcell(ks,kc),
        })

# ── build HTML ────────────────────────────────────────────────────────────────
TH = 'style="background:#1a1a2e;color:white;padding:8px 12px;text-align:left;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.04em"'
TD = 'style="padding:6px 10px;font-size:13px;vertical-align:top;border-bottom:1px solid #eee"'
TDM = 'style="padding:6px 10px;font-size:13px;font-weight:700;vertical-align:top;border-bottom:1px solid #eee;border-right:3px solid #e8eaed"'

# section 1 rows
s1_html = ''
mod_counts = {}
for r in rows1:
    mod_counts[r['mod']] = mod_counts.get(r['mod'],0)+1

seen_mods = {}
for i,r in enumerate(rows1):
    mod = r['mod']
    row_html = f'<tr style="background:{"#fafbfc" if i%2==0 else "#fff"}">'
    row_html += f'<td {TD} style="padding:6px 10px;font-size:12px;color:#bbb;text-align:right">{i+1}</td>'
    if mod not in seen_mods:
        seen_mods[mod] = True
        row_html += f'<td {TDM} rowspan="{mod_counts[mod]}">{htmllib.escape(mod)}</td>'
    row_html += f'<td {TD}>{htmllib.escape(r["feat"])}</td>'
    row_html += f'<td {TD} style="padding:6px 10px;font-size:12px;color:#777">{htmllib.escape(r["plat"])}</td>'
    for v in ['wiztivi','applicaster','magycal','kux','ksp']:
        row_html += cell_html(r[v])
    prio = r['prio']
    pcls = '#ffebee' if prio=='1' else '#fff8e1' if prio=='2' else '#f5f5f5'
    row_html += f'<td style="background:{pcls};padding:6px 10px;font-size:12px;font-weight:700;text-align:center">{prio or "—"}</td>'
    row_html += '</tr>'
    s1_html += row_html

# section 2 rows
s2_html = ''
mod_counts2 = {}
for r in rows2:
    mod_counts2[r['mod']] = mod_counts2.get(r['mod'],0)+1

seen_mods2 = {}
for i,r in enumerate(rows2):
    mod = r['mod']
    row_html = f'<tr style="background:{"#fafbfc" if i%2==0 else "#fff"}">'
    row_html += f'<td {TD} style="padding:6px 10px;font-size:12px;color:#bbb;text-align:right">{i+1}</td>'
    if mod not in seen_mods2:
        seen_mods2[mod] = True
        row_html += f'<td {TDM} rowspan="{mod_counts2[mod]}">{htmllib.escape(mod)}</td>'
    row_html += f'<td {TD}><strong style="font-size:11px;color:#1a1a2e">{htmllib.escape(r["id"])}</strong><br>{htmllib.escape(r["feat"])}</td>'
    row_html += f'<td {TD}></td>'
    row_html += r['wiztivi'] + r['applicaster']
    row_html += f'<td {TD}></td><td {TD}></td>'
    row_html += r['ksp']
    prio = r['prio']
    pcls = '#ffebee' if prio=='P0' else '#fff8e1' if prio=='P1' else '#f5f5f5'
    row_html += f'<td style="background:{pcls};padding:6px 10px;font-size:12px;font-weight:700;text-align:center">{htmllib.escape(prio)}</td>'
    row_html += '</tr>'
    s2_html += row_html

out = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8">
<title>FE Alternatives — Confluence Export</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 32px; background: #f5f5f5; }}
h1 {{ color: #1a1a2e; margin-bottom: 4px; }}
h2 {{ color: #1a1a2e; margin: 40px 0 8px; }}
p {{ color: #888; font-size:13px; margin-bottom:16px; }}
.tip {{ background:#e8f0fe;border-left:4px solid #4285f4;padding:12px 16px;border-radius:4px;font-size:13px;margin-bottom:24px }}
table {{ border-collapse:collapse; width:100%; background:white; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,.1); }}
</style>
</head>
<body>
<div class="tip">
  <strong>How to paste into Confluence:</strong><br>
  1. Select a table below (click in it, then Cmd+A to select all, or just select the table rows)<br>
  2. Copy (Cmd+C)<br>
  3. In Confluence editor, click where you want the table and paste (Cmd+V)<br>
  4. Confluence will import the table with colours intact.
</div>

<h1>FE Alternatives — Vendor Comparison</h1>
<p>Wiztivi · Applicaster · Magycal · KUX · KSP &nbsp;|&nbsp; {len(rows1)} features</p>
<table>
<thead>
<tr>
  <th {TH}>#</th>
  <th {TH}>Module</th>
  <th {TH}>Feature</th>
  <th {TH}>Platforms</th>
  <th {TH}>Wiztivi</th>
  <th {TH}>Applicaster</th>
  <th {TH}>Magycal</th>
  <th {TH}>KUX</th>
  <th {TH}>KSP</th>
  <th {TH}>Priority</th>
</tr>
</thead>
<tbody>{s1_html}</tbody>
</table>

<h2>True Vision</h2>
<p>{len(rows2)} requirements &nbsp;|&nbsp; Wiztivi · Applicaster · KSP</p>
<table>
<thead>
<tr>
  <th {TH}>#</th>
  <th {TH}>Module</th>
  <th {TH}>Feature / Requirement</th>
  <th {TH}>Platforms</th>
  <th {TH}>Wiztivi</th>
  <th {TH}>Applicaster</th>
  <th {TH}>Magycal</th>
  <th {TH}>KUX</th>
  <th {TH}>KSP</th>
  <th {TH}>Priority</th>
</tr>
</thead>
<tbody>{s2_html}</tbody>
</table>
</body></html>"""

out_path = os.path.join(os.path.dirname(__file__), 'confluence_export.html')
open(out_path, 'w', encoding='utf-8').write(out)
print(f"Done! Written to: {out_path}")
print(f"Section 1: {len(rows1)} rows | Section 2: {len(rows2)} rows")
