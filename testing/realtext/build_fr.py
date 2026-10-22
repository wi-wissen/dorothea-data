"""Build the French passages of the real-text development set (selection + extraction).

Same rules as build.py (README, "Selection rule"), for French: Project Gutenberg prose, French
Wikipedia (first section after the lead of a randomly chosen member of one category per topic)
and Tatoeba sentences of native speakers. Not shipped.

Usage: python3 build_fr.py <out dir> <download dir> books,wiki,tatoeba
"""
import bz2, json, os, random, re, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from html.parser import HTMLParser
from mw import api

OUT, DL = sys.argv[1], sys.argv[2]
RETRIEVED = '2026-10-22'
MIN_W, MAX_W = 200, 400
os.makedirs(os.path.join(OUT, 'passages'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'attribution'), exist_ok=True)
CACHE = os.path.join(DL, 'cache')
os.makedirs(CACHE, exist_ok=True)


def rng(key):
    return random.Random('realtext-v1:' + key)


def nwords(s):
    return len(s.split())


SENT_RE = re.compile(r'(?<=[.!?…»])\s+(?=[«"“(A-ZÀÂÉÈÊÎÔÛÇ0-9—–-])')


def sentences(p):
    return [s.strip() for s in SENT_RE.split(p) if s.strip()]


def assemble(paras):
    """Whole paragraphs until MAX_W; if still under MIN_W, fill with whole sentences of the next one."""
    got, total = [], 0
    for p in paras:
        w = nwords(p)
        if total + w <= MAX_W:
            got.append(p)
            total += w
            if total >= MIN_W and total >= MAX_W - 40:
                break
            continue
        if total >= MIN_W:
            break
        part = []
        for s in sentences(p):
            if total + nwords(s) > MAX_W:
                break
            part.append(s)
            total += nwords(s)
        if part:
            got.append(' '.join(part))
        break
    return got if total >= MIN_W else None


SKIP_TAGS = {'table', 'figure', 'style', 'script', 'math', 'ul', 'ol', 'dl', 'blockquote', 'pre', 'gallery', 'caption'}
SKIP_CLASS = ('reference', 'mw-editsection', 'mwe-math', 'noprint', 'navbox', 'infobox', 'thumb', 'hatnote',
              'metadata', 'toccolours', 'sister', 'ambox', 'mw-empty-elt', 'noexcerpt', 'printfooter', 'catlinks',
              'IPA', 'mw-ref', 'cite-bracket', 'bandeau', 'homonymie', 'navigation', 'API')
VOID = {'br', 'img', 'hr', 'meta', 'link', 'input', 'wbr', 'source', 'track', 'col', 'area'}


class Para(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.items, self.cur = [], [], None

    def skipping(self):
        return any(s for _, s in self.stack)

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        cls = a.get('class') or ''
        skip = tag in SKIP_TAGS or any(c in cls for c in SKIP_CLASS) or 'display:none' in a.get('style', '').replace(' ', '')
        self.stack.append((tag, skip))
        if not self.skipping() and tag in ('p', 'h2', 'h3') and self.cur is None:
            self.cur = [tag, []]

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack:
            t, _ = self.stack.pop()
            if t == tag:
                break
        if self.cur is not None and tag == self.cur[0]:
            txt = re.sub(r'\s+', ' ', ''.join(self.cur[1])).strip()
            txt = re.sub(r'\[\d+\]|\[note \d+\]|\[réf\. nécessaire\]|\[a\]|\[b\]', '', txt)
            txt = re.sub(r'\s+([,.;:])', r'\1', txt).strip()
            if txt:
                self.items.append((self.cur[0], txt))
            self.cur = None

    def handle_data(self, d):
        if self.cur is not None and not self.skipping():
            self.cur[1].append(d)


def parse_page(base, title):
    fn = os.path.join(CACHE, 'parse_' + re.sub(r'\W+', '_', base + title) + '.json')
    if os.path.exists(fn):
        d = json.load(open(fn))
    else:
        d = api(base, action='parse', page=title, prop='text|revid|displaytitle', disableeditsection=1,
                disabletoc=1, redirects=1)
        json.dump(d, open(fn, 'w'))
    p = d['parse']
    pr = Para()
    pr.feed(p['text'])
    return p['title'], p['revid'], pr.items


def is_prose(t):
    return nwords(t) >= 8 and re.search(r'[.!?…]["“”»)]?$', t)


def wiki_section_after_lead(items):
    out, seen_h2 = [], False
    for kind, t in items:
        if kind == 'h2':
            seen_h2 = True
            continue
        if kind == 'p' and seen_h2 and is_prose(t):
            out.append(t)
    return out


def members(base, cat):
    fn = os.path.join(CACHE, re.sub(r'\W+', '_', base + cat) + '.json')
    if os.path.exists(fn):
        return json.load(open(fn))
    titles, cont = [], {}
    while True:
        d = api(base, action='query', list='categorymembers', cmtitle=cat, cmtype='page', cmnamespace=0,
                cmlimit=500, **cont)
        titles += [m['title'] for m in d['query']['categorymembers']]
        if 'continue' not in d:
            break
        cont = {'cmcontinue': d['continue']['cmcontinue']}
    titles.sort()
    json.dump(titles, open(fn, 'w'))
    return titles


rows = []


def write(pid, genre, topic, source, title, url, licence, attribution, paras):
    text = '\n\n'.join(paras) + '\n'
    open(os.path.join(OUT, 'passages', pid + '.txt'), 'w', encoding='utf-8').write(text)
    rows.append(dict(id=pid, lang='fr', genre=genre, topic=topic, source=source, title=title, url=url,
                     licence=licence, attribution=attribution, retrieved=RETRIEVED, words=nwords(text)))
    print(pid, title, nwords(text), flush=True)


# One category per topic; the first one with at least five articles is used.
WP = [
    ('history', ['Catégorie:Traité de paix', 'Catégorie:Bataille de la guerre de Cent Ans']),
    ('biography', ['Catégorie:Peintre français du XIXe siècle']),
    ('geography', ['Catégorie:Île de la mer Méditerranée', 'Catégorie:Île de la mer Égée']),
    ('science', ['Catégorie:Élément chimique']),
    ('technology', ['Catégorie:Appareil électroménager']),
    ('food', ['Catégorie:Fromage français', 'Catégorie:Fromage au lait de vache']),
]


def run_wiki():
    host = 'fr.wikipedia.org'
    base = f'https://{host}/w/api.php'
    for topic, cats in WP:
        pid = f'fr-wp-{topic}'
        cat = next((c for c in cats if len(members(base, c)) >= 5), None)
        if cat is None:
            raise RuntimeError('no category for ' + pid)
        order = list(members(base, cat))
        rng(pid).shuffle(order)
        for t in order[:40]:
            if re.match(r'Liste ', t):
                continue
            title, revid, items = parse_page(base, t)
            paras = wiki_section_after_lead(items)
            got = assemble(paras) if paras else None
            if got:
                q = urllib.parse.quote(title.replace(' ', '_'))
                write(pid, 'encyclopedia', topic, 'Wikipedia', title,
                      f'https://{host}/w/index.php?title={q}&oldid={revid}', 'CC BY-SA 4.0',
                      f'Wikipedia contributors, see https://{host}/w/index.php?title={q}&action=history', got)
                print('  category:', cat, file=sys.stderr)
                break
        else:
            raise RuntimeError('no candidate for ' + pid)


BOOKS = [
    ('literature', 14790, 'maupassant', 'Guy de Maupassant', 'Contes du jour et de la nuit'),
    ('literature', 11770, 'daudet', 'Alphonse Daudet', 'Lettres de mon moulin'),
    ('literature', 17489, 'hugo', 'Victor Hugo', 'Les misérables, tome I : Fantine'),
    ('literature', 13951, 'dumas', 'Alexandre Dumas', 'Les trois mousquetaires'),
    ('literature', 23582, 'sand', 'George Sand', 'La Mare au Diable'),
]


def gutenberg_paras(path):
    raw = open(path, encoding='utf-8-sig').read().replace('\r\n', '\n')
    body = raw.split('*** START OF', 1)[1].split('\n', 1)[1].split('*** END OF', 1)[0]
    paras = []
    for block in re.split(r'\n\s*\n', body):
        lines = [l.strip() for l in block.strip().split('\n')]
        t = ' '.join(l for l in lines if l)
        t = re.sub(r'\[Illustration[^\]]*\]', '', t)
        t = re.sub(r'\[\d+\]|\[Note[^\]]*\]', '', t)
        t = t.replace('~', '').replace('_', '').replace('=', '')
        t = re.sub(r'\s+', ' ', t).strip()
        paras.append(t)
    return paras


def run_books():
    for genre, eid, slug, author, title in BOOKS:
        pid = f'fr-lit-{slug}'
        paras = gutenberg_paras(os.path.join(DL, 'gutenberg', f'pg{eid}.txt'))
        r = rng(pid)
        n = len(paras)
        for _ in range(50):
            i = r.randrange(int(n * 0.2), int(n * 0.8))
            while i < n and not is_prose(paras[i]):
                i += 1
            run = []
            for p in paras[i:]:
                if not p:
                    continue
                if not is_prose(p) and nwords(p) < 12:
                    break
                run.append(p)
                if sum(map(nwords, run)) > MAX_W:
                    break
            got = assemble(run)
            if got:
                write(pid, genre, slug, 'Project Gutenberg', f'{author}: {title}',
                      f'https://www.gutenberg.org/ebooks/{eid}', 'public domain',
                      f'{author}; Project Gutenberg eBook #{eid} (licence header removed)', got)
                break
        else:
            raise RuntimeError('no passage ' + pid)


def run_tatoeba():
    tdir = os.path.join(DL, 'tatoeba')
    cc0 = set()
    for line in open(os.path.join(tdir, 'sentences_CC0.csv'), encoding='utf-8'):
        cc0.add(line.split('\t', 1)[0])
    natives = set()
    for line in open(os.path.join(tdir, 'user_languages.csv'), encoding='utf-8'):
        f = line.rstrip('\n').split('\t')
        if len(f) >= 3 and f[0] == 'fra' and f[1] == '5':
            natives.add(f[2])
    cand = []
    with bz2.open(os.path.join(tdir, 'fra_sentences_detailed.tsv.bz2'), 'rt', encoding='utf-8') as fh:
        for line in fh:
            f = line.rstrip('\n').split('\t')
            if len(f) < 4 or f[3] not in natives:
                continue
            if 5 <= nwords(f[2]) <= 15:
                cand.append((int(f[0]), f[2], f[3]))
    cand.sort()
    rng('fr-tatoeba').shuffle(cand)
    pos = 0
    for n in (1, 2):
        pid = f'fr-tatoeba-{n}'
        got, total = [], 0
        while total < 300:
            s = cand[pos]
            pos += 1
            got.append(s)
            total += nwords(s[1])
        with open(os.path.join(OUT, 'attribution', pid + '.tsv'), 'w', encoding='utf-8') as fa:
            fa.write('sentence_id\tusername\tlicence\turl\n')
            for sid, text, user in got:
                lic = 'CC0 1.0' if str(sid) in cc0 else 'CC BY 2.0 FR'
                fa.write(f'{sid}\t{user}\t{lic}\thttps://tatoeba.org/en/sentences/show/{sid}\n')
        write(pid, 'everyday', 'sentences', 'Tatoeba', f'{len(got)} sentences',
              'https://downloads.tatoeba.org/exports/per_language/fra/fra_sentences_detailed.tsv.bz2',
              'CC BY 2.0 FR (some CC0 1.0)', f'Tatoeba users, per sentence in attribution/{pid}.tsv',
              ['\n'.join(s[1] for s in got)])


if __name__ == '__main__':
    parts = sys.argv[3].split(',')
    if 'books' in parts:
        run_books()
    if 'tatoeba' in parts:
        run_tatoeba()
    if 'wiki' in parts:
        run_wiki()
    json.dump(rows, open(os.path.join(DL, 'rows-fr-' + sys.argv[3].replace(',', '_') + '.json'), 'w'),
              ensure_ascii=False, indent=1)
