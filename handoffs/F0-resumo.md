# F0 — Resumo (Alfred)

**Status:** código e build aprovados pela Coruja (`handoffs/review-F0.md`). **O gate F0 ainda não fechou:**
falta ver o spike rodando dentro do Power BI Desktop, que não está instalado nesta máquina.

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

| Medição | Resultado |
|---|---|
| Edição do HTML Content / GUID | _pendente_ |
| JS via script / via onerror | _pendente_ |
| Estado após trocar filtro / trocar página | _pendente_ |
| Maior payload que renderiza bem | _pendente_ |
| Tempo do visual (1 mil / 100 mil / 1 mi) | _pendente_ |

## Recomendação para a F1

1. Fechar o gate F0 com as medições acima. O orçamento de tamanho (`build/budget.json`) e a decisão
   entre `[JS Gotham]` único ou paginado (§15) dependem do limite medido.
2. Em seguida, F1: Oráculo seleciona os 50 primeiros personagens (sprint 1) com coluna `fonte`, e
   Ra's transcreve a matriz §8.2 e os arquétipos para `data/seeds/`. Antes de qualquer ETL, verificar
   os termos e limites de uso das APIs (§4).

**Não avançar para a F1 sem aprovação humana.**
