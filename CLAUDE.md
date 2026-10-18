# Gotham Database — regras globais

Plano completo: `docs/plano.md`. Fase atual e pendências: último `handoffs/Fx-resumo.md`.

- Idioma: código e nomes técnicos em português sem acento (IdPersonagem), comentários em pt-BR.
- Fonte da verdade: /contracts. Nunca altere um contrato que não é seu.
- JS e HTML: PROIBIDO aspas duplas. Use aspas simples ou template literals.
- DAX: FORMAT numérico sempre com "en-US" quando o valor vai para SVG/JS/CSS.
- Escape de texto vindo de dados: & < > ' (ex.: Ra's al Ghul).
- Toda entrega termina com handoff em /handoffs seguindo o template.
- Nunca commite chaves de API (.env no .gitignore).
- Não invente fatos de lore: sem fonte, marque como "pendente de verificação".

## Como o build funciona

- Medidas: 1 arquivo `src/dax/<Nome da Medida>.dax`. Cabeçalho opcional:
  `-- @pasta: 00 Seleção` e `-- @formato: 0`.
- Dentro de um `.dax`, `TEMPLATE(arquivo.html)` é expandido pelo build para uma
  concatenação DAX de literais + slots.
- Templates `src/html/*.html` aceitam slots:
  - `[[css:arquivo.css]]` → conteúdo de `src/css/arquivo.css`
  - `[[js:arquivo.js]]` → conteúdo de `src/js/arquivo.js`
  - `[[dax:<expressão DAX>]]` → expressão DAX concatenada no lugar
- `python build/checks.py` reprova aspas duplas, crases triplas, slots quebrados,
  tokens CSS inexistentes e medidas acima do orçamento (`build/budget.json`).
- `python build/build_model.py` regrava `tables/_Medidas.tmdl` (arquivo gerado — não editar à mão).
- O Power BI Desktop regrava `_Medidas.tmdl` ao salvar: depois de salvar no Desktop, rode
  `build/build_model.py` de novo (o teste de sincronia acusa se esquecer).
- Limite medido na F0: uma medida até ~1 milhão de caracteres renderiza; 5 milhões falha.
- `python build/build_preview.py` gera `dist/preview/*.html` com valores mock
  (`src/html/*.mock.json`) para testar no navegador sem Power BI.

## Comandos

```bash
python build/checks.py
python build/build_model.py
python build/build_report.py
python build/build_preview.py
python -m pytest
npm test        # Vitest (requer Node 20)
```
