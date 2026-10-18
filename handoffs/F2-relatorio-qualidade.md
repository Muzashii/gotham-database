# F2 — Relatório de qualidade do ETL (gerado por `etl/run_etl.py`)

Gerado em 2026-10-18. Todas as tabelas passaram nos schemas pandera; **0 chaves órfãs** em 23 relações verificadas.

## Contagem por tabela

| Tabela | Linhas |
|---|---|
| `dPersonagem` | 50 |
| `dVersao` | 50 |
| `dEra` | 8 |
| `dMidia` | 5 |
| `dAfiliacao` | 6 |
| `bPersonagemAfiliacao` | 54 |
| `dObra` | 319 |
| `fAparicao` | 689 |
| `fRelacao` | 116 |
| `dArquetipo` | 8 |
| `fMatchup` | 64 |
| `dGolpe` | 24 |
| `bVersaoGolpe` | 200 |
| `dGadget` | 4 |
| `dBairro` | 6 |
| `fEncontro` | 42 |
| `dCentralidade` | 50 |
| `dStat` | 6 |

## Casamento entre fontes (chave canônica = `IdPersonagem` do seed)

| Fonte | Casados |
|---|---|
| Comic Vine | não coletado (sem COMICVINE_API_KEY) |
| Wikidata — QID preenchido no seed | 50/50 (100%) |
| SuperHero API — id preenchido no seed | 32/50 (64%) |
| Wikidata — personagens com obras (P674) | 43/50 (86%) |
| Wikidata — personagens com relações | 46/50 (92%) |

## Obras (Wikidata P674)

- Obras brutas: 350 → descartadas: fora do escopo de mídia 10, sem rótulo 4, sem data 59, futuras 1, anteriores à 1ª era 1 → no modelo 275
- Total em `dObra` (com as 48 obras de estreia, menos as unificadas): 319
- Granularidade: Episódio 86, Obra 172, Série 61
- Duplicadas com obras-seed (unificadas): 4
  - Q1623280 “Batman: Son of the Demon” = obra-seed 6 “Batman: Son of the Demon”
  - Q18245775 “Detective Comics #27” = obra-seed 1 “Detective Comics #27”
  - Q5229132 “Action Comics #1” = obra-seed 46 “Action Comics #1”
  - Q6269708 “Batman: The Animated Series — Joker's Favor” = obra-seed 19 “Batman: The Animated Series — Joker's Favor”
- Aparições por mídia: Animação 288, Filme 41, Game 137, HQ 202, Série 21

## Rede de relações

- Arestas por tipo: aliado 11, família 21, inimigo 40, mentor 14, organização 19, romance 11
- Maiores intermediações (hubs): Batman (0.839); Asa Noturna (0.076); Oráculo (0.072); Comissário Gordon (0.037); Talia al Ghul (0.037)
- Sem nenhuma relação: Professor Pyg, Zatanna, Etrigan
