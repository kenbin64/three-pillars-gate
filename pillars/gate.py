# The ship gate: the point where the three pillars meet. It runs every deterministic check (the Software pillar),
# confirms the AI did its part and the Human gave the final word, and issues a certificate only when ALL of it is
# green. Nothing ships on a promise. Run: python -m pillars.gate <manifest.json>
#
# The gate itself is Software: deterministic and repeatable. Run it again on the same code and it says the same thing.
import hashlib
import json
import os
import sys

from pillars import engines, config, report as report_mod, report_html


def _sha(paths):
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(open(p, 'rb').read())
    return h.hexdigest()[:16]


def _software_pillar(man, base):
    # The deterministic heavy lifting, filled by the one engine layer for whatever language the product is in.
    sources = [os.path.join(base, s) for s in man['source']]
    test_files = [os.path.join(base, t) for t in man.get('test_files', [])]
    return engines.software(man, base, sources, test_files)


def _ai_pillar(man):
    ai = man.get('ai', {})
    ok = bool(ai.get('authored')) and bool(ai.get('self_check'))
    return {'pass': ok, 'self_check': ai.get('self_check', '(missing)')}


def _human_pillar(man):
    h = man.get('human', {})
    sign = h.get('signoff', {})
    ok = bool(sign.get('approved')) and bool(sign.get('by')) and bool(sign.get('date')) and bool(h.get('criteria'))
    return {'pass': ok, 'by': sign.get('by', '(unsigned)'), 'date': sign.get('date', '')}


def certify(manifest_path):
    man = json.load(open(manifest_path, encoding='utf-8'))
    base = os.path.join(os.path.dirname(os.path.abspath(manifest_path)), man.get('dir', '.'))

    # First thing checked: the config itself (the law). A broken law blocks before any code is touched. The
    # fingerprint covers the config, so changing the law invalidates the old certificate and re-opens the loop.
    config_problems = config.validate(man)
    cfg = {'pass': not config_problems, 'problems': config_problems}
    if config_problems:
        return {'product': man.get('name', '(unnamed)'), 'version': man.get('version', ''),
                'fingerprint': _sha([os.path.abspath(manifest_path)]),
                'config': cfg, 'software': None, 'ai': None, 'human': None, 'certified': False}

    sources = [os.path.join(base, s) for s in man['source']]
    soft = _software_pillar(man, base)
    ai = _ai_pillar(man)
    human = _human_pillar(man)
    shipped = cfg['pass'] and soft['pass'] and ai['pass'] and human['pass']

    report = {
        'product': man['name'], 'version': man.get('version', ''),
        'fingerprint': _sha(sources + [os.path.abspath(manifest_path)]),
        'config': cfg, 'software': soft, 'ai': ai, 'human': human,
        'certified': shipped,
    }
    return report


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    want_detail = '--detail' in sys.argv
    rep = certify(args[0])
    here = os.path.dirname(os.path.abspath(args[0]))

    # The human reads this: concise but complete, no team needed to decipher it. --detail adds the full breakdown.
    human_text = report_mod.detail(rep) if want_detail else report_mod.summary(rep)
    print('\n' + human_text + '\n')
    open(os.path.join(here, 'report.md'), 'w', encoding='utf-8').write(report_mod.detail(rep))

    # The AI reads this: the machine-readable version it corrects from. Always written, pass or block.
    json.dump(rep, open(os.path.join(here, 'report.json'), 'w', encoding='utf-8'), indent=2)
    # The visual report: color-coded dots by severity, for a glance. Open report.html in a browser.
    open(os.path.join(here, 'report.html'), 'w', encoding='utf-8').write(report_html.html(rep))

    if rep['certified']:
        # The final report: issued only when every pillar is green and the human has given the final word.
        json.dump(rep, open(os.path.join(here, 'certificate.json'), 'w', encoding='utf-8'), indent=2)
    sys.exit(0 if rep['certified'] else 1)
