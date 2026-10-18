# Catálogo de medidas

- **Dono:** engenheiro-dax (Batcomputador) · **Consumidores:** revisor-qa, documentador
- **Versão:** 0.1 (F0). Fonte: `src/dax/*.dax` (1 arquivo por medida). Orçamentos em `build/budget.json`.

Pastas de exibição: `00 Seleção`, `10 Ficha HTML`, `20 CSS`, `30 SVG`, `40 JS`, `50 Analítico`, `99 Spike` (temporária).

| Medida | Pasta | Propósito | Depende de |
|---|---|---|---|
| `Spike Tamanho` | 99 Spike | Nº de caracteres de payload escolhido no slicer (padrão 1.000) | `SpikeTamanho[Caracteres]` |
| `Spike Tamanho Rotulo` | 99 Spike | Rótulo formatado do tamanho (`en-US`) | `[Spike Tamanho]` |
| `Spike Payload` | 99 Spike | `REPT` de N caracteres para medir o limite do visual | `[Spike Tamanho]` |
| `Spike Linhas` | 99 Spike | Prova de leitura do modelo (contagem de linhas) | `SpikeTamanho` |
| `HTML Spike` | 99 Spike | HTML + CSS + JS do spike (template `src/html/spike.html`) | todas acima |
| `Tamanho HTML Spike` | 99 Spike | `LEN([HTML Spike])` — tamanho real entregue ao visual | `[HTML Spike]` |

Medidas de produção (F4a) seguem `docs/plano.md` §7: `Id Selecionado`, `SVG Radar`, `HTML Ficha`, `CSS Base`, `CSS Faccao`, `JS Gotham`…
