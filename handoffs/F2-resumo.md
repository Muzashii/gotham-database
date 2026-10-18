# F2 — Resumo (Alfred)

**Status:** gate F2 **aprovado** pela Coruja no ciclo 2 (`handoffs/review-F2.md`); achados N1, N2 e N4 do ciclo 2
corrigidos em seguida.

## Entregas

| Item | Onde |
|---|---|
| Pipeline `python -m etl.run_etl [--offline]` (extract → transform → quality → graph) | `etl/` |
| 18 tabelas curadas, determinísticas, em CSV UTF-8/LF | `data/curated/` |
| 319 obras (5 mídias, com granularidade Obra/Série/Episódio) e 689 aparições | `dObra`, `fAparicao` |
| Rede de 116 relações tipadas e centralidade (grau, intermediação, PageRank) | `fRelacao`, `dCentralidade` |
| Validação pandera (`strict`) + 23 chaves estrangeiras | `etl/quality/schemas.py` |
| Relatório de qualidade e cobertura das fontes | `handoffs/F2-relatorio-qualidade.md`, `data/curated/_qualidade.json` |
| Comic Vine pronta, opcional (falta chave) | `etl/extract/comicvine.py` |
| Contrato das tabelas curadas | `contracts/data-dictionary.md` v0.3 |

## Gate F2 (plano §12)

| Critério | Resultado |
|---|---|
| pytest verde | ✔ 176 testes |
| 0 chaves órfãs | ✔ 23 FKs verificadas a cada execução (falha interrompe o pipeline) |
| Taxa de casamento entre fontes reportada | ✔ Wikidata: obras 43/50, relações 46/50 · SuperHero API 32/50 · Comic Vine: não coletada (sem chave) |
| Revisão independente | ✔ ciclo 1 reprovado (relações simétricas em dobro), ciclo 2 aprovado |

## Resultado que já dá para mostrar

O **Batman é o hub** da rede (intermediação 0,84), seguido de Asa Noturna, Oráculo, Comissário Gordon e Talia.
Aparições por mídia: Animação 288, HQ 202, Game 137, Filme 41, Série 21.

## Pendências

- **Comic Vine:** criar chave gratuita (só o dono do projeto pode) e colocar em `.env` → `EdicoesComicVine`.
- Granularidade de HQ herdada dos tipos do Wikidata (Action Comics = Obra; Batman = Série) — revisar na F4 (Painel).
- `ano_maximo` = ano corrente: a saída offline muda na virada do ano (obras anunciadas entram).
- SubZero e Mystery of the Batwoman como Filme (Wikidata sem dado de animação).
- **F4a:** a regra de escape do CLAUDE.md (`& < > '`) não cobre barra invertida em strings JS
  (ex.: título "The Darkness\Batman") — decidir na F4a junto com a medida de escape.

## Recomendação para a F3 (Modelo)

Gordon cria as tabelas no TMDL lendo `data/curated/*.csv` via Power Query (`Csv.Document`, `Encoding=65001`,
de preferência pela URL raw do GitHub para permitir atualização no serviço), relações 1:N unidirecionais, tabelas
desconectadas (`Modo`, `VersaoSel`, `RelacaoSel`, `ObraSel`, `TemaSel`) e roda o Best Practice Analyzer.

**Não avançar para a F3 sem aprovação humana.**
