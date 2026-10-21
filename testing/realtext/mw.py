import json, time, urllib.request, urllib.parse, sys
UA = 'DorotheaDevSet/0.1 (https://github.com/wi-wissen/dorothea-data)'
def get(url, params=None, tries=12):
    if params:
        url = url + '?' + urllib.parse.urlencode(params)
    for i in range(tries):
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                ra = int(e.headers.get('retry-after') or 30)
                print(f'  {e.code}, waiting {ra+5}s', file=sys.stderr, flush=True)
                time.sleep(ra + 5)
                continue
            raise
    raise RuntimeError('too many retries: ' + url)
def api(base, **params):
    params.setdefault('format', 'json'); params.setdefault('formatversion', '2')
    data = json.loads(get(base, params))
    time.sleep(1.5)
    return data
