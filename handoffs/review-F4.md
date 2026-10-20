## Revisão: F4 (sprint 2) — página Batcomputador (Coruja)

- **Veredito: REPROVADO.** Falta 1 critério do gate **F4b** (contraste AA, achado B1). F4a e F4c passam, com as
  ressalvas descritas abaixo. A correção de B1 é pequena, de uma linha de CSS. Também há 13 achados MENORES. M1, M2 e M3
  devem ser corrigidos nesta mesma volta.
- **Escopo:** `src/dax/{JS Gotham,HTML Batcomputador,Tamanho JS Gotham}.dax`, `src/html/batcomputador.html`,
  `src/css/batcomputador.css`, `src/js/batcomputador.js`, `build/mock_gotham.py`, `tests/js/batcomputador.test.js`
  (+ fixture), além dos contratos `js-data-schema.json` v0.2, `measure-catalog.md` v0.2 e `design-tokens.md`, e do
  handoff `F4-batcomputador.md`. Não toquei no Power BI Desktop.

### Saída dos comandos (rodados na raiz, Python do venv)

| Comando | Resultado |
|---|---|
| `.venv/Scripts/python -m pytest -q` | **224 passed** em 2,1 s |
| `.venv/Scripts/python build/checks.py` | **APROVADO: checks.py sem erros**. `HTML Batcomputador` tem 29.869/40.000 caracteres literais e `JS Gotham` tem 412/20.000 |
| `.venv/Scripts/python build/mock_gotham.py` | `OK: window.GOTHAM mock com 26,424 caracteres`, o mesmo número do handoff |
| `.venv/Scripts/python build/build_preview.py` | `OK: dist\preview\batcomputador.html (56,293 chars)`, além de painel e spike |
| `npm test` (Vitest) | **não rodado**: não há Node nesta máquina. Fiz a análise por leitura (ver abaixo) |
| aspas duplas | `grep -c '"'` dá 0 em `batcomputador.js` e 0 em `batcomputador.html`. O teste Vitest também verifica isso |

O tamanho total entregue ao visual é de cerca de 56 mil caracteres: 29,9 mil de literais mais 26,6 mil da medida. Isso
equivale a 5,6% do limite de ~1 milhão medido na F0.

### Vitest por leitura (contexto `vm`)

Minha conclusão é que **os 13 casos devem passar**:
- `carregar()`: em um contexto sem `window`, `G` vira o sandbox, porque `ctx.globalThis = ctx`. `GOTHAM_BC` é gravado
  nele, e `G.document` indefinido encerra o script antes do DOM. O spike já usa o mesmo padrão.
- Verifiquei os valores na mão: `ameaca([100,26,27,50,47,100])` dá 350/6 = 58,3, ou seja `{58,'Alto'}`. O 1º vértice
  do radar dá `[100,20]`, porque `toFixed(1)` elimina o resíduo de `cos(-π/2)`, e não aparece `-0` nos valores
  comparados. `vantagens` dá `{forte:[2],fraco:[3],vulneravel:[3],resiste:[2]}`. A ordenação de `relacoesDe` dá
  `[3,16,19]`. A regex de acentos contém de fato U+0300–U+036F (bytes `CC 80`–`CD AF`).
- Arrays criados no contexto e comparados com `toEqual`: o `equals` do Vitest compara pelo `toString` da classe e não
  pelo construtor, então a diferença de realm não reprova.
- Fixture versus contrato: as chaves de topo são as mesmas 10 (`ar m er af md v p rel g vg`). São 50 personagens. A
  matriz é 8×8 com valores em {0,5; 1; 2}. Os atributos vão de 7 a 100. As 116 relações apontam para ids existentes.
  Conferi tudo isso em `data/curated`.
- Limitação: os testes cobrem o **mock**, não a saída da medida DAX (ver M1).

### Teste no navegador (preview + harness, Chromium do app)

| Verificação | Resultado |
|---|---|
| Carga inicial | Ficha do Batman, 50 itens, 0 `.bc-erro`, **console sem mensagens** |
| Troca de personagem | Ra's al Ghul renderiza com apóstrofo correto. 50 trocas seguidas levaram **350 ms (~7 ms por troca)**, com 0 erros |
| Busca | `coringa` retorna `[Coringa]`. `RA` retorna 16. `zzz` mostra "Nenhum arquivo com esses filtros." |
| Filtros | Vilão: 25. + Galeria de Vilões: 24. + 1ª era: 11. O estado é gravado em `GOTHAM_STATE.bc` |
| Favoritos | A estrela não troca a seleção. "Só favoritos" mostra `[Oráculo, Ra's al Ghul]` |
| Redesenho com script | `sel`, `busca`, `fav` e `favoritos` iguais antes e depois. Restam 1 `#bc-raiz` e 3 `<script>` após 20 redesenhos seguidos. Não há listeners duplicados: um clique na estrela alterna uma única vez |
| Redesenho só innerHTML (via `onerror`) | O app roda e o estado é preservado. "Zerar estado" volta para o Batman |
| XSS | Injetei `'><img src=x onerror=…>"</script>&` em nome, codinome, identidade, estreia, criadores, justificativa, mídia, alinhamento, facção, era, afiliação, arquétipo e URL de imagem. **0 execuções**: todo dado passa por `esc` |
| Larguras 1280 e 900 px | Sem overflow em nenhuma coluna |
| Largura 760 px | **Conteúdo cortado** na ficha (M4) |

### Gates

| Gate | Situação |
|---|---|
| **F4a**: medida < orçamento | ✅ `checks.py` aprova |
| **F4a**: troca < 1,5 s | ⚠️ A troca é feita no cliente e mede ~7 ms. O 1º render da medida (DAX Studio / Analisador de desempenho) **não foi medido**, e o próprio handoff registra isso como pendência. Não bloqueio por isso, mas a medição precisa sair até a F6 (§14.2) |
| **F4b**: `prefers-reduced-motion` | ✅ Por leitura, todas as animações (`.bc-fx` ::before/::after, `.bc-part span`, `.bc-area`, `.bc-b em`, `.bc-glitch`) e a transição `.bc-item` são desligadas, e o JS deixa de gerar partículas. Todas as animações usam só `transform`/`opacity`. Não consegui emular a media query no navegador |
| **F4b**: contraste AA | ❌ **B1** |
| **F4c** | ✅ Testes devem passar (por leitura), 0 aspas duplas, app funcionando com o mock do contrato |

### Achados

#### BLOQUEANTE

**B1. O texto secundário do item selecionado fica abaixo de AA quando há um tema com névoa.**
`src/css/batcomputador.css:42`
- **Causa:** `.bc-sel { background: rgba(245,197,24,0.08) }` **substitui** o fundo `rgba(16,20,26,0.85)` de `.bc-item`
  (linha 38), porque tem a mesma especificidade e vem depois. O item selecionado fica quase transparente sobre o fundo
  animado. O texto `.bc-in small` (11 px, `--g-muted #7d8794`) passa a depender do tema.
- **Reprodução:** no preview, selecione o Espantalho (`fx-espantalho`). `getComputedStyle(document.querySelector('.bc-sel')).backgroundColor`
  retorna `rgba(245, 197, 24, 0.08)`. Calculei a composição alfa dos estilos computados com a fórmula WCAG:
  - fundo puro: 4,88:1 (passa)
  - chuva de Gotham: 3,95:1
  - Vagalume: 4,2:1
  - névoa do Coringa: 3,58:1
  - névoa do Espantalho: **3,06:1**

  Um item não selecionado, sobre os mesmos fundos, fica entre 4,89 e 5,07:1. Esses valores vêm de cálculo e não de
  amostragem de pixel, mas a causa no CSS está confirmada.
- **Correção sugerida:** manter a base opaca, por exemplo
  `background: linear-gradient(rgba(245,197,24,.08), rgba(245,197,24,.08)), rgba(16,20,26,.85)`, ou usar `--g-text`
  no `small` do item selecionado.

#### MENORES

**M1. O escape de string JS no DAX não cobre todos os campos de texto, e o mock diverge da medida.**
`src/dax/JS Gotham.dax:9,26,28,30,38,80,86-88` versus `build/mock_gotham.py:37-45,62`
- A medida escapa só `NomeVersao` e os 6 textos de `dPersonagem`. Ficam **sem escape**:
  - `dArquetipo[Sigla/Nome/Cor]`
  - `dEra[Nome]`
  - `dAfiliacao[Nome]`
  - `dMidia[Nome]`
  - `dVersao[UrlImagem/Raridade]`
  - `dPersonagem[Alinhamento/Faccao/MidiaEstreia]`
  - `fRelacao[TipoRelacao]`
  - `dGolpe[Nome/Efeito]`
- **Nenhum campo** escapa quebra de linha (`\n`, `\r`).
- Hoje nenhum desses campos tem `'`, `\`, `</`, LF ou CR (verifiquei os CSVs), então **não quebra com os dados
  atuais**. Basta, porém, um golpe ou era com apóstrofo (por exemplo "Joker's …") ou uma justificativa com quebra de
  linha para causar `SyntaxError` em `window.GOTHAM`.
- Além disso, `mock_gotham.py` **escapa** `ar.Nome`, `er.Nome`, `af.Nome`, `md`, `UrlImagem` e `dGolpe[Nome/Efeito]`,
  mas a medida não. Por isso a fixture e os testes nunca detectariam esse defeito na medida.
- **Correção sugerida:** aplicar o mesmo escape (mais `UNICHAR(10)` → `\n` e `UNICHAR(13)` → `""`) a todos os textos,
  na medida e no mock. Acrescentar um teste pytest que confira, no `.dax`, que toda coluna de texto passa pelo escape.

**M2. Falha no script de dados é silenciosa.**
`src/js/batcomputador.js:78`
- Se `bc-dados` lança erro (por exemplo M1), `window.GOTHAM` fica indefinido e o app faz `return` sem avisar. A página
  fica para sempre em "carregando o Batcomputador…".
- Isso contradiz a decisão "erros de render aparecem na página".
- **Reprodução (por leitura, não executada):** se `bc-dados` contiver `n:'a'b'`, o script de dados lança
  `SyntaxError`, `G.GOTHAM` fica indefinido e a linha 78 retorna sem mensagem.
- **Sugestão:** se `doc` existe mas `D` não, escrever um `.bc-erro` em `#bc-raiz`.

**M3. Setas do teclado sequestram os `<select>` de filtro.**
`src/js/batcomputador.js:265-271`
- O `keydown` em `#bc-raiz` intercepta ↑/↓ vindos de qualquer descendente e chama `preventDefault()`.
- **Reprodução:** foco em `#bc-alin`, depois `keydown ArrowDown`. O evento é cancelado (`defaultPrevented = true`), o
  personagem muda (1 → 2) e o select não muda.
- O mesmo acontece no campo de busca, o que pode ser intencional.
- **Sugestão:** ignorar o evento quando `ev.target` for `SELECT`. Avaliar também o caso de `INPUT`.

**M4. Corte de conteúdo na ficha a 760 px, uma largura que o handoff diz ter testado.**
`src/css/batcomputador.css:64-66,73,80`
- Com viewport de 760 px, a coluna central tem 264 px:
  - `.bc-card` tem `scrollWidth` 310 contra `clientWidth` 264
  - `.bc-radar-box` tem 142 contra 94
  - `.bc-mini3` tem 292 contra 228
- O `overflow:hidden` do card esconde a coluna de valores das barras, corta "ÍNDICE DE AMEA…" e corta o 3º contador
  ("ano de estreia"). Os selects de filtro ficam com 49 px ("Alin", "Afili").
- A 900 e 1280 px está tudo certo.
- **Sugestão:** um breakpoint menor (~820 px) que empilhe `.bc-corpo` e reduza `.bc-foto` e `.bc-mini3`, ou filtros em
  2 linhas.

**M5. O holofote da Bat-família é invisível.**
`src/css/batcomputador.css:131-133`
- O `conic-gradient(from 165deg at 50% 100%)` põe a faixa entre 177° e 183°, ou seja **apontando para baixo** a partir
  da base do pseudo-elemento, fora da área visível.
- **Reprodução:** sobrescrevi o gradiente com vermelho opaco e não apareceu nenhum pixel vermelho. Com `from 345deg`, o
  feixe aparece varrendo a ficha.
- O tema padrão do Batman (`fx-batfamilia`) mostra só o pulso elíptico do `::after`.

**M6. `aria-pressed` do botão "Só favoritos" não é restaurado após redesenho.**
`src/js/batcomputador.js:272`
- A linha 272 restaura só `textContent='★'`.
- **Reprodução:** com o filtro ativo, clique em "Redesenhar (executa script)". O botão mostra ★ com `aria-pressed='false'`.

**M7. Favoritos e itens da lista não são acessíveis por teclado.**
`src/js/batcomputador.js:132-134`
- A estrela é um `<span data-fav>` sem `role`, `tabindex` ou rótulo, então não dá para favoritar pelo teclado.
- Os `li role='option'` não são focáveis e o `listbox` não tem `aria-activedescendant`.
- Ao clicar num `.bc-rel`, a coluna é recriada e o foco vai para `body`. A partir daí ↑/↓ deixa de funcionar até a
  pessoa focar `#bc-raiz` de novo. **Reprodução:** `rel.focus(); rel.click();` resulta em `document.activeElement === body`.

**M8. Erro ao montar a ficha aparece na coluna errada.**
`src/js/batcomputador.js:230`
- `seguro('ficha', …)` escreve o aviso em `#bc-lado` e deixa a ficha anterior visível em `#bc-ficha`. Isso pode
  mostrar dados de outro personagem.

**M9. Relações duplicadas ocupam o top 9.**
`src/js/batcomputador.js:192`
- `fRelacao` tem 21 pares repetidos com tipos diferentes e 52 pares nos dois sentidos.
- Ra's al Ghul mostra "Damian Wayne · família" e "Damian Wayne · pupilo", e "Talia" em dobro.
- **Sugestão:** agrupar por `outro` e juntar os rótulos.

**M10. O id da versão padrão é inferido por convenção.**
`src/dax/JS Gotham.dax:73` (e `mock_gotham.py:57`)
- `v: _id*100+1` vale para os dados atuais (1 versão por personagem, verifiquei), mas quebra quando entrarem versões
  com outra numeração.
- **Sugestão:** usar `MINX`/`LOOKUPVALUE` em `dVersao` com uma coluna de versão padrão.

**M11. Cores fora dos tokens.**
- CSS: `#1a2330`, `#2a3542`, `#e9d27a`, `#9c7a1b`, `rgba(245,160,24,…)` (`batcomputador.css:13,43,65,149,167`).
- JS: `COR_REL` com `#e07aa8` e `#e07a1f` (`batcomputador.js:8`).
- O `checks.py` só valida `var()` existentes, então isso passa. Fere a regra "CSS sempre via variáveis" (§13.7).
- `rival` em `COR_REL` não existe nos dados.

**M12. Contexto de filtro: risco residual, sem defeito hoje.**
- A medida usa `ALLNOBLANKROW` e `ALL` em tudo, exceto `LOOKUPVALUE(dCentralidade…)`, que pode respeitar filtros
  externos.
- Hoje a página `gdBatcomputador` tem um único visual, sem segmentadores nem filtros, então não há efeito.
- Se entrar um segmentador sincronizado de `dPersonagem`, conferir `gr` e `in` (que viram 0 com `+0`).

**M13. Catálogo de medidas fica desatualizado em relação ao §7.**
- O catálogo registra a troca das medidas de §7.1–7.3 por JS, mas `docs/plano.md` §7 e o gate F4a ("DAX Studio")
  continuam descrevendo o desenho antigo.
- Sugiro que o orquestrador ajuste o texto do gate para "1º render da medida < 1,5 s".

### Contrato e números

- `js-data-schema.json` v0.2: as 10 chaves de topo e os campos `required` de `p`, `v`, `ar`, `er`, `af` e `g` estão
  presentes. `t` é int 0/1 (`EhTransformacao` é `int64` no TMDL, sem risco de virar `True`). `in` usa `FORMAT en-US`.
  Os demais números são `int64` no TMDL e concatenados sem separador decimal. A matriz usa `FORMAT "0.0#" en-US`.
- `ALLNOBLANKROW` está em todas as dimensões iteradas. As tabelas fato e ponte usam `ALL`, sem membro em branco. O
  teste de regressão existe (`test_js_gotham_itera_dimensoes_sem_membro_em_branco`).
- Os números do handoff batem com o que medi: 224 testes, mock com 26.424 caracteres, `HTML Batcomputador` dentro do
  orçamento e o catálogo citando ~26,6 mil.

### O que não foi possível verificar

- Vitest **não executado** (sem Node). A conclusão "passa" vem só de leitura.
- O tempo do 1º render da medida no Power BI (DAX Studio / Analisador de desempenho). Não toquei no Desktop.
- A saída real da medida no Power BI. Comparei só o mock com o DAX, por leitura.
- A emulação real de `prefers-reduced-motion`, que verifiquei só por leitura do CSS e do JS.
- O contraste por amostragem de pixel. B1 vem de cálculo sobre os estilos computados.
- Lore: não refiz a amostra de 10 fatos. Os dados são os da F1/F2, já revisados. Batman (Detective Comics #27, 1939) e
  Espantalho (World's Finest Comics #3, 1941) conferem.

### Para aprovar

1. Corrigir B1 e reenviar com o contraste do item selecionado ≥ 4,5:1 em todos os temas.
2. Recomendado na mesma volta: M1, com teste; M2; M3.

---

## Revisão: F4 — ciclo 2 (Coruja)

- **Veredito: REPROVADO.** O **B1 continua**: a correção do texto não chega a ser aplicada por causa da cascata do CSS.
  O contraste efetivo do texto secundário do item selecionado é **4,40:1**, abaixo de 4,5:1. A correção é mover uma
  linha. Os itens M1–M10 e M12 foram corrigidos e eu os confirmei. Encontrei 3 achados MENORES novos (N1–N3), nenhum
  bloqueante.

### Saída dos comandos

| Comando | Resultado |
|---|---|
| `.venv/Scripts/python -m pytest -q` | **226 passed** em 2,2 s |
| `.venv/Scripts/python build/checks.py` | **APROVADO**. `HTML Batcomputador` tem 32.395/40.000 caracteres literais e `JS Gotham` tem 650/20.000 |
| `.venv/Scripts/python build/mock_gotham.py` | `OK: window.GOTHAM mock com 26,424 caracteres` |
| `.venv/Scripts/python build/build_preview.py` | `OK: dist\preview\batcomputador.html (58,819 chars)` |
| aspas duplas | 0 em `batcomputador.js` e 0 em `batcomputador.html` |
| Vitest | não rodado (sem Node). Por leitura, o caso novo `agruparRelacoes` passa: a ordenação estável dá `[6,19]` e os rótulos `['família','pupilo','lidera']` |

### BLOQUEANTE

**B1 (persiste). `.bc-sel small` perde para `.bc-in small` na cascata.**
`src/css/batcomputador.css:44` versus `:48`
- As duas regras têm especificidade (0,1,1) e `.bc-in small { color: var(--g-muted) }` vem **depois**. Por isso o
  texto do item selecionado continua em `--g-muted`.
- **Reprodução no preview:** `getComputedStyle(document.querySelector('.bc-sel small')).color` retorna
  `rgb(125, 135, 148)`, não `--g-text`. Sobre o fundo opaco `#22221a`, isso dá **4,40:1** (calculado com a mesma
  fórmula do `test_pbip.contraste`).
- O fundo opaco funcionou: o selecionado é `rgb(34,34,26)` e os demais itens `rgb(16,20,26)`, sem dependência do tema.
- O teste `test_contraste_aa_do_item_selecionado_da_lista` dá **falso positivo**: ele só confere que a string
  `.bc-sel small { color: var(--g-text); }` existe e o contraste de `--g-text`, não a regra que vence na cascata.
- **Correção:** trocar o seletor para `.bc-sel .bc-in small` ou movê-lo para depois da linha 48. No teste, verificar a
  ordem ou a especificidade, ou medir o contraste de `--g-muted` sobre o fundo.

### Itens do ciclo 1 conferidos

| Item | Situação | Como verifiquei |
|---|---|---|
| M1 escape | ✅ | Todos os 21 campos de texto de `JS Gotham.dax` passam por `\`, `'`, `</`, LF→`\n` e CR→`\r`. A ordem está certa (a barra invertida é escapada primeiro). O teste novo pega `'" & coluna` cru, e o mock escapa os mesmos campos |
| M2 sem dados | ✅ | Com `GOTHAM` removido e o app rodando sozinho, o cabeçalho mostra "dados indisponíveis — atualize o relatório". O app se recupera no redesenho seguinte |
| M3 select | ✅ | ↓ em `#bc-alin` não é cancelado e o personagem não muda. No campo de busca, ↓ troca o personagem e mantém o foco no input, o que é intencional |
| M4 larguras | ✅ | Sem overflow nem corte em 760, 780, 900, 950 e 1280 px. A ≤ 900 px o layout tem 2 colunas e o painel lateral fica embaixo |
| M5 holofote | ✅ | `from 345deg`: o feixe aparece, conferido no ciclo 1 com o mesmo ângulo |
| M6 aria-pressed | ✅ | Após o redesenho com o filtro ativo, o botão mostra `★` com `aria-pressed='true'` |
| M7 teclado | ✅ | Enter no item 7 seleciona e o foco fica no item. ↓ depois disso vai para o 8. A estrela é um `<button aria-label='Favoritar …' aria-pressed>`. Depois de clicar numa relação, o foco vai para o item selecionado e ↓ continua funcionando |
| M8 erro na ficha | ✅ | Forcei `p.er=999`: o erro substitui `#bc-ficha` e `#bc-lado` fica vazio |
| M9 relações | ✅ | Ra's al Ghul mostra 6 pessoas, sem nomes repetidos ("Damian Wayne — família · pupilo · lidera") |
| M10 versão padrão | ✅ na medida | `MINX` das versões que não são transformação. Ver N1 |
| M12 centralidade | ✅ | `FILTER(ALLNOBLANKROW(dCentralidade))` com `MAXX` |
| Redesenho | ✅ | O estado é igual antes e depois, e resta 1 `#bc-raiz` após 20 redesenhos. Um clique na estrela alterna uma única vez. Console sem mensagens |

### MENORES novos

**N1. O mock não acompanhou o M10.**
`build/mock_gotham.py:57`
- O mock continua com `v:{IdPersonagem*100+1}`, enquanto a medida usa `MINX` das versões que não são transformação.
- Com os dados atuais o resultado é igual (1 versão por personagem, todas com `EhTransformacao = 0`), mas mock e medida
  divergem de novo.
- Além disso, se um personagem tiver só versões de transformação, `MINX` retorna branco e a medida gera `v:,`, um
  `SyntaxError` que derruba o objeto inteiro. Sugiro usar `COALESCE` com o menor `IdVersao` de qualquer versão.

**N2. Lista com 100 paradas de Tab e controle aninhado em `role='option'`.**
`src/js/batcomputador.js:150-152`
- Cada item tem `tabindex='0'` e contém um `<button>`, o que dá 111 elementos focáveis na raiz.
- O padrão de listbox pede *roving tabindex*: só o item selecionado com `tabindex=0`, os demais com `-1`.
- Um botão dentro de `option` é conteúdo interativo aninhado, que leitores de tela tratam mal.
- Não bloqueia, porque ↑/↓ e Enter funcionam.

**N3. Selects estreitos entre 901 e ~1000 px.**
- Na faixa de 3 colunas os filtros ficam com 51 px a 950 px e o rótulo aparece cortado ("Alin…").
- Sugiro aplicar `.bc-filtros { grid-template-columns: 1fr 1fr }` já a partir de ~1050 px.

### Sem mudança

- M11 e M13 continuam como pendências documentadas.
- Continuam sem verificação: Vitest executado, 1º render da medida no Power BI, emulação real de
  `prefers-reduced-motion` (os seletores do bloco não mudaram), contraste por pixel e saída real da medida.
- Observação: no navegador embutido, o `#visual` do harness tinha `width:1280px` inline, deixado por outra sessão no
  mesmo painel. Removi esse estilo apenas no DOM do preview antes de medir as larguras. Nenhum arquivo foi alterado.

### Para aprovar

Corrigir B1 (seletor e teste). N1 é recomendado na mesma volta.

---

## Revisão: F4 — ciclo 3 (Coruja)

- **Veredito: APROVADO.** O B1 está resolvido e confirmei a correção pela cor **computada** no preview. Os gates F4a
  (orçamento), F4b (contraste AA e `prefers-reduced-motion`) e F4c (0 aspas duplas, testes, mock) estão cumpridos. N1,
  N2 e N3 foram corrigidos. Encontrei 1 achado MENOR novo de foco (P1) e 1 divergência de número no handoff (P2),
  nenhum bloqueante.

### Saída dos comandos

| Comando | Resultado |
|---|---|
| `.venv/Scripts/python -m pytest -q` | **226 passed** em 2,0 s |
| `.venv/Scripts/python build/checks.py` | **APROVADO**. `HTML Batcomputador` tem 33.175/40.000 caracteres literais e `JS Gotham` tem 650/20.000 |
| `.venv/Scripts/python build/mock_gotham.py` | `OK: window.GOTHAM mock com 26,424 caracteres` |
| `.venv/Scripts/python build/build_preview.py` | `OK: dist\preview\batcomputador.html (59,599 chars)` |
| aspas duplas | 0 em `batcomputador.js` e 0 em `batcomputador.html` |
| Vitest | não rodado (sem Node). Os 14 casos não mudaram de lógica em relação ao ciclo 2 e, por leitura, passam |

### B1: conferido pela cor computada

- `.bc-sel .bc-in small` tem especificidade (0,2,1) e vence `.bc-in small` (0,1,1), que está em `css:48`.
- No preview, `getComputedStyle(document.querySelector('.bc-sel small')).color` retorna **`rgb(215, 221, 228)`**
  (`--g-text`) sobre **`rgb(34, 34, 26)`**, o que dá **11,7:1**. Repeti nos temas Espantalho, Coringa, Vagalume,
  Bat-família e Gotham, e os valores computados são idênticos (o fundo é opaco).
- Itens não selecionados ficam em `--g-muted` sobre `rgb(16,20,26)`, ou seja 5,07:1.
- O teste agora recusa o seletor fraco `.bc-sel small {` e documenta que `--g-muted` sobre `#22221a` fica abaixo de 4,5.

### N1–N3

| Item | Situação | Verificação |
|---|---|---|
| N1 versão padrão | ✅ | A medida usa `COALESCE(MINX das versões que não são transformação, MINX de todas as versões do personagem, 0)` e nunca gera `v:,`. `mock_gotham.versao_padrao` segue a mesma regra. Com `v:0`, o JS cai no `seguro` e mostra um aviso, sem quebrar |
| N2 roving tabindex | ✅ | Na lista, só 1 elemento tem `tabindex=0`. As 50 estrelas têm `tabindex=-1`. Na raiz há 7 paradas de Tab sem as relações, contra 111 no ciclo 2. Com o selecionado fora do filtro, o 1º item visível recebe `tabindex=0` sem ficar `aria-selected` |
| N3 filtros | ✅ | 2 colunas abaixo de 1100 px. Os selects ficam com 99 px a 950 px, 104 px a 760 px e 75 px a 1280 px (3 colunas) |

### Teclado e foco (regressões procuradas)

| Cenário | Resultado |
|---|---|
| Clique num item | Seleciona e põe o foco no item |
| ↓/↑ no item | O foco e a seleção acompanham (1→2→1). ↑ no topo mantém o 1 |
| F / f no item | Alterna o favorito, mantém o foco e atualiza o `aria-pressed` da estrela |
| Enter / Espaço no item | Seleciona e cancela o padrão. O foco fica no item |
| ↓ dentro de `<select>` | Não é cancelado e o personagem não muda (M3 mantido) |
| ↓ no campo de busca | Troca o personagem e mantém o foco no input. `f` digitado na busca **não** favorita |
| Clique numa relação | Seleciona o personagem, o foco vai para o item na lista e ↓ continua funcionando |
| Redesenho com script (1 + 20 vezes) | O estado fica igual, resta 1 `#bc-raiz`, 1 item com `tabindex=0` e `aria-pressed` correto. 0 `.bc-erro`, console sem mensagens |
| Larguras 760 / 950 / 1280 px | Sem overflow e sem elementos cortados em nenhuma coluna |

### MENORES novos

**P1. O foco se perde ao desfavoritar com "Só favoritos" ativo.**
`src/js/batcomputador.js` (bloco da tecla F no `keydown`)
- **Reprodução:** com favoritos `[1,7]`, ative "Só favoritos", foque o item 1 e pressione F. O item sai da lista,
  `document.activeElement` vira `body` e ↓/↑ param de responder até a pessoa clicar ou dar Tab.
- **Sugestão:** quando o item não existir mais, focar o elemento com `tabindex=0` da lista, ou `#bc-raiz`.
- Cenário restrito. Não bloqueia.

**P2. Divergência de número no handoff.**
- O handoff do ciclo 3 diz "132 px a 950 px" para os selects. Eu medi 99 px no mesmo viewport.
- Não há corte de texto, e a legibilidade está ok. É só para corrigir o número.

### Pendências que continuam (não bloqueiam este gate)

- M11: cores fixas fora dos tokens.
- M13: §7 do plano e texto do gate F4a.
- Tempo do 1º render da medida no Power BI, a medir até a F6.
- Vitest executado em CI.
- Emulação real de `prefers-reduced-motion`, verificada só por leitura.
- No preview, o `#visual` do harness voltou a abrir com `width:1280px` inline. Removi esse estilo só no DOM antes de
  medir. Nenhum arquivo foi alterado.
