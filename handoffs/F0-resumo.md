# F0 — Resumo (Alfred)

**Status:** código e build aprovados pela Coruja (`handoffs/review-F0.md`); spike validado no Power BI
Desktop e publicado na web em 18/10/2026 (resultados abaixo). **Gate F0 aprovado.**

## O que foi feito

| Item | Onde |
|---|---|
| Estrutura do repositório (§10), `CLAUDE.md`, 10 agentes (§13) | raiz, `.claude/agents/` |
| Contratos v0.1: dicionário, schema JS, tokens, catálogo de medidas | `contracts/` |
| Spike: HTML + CSS (chuva) + JS (holofote em canvas, contador em `window.GOTHAM_STATE`) | `src/html/spike.html`, `src/css`, `src/js/spike.js` |
| 6 medidas DAX (`99 Spike`), incluindo payload variável para medir o limite de tamanho | `src/dax/` |
| Build: templates → DAX → TMDL; PBIR + tema Gotham Noir; preview no navegador | `build/` |
| `checks.py`: aspas duplas, ```, slots, tokens, orçamento por medida | `build/checks.py` |
| Projeto PBIP (TMDL + PBIR) | `powerbi/` |
| 41 testes pytest (incluindo validação dos JSON PBIR nos schemas oficiais e contraste AA) | `tests/build/` |
| Testes Vitest do spike (6) | `tests/js/` |
| CI (checks, sincronia do TMDL, pytest, Vitest) | `.github/workflows/ci.yml` |

## Verificado

- `checks.py` APROVADO; `pytest` 41/41.
- Harness no navegador (`dist/preview/spike.html`): JS executa pelos dois caminhos (`<script>` e o
  `<img onerror>` de reserva); o contador sobrevive ao redesenho com e sem execução de script; console sem erros.
- JSON do PBIR, `.pbip` e `.pbism` validam nos schemas oficiais da Microsoft.

## Achados da revisão (todos MENORES) e o que foi feito

| # | Achado | Ação |
|---|---|---|
| 1 | `compactar` fundia texto/comentário com slots `[[dax:]]` | Corrigido + teste de regressão |
| 2 | Compactação altera template literals multilinha / `<pre>` | Documentado na docstring (usar `\n` explícito) |
| 3 | `literal_dax` podia dividir `""` entre pedaços | Corrigido (quebra antes de escapar) + teste |
| 4 | `checks.py`: glob não recursivo, tokens fora de `tokens.css`, slot desconhecido, ``` em `.dax` | Corrigidos + 3 testes |
| 5 | Teste Vitest de estado era tautológico | Reescrito com DOM falso mínimo |
| 6 | Dicionário citava coluna `Ordem` inexistente | Corrigido |
| 7 | `onerror` sem proteção contra `gd-src` nulo | Corrigido; recriação assíncrona de `<script>` segue como suspeita |

## Não verificado (bloqueia o fechamento do gate)

- Abertura do `.pbip` no Desktop (TMDL não tem validador offline).
- Se a edição do HTML Content usada executa `<script>`, `onerror` e `new Function` (CSP).
- Limite prático de tamanho de string (slicer até 5 milhões de caracteres) e tempo no Analisador de desempenho.
- Vitest (sem Node aqui; roda no CI).

→ Roteiro de 10 minutos em `docs/f0-spike.md`. Os resultados devem ser preenchidos aqui:

**Medido em 18/10/2026** — Power BI Desktop 2.159.883.0 (Microsoft Store) e Power BI Service:

| Medição | Resultado |
|---|---|
| Abertura do PBIP (TMDL + PBIR gerados pelo build) | ✔ abriu sem erro; Desktop só reformatou (CRLF, `lineageTag`, compat. 1606, report schema 3.3.0) |
| Edição do HTML Content / GUID | *HTML Content* padrão (Daniel Marsh-Patrick) — `htmlContent443BE3AD55E043BF878BED274D3A6855` |
| JS via script / via onerror | ✔ / ✔ (Desktop **e** Service **e** Publicar na Web) |
| Estado após trocar o filtro | ✔ contador 3 → 3 após 1 mil → 100 mil → 1 milhão (renderizações 2 → 3 → 4) |
| Estado após erro do visual | ✖ o visual é recriado e `window.GOTHAM_STATE` zera — apps devem tolerar perda de estado |
| Troca de página | não testado (relatório tem 1 página) — testar na F5 |
| Maior payload que renderiza bem | **1.000.000 chars ✔**; 5.000.000 ✖ (“Failed to move the data reader to the next row”) |
| Tempo do visual | não medido com o Analisador de desempenho; 1 milhão respondeu em poucos segundos (observação visual) |
| Publicar na Web | ✔ link público funcionando (ver README) |

**Gate F0: APROVADO** (exceto troca de página e tempo formal, que passam para os gates F4a/F5).

Consequências para o projeto:
- Orçamento: `[JS Gotham]` único é viável — 250 personagens × ~200 chars ≈ 50 mil, 20× abaixo do limite.
  Manter teto de 500 mil por medida no `budget.json` como margem de segurança.
- Fluxo PBIP: depois de salvar no Desktop, rodar `build/build_model.py` (o Desktop regrava `_Medidas.tmdl`).

## Recomendação para a F1

1. ~~Fechar o gate F0~~ feito: `[JS Gotham]` único (não paginado).
2. F1: Oráculo seleciona os 50 primeiros personagens (sprint 1) com coluna `fonte`, e
   Ra's transcreve a matriz §8.2 e os arquétipos para `data/seeds/`. Antes de qualquer ETL, verificar
   os termos e limites de uso das APIs (§4).

**Não avançar para a F1 sem aprovação humana.**
