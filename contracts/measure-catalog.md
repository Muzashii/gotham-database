# Catálogo de medidas

- **Dono:** engenheiro-dax (Batcomputador) · **Consumidores:** revisor-qa, documentador
- **Versão:** 0.2 (F4). Fonte: `src/dax/*.dax` (1 arquivo por medida). Orçamentos em `build/budget.json`.

Pastas de exibição: `00 Seleção`, `10 Ficha HTML`, `20 CSS`, `30 SVG`, `40 JS`, `50 Analítico`, `99 Spike` (temporária).

| Medida | Pasta | Propósito | Depende de |
|---|---|---|---|
| `Spike Tamanho` | 99 Spike | Nº de caracteres de payload escolhido no slicer (padrão 1.000) | `SpikeTamanho[Caracteres]` |
| `Spike Tamanho Rotulo` | 99 Spike | Rótulo formatado do tamanho (`en-US`) | `[Spike Tamanho]` |
| `Spike Payload` | 99 Spike | `REPT` de N caracteres para medir o limite do visual | `[Spike Tamanho]` |
| `Spike Linhas` | 99 Spike | Prova de leitura do modelo (contagem de linhas) | `SpikeTamanho` |
| `HTML Spike` | 99 Spike | HTML + CSS + JS do spike (template `src/html/spike.html`) | todas acima |
| `Tamanho HTML Spike` | 99 Spike | `LEN([HTML Spike])` — tamanho real entregue ao visual | `[HTML Spike]` |
| `Painel KPIs` | 50 Analítico | Cartões HTML: personagens, obras, aparições, relações, % vilões | dPersonagem, dObra, fAparicao, fRelacao |
| `Painel Barras Midia` | 50 Analítico | Barras de aparições por mídia | dMidia → dObra → fAparicao |
| `Painel Barras Era` | 50 Analítico | Colunas de obras por era (ordem de `dEra[Ordem]`) | dEra → dObra |
| `Painel Hubs` | 50 Analítico | Top 8 por intermediação, com grau | dCentralidade, dPersonagem |
| `Painel Grade` | 50 Analítico | Cards do arquivo de personagens (retrato com fallback, faixa da facção) | dPersonagem, dVersao, dArquetipo |
| `HTML Painel` | 10 Ficha HTML | Página Painel do Comissário (template `src/html/painel.html`) | todas `Painel *` |
| `JS Gotham` | 40 JS | Serializa o modelo em `window.GOTHAM` (contrato `js-data-schema.json` v0.2); dimensões com `ALLNOBLANKROW` | todas as tabelas curadas |
| `Tamanho JS Gotham` | 40 JS | `LEN([JS Gotham])` — ~26,6 mil caracteres (2,7% do limite medido na F0) | `[JS Gotham]` |
| `HTML Batcomputador` | 10 Ficha HTML | Página Batcomputador: dados + app `src/js/batcomputador.js` + CSS por facção | `[JS Gotham]` |

Decisão F4: seleção, radar e ficha são renderizados em JS a partir de `[JS Gotham]` (como na Pokédex de referência), em vez das medidas DAX de seleção do plano §7.1–7.3 (`Id Selecionado`, `SVG Radar`, `HTML Ficha`). Troca de personagem é instantânea (sem consulta ao modelo).
