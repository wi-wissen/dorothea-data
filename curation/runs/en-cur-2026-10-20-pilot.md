# Run en-cur-2026-10-20-pilot

| Field | Value |
|---|---|
| Date | 2026-10-20 |
| Type | `gloss` pilot (show/hide, order, learner definition, German check) followed by `check` |
| Input | English entries (English Wiktionary extract of 2026-10-03, merged and reverse-filled build) of 600 lemmas: frequency ranks 100–399 and 3,000–3,299 (Heinrich English frequency list, forms counted as written); 442 lemmas found, 1,076 entries (lemma + part of speech), 5,513 senses; 22 batches of about 250 senses |
| Bulk agents | 5 agents (smaller model), 4–5 batches each |
| Check | 1 independent agent (larger model), 80 random entries |
| Output | `curation/edits/en/en-cur-2026-10-20-pilot/out-NN.jsonl` (run file format of `docs/FORMAT.md`, "Curation runs"; read by the build as is) |

## Instruction (verbatim)

# Run en-cur-2026-10-20-pilot: learner-ready English entries

You curate English dictionary entries for **Dorothea**, a reading aid for learners and school
students (German speakers learning English, and English readers). The source is English Wiktionary
(CC BY-SA). Readers tap a word in a text and see a small card: it must show the senses a reader is
likely to need, in plain words, with correct German translations. Work from your own knowledge of
English and German. Do not consult other dictionaries or word lists, and do not open any files other
than the ones named below.

## Input

`/home/user/dorothea-build/cur-pilot/batch-NN.jsonl`: one entry per line:
`key, lemma, pos, rank` (frequency rank, lower = more frequent) and `senses`: `id`, `def` (the
Wiktionary definition, possibly cut at 300 characters), `tags` (usage labels), `de` (German
translations currently attached to the sense; some were added automatically and may be wrong).

## For every sense decide

1. **`show`**:
   - `main`: a sense a typical reader of everyday, school, news or fiction texts meets. Show it on
     the card. At most 6 `main` senses per entry; for most entries 1–3.
   - `more`: correct and occasionally useful, but secondary (less common uses, specialised but known
     uses, idiomatic extensions). Shown only under "More meanings".
   - `hide`: obsolete, archaic, dialectal, very rare, narrow technical/jargon senses, pure
     cross-references, or senses that duplicate another sense. Kept in the data, not shown.
2. **`order`**: 1, 2, 3 … for `main` and `more` senses together, most common first (the order a
   good learner's dictionary would use). `hide` senses get no order.
3. **`learner`** (only for `main` and `more`): a short definition in plain English: ≤ 15 words,
   vocabulary of level B1 where possible, no circular use of the headword, no parentheses unless
   needed. Write it yourself; do not copy the Wiktionary wording.
4. **German** (only for `main` and `more`):
   - `de_keep`: the given German translations that are correct for this sense (keep their spelling;
     you may drop a trailing gender letter but keep the word).
   - `de_drop`: given translations that are wrong or misleading for this sense.
   - `de_add`: for a `main` sense with no correct German translation, add 1–3 correct, common German
     translations (nouns with article, e.g. `das Haus`; verbs in the infinitive; separable verbs
     written together). Leave empty if the given ones are fine.
5. **`note`** (optional, ≤ 10 words): why, if you hid a frequent-looking sense or dropped
   translations.

## Output

`/home/user/dorothea-build/cur-pilot/out-NN.jsonl`: one line per input entry, same order:

```json
{"key": "en:run:verb:1", "senses": [{"id": "…", "show": "main", "order": 1, "learner": "to move quickly on your feet", "de_keep": ["rennen", "laufen"], "de_drop": [], "de_add": [], "note": ""}, {"id": "…", "show": "hide"}]}
```

Every input sense must appear exactly once with its `id`. Valid JSON per line. Verify with a short
script before finishing: same keys and sense ids in the same order as the input, allowed values only,
`main` count ≤ 6, `learner` ≤ 15 words.

## Agent task line (verbatim; NN = the agent's batches)

> Read /home/user/dorothea-build/cur-pilot/BRIEF.md and follow it exactly. Your batches: NN, NN, NN, NN (input batch-NN.jsonl → output out-NN.jsonl in the same folder). Every decision is your own judgement per sense; write the output files directly or with a small script that only serialises your decisions. Keep your own scratch files in /home/user/dorothea-build/cur-pilot/work-NN/ (create it). Verify each output as the brief says. Report back only: per batch the counts of main/more/hide, how many German translations you kept/dropped/added, and anything unclear in the brief.

## Results

| | count |
|---|---:|
| senses `main` / `more` / `hide` | 1,114 / 986 / 3,413 |
| learner definitions (mean 7.2 words) | 2,100 |
| German translations kept / dropped / added | 1,789 / 537 / 1,198 |
| entries without a `main` sense / fully hidden | 448 / 334 (mostly secondary part-of-speech entries and cross-references) |

## Independent check (80 random entries with at least one shown sense)

| measure | result |
|---|---:|
| card better / same / worse than before | 80 % / 20 % / 0 % |
| card good / missing a common sense / wrong order / too much | 90 % / 6.3 % / 3.8 % / 0 % |
| learner definitions correct | 99.6 % (253 of 254) |
| German translations correct (kept + added) | 99.4 % (359 of 361); added 100 % |
| correct translations wrongly dropped | 6 of 65 drops in the sample |

Patterns: frequent informal senses were pushed down; six card slots are too few for the most
versatile verbs; correct but non-preferred translations were sometimes dropped; `order` sometimes put
`more` senses before `main` ones.

## Changes for the next run (instruction version 2)

- Frequent informal or spoken senses belong on the card.
- Up to 8 card senses for very versatile verbs; the limit applies per lemma across parts of speech.
- Drop a translation only if it is wrong for the sense, not if it is a second choice.
- `order`: all card senses first, then `more`.
- Entries whose senses are only cross-references point to the base word instead of being empty.
- Translations allowed on `more` senses; one format (nouns with article, base forms).
- A field to report a common sense that is missing from the source.
