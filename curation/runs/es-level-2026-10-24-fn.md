# Run es-level-2026-10-24-fn (Spanish function words and gaps)

| Field | Value |
|---|---|
| Date | 2026-10-24 |
| Type | `level` (small, one agent) |
| Input | the lemmas among the 3,000 most frequent of the Spanish frequency list that have no row in `curation/levels/es.tsv` in any part of speech and are words a learner needs a level for (participles used as adjectives left out: they take their verb's level) |
| Agent | the developer agent of the Dorothea branch `spanish-quality` (no published level list consulted) |
| Output | 5 rows in `curation/levels/es.tsv` (A1 2, A2 1, B1 2); per-row method in `es-level-2026-10-24-fn.rows.tsv` |

## Why these words had no level

Run `es-level-2026-10-22-a` rated every lemma in its most frequent part of speech when the
dictionary had an entry with that part of speech. The possessives `mi` and `tu` are determiners in
the frequency list and adjectives in the dictionary, `través` exists only inside `a través de`,
`atrever` only as the pronominal `atreverse`, and `web` was left out as a foreign word. Dorothea
applies a determiner's level to the dictionary's adjective (sibling parts of speech), and from
branch `spanish-quality` on a pronominal verb takes its simple verb's level when it has no row of
its own.

## Instruction (own task, same scale as `es-level-2026-10-22-a`)

Rate each lemma with the level descriptions of `es-level-2026-10-22-a` ("at which stage does a
learner of Spanish as a foreign language typically learn and need this word?"), in the part of
speech the dictionary gives it, from own knowledge of Spanish and of how Spanish is taught; core
function words are A1.
