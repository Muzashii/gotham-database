## Entrega: F3 — modelo semântico em estrela (Gordon)

- **Status:** pronto para revisão
- **Arquivos alterados:** `build/modelo_spec.py`, `build/build_tabelas.py`,
  `powerbi/GothamDatabase.SemanticModel/definition/{expressions,relationships,model}.tmdl`,
  `.../tables/*.tmdl` (18 curadas + 5 desconectadas), `tests/bpa/test_bpa.py`, `contracts/data-dictionary.md`
  (seção gerada), CI, `CLAUDE.md`
- **Decisões tomadas (e por quê):**
  - **TMDL gerado a partir do contrato** (`etl/quality/schemas.py`): colunas e tipos nunca divergem do ETL; decisões
    de modelagem isoladas em `modelo_spec.py`. Teste de sincronia como no `_Medidas.tmdl`.
  - **Power Query lê do GitHub**: função `LerCsv` com `Web.Contents("https://raw.githubusercontent.com",
    [RelativePath=…])` — URL base fixa, o padrão que o serviço consegue atualizar sem gateway. `Encoding=65001`,
    tipos com cultura `en-US` (o modelo é pt-BR: sem isso `0.5` viraria 5).
  - **23 relações N:1 unidirecionais, 16 ativas**. As 7 inativas evitam caminhos ambíguos (que o Power BI recusa)
    ou são a 2ª relação para a mesma tabela; o motivo de cada uma está no dicionário. Ex.: era de estreia do
    personagem e arquétipo da versão serão usados via `USERELATIONSHIP` nas medidas da F4a.
  - **Nenhum filtro bidirecional**: a ponte de afiliações filtra via `TREATAS` no DAX (plano §6.2).
  - Colunas `Id*` (regex `Id[A-Z]`) e técnicas ocultas; `summarizeBy: none` em tudo exceto `EdicoesComicVine`;
    ordenações (Era por Ordem, Mídia por Id, Stat por Ordem, Arquétipo por Id); `dataCategory: ImageUrl` nas URLs.
  - **Desconectadas:** `Modo` e `TemaSel` estáticas; `VersaoSel`, `RelacaoSel`, `ObraSel` referenciam as consultas
    de dimensão (sem relação).
  - `SpikeTamanho` **mantida** (o plano dizia remover na F3): o link público ainda mostra a página F0 e depende dela.
    Sai quando a página do Batcomputador substituir o spike (F5).
  - **BPA:** Tabular Editor não está instalado; 15 regras equivalentes + teste de sincronia em `tests/bpa` (ambiguidade
    de caminhos, bidirecional, FKs ocultas, tipos iguais nas relações, unicidade do lado 1 nos dados, soma implícita,
    chaves não flutuantes, descrições, sortBy, refs). O teste de BPA já pegou um bug do gerador
    (`IdentidadeCivil` tratada como chave e ocultada).
- **Validação no Power BI Desktop 2.159 (18/10/2026):** "Aplicar alterações externas" carregou o TMDL sem erro;
  atualização a partir do GitHub (acesso anônimo) carregou as 25 tabelas — conferidos `dObra` 319 linhas,
  `dPersonagem` 50, `dStat` 6, acentos corretos; exibição de modelo com as relações esperadas. O Desktop não
  regravou arquivos (teste de sincronia verde depois).
- **Contratos afetados:** `data-dictionary.md` — nova seção "Modelo semântico (F3)" gerada.
- **Como testar:** `python build/build_tabelas.py && python -m pytest tests/bpa -q`; abrir o `.pbip` e Atualizar.
- **Pendências / riscos:** BPA oficial do Tabular Editor não rodado; atualização no **serviço** (publicado) não
  testada nesta fase; descrições das tabelas incluem a linha "Gerado por…" (cosmético).

### Pós-revisão (achados de `review-F3.md`, veredito APROVADO)
- **M1** `dVersao.IdMidia → dMidia` ativada (o motivo "ambígua" era falso; o teste de ambiguidade confirma).
- **M2** `dGadget.SoContraArquetipo → dArquetipo` inativada (vazio = gadget universal; ativa, sumiria no filtro).
- **M3** comentários/dicionário atualizados (`SpikeTamanho` mantida até a F5; dicionário v0.4; relações N:1 com cadeias dim→dim).
- **M4** nova regra no BPA local: toda relação é muitos-para-um.
- **M6** `LerCsv` converte célula vazia em `null` (verificado no Power Query: `Plataforma`/`UrlCapa` = null).
- **M7** `Plataforma` e `EdicoesComicVine` ocultas enquanto vazias. **M8** sem "Gerado por…" nas descrições.
- **M5** (`returnErrorValuesAsNull`, propriedade do Desktop) e **M9** (Desktop regrava anotações): pendências; o fluxo
  é rodar `build_tabelas.py`/`build_model.py` depois de salvar no Desktop, e o teste de sincronia acusa se esquecer.
- Teste de schema PBIR: pula (não falha) quando o Desktop grava uma versão de schema que a Microsoft ainda não publicou.

### Publicação (18/10/2026, 22:56)
Modelo novo publicado no Meu workspace substituindo o anterior; o link público continua funcionando (página F0).
A atualização agendada no serviço **não** foi configurada (credencial anônima da fonte web pendente no serviço).
