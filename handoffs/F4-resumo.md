# F4 (sprint 2) — Resumo (Alfred)

**Status:** gate F4 da página Batcomputador **aprovado** pela Coruja no ciclo 3 (`handoffs/review-F4.md`).
Publicado no Power BI Service como página principal do relatório.

## O que entrou

| Item | Onde |
|---|---|
| **F4a** — `[JS Gotham]`: o modelo inteiro serializado em ~26,6 mil caracteres (2,7% do limite medido na F0) | `src/dax/JS Gotham.dax` |
| **F4b** — layout 3 colunas responsivo, 10 temas animados por facção, `prefers-reduced-motion`, contraste AA | `src/css/batcomputador.css` |
| **F4c** — app: lista com busca/filtros/favoritos, ficha com radar SVG e Índice de Ameaça, arquétipo com vantagens (×2 ↑ / ×2 ↓ / ×½), rede de relações clicável e agrupada, aparições por mídia, teclado (roving tabindex, ↑/↓, Enter, F) | `src/js/batcomputador.js` |
| Mock fiel à medida para preview e testes | `build/mock_gotham.py` |
| Testes: 226 pytest + 14 Vitest (CI) | `tests/` |

## Bugs que só apareceram no Power BI (e viraram testes)

1. **Membro em branco da dimensão:** `ALL(dArquetipo)` incluía a linha em branco criada pela FK vazia de
   `dGadget` → matriz deslocada. Solução: `ALLNOBLANKROW`.
2. **Iframe mais estreito que a página:** colunas fixas empurravam a coluna direita para fora. Grade proporcional.
3. **Dados velhos na `window`:** o caminho de reserva `onerror` não recarregava os dados. Sempre recarrega.
4. **Cache do Desktop:** "Aplicar alterações externas" não reexecutou o visual; foi preciso reabrir o projeto.

## Revisão (3 ciclos)

Ciclo 1 reprovado (contraste do item selecionado + 13 menores); ciclo 2 reprovado (a correção perdia na cascata
CSS e o teste dava falso positivo); ciclo 3 aprovado. Escape de string JS de todos os 21 campos de texto, contraste
11,7:1, acessibilidade por teclado.

## Pendências

- Tempo do 1º render da medida no Analisador de desempenho (gate F4a) — medir até a F6.
- Cores fixas fora dos tokens (`COR_REL`, gradientes) — M11.
- Vitest só no CI (sem Node local). Correção P1 (foco ao desfavoritar) entra na próxima publicação.
- Próximas sprints do plano: 3 (modos Arkham/Versões/Capas), 4 (Rede de Relações e Linha do Tempo),
  5 (Arena + balanceamento F4d), 6 (Quiz + Patrulha).

**Não avançar sem aprovação humana.**
