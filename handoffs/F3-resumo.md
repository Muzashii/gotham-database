# F3 — Resumo (Alfred)

**Status:** gate F3 **aprovado** pela Coruja (`handoffs/review-F3.md`, sem bloqueantes); menores M1–M4, M6–M8
corrigidos; modelo **validado no Power BI Desktop e publicado** no serviço.

| Critério (plano §12) | Resultado |
|---|---|
| BPA sem erros críticos | ✔ 16 regras em `tests/bpa` (Tabular Editor não instalado) — inclui ambiguidade de caminhos, cardinalidade, bidirecional, FKs ocultas, unicidade do lado 1 nos dados |
| Dicionário de dados completo | ✔ seção "Modelo semântico (F3)" gerada a partir do TMDL (`contracts/data-dictionary.md` v0.4) |
| Carga real | ✔ Desktop 2.159: 25 tabelas carregadas do GitHub (acesso anônimo), `dObra` 319, `dPersonagem` 50, nulos corretos |

**Entregas:** `build/modelo_spec.py` (decisões de modelagem), `build/build_tabelas.py` (gera TMDL + dicionário),
18 tabelas curadas + 5 desconectadas, 23 relações N:1 (16 ativas), função M `LerCsv`, 219 testes.

**Pendências:** BPA oficial do Tabular Editor; atualização agendada no serviço; `returnErrorValuesAsNull`;
coluna de década (F4a); Comic Vine (chave).

**Recomendação para a F4:** começar pela F4a (DAX: `Id Selecionado`, `SVG Radar`, `HTML Ficha`, `JS Gotham`) e F4b
(CSS por facção) em paralelo, para a primeira página real — o Batcomputador — substituir o spike na F5.

**Não avançar para a F4 sem aprovação humana.**
