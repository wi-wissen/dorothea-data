# Sources

Every import is recorded here: source, version or dump date, download date, file name and SHA-256.
Downloads are kept outside the repository.

| Source | Version / dump date | Downloaded | File | SHA-256 |
|---|---|---|---|---|
| English Wiktionary, German entries, via kaikki.org (`kaikki.org-dictionary-German.jsonl`) | extract of 2026-10-03 (Last-Modified) | 2026-10-20 | `kaikki.org-dictionary-German.jsonl` (1,085,014,820 bytes) | `d7ae58be5479ebf607bb9f714e74d796f4df3e8b558478d8e9c7710c55510394` |
| English Wiktionary, English entries, via kaikki.org (`kaikki.org-dictionary-English.jsonl`) | extract of 2026-10-03 (Last-Modified) | 2026-10-20 | `kaikki.org-dictionary-English.jsonl` (3,335,546,346 bytes) | `9978ce34256e4143c3498387564d293a9a2971ef376c1e038d369a2021c02195` |
| German Wiktionary, all entries, via kaikki.org (`de-extract.jsonl.gz`) | extract of 2026-10-03 (Last-Modified) | 2026-10-20 | `de-extract.jsonl.gz` (308,579,949 bytes) | `2e66f18a093e94b29b04733d0222625695a3d5ed199e700059193895490dfb19` |
| English Wiktionary, French entries, via kaikki.org (`kaikki.org-dictionary-French.jsonl`, https://kaikki.org/dictionary/French/; marked deprecated by kaikki.org, still served) | extract of 2026-10-03 (Last-Modified) | 2026-10-21 | `kaikki.org-dictionary-French.jsonl` (583,677,104 bytes) | `829805e271688af4cb7e4430b2c49b7d29f4fe0ce523d6b9c19a8b6c585a25b7` |
| French Wiktionary, all entries, via kaikki.org (`fr-extract.jsonl.gz`, https://kaikki.org/dictionary/downloads/fr/fr-extract.jsonl.gz) | extract of 2026-10-03 (Last-Modified) | 2026-10-21 | `fr-extract.jsonl.gz` (736,590,407 bytes) | `f3fc5417d1759188ecfd74df90cbf231b28306b150970ea89614cb8cb4668f32` |
| English Wiktionary, Spanish entries, via kaikki.org (`kaikki.org-dictionary-Spanish.jsonl`, https://kaikki.org/dictionary/Spanish/; marked deprecated by kaikki.org, still served; stored gzipped as `en-Spanish.jsonl.gz`, 81,441,448 bytes, SHA-256 `d480a9199d54e2150c576f9b87324630e0960b7c64f91952ef9c93eb0e2ebde0`) | extract of 2026-10-03 (Last-Modified) | 2026-10-22 | `kaikki.org-dictionary-Spanish.jsonl` (1,054,565,723 bytes) | `7b23a5dc004a47b63edc2e79a34b246bbf59d1a3067a1843a5c554c0e252b97c` |
| Spanish Wiktionary, all entries, via kaikki.org (`es-extract.jsonl.gz`, https://kaikki.org/dictionary/downloads/es/es-extract.jsonl.gz) | extract of 2026-10-03 (Last-Modified) | 2026-10-22 | `es-extract.jsonl.gz` (103,226,106 bytes) | `fb5b5b8520912d1d1a398f2b8bf2569c11911b4c26bad6b8c066a84f5e3d34ed` |
| English Wiktionary, Latin entries, via kaikki.org (`kaikki.org-dictionary-Latin.jsonl.gz`, https://kaikki.org/dictionary/Latin/) | extract of 2026-10-21 (Last-Modified) | 2026-10-24 | `kaikki.org-dictionary-Latin.jsonl.gz` (110,190,443 bytes) | `71a71ba140868e1a64d23b4f38a84be18affab9a12fbd4fbe6076a4882b0c9bc` |
| OdeNet (Open German WordNet), `odenet_oneline.xml` of https://github.com/hdaSprachtechnologie/odenet, CC BY-SA 4.0 | version 1.3, commit `8ba741223048c28f67d4c38560ea4c0ee89568bb` (2026-01-07) | 2026-10-21 | `odenet_oneline.xml` (24,404,316 bytes) | `ff2bd92b8758c36e80477393e220675edf4062d13e6c8f8e3eb84b9df569df83` |
| Open English WordNet, https://github.com/globalwordnet/english-wordnet, CC BY 4.0 | 2025 edition (release `2025-edition`) | 2026-10-21 | `english-wordnet-2025.xml.gz` (11,363,503 bytes) | `9ca6d1dcb75f822fdd66617f7d9da48142ace38dd544d6ad5e2feca1674ad3fe` |
| Wikidata lexemes, https://dumps.wikimedia.org/wikidatawiki/entities/, CC0 1.0 (evaluated, not used by the default build) | `latest-lexemes.json.gz`, Last-Modified 2026-10-21 03:55 UTC | 2026-10-21 | `latest-lexemes.json.gz` (655,273,999 bytes) | `85ebe293f2357f69776fd06edc4fb4c23f26403f3489b8ff9e1014322dc3f4c2` |

## Licence notes

- **OdeNet** (CC BY-SA 4.0, stated in the repository's `LICENSE`, `README.md` and the lexicon's
  `license` attribute; the Python code is MIT and not used) and **Open English WordNet**
  (CC BY 4.0, the lexicon's `license` attribute) allow commercial use. Only English–German pairs
  derived from them go into the en → de data, which is CC BY-SA 4.0 like the rest; the packs and
  the website name both. Credit: "OdeNet, Melanie Siegel and Francis Bond (2021), CC BY-SA 4.0;
  Open English WordNet, CC BY 4.0".
- **Wikidata** lexemes are CC0 1.0 (no conditions). Their English–German pairs reached 88 %
  precision in two independent samples, below the 90 % aim, so the build does not use them
  (`WIKIDATA=<dump>` adds them).
- Nothing from these sources, and nothing derived from them, goes into Heinrich or
  heinrich-data.
- **French** (2026-10-21): the French directions (fr–fr, fr → de, de → fr, fr → en, en → fr)
  use the French Wiktionary extract (French entries with their German and English
  translations; German entries with French definitions), the French entries of the English
  Wiktionary, the French entries and the French translation tables of the German Wiktionary
  (`de-extract.jsonl.gz` above) and the French translation tables of the English Wiktionary
  (`kaikki.org-dictionary-English.jsonl` above). All CC BY-SA 4.0, like the other Wiktionary
  data.
- **Spanish** (2026-10-22): the Spanish directions (es–es, es → de, de → es, es → en, en → es)
  use the Spanish Wiktionary extract (Spanish entries with their German and English
  translations; German entries with Spanish definitions), the Spanish entries of the English
  Wiktionary, the Spanish entries and the Spanish translation tables of the German Wiktionary
  (`de-extract.jsonl.gz` above) and the Spanish translation tables of the English Wiktionary
  (`kaikki.org-dictionary-English.jsonl` above). All CC BY-SA 4.0, like the other Wiktionary
  data. German translations reached through English for Spanish words without German
  (`pivot`) come from the same English Wiktionary data.
- **Latin** (2026-10-24): the Latin directions (la → de, la → en) use the Latin entries of the
  English Wiktionary (above) and of the German Wiktionary (`de-extract.jsonl.gz` above). Levels
  (`curation/levels/la.tsv`) are school stages, see `curation/runs/la-level-2026-10-24-a.md`.

## Real-text development set (`testing/realtext/`)

Passages of human-written text for measuring coverage; not imported into the dictionary. The
revision, URL, licence and attribution of every passage are in `testing/realtext/passages.tsv`.

| Source | Version / dump date | Downloaded | File | SHA-256 |
|---|---|---|---|---|
| German and English Wikipedia, Simple English Wikipedia, Klexikon, MiniKlexikon (CC BY-SA 4.0) | page revision per passage (`oldid` in `passages.tsv`) | 2026-10-21 | MediaWiki API `action=parse`, one page per passage | – (the revision id fixes the version) |
| German Wikinews (CC BY 2.5), English Wikinews (CC BY 2.5 / CC BY 4.0 by publication date) | page revision per passage (`oldid` in `passages.tsv`) | 2026-10-21 | MediaWiki API `action=parse`, one page per passage | – (the revision id fixes the version) |
| Tatoeba, German sentences (`deu_sentences_detailed.tsv.bz2`) | weekly export | 2026-10-20 | `deu_sentences_detailed.tsv.bz2` (17,679,592 bytes) | `224edaef9c1fd23587bcaaf77d8c79d8a33b32deba90062b9c8e026706ea4934` |
| Tatoeba, English sentences (`eng_sentences_detailed.tsv.bz2`) | weekly export | 2026-10-20 | `eng_sentences_detailed.tsv.bz2` (34,943,159 bytes) | `24f742143d9079308d8c6b9c8cb4f6efb54e908a37d27fd5e40f22ab841b3d0d` |
| Tatoeba, user language skills (`user_languages.tar.bz2`) | weekly export | 2026-10-20 | `user_languages.tar.bz2` (833,908 bytes) | `4ab949dde556d74f6bcc50ae50d91e786d21da83c695f55f3a4f0446968da3d3` |
| Tatoeba, list of CC0 sentences (`sentences_CC0.tar.bz2`) | weekly export | 2026-10-20 | `sentences_CC0.tar.bz2` (7,962,216 bytes) | `371638b7658899418ebd64d183f11a118edbe63e57fc60358036f2cec120d4d7` |
| Project Gutenberg eBook #77905 (public domain) | plain-text edition | 2026-10-21 | `pg77905.txt` (562,382 bytes) | `3cc443c1f71bc23a6a33f566b8de3dca7c49604d81be1696d1aef5137c579e3f` |
| Project Gutenberg eBook #6638 (public domain) | plain-text edition | 2026-10-20 | `pg6638.txt` (283,592 bytes) | `0d585c02732f1efcf4fac238e647ec95ab7efd59438e0bbefae04eed5fbbcdb4` |
| Project Gutenberg eBook #5323 (public domain) | plain-text edition | 2026-10-20 | `pg5323.txt` (633,751 bytes) | `15a93db448403b07093042b6aa251ab22474ad9c05918e69f7ead5c62c0b2e8e` |
| Project Gutenberg eBook #74008 (public domain) | plain-text edition | 2026-10-21 | `pg74008.txt` (265,480 bytes) | `464e776735b91a336d40fa2b96e6b9f88d20e20bbdadc59e3290cfc127e97907` |
| Project Gutenberg eBook #22367 (public domain) | plain-text edition | 2026-10-20 | `pg22367.txt` (145,983 bytes) | `359d3f5983c812393f4bd7ee49a350ffffc7d476015e58d6b84b6c848dd2b0e9` |
| Project Gutenberg eBook #35312 (public domain) | plain-text edition | 2026-10-21 | `pg35312.txt` (217,691 bytes) | `de657654648ca6f8dcda1ce2a289b5f9376e7f67c3f6a30eb241c2fcd51fbd25` |
| Project Gutenberg eBook #2591 (public domain) | plain-text edition | 2026-10-20 | `pg2591.txt` (560,164 bytes) | `377ebb8ca06cd8bc0b1015ddb54766c44f50dece731c53bb030f1cc00f54092a` |
| Project Gutenberg eBook #902 (public domain) | plain-text edition | 2026-10-20 | `pg902.txt` (112,604 bytes) | `77ae1b3c7be77aea82b1f935e531e53f4df43db572cbc14af39d6cd0d5ba50da` |
| Project Gutenberg eBook #1342 (public domain) | plain-text edition | 2026-10-20 | `pg1342.txt` (772,386 bytes) | `3f6bb9d6f78e0293b56acd4714dd68cb7d6d1d293402031ce9d5a216bcaf9d75` |
| Project Gutenberg eBook #1661 (public domain) | plain-text edition | 2026-10-20 | `pg1661.txt` (607,606 bytes) | `922e2a12ccb43a4c9544c260b2166c6ad2097aeb5957faeee113f173bb857cd0` |
| Project Gutenberg eBook #74 (public domain) | plain-text edition | 2026-10-20 | `pg74.txt` (434,357 bytes) | `74d77384b123a6360db9ab58463cff8b38df8525fbdc6000c81ee388e1f3cf10` |
| Project Gutenberg eBook #215 (public domain) | plain-text edition | 2026-10-20 | `pg215.txt` (199,757 bytes) | `30f569c5671bba7bbc4a92ab6d8ee01a0d3be00f994819c77da62c28041eb8a2` |
| Spanish Wikipedia (CC BY-SA 4.0) | page revision per passage (`oldid` in `passages.tsv`) | 2026-10-22 | MediaWiki API `action=parse`, one page per passage | – (the revision id fixes the version) |
| Tatoeba, Spanish sentences (`spa_sentences_detailed.tsv.bz2`) | weekly export | 2026-10-22 | `spa_sentences_detailed.tsv.bz2` (9,511,792 bytes) | `1c1a471125889fee14c4ad1cbb85edb45e5160d56a4c933136433c6b67b5f48d` |
| Tatoeba, user language skills and CC0 list (`user_languages.tar.bz2`, `sentences_CC0.tar.bz2`, extracted on download) | weekly export | 2026-10-22 | `user_languages.csv` (2,425,571 bytes), `sentences_CC0.csv` (41,861,135 bytes) | `8770cd3ae712fd791fc9370f98f6b17abb6d05d151cc5e5b67fe0494163b9376`, `92311f0c5644b703c04b7834f19bcded848c91bdcfb39c387f01024bd23b115c` |
| Project Gutenberg eBook #15725 (public domain) | plain-text edition | 2026-10-22 | `pg15725.txt` (814,730 bytes) | `876c07627e3cca60c43f838fe38644d525b44b425c55bebcf3e0b3a9d7b29ed3` |
| Project Gutenberg eBook #17073 (public domain) | plain-text edition | 2026-10-22 | `pg17073.txt` (1,889,429 bytes) | `29cd4c40b2a89cf643f7b3f3a53f8bbef1e67b9be204333bcb9a4dd50b61e86f` |
| Project Gutenberg eBook #17223 (public domain) | plain-text edition | 2026-10-22 | `pg17223.txt` (346,924 bytes) | `5ac6722b1de675f7e7f9d64ed03dc5ed34565f46c86c769d6062cddf3c0ecdd4` |
| Project Gutenberg eBook #18005 (public domain) | plain-text edition | 2026-10-22 | `pg18005.txt` (535,176 bytes) | `c42f30054c6389bcbb4a3a77de391571837f882ab198d77735551da726150450` |
| Project Gutenberg eBook #53552 (public domain) | plain-text edition | 2026-10-22 | `pg53552.txt` (598,876 bytes) | `db72bf4d6335251432311789e9fcb5aa4f4217a35731818b9e4ed2b0850a3685` |
