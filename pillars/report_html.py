# A visual report with color-coded dots: each check and each finding carries a severity, and the dot's colour shows
# it at a glance. Written alongside the plain report so a person can scan the status without reading every line.
# Severities: show-stopper and critical are red, major orange, minor yellow, info blue, and a pass is green.
COLORS = {
    'ok': '#58d68d', 'info': '#5dade2', 'minor': '#f4d03f', 'major': '#e67e22',
    'critical': '#e74c3c', 'show-stopper': '#c0392b',
}

# What a failed check means, by how much it should stop the ship.
FAIL_SEVERITY = {
    'config': 'show-stopper', 'tests': 'show-stopper', 'mutation': 'critical', 'security': 'critical',
    'direction': 'major', 'libraries': 'major', 'style': 'minor', 'bloat': 'minor',
}
LABELS = {'config': 'Config (the law)', 'tests': 'Tests', 'mutation': 'Tests of the tests', 'style': 'Coding style',
          'direction': 'Your direction', 'bloat': 'Bloat', 'security': 'Security', 'libraries': 'Libraries'}


def _dot(sev):
    return f'<span class="dot" style="background:{COLORS[sev]}"></span>'


def _rows(report):
    soft = report.get('software')
    out = []
    cfg = report.get('config', {'pass': True, 'problems': []})
    out.append((('ok' if cfg['pass'] else 'show-stopper'), 'config', 'well-formed' if cfg['pass'] else f"{len(cfg['problems'])} problem(s)", cfg.get('problems', [])))
    if soft is None:
        return out
    for key in ('tests', 'mutation', 'style', 'direction', 'bloat', 'security', 'libraries'):
        part = soft[key]
        if key == 'libraries':
            n = len(part.get('reported', []))
            if part['pass']:
                out.append(('info' if n else 'ok', key, f'{n} reported, not blocking' if n else 'none flagged', part.get('reported', [])))
            else:
                out.append(('major', key, f"{len(part.get('blockers', []))} at or above your flag", part.get('blockers', [])))
            continue
        sev = 'ok' if part['pass'] else FAIL_SEVERITY[key]
        detail = part.get('detail') or (f"{len(part.get('violations', []))} finding(s)" if not part['pass'] else 'ok')
        out.append((sev, key, detail, part.get('violations', []) if key not in ('tests', 'mutation') else part.get('survivors', [])))
    return out


def html(report):
    cert = report['certified']
    big = 'ok' if cert else 'critical'
    verdict = 'CERTIFIED TO SHIP' if cert else 'BLOCKED'
    rows = _rows(report)
    body = []
    for sev, key, detail, findings in rows:
        items = ''.join(f'<li>{_esc(f)}</li>' for f in findings[:12])
        body.append(f'''<div class="row"><div class="head">{_dot(sev)}<b>{LABELS.get(key, key)}</b>
          <span class="sev">{sev}</span><span class="detail">{_esc(detail)}</span></div>
          {f'<ul>{items}</ul>' if items else ''}</div>''')
    testing = [r for r in rows if r[1] in ('tests', 'mutation')]
    tstrip = ''.join(f'{_dot(s)} <span>{LABELS[k]}</span> &nbsp;' for s, k, _, _ in testing)
    ai, human = report.get('ai'), report.get('human')
    people = ''
    if ai is not None:
        people = f'''<div class="row"><div class="head">{_dot('ok' if ai['pass'] else 'major')}<b>AI</b>
          <span class="detail">{_esc(ai['self_check'] if ai['pass'] else 'part not recorded')}</span></div></div>
          <div class="row"><div class="head">{_dot('ok' if human['pass'] else 'major')}<b>Human (final word)</b>
          <span class="detail">{_esc(('certified by ' + human['by'] + ' ' + human['date']) if human['pass'] else 'waiting on your final word')}</span></div></div>'''
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(report['product'])} gate report</title><style>
  body{{margin:0;background:#0b1020;color:#fff;font-family:"Segoe UI",system-ui,Arial,sans-serif;padding:24px;max-width:860px}}
  h1{{font-size:26px;margin:0 0 4px}} .sub{{color:#cfd8ff;font-size:13px;margin:0 0 18px}}
  .verdict{{display:flex;align-items:center;gap:12px;font-size:22px;font-weight:700;margin:14px 0 24px}}
  .dot{{display:inline-block;width:14px;height:14px;border-radius:50%;flex:0 0 auto}}
  .big{{width:22px;height:22px}}
  .strip{{background:#121a33;border:1px solid #2b3a6b;border-radius:10px;padding:12px 14px;margin:0 0 18px;font-size:14px}}
  .row{{background:#121a33;border:1px solid #2b3a6b;border-radius:10px;padding:12px 14px;margin:8px 0}}
  .head{{display:flex;align-items:center;gap:10px;font-size:15px}}
  .sev{{font-size:11px;text-transform:uppercase;color:#0b1020;background:#cfd8ff;border-radius:10px;padding:2px 8px}}
  .detail{{color:#cfd8ff;font-size:13px;margin-left:auto}}
  ul{{margin:8px 0 0 30px;color:#cfd8ff;font-size:13px}} li{{margin:2px 0}}
  .legend{{color:#cfd8ff;font-size:12px;margin-top:20px}} .legend .dot{{margin:0 4px 0 12px}}
</style></head><body>
  <h1>{_esc(report['product'])} {_esc(report.get('version', ''))}</h1>
  <p class="sub">fingerprint {report.get('fingerprint', '')}; this report is reproducible</p>
  <div class="verdict"><span class="dot big" style="background:{COLORS[big]}"></span>{verdict}</div>
  <div class="strip"><b>Testing status</b> &nbsp; {tstrip}</div>
  {''.join(body)}
  {people}
  <div class="legend">Severity:
    <span class="dot" style="background:{COLORS['show-stopper']}"></span>show-stopper
    <span class="dot" style="background:{COLORS['critical']}"></span>critical
    <span class="dot" style="background:{COLORS['major']}"></span>major
    <span class="dot" style="background:{COLORS['minor']}"></span>minor
    <span class="dot" style="background:{COLORS['info']}"></span>info
    <span class="dot" style="background:{COLORS['ok']}"></span>pass
  </div>
</body></html>'''


def _esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
