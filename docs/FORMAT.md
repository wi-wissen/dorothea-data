# Entry format

Status: draft for the first milestone (German→English). Fields may be added; existing fields keep
their meaning.

Dorothea's data has two layers:

1. **Imported data**, generated from the sources by the import tool. It is never edited by hand and
   is published as release assets (`entries-<lang>.jsonl.gz`), not committed.
2. **Curation layer** in `curation/`, committed here: our own corrections, unified glosses, CEFR
   levels and topics, stored as an overlay on top of the imported data.

The build applies the overlay to the imported data and produces the final entries and packs.

## Entries (`entries-<lang>.jsonl`)

One JSON object per line, sorted by `key`. One entry is one lemma with one part of speech (and one
etymology where a source distinguishes homographs).

```json
{
  "key": "de:Bank:noun:1",
  "lang": "de",
  "lemma": "Bank",
  "pos": "noun",
  "gender": ["f"],
  "ipa": ["baŋk"],
  "forms": {"plural": ["Bänke"], "genitive": ["Bank"]},
  "cefr": "A2",
  "topics": ["furniture"],
  "senses": [
    {
      "id": "en-Bank-de-noun-AbCdEf12",
      "gloss": {"en": ["bench"]},
      "tags": [],
      "cefr": "A2",
      "topics": ["furniture"],
      "src": "enwikt"
    }
  ],
  "src": {"entry": "enwikt", "gender": "enwikt", "ipa": "enwikt", "forms": "enwikt", "cefr": "cur"}
}
```

| Field | Meaning |
|---|---|
| `key` | stable key `lang:lemma:pos:n`; `n` numbers homographs (1, 2, …) in source order |
| `lang` | `de` or `en` |
| `lemma` | dictionary form as the source writes it |
| `pos` | `noun`, `verb`, `adj`, `adv`, `pron`, `det`, `prep`, `conj`, `num`, `part`, `intj`, `propn`, `phrase`, `prefix`, `suffix`, `abbr` |
| `gender` | nouns: list of `m`, `f`, `n` (several for nouns with variable gender) |
| `ipa` | pronunciations, without slashes |
| `forms` | a few display forms only (plural, genitive; for verbs `pres3sg`, `past`, `pp`, `aux`; for adjectives `comp`, `sup`). Lookup does not use them: inflected forms are resolved by Heinrich's morphology. |
| `cefr` | level of the entry: `A1` … `C2`; absent if unknown |
| `topics` | topic ids from `curation/topics.tsv` |
| `senses` | ordered list, most common sense first |
| `senses[].id` | sense id from the source (for English Wiktionary the wiktextract id); used as the overlay anchor |
| `senses[].gloss` | short translations or definitions per target language (`en` for German→English) |
| `senses[].def` | optional longer definition per language |
| `senses[].tags` | register and usage labels (`colloquial`, `regional`, `dated`, `figurative`, …) |
| `src` | source of each field: `enwikt`, `dewikt`, `wikidata`, `oewn`, `odenet`, or `cur` (curation layer) |

Source codes and their versions are listed in `SOURCES.md`; every release names the versions it was
built from.

### What the import keeps and drops (English Wiktionary, German entries)

- Kept: lemma entries with at least one sense that is not only a form-of or alt-of reference.
  Senses that only point to another lemma are dropped; Heinrich's morphology resolves those forms.
- Kept per sense: glosses (split into short glosses at `;`), labels as `tags`.
- Dropped in the first milestone: etymology, descendants, derived terms, examples, audio. They can
  be added later as new fields.

## Curation layer (`curation/`)

```
curation/topics.tsv              topic catalogue: id, German label, English label
curation/levels/<lang>.tsv       CEFR level and topics per entry or sense
curation/edits/<lang>/<x>.jsonl  edits per entry, sharded by the first letter of the lemma
```

### Levels (`curation/levels/<lang>.tsv`)

Tab-separated, header row, sorted:

```
lemma	pos	sense	cefr	topics
Bank	noun		A2	furniture
Bank	noun	en-Bank-de-noun-XyZ98765	B1	money
```

An empty `sense` sets the level of the whole entry.

### Edits (`curation/edits/<lang>/<x>.jsonl`)

One edit per line:

```json
{"key": "de:Bank:noun:1", "sense": "en-Bank-de-noun-AbCdEf12", "anchor": "bench (furniture)", "op": "set", "field": "gloss.en", "value": ["bench"], "run": "cur-2026-11-a"}
```

| Field | Meaning |
|---|---|
| `key`, `sense` | target entry and sense (`sense` empty for entry-level fields) |
| `anchor` | the original source gloss of that sense, so that the edit can be re-attached if a new dump changes the sense id |
| `op` | `set` (replace a field), `add` (add a sense or list value), `hide` (do not show a sense), `order` (new sense order: `value` is a list of sense ids) |
| `field`, `value` | the field and its new value |
| `run` | the curation run that made the edit (documented in `curation/RUNS.md`) |

On every import, the build reports edits whose key or sense no longer exists and could not be
re-attached through the anchor; those are reviewed by hand.
