# Revisão F0 — spike HTML+JS, build_model/build_report/checks, PBIP

- **Revisor:** Coruja (revisor-qa), revisão independente
- **Data:** 2026-10-17
- **Escopo:** `src/html/spike.html`, `src/js/spike.js`, `src/css/*.css`, `src/dax/*.dax`, `build/*.py`,
  `build/preview_harness.html`, `powerbi/**`, `contracts/*`, `tests/**`, `.github/workflows/ci.yml`

## Veredito: APROVADO (código e build) — gate F0 do plano §12 ainda NÃO fechado

Não achei nenhum defeito bloqueante no código entregue. Os achados abaixo são todos MENORES ou
latentes: nenhum afeta a saída atual. O **gate de saída da F0** pede a página "hello world" com JS
animado e estado na `window` sobrevivendo a redesenho **dentro do Power BI**. Isso não pôde ser
verificado (sem Power BI Desktop, e o visual HTML Content ainda não está no relatório). O gate só fecha
depois que alguém executar `docs/f0-spike.md` e registrar os resultados em `handoffs/F0-resumo.md`.

## Saída dos comandos (resumida)

| Comando | Resultado |
|---|---|
| `.venv/Scripts/python build/checks.py` | `APROVADO: checks.py sem erros` — HTML Spike 7610/30000; demais ≤ 14 chars |
| `.venv/Scripts/python build/build_model.py` | `OK: 6 medidas -> ...\_Medidas.tmdl` |
| `.venv/Scripts/python build/build_report.py` | `OK` + `AVISO: visual HTML Content ainda não importado` |
| `.venv/Scripts/python build/build_preview.py` | `OK: dist\preview\spike.html (8,622 chars)` |
| Idempotência (repo sem commits: sha256 de `powerbi/**` e `dist/**` antes e depois) | 15 arquivos, **nenhuma diferença** |
| `.venv/Scripts/python -m pytest -q` | `36 passed in 0.20s` (schemas vindos do cache `.cache/`) |
| `npm test` (Vitest) | **NÃO EXECUTADO**: Node não está instalado. Análise estática abaixo |
| BPA (Tabular Editor) | Não se aplica na F0 (o CI prevê para a F3) |
| Preview no navegador (painel do Claude) | `dist/preview/spike.html`: via script → `script ✔`; "Redesenhar (só innerHTML)" → `script ✖ / onerror ✔`, contador preservado (7→7), renders +1; "executa script" → `script ✔`, contador preservado. Sem erros no console. A taxa do rAF não pôde ser medida porque o painel estava oculto e o rAF não disparou |

### Análise estática do Vitest (`tests/js/spike.test.js` contra `src/js/spike.js`)

Conclusão: os 6 testes **devem passar**.
- No `vm.createContext({Math, Date, String})`, `window` fica indefinido, então `G = globalThis` = contexto.
  `G.document` é indefinido e o script retorna depois de criar `GOTHAM_STATE = {}` e `GOTHAM_SPIKE`.
- `toEqual({})` e `toEqual(['script','onerror'])` com objetos de outro realm: `toEqual` não compara
  construtores (o array é tratado por `Array.isArray`/`toString`), então passam.
- Holofote: `150 ± 120` → [30, 270] ✔. Sem aspas duplas no arquivo ✔.

## Achados

Nenhum BLOQUEANTE.

### MENORES

1. **`compactar` remove a quebra de linha na fronteira com slot `[[dax:]]`, que é a forma que a F4 vai usar.**
   `build/gotham_build.py:106-109` (aplicado por pedaço em `:126` e `:141`). Cada pedaço `txt` perde o `\n`
   final e o inicial. Por isso, um slot depois de um comentário `//` vira comentário, e o ASI se perde.
   Reprodução:
   ```
   tpl = '<script>\n// dados\n[[dax:[JS Gotham]]]\nGOTHAM.ok=1\n</script>'
   -> '<script>\n// dadosX=1GOTHAM.ok=1\n</script>'
   ```
   O `[JS Gotham]` (padrão §7.4) seria engolido pelo comentário. Também some o espaço junto ao slot:
   `'<p>Total: [[dax:[X]]] chars</p>'` → `'<p>Total:42chars</p>'`. O `spike.html` atual não é afetado,
   porque o slot `js` vira `txt` antes de compactar e os slots `dax` estão colados nas tags.
   **Corrigir antes da F4a** (por exemplo, compactar só o miolo de cada linha e manter as quebras e espaços das bordas).
2. **`compactar` altera template literals multilinha e `<pre>`/`<textarea>`.** Mesmo arquivo, `:106-109`.
   `` `linha1\n    indentada\n\n fim` `` → `` `linha1\nindentada\nfim` ``. Hoje é latente: não há template literal
   multilinha em `spike.js`. Para a F4c, documente a restrição ou aplique uma exceção.
3. **`literal_dax` escapa antes de quebrar em pedaços, então pode partir um `""` ao meio e corromper o texto
   em silêncio.** `build/gotham_build.py:112-115`. Reprodução: `literal_dax('a'*7999 + '"b')` gera
   `"aaa…a"" & ""b"`, um único literal DAX válido cujo conteúdo é `aaa…" & "b`. Hoje é latente, porque o
   `checks.py` proíbe `"` em html/css/js. Correção: quebrar antes de escapar.
4. **Falsos negativos do `checks.py`:**
   - `build/checks.py:41,52,65,67` usam `glob("*.x")` sem recursão: arquivos em subpastas de `src/js`,
     `src/css` e `src/html` não são checados (nem as aspas duplas).
   - `build/checks.py:65-66`: um token vale se estiver definido em **qualquer** `.css`, não só em
     `tokens.css`. Isso contraria a docstring (`:4`) e o contrato `design-tokens.md` ("fonte única").
     `RE_DEF` também casa definições dentro de comentários.
   - Slots com tipo desconhecido (`[[svg:x]]`, `[[html:x]]`) passam calados como texto literal: o regex de
     `gotham_build.py:52` só reconhece `css|js|dax`.
   - Crase tripla em `src/dax/*.dax`: o `checks.py` não chama `medidas_para_tmdl` (`:78` só chama
     `ler_medidas`). O erro só aparece no `build_model.py`. O CI pega mesmo assim, mas o gate de checks
     não detecta.
5. **O teste "estado existente é reaproveitado" é tautológico.** `tests/js/spike.test.js:46-51`. Sem
   `document`, o script retorna antes de `S.spike = S.spike || …` (`src/js/spike.js:53` vs `:59`), então
   o teste passaria mesmo se a linha 59 sobrescrevesse o estado. Sugestão: injetar um `document` falso
   mínimo, ou extrair `L.obterEstado(S, agora)` puro e testá-lo.
6. **Contrato `data-dictionary.md` diverge do TMDL.** `contracts/data-dictionary.md:14` lista a coluna
   `Ordem int64` em `SpikeTamanho`, mas `tables/SpikeTamanho.tmdl` não tem `Ordem` (`Rotulo` usa
   `sortByColumn: Caracteres`, o que está correto). Quem deve ajustar é o dono do contrato.
7. **Diagnóstico do fallback pode enganar em uma ordem específica.** Se o visual recriar `<script>` de
   forma **assíncrona** depois de o `<img onerror>` disparar, o onerror roda primeiro e marca `gdRan`. O
   script recriado retorna em `spike.js:55`, e o cartão "JS via script" mostra ✖ mesmo com scripts
   funcionando. Em `spike.html:21`, `document.getElementById(`gd-src`)` não é protegido contra `null`,
   caso um sanitizador remova `<script>` e mantenha o `onerror`. *Suspeita, não reproduzida*: depende
   do comportamento real do HTML Content.

### Verificado sem problema

- `spike.html`/`spike.js`: nenhuma aspa dupla. O atributo `onerror` usa aspas simples por fora e crases por
  dentro, sem aspas simples internas, e `&&` não forma referência de entidade. `data-gd-ran` impede a
  execução dupla no mesmo DOM. `cancelAnimationFrame(st.raf)` é chamado a cada render, e o loop também
  para com `!raiz.isConnected`. Com `prefers-reduced-motion`, o CSS desliga chuva e transição, e o canvas
  desenha um quadro estático. Não há texto vindo de dados que exija escape: os slots são números/rótulos
  `en-US` e `x`.
- `_Medidas.tmdl`: bloco ``` por medida (abre em `= ```` e fecha com 3 tabs), propriedades com 2 tabs,
  `formatString`/`displayFolder` corretos, nomes citados com `'…'`. O DAX é válido: `FORMAT(...,"0","en-US")`,
  `FORMAT(...,"#,0","en-US") & " chars"`, `REPT("x",[Spike Tamanho])`, `SELECTEDVALUE(...,1000)`,
  `LEN([HTML Spike])`. Os slots viram `& ( [Medida] ) &` e todas as medidas citadas existem.
  O arquivo commitado é idêntico ao gerado.
- `SpikeTamanho.tmdl`: o tipo M `Int64.Type`/`text` bate com `int64`/`string`, e `sortByColumn` é 1:1.
  `model.tmdl` referencia as 2 tabelas (testado). `definition.pbism` 4.0 (TMDL), `database.tmdl` 1600.
- PBIR: o slicer usa `SpikeTamanho.Rotulo` e o card usa `_Medidas.Tamanho HTML Spike`, ambos existentes.
  O JSON valida nos schemas oficiais (pytest). `build_report.py` preserva o `report.json` e as páginas
  que não têm prefixo `gd`.
- Contratos: `measure-catalog.md` cobre as 6 medidas com pasta e dependências corretas.
  `design-tokens.md` bate com `tokens.css`, e o contraste AA é testado.

## Não verificável nesta máquina

- **Power BI Desktop não instalado.** Não foi possível testar a abertura do `.pbip`, o parse real do TMDL,
  em especial se a indentação de 3 tabs dentro do literal DAX multilinha é removida ou preservada no modo
  ``` (se for preservada, só entra espaço em branco inofensivo no HTML), a execução de JS no HTML Content
  (script / onerror / CSP para `new Function`), o limite prático de tamanho e a sobrevivência do estado à
  troca de página. O visual `gdSpikeHtml` ainda não existe no relatório (`config.json` com
  `visualType: null`).
- **Vitest não executado** (Node ausente). Fica só a análise estática acima.
- **Taxa de quadros do rAF depois de vários redesenhos**: o painel do navegador estava oculto (rAF não dispara).
- **Amostra de lore**: não há fatos de lore na entrega F0, então não se aplica.
- **BPA**: previsto para a F3.

## Para fechar o gate F0

1. Executar `docs/f0-spike.md` no Desktop e registrar a tabela em `handoffs/F0-resumo.md`.
2. Rodar `npm test` no CI ou em uma máquina com Node 20.
3. Corrigir o item 1 (e de preferência os itens 3 e 4) antes de iniciar a F4a.
