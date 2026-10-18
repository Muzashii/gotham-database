# 🦇 Gotham Database — Batcomputador em Power BI

Relatório Power BI que parece um Batcomputador: ficha de personagens do universo Batman, rede de
relações, linha do tempo, arena de confrontos, quiz e minijogo — tudo renderizado por **medidas DAX
que geram HTML/CSS/SVG/JavaScript** no visual *HTML Content*.

> **Status:** Fase 2 concluída (ETL: 50 personagens, 319 obras, rede de 116 relações). Plano completo em [`docs/plano.md`](docs/plano.md).
>
> 🔗 **[Ver online no Power BI](https://app.powerbi.com/view?r=eyJrIjoiZGFiYTA5YzktMjk4YS00ZmQ5LTk1NGYtMTFlMjllN2E0ZGUyIiwidCI6IjExZGJiZmUyLTg5YjgtNDU0OS1iZTEwLWNlYzM2NGU1OTU1MSIsImMiOjR9)**
> — por enquanto mostra o painel de diagnóstico da F0 (JS rodando no visual, estado na `window`, limite de tamanho).

## Arquitetura (resumo)

```
src/html  (templates com slots)  ┐
src/css   (tokens Gotham Noir)   ├─▶ build/ (Python) ─▶ powerbi/*.SemanticModel (TMDL)
src/js    (apps, sem aspas ")    │      checks.py           powerbi/*.Report (PBIR)
src/dax   (1 arquivo/medida)     ┘      build_preview.py ─▶ dist/preview (harness no navegador)
etl/ ─▶ data/curated ─▶ Power Query                                   (a partir da F2)
```

- **Medidas** em `src/dax/<Nome>.dax`; `TEMPLATE(x.html)` expande um template HTML em concatenação DAX.
- **Templates** em `src/html` usam `[[css:arquivo]]`, `[[js:arquivo]]` e `[[dax:expressão]]`.
- **Estado** dos apps fica em `window.GOTHAM_STATE` e sobrevive ao redesenho do visual.

## Como rodar

```bash
python -m venv .venv
.venv/Scripts/python -m pip install pytest jsonschema pandas pandera networkx scipy
.venv/Scripts/python -m etl.run_etl          # ETL -> data/curated (Wikidata; Comic Vine opcional)
.venv/Scripts/python build/checks.py
.venv/Scripts/python build/build_model.py
.venv/Scripts/python build/build_report.py
.venv/Scripts/python build/build_preview.py
.venv/Scripts/python -m pytest
npm install && npm test   # Vitest (Node 20)
```

Abrir no Power BI: `powerbi/GothamDatabase.pbip` — passo a passo em [`docs/f0-spike.md`](docs/f0-spike.md).

## Time de agentes

Definições em [`.claude/agents/`](.claude/agents), contratos em [`contracts/`](contracts),
entregas e revisões em [`handoffs/`](handoffs). Regras globais em [`CLAUDE.md`](CLAUDE.md).

## Créditos e aviso legal

Projeto pessoal, sem fins comerciais, para estudo e portfólio. Batman e personagens relacionados
pertencem à DC Comics / Warner Bros. Discovery; imagens são referenciadas por URL das fontes, não
redistribuídas. Inspiração: *Pokédex em Power BI*, de Kelven Cardoso. Fontes de dados e atribuições
(SuperHero API, Comic Vine, Wikidata, TMDB, IGDB, DC Database) serão listadas a partir da F1.
