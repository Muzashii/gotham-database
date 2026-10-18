## Entrega: F2 — ETL (Lucius)

- **Status:** pronto para revisão
- **Arquivos alterados:** `etl/run_etl.py`, `etl/extract/{wikidata,comicvine,http}.py`, `etl/transform/modelo.py`,
  `etl/quality/schemas.py`, `etl/graph/centralidade.py`, `data/curated/*.csv` (18 tabelas + `_qualidade.json`),
  `tests/etl/test_etl.py`, `contracts/data-dictionary.md` v0.3, `handoffs/F2-relatorio-qualidade.md`, CI
- **Decisões tomadas (e por quê):**
  - **Wikidata como fonte de obras e relações** (sem chave, CC0): 350 obras via P674 ("personagens"), 179 relações
    tipadas entre os 50 (inimigo, família, mentor, romance, aliado). Comic Vine/TMDB/IGDB pedem chave — a Comic
    Vine ficou implementada e **opcional** (roda se `COMICVINE_API_KEY` existir; a chave nunca vai para o cache).
  - Classificação de mídia pelo rótulo do tipo Wikidata + tipo da série-mãe (episódio de série animada = Animação).
    Obra com vários tipos: Game > Animação > Filme > Série > HQ. Sem data → descartada e contada (63).
  - `IdObra` do Wikidata = QID + 1e9: estável entre execuções e sem colisão com as 48 obras de estreia.
  - Deduplicação seed × Wikidata só com título normalizado **idêntico**, mesma mídia e ano ±1. A 1ª versão
    (substring) casava o filme *Batman* (1989) com a HQ *Batman #436* — corrigido antes da entrega, com teste.
  - Relações de organização: Líder → membro de cada afiliação (evita cliques de 28 vilões dominando a rede).
  - Centralidade em grafo não dirigido ponderado; intermediação usa distância = 1/peso.
  - CSV (e não Parquet) em `data/curated`: diffs legíveis no Git e leitura direta pelo Power Query via URL raw.
  - `--offline` reproduz tudo a partir do cache local (`data/raw/cache`, fora do Git).
- **Contratos afetados:** `data-dictionary.md` v0.3 (seção das tabelas curadas; novas `dMidia` e colunas extras)
- **Como testar:**
  ```bash
  python -m etl.run_etl --offline    # ou sem --offline para baixar (cache em data/raw/cache)
  python -m pytest -q                # 161 testes; tests/etl/test_etl.py valida data/curated sem rede
  ```
- **Gate F2 (plano §12):** pytest verde ✔ · 0 chaves órfãs (23 FKs verificadas) ✔ · taxa de casamento
  reportada em `handoffs/F2-relatorio-qualidade.md` ✔ (Wikidata 100%, SuperHero API 64%, obras P674 86%, Comic Vine não coletado).
- **Pendências / riscos:**
  - Comic Vine sem chave: `EdicoesComicVine` vazio. Precisa de uma chave criada pelo dono do projeto.
  - 7 personagens sem nenhuma obra no Wikidata e 3 sem relação (Pyg, Zatanna, Etrigan).
  - Rótulos das obras vêm em pt quando o Wikidata tem, senão em inglês.
  - Determinismo testado só com cache: com rede, o Wikidata pode mudar entre execuções (é o esperado).

### Ciclo 2 — correções após `handoffs/review-F2.md`
- **B1** relações simétricas (inimigo, romance, família, aliado, rival) agora em forma canônica (menor id → maior id):
  184 → **115** linhas; schema pandera reprova par fora da forma canônica; teste de regressão.
  Hubs corrigidos: Batman (0.839); Asa Noturna (0.076); Oráculo (0.072); Comissário Gordon (0.037); Talia al Ghul (0.037).
- **M1/M2** obras sem rótulo e anteriores à 1ª era agora descartadas **e contadas**; o relatório fecha a conta (teste).
- **M3** filmes com gênero de animação → Animação. SubZero e Mystery of the Batwoman seguem como Filme porque o
  Wikidata não tem nenhum dado de animação nelas (P31 = film, gêneros de ação) — limitação da fonte.
- **M4** títulos em inglês primeiro (o rótulo pt de Q205575 era de outra obra); episódios recebem o nome da série
  ("Smallville — Pilot"); obras futuras (> ano corrente) descartadas e contadas. Curta de fã *Harley* mantido (é obra
  catalogada no Wikidata; filtrar por relevância fica para a F4).
- **M5** "ongoing series" entra como HQ e a data cai para P571 (criação) quando faltam P577/P580: sem data 63 → 59.
- **M6** a tabela de fontes agora diz "QID/id preenchido no seed" para o que é preenchimento e mede cobertura real
  de obras e relações.
- **M7** dicionário atualizado (319 obras, 689 aparições, `EhTransformacao` inteiro, nota de encoding).
  *Os números de 305/681 do ciclo 1 eram de uma execução anterior à correção da deduplicação — erro meu no handoff.*
- **M8** Comic Vine: busca pelo nome civil e depois pelo nome em inglês, só aceita casamento exato e desempata
  apenas dentro do mesmo critério; código 107 (limite por hora) falha na hora em vez de esperar. Ainda **não testado com chave real**.
- **M9** nova coluna `dObra.Granularidade` (Obra/Série/Episódio) para não misturar séries inteiras com episódios nas análises.
- Testes: 173.

### Pós-ciclo 2 (achados N1–N5 de `review-F2.md`)
- **N1** Comic Vine: título com manto compartilhado ("Batman (Terry McGinnis)") passa a buscar pelo nome entre
  parênteses; nome também casa com o nome civil. 3 testes unitários com respostas simuladas.
- **N2** cobertura do Wikidata em relações conta só arestas do Wikidata: 46/50.
- **N4** `aliado` volta a ter direção (P2546 "sidekick of": parceiro → titular): 10 → 11 linhas; schema atualizado.
- **N3** (granularidade inconsistente em HQ, herdada dos tipos do Wikidata) e **N5** (`ano_maximo` = ano corrente
  muda a saída offline na virada do ano) ficam como pendências documentadas.
