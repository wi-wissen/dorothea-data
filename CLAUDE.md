# dorothea-data – Rules for Agents

Public data repository of Dorothea (CC BY-SA 4.0). The program lives in the private repository
`wi-wissen/Dorothea`; read its `docs/PLAN.md` first.

1. **Everything in English:** file names, docs, commit messages, comments. German appears only as
   language data (lemmas, glosses, examples).
2. **Only openly licensed sources** that allow commercial use (CC BY-SA, CC BY, CC0, permissive).
   Never GPL/LGPL/NC data or anything with an unclear licence (e.g. dict.cc, BEOLINGUS, Duden, PONS,
   Langenscheidt, LEO). Record every import in `SOURCES.md` with version, date and checksum.
3. **Provenance per field:** every value keeps the source it came from. Curation changes go into
   `curation/` as an overlay, never by editing imported data, so a new Wiktionary dump keeps them.
4. **No Heinrich data in here.** Heinrich's own lexicon and frequency lists are not published under
   CC BY-SA. Do not copy them, or anything derived from them, into this repository.
5. **No raw dumps in git.** Downloads stay outside the repository; large generated data goes into
   release assets.
6. No AI model identifiers in commits, files or PRs.
