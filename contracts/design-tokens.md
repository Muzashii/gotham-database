# Design tokens — Gotham Noir

- **Dono:** designer-ui (Selina) · **Consumidores:** engenheiro-dax, dev-js-apps
- **Versão:** 0.1 (F0). Fonte única: `src/css/tokens.css` (o build reprova `var(--x)` sem token definido).

## Cores

| Token | Valor | Uso |
|---|---|---|
| `--g-bg` | `#07090c` | Fundo (noite de Gotham) |
| `--g-panel` | `#10141a` | Cards e painéis |
| `--g-line` | `#1f2a36` | Bordas, grades |
| `--g-text` | `#d7dde4` | Texto principal (14,6:1 sobre `--g-bg`, 13,5:1 sobre `--g-panel`) |
| `--g-muted` | `#7d8794` | Texto secundário (5,5:1 / 5,1:1) |
| `--bat-yellow` | `#f5c518` | Destaque, página ativa, Bat-sinal |
| `--arkham-green` | `#39d98a` | Arkham, Charada, sucesso |
| `--joker-purple` | `#7b2cbf` | Coringa (só fundo/borda — contraste baixo como texto) |
| `--blood` | `#c1121f` | Dano, alerta (só fundo/borda) |
| `--ice` | `#8ecae6` | Sr. Frio |
| `--ivy` | `#2d6a4f` | Hera Venenosa (só fundo/borda) |
| `--owl-bronze` | `#a47148` | Corte das Corujas (texto só ≥ 18px: 4,4:1 sobre `--g-panel`) |

## Tipografia

| Token | Pilha |
|---|---|
| `--font-ui` | Rajdhani, Barlow Condensed, Arial Narrow, sans-serif |
| `--font-mono` | JetBrains Mono, Consolas, monospace (telas do Batcomputador) |
| `--font-title` | Bebas Neue, Impact, sans-serif |

O visual HTML Content roda em sandbox e pode bloquear fontes externas: toda pilha termina em fonte do sistema.

## Movimento

| Token | Valor |
|---|---|
| `--t-fast` | `150ms` |
| `--t-med` | `300ms` (glitch entre versões) |

Contrastes verificados em `tests/build/test_pbip.py` (AA ≥ 4,5:1 para texto).

Toda animação usa só `transform`/`opacity` e é desligada em `@media (prefers-reduced-motion: reduce)`.

## Classes por facção (planejadas, F4b)

`fx-gotham` (chuva, padrão) · `fx-coringa` · `fx-espantalho` · `fx-frio` · `fx-hera` · `fx-charada` ·
`fx-duascaras` · `fx-corujas` · `fx-batfamilia` · `fx-vagalume` — ver `docs/plano.md` §9.2.

Prefixos de classe: `gd-` (componentes compartilhados), `fx-` (tema de facção), `bc-` (ficha do Batcomputador).
