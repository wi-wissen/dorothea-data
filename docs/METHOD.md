# Method

How Dorothea's dictionary data is made: from the sources to the published packs. This document is
the binding description; every curation run is logged in `curation/runs/` with its exact
instructions. It is written for any language pair; German and English are the first.

## 1. Directions

A **direction** is a pair (headword language → explanation language). Monolingual directions use
the same language on both sides.

| Direction | Headwords from | Explanations from |
|---|---|---|
| de → en | English Wiktionary, German entries | English glosses of those entries |
| en → de | English Wiktionary, English entries | English Wiktionary translation tables, reversed de → en glosses, rules from related words (adverbs, comparatives, plurals, spelling variants and synonyms), OdeNet linked to Open English WordNet |
| de → de | German Wiktionary | German definitions |
| en → en | English Wiktionary | English definitions; Open English WordNet for synonyms |

Explanations that do not come from the headword's own Wiktionary entry (reversed glosses, rules
from related words, other open sources) keep their origin in `prov` and are measured before use:
a random sample of the added pairs is judged by an independent agent that sees only the pairs. A
new source or rule is used at 90 % precision or more; below 97 % its translations are shown as
"less certain" (the older reverse lookup, measured at about two in three, is shown that way too).

For a new language X the same table is filled in: headwords from the Wiktionary edition that covers
X best, explanations from the target-language glosses, translation tables and Wikidata lexemes.

## 2. Pipeline

1. **Download** the source extracts (kaikki.org for Wiktionary, the Wikidata lexeme dump, WordNet
   releases). Record source, dump date, download date, size and SHA-256 in `SOURCES.md`. Raw files
   stay outside git.
2. **Import** (program `dorothea-import`): read the extract, keep lemma entries, drop senses that
   only point to another form (form-of/alt-of), map parts of speech, keep gender, IPA, a few display
   forms, short glosses and usage labels. Every field records its source. Output: one JSONL file per
   language in the format of `docs/FORMAT.md`. The import is deterministic: same input, same output.
3. **Lemmatisation** at lookup time: inflected forms, separable verbs and compounds are resolved by
   a morphology component. For German and English this is the morphology of the sister project
   Heinrich, built from its own lexicon and shipped as a separate pack (not part of this data and not
   under CC BY-SA). For a new language without such a component, the form tables of the Wiktionary
   extract are used to build a form → lemma index.
4. **Selection**: the fast-start core of a direction is the N most frequent lemmas (N ≈ 20,000–
   30,000), by a frequency list of running text. The rest is split into small chunks that are loaded
   on demand.
5. **Curation** (section 3) adds and corrects data as an overlay in `curation/`.
6. **Build**: apply the overlay, build the packs, publish entries and packs as release assets with
   the list of source versions they were built from.

## 3. Curation runs (generated data)

Some data is produced by AI agents: unified short glosses, CEFR levels, topics, flags for doubtful
senses and false friends. This data is synthetic and is labelled as such.

Rules for every run:

1. **Fixed brief.** Each run has a written instruction with examples, an input (a batch of entries,
   e.g. one initial letter of one direction) and an output format. The instruction is stored
   verbatim in `curation/runs/<run-id>.md` together with the agent role (bulk agent or review
   agent), the date, the input batch and summary counts.
2. **Overlay only.** Output goes into `curation/levels/` or `curation/edits/` with the run id in
   every line. Imported data is never edited.
3. **Automatic check.** A validator checks the format, allowed values, that every edit hits an
   existing entry and sense, and that glosses do not contradict the source glosses (e.g. a new gloss
   must keep at least one content word of a source gloss or be flagged).
4. **No back-and-forth.** Items the validator rejects or the bulk agent marks as unsure are collected
   once and handed to a review agent; its decisions are a run of their own.
5. **Human spot check.** After each curation round 100 random edited entries are checked by a person;
   the error rate is recorded in the run log.
6. **Provenance.** Every curated value has `src: "cur"` in the entries and points to its run.

### Run types

| Type | Input | Output | Agent |
|---|---|---|---|
| `gloss` | entries of a batch with their source glosses | 1–3 short glosses per sense, in the explanation language | bulk |
| `level` | lemmas of a batch | CEFR level and topics per entry (optionally per sense) | bulk |
| `doubt` | items flagged by validator or bulk agents | decision and corrected value | review |
| `check` | random sample | error rate | person |

### CEFR levels and topics

CEFR levels start from Dorothea's own lists (CC BY 4.0), written by agents per topic area and sorted
into levels by other agents, then compared statistically with public reference lists only to measure
the distance (no list entries were copied). Words without a level get one in `level` runs.

## 4. Applying the method to a new language

1. Fill in the direction table (section 1) and check every source licence (commercial use allowed;
   no NC, no GPL data).
2. Write the import mapping for that Wiktionary edition (parts of speech, gender, form tables).
3. Provide lemmatisation: a morphology component or the form-table index (step 3).
4. Choose a frequency list of running text with a compatible licence.
5. Translate the run briefs; keep the run types, checks and logging unchanged.
6. Build a lookup test set of hand-written sentences for the new language before scaling.
