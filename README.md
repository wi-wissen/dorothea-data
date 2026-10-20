# Dorothea data

Open dictionary data for **Dorothea**, a dictionary and reading aid for German and English
(German–English, English–German, German–German, English–English) with CEFR levels and topics.

This repository holds the data only. It is published under
[CC BY-SA 4.0](LICENSE), because most of it is derived from Wiktionary. Exception: our own CEFR
level and topic lists (`curation/levels/`, `curation/topics.tsv`) are licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

> **Status:** setting up. There is no data here yet; see the planned layout below.

## Sources

| Source | Used for | Licence |
|---|---|---|
| English Wiktionary, via the [kaikki.org](https://kaikki.org/) extracts | German entries with English glosses; English definitions, forms, pronunciation | CC BY-SA 4.0 |
| German Wiktionary, via the kaikki.org extracts | German definitions; translations into English | CC BY-SA 4.0 |
| [Wikidata lexemes](https://www.wikidata.org/wiki/Wikidata:Lexicographical_data) | linking senses and translations | CC0 1.0 |
| [Open English WordNet](https://en-word.net/) | English sense groups and synonyms | CC BY 4.0 |
| [OdeNet](https://github.com/hdaSprachtechnologie/odenet) | German sense groups and synonyms | CC BY-SA 4.0 |
| Dorothea's own curation | unified glosses, corrections | CC BY-SA 4.0 |
| Dorothea's own CEFR and topic lists | level and topics per headword | CC BY 4.0 |

Exact versions and download dates of every import are listed in [SOURCES.md](SOURCES.md).

## Attribution

If you reuse this data, credit it like this:

> Dorothea dictionary data, https://github.com/wi-wissen/dorothea-data, CC BY-SA 4.0.
> Contains material from Wiktionary (https://www.wiktionary.org/, CC BY-SA 4.0; authors listed in
> each page's history), Wikidata (CC0), Open English WordNet (CC BY 4.0) and OdeNet (CC BY-SA 4.0).

Each entry records which source each field came from, so that every page can be traced back.

## Planned layout

```
SOURCES.md          versions, dates and checksums of all imported sources
docs/FORMAT.md      the entry format
docs/METHOD.md      how the data is made, including AI curation runs
curation/           Dorothea's own layer: corrections, unified glosses, CEFR levels, topics
```

The full normalised dictionary is generated from the sources plus `curation/` and published as
release assets, not committed file by file (see `docs/FORMAT.md` once it exists).
