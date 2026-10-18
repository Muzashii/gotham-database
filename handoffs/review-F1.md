# Revisão F1 — Curadoria (Oráculo) + seeds de game design (Ra's)

- **Revisor:** Coruja (revisor-qa), revisão independente, 18/10/2026
- **Escopo:** `data/seeds/*.csv`, `etl/extract/*.py`, `etl/curadoria/*.py`, `docs/fontes.md`,
  `contracts/data-dictionary.md` v0.2, handoffs `F1-curador-lore-personagens.md`, `F1-game-designer-seeds.md`,
  `F1-checagem-fatos.md`

## Veredito: **REPROVADO** (1 bloqueante, correção pequena)

Os critérios formais do gate F1 (plano §12) foram atingidos: 100% das linhas dos 14 seeds têm `fonte`, e há
27 estreias confirmadas em 2+ fontes (o mínimo é 20). Mesmo assim, a amostragem independente achou um fato de
lore **errado** num seed que o dicionário declara congelado ao fim da F1 (B1). A correção é de 2 células e a
nova revisão pode ser rápida. Os itens MENORES não impedem a aprovação, mas vale corrigir M1 a M4 no mesmo ciclo.

## Saída dos comandos

```
.venv/Scripts/python -m pytest -q
125 passed in 0.41s

.venv/Scripts/python build/checks.py
... (orçamentos das medidas do spike dentro do limite)
APROVADO: checks.py sem erros

.venv/Scripts/python -m etl.curadoria.checar
27/50 estreias com 2+ fontes concordantes -> handoffs/F1-checagem-fatos.md   (exit 0)
```

Observação: o `checar` regrava `handoffs/F1-checagem-fatos.md` toda vez que roda. A saída reproduziu a mesma
contagem (27/50).

Verificações extras que rodei por script (sem alterar arquivos):
- `confianca` em personagens: alta 26, media 6, baixa 18. **Bate** com o handoff.
- Arquétipos: EST 9, FUR 9, LUT 7, TEC 7, PSI 6, MET 5, BRU 4, MIS 3. **Bate** com o handoff.
- Afiliações: Bat-família 15, GCPD 3, Liga das Sombras 3 (+ Damian como ex-membro), Galeria 27. **Batem** com o handoff.
- `IdEra` coerente com `AnoEstreia` nos 50 personagens e com `Ano` nas 48 obras. Ano da obra = `AnoEstreia`
  do personagem em todas as estreias. Título da obra = prefixo de `PrimeiraAparicao`.
- `IdArquetipo` da versão = do personagem nas 50 versões. Cada versão tem 4 golpes (3 do arquétipo + 1 de cobertura).
- `matchup.csv`: as 64 células são idênticas à matriz do plano §8.2.
- `encontros.csv`: só não-heróis, e a `Raridade` é igual à da versão nas 42 linhas.
- Aspas duplas: só aparecem como delimitador CSV de campo com vírgula. Nenhum valor de texto contém `"`
  (o teste `test_sem_aspas_duplas_nos_textos` confirma).

## Amostragem independente: 10 fatos de lore (nenhum usa a Wikipédia em inglês)

Fandom e GCD devolveram 402/403 ao acesso automatizado. Por isso usei dc.com (oficial), DCU Guide e as
Wikipédias em francês e alemão.

| # | Personagem (linha) | confianca | Fato checado (seed) | Fonte independente | Veredito |
|---|---|---|---|---|---|
| 1 | Signal (`personagens.csv:12`) | baixa | estreia Batman (vol. 2) #21, **AnoEstreia 2014** | dc.com/characters/signal: First Appearance BATMAN #21 (2013); keycollectorcomics: capa de agosto de 2013 | **ERRADO**: edição ok, ano é 2013 (ver B1) |
| 2 | Batman Que Ri (`:48`) | baixa | Dark Days: The Casting #1 (**jul** 2017), 2017 | dcuguide.com/Dark_Days:_The_Casting_1: Cover Date September 2017; estreia em cameo, nas sombras | Edição e ano ok. **Mês** está fora da convenção: jul é a data de venda, a capa é set (M1) |
| 3 | Lady Shiva (`:44`) | baixa | Sandra Wu-San; Richard Dragon, Kung Fu Fighter #5 (dez 1975); O'Neil/Estrada | fr.wikipedia.org/wiki/Lady_Shiva | **CONFIRMADO** (nome, edição, mês, criadores) |
| 4 | Talia al Ghul (`:43`) | baixa | Detective Comics #411 (mai 1971) | fr.wikipedia.org/wiki/Talia_al_Ghul | **CONFIRMADO** |
| 5 | Vagalume (`:35`) | baixa | Detective Comics #184 (jun 1952); Herron/Sprang | dcuguide.com/Firefly_(Garfield_Lynns)_Chronology | **CONFIRMADO** |
| 6 | Crocodilo (`:31`) | media | Waylon Jones; Detective Comics #523 (fev 1983) | de.wikipedia.org/wiki/Killer_Croc: Waylon Jones; Erstauftritt Batman #357 (1983) | Nome e ano **CONFIRMADOS**. A edição diverge (cameo #523 contra #357), mas isso já está documentado em `nota` e reflete a `confianca` media |
| 7 | Cassandra Cain (`:9`) | media | Batman #567 (1999); Puckett/Scott | fr.wikipedia.org/wiki/Cassandra_Cain | **CONFIRMADO** |
| 8 | Alfred Pennyworth (`:3`) | alta | Batman #16 (abr–mai 1943); criadores Cameron/Kane | fr.wikipedia.org/wiki/Alfred_Pennyworth: Batman #16 (avril-mai 1943), criado por Kane e Robinson | Estreia **CONFIRMADA**. Criadores divergem, e o seed já marca isso como pendente (ver M6) |
| 9 | Hera Venenosa (`:26`) | alta | Pamela Isley; Batman #181 (jun 1966); Kanigher/Moldoff | de.wikipedia.org/wiki/Poison_Ivy_(Comics) | **CONFIRMADO** |
| 10 | Solomon Grundy (`:41`) | alta | Cyrus Gold; All-American Comics #61 (out 1944); Bester/Reinman | fr.wikipedia.org/wiki/Solomon_Grundy_(comics) | **CONFIRMADO** |

Resultado: 7 confirmados por inteiro, 2 confirmados com divergência já documentada (Crocodilo, Alfred),
1 ano errado (Signal) e 1 mês fora da convenção (Batman Que Ri).

## Achados

### BLOQUEANTE

**B1. O ano de estreia do Signal está errado (2014; o certo é 2013).**
- Onde: `data/seeds/personagens.csv:12` (`PrimeiraAparicao` = `Batman (vol. 2) #21 (2013–2014)`,
  `AnoEstreia` = 2014) e `data/seeds/obras.csv:12` (`Ano` = 2014).
- Prova: a página oficial dc.com/characters/signal traz First Appearance BATMAN #21 (2013). Batman (vol. 2) #21
  abre o arco Zero Year e tem capa de agosto de 2013 (lançado em junho de 2013). O `March 2014` do infobox da
  Wikipédia em inglês (`data/raw/curadoria.json`, Id 11) é o erro que foi copiado.
- Impacto: fato de lore errado num seed congelado, que alimenta a Linha do Tempo e o Painel. A `IdEra` (5,
  Novos 52) não muda.
- Correção: `AnoEstreia` = 2013, `PrimeiraAparicao` = `Batman (vol. 2) #21 (ago 2013)`, `obras.csv` `Ano` = 2013.
  Atualizar a pendência no handoff do curador.

### MENORES

**M1. A data de estreia do Batman Que Ri usa o mês de venda, não o de capa.** `personagens.csv:48` traz
`(jul 2017)`, mas a capa é setembro de 2017 (DCU Guide). Os outros 49 personagens usam a data de capa. O infobox
da Wikipédia em inglês dá a data de venda (July 12, 2017). O ano está certo. Correção: `(set 2017)`.

**M2. O verificador `checar.py` aceita falsos positivos, e por isso não pegou o B1.** `etl/curadoria/checar.py:68-70`
- Ignora volume e ano: `concorda('Batman (vol. 2) #21 (2099)', "''Batman'' #21 (May 1944)")` → `True`.
- Concorda só pela série quando um dos lados não tem número:
  `concorda('Batman #999 (jan 2099)', "''Batman'' (16 July 1943)")` → `True`. O `re.split(...|\|)` da linha 81
  gera trechos sem número a partir de infobox com `{{ubl|...}}` (ex.: o do Alfred).
- O Wikidata do Gordon (`Detective Comics ()`) conta como concordância só pela série. O handoff reconhece isso
  e mantém `media`.
- Reprodução: `.venv/Scripts/python -c "from etl.curadoria.checar import concorda; print(concorda('Batman #999 (jan 2099)', \"''Batman'' (16 July 1943)\"))"`.
- Sugestão: exigir número dos dois lados, comparar volume e checar `AnoEstreia` contra o ano extraído.

**M3. O backoff do `http.py` não cobre o que o `docs/fontes.md` promete.** `etl/extract/http.py:36`
- Só `HTTPError` é repetido. `URLError`, timeout e reset de conexão derrubam a coleta na primeira falha.
- `docs/fontes.md` diz que há backoff em `ratelimited`. Só que o MediaWiki devolve `ratelimited`/`maxlag` como
  JSON de erro com HTTP 200, e esse JSON é **gravado no cache para sempre** (`http.py:42-43`). Também não é
  enviado `maxlag`.
- Efeito colateral: se a chamada devolver erro, `wikipedia.infobox` lança KeyError em `["query"]` e o cache já
  ficou envenenado.
- Pontos fortes: o cache por SHA-256 da URL está correto, a pausa de 1 s só vale para requisições reais, o
  `Retry-After` é respeitado e o User-Agent tem URL de contato (etiqueta Wikimedia ok).

**M4. A Oráculo está em TEC, mas o plano §8.1 a lista como exemplo de EST.** `personagens.csv:8`
(`IdArquetipo` = 4). A justificativa (hacker e central de informações) é defensável, mas o desvio do plano não
está documentado em nenhum handoff. Documentar a decisão ou alinhar ao plano.

**M5. Os criadores do Damian não correspondem à obra de estreia.** `personagens.csv:7` registra a estreia em
Batman: Son of the Demon (1987), de Mike W. Barr e Jerry Bingham, mas os `Criadores` são Morrison e Kubert, que
criaram o personagem nomeado em 2006. Isso está de acordo com o infobox da Wikipédia, então **não é fato errado**.
O problema é de coerência, e a pista de criador do Quiz pode confundir. Sugestão: acrescentar na `nota`.

**M6. A nota dos criadores do Alfred está incompleta.** `personagens.csv:3` diz que o infobox da Wikipédia
credita Cameron/Kane. Na verdade, o infobox credita Cameron/Kane para o **Alfred Beagle** e Finger/Robinson para
o **Alfred Pennyworth** (`curadoria.json`, Id 2), e a Wikipédia em francês credita Kane/Robinson. A marcação
como pendente está correta, mas a nota descreve a fonte de forma imprecisa.

**M7. O Exterminador (Deathstroke) não tem nenhuma afiliação.** `personagem_afiliacao.csv` não tem linha para
o Id 44, embora ele conste na lista usada como fonte da Galeria
(https://en.wikipedia.org/wiki/List_of_Batman_family_enemies) e o handoff o conte entre os vilões. Ele fica
órfão nos filtros por afiliação. Etrigan também está sem afiliação, o que é aceitável para um convidado.

**M8. Dois títulos de obra trazem a data embutida.** `obras.csv:15` (`... Rebirth, Part 1 (1999)`) e
`obras.csv:20` (`... Joker's Favor (set 1992)`) repetem a data, enquanto as outras 46 obras usam só o título e
deixam o ano na coluna `Ano`. Isso gera duplicidade nos rótulos da Timeline.

**M9. O Zsasz tem imagem-placeholder em vez de URL vazia.** `versoes.csv:38` aponta para `no-portrait.jpg` da
SuperHero API. A imagem carrega, então o fallback `onerror` (plano §3.8) nunca dispara. As outras 17 versões
sem imagem deixam o campo vazio.

## Itens conformes (sem achado)

- CLAUDE.md: nenhuma aspa dupla em valores de texto. O apóstrofo do Coringa é tipográfico (‘ ’). Os fatos sem
  fonte dupla estão marcados `baixa` ou têm `nota` de pendência.
- Os seeds de game design transcrevem §8.1, §8.2 e §8.5 sem divergência. Os gadgets batem com §8.5 e os
  bairros com §3.6.
- Afiliações plausíveis: Ra's é Líder e Talia e Shiva são Membros da Liga dos Assassinos/Sombras, com Damian
  como ex-membro. No GCPD, Gordon é Líder, Montoya e Bullock são Membros e Barbara é Aliada. A nota sobre o nome
  Liga das Sombras é adequada.
- Verifiquei no cache bruto a nota do Duas-Caras (a Wikipédia credita só o Kane): está correta.

## Itens não verificáveis nesta revisão

- DC Database (Fandom) devolveu HTTP 402 e GCD (comics.org) devolveu 403 ao WebFetch. Usei outras fontes.
- O mês de capa de 52 #7 (Batwoman): as fontes divergem entre jun e ago de 2006. O seed não fixa o mês, o que
  é aceitável.
- Os termos da IGDB continuam pendentes, como já registra `docs/fontes.md`.
- Atributos estimados de 18 versões (`confianca` baixa): são design, sem fonte verificável. Não auditei.
- O balanceamento fica para a F4d e está fora do escopo do gate F1.

## Para reaprovar

1. Corrigir o B1 em `personagens.csv:12` e `obras.csv:12`.
2. (Recomendado) M1 e M4, e a nota dos itens M5 e M6.
3. Rodar de novo `pytest` e `etl.curadoria.checar`.

---

# Ciclo 2: nova revisão após as correções (18/10/2026)

## Veredito do ciclo 2: **APROVADO**

O B1 foi corrigido e confirmado em fonte oficial. As correções de M1 a M9 conferem nos arquivos. As contagens do
handoff batem. Achei três regressões ou inconsistências, todas MENORES (N1 a N3), que não bloqueiam o gate F1;
convém resolvê-las antes da F2.

## Saída dos comandos

```
.venv/Scripts/python -m pytest -q          -> 136 passed in 0.38s
.venv/Scripts/python build/checks.py       -> APROVADO: checks.py sem erros
.venv/Scripts/python -m etl.curadoria.checar -> 25/50 estreias com 2+ fontes concordantes (exit 0; gate >= 20)
```

## Conferência das correções do ciclo 1

| Item | Verificação | Status |
|---|---|---|
| B1 | `personagens.csv:12`: `Batman (vol. 2) #21 (ago 2013)`, `AnoEstreia` 2013, `IdEra` 5, dc.com incluído em `fonte`; `obras.csv:12`: `Ano` 2013 | OK |
| M1 | `personagens.csv:48`: `(set 2017)`, com a data de venda na `nota` | OK |
| M2 | `checar.py:21-47` compara série, volume, número e ano (±1); o exemplo da revisão agora dá `False` | OK, mas ver N1 e N2 |
| M3 | `http.py:36-57`: repete em URLError, timeout e queda de conexão, e em `ratelimited`/`maxlag` com HTTP 200; JSON de erro gera exceção e não é gravado no cache (testado em `tests/etl/test_extract.py`). A ordem dos `except` está certa (HTTPError antes de URLError) | OK |
| M4 | Oráculo: `IdArquetipo` 1 (EST) em `personagens.csv` e `versoes.csv:8`; golpes 701 = 1, 2, 3 (EST) + 10 (cobertura TEC) | OK |
| M5/M6 | Notas do Damian e do Alfred agora descrevem a fonte corretamente | OK |
| M7 | `personagem_afiliacao.csv`: (44, 2, Membro) | OK, mas ver N3 |
| M8 | `obras.csv:15` e `obras.csv:20` sem data no título | OK |
| M9 | `versoes.csv:38`: `UrlImagem` vazia | OK |

Contagens do handoff: `confianca` 25/7/18 **bate**; arquétipos EST 10, FUR 9, LUT 7, TEC 6, PSI 6, MET 5, BRU 4,
MIS 3 **batem**; 25/50 **bate**. Todo `alta` agora tem 2+ concordâncias e nenhum não-alta tem 2+, o que deixa a
coerência maior que no ciclo 1. A queda de 27 para 25 vem do Terry (explicada no handoff) e do Gordon: o Wikidata
`Detective Comics ()`, que não tem número nem ano, deixou de contar, como era esperado; isso não está no handoff.
O Gordon segue `media`.

Integridade refeita por script: era × ano, obra × estreia, arquétipo da versão = do personagem, 4 golpes por
versão e raridade dos encontros. Tudo OK.

## Achados novos (MENORES)

**N1. Regressão em `trechos()`: o split em `. ` quebra volume.** `etl/curadoria/checar.py:53` (regex
`<br\s*/?>|\||;|\.\s|\(as `). A string `Batman (vol. 2) #21` vira `["''Batman'' (vol", "2) #21 (New 52)"]`. O
segundo trecho é lido como série `52`. Resultado: o Signal aparece como `Wikipédia ✖` (0 concordâncias) em
`handoffs/F1-checagem-fatos.md`, embora a edição bata com o infobox. O erro é um falso negativo, ou seja, vai para
o lado seguro, e o Signal já era `baixa`.
Reprodução: `.venv/Scripts/python -c "from etl.curadoria.checar import trechos; print(trechos(\"''Batman'' (vol. 2) #21 (New 52)\"))"`.
Sugestão: não dividir em `vol. ` (por exemplo, `(?<!vol)\.\s`).

**N2. A tolerância de ±1 ano não pegaria o próprio B1.**
`concorda('Batman (vol. 2) #21 (ago 2014)', 'Batman (vol. 2) #21 (August 2013)')` → `True`. A tolerância é
legítima, porque ano de capa e ano de venda diferem. A consequência é que o checador não detecta erro de ano em ±1:
o B1 só seria pego por revisão humana. Basta documentar essa limitação no cabeçalho do relatório gerado. Esse
cabeçalho (`checar.py:76`) ainda descreve o critério antigo: série e número, ou só série quando falta o número.

**N3. Contagens e fontes desatualizadas.**
- O handoff do curador (linha 11) ainda diz galeria de vilões (27). Com o Exterminador, a afiliação 2 tem
  **28** membros.
- `obras.csv:12` (Batman (vol. 2) #21, `Ano` 2013) tem como única `fonte` o artigo da Wikipédia em inglês, que dá
  2014. Incluir dc.com, como já foi feito em `personagens.csv:12`.

Não houve regressão no `http.py`. Com `ratelimited` na última tentativa, a função lança `RuntimeError` sem gravar
no cache. Respostas em lista (SuperHero API) e SPARQL não têm a chave `error`, então passam direto.
