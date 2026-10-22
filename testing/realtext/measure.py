#!/usr/bin/env python3
"""Run `dorothea analyze --json` over every passage of the real-text development set and report coverage.

Buckets per word token (one entry of the analyser's `words` list):
  level      found, with a card that has a gloss and a CEFR level
  no-level   found, with a gloss but without a CEFR level
  part-gloss compound with no entry of its own (how=compound, no key): only the parts are glossed
  base-gloss no entry of its own, but a gloss taken from a base word (how=derived, separable, ...)
  empty      recognised (lemma, from the morphology or the dictionary) but the card has no gloss
  not-found  no lemma and no gloss
  other      anything else (should stay 0)

The not-found words and the no-level, base-gloss and empty-card lemmas are written with counts to an output folder outside git.

Names: `names.tsv` lists, per passage, the word tokens that are names (kind person, place, org,
other) and the ordinary words inside names that may count either way (kind part). A token is
marked as a name when the analyser sets `name`. Reported per language: recall (gold name tokens
marked), false alarms (marked tokens that are neither names nor parts) and precision; the misses
and false alarms are written to `names-missed-<lang>.tsv` and `names-false-<lang>.tsv`.
Python 3 standard library only.
"""
import argparse
import collections
import csv
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CLI = '/home/user/dorothea-wt-sense/target/release/dorothea'
DEFAULT_PACKS = '/home/user/dorothea-build/packs-v9'
DEFAULT_OUT = '/home/user/dorothea-build/realtext-out'
BUCKETS = ['level', 'no-level', 'part-gloss', 'base-gloss', 'empty', 'not-found', 'other']


FR_DIRECTION = 'fr-de'


def pack_args(packs, lang):
    # Name list packs (`names-*.pack`; French ones end in `-fr.pack`) of the pack directory, if any.
    names = []
    for f in sorted(os.listdir(packs)):
        if f.startswith('names-') and f.endswith('.pack') and f.endswith('-fr.pack') == (lang == 'fr'):
            names += ['--names-pack', f'{packs}/{f}']
    if lang == 'fr':
        d = FR_DIRECTION
        return ['--morph-pack', f'{packs}/fr-morph.pack', '--dict-pack', f'{packs}/{d}/core.pack',
                '--chunks', f'{packs}/{d}', '--freq-pack', f'{packs}/freq-fr.pack'] + names
    if lang == 'de':
        return ['--morph-pack', f'{packs}/de-morph.pack', '--dict-pack', f'{packs}/de-en/core.pack',
                '--chunks', f'{packs}/de-en', '--freq-pack', f'{packs}/freq-de.pack'] + names
    return ['--morph-pack', f'{packs}/en-morph.pack', '--dict-pack', f'{packs}/en-de/core.pack',
            '--chunks', f'{packs}/en-de', '--freq-pack', f'{packs}/freq-en.pack'] + names


def bucket(w):
    if w.get('key') and w.get('gloss'):
        return 'level' if w.get('cefr') else 'no-level'
    if w.get('how') == 'compound' and not w.get('key'):
        return 'part-gloss'
    if not w.get('key') and w.get('gloss'):
        return 'base-gloss'
    if (w.get('key') or w.get('lemma')) and not w.get('gloss'):
        return 'empty'
    if not w.get('lemma') and not w.get('gloss'):
        return 'not-found'
    return 'other'


NAME_KINDS = ('person', 'place', 'org', 'other')


def load_names():
    """(passage id, token) -> kind from names.tsv."""
    gold = {}
    with open(os.path.join(HERE, 'names.tsv'), encoding='utf-8', newline='') as fh:
        for row in csv.DictReader(fh, delimiter='\t'):
            for tok in row['tokens'].split():
                gold[(row['id'], tok)] = row['kind']
    return gold


def name_kind(gold, pid, surface):
    """Gold kind of a token: as written, else without a possessive ending or a final full stop."""
    for s in (surface, re.sub(r"(['’]s|['’])$", '', surface), surface.rstrip('.')):
        if (pid, s) in gold:
            return gold[(pid, s)]
    return None


def analyze(cli, packs, lang, text):
    cmd = [cli, 'analyze', '--json'] + pack_args(packs, lang) + ['-']
    res = subprocess.run(cmd, input=text.encode('utf-8'), capture_output=True, check=False)
    if res.returncode != 0:
        sys.exit(f'dorothea failed ({res.returncode}): {res.stderr.decode("utf-8", "replace")[:500]}')
    return json.loads(res.stdout)


def pct(n, d):
    return f'{100.0 * n / d:.1f}' if d else '-'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--cli', default=DEFAULT_CLI)
    ap.add_argument('--packs', default=DEFAULT_PACKS)
    ap.add_argument('--out', default=DEFAULT_OUT, help='output folder (keep it outside git)')
    ap.add_argument('--lang', choices=['de', 'en', 'fr'], help='only this language')
    ap.add_argument('--fr-direction', default='fr-de', choices=['fr-de', 'fr-fr', 'fr-en'],
                    help='direction for the French passages')
    ap.add_argument('--id', action='append', help='only these passage ids (repeatable)')
    ap.add_argument('--markdown', action='store_true', help='print the summary as a Markdown table')
    args = ap.parse_args()
    global FR_DIRECTION
    FR_DIRECTION = args.fr_direction

    with open(os.path.join(HERE, 'passages.tsv'), encoding='utf-8', newline='') as fh:
        rows = list(csv.DictReader(fh, delimiter='\t'))
    if args.lang:
        rows = [r for r in rows if r['lang'] == args.lang]
    if args.id:
        rows = [r for r in rows if r['id'] in set(args.id)]
    os.makedirs(args.out, exist_ok=True)

    totals = collections.defaultdict(collections.Counter)   # group -> bucket counts
    notfound = collections.defaultdict(collections.Counter)  # lang -> surface
    nolevel = collections.defaultdict(collections.Counter)   # lang -> (lemma, pos)
    nolevel_ex = {}
    empty = collections.defaultdict(collections.Counter)    # lang -> (lemma, pos)
    basegloss = collections.defaultdict(collections.Counter)  # lang -> (lemma, how: gloss)
    propn = collections.Counter()
    gold = load_names()
    names = collections.defaultdict(collections.Counter)  # lang -> gold/hit/marked/false
    missed = collections.defaultdict(collections.Counter)  # lang -> (id, surface)
    false = collections.defaultdict(collections.Counter)
    per_passage = []
    for r in rows:
        with open(os.path.join(HERE, 'passages', r['id'] + '.txt'), encoding='utf-8') as fh:
            text = fh.read()
        data = text.encode('utf-8')
        res = analyze(args.cli, args.packs, r['lang'], text)
        c = collections.Counter()
        for w in res['words']:
            b = bucket(w)
            c[b] += 1
            surface = data[w['start']:w['end']].decode('utf-8', 'replace')
            kind = name_kind(gold, r['id'], surface)
            marked = bool(w.get('name'))
            nc = names[r['lang']]
            if kind in NAME_KINDS:
                nc['gold'] += 1
                nc['hit'] += marked
                if not marked:
                    missed[r['lang']][(r['id'], surface, w.get('lemma') or '', w.get('pos') or '')] += 1
            if marked:
                nc['marked'] += 1
                if kind is None:
                    nc['false'] += 1
                    false[r['lang']][(r['id'], surface, w.get('lemma') or '', w.get('pos') or '')] += 1
            if b == 'not-found':
                notfound[r['lang']][surface] += 1
            elif b == 'base-gloss':
                k = (w['lemma'] or '', (w.get('how') or '') + ': ' + '; '.join(w['gloss'])[:80])
                basegloss[r['lang']][k] += 1
            elif b == 'empty':
                empty[r['lang']][(w.get('lemma') or '', w.get('pos') or '')] += 1
            elif b == 'no-level':
                k = (w['lemma'], w.get('pos') or '')
                nolevel[r['lang']][k] += 1
                nolevel_ex.setdefault((r['lang'],) + k, surface)
                if w.get('pos') == 'propn':
                    propn[r['lang']] += 1
        for g in ('all', r['lang'], f"{r['lang']}/{r['genre']}"):
            totals[g].update(c)
        per_passage.append({'id': r['id'], **{b: c[b] for b in BUCKETS}, 'tokens': sum(c.values())})

    with open(os.path.join(args.out, 'per-passage.tsv'), 'w', encoding='utf-8') as fh:
        fh.write('id\ttokens\t' + '\t'.join(BUCKETS) + '\n')
        for p in per_passage:
            fh.write(f"{p['id']}\t{p['tokens']}\t" + '\t'.join(str(p[b]) for b in BUCKETS) + '\n')
    for lang, cnt in notfound.items():
        with open(os.path.join(args.out, f'not-found-{lang}.tsv'), 'w', encoding='utf-8') as fh:
            fh.write('count\tword\n')
            for word, n in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
                fh.write(f'{n}\t{word}\n')
    for lang, cnt in nolevel.items():
        with open(os.path.join(args.out, f'no-level-{lang}.tsv'), 'w', encoding='utf-8') as fh:
            fh.write('count\tlemma\tpos\texample\n')
            for (lemma, pos), n in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
                fh.write(f'{n}\t{lemma}\t{pos}\t{nolevel_ex[(lang, lemma, pos)]}\n')

    for lang, cnt in empty.items():
        with open(os.path.join(args.out, f'empty-{lang}.tsv'), 'w', encoding='utf-8') as fh:
            fh.write('count\tlemma\tpos\n')
            for (lemma, pos), n in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
                fh.write(f'{n}\t{lemma}\t{pos}\n')

    for lang, cnt in basegloss.items():
        with open(os.path.join(args.out, f'base-gloss-{lang}.tsv'), 'w', encoding='utf-8') as fh:
            fh.write('count\tlemma\thow: gloss\n')
            for (lemma, g), n in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
                fh.write(f'{n}\t{lemma}\t{g}\n')

    for lang in names:
        for fname, cnt in ((f'names-missed-{lang}.tsv', missed[lang]), (f'names-false-{lang}.tsv', false[lang])):
            with open(os.path.join(args.out, fname), 'w', encoding='utf-8') as fh:
                fh.write('count\tid\tword\tlemma\tpos\n')
                for k, n in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
                    fh.write(f'{n}\t' + '\t'.join(k) + '\n')

    groups = ['all'] + sorted(g for g in totals if g != 'all')
    if args.markdown:
        print('| group | tokens | level | no level | part-gloss | base-gloss | empty | not found | other |')
        print('|---|--:|--:|--:|--:|--:|--:|--:|--:|')
        for g in groups:
            t = totals[g]; n = sum(t.values())
            print(f'| {g} | {n} | ' + ' | '.join(f'{t[b]} ({pct(t[b], n)}%)' for b in BUCKETS) + ' |')
    else:
        print(f"{'group':24} {'tokens':>7} " + ' '.join(f'{b:>16}' for b in BUCKETS))
        for g in groups:
            t = totals[g]; n = sum(t.values())
            print(f'{g:24} {n:7d} ' + ' '.join(f'{t[b]:6d} ({pct(t[b], n):>5}%)' for b in BUCKETS))
    for lang in sorted(names):
        n = names[lang]
        prec = pct(n['hit'], n['hit'] + n['false'])
        print(f"{lang} names: {n['hit']} of {n['gold']} marked (recall {pct(n['hit'], n['gold'])}%), "
              f"{n['false']} false alarms of {n['marked']} marked (precision {prec}%)")
    for lang in sorted(propn):
        print(f'{lang}: {propn[lang]} of the no-level tokens are proper nouns (pos=propn)')
    print(f'details: {args.out}')


if __name__ == '__main__':
    main()
