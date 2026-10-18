## Entrega: F0 — spike HTML + JS com estado na window

- **Status:** pronto para revisão
- **Arquivos alterados:** `src/js/spike.js`, `src/css/spike.css`, `src/css/tokens.css`, `src/html/spike.html`,
  `src/html/spike.mock.json`, `src/dax/*.dax` (6 medidas `99 Spike`), `tests/js/spike.test.js`
- **Decisões tomadas (e por quê):**
  - Duas vias de execução: `<script id='gd-src'>` normal e, de reserva, `<img onerror>` que avalia o
    texto do mesmo `<script>` via `new Function`. Se o visual inserir o HTML com `innerHTML` (scripts
    não executam), o código ainda roda — sem duplicar o JS na string. `data-gd-ran` no nó raiz evita
    rodar duas vezes no mesmo DOM.
  - Estado em `window.GOTHAM_STATE.spike`; o loop `requestAnimationFrame` anterior é cancelado a cada
    redesenho (senão as animações aceleram a cada atualização de filtro).
  - Payload sintético `REPT("x", N)` controlado por slicer desconectado para medir o limite de tamanho.
  - Lógica pura (`GOTHAM_SPIKE.*`) separada da renderização para teste em Node sem DOM.
  - `prefers-reduced-motion` desliga chuva e holofote.
- **Contratos afetados:** `design-tokens.md` v0.1 (criado), `measure-catalog.md` v0.1 (criado)
- **Como testar:**
  - `python build/build_preview.py` e abrir `dist/preview/spike.html` → +1 ×3 → "Redesenhar (só innerHTML)"
    → "Redesenhar (executa script)": contador permanece 3, renders 2→3, as duas vias ✔.
  - `npm test` (Vitest, requer Node 20)
- **Pendências / riscos:**
  - Vitest **não foi executado** (Node não instalado na máquina de build). O CI roda.
  - Comportamento real no visual HTML Content **não verificado** (sem Power BI Desktop) — ver `docs/f0-spike.md`.
