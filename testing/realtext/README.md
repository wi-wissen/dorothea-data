# Real-text development set

About 60 passages of text **written by people**, half German and half English, for measuring how
well Dorothea covers real reading material: how many words it finds, how many get a CEFR level,
which words it misses.

**This is a development set.** Unlike the held-out sets in the private `dorothea-eval` repository,
it may be read, inspected and used for tuning lookup, import, curation and levels. Its purpose is an
independent signal: the hand-written development sentences elsewhere were written by AI agents,
which share blind spots with the agents that write the rules. Because it is open for tuning, its
numbers will drift upward over time; confirm real progress on the held-out sets.

## Files

| File | Content |
|---|---|
| `passages.tsv` | one row per passage: `id`, `lang`, `genre`, `topic`, `source`, `title`, `url` (permalink of the exact revision or eBook), `licence`, `attribution`, `retrieved` (download date), `words` (whitespace-separated tokens) |
| `passages/<id>.txt` | the passage, UTF-8, paragraphs separated by a blank line (Tatoeba: one sentence per line) |
| `attribution/<id>.tsv` | Tatoeba only: sentence id, author (username), licence and URL of every sentence |
| `check.py` | validator (Python 3, standard library only) |
| `measure.py` | runs `dorothea analyze --json` over every passage and reports coverage and name recognition |
| `names.tsv` | the names in each passage (gold annotation for the name metric, see below) |

## Composition

| Source | Genre | de | en | Licence |
|---|---|--:|--:|---|
| Wikipedia (12 topics) | `encyclopedia` | 12 | 12 | CC BY-SA 4.0 |
| Klexikon / MiniKlexikon; Simple English Wikipedia | `encyclopedia-simple` | 4 + 2 | 6 | CC BY-SA 4.0 |
| Wikinews | `news` | 4 | 4 | CC BY 2.5 (all eight articles predate the English switch to CC BY 4.0) |
| Project Gutenberg, 19th/early 20th century prose | `literature` | 4 | 4 | public domain |
| Project Gutenberg, fairy tales | `fairy-tale` | 2 | 2 | public domain |
| Tatoeba, short everyday sentences (~300 words per block) | `everyday` | 2 | 2 | CC BY 2.0 FR (a few CC0 1.0) |

Topics of the Wikipedia passages (one article each, per language): history, biography, geography,
science, technology, sport, culture, politics, biology, economy, medicine, food.

## Selection rule

Passages were chosen mechanically, not by reading candidates. Every random choice uses Python's
`random.Random("realtext-v1:<passage id>")`, so the choice is reproducible from the same inputs.

- **Wikipedia** (`<lang>-wp-<topic>`): all articles that are direct members of one category per
  topic (German: Friedensvertrag, Maler (Deutschland), Insel (Europa), Chemisches Element,
  Haushaltsgerät, Ballsportart, Musikinstrument, Wahlsystem, Raubtiere, Wirtschaftsgeschichte,
  Infektionskrankheit, Deutsche Küche; English: Battles of the Hundred Years' War, 19th-century
  American painters, Islands of Greece, Chemical elements, Home appliances, Ball games, String
  instruments, Electoral systems, Birds of Europe, Banking terms, Viral diseases, Breads), sorted by
  title and shuffled with the seed; list articles are skipped. The passage is the **first section
  after the lead**: the prose paragraphs from the first level-2 heading on, continuing into the
  following sections only when the first one is shorter than 200 words. If an article has fewer
  than 200 words after the lead, the next article in the shuffled order is taken.
- **Simple English Wikipedia** (`en-simple-<topic>`): the same with the categories Mammals, Sports,
  Musical instruments, Birds, Mountains and Chemical elements, but from the **start of the
  article** (lead included), because these articles are short.
- **Klexikon, MiniKlexikon** (`de-klexikon-<n>`, `de-miniklexikon-<n>`): all articles of the wiki
  (non-redirects, sorted, shuffled with the seed), from the start of the article.
- **Wikinews** (`<lang>-news-<…>`): German: four articles from *Kategorie:Veröffentlicht*; English:
  one article each from *Politics and conflicts*, *Science and technology*, *Sports*, *Culture and
  entertainment*; from the start of the article (dateline included).
- **Project Gutenberg** (`<lang>-lit-<author>`): a fixed list of well-known public-domain works
  (German: Grimm, Hauff, Fontane, Storm, Kafka, Eichendorff; English: Grimm in the
  Taylor/Edwardes translation, Wilde, Austen, Doyle, Twain, London). A position is drawn uniformly
  between 20 % and 80 % of the book; the passage starts at the next prose paragraph and runs
  through consecutive paragraphs (a heading or a verse line ends it). The old spelling of the
  editions (e.g. *muß*) is kept: real readers meet it.
- **Tatoeba** (`<lang>-tatoeba-<n>`): sentences of 5 to 15 words whose owner states native
  proficiency (level 5 of 5) in the language, shuffled with the seed and taken in order until a
  block reaches 300 words; block 2 continues where block 1 stopped.

Length: whole paragraphs are taken while the passage stays at most 400 words; a passage still under
200 words is filled with whole sentences of the next paragraph. Wiki text is extracted from the
rendered page: only `<p>` paragraphs, without tables, infoboxes, image captions, lists, footnote
markers and formulas. The Wikipedia article on Klaus Störtebeker is excluded (already used
elsewhere).

## Licences and attribution

Every row of `passages.tsv` names its licence and how to attribute it:

- **Wikipedia, Simple English Wikipedia, Klexikon, MiniKlexikon** — CC BY-SA 4.0. Authors: the
  contributors listed in the page history linked in the `attribution` column; the `url` column is
  the permalink to the revision used. Changes: extracted plain text of one section, shortened.
- **Wikinews** — CC BY 2.5 (German; English before 2024-12-16) or CC BY 4.0 (English from
  2024-12-16; decided by the page's first revision). Attribution: "Wikinews" with the page link.
- **Project Gutenberg** — the texts are in the public domain (authors died before 1956). The Project
  Gutenberg licence header and footer are removed, as the Project Gutenberg licence permits for
  public-domain texts; the trademark "Project Gutenberg" is used only to name the source.
- **Tatoeba** — CC BY 2.0 FR, some sentences CC0 1.0. Each sentence's author and link is listed in
  `attribution/<id>.tsv`.

All of these allow commercial use and redistribution and are compatible with this repository's
CC BY-SA 4.0 licence.

## How to run

```sh
python3 testing/realtext/check.py      # validate the files
python3 testing/realtext/measure.py    # coverage report
python3 testing/realtext/measure.py --lang de --markdown
python3 testing/realtext/measure.py --cli path/to/dorothea --packs path/to/packs --out /tmp/realtext-out
```

`measure.py` expects the `dorothea` CLI and a pack directory with `de-morph.pack`,
`de-en/core.pack` + chunks, `freq-de.pack`, `en-morph.pack`, `en-de/core.pack` + chunks and
`freq-en.pack`. German passages are analysed with the German→English packs, English passages with
the English→German packs. Every word token the analyser returns falls into one bucket:

| Bucket | Meaning |
|---|---|
| level | found, card with a gloss and a CEFR level |
| no level | found, card with a gloss but no CEFR level |
| part-gloss | compound without an entry of its own (`how=compound`, no key): only its parts are glossed |
| base-gloss | no entry of its own, but a gloss borrowed from a base word (`how=derived`, `separable`, …) |
| empty | recognised (lemma known) but the card has no gloss |
| not found | no lemma, no gloss |
| other | anything else (should stay 0) |

The output folder (default `/home/user/dorothea-build/realtext-out/`, keep it outside git) gets
`per-passage.tsv`, `not-found-<lang>.tsv`, `no-level-<lang>.tsv`, `base-gloss-<lang>.tsv` and
`empty-<lang>.tsv` with counts.

### Names

`names.tsv` lists, per passage, the word tokens that are names: `id`, `kind`, `tokens`
(space-separated, as the analyser tokenises them; every occurrence of the token in that passage
counts). Kinds: `person`, `place`, `org` (organisations, companies, bands), `other` (works,
ships, games, religions named like a name) and `part`. `part` marks ordinary words inside a name
(`Federal` and `List` in a list's title, `University`, `River`, `Street`, the `SPD`), title-case
words and abbreviations of organisations: they count neither as a name nor as a false alarm.
Not names: demonyms and language names (*Indian*, *Japanese*, *Latein*), months, weekdays,
feasts, titles (*Mr*, *Herr*, *Rev.*), and nouns used as nouns (*der Bauer*). A token whose
analysis has `name: true` is marked; `measure.py` reports per language:

- **recall**: marked tokens among the tokens of kind person, place, org or other;
- **false alarms**: marked tokens that `names.tsv` does not list at all;
- **precision**: recall hits / (hits + false alarms).

A possessive or genitive ending (`Tom's`, `Huangs` is listed itself) and a final full stop
are stripped before the lookup in `names.tsv`. `names-missed-<lang>.tsv` and
`names-false-<lang>.tsv` in the output folder list the errors. The annotation was made by one
annotator reading every passage; doubtful cases went to `part`.

## Baseline

Dorothea at `main` abad93d, packs `packs-v9`, 2026-10-21. Shares of word tokens:

| group | tokens | level | no level | part-gloss | base-gloss | empty | not found | other |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| all | 18999 | 16451 (86.6%) | 1417 (7.5%) | 319 (1.7%) | 6 (0.0%) | 75 (0.4%) | 731 (3.8%) | 0 (0.0%) |
| de | 9351 | 8003 (85.6%) | 744 (8.0%) | 290 (3.1%) | 6 (0.1%) | 31 (0.3%) | 277 (3.0%) | 0 (0.0%) |
| de/encyclopedia | 3680 | 2908 (79.0%) | 388 (10.5%) | 197 (5.4%) | 2 (0.1%) | 10 (0.3%) | 175 (4.8%) | 0 (0.0%) |
| de/encyclopedia-simple | 1737 | 1561 (89.9%) | 116 (6.7%) | 34 (2.0%) | 1 (0.1%) | 7 (0.4%) | 18 (1.0%) | 0 (0.0%) |
| de/everyday | 606 | 555 (91.6%) | 44 (7.3%) | 1 (0.2%) | 0 (0.0%) | 1 (0.2%) | 5 (0.8%) | 0 (0.0%) |
| de/fairy-tale | 710 | 671 (94.5%) | 28 (3.9%) | 2 (0.3%) | 1 (0.1%) | 4 (0.6%) | 4 (0.6%) | 0 (0.0%) |
| de/literature | 1466 | 1323 (90.2%) | 80 (5.5%) | 22 (1.5%) | 2 (0.1%) | 7 (0.5%) | 32 (2.2%) | 0 (0.0%) |
| de/news | 1152 | 985 (85.5%) | 88 (7.6%) | 34 (3.0%) | 0 (0.0%) | 2 (0.2%) | 43 (3.7%) | 0 (0.0%) |
| en | 9648 | 8448 (87.6%) | 673 (7.0%) | 29 (0.3%) | 0 (0.0%) | 44 (0.5%) | 454 (4.7%) | 0 (0.0%) |
| en/encyclopedia | 3980 | 3351 (84.2%) | 325 (8.2%) | 14 (0.4%) | 0 (0.0%) | 16 (0.4%) | 274 (6.9%) | 0 (0.0%) |
| en/encyclopedia-simple | 2003 | 1811 (90.4%) | 121 (6.0%) | 6 (0.3%) | 0 (0.0%) | 8 (0.4%) | 57 (2.8%) | 0 (0.0%) |
| en/everyday | 600 | 561 (93.5%) | 24 (4.0%) | 0 (0.0%) | 0 (0.0%) | 4 (0.7%) | 11 (1.8%) | 0 (0.0%) |
| en/fairy-tale | 711 | 652 (91.7%) | 45 (6.3%) | 1 (0.1%) | 0 (0.0%) | 3 (0.4%) | 10 (1.4%) | 0 (0.0%) |
| en/literature | 1049 | 969 (92.4%) | 52 (5.0%) | 3 (0.3%) | 0 (0.0%) | 9 (0.9%) | 16 (1.5%) | 0 (0.0%) |
| en/news | 1305 | 1104 (84.6%) | 106 (8.1%) | 5 (0.4%) | 0 (0.0%) | 4 (0.3%) | 86 (6.6%) | 0 (0.0%) |

Proper nouns (`pos=propn`) make up 197 of the German and 169 of the English no-level tokens.

What stands out (described with our own examples, not as a to-do list):

- **German compounds** are the largest German gap after missing levels: 3.1 % of tokens get only the
  glosses of their parts, 5.4 % in encyclopedia text (law and science compounds such as *Sicherheitsstufe*,
  *Verhältniswahlrecht*, *Gentechnikgesetz*).
- **Not found** is dominated by names (people, places), abbreviations (*GenTSV*, *IUPAC*, *EAD*),
  foreign words inside the text (English *of* in German text, Italian *da* in English text),
  decade forms (*1950er*), unit symbols (*cm*, *km*) and chemistry notation with mass numbers.
  English plurals of technical nouns (*monotremes*, *lanthanides*, *breadcrumbs*) are not found.
- **No level** hits frequent everyday compounds and phrasal verbs that have entries but no level
  (*find out*, *world record*, *gold medal*, *Landtagswahl*, *Kinderkrankheit*) and a few function
  words (*all* as pronoun, *die* as determiner).
- **Base-gloss** is rare but can mislead: a negated derivation can show the gloss of its base
  without the negation (an *un-* adjective glossed like the positive word).
- Old spellings in 19th-century prose (*muß*) are handled: literature and fairy
  tales have the best German coverage.

Names (added 2026-10-21; Dorothea `main` 9013317, packs `packs-v11`): German 308 of 380 name
tokens marked (recall 81.1 %), 42 false alarms (precision 88.0 %); English 281 of 413 (68.0 %),
52 false alarms (84.4 %).

## Changes

- 2026-10-21: first version, 60 passages.
- 2026-10-21: `names.tsv` (names in every passage) and the name metric in `measure.py` (recall,
  false alarms, precision); `measure.py` passes the name list packs (`names-*.pack`) of the pack
  directory to the CLI.
