# Revisão F2 — ETL (Coruja)

- **Revisor:** revisor-qa (Coruja), sem acesso ao raciocínio do autor
- **Data:** 2026-10-18
- **Entrega revisada:** `handoffs/F2-engenheiro-dados-etl.md` + `handoffs/F2-relatorio-qualidade.md`
- **Veredito:** **REPROVADO**. Há 1 achado BLOQUEANTE (B1, relações simétricas duplicadas que distorcem `Peso`
  e `dCentralidade`). Os critérios formais do gate F2 (§12) **estão cumpridos**: pytest verde, 0 órfãs e taxa
  de casamento reportada. Mesmo assim, a tabela `fRelacao`/`dCentralidade` que segue para a F3 tem um defeito
  de dados confirmado e de correção barata. Os MENORES podem entrar no mesmo ciclo, e M1 e M2 são recomendados.

## 1. Saída dos comandos (resumida)

| Comando | Resultado |
|---|---|
| `.venv/Scripts/python -m pytest -q` | `161 passed in 1.71s` |
| `.venv/Scripts/python build/checks.py` | `APROVADO: checks.py sem erros` |
| `.venv/Scripts/python -m etl.run_etl --offline` (1ª) | rc=0 · `OK: 18 tabelas em data\curated · órfãs: 0` · contagens iguais às do relatório |
| `.venv/Scripts/python -m etl.run_etl --offline` (2ª) | rc=0 · idem |
| SHA-256 de `data/curated/*` (commitado → 1ª → 2ª execução) | **idênticos nas 3 leituras**, incluindo `_qualidade.json`, porque a data `gerado_em` é a mesma no dia. Determinismo **confirmado** com o cache. |

Formato dos 18 CSVs: UTF-8 **sem BOM**, LF, nenhum campo multilinha e nenhuma aspa dupla dentro do texto.
As aspas que aparecem são só o *quoting* CSV de campos com vírgula, em 4 linhas de `dPersonagem` e 4 de `dObra`.

## 2. Gate F2 (plano §12)

| Critério | Status | Evidência |
|---|---|---|
| pytest verde | ✔ | 161 passed |
| 0 chaves órfãs | ✔ | `_qualidade.json` → 23 FKs = 0. `validar()` levanta erro se houver órfã (testado em `test_validacao_reprova_chave_orfa`) |
| Taxa de casamento reportada | ✔ (com ressalva M6) | Wikidata 50/50, SuperHero 32/50, obras P674 43/50, Comic Vine não coletado |

## 3. Achados

### BLOQUEANTE

**B1. Relações simétricas aparecem em dobro em `fRelacao` e inflam `Peso`, contagens e `dCentralidade`.**
- Onde: `etl/transform/modelo.py:141` (o `drop_duplicates` só remove a mesma direção),
  `etl/extract/wikidata.py:192-205` (P7047, P451, P26, P3373 e P1038 são simétricas no Wikidata) e
  `etl/graph/centralidade.py:173-174` (arestas paralelas somam peso).
- Fato confirmado: das 184 linhas, **69 pares** existem nas duas direções com o mesmo tipo. Exemplos:
  Batman→Coringa e Coringa→Batman (inimigo), Batman↔Mulher-Gato (romance) e Asa Noturna↔Tim Drake (família).
  Isso depende de o Wikidata ter registrado a propriedade nos dois itens, então o resultado é **inconsistente
  entre pares**. Batman–Coringa fica com peso 2 e Alfred–Coringa também; outro par inimigo registrado num só
  item fica com peso 1. Em família, P22 (filho→pai) e P40 (pai→filho) misturam as duas direções.
- Impacto:
  - O relatório diz "inimigo 77", mas são 40 pares distintos. Removendo a redundância simétrica
    (par não ordenado + tipo), sobram 115 linhas: inimigo 40, família 21, organização 19, mentor 14,
    romance 11, aliado 10.
  - A intermediação muda de forma material. Com e sem a redundância: Bane 0,038 → 0,000; Chapeleiro Louco
    0,037 → 0,000; Comissário Gordon 0,001 → 0,037; Oráculo 0,037 → 0,072; Talia 0,075 → 0,037.
    Os hubs 2–10 do relatório e da futura página "Rede" vêm desse artefato.
  - Na F3, a rede desenharia arestas duplas e medidas como "nº de inimigos" contariam alguns pares em dobro.
- Reprodução:
  ```python
  import pandas as pd
  r = pd.read_csv('data/curated/fRelacao.csv'); k = set(zip(r.IdOrigem, r.IdDestino, r.TipoRelacao))
  sum((b, a, t) in k for a, b, t in k) // 2   # -> 69
  ```
- Correção sugerida:
  - Para tipos simétricos (inimigo, romance, família, aliado de P3342), canonizar o par como
    (min, max) antes do `drop_duplicates`.
  - Manter a direção só onde ela tem sentido: mentor (mentor→aluno) e aliado via P2546 (sidekick→herói).
  - Somar peso só entre **tipos diferentes**.
  - Adicionar um teste: "nenhum par (a,b,t) e (b,a,t) para t simétrico".

### MENORES

**M1. Uma obra sem rótulo entra com o QID como título.** `dObra` IdObra 1140010782 tem `Titulo` = `Q140010782`.
- No Wikidata, o item não tem rótulo pt nem en, só a descrição "Comic book series by DC Comics" (P577 2026-06-10).
- Causa: o serviço de rótulos devolve o QID quando falta rótulo (`etl/extract/wikidata.py:183`).
- Reprodução: `grep Q140010782 data/curated/dObra.csv`.
- Correção: descartar e contar as obras cujo título casa com `^Q\d+$`, ou buscar rótulo em outra língua.

**M2. Obra fora das eras descartada em silêncio: "Detective Comics" (Q1799866, 1937).**
- `etl/transform/modelo.py:79-80` remove obras com `IdEra` nulo sem contar. A conta do relatório não fecha:
  350 − 11 − 63 = 276, mas `obras_no_modelo` = 275.
- A obra perdida é justamente a série *Detective Comics*. O Wikidata dá 1937 (início da revista) e `dEra`
  começa em 1938.
- Correção: contar e reportar a perda, ou fixar o ano mínimo na 1ª era.

**M3. Animações classificadas como Filme.**
- Casos: *Batman & Mr. Freeze: SubZero* (Q498757, 1998), *Batman: Mystery of the Batwoman* (Q810861, 2003)
  e *Dynamic Duo* (Q136555546, descrita como "upcoming American animated film").
- O P31 deles é só `film`, e `classificar_midia` (`modelo.py:34-35`) usa apenas P31 e o tipo da série.
- O defeito vem do dado do Wikidata, mas afeta a contagem por mídia. Sugestão: usar também o gênero
  (P136 = animated film / Q202866).

**M4. Ruído e ambiguidade em títulos.**
- *Harley* (Q33228872) é um curta de fã de 2016 ("short film by Fernando Huerto"), não uma obra DC.
- *Dynamic Duo* tem `Ano` 2028, no futuro. `schemas.py:44` aceita até 2100.
- *Pilot* (Q932124, episódio de *Smallville*) fica sem contexto.
- *The Batman* (Q205575) com Ano 1943 é o seriado de cinema *Batman* (1943). O rótulo pt do Wikidata é
  "The Batman", enquanto *The Batman* (2022, Q61117344) aparece como "Batman".
- Há 10 obras com o título "Batman". Na F3, segmentações por `Titulo` vão fundir obras diferentes.
- Sugestão:
  - filtrar `Ano` > ano corrente;
  - gerar um rótulo de exibição único (`Titulo (Ano, Mídia)`) ou usar *sort by* no IdObra;
  - preferir o rótulo en para obras, ou exibir os dois.

**M5. Obras perdidas pela classificação.** `ongoing series` não está em `PALAVRAS_HQ` (`modelo.py:19`).
*Grayson* (Q85764394) e `written work` (*Batman/Judge Dredd: Judgment on Gotham*) caem como fora do escopo.
Das 63 descartadas sem data, 61 são HQ (ex.: *Batman Black and White*, *World's Finest Comics*). A consulta
usa só P577|P580; P571 (inception) recuperaria parte delas. Isso está reportado, então é só sugestão.

**M6. A "taxa de casamento" de Wikidata (QID) e SuperHero API mede preenchimento do seed, não casamento.**
`run_etl.py:74-75` conta células não vazias de `WikidataQid`/`IdSuperHeroApi` curadas à mão na F1. O "100%"
é tautológico: nenhum QID é resolvido nem conferido nesta fase, e `wikidata.fatos()` existe mas não é chamado.
Sugestão: renomear para "cobertura de ID no seed" ou validar cada QID por rótulo/instância.

**M7. O dicionário de dados v0.3 está desatualizado em relação aos arquivos.**
- `contracts/data-dictionary.md` diz `dObra` 305 e `fAparicao` 681. Os arquivos e o relatório têm 319 e 690.
- O dicionário §6 diz `EhTransformacao` bool. `schemas.py:30` e o CSV usam int 0/1, o que funciona no PQ
  mas diverge do contrato.
- É contrato do modelador (Gordon), então o autor deve pedir a correção, não editar.

**M8. Comic Vine: o casamento por nome vai errar quando houver chave.** O código não roda hoje (sem chave), mas:
- `run_etl.py:65` busca por `Codinome or Nome`, e os codinomes estão em pt ("Coringa", "Arlequina", "Pinguim",
  "Charada", "Duas-Caras", "Mulher-Gato"…) ou compostos ("Nightwing (ex-Robin)", "Robin / Red Robin",
  "Batgirl / Oráculo"). Em `comicvine.py:119` a igualdade normalizada não casa com o nome em inglês da
  Comic Vine.
- Falsos positivos: o desempate por mais edições (`comicvine.py:122`) faz "Batman do Futuro" (Codinome
  "Batman") casar com o Batman de Bruce Wayne. Com Damian ("Robin"), casa o "Robin" com mais edições.
- Sugestão: buscar por um alias em inglês (nova coluna no seed ou rótulo en do Wikidata) e casar
  preferencialmente pelo nome civil.
- Com status 107 (limite), o backoff total fica em torno de 1 minuto (`http.py:67-70`), mas o limite da
  Comic Vine é por hora. O pipeline vai abortar em vez de esperar, o que é aceitável se documentado.
- Fato confirmado por leitura, **não executado** (não há chave).

**M9. Granularidade misturada em `dObra`.** Série inteira e itens individuais convivem:
*Batman: The Animated Series* com ~80 episódios, *Heart of Steel* com *Part 1/Part 2*, *Action Comics* com
*Action Comics #1*, *Batman* (HQ 1940) com *Batman #1*. Isso infla "aparições por mídia" (Animação 288).
Não é erro de ETL, mas a F3 e a página Linha do Tempo precisam saber disso. Registrar no dicionário.

### Itens conferidos sem defeito

- **Deduplicação seed × Wikidata:** as 4 unificações estão corretas. Busca *fuzzy* (ratio > 0,75, ±2 anos)
  não achou falso positivo. Os quase-duplicados restantes têm granularidade diferente (edição #1 × minissérie:
  *Batman: Sword of Azrael #1* × Q2891499; *Batman #1* × série *Batman*), então não são falso negativo
  estrito. O teste de regressão Batman (1989) × *Batman #436* existe e passa.
- **Direção mentor→aluno:** P1066 invertido e P802 mantido (`wikidata.py:201-202`) estão corretos. Por exemplo,
  `Batman→Asa Noturna` vem com Fonte P1066.
- **Centralidade, distância = 1/peso:** a escolha é adequada (padrão do networkx: relação mais forte = caminho
  mais curto). PageRank usa `peso` como força, o que é coerente. O problema está nos pesos de entrada (B1),
  não na fórmula.
- **Comic Vine e segredo:** a chave não entra no nome do cache, porque `chave_cache` = URL sem `api_key`
  (`comicvine.py:43-44`). Também não entra no conteúdo, já que a resposta não ecoa a chave. A mensagem de
  erro usa `url` sem chave (`http.py:71`), e `HTTPError.__str__` não inclui a URL. `status_code != 1` →
  erro e nunca vai para o cache. `.env` está no `.gitignore` e não existe no repositório.
- **`--offline`:** `SOMENTE_CACHE` levanta `RuntimeError` sem cache (`http.py:31-32`). As duas execuções
  offline funcionaram.
- **`IdObra`:** o máximo é 1.140.010.782, que cabe em Int64 e até em Int32 (< 2.147.483.647). O Power Query
  não quebra. A margem para Int32 acaba com QIDs acima de ~Q1,147 bi, o que é irrelevante no Int64.Type.
- **Números do handoff:** 350 obras brutas, 179 relações cruas do Wikidata (165 únicas por direção+tipo),
  63 sem data, 161 testes, 23 FKs, 7 sem obra e 3 isolados batem com os arquivos e o cache. A exceção é M7.

### Observações para a F3 e a F4 (não são defeitos da F2)

- No Power Query, declare `Encoding=65001` em `Csv.Document`, porque os CSVs não têm BOM.
- O título "The Darkness\Batman" tem barra invertida. A regra de escape do CLAUDE.md (& < > ') não cobre `\`
  em strings JS de aspas simples, então o escape no DAX/JS precisa tratar `\`.

## 4. Amostra conferida

**Obras (25 de `dObra.csv`):** `TipoMidia`/`Ano` conferidos contra o rótulo, P31 e P577 do Wikidata (API
`wbgetentities` e o cache SPARQL) e contra conhecimento editorial.

| Obra | Mídia/Ano no CSV | Conferência |
|---|---|---|
| Batman (Q116852) | Filme 1989 | ✔ |
| The Dark Knight (Q163872) | Filme 2008 | ✔ |
| Batman: Arkham City (Q288811) | Game 2011 | ✔ |
| Lego Batman: The Videogame (Q74545) | Game 2008 | ✔ |
| Batman: The Killing Joke (Q240358) | HQ 1988 | ✔ |
| Batman: The Long Halloween (Q512835) | HQ 1996 | ✔ |
| Batman: Year One (Q383811) | HQ 1987 | ✔ |
| Batman: Year One (filme) (Q129161) | Animação 2011 | ✔ |
| Batman - A Máscara do Fantasma (Q810858) | Animação 1993 | ✔ |
| Heart of Ice (Q5692305) | Animação 1992 | ✔ (episódio de BTAS) |
| Gotham (Q15726959) | Série 2014 | ✔ |
| Batman (Q1247201) | Série 1966 | ✔ |
| Joker (Q42759035) | Filme 2019 | ✔ |
| Space Jam: A New Legacy (Q56850065) | Animação 2021 | ✔ aceitável (híbrido; P31 inclui animated film) |
| Superman (Q1975401) | Animação 1941 | ✔ (curtas Fleischer) |
| Superman (Q29715) | Game 1979 | ✔ (Atari 2600) |
| Crise nas Infinitas Terras (Q522623) | HQ 1984 | ⚠ P580 1984-12-11 (data de venda); a data de capa é 1985. MIN é defensável |
| Pilot (Q932124) | Série 2001 | ✔ ano, ⚠ título (M4) |
| Batman & Mr. Freeze: SubZero (Q498757) | Filme 1998 | ✘ é animação (M3) |
| Batman: Mystery of the Batwoman (Q810861) | Filme 2003 | ✘ é animação (M3) |
| Dynamic Duo (Q136555546) | Filme 2028 | ✘ animação e ano futuro (M3/M4) |
| Harley (Q33228872) | Filme 2016 | ✘ curta de fã, fora do cânone (M4) |
| The Batman (Q205575) | Filme 1943 | ✔ ano, ⚠ título pt enganoso; é o seriado *Batman* de 1943 (M4) |
| Batman & Robin (Q810855) | Série 1949 | ⚠ é seriado de cinema ("1949 film serial"); P31 = television series no Wikidata |
| Q140010782 | HQ 2026 | ✘ sem título (M1) |

**Universo:** todas as obras não-Batman da amostra são ligadas a personagens do seed: Superman (48), Zatanna
(49, *To/From Eternia with Death*) e Mulher-Gato (Q140010782). Nenhuma está fora do universo DC, salvo o fan
film *Harley*.

**Relações (7 conferidas nos claims do Wikidata via API):**
- Asa Noturna P1066 Batman → `Batman→Asa Noturna mentor` ✔
- Damian P25 Talia → `Damian→Talia família` ✔
- Barbara Gordon P22 James Gordon → `Oráculo→Gordon família` ✔
- Arlequina P451 Coringa e Hera → romance ✔
- Superman P3342 Batman → aliado ✔
- Lady Shiva P802 Cassandra, Tim e Jason → mentor ✔
- Tim Drake P1066 Batman e Lady Shiva → mentor ✔

## 5. O que não foi possível verificar

- Execução **online** (sem `--offline`) e a Comic Vine com chave real, porque não há chave. M8 vem só de leitura.
- O CI em Python 3.12: o venv local é 3.14, então não verifiquei se os floats de `dCentralidade` saem
  idênticos entre versões.
- A carga real no Power Query/Power BI (isso fica para a F3).
- A precisão de todos os 319 anos e mídias: só a amostra acima foi conferida.

---

# Ciclo 2 — revisão das correções (2026-10-18)

- **Veredito do ciclo 2:** **APROVADO**.
  - B1 está corrigido e protegido por schema e por testes.
  - M1–M9 foram tratados ou têm justificativa aceitável.
  - O gate F2 continua cumprido.
  - Os achados novos (N1–N5) são todos MENORES e podem seguir como pendências da F3/F4.
- **Ponto do ciclo 1 sobre `\` no escape do CLAUDE.md:** aceito como pendência da F4a, conforme decisão
  do orquestrador.

## 1. Saída dos comandos

| Comando | Resultado |
|---|---|
| `.venv/Scripts/python -m pytest -q` | `173 passed in 4.04s` |
| `.venv/Scripts/python build/checks.py` | `APROVADO: checks.py sem erros` |
| `-m etl.run_etl --offline` (1ª e 2ª) | rc=0 nas duas · `OK: 18 tabelas · órfãs: 0` · dObra 319, fAparicao 689, fRelacao 115 |
| SHA-256 de `data/curated/*` + `handoffs/F2-relatorio-qualidade.md` (entregue → 1ª → 2ª) | **idênticos nas 3 leituras**: determinístico e igual ao que foi entregue |

## 2. Conferência das correções

| Item | Status | Evidência |
|---|---|---|
| B1 simétricas | ✔ | Ver o detalhamento logo abaixo da tabela. |
| M1 título = QID | ✔ | 0 títulos `^Q\d+$`. `obras_sem_rotulo` = 4 (`modelo.py:93`) |
| M2 obra antes da 1ª era | ✔ | Contada (`obras_antes_da_1a_era` = 1). A cadeia fecha: 350 − 10 − 4 − 59 − 1 − 1 = 275 (teste `test_contagens_do_relatorio_fecham`). 275 + 48 − 4 = 319 ✔ |
| M3 animação | ✔ parcial (aceito) | Usa gênero P136 (`modelo.py:34-38`). SubZero e Mystery of the Batwoman seguem como Filme porque o Wikidata não tem P31 nem gênero de animação para elas: limitação da fonte, documentada |
| M4 títulos | ✔ parcial | Ver o detalhamento logo abaixo da tabela. |
| M5 | ✔ | *Grayson* (Q85764394) e *World's Finest Comics* (Q178477) agora entram. Sem data caiu de 63 para 59 (P571 adicionado) |
| M6 | ✔ parcial | Rótulos "QID/id preenchido no seed" estão corretos. Ver N2 |
| M7 dicionário | ✔ | `data-dictionary.md` v0.3 bate com os arquivos (319/689/115, `EhTransformacao` int, `Granularidade`, nota de encoding e de forma canônica) |
| M8 Comic Vine | ✔ parcial | Busca por nome civil e depois por nome em inglês (`WikipediaTitulo` sem parênteses). Casamento só exato, e o código 107 falha sem retry (`http.py:64-65`). Ver N1 |
| M9 granularidade | ✔ parcial | Coluna `dObra.Granularidade` criada: Obra 172, Série 61, Episódio 86. Ver N3 |
| Relatório F2 | ✔ | Contagens, descartes, cobertura, granularidade e hubs batem com `_qualidade.json` e com os CSVs |

**Detalhamento de B1:**
- Não há nenhum par espelhado (a,b,t)/(b,a,t) em `fRelacao`.
- Todas as linhas com `IdOrigem > IdDestino` são `mentor` (4) ou `organização` (1).
- A contagem por tipo bate com o que eu calculei de forma independente no ciclo 1: inimigo 40, família 21,
  organização 19, mentor 14, romance 11, aliado 10.
- O schema reprova par simétrico não canônico (`schemas.py:56-57`), e há teste de regressão para isso.
- `dCentralidade` bate com o meu recálculo do ciclo 1: Batman 0,839286; Asa Noturna 0,075680; Oráculo 0,072279;
  Gordon 0,037415; Talia 0,037415.

**Detalhamento de M4:**
- Títulos agora vêm em inglês primeiro: Q205575 = "Batman" (1943) e Q61117344 = "The Batman" (2022).
- O episódio aparece com a série: "Smallville — Pilot".
- Obras futuras são descartadas e contadas (*Dynamic Duo* saiu; máximo agora é 2025).
- *Harley* (curta de fã) foi mantido por decisão do autor; aceito, com o filtro ficando para a F4.
- Nove obras continuam com título idêntico "Batman", o que é esperado. A F3 deve exibir `Titulo` com o ano
  ou ordenar por `IdObra`.

**Regressões procuradas:**
- `relacoes()`: a forma canônica é aplicada só aos tipos de `SIMETRICAS`. Mentor mantém a direção (Batman→Asa
  Noturna, Ra's→Damian) e organização mantém Líder→membro. O `drop_duplicates` vem depois da canonização.
  Sem regressão.
- `obras_wikidata()`: os descartes são sequenciais e por obra. Uma obra só cai numa etapa se nenhuma das suas
  linhas passar.
  - O título de episódio só ganha prefixo quando a série não está contida no título. Os 86 episódios têm " — ".
  - A obra-seed 19 continua unificada com Q6269708 (agora pelo título completo).
  - Sem duplicata nova seed × Wikidata.
- `comicvine.buscar()`: ver N1.

## 3. Achados novos (ciclo 2), todos MENORES

**N1. Comic Vine: o falso positivo do Batman do Futuro provavelmente continua (suspeita, não executado).**
- Contexto: `etl/extract/comicvine.py:44-60`. Para o personagem 14, `civil` = "Terry McGinnis" e `nome_en` =
  "Batman" (de "Batman (Terry McGinnis)").
- Na Comic Vine, o personagem se chama "Terry McGinnis" (página 4005-40501) e o nome real provavelmente é
  "Terrence McGinnis".
- O que acontece no código:
  1. Na 1ª consulta ("Terry McGinnis"), o critério `real_name` falha ("terrence…" ≠ "terry…").
  2. O critério `name` compara com `nome_en` = "batman", não com o nome civil, e também falha.
  3. Na 2ª consulta ("Batman"), o critério `name` casa com o Batman de Bruce Wayne.
- É exatamente o caso que a docstring diz evitar. O caminho é o mesmo sempre que `real_name` diverge do civil
  do seed: o mesmo `nome_en` genérico "Batman" pode ser escolhido.
- Correção:
  - no critério `name`, aceitar também o nome civil;
  - recusar `nome_en` que seja codinome de outro personagem do seed;
  - adicionar teste unitário com `get_json` simulado (hoje `buscar()` não tem teste).
- Classificado como suspeita: não há chave nem resposta real da API para confirmar.

**N2. A cobertura "Wikidata — personagens com relações 47/50" inclui arestas do seed.**
- Em `run_etl.py` (bloco "relações e centralidade"), `com_rel` usa todas as linhas de `fRelacao`, inclusive
  `organização`, que vem do seed.
- Lucius Fox (15) só tem a aresta `organização` Batman→Lucius, então a cobertura real do Wikidata é 46/50.
- Reprodução: filtrar `Fonte.str.startswith('Wikidata')` → 46 personagens.
- Correção: filtrar por `Fonte` ou renomear a linha do relatório.

**N3. `Granularidade` inconsistente em HQ e em séries de curtas.** `granularidade()` (`modelo.py:44-51`) olha
só se o texto do P31 contém "series"/"episode". Resultados:
- *Action Comics* (Q343615, P31 magazine/comics anthology) fica como **Obra**, enquanto *Batman* (HQ 1940) e
  *World's Finest Comics* ficam como **Série**.
- Minisséries ("limited series") viram **Série**: *The Long Halloween*, *The Dark Knight Returns*, *Crisis on
  Infinite Earths*. Já *Batman: Year One* e *Batman R.I.P.* ficam como **Obra**.
- *Superman* (1941, "animated short film series") fica como **Obra** por causa da exceção "film series".
- *Red Hood and the Outlaws* (série mensal) fica como **Obra**.
- Impacto: o filtro por granularidade, que o próprio dicionário recomenda, não separa bem HQ.
- Sugestão: tratar "magazine", "anthology" e "ongoing" como Série, e "limited series" como Obra (história
  fechada). Ou documentar a regra no dicionário.

**N4. `aliado` canonizado perde a direção de P2546 ("sidekick of").**
- Exemplo: a linha `1 → 3 aliado, Fonte "Wikidata P2546"` se lê como "Batman é sidekick de Asa Noturna".
- Tratar aliado como simétrico é uma decisão de modelagem aceitável, mas a coluna `Fonte` fica enganosa.
- Sugestão: mapear P2546 como `mentor`/assimétrico, ou anotar no dicionário que `Fonte` não indica a direção
  em tipos simétricos.

**N5. A saída depende do ano do relógio.**
- `ano_maximo=date.today().year` (`run_etl.py:80`) muda o resultado de `--offline` sobre o mesmo cache quando
  o ano vira. Exemplo: *Dynamic Duo* (2028) volta a entrar em 2028.
- O determinismo foi verificado no mesmo dia. Aceitável, mas vale documentar ou fixar o corte por parâmetro.

## 4. O que não foi possível verificar (ciclo 2)

- A execução **online** que regenerou o cache de obras. Conferi só o resultado via `--offline` e os arquivos
  entregues.
- A Comic Vine com chave real (N1 é análise de código mais a página pública da Comic Vine).
- O determinismo entre o Python 3.12 do CI e o 3.14 local, e a carga no Power Query.
