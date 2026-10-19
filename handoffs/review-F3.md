## Revisão: F3 — modelo semântico em estrela (Coruja)

- **Veredito: APROVADO** (gate F3 cumprido: nenhum erro crítico de BPA e dicionário completo). Não há achados
  BLOQUEANTES. Há 9 achados MENORES; 1 a 3 devem ser corrigidos antes ou durante a F4a.
- **Escopo:** `build/modelo_spec.py`, `build/build_tabelas.py`, `definition/{expressions,relationships,model}.tmdl`,
  `definition/tables/*.tmdl` (18 curadas + 5 desconectadas), `tests/bpa/test_bpa.py`, seção gerada de
  `contracts/data-dictionary.md`, handoff `F3-modelador-semantico-modelo.md`. O Power BI Desktop não foi tocado.

### Saída dos comandos (rodados na raiz, Python do venv)

| Comando | Resultado |
|---|---|
| `.venv/Scripts/python -m pytest -q` | **218 passed** em 1,9 s (o `tests/bpa` sozinho tem 42) |
| `.venv/Scripts/python build/checks.py` | **APROVADO: checks.py sem erros** (todas as medidas dentro do orçamento) |
| `.venv/Scripts/python build/build_tabelas.py` | `OK: 23 tabelas, 23 relações (16 ativas)` |
| idempotência | o md5 de todos os arquivos em `definition/` e `contracts/` é igual antes e depois, e o `git status --porcelain` também. **A geração é idempotente.** |
| `npm test` (Vitest) | **não rodado**: Node não está instalado nesta máquina. A F3 não mexe em JS. |

### Conferências feitas (fatos confirmados)

- **Números do handoff batem:** 18 curadas + 5 desconectadas = 23 arquivos gerados; com `_Medidas` e `SpikeTamanho` são 25
  tabelas no `model.tmdl`. São 23 relações, 16 ativas e 7 inativas. São 15 testes de regra mais a sincronia
  em `test_bpa.py`. `dObra` tem 319 linhas, `dPersonagem` 50 e `dStat` 6 nos CSVs.
- **Ambiguidade:** com o mesmo algoritmo do teste, simulei a ativação de cada relação inativa, uma por vez. Em 6 das 7,
  ativar a relação cria de fato um caminho ambíguo ou uma segunda relação para o mesmo par. A exceção, `dVersao.IdMidia`,
  é o achado M1.
- **Dados x modelo:** os cabeçalhos dos 18 CSVs têm as mesmas colunas do contrato. Em `dPersonagem` a ordem difere
  (`confianca`), mas isso não importa porque `TransformColumnTypes` é por nome. Todo valor em coluna `int64` é inteiro
  puro e todo valor em `double` está no formato `en-US`. As 23 relações, inclusive as inativas, não têm chaves órfãs.
  O lado 1 é único em todas.
- **CSV:** nenhum arquivo tem BOM. `Encoding = 65001` e `QuoteStyle.Csv` tratam os campos com vírgula entre aspas, que
  existem em `dPersonagem`.
- **Power Query:** `Web.Contents` tem URL base literal e a parte variável só em `RelativePath`, que é o padrão aceito pelo
  serviço como fonte não dinâmica. A cultura `en-US` está em todas as 18 partições. As desconectadas `VersaoSel`,
  `RelacaoSel` e `ObraSel` só referenciam consultas e não acessam fonte diretamente, então não há risco de
  Formula.Firewall. O `#table` com `Int64.Type` usa o mesmo padrão do `SpikeTamanho`, já validado na F0.
- **TMDL:** os `lineageTag` são únicos em todo o modelo e os `sortByColumn` apontam para colunas existentes.
  `dataCategory: ImageUrl` está em `UrlImagem` e `UrlCapa`. `///` aparece só antes de tabelas e expressões, nunca em
  relações. Nomes simples dispensam aspas. Todas as FKs estão ocultas. `IdentidadeCivil` está visível, o que é o correto.
- **TemaSel:** as 10 facções batem com as classes `fx-*` de `contracts/design-tokens.md`.
- **SpikeTamanho mantida:** decisão **razoável**. A página `gdF0Spike` (visuais `gdSpikeSlicer` e `gdSpikeTamanho`) e as
  medidas `Spike Tamanho*` dependem dela, e o link público ainda mostra essa página. Removê-la agora quebraria a
  publicação da F0. Ver M3, porque a documentação ficou contraditória.

### Viabilidade das medidas e páginas planejadas (§3 e §7) com estas relações

| Uso | Viável? | Como |
|---|---|---|
| Lista do Batcomputador × **afiliação** | Sim | O filtro vai de dAfiliacao para a ponte e não chega a dPersonagem, então a lista precisa de um filtro de visual por medida, por exemplo `COUNTROWS(bPersonagemAfiliacao) > 0` no contexto da linha, ou `TREATAS`. Um segmentador nativo aceita filtro de medida no nível do visual. Isso não foi testado aqui. |
| Lista × **era de estreia** | Sim | Medida `CALCULATE(COUNTROWS(dPersonagem), USERELATIONSHIP(dPersonagem[IdEra], dEra[IdEra]))` como filtro do visual. Atenção: um segmentador de `dEra` em qualquer página significa, por padrão, a "era da obra". Cuidado ao sincronizar segmentadores entre páginas. |
| Grafo de relações | Sim | Serialização em JS. A medida "relações do selecionado" precisa unir Origem (ativa) e Destino (`USERELATIONSHIP` ou `TREATAS`), porque os tipos simétricos estão gravados uma vez só, com Origem < Destino. |
| Matriz de arquétipos | Sim, via HTML | Uma matriz nativa ataque × defesa não é possível com uma única `dArquetipo`, pois não dá para pôr a mesma coluna nos dois eixos. A medida HTML itera `fMatchup`. Para uma matriz nativa seria preciso uma cópia de papel, `dArquetipoDefesa`. |
| Linha do tempo por obra/era/mídia | Sim | Caminhos dEra→dObra→fAparicao e dMidia→dObra→fAparicao, ambos ativos. |
| Painel do Comissário (década × mídia, top vilões, mapa de calor) | Sim | Não existe coluna de década. Na F4a ela pode virar coluna calculada ou passo no M (`Number.IntegerDivide([Ano],10)*10`). `Granularidade` (Obra/Série/Episódio) precisa ser filtrada para não haver contagem dupla, como o dicionário já avisa. |
| Arquétipo da versão (`USERELATIONSHIP` em dVersao.IdArquetipo) | Provável | Ativar a relação cria ambiguidade com dArquetipo→dPersonagem→dVersao. O DAX resolve em tempo de consulta pelo caminho mais curto e não dá erro, mas isso não foi verificado. Por segurança, incluir `CROSSFILTER(dPersonagem[IdArquetipo], dArquetipo[IdArquetipo], NONE)`, ou usar `LOOKUPVALUE` nas medidas da Arena. |

### Achados

Nenhum BLOQUEANTE.

**M1 (MENOR): uma relação inativa sem necessidade e com motivo errado.** Em `build/modelo_spec.py:40` e
`contracts/data-dictionary.md:100`, `dVersao.IdMidia → dMidia` aparece como "ambígua com dMidia→dObra→fAparicao".
Isso é falso: `fAparicao.IdVersao` já é inativa, então dMidia chega a fAparicao por um caminho só.
Reprodução: aplicar a função de caminhos de `test_erro_relacoes_ativas_sem_caminho_ambiguo` com essa relação ativada
devolve `[]`, ou seja, nenhum par ambíguo. Efeito: um segmentador de mídia não filtra versões (carrossel "Versões" por
mídia, mapa de calor) sem `USERELATIONSHIP`. Correção: ativar a relação ou corrigir o motivo.

**M2 (MENOR): semântica de `dGadget.SoContraArquetipo → dArquetipo` (ativa) contrária ao contrato.** Em
`build/modelo_spec.py:56`, o dicionário (linha 34) diz que o campo vazio significa "vale para todos". No Power BI, as
linhas com FK vazia se ligam à linha em branco da dimensão. Assim, um filtro em `dArquetipo` esconde justamente os
gadgets universais (3 de 4 têm o campo vazio, conferido no CSV). Hoje o impacto é baixo, porque a Patrulha deve
serializar todos os gadgets em JS. Recomendação: deixar a relação inativa, ou registrar a ressalva no dicionário.

**M3 (MENOR): documentação desatualizada e contraditória.**
- `tables/SpikeTamanho.tmdl:2` e `contracts/data-dictionary.md:14` ainda dizem "Remover na F3". O handoff diz "sai na F5".
- `contracts/data-dictionary.md:4` ainda diz "Versão: 0.3 (F2)… o modelo TMDL segue na F3".
- O dicionário (linha 6 e cabeçalho da linha 92) diz "das dimensões para os fatos", mas o modelo tem snowflakes
  dimensão→dimensão (dArquetipo→dPersonagem, dEra/dMidia→dObra, dPersonagem→dVersao/dCentralidade, dArquetipo→dGadget).
  Funciona, mas o texto deveria dizer isso.

**M4 (MENOR): o BPA local cobre os críticos, mas omite avisos que o BPA oficial acusaria (falsos negativos de severidade
média).** O cabeçalho de `tests/bpa/test_bpa.py:3` diz que avisos "também falham aqui", mas o subconjunto não testa:
- ponto flutuante: há 5 colunas `double` (`Multiplicador`, `MultCaptura`, `BonusCaptura`, `Intermediacao`, `PageRank`);
  a regra oficial "Do not use floating point data types" sugere decimal fixo;
- snowflake: a regra "Consider a star-schema instead of a snowflake";
- cardinalidade/`toCardinality`: `ler_relacoes` em `test_bpa.py:43-52` não lê a cardinalidade, então uma relação
  muitos-para-muitos passaria;
- `IsAvailableInMdx` em colunas não atributo e formatação de flags 0/1 (`EhEstreia`, `EhTransformacao`, `TemRecarga`).

Os críticos (severidade 3 no BPA) relevantes estão cobertos: tipos iguais nas relações, coluna de origem, ambiguidade,
unicidade do lado 1 e bidirecional. Integridade referencial fica em `tests/etl`. Também não há teste que confira se o
GitHub (fonte real do modelo) tem os mesmos CSVs do disco local que o teste de unicidade lê. Hoje `main...origin/main`
está sincronizado.

**M5 (MENOR, risco): erros de conversão de tipo seriam silenciados.** `model.tmdl:8` tem `returnErrorValuesAsNull`
(padrão do Desktop, anterior à F3). Se um dia o ETL gravar algo não inteiro numa coluna `Int64`, o valor vira BLANK sem
aviso. Sugestão para a F4a/F6: uma medida ou teste de reconciliação de contagem de não vazios contra os CSVs.

**M6 (MENOR): texto vazio continua `""`, não `null`.** `Table.TransformColumnTypes` com `type text` mantém a string
vazia. Exemplos: `dPersonagem.Codinome` (7/50), `dGolpe.Efeito` (13/24), `dGadget.Efeito`, `dVersao.UrlImagem`
(19/50). Na F4a, `ISBLANK()` sobre essas colunas dá FALSE. Usar `= ""` ou `LEN() = 0`, ou converter `""` em `null` no M.

**M7 (MENOR): colunas visíveis sem conteúdo ou com nome técnico.**
- `dObra.Plataforma` está 100% vazia (319/319) e visível.
- `dPersonagem.EdicoesComicVine` está 100% vazia e é a única coluna com `summarizeBy: sum`.
- `confianca` aparece em minúsculas e visível em `dPersonagem` e `dVersao`, fora da convenção PascalCase.

Herança do contrato F2, não da F3. Fica registrado para não aparecer no painel de campos.

**M8 (cosmético, já declarado no handoff):** a descrição das tabelas inclui a linha "Gerado por… NÃO EDITAR À MÃO."
(`build/build_tabelas.py:55`), que aparece na dica de ferramenta do painel de campos. As desconectadas repetem
"Desconectada: Cópia desconectada…" (`build_tabelas.py:82` com `modelo_spec.py:96`).

**M9 (MENOR, suspeita): `annotation SummarizationSetBy = Automatic`.** Está junto de `summarizeBy: none` explícito e
de `LerCsv` ausente de `PBI_QueryOrder`. O Desktop pode regravar isso ao salvar (`User`, ordem de consultas). Nesse
caso o teste de sincronia acusa e rodar `build_tabelas.py` de novo resolve. O handoff diz que o Desktop não regravou,
mas não está claro se houve **salvamento**. Isso não foi verificado.

### O que não foi possível verificar

- **Carga no Power BI Desktop:** o Desktop está aberto pelo orquestrador e não foi tocado. A carga sem erro e as
  contagens dependem do relato do handoff.
- **Conteúdo servido pelo GitHub raw:** a consulta HTTP foi negada pelo classificador de permissões. Pelo git, o
  `data/curated` está commitado e `main` está sincronizado com `origin/main`.
- **Atualização no serviço** (credencial anônima, agendamento): não foi testada, nem por mim nem pelo autor.
- **BPA oficial do Tabular Editor:** não instalado.
- **Vitest:** sem Node.
- **Conversão de `""` para `null` em `Int64.Type`:** é o comportamento esperado do Power Query e é coerente com a carga
  relatada, mas está mascarada por `returnErrorValuesAsNull` (M5).
- **Desempate de ambiguidade com `USERELATIONSHIP` em `dVersao.IdArquetipo`:** não verificado.
- **Lore:** a F3 não introduz fatos de lore novos (só rótulos de tema e descrições), então não houve amostragem nesta
  fase.

### Recomendações para fechar

1. M1: ativar `dVersao.IdMidia` ou corrigir o motivo.
2. M3: atualizar o texto do `SpikeTamanho` e o cabeçalho do dicionário.
3. M2: deixar `dGadget.SoContraArquetipo` inativa ou documentar a ressalva.

Os demais achados podem ir para a F4a ou F6.
