## Entrega: F0 — build_model.py, build_report.py, checks.py

- **Status:** pronto para revisão
- **Arquivos alterados:** `build/gotham_build.py`, `build/build_model.py`, `build/build_report.py`,
  `build/build_preview.py`, `build/preview_harness.html`, `build/checks.py`, `build/budget.json`,
  `build/config.json`, `powerbi/**`, `tests/build/*.py`, `pyproject.toml`, `.github/workflows/ci.yml`
- **Decisões tomadas (e por quê):**
  - Templates HTML em `src/html` com slots `[[css:]]`, `[[js:]]`, `[[dax:]]`; o `.dax` usa `TEMPLATE(x.html)`.
    O HTML fica legível/editável como HTML e o mesmo template gera DAX (build) e HTML de preview (mocks).
  - Literais DAX quebrados em pedaços de 8.000 caracteres concatenados com `&` (evita depender de
    limite de literal). Quebras de linha são preservadas (JS com `//` depende delas); só indentação sai.
  - `_Medidas.tmdl` é 100% gerado (bloco ``` por medida); outras tabelas TMDL são do modelador.
    Teste garante que o arquivo commitado está em sincronia com `src/`.
  - `build_report.py` só regrava visuais/páginas com prefixo `gd` e preserva o resto do `report.json`.
    O GUID do HTML Content não é chutado: é detectado após importar o visual no Desktop
    (o GUID da edição *Secure* foi confirmado no GitHub do autor — `…6865` — mas essa edição não executa scripts).
  - Tema `GothamNoir.json` gerado dos tokens CSS (fonte única de cor).
- **Contratos afetados:** `data-dictionary.md` v0.1 (rascunho, dono Gordon — criado no kickoff, ele assume na F3)
- **Como testar:**
  ```bash
  python build/checks.py
  python build/build_model.py && python build/build_report.py
  python -m pytest            # 36 testes; os de schema baixam JSON Schema da Microsoft (cache em .cache/)
  ```
- **Pendências / riscos:**
  - JSON do PBIR **valida nos schemas oficiais**, mas a abertura no Desktop **não foi testada**.
  - TMDL não tem validador offline aqui; formato segue o que o Desktop serializa (risco baixo-médio).
  - Orçamento atual: `HTML Spike` 7.6k / 30k caracteres estáticos.
