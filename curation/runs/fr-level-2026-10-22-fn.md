# Run fr-level-2026-10-22-fn (French function words)

| Field | Value |
|---|---|
| Date | 2026-10-22 |
| Type | `level` (small, one agent) |
| Input | the lemmas among the 5,000 most frequent of the French frequency list that have no row in `curation/levels/fr.tsv` in any part of speech and are words a learner needs a level for, plus the multi-word conjunctions and prepositions whose words have no entry of their own |
| Agent | the developer agent of the Dorothea branch `french-quality` (no published level list consulted) |
| Output | 16 rows in `curation/levels/fr.tsv` (A1 5, A2 1, B1 10); per-row method in `fr-level-2026-10-22-fn.rows.tsv` |

## Why these words had no level

Run `fr-level-2026-10-24-a` rated every lemma of the frequency list "in its most frequent part of
speech" as the frequency list tags it, and only when the dictionary had an entry with that part of
speech. The frequency list and the French Wiktionary tag several function words differently
(`ne` adv / part, `donc` conj / adv, `chaque` det / adj, `tel` det / adj, `le mien` pron / adj), so
these lemmas never reached a batch. Dorothea now also applies a lemma's level to its other
function-word parts of speech (determiner, pronoun and adjective; adverb, particle and conjunction)
when the dictionary's differs from the level file's, as the run's own inheritance step intended;
the rows below cover the lemmas that had no row at all.

Left out: `fondé` (only in `fondé de pouvoir`), participles used as adjectives (`reconnu`,
`réuni`, `accepté`, `réparti`: they take their verb's level from the lemma).

## Instruction (own task, same scale as `fr-level-2026-10-24-a`)

Rate each lemma with the level descriptions of `fr-level-2026-10-24-a` ("at which stage does a
learner of French as a foreign language typically learn and need this word?"), in the part of
speech the dictionary gives it, from own knowledge of French and of how French is taught; core
function words are A1.

## Observed while checking

`rien` is rated C1 (pron and noun) in `fr.tsv`; for the pronoun ("nothing") A1 would fit the scale.
Not changed here (a correction belongs to a `doubt` or `check` run).

## Correction (2026-10-22)

`rien` pron C1 → A1 (*ne … rien* is first-weeks vocabulary; the bulk rating followed a rare noun gloss);
`rien` noun C1 → B2 (*un rien*, *en un rien de temps*). Set by the run owner after review.
