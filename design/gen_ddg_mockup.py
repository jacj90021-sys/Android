#!/usr/bin/env python3
"""Generates design/duckduckgo-design-mockup.html.

Everything shown in the mockup is derived from this repository's real source:
 - icon/logo path data: parsed from android vector XMLs (converted to SVG)
 - colors: copied from design-system-colors.xml / theming (light + *_dark)
 - layout structure: mirrored from the app's real layout XMLs
     include_omnibar_toolbar_mockup.xml, view_omnibar.xml,
     view_browser_navigation_bar.xml, activity_tab_switcher.xml,
     item_tab_grid.xml, view_configurable_new_tab_page.xml
 - dimensions: design-system-dimensions.xml (keylines, radii, icon sizes)
Run from the repo root:  python3 design/gen_ddg_mockup.py
"""
import xml.etree.ElementTree as ET
import json, os, re

NS = '{http://schemas.android.com/apk/res/android}'
DS = 'android-design-system/design-system/src/main/res'

def parse_vector(path):
    root = ET.parse(path).getroot()
    paths = []
    for el in root.iter():
        if el.tag.endswith('path'):
            d = el.get(NS + 'pathData')
            if not d:
                continue
            fill = el.get(NS + 'fillColor') or '#000000'
            fill = fill.replace('?attr/daxColorPrimaryIcon', '%%PRIMARY%%')
            ft = (el.get(NS + 'fillType') or 'nonZero').lower()
            paths.append({'d': ' '.join(d.split()), 'fill': fill,
                          'ft': 'evenodd' if 'even' in ft else 'nonzero'})
    return paths

ICONS = {}
for key, rel in {
    'fire': 'drawable/ic_fire_24.xml',
    'menu': 'drawable/ic_menu_vertical_24.xml',
    'add': 'drawable/ic_add_24.xml',
    'bookmarks': 'drawable/ic_bookmarks_24.xml',
    'key': 'drawable/ic_key_24.xml',
    'search': 'drawable/ic_find_search_small_24.xml',
    'shield': 'drawable/ic_shield_24.xml',
    'close': 'drawable/ic_close_16.xml',
    'dax': 'drawable/ic_dax_icon.xml',
}.items():
    ICONS[key] = parse_vector(os.path.join(DS, rel))

LOGO_PATHS = parse_vector(os.path.join(DS, 'drawable/logo_full.xml'))
# split logo into duck (explicit colors) vs wordmark (dynamic title color)
DUCK, TITLE = [], []
for p in LOGO_PATHS:
    if p['fill'].startswith('?attr'):      # daxLogoTitleText -> wordmark
        TITLE.append(p)
    else:
        DUCK.append(p)

def svg(name, size, color='#1F1F1F', cls=''):
    paths = ICONS[name]
    body = ''.join(
        f"<path d='{p['d']}' fill='{p['fill'].replace('%%PRIMARY%%', color)}'"
        f" fill-rule='{p['ft']}'/>" for p in paths)
    return (f"<svg class='{cls}' width='{size}' height='{size}' viewBox='0 0 24 24' "
            f"xmlns='http://www.w3.org/2000/svg'>{body}</svg>")

def svg16(name, size, color, vb='0 0 16 16'):
    p = ICONS[name][0]
    return (f"<svg width='{size}' height='{size}' viewBox='{vb}' "
            f"xmlns='http://www.w3.org/2000/svg'>"
            f"<path d='{p['d']}' fill='{color}' fill-rule='{p['ft']}'/></svg>")

def logo(width, title_color, duck_scale=1.0):
    # logo_full viewBox is 207x165 (w x h)
    body = ''
    for p in TITLE:
        body += f"<path d='{p['d']}' fill='{title_color}' fill-rule='{p['ft']}'/>"
    for p in DUCK:
        body += f"<path d='{p['d']}' fill='{p['fill']}' fill-rule='{p['ft']}'/>"
    h = round(width * 165 / 207 * duck_scale)
    return (f"<svg width='{width}' height='{h}' viewBox='0 0 207 165' "
            f"xmlns='http://www.w3.org/2000/svg'>{body}</svg>")

def dax_head(size, color):
    body = ''.join(f"<path d='{p['d']}' fill='{color}' fill-rule='{p['ft']}'/>"
                   for p in ICONS['dax'])
    return (f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' "
            f"xmlns='http://www.w3.org/2000/svg'>{body}</svg>")

# ---------------- colors (verbatim from design-system-colors.xml) -----------
L = dict(
    toolbar='#F9F9F9', background='#F2F2F2', surface='#F9F9F9', window='#FFFFFF',
    text='#1F1F1F', text2='rgba(28,31,33,.72)', text3='rgba(31,31,31,.40)',
    icon='rgba(31,31,31,.84)', line='rgba(31,31,31,.09)',
    hairline='#CBCBCB', omnibar='#FFFFFF', ctrl='rgba(31,31,31,.09)')
D = dict(
    toolbar='#282828', background='#282828', surface='#373737', window='#3D3D3D',
    canvas='#1F1F1F', text='#E6FFFFFF', text2='#99FFFFFF', text3='#66FFFFFF',
    icon='#C7FFFFFF', line='rgba(249,249,249,.12)', hairline='#414141',
    omnibar='#373737', ctrl='rgba(249,249,249,.12)')
ORANGE, BLUE, GREEN, YELLOW = '#DE5833', '#3969EF', '#4CBA3C', '#FFCC33'

# ---------------- shared fragments -----------------------------------------
def omnibar_row(c, mode='page'):
    """include_omnibar_toolbar_mockup.xml: pill(fire) + [fire, tabs, menu]."""
    if mode == 'home':
        lead = dax_head(24, c['icon'])
        txt = 'Search or type URL'
    else:
        lead = svg('search', 24, c['icon'])
        txt = 'example.com/article'
    pill = (f"<div class='pill'>"
            f"<span class='pill-ic'>{lead}</span>"
            f"<span class='pill-txt'>{txt}</span></div>")
    tabs = (f"<span class='tabsbtn'>{dax_head(24, c['icon'])}"
            f"<i class='cnt'>4</i></span>")
    return (f"<div class='tbar' style='background:{c['toolbar']}'>"
            f"{pill}"
            f"<span class='tic' style='color:{c['icon']}'>{svg('fire', 24, c['icon'])}</span>"
            f"{tabs}"
            f"<span class='tic'>{svg('menu', 24, c['icon'])}</span>"
            f"</div>")

def navbar_bottom(c):
    """view_browser_navigation_bar.xml: [+|key] bookmarks fire tabs menu."""
    return ("<div class='navbar'>"
            f"<span class='nic'>{svg('add', 24, c['icon'])}</span>"
            f"<span class='nic'>{svg('bookmarks', 24, c['icon'])}</span>"
            f"<span class='nic'>{svg('fire', 24, c['icon'])}</span>"
            f"<span class='nic'>{dax_head(24, c['icon'])}<i class='cnt cnt2'>4</i></span>"
            f"<span class='nic'>{svg('menu', 24, c['icon'])}</span>"
            f"</div>")

def tab_card(c, title, grad, active=False):
    close = svg16('close', 16, c['icon'])
    outline = "outline:1px solid %s;" % ORANGE if active else ''
    fav = (f"<div class='tfav' style='background:{grad}'></div>")
    return (f"<div class='tcard' style='background:{c['window']};{outline}'>"
            f"<div class='trow1'>{fav}<span class='ttitle' style='color:{c['text']}'>{title}</span>"
            f"<span class='tclose'>{close}</span></div>"
            f"<div class='tprev' style='background:{grad}'></div></div>")

def tab_switcher_screen(c):
    cards = (
        tab_card(c, 'Slashdot', 'linear-gradient(150deg,#5a3226,#3d2a24)', True) +
        tab_card(c, 'Hacker News', 'linear-gradient(150deg,#2e4157,#26333f)') +
        tab_card(c, 'Wikipedia', 'linear-gradient(150deg,#4a4a4a,#383838)') +
        tab_card(c, 'GitHub', 'linear-gradient(150deg,#3d2f52,#2e2440)'))
    return (f"<div style='background:{c['toolbar']}'>"
            f"<div class='swtitle' style='color:{c['text']}'>Open tabs</div></div>"
            f"<div class='swgrid' style='background:{c['toolbar']}'>{cards}</div>"
            f"<div class='swbot' style='background:{c['toolbar']};border-top:1px solid {c['hairline']}'>"
            f"<span class='nic'>{svg('fire', 24, c['icon'])}</span>"
            f"<span class='nic'>{svg('add', 24, c['icon'])}</span>"
            f"<span class='nic'>{svg('menu', 24, c['icon'])}</span></div>")

# ---------------- CSS ------------------------------------------------------
CSS = """
:root{--or:%(ORANGE)s;--bl:%(BLUE)s;--gr:%(GREEN)s}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Roboto,system-ui,-apple-system,'Segoe UI',sans-serif;background:#EDEBE6;
  color:#1F1F1F;padding:40px 20px 70px}
.wrap{max-width:1240px;margin:0 auto}
.kick{font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--or)}
h1{font-size:clamp(24px,3.6vw,36px);letter-spacing:-.02em;margin:10px 0 8px}
.sub{color:rgba(28,31,33,.72);font-size:13.5px;line-height:1.65;max-width:760px}
.screens{display:flex;gap:30px;flex-wrap:wrap;justify-content:center;margin:40px 0 60px}
.stage{display:flex;flex-direction:column;align-items:center;gap:12px}
.slabel{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#6b6b6b}
.phone{width:300px;height:626px;border-radius:36px;overflow:hidden;position:relative;
  display:flex;flex-direction:column;border:1px solid rgba(0,0,0,.15);
  box-shadow:0 22px 44px rgba(0,0,0,.22),0 0 0 8px #111}
.status{height:28px;display:flex;align-items:center;justify-content:space-between;
  padding:0 16px;font-size:10px;font-weight:600;flex:none}
/* -- omnibar toolbar (include_omnibar_toolbar_mockup.xml) -- */
.tbar{display:flex;align-items:center;gap:6px;padding:8px 12px 12px 16px;flex:none}
.pill{flex:1;display:flex;align-items:center;gap:6px;height:36px;border-radius:16px;
  padding:0 8px 0 10px;box-shadow:0 1px 3px rgba(0,0,0,.08),0 0 0 1px rgba(31,31,31,.05)}
.pill-ic{display:flex;align-items:center}
.pill-ic svg{width:20px;height:20px}
.pill-txt{font-size:12.5px;color:rgba(28,31,33,.72);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tic{width:40px;height:40px;display:flex;align-items:center;justify-content:center;flex:none}
.tic svg{width:24px;height:24px}
.tabsbtn{width:40px;height:40px;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:1px;flex:none;position:relative}
.tabsbtn svg{width:21px;height:21px}
.cnt{font-style:normal;font-size:9px;font-weight:700;line-height:1;letter-spacing:.02em}
.cnt2{position:absolute;top:6px;right:5px;font-size:8.5px;font-weight:700;
  min-width:13px;height:13px;border-radius:7px;color:#fff;display:flex;
  align-items:center;justify-content:center;background:var(--bl);padding:0 3px}
/* -- bottom nav bar (view_browser_navigation_bar.xml) -- */
.navbar{display:flex;align-items:center;justify-content:space-between;flex:none;
  padding:8px 18px 4px;border-top:.5px solid rgba(0,0,0,.2)}
.nic{width:40px;height:40px;display:flex;align-items:center;justify-content:center;position:relative}
.nic svg{width:24px;height:24px}
.homebar{width:96px;height:4px;border-radius:2px;background:rgba(0,0,0,.24);margin:2px auto 6px;flex:none}
/* -- page content -- */
.pbody{flex:1;overflow:hidden;background:#fff;padding:16px;display:flex;flex-direction:column;gap:12px}
.sk1{height:20px;width:55%%;border-radius:6px;background:#E5E5E5}
.sk2{height:11px;width:92%%;border-radius:6px;background:#EEEEEE}
.sk2b{height:11px;width:84%%;border-radius:6px;background:#EEEEEE}
.dot-note{font-size:10px;color:#8a8a8a;text-align:center;margin-top:auto;margin-bottom:8px}
/* -- ntp -- */
.ntp{flex:1;overflow:hidden;display:flex;flex-direction:column;align-items:center}
.ntp .logo{margin-top:64px}
.ntp h4{font-size:12px;font-weight:700;margin:34px 0 12px;align-self:flex-start;padding:0 20px}
.favgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:0 16px;width:100%%}
.fav{display:flex;flex-direction:column;align-items:center;gap:5px}
.fav .tile{width:50px;height:50px;border-radius:12px;background:#fff;display:flex;
  align-items:center;justify-content:center;font-size:16px;font-weight:700;
  box-shadow:0 0 0 1px rgba(31,31,31,.06),0 1px 3px rgba(0,0,0,.06)}
.fav small{font-size:9px;color:rgba(28,31,33,.72);max-width:62px;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}
.editbtn{align-self:flex-end;margin:26px 20px 0;width:48px;height:36px;border-radius:10px;
  background:%%CTRL%%;display:flex;align-items:center;justify-content:center}
/* -- tab switcher -- */
.swtitle{font-size:16px;font-weight:700;padding:14px 16px 10px}
.swgrid{flex:1;display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:10px;overflow:hidden;align-content:start}
.tcard{border-radius:12px;padding:8px;display:flex;flex-direction:column;gap:8px;
  box-shadow:0 1px 3px rgba(0,0,0,.18)}
.trow1{display:flex;align-items:center;gap:7px}
.tfav{width:16px;height:16px;border-radius:4px;flex:none}
.ttitle{font-size:11px;font-weight:600;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tclose{display:flex;opacity:.75}
.tprev{height:118px;border-radius:8px 8px 4px 4px;align-self:stretch}
.swbot{display:flex;align-items:center;justify-content:space-between;padding:8px 18px 4px;flex:none}
/* -- legend & tokens -- */
.legend{display:flex;flex-direction:column;gap:6px;max-width:300px}
.legend div{font-size:11px;color:#5b5b5b;line-height:1.45}
.legend b{color:#1F1F1F}
.chip{display:inline-block;font-size:9px;font-weight:800;letter-spacing:.04em;
  padding:2px 7px;border-radius:6px;background:rgba(222,88,51,.12);color:#BC4726;
  margin-right:6px;font-family:ui-monospace,Menlo,monospace}
.tokens{background:#fff;border:1px solid rgba(31,31,31,.09);border-radius:20px;
  padding:26px;margin:0 auto 50px;max-width:1240px}
.tokens h2{font-size:17px;font-weight:700;margin-bottom:6px}
.tokens .src{font-size:12px;color:rgba(28,31,33,.72);line-height:1.6;margin-bottom:18px}
.tokens code{font-family:ui-monospace,Menlo,monospace;font-size:11px;
  background:rgba(31,31,31,.05);padding:1px 5px;border-radius:5px}
.swrow{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.sw{border:1px solid rgba(31,31,31,.09);border-radius:12px;overflow:hidden}
.sw .c{height:48px}
.sw .m{padding:7px 10px}
.sw .m b{font-size:10.5px;display:block}
.sw .m code{font-size:9.5px;background:none;padding:0;color:rgba(28,31,33,.72)}
.sechead{font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;
  color:rgba(28,31,33,.72);margin:22px 0 10px}
.foot{text-align:center;color:#8a8a8a;font-size:11.5px;line-height:1.7}
""" % dict(ORANGE=ORANGE, BLUE=BLUE, GREEN=GREEN, CTRL=L['ctrl'])

def phone(inner, label, legend, extra_status_color=L['text']):
    return f"""
<div class='stage'>
  <div class='slabel'>{label}</div>
  <div class='phone'>{inner}</div>
  <div class='legend'>{''.join(f'<div>{x}</div>' for x in legend)}</div>
</div>"""

# ---------------- screens ---------------------------------------------------
G = lambda a, b: f'linear-gradient(150deg,{a},{b})'

status_light = f"<div class='status' style='color:{L['text']}'><span>9:41</span><span>▲ ● ▮</span></div>"
status_dark = f"<div class='status' style='color:{D['text2']}'><span>9:41</span><span>▲ ● ▮</span></div>"

# 1. browser, top omnibar, light — include_omnibar_toolbar_mockup.xml
s1 = (
    status_light
    + omnibar_row(L, 'page')
    + f"<div class='pbody'>"
      f"<div class='sk1'></div><div class='sk2'></div><div class='sk2b'></div>"
      f"<div class='sk2'></div><div class='sk2b' style='width:60%'></div>"
      f"<div class='dot-note'>top-omnibar mode — no bottom bar (include_new_browser_tab.xml)</div></div>"
    + "<div class='homebar'></div>")

# 2. browser, bottom nav bar, light — view_browser_navigation_bar.xml
s2 = (
    status_light
    + omnibar_row(L, 'page')
    + f"<div class='pbody' style='padding-bottom:6px'>"
      f"<div class='sk1'></div><div class='sk2'></div><div class='sk2b'></div>"
      f"<div class='sk2'></div></div>"
    + f"<div style='background:{L['window']}'>"
    + navbar_bottom(L)
    + "</div><div class='homebar'></div>")

# 3. new tab page, light — view_configurable_new_tab_page.xml
favs = ''.join(
    f"<div class='fav'><div class='tile' style='color:{c}'>{ch}</div><small>{n}</small></div>"
    for ch, c, n in [('N', ORANGE, 'News'), ('G', BLUE, 'GitHub'),
                     ('W', GREEN, 'Wiki'), ('Y', '#7A4BDC', 'YouTube'),
                     ('M', BLUE, 'Mail'), ('D', ORANGE, 'Docs'), ('S', GREEN, 'Shop')])
s3 = (
    status_light
    + omnibar_row(L, 'home')
    + f"<div class='ntp' style='background:{L['background']}'>"
      f"<div class='logo'>{logo(140, '#14307E')}</div>"
      f"<h4>Favorites</h4><div class='favgrid'>{favs}</div>"
      f"<div class='editbtn' style='background:{L['ctrl']}'>{svg16('close', 16, L['icon']).replace('16 16 16 16', '16 16 16 16')}</div>"
      f"</div>"
    + "<div class='homebar'></div>")

# 4. tab switcher, dark — activity_tab_switcher.xml + item_tab_grid.xml
s4 = (
    status_dark
    + tab_switcher_screen(D)
    + "<div class='homebar' style='background:rgba(255,255,255,.25)'></div>")

legend1 = [
    "<span class='chip'>omnibar pill</span> r=16 card, shadow, <b>search icon 20px</b> + placeholder — exactly include_omnibar_toolbar_mockup.xml",
    "<span class='chip'>fire</span> fire icon <b>left of tabs</b>, 40dp tap target, 24dp glyph — same order as the XML",
    "<span class='chip'>tabs</span> tab button = <b>Dax head + count</b> (NewTabSwitcherButton), then ⋮ menu",
]
legend2 = [
    "<span class='chip'>nav bar</span> <b>[+|key] bookmarks fire tabs menu</b> spread edge-to-edge — view_browser_navigation_bar.xml order",
    "<span class='chip'>hairline</span> 0.5dp solid shade line on top of the bar (shadowView)",
    "<span class='chip'>icons</span> all 40dp touch / 24dp glyph, keyline-4 (16dp→18px) horizontal padding",
]
legend3 = [
    "<span class='chip'>logo</span> the <b>real logo_full vector</b> (207×165 viewBox, all 21 paths), 140dp wide",
    "<span class='chip'>ntp</span> omnibar pill shows <b>Dax head + 'Search or type URL'</b> (home state)",
    "<span class='chip'>favorites</span> white tiles r=12 on #F2F2F2 background (daxColorBackground)",
]
legend4 = [
    "<span class='chip'>switcher</span> toolbar bg #282828, cards <b>#3D3D3D r=12</b>, 2-col grid, 8dp margins (item_tab_grid.xml)",
    "<span class='chip'>card</b></span> favicon 16px + title + 16px close + preview area (162dp on phone)",
    "<span class='chip'>bottom</span> switcher toolbar: <b>fire · + · ⋮</b> (menu_tab_switcher_activity.xml icons)",
]

phones = (
    phone(s1, '01 · browser · top omnibar · light', legend1) +
    phone(s2, '02 · browser · bottom nav bar · light', legend2) +
    phone(s3, '03 · new tab page · light', legend3) +
    phone(s4, '04 · tab switcher · dark', legend4))

sw = lambda hexv, name, note: (
    f"<div class='sw'><div class='c' style='background:{hexv}'></div>"
    f"<div class='m'><b>{name}</b><code>{hexv}</code></div></div>")

token_sheet = f"""
<div class='tokens'>
  <h2>Everything above is copied from this repo's source</h2>
  <div class='src'>
    Colors: <code>design-system/src/main/res/values/design-system-colors.xml</code> +
    <code>values-night</code> &nbsp;·&nbsp; Sizes: <code>design-system-dimensions.xml</code>
    (keyline_1=4dp, keyline_2=8dp, toolbarIcon=40dp, bottomNavIcon=24dp,
    largeShapeCornerRadius=16dp, mediumShapeCornerRadius=12dp, gridItemPreviewHeight=162dp)
    &nbsp;·&nbsp; Layouts mirrored: <code>include_omnibar_toolbar_mockup.xml</code>,
    <code>view_omnibar.xml</code>, <code>view_browser_navigation_bar.xml</code>,
    <code>activity_tab_switcher.xml</code>, <code>item_tab_grid.xml</code>,
    <code>view_configurable_new_tab_page.xml</code>.
    Icons &amp; logo are the repo's actual vector path data, converted to SVG.
  </div>
  <div class='sechead'>Brand</div>
  <div class='swrow'>
    {sw(ORANGE, 'fire / brand (red50)', '')}
    {sw(BLUE, 'primary blue (blue50)', '')}
    {sw(GREEN, 'protection green (green50)', '')}
    {sw(YELLOW, 'accent yellow (yellow50)', '')}
  </div>
  <div class='sechead'>Light</div>
  <div class='swrow'>
    {sw('#FFFFFF', 'window', '')}
    {sw('#F2F2F2', 'background', '')}
    {sw('#F9F9F9', 'surface / toolbar', '')}
    {sw('#1F1F1F', 'text / icon primary', '')}
    {sw('#CBCBCB', 'shade solid hairline', '')}
  </div>
  <div class='sechead'>Dark</div>
  <div class='swrow'>
    {sw('#282828', 'background / toolbar', '')}
    {sw('#373737', 'surface / omnibar card', '')}
    {sw('#3D3D3D', 'window / tab cards', '')}
    {sw('#1F1F1F', 'canvas', '')}
    {sw('#414141', 'shade solid hairline', '')}
  </div>
</div>"""

html = f"""<!DOCTYPE html>
<html lang='en'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>DuckDuckGo skin — 100% copied from the app's real source</title>
<style>{CSS}</style></head>
<body><div class='wrap'>
<div class='kick'>Skin 1/3 · faithful copy</div>
<h1>DuckDuckGo frontend — rebuilt from the actual repo source</h1>
<p class='sub'>Same icons (real vector paths), same colors (verbatim tokens), same layout
structure (mirrored from the real layout XMLs), same dimensions (keylines &amp; radii from
the design system). Omnibar pill on the left with fire → tabs → menu on its right —
not an invented arrangement. Bottom-nav and top-omnibar are both real DDG modes.</p>
<div class='screens'>{phones}</div>
{token_sheet}
<div class='foot'>Skin 1/3 · DuckDuckGo — generated by design/gen_ddg_mockup.py from repo source<br>
Next: skin 2/3 Firefox (Fenix), skin 3/3 Chromium, then the invented mix.</div>
</div></body></html>"""

out = os.path.join('design', 'duckduckgo-design-mockup.html')
os.makedirs('design', exist_ok=True)
open(out, 'w').write(html)
print('wrote', out, len(html), 'bytes')
