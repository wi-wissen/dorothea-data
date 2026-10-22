#!/usr/bin/env python3
"""Validate the real-text development set: passages.tsv, passages/<id>.txt, attribution/<id>.tsv.

Exit code 0 when everything is consistent, 1 otherwise. Python 3 standard library only.
"""
import csv
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
COLUMNS = ['id', 'lang', 'genre', 'topic', 'source', 'title', 'url', 'licence', 'attribution', 'retrieved', 'words']
LANGS = {'de', 'en', 'fr'}
GENRES = {'encyclopedia', 'encyclopedia-simple', 'news', 'literature', 'fairy-tale', 'everyday'}
LICENCES = {'CC BY-SA 4.0', 'CC BY 2.5', 'CC BY 4.0', 'public domain', 'CC BY 2.0 FR (some CC0 1.0)'}
SENTENCE_LICENCES = {'CC BY 2.0 FR', 'CC0 1.0'}
EXCLUDED_TITLES = {'Klaus Störtebeker'}
MIN_WORDS, MAX_WORDS = 200, 400


def main():
    errors = []

    def err(msg):
        errors.append(msg)

    with open(os.path.join(HERE, 'passages.tsv'), encoding='utf-8', newline='') as fh:
        reader = csv.DictReader(fh, delimiter='\t', quoting=csv.QUOTE_NONE)
        if reader.fieldnames != COLUMNS:
            err(f'passages.tsv columns {reader.fieldnames} != {COLUMNS}')
        rows = list(reader)

    ids = set()
    for n, r in enumerate(rows, start=2):
        pid = r['id']
        where = f'passages.tsv line {n} ({pid})'
        if any(v is None or v == '' for v in r.values()):
            err(f'{where}: empty field')
            continue
        if pid in ids:
            err(f'{where}: duplicate id')
        ids.add(pid)
        if not re.fullmatch(r'[a-z]{2}-[a-z0-9-]+', pid) or not pid.startswith(r['lang'] + '-'):
            err(f'{where}: id must be <lang>-<lowercase slug>')
        if r['lang'] not in LANGS:
            err(f'{where}: unknown lang {r["lang"]}')
        if r['genre'] not in GENRES:
            err(f'{where}: unknown genre {r["genre"]}')
        if r['licence'] not in LICENCES:
            err(f'{where}: licence {r["licence"]} not in the allowed list')
        if not r['url'].startswith('https://'):
            err(f'{where}: url must be https')
        if 'wikipedia.org' in r['url'] or 'wikinews.org' in r['url'] or 'zum.de' in r['url']:
            if 'oldid=' not in r['url']:
                err(f'{where}: wiki url must be a permalink with oldid')
            if 'action=history' not in r['attribution']:
                err(f'{where}: wiki attribution must link the page history')
        if r['title'] in EXCLUDED_TITLES:
            err(f'{where}: excluded article {r["title"]}')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', r['retrieved']):
            err(f'{where}: retrieved must be YYYY-MM-DD')
        path = os.path.join(HERE, 'passages', pid + '.txt')
        if not os.path.exists(path):
            err(f'{where}: missing passages/{pid}.txt')
            continue
        with open(path, encoding='utf-8') as fh:
            text = fh.read()
        if unicodedata.normalize('NFC', text) != text:
            err(f'{pid}.txt: not NFC')
        if not text.endswith('\n') or text.endswith('\n\n'):
            err(f'{pid}.txt: must end with exactly one newline')
        if re.search(r'[ \t]+$', text, re.M):
            err(f'{pid}.txt: trailing whitespace')
        if re.search(r'\[\d+\]', text):
            err(f'{pid}.txt: footnote marker left in text')
        words = len(text.split())
        if str(words) != r['words']:
            err(f'{where}: words {r["words"]} but file has {words}')
        if not MIN_WORDS <= words <= MAX_WORDS:
            err(f'{where}: {words} words, outside {MIN_WORDS}-{MAX_WORDS}')
        if r['source'] == 'Tatoeba':
            apath = os.path.join(HERE, 'attribution', pid + '.tsv')
            if not os.path.exists(apath):
                err(f'{where}: missing attribution/{pid}.tsv')
                continue
            with open(apath, encoding='utf-8', newline='') as fh:
                arows = list(csv.DictReader(fh, delimiter='\t', quoting=csv.QUOTE_NONE))
            lines = text.rstrip('\n').split('\n')
            if len(arows) != len(lines):
                err(f'{pid}: {len(lines)} sentences but {len(arows)} attribution rows')
            for a in arows:
                if not a.get('username') or a.get('licence') not in SENTENCE_LICENCES:
                    err(f'attribution/{pid}.tsv: bad row {a}')

    for d, ext in (('passages', '.txt'), ('attribution', '.tsv')):
        for f in sorted(os.listdir(os.path.join(HERE, d))):
            if not f.endswith(ext) or f[:-len(ext)] not in ids:
                err(f'{d}/{f}: not listed in passages.tsv')

    by = {}
    for r in rows:
        by[(r['lang'], r['genre'])] = by.get((r['lang'], r['genre']), 0) + 1
    for e in errors:
        print('ERROR', e)
    print(f'{len(rows)} passages: ' + ', '.join(f'{l}/{g} {n}' for (l, g), n in sorted(by.items())))
    print('OK' if not errors else f'{len(errors)} errors')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
