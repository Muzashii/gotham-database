## Entrega: F4 (sprint 2) — página Batcomputador (F4a DAX + F4b design + F4c JS)

- **Status:** pronto para revisão
- **Arquivos alterados:** `src/dax/{JS Gotham,HTML Batcomputador,Tamanho JS Gotham}.dax`, `src/html/batcomputador.html`,
  `src/css/batcomputador.css`, `src/js/batcomputador.js`, `build/mock_gotham.py`, `build/build_report.py` (página
  `gdBatcomputador` como principal), `build/budget.json`, `contracts/js-data-schema.json` v0.2,
  `contracts/measure-catalog.md` v0.2, `tests/js/batcomputador.test.js`, `tests/js/fixtures/gotham.js`, `tests/build/test_build.py`
- **Escopo:** sprint 2 do roadmap (MVP: ficha, radar, temas por facção). Arena/Quiz/Patrulha (F4c restante) e o
  balanceamento (F4d) ficam para as sprints 5–6, como no plano §16.
- **Decisões tomadas (e por quê):**
  - **F4a:** uma medida `[JS Gotham]` serializa o modelo inteiro (personagens com agregados de afiliação,
    aparições por mídia e centralidade; versões; matriz; eras; relações; golpes) em ~26,6 mil caracteres.
    A ficha, o radar e os filtros são renderizados em JS — troca de personagem sem consulta ao modelo.
    Isso substitui as medidas DAX de seleção do §7.1–7.3 (registrado no catálogo de medidas).
  - Escape de string JS no DAX: `\`, `'` e `</` (Ra's al Ghul, "Dennis O'Neil", "Joker's Favor").
  - **Bug achado no Power BI:** `ALL(dArquetipo)` trazia o *membro em branco* criado pela FK vazia
    `dGadget[SoContraArquetipo]`, gerando uma linha extra na matriz e deslocando as vantagens. Corrigido com
    `ALLNOBLANKROW` em todas as dimensões + teste de regressão (`test_js_gotham_itera_dimensoes_sem_membro_em_branco`).
  - **Bug de layout no Power BI:** o iframe do visual é mais estreito que 1280 px CSS; colunas fixas empurravam a
    coluna direita para fora. Grade proporcional com `minmax(0, 1fr)`, testada em 1280/1050/900/760 px.
  - **Bug do fallback `onerror`:** só recarregava os dados se `window.GOTHAM` não existisse → dados velhos após
    republicar. Agora sempre recarrega.
  - **F4b:** layout 3 colunas; 10 temas por facção (chuva/relâmpago, holofote, névoa, gelo, vinhas, moeda,
    brasas, `?`, penas) só com `transform`/`opacity` + partículas geradas pelo JS; `prefers-reduced-motion` desliga tudo.
    Nenhum logo/personagem desenhado (plano §18).
  - **F4c:** lógica pura (`filtrar`, `ameaca`, `pontosRadar`, `vantagens`, `relacoesDe`, `esc`) exportada em
    `window.GOTHAM_BC` e testada em Vitest; estado (seleção, filtros, favoritos) em `window.GOTHAM_STATE.bc`;
    erros de render aparecem na página (o visual não tem console); navegação por ↑/↓.
  - `build/mock_gotham.py` reproduz a saída da medida a partir de `data/curated` (preview + fixture dos testes).
- **Contratos afetados:** `js-data-schema.json` v0.2 (chaves `ar`, `er`, `af`, `md`, `p`, `rel`); `measure-catalog.md` v0.2.
- **Como testar:**
  ```bash
  python build/mock_gotham.py && python build/build_preview.py   # abrir dist/preview/batcomputador.html
  python -m pytest -q            # 224
  npm test                       # Vitest (CI)
  ```
- **Validação no Power BI Desktop (19/10/2026):** ficha do Batman completa, busca "coringa" → tema roxo com cartas,
  vantagens PSI corretas, rede e aparições; publicado no serviço (página principal).
- **Pendências / riscos:**
  - Gate F4a "troca de personagem < 1,5 s no DAX Studio": a troca é client-side (instantânea); o custo é o 1º
    render da medida — não medido no Analisador de desempenho.
  - Mock e saída real diferem só na formatação de números (26.424 vs 26.613 caracteres: `1.0` vs `1`, `0.000` vs `0`).
  - Contraste AA dos chips coloridos sobre fundo escuro não auditado; layout mobile não feito.
  - Vitest não roda localmente (sem Node); roda no CI.

### Ciclo 2 — correções após `handoffs/review-F4.md`
- **B1** contraste: itens da lista com fundo opaco (`--g-panel`); selecionado com `#22221a` opaco e texto secundário
  em `--g-text` (11,7:1). Teste `test_contraste_aa_do_item_selecionado_da_lista`.
- **M1** `[JS Gotham]`: os 21 campos de texto passam pelo mesmo escape (`\`, `'`, `</`, LF, CR) — inclusive arquétipo,
  era, afiliação, mídia, URL, raridade, alinhamento, facção, tipo de relação e golpes. Teste falha se alguma coluna
  entrar em string JS sem escape. `mock_gotham.py` escapa os mesmos campos.
- **M2** sem dados → aviso "dados indisponíveis" no cabeçalho. **M3** ↑/↓ ignorados dentro de `<select>`.
- **M4** ≤ 900 px: 2 colunas, painel lateral embaixo da ficha; verificado sem cortes em 1280/900/760 px.
- **M5** holofote da Bat-família apontando para cima (`from 345deg`). **M6** `aria-pressed` do filtro de favoritos
  restaurado no redesenho. **M7** itens da lista focáveis (Enter/Espaço), estrela virou `<button>` com rótulo, foco
  volta para o item selecionado após clicar numa relação. **M8** erro de render substitui a ficha (não deixa a anterior).
- **M9** relações agrupadas por pessoa (`L.agruparRelacoes`: "família · pupilo · lidera"). **M10** versão padrão =
  menor `IdVersao` não transformação (sem depender de Id×100+1). **M12** centralidade via `FILTER(ALLNOBLANKROW…)`.
- **M11** (cores fixas fora dos tokens) e **M13** (plano §7 descreve seleção em DAX) — pendências documentadas.
- Validado de novo no Power BI Desktop (reaberto do zero) e republicado. 226 testes.

### Ciclo 3 — correções após o ciclo 2 de `review-F4.md`
- **B1** (cascata): `.bc-sel small` perdia para `.bc-in small` (mesma especificidade, declarada depois). Agora
  `.bc-sel .bc-in small` (0,2,1); cor computada no preview `rgb(215,221,228)` sobre `rgb(34,34,26)` = 11,7:1.
  O teste passou a recusar o seletor fraco (antes dava falso positivo).
- **N1** versão padrão: `COALESCE(menor não-transformação, menor do personagem, 0)` — nunca gera `v:,`; o mock usa a mesma regra.
- **N2** roving tabindex: só 1 elemento focável na lista; ↑/↓ movem o foco; **F** favorita; estrela fora do Tab.
- **N3** filtros em 2 colunas abaixo de 1100 px (99 px a 950 px, medido pela Coruja).
- Republicado (instâncias duplicadas do Desktop fechadas antes).
- **P1** (pós-ciclo 3): com "Só favoritos", desfavoritar por F levava o foco ao `body`; agora vai ao item focável
  restante ou à raiz. Correção no repositório; entra no ar na próxima publicação.
