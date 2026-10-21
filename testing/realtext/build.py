"""Build the real-text development set (selection + extraction). Not shipped; the rule is documented in README."""
import bz2, csv, html, json, os, random, re, sys, urllib.parse
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from html.parser import HTMLParser
from mw import api, get

OUT = sys.argv[1]
DL = sys.argv[2]
RETRIEVED = '2026-10-21'
MIN_W, MAX_W = 200, 400
os.makedirs(os.path.join(OUT, 'passages'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'attribution'), exist_ok=True)
CACHE = os.path.join(DL, 'cache'); os.makedirs(CACHE, exist_ok=True)

def rng(key):
    return random.Random('realtext-v1:' + key)

def nwords(s):
    return len(s.split())

SENT_RE = re.compile(r'(?<=[.!?…])["“”»«\')]?\s+(?=[„"«»“(\'A-ZÄÖÜ0-9])')
def sentences(p):
    out, last = [], 0
    for m in SENT_RE.finditer(p):
        out.append(p[last:m.start()].strip() + (m.group(0).strip() if m.group(0).strip() else ''))
        last = m.end()
    out.append(p[last:].strip())
    return [s for s in out if s]

def assemble(paras):
    """Whole paragraphs until MAX_W; if still under MIN_W, fill with whole sentences of the next one."""
    got, total = [], 0
    for p in paras:
        w = nwords(p)
        if total + w <= MAX_W:
            got.append(p); total += w
            if total >= MIN_W and total >= MAX_W - 40:
                break
            continue
        if total >= MIN_W:
            break
        part = []
        for s in sentences(p):
            if total + nwords(s) > MAX_W:
                break
            part.append(s); total += nwords(s)
        if part:
            got.append(' '.join(part))
        break
    return got if total >= MIN_W else None

# ---------- MediaWiki HTML -> paragraphs ----------
SKIP_TAGS = {'table', 'figure', 'style', 'script', 'math', 'ul', 'ol', 'dl', 'blockquote', 'pre', 'gallery', 'caption'}
SKIP_CLASS = ('reference', 'mw-editsection', 'mwe-math', 'noprint', 'navbox', 'infobox', 'thumb', 'hatnote',
              'metadata', 'toccolours', 'sister', 'ambox', 'mw-empty-elt', 'noexcerpt', 'printfooter', 'catlinks',
              'IPA', 'mw-ref', 'cite-bracket', 'rt-commentedText', 'Familienname', 'navigation')
VOID = {'br', 'img', 'hr', 'meta', 'link', 'input', 'wbr', 'source', 'track', 'col', 'area'}

class Para(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # (tag, skipping)
        self.items = []  # ('h2'|'h3'|'p', text)
        self.cur = None
    def skipping(self):
        return any(s for _, s in self.stack)
    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        cls = a.get('class') or ''
        skip = tag in SKIP_TAGS or any(c in cls for c in SKIP_CLASS) or a.get('style', '').replace(' ', '').find('display:none') >= 0
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
            txt = re.sub(r'\[\d+\]|\[Anm\. \d+\]|\[note \d+\]', '', txt)
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
        d = api(base, action='parse', page=title, prop='text|revid|displaytitle', disableeditsection=1, disabletoc=1, redirects=1)
        json.dump(d, open(fn, 'w'))
    p = d['parse']
    pr = Para(); pr.feed(p['text'])
    return p['title'], p['revid'], pr.items

def is_prose(t):
    return nwords(t) >= 8 and re.search(r'[.!?…]["“”»«)]?$', t)

def wiki_section_after_lead(items):
    """First h2 section after the lead; following sections continue it if it is short."""
    out, seen_h2 = [], False
    for kind, t in items:
        if kind == 'h2':
            seen_h2 = True; continue
        if kind == 'p' and seen_h2 and is_prose(t):
            out.append(t)
    return out

# Klexikon/MiniKlexikon append site boilerplate (about the site, sponsors, links) after the article.
BOILER = re.compile(r'^(Klexikon\.de ist die Wikipedia|Das Klexikon wird gefördert|Unsere Klexikon-Botschafter|'
                    r'Das Kinderlexikon Klexikon|Mehr über „|⇒)')

def from_start(items):
    out = []
    for k, t in items:
        if k == 'p' and BOILER.match(t):
            break
        if k == 'p' and is_prose(t):
            out.append(t)
    return out

def members(base, cat):
    fn = os.path.join(CACHE, re.sub(r'\W+', '_', base + cat) + '.json')
    if os.path.exists(fn):
        return json.load(open(fn))
    titles, cont = [], {}
    while True:
        d = api(base, action='query', list='categorymembers', cmtitle=cat, cmtype='page', cmnamespace=0, cmlimit=500, **cont)
        titles += [m['title'] for m in d['query']['categorymembers']]
        if 'continue' not in d:
            break
        cont = {'cmcontinue': d['continue']['cmcontinue']}
    titles.sort()
    json.dump(titles, open(fn, 'w'))
    return titles

def allpages(base):
    fn = os.path.join(CACHE, re.sub(r'\W+', '_', base) + '_allpages.json')
    if os.path.exists(fn):
        return json.load(open(fn))
    titles, cont = [], {}
    while True:
        d = api(base, action='query', list='allpages', apnamespace=0, apfilterredir='nonredirects', aplimit=500, **cont)
        titles += [m['title'] for m in d['query']['allpages']]
        if 'continue' not in d:
            break
        cont = {'apcontinue': d['continue']['apcontinue']}
    titles.sort()
    json.dump(titles, open(fn, 'w'))
    return titles

rows = []
used_titles = set()
EXCLUDE = {'Klaus Störtebeker', 'Störtebeker'}

def write(pid, lang, genre, topic, source, title, url, licence, attribution, paras):
    text = '\n\n'.join(paras) + '\n'
    open(os.path.join(OUT, 'passages', pid + '.txt'), 'w', encoding='utf-8').write(text)
    rows.append(dict(id=pid, lang=lang, genre=genre, topic=topic, source=source, title=title, url=url,
                     licence=licence, attribution=attribution, retrieved=RETRIEVED, words=nwords(text)))
    print(pid, title, nwords(text), flush=True)

def wiki_pick(pid, lang, genre, topic, base, host, source, licence, cand, mode, who):
    order = list(cand)
    rng(pid).shuffle(order)
    for t in order[:40]:
        if t in EXCLUDE or (host, t) in used_titles or re.search(r'(Liste|List) ', t):
            continue
        title, revid, items = parse_page(base, t)
        paras = wiki_section_after_lead(items) if mode == 'section' else from_start(items)
        got = assemble(paras) if paras else None
        if got:
            used_titles.add((host, t))
            url = f'https://{host}/w/index.php?title={urllib.parse.quote(title.replace(" ", "_"))}&oldid={revid}'
            hist = f'https://{host}/w/index.php?title={urllib.parse.quote(title.replace(" ", "_"))}&action=history'
            if host.endswith('zum.de'):
                url = url.replace('/w/index.php', '/index.php'); hist = hist.replace('/w/index.php', '/index.php')
            write(pid, lang, genre, topic, source, title, url, licence, f'{who}, see {hist}', got)
            return
    raise RuntimeError('no candidate for ' + pid)

BY_SA = 'CC BY-SA 4.0'
WP = [
 ('de', 'history', 'Kategorie:Friedensvertrag'), ('de', 'biography', 'Kategorie:Maler (Deutschland)'),
 ('de', 'geography', 'Kategorie:Insel (Europa)'), ('de', 'science', 'Kategorie:Chemisches Element'),
 ('de', 'technology', 'Kategorie:Haushaltsgerät'), ('de', 'sport', 'Kategorie:Ballsportart'),
 ('de', 'culture', 'Kategorie:Musikinstrument'), ('de', 'politics', 'Kategorie:Wahlsystem'),
 ('de', 'biology', 'Kategorie:Raubtiere'), ('de', 'economy', 'Kategorie:Wirtschaftsgeschichte'),
 ('de', 'medicine', 'Kategorie:Infektionskrankheit'), ('de', 'food', 'Kategorie:Deutsche Küche'),
 ('en', 'history', "Category:Battles of the Hundred Years' War"), ('en', 'biography', 'Category:19th-century American painters'),
 ('en', 'geography', 'Category:Islands of Greece'), ('en', 'science', 'Category:Chemical elements'),
 ('en', 'technology', 'Category:Home appliances'), ('en', 'sport', 'Category:Ball games'),
 ('en', 'culture', 'Category:String instruments'), ('en', 'politics', 'Category:Electoral systems'),
 ('en', 'biology', 'Category:Birds of Europe'), ('en', 'economy', 'Category:Banking terms'),
 ('en', 'medicine', 'Category:Viral diseases'), ('en', 'food', 'Category:Breads'),
]
SIMPLE = [('animals', 'Category:Mammals'), ('sport', 'Category:Sports'), ('music', 'Category:Musical instruments'),
          ('birds', 'Category:Birds'), ('geography', 'Category:Mountains'), ('science', 'Category:Chemical elements')]

def run_wiki():
    for lang, topic, cat in WP:
        host = f'{lang}.wikipedia.org'; base = f'https://{host}/w/api.php'
        wiki_pick(f'{lang}-wp-{topic}', lang, 'encyclopedia', topic, base, host, 'Wikipedia', BY_SA,
                  members(base, cat), 'section', 'Wikipedia contributors')
    base = 'https://simple.wikipedia.org/w/api.php'
    for topic, cat in SIMPLE:
        if isinstance(cat, list):  # first category in the list with at least 20 articles
            cat = next(c for c in cat if len(members(base, c)) >= 20)
            print('  simple places category:', cat, file=sys.stderr)
        m = members(base, cat)
        if not m:
            print('empty', cat); continue
        wiki_pick(f'en-simple-{topic}', 'en', 'encyclopedia-simple', topic, base, 'simple.wikipedia.org',
                  'Simple English Wikipedia', BY_SA, m, 'start', 'Simple English Wikipedia contributors')
    for n in range(1, 5):
        base = 'https://klexikon.zum.de/api.php'
        wiki_pick(f'de-klexikon-{n}', 'de', 'encyclopedia-simple', 'random', base, 'klexikon.zum.de', 'Klexikon',
                  BY_SA, allpages(base), 'start', 'Klexikon authors')
    for n in range(1, 3):
        base = 'https://miniklexikon.zum.de/api.php'
        wiki_pick(f'de-miniklexikon-{n}', 'de', 'encyclopedia-simple', 'random', base, 'miniklexikon.zum.de',
                  'MiniKlexikon', BY_SA, allpages(base), 'start', 'MiniKlexikon authors')

def run_news():
    base = 'https://de.wikinews.org/w/api.php'
    m = members(base, 'Kategorie:Veröffentlicht')
    for n in range(1, 5):
        wiki_pick(f'de-news-{n}', 'de', 'news', 'random', base, 'de.wikinews.org', 'Wikinews', 'CC BY 2.5', m, 'start',
                  'Wikinews contributors')
    base = 'https://en.wikinews.org/w/api.php'
    for topic, cat in [('politics', 'Category:Politics and conflicts'), ('science', 'Category:Science and technology'),
                       ('sport', 'Category:Sports'), ('culture', 'Category:Culture and entertainment')]:
        wiki_pick(f'en-news-{topic}', 'en', 'news', topic, base, 'en.wikinews.org', 'Wikinews', 'EN_NEWS_LICENCE',
                  members(base, cat), 'start', 'Wikinews contributors')

# ---------- Project Gutenberg ----------
BOOKS = [
 ('de', 'fairy-tale', 77905, 'grimm', 'Jacob und Wilhelm Grimm', 'Deutsche Märchen gesammelt durch die Brüder Grimm'),
 ('de', 'fairy-tale', 6638, 'hauff', 'Wilhelm Hauff', 'Märchen-Almanach auf das Jahr 1826'),
 ('de', 'literature', 5323, 'fontane', 'Theodor Fontane', 'Effi Briest'),
 ('de', 'literature', 74008, 'storm', 'Theodor Storm', 'Der Schimmelreiter'),
 ('de', 'literature', 22367, 'kafka', 'Franz Kafka', 'Die Verwandlung'),
 ('de', 'literature', 35312, 'eichendorff', 'Joseph von Eichendorff', 'Aus dem Leben eines Taugenichts'),
 ('en', 'fairy-tale', 2591, 'grimm', 'Jacob and Wilhelm Grimm, translated by Edgar Taylor and Marian Edwardes', "Grimms' Fairy Tales"),
 ('en', 'fairy-tale', 902, 'wilde', 'Oscar Wilde', 'The Happy Prince, and Other Tales'),
 ('en', 'literature', 1342, 'austen', 'Jane Austen', 'Pride and Prejudice'),
 ('en', 'literature', 1661, 'doyle', 'Arthur Conan Doyle', 'The Adventures of Sherlock Holmes'),
 ('en', 'literature', 74, 'twain', 'Mark Twain', 'The Adventures of Tom Sawyer'),
 ('en', 'literature', 215, 'london', 'Jack London', 'The Call of the Wild'),
]

def gutenberg_paras(path):
    raw = open(path, encoding='utf-8-sig').read().replace('\r\n', '\n')
    body = raw.split('*** START OF', 1)[1].split('\n', 1)[1].split('*** END OF', 1)[0]
    paras = []
    for block in re.split(r'\n\s*\n', body):
        lines = [l.strip() for l in block.strip().split('\n')]
        t = ' '.join(l for l in lines if l)
        t = re.sub(r'\[Illustration[^\]]*\]', '', t)
        t = re.sub(r'\[\d+\]|\[Footnote[^\]]*\]|\[Fußnote[^\]]*\]', '', t)
        t = t.replace('~', '').replace('_', '').replace('=', '')
        t = re.sub(r'\s+', ' ', t).strip()
        paras.append(t)
    return paras

def run_books():
    for lang, genre, eid, slug, author, title in BOOKS:
        pid = f'{lang}-lit-{slug}'
        paras = gutenberg_paras(os.path.join(DL, 'gutenberg', f'pg{eid}.txt'))
        r = rng(pid)
        n = len(paras)
        for _ in range(50):
            i = r.randrange(int(n * 0.2), int(n * 0.8))
            # start at the next prose paragraph
            while i < n and not is_prose(paras[i]):
                i += 1
            run = []
            for p in paras[i:]:
                if not p:
                    continue
                if not is_prose(p) and nwords(p) < 12:
                    break  # heading or verse break ends the run
                run.append(p)
                if sum(map(nwords, run)) > MAX_W:
                    break
            got = assemble(run)
            if got:
                write(pid, lang, genre, slug, 'Project Gutenberg', f'{author}: {title}',
                      f'https://www.gutenberg.org/ebooks/{eid}', 'public domain',
                      f'{author}; Project Gutenberg eBook #{eid} (licence header removed)', got)
                break
        else:
            raise RuntimeError('no passage ' + pid)

# ---------- Tatoeba ----------
def run_tatoeba():
    tdir = os.path.join(DL, 'tatoeba')
    cc0 = set()
    for line in open(os.path.join(tdir, 'sentences_CC0.csv'), encoding='utf-8'):
        cc0.add(line.split('\t', 1)[0])
    for lang3, lang in [('deu', 'de'), ('eng', 'en')]:
        natives = set()
        for line in open(os.path.join(tdir, 'user_languages.csv'), encoding='utf-8'):
            f = line.rstrip('\n').split('\t')
            if len(f) >= 3 and f[0] == lang3 and f[1] == '5':
                natives.add(f[2])
        cand = []
        with bz2.open(os.path.join(tdir, f'{lang3}_sentences_detailed.tsv.bz2'), 'rt', encoding='utf-8') as fh:
            for line in fh:
                f = line.rstrip('\n').split('\t')
                if len(f) < 4 or f[3] not in natives:
                    continue
                if 5 <= nwords(f[2]) <= 15:
                    cand.append((int(f[0]), f[2], f[3]))
        cand.sort()
        r = rng(f'{lang}-tatoeba')
        r.shuffle(cand)
        pos = 0
        for n in (1, 2):
            pid = f'{lang}-tatoeba-{n}'
            got, total = [], 0
            while total < 300:
                s = cand[pos]; pos += 1
                got.append(s); total += nwords(s[1])
            with open(os.path.join(OUT, 'attribution', pid + '.tsv'), 'w', encoding='utf-8') as fa:
                fa.write('sentence_id\tusername\tlicence\turl\n')
                for sid, text, user in got:
                    lic = 'CC0 1.0' if str(sid) in cc0 else 'CC BY 2.0 FR'
                    fa.write(f'{sid}\t{user}\t{lic}\thttps://tatoeba.org/en/sentences/show/{sid}\n')
            write(pid, lang, 'everyday', 'sentences', 'Tatoeba', f'{len(got)} sentences',
                  'https://downloads.tatoeba.org/exports/per_language/' + lang3 + '/' + lang3 + '_sentences_detailed.tsv.bz2',
                  'CC BY 2.0 FR (some CC0 1.0)', f'Tatoeba users, per sentence in attribution/{pid}.tsv',
                  ['\n'.join(s[1] for s in got)])

if __name__ == '__main__':
    parts = sys.argv[3].split(',')
    if 'books' in parts: run_books()
    if 'tatoeba' in parts: run_tatoeba()
    if 'wiki' in parts: run_wiki()
    if 'news' in parts: run_news()
    fn = os.path.join(DL, 'rows-' + sys.argv[3].replace(',', '_') + '.json')
    json.dump(rows, open(fn, 'w'), ensure_ascii=False, indent=1)
