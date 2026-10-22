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
| `senses[].prov` | source of values added to a sense by another step, per field path: `{"gloss.en[2..]": "dewikt"}` (items from index 2 on), `{"gloss.de": "reverse"}` (German translations found by looking the English word up in the German entries' glosses), `"derived"` (rules from a related word: an adverb from its adjective, a comparative, a plural, a spelling variant or synonym from the word it names), `"odenet"` (OdeNet linked to Open English WordNet through the Interlingual Index, confirmed by the German entries' glosses), `"wikidata"` (Wikidata lexemes), `"cur"` (curation). `reverse`, `derived`, `odenet` and `wikidata` translations are shown as "less certain". |

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
curation/topics.tsv                       topic catalogue: id, German label, English label
curation/levels/<lang>.tsv                CEFR level and topics per entry or sense
curation/edits/<lang>/<run-id>/*.jsonl    output of one curation run (sense visibility, order,
                                          learner explanations, translation fixes), read as is
curation/edits/<lang>/<x>.jsonl           single edits per entry (reserved for hand edits)
curation/runs/<run-id>.md                 instruction and log of each run
```

### Levels (`curation/levels/<lang>.tsv`)

Tab-separated, `#` comment lines, header row, sorted by lemma:

```
lemma	pos	hint	cefr	topics
Bank	noun		A2	furniture
Bank	noun	money	B1	money
```

`hint` is empty for the whole entry; otherwise a short own sense label or a source sense id. The
build attaches a hinted level to the sense whose gloss matches the label; unmatched hints are
reported. Topic ids come from `curation/topics.tsv`.

The level and topic files and the topic catalogue are Dorothea's own work and licensed under
**CC BY 4.0** (they are not derived from Wiktionary). Levels attached to a Wiktionary sense in the
built entries are part of the CC BY-SA data.

### Curation runs (`curation/edits/<lang>/<run-id>/*.jsonl`)

The output of a curation run (instruction and log in `curation/runs/<run-id>.md`) is stored as the
agents wrote it, one file per batch (`out-NN.jsonl`), in a directory named after the run. The build
reads these files directly (`dorothea-import direction --curation <run dir>`); there is no
conversion step. `<lang>` is the headword language; the run id is the directory name. Runs are
applied in run-id order; a later run's edit of the same sense wins.

One line per entry:

```json
{"key": "de:Zug:noun:1",
 "senses": [
   {"id": "en-Zug-de-noun-9xdFfRLl", "show": "main", "order": 1,
    "learner_de": "Fahrzeug auf Schienen mit mehreren Wagen",
    "en_keep": [], "en_drop": ["train (multiple vehicles …)"], "en_add": ["train"]},
   {"id": "dewikt-Zug-noun-3", "show": "hide"}],
 "missing": null,
 "see": null}
```

Several missing meanings (Spanish *poner*: *ponerse la ropa* and *ponerse nervioso*):

```json
"missing": [
  {"learner_es": "vestirse con algo", "de": ["anziehen"], "en": ["to put on"]},
  {"learner_es": "empezar a sentirse así", "de": ["werden"], "en": ["to get", "to become"]}]
```

| Field | Meaning |
|---|---|
| `key` | target entry (`lang:lemma:pos:n`) |
| `senses[].id` | source sense id (the anchor; see below) |
| `senses[].show` | `main` (on the card), `more` (under "more meanings"), `hide` (kept in the data, not shown: obsolete, rare, duplicate, cross-reference) |
| `senses[].order` | position among the `main` and `more` senses, 1 = first; `hide` senses have none |
| `senses[].learner_<lang>` | short explanation for learners in the headword language: `learner_de` for German headwords, `learner_en` for English ones (the English pilot writes it as `learner`). Stored as `learner.<lang>` |
| `senses[].<t>_keep`, `<t>_drop`, `<t>_add` | translations into language `t` (`en` for German headwords, `de` for English ones): source glosses that are correct, source glosses that are wrong, new ones. German nouns may be added with their article (`das Haus`); the build writes them like the source (`Haus n`) |
| `senses[].note` | optional remark of the curator; not used by the build |
| `missing` | optional everyday meanings the source lacks: one object `{"learner_<lang>": "…", "<t>": ["…"]}`, an array of such objects (in card order), or `null`; `[]` means none |
| `see` | optional base word of an entry that only refers to it (an inflected form or a pure cross-reference); the lookup follows it like a `form_of` reference |

How the build applies a run (all four directions):

- **Entry.** By `key`; if the key is missing, among the entries with the same lemma and part of
  speech the one holding most of the edit's sense ids (homograph numbers differ between sources).
- **Sense.** By `id`. If a new dump changed the id, the edit is re-attached by its **anchor**: the
  kept and dropped glosses of the edit are verbatim source glosses, and the unclaimed sense sharing
  most of them wins. Edits that attach nowhere are reported (`curation-unattached.tsv` next to the
  pack, count in `manifest.json`) and reviewed by hand.
- **Translations** of language `t`: kept glosses first (in the edit's order), then added ones, then
  source glosses the edit neither kept nor dropped; dropped ones go. A gloss string that holds
  several translations (`to bring, to lead`) is replaced as a whole when the edit drops it and adds
  clean ones.
- **Order.** `main` senses by `order`, then `more` senses by `order`, then senses without an edit,
  then `hide` senses.
- **`missing`** adds a `main` sense with `src: cur` per object after the other `main` senses,
  in array order (ids `cur-missing-<n>`, `cur-missing-<n>-2`, `cur-missing-<n>-3`, …; a single
  object is the same as a one-element array). Objects with neither a learner explanation nor
  translations are skipped. **`see`** sets the entry's `see` field.
- **Directions whose input lacks curated senses** (`de → de` is built from the German Wiktionary
  alone): a `main` or `more` sense of the other Wiktionary is carried over with its learner
  explanation as its gloss (`src: cur`); a lemma the input lacks gets an entry (`src.entry: cur`)
  when it has such senses.
- Entries without an edit are unchanged.

Entry fields written by the build:

| Field | Meaning |
|---|---|
| `senses[].show` | `main`, `more` or `hide`; absent for uncurated senses |
| `senses[].learner` | `{"de": "…"}` or `{"en": "…"}` |
| `see` | base word of a reference entry |
| `src.cur` | id of the run that curated the entry |

Provenance: `show` and `learner` exist only through curation, so their source is always `cur`.
Glosses a run adds are marked in `prov` (`{"gloss.en[1..]": "cur"}`), senses and entries it adds
have `src: cur`, and `src.cur` names the run.

The run files are synthetic data written by AI agents and are published here under CC BY-SA 4.0
like the rest of the repository (they edit Wiktionary data).

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
re-attached through the anchor; those are reviewed by hand. The single-edit format is reserved
for hand edits; the build does not read it yet (curation runs use the run files above).
