# 🦇 GOTHAM DATABASE — Batcomputador em Power BI

> Plano de projeto detalhado para construir uma aplicação **visual e técnica** sobre o universo do Batman (quadrinhos, games, séries, filmes e animações) **inteiramente dentro do Power BI**, usando medidas DAX que geram HTML/CSS/SVG/JavaScript, no estilo da *Pokédex em Power BI* de Kelven Cardoso — e desenvolvida por um **time de agentes de IA especializados** (Claude Code + subagentes) para maximizar a qualidade da entrega.

---

## Sumário

1. [Visão do produto](#1-visão-do-produto)
2. [O que aprender com a referência (Pokédex)](#2-o-que-aprender-com-a-referência-pokédex)
3. [Páginas e funcionalidades](#3-páginas-e-funcionalidades)
4. [Fontes de dados](#4-fontes-de-dados)
5. [Arquitetura técnica](#5-arquitetura-técnica)
6. [Modelo semântico (star schema)](#6-modelo-semântico-star-schema)
7. [Padrões DAX → HTML/SVG/JS](#7-padrões-dax--htmlsvgjs)
8. [Game design: Arena, arquétipos e fórmulas](#8-game-design-arena-arquétipos-e-fórmulas)
9. [Identidade visual "Gotham Noir"](#9-identidade-visual-gotham-noir)
10. [Estrutura do repositório](#10-estrutura-do-repositório)
11. [Time multiagente](#11-time-multiagente)
12. [Fluxo de trabalho, fases e quality gates](#12-fluxo-de-trabalho-fases-e-quality-gates)
13. [Definições dos agentes (`.claude/agents/`)](#13-definições-dos-agentes-claudeagents)
14. [Testes e qualidade](#14-testes-e-qualidade)
15. [Riscos e mitigação](#15-riscos-e-mitigação)
16. [Roadmap sugerido](#16-roadmap-sugerido)
17. [Prompt de kickoff](#17-prompt-de-kickoff)
18. [Aspectos legais e créditos](#18-aspectos-legais-e-créditos)

---

## 1. Visão do produto

**Nome de trabalho:** *Gotham Database* (alternativas: *Batcomputador BI*, *Arquivo Arkham*).

**Pitch:** um relatório Power BI que parece um Batcomputador. Você escolhe qualquer personagem do universo do Batman e vê sua ficha completa, versões em cada mídia, rede de relações, linha do tempo, além de jogar uma arena de confrontos, um quiz com o Bat-sinal e um minijogo de patrulha por Gotham — tudo renderizado por medidas DAX.

**Objetivos:**

| Objetivo | Como medir |
|---|---|
| Visual de impacto (portfólio) | Cada página com pelo menos 1 elemento animado e tema dinâmico por personagem |
| Profundidade técnica | Modelo em estrela documentado, PBIP/TMDL no Git, testes automatizados, ETL reprodutível |
| Dados reais e analisáveis | Página analítica com KPIs de verdade (aparições por era, mídia, crescimento) |
| Performance | Troca de personagem < 1,5 s; páginas JS carregam < 3 s |
| Qualidade via multiagentes | Todo artefato passa por revisão de um agente independente antes do merge |

**Fora de escopo (v1):** login, escrita de dados pelo usuário, imagens hospedadas pelo projeto (só referências por URL das fontes).

---

## 2. O que aprender com a referência (Pokédex)

Pontos-chave da arquitetura do projeto de referência que devem ser replicados:

| Técnica da Pokédex | Como aplicar no Gotham Database |
|---|---|
| Uma consulta GraphQL traz quase tudo; consultas M derivam o resto | ETL em Python consolida várias APIs num **cache estático versionado**; Power Query só lê e deriva |
| Visual **HTML Content** renderiza o texto de uma medida | Toda ficha, radar, grafo e jogo é uma medida |
| Duas medidas por painel: **HTML** e **CSS** separadas | Mesmo padrão + medida única de **design tokens** por facção |
| **Tabelas desconectadas** (Modo, EvoSel, FormaSel) + `COALESCE` de seleção | `Modo`, `VersaoSel`, `RelacaoSel`, `MidiaSel` + `[Id Selecionado]` com prioridade |
| Medida `[JS Dados]` serializa o modelo em objeto JS | `[JS Gotham]` serializa personagens, golpes, arquétipos, relações |
| **Sem aspas duplas** no JS (quebram a string DAX) | Script de build bloqueia o arquivo se encontrar `"` |
| **Estado na `window`** (visual pode redesenhar a qualquer momento) | `window.GOTHAM_STATE` guarda batalha, quiz e patrulha |
| **PBIP** (TMDL + PBIR) + scripts Python que gravam modelo e páginas | Igual, + CI que roda lint, testes Node e Best Practice Analyzer |
| Lógica da Arena testada em Node fora do Power BI | Motor de batalha e balanceamento testados com Vitest |

### 2.1 Detalhes de UX observados no relatório publicado

Esses detalhes aparecem quando se navega pelo relatório publicado, mas não estão descritos no post. São eles que dão a sensação de "app de verdade":

| Onde | Detalhe observado | Versão Gotham |
|---|---|---|
| Todas as páginas | Barra de navegação **dentro do HTML**, sempre no mesmo lugar, com a página ativa destacada; título e subtítulo da página no canto direito | Barra "Batcomputador" fixa no topo com ícone por página e a ativa em amarelo Bat-sinal |
| Pokédex | Contador "N encontrados" que reage aos filtros + dois filtros (geração e tipo) + botão de **favoritos** (estrela) | "N arquivos encontrados" + filtros Era e Afiliação + ⭐ favoritos guardados na `window` |
| Pokédex | Lista em **grade de cards com imagem**, não lista de texto | Grade de cards com retrato e faixa colorida da facção |
| Ficha | Número grande translúcido atrás do nome (#001) e **chips de contexto** (região/geração, estágio, raridade, shiny) | Número do arquivo (#BAT-001) e chips: Era, Mídia de estreia, Nível de ameaça, Versão |
| Ficha | Atributos em **radar + barras + total** no mesmo card | Radar + barras + "Índice de Ameaça" total |
| Ficha | Três mini-cards de números (altura, peso, total base) | Altura, peso, nº de aparições |
| Ficha | Fraquezas e resistências **agrupadas com contagem** ("Fraco contra 4") e chip com multiplicador | "Vulnerável a 3 / Resiste a 2" com chips ×2, ×½ |
| Ficha | Selo **"EVOLUIR ›"** sobre o próximo estágio e instrução curta no cabeçalho do card | Selo "VERSÃO ›" sobre a próxima encarnação na linha de versões |
| Ficha | Partículas flutuando no fundo conforme o tipo | Partículas por facção (§9.2) |
| Arena | Toggle **1×1 / Time de 3**; grade de seleção com busca, filtro por geração e **ícones de tipo** clicáveis | Toggle 1×1 / Equipe de 3; filtros por Era e por **ícone de arquétipo** |
| Arena | Slots vazios "+ Escolher" e botão **Sortear time** para cada lado | Igual, com "Sortear equipe" |
| Arena | Barra de **previsão** com % e frase ("Seu time é favorito") antes da luta | Barra "Probabilidade de vitória (Batcomputador)" |
| Batalha | **Fundo dividido** nas cores dos dois lutadores; HUD com nível e HP numérico | Fundo dividido nas cores das facções, com chuva atravessando |
| Batalha | Botões de golpe mostram **efetividade antes de escolher** ("super efetivo ×2"), poder e precisão | Golpes com selo de matchup e categoria (Físico/Tático) |
| Batalha | Painel lateral com atributos e **time clicável para troca**, cada um com barra de HP | Igual |
| Batalha | Painel **Registro** (log) + botões Automático, **Simular ×1000** e Sair | Log no estilo terminal do Batcomputador |
| Tipos | Abas **Roda / Matriz / Ranking**; toggle Ataque/Defesa; legenda de cores das setas | Abas Roda / Matriz / Ranking de arquétipos |
| Tipos | Card de confronto (A × B = ×2) + barras de dano recebido por tipo + grade "Pokémon com essa defesa" com "+36" | Calculadora Arquétipo × Arquétipo + "Personagens com esse arquétipo" |
| Quiz | Tela inicial com fundo em raios e título estilizado + botão Começar | Bat-sinal girando nas nuvens + "COMEÇAR INVESTIGAÇÃO" |
| Quiz | Placar com pontos, sequência, recorde, acertos, precisão; "Últimas respostas"; "Zerar placar" | Igual |
| Safari | Mapa com construção funcional (Centro Pokémon reabastece a mochila), lago, mato alto | Batcaverna/delegacia reabastece gadgets; telhados e becos escondem encontros |
| Safari | Controles por **setas/WASD e D-pad na tela**; filtro de região; contadores vistos/capturas/encontros/fugas; "Sua caixa" | Igual, com "Arquivo de capturados" e destino Arkham/Blackgate |

---

## 3. Páginas e funcionalidades

### 3.1 🖥️ Batcomputador (ficha do personagem) — *equivalente à Pokédex*

Layout em 3 colunas:

- **Esquerda:** lista/segmentação de personagens com busca, filtro por *alinhamento* (Herói, Vilão, Anti-herói, Neutro), *afiliação* (Bat-família, Galeria de Vilões, Corte das Corujas, Liga das Sombras, GCPD, Liga da Justiça) e *era de estreia*.
- **Centro:** ficha principal
  - Nome, codinome, identidade civil, imagem, primeira aparição (revista, ano, criadores).
  - **Radar SVG** de 6 atributos: Inteligência, Força, Velocidade, Durabilidade, Poder, Combate.
  - **Fundo animado por facção** (ver §9): chuva para o padrão de Gotham, gás verde para Coringa/Espantalho, gelo para Sr. Frio, folhas para Hera Venenosa, pontos de interrogação para Charada, moeda girando para Duas-Caras, penas para Corte das Corujas, fogo para Vagalume.
- **Direita:** arquétipo de combate, vantagens/desvantagens (multiplicadores, como fraquezas de tipo), aliados e inimigos principais, contadores de aparições por mídia.

**Modos (tabela desconectada `Modo`):**

| Modo | O que muda |
|---|---|
| 🦇 **Arquivo** (padrão) | Ficha estilo Batcomputador, fonte monoespaçada, scanline |
| 🏥 **Arkham** | Para vilões: prontuário de paciente do Asilo Arkham (diagnóstico ficcional, nível de periculosidade, cela, tentativas de fuga) |
| 🎭 **Versões** | Encarnações do personagem por mídia (ex.: Batman de *BTAS*, *Arkham*, Nolan, Reeves, *Absolute*), clicáveis — equivalente às "formas" da Pokédex; atributos e visual mudam junto |
| 📚 **Capas** | Galeria de capas/aparições marcantes (Comic Vine) com prévia ampliada — equivalente ao modo Cartas |

**Versões clicáveis** recalculam atributos, arquétipo e tema (ex.: *Batman — Hellbat*, *Bane — com Veneno*, *Batman Que Ri*), como a Mega Evolução na referência.

### 3.2 🕸️ Rede de Relações

- Grafo **force-directed** em canvas/SVG (JS puro, sem bibliotecas externas ou com D3 embutido se o visual permitir).
- Arestas tipadas e coloridas: aliado, inimigo, mentor/pupilo, família, romance, rival, organização.
- Clique em um nó recentraliza o grafo; slider de "graus de separação" (1–3).
- Painel lateral: **centralidade** (grau, intermediação) calculada no ETL — mostra quem é o "hub" do universo.
- Equivalente à roda de tipos: aqui é a **roda de arquétipos** com setas animadas de vantagem.

### 3.3 🕰️ Linha do Tempo Multimídia (1939 → hoje)

- Eixo horizontal com eras: Ouro, Prata, Bronze, Moderna, *Novos 52*, *Renascimento*, *Infinite Frontier*, *Dawn of DC / Absolute*.
- Faixas paralelas por mídia: Quadrinhos · Séries live-action · Animações · Filmes · Games.
- Marcos clicáveis (*O Cavaleiro das Trevas*, *A Piada Mortal*, *BTAS*, *Arkham Asylum*, *The Batman*…) com card expandido.
- Filtro pelo personagem selecionado: "quando esse personagem apareceu em cada mídia".

### 3.4 ⚔️ Arena de Gotham — *equivalente à Arena*

- Confrontos **1x1** ou **equipes de 3** com troca de personagem.
- Fórmula de dano baseada em atributos + **matriz de arquétipos** (§8).
- **IA oponente** escolhe o melhor golpe e troca quando o confronto é desfavorável.
- **Transformações** (equivalente à Mega/Gigantamax): Armadura Hellbat, Veneno do Bane, Toxina do Medo, Lázaro (Ra's al Ghul).
- Barra de **previsão de vitória**, modo automático e **simulação Monte Carlo de 1.000 lutas**.
- Introdução "VS" animada com splash do Bat-sinal.

### 3.5 🔦 Quiz "Quem está no Bat-sinal?"

- Silhueta do personagem projetada no Bat-sinal sobre nuvens (`filter: brightness(0)` + máscara).
- 4 opções ou digitação livre, cronômetro, dicas progressivas (era → afiliação → criador), sequência e recorde (estado na `window`).
- Filtros por era, mídia e dificuldade.

### 3.6 🌃 Patrulha em Gotham — *equivalente ao Safari*

- Minijogo em **pixel art desenhado em canvas** (nenhuma imagem de cenário).
- O jogador (silhueta genérica de vigilante) anda pelos bairros: *The Narrows*, *Beco do Crime*, *Diamond District*, *Ilha Arkham*, *Ace Chemicals*, *Porto de Gotham*.
- Cada bairro tem uma **tabela de encontros** com raridade (comum → lendário; "versões raras" equivalem ao shiny).
- Captura com gadgets: Batarangue, Bola-Gel, Gancho, Granada de Fumaça; chance de captura por fórmula (§8.5). Capturados vão para Arkham ou Blackgate.

### 3.7 📊 Painel do Comissário (página analítica "de verdade")

Página que prova competência de BI com visuais nativos + HTML:

- KPIs: personagens catalogados, obras, aparições, % vilões, era mais produtiva.
- Aparições por década e por mídia (linha empilhada), top 15 vilões mais recorrentes, crescimento de games/séries a partir dos anos 2000.
- Mapa de calor **Personagem × Mídia**; curva de Pareto (poucos personagens concentram a maioria das aparições?).
- Métricas de rede: personagens mais centrais.

### 3.8 🧩 Ideias além da referência (diferenciais)

Funcionalidades que a Pokédex não tem e que tornam o projeto mais técnico e mais "Batman":

| Ideia | O que é | Por que vale a pena |
|---|---|---|
| **🔍 Caso do Dia (página Detetive)** | Um crime ficcional com pistas reveladas aos poucos (arquétipo, modus operandi, bairro, era). O jogador deduz o culpado filtrando suspeitos numa grade que vai se apagando | É o lado "detetive" do Batman, que nenhuma Pokédex tem; a filtragem de suspeitos é lógica de conjunto feita em JS sobre os dados do modelo |
| **📈 Meta da Arena (BI sobre o próprio jogo)** | O ETL roda uma simulação Monte Carlo (ex.: 200 lutas por par) em Node/Python e grava `fSimulacao`. Uma página analisa: taxa de vitória por personagem e arquétipo, matchups mais desequilibrados, personagens "quebrados" | Transforma o jogo em dados analisáveis com DAX nativo; é o melhor argumento de portfólio: modelagem, simulação e análise |
| **⚖️ Comparador lado a lado** | Duas fichas espelhadas com radares sobrepostos e diferença por atributo | Uso de duas tabelas desconectadas de seleção ao mesmo tempo |
| **🧠 Draft com orçamento** | Montar equipe de 3 com limite de "Índice de Ameaça" total (como teto salarial) | Força escolhas e mostra a previsão recalculando em tempo real |
| **🟢 Easter eggs do Charada** | `?` verdes escondidos nas páginas; achar todos libera um tema visual extra | Engajamento; estado guardado na `window` |
| **🎚️ Tooltips HTML nativas** | Páginas de tooltip do Power BI com mini-ficha HTML ao passar o mouse nos visuais do Painel do Comissário | Mostra integração entre visuais nativos e HTML |
| **📱 Layout mobile** | Layout de telefone do Power BI só para Batcomputador e Quiz | Relatório publicado é muito aberto pelo celular |
| **🌐 Fallback de imagem** | Silhueta genérica em CSS quando a URL externa falha (`onerror`) | Imagens hotlinkadas quebram com o tempo |

---

## 4. Fontes de dados

> ⚠️ O agente de curadoria deve **verificar endpoints, limites e termos de uso de cada fonte na Fase 1** antes de qualquer ETL.

| Fonte | O que fornece | Acesso | Observações |
|---|---|---|---|
| **SuperHero API (akabab, GitHub)** | Powerstats (6 atributos), biografia, aparência, conexões, imagens | JSON estático via jsDelivr/GitHub Pages, sem chave | Base dos atributos; filtrar `publisher = DC Comics` e conexões com Batman |
| **Comic Vine API** | Personagens, primeira aparição, contagem de edições, equipes, aliados/inimigos, capas | Chave gratuita, limite por recurso/hora, User-Agent obrigatório | Fonte principal de quadrinhos e relações; uso não comercial |
| **Wikidata (SPARQL)** | Criadores, obras em que aparece, datas, IDs cruzados | Público, CC0 | Ótimo para cruzar IDs e validar fatos |
| **TMDB API** | Filmes, séries, animações, ano, elenco, pôsteres | Chave gratuita, exige atribuição | Faixas de cinema/TV |
| **IGDB API** | Games (série Arkham, Telltale, *Gotham Knights*, LEGO…) | OAuth via Twitch | Faixa de games |
| **DC Database (Fandom, MediaWiki API)** | Complemento de versões/encarnações | CC BY-SA | Usar com atribuição, só para dados faltantes |
| **Seeds curados (CSV no repo)** | Arquétipos, golpes, transformações, bairros, tabela de encontros, matriz de vantagens | Manual (agente de curadoria + revisão) | Tudo que é *game design* fica aqui, com campo `fonte`/`justificativa` |

**Decisão de arquitetura:** APIs com chave e limite de taxa **não** são chamadas pelo Power Query. Um ETL em Python coleta, normaliza e grava **arquivos Parquet/CSV versionados** em `data/curated/`. O Power Query lê esses arquivos (local ou via URL raw do GitHub, para permitir atualização no serviço). Isso deixa o refresh rápido, determinístico e sem expor chaves.

---

## 5. Arquitetura técnica

```
┌──────────────────────────┐    ┌────────────────────────┐    ┌──────────────────────────┐
│  FONTES                  │    │  ETL (Python)          │    │  POWER BI (PBIP)         │
│  SuperHero API ─┐        │    │  extract/  (cache raw) │    │  Power Query (M)         │
│  Comic Vine ────┤        │───▶│  transform/ (pandas)   │───▶│   └ deriva tabelas       │
│  Wikidata ──────┤        │    │  quality/  (pandera)   │    │  Modelo TMDL (estrela)   │
│  TMDB / IGDB ───┤        │    │  graph/ (networkx)     │    │  Medidas DAX             │
│  Seeds CSV ─────┘        │    │  → data/curated/*.parq │    │   ├ HTML + CSS + SVG     │
└──────────────────────────┘    └────────────────────────┘    │   └ JS Gotham (JSON+app) │
                                                              │  Visual HTML Content     │
┌──────────────────────────┐    ┌────────────────────────┐    │  Relatório PBIR          │
│  src/js  (apps)          │───▶│  build/ (Python)       │───▶│                          │
│  src/css (tokens)        │    │  embute JS/CSS/DAX     │    └──────────────────────────┘
│  src/dax (medidas)       │    │  valida aspas/tamanho  │
└──────────────────────────┘    └────────────────────────┘
          ▲                                ▲
          └──── tests/ (Vitest, pytest, BPA) ─ CI GitHub Actions
```

**Stack:**

- **Power BI Desktop** com projeto em **PBIP** (modelo **TMDL**, relatório **PBIR**).
- **Visual HTML Content** (validar na Fase 0 qual versão executa JavaScript e quais limites de tamanho existem).
- **Python 3.12**: `httpx`, `pandas`/`polars`, `pyarrow`, `pandera` (validação), `networkx` (centralidade), `python-dotenv` (chaves).
- **Node 20 + Vitest** para testar a lógica JS (Arena, captura, quiz) fora do Power BI; **esbuild** opcional para minificar.
- **Tabular Editor 2 CLI** com Best Practice Analyzer; **DAX Studio** para performance.
- **GitHub Actions** para CI.

---

## 6. Modelo semântico (star schema)

### 6.1 Tabelas

| Tabela | Tipo | Grão | Colunas principais |
|---|---|---|---|
| `dPersonagem` | Dimensão | 1 linha por personagem | `IdPersonagem`, `Nome`, `Codinome`, `IdentidadeCivil`, `Alinhamento`, `IdArquetipo`, `PrimeiraAparicao`, `AnoEstreia`, `IdEra`, `Criadores`, `UrlImagem`, `Faccao` (tema visual) |
| `dVersao` | Dimensão | 1 linha por encarnação | `IdVersao`, `IdPersonagem`, `NomeVersao`, `IdMidia`, `Int`, `For`, `Vel`, `Dur`, `Pod`, `Com`, `IdArquetipo`, `EhTransformacao`, `Raridade`, `UrlImagem` |
| `dObra` | Dimensão | 1 linha por obra | `IdObra`, `Titulo`, `TipoMidia` (HQ/Série/Animação/Filme/Game), `Ano`, `IdEra`, `Plataforma`, `UrlCapa` |
| `dEra` | Dimensão | 1 linha por era | `IdEra`, `Nome`, `AnoInicio`, `AnoFim`, `Ordem` |
| `dAfiliacao` | Dimensão | 1 linha por grupo | `IdAfiliacao`, `Nome`, `Tipo` |
| `bPersonagemAfiliacao` | Ponte | personagem × grupo | `IdPersonagem`, `IdAfiliacao`, `Papel` |
| `fAparicao` | Fato | personagem × obra | `IdPersonagem`, `IdObra`, `IdVersao`, `EhEstreia`, `Relevancia` |
| `fRelacao` | Fato | par direcionado | `IdOrigem`, `IdDestino`, `TipoRelacao`, `Peso` |
| `dArquetipo` | Dimensão | 8 linhas | `IdArquetipo`, `Nome`, `Sigla`, `Cor`, `Icone` |
| `fMatchup` | Fato | arquétipo × arquétipo | `IdAtaque`, `IdDefesa`, `Multiplicador` |
| `dGolpe` | Dimensão | 1 linha por golpe/gadget | `IdGolpe`, `Nome`, `IdArquetipo`, `Categoria` (Físico/Tático), `Poder`, `Precisao`, `Efeito` |
| `bVersaoGolpe` | Ponte | versão × golpe | `IdVersao`, `IdGolpe` |
| `dBairro` / `fEncontro` | Dim/Fato | bairro × personagem | `IdBairro`, `IdPersonagem`, `Peso`, `Raridade` |
| `dCentralidade` | Dimensão | 1 por personagem | `Grau`, `Intermediacao`, `PageRank` (calculados no ETL) |
| `dStat` | Auxiliar | 6 linhas | `Ordem`, `Codigo`, `Rotulo` (para o radar) |
| `fSimulacao` | Fato | versão × versão | `IdVersaoA`, `IdVersaoB`, `Lutas`, `VitoriasA`, `TurnosMedios`, `DanoMedioA` (gerado pelo ETL a partir do motor da Arena) |
| `dCaso` / `bCasoPista` | Dim/Ponte | 1 por caso / caso × pista | `IdCaso`, `IdCulpado`, `Dificuldade`; `Ordem`, `TipoPista`, `Valor` (Caso do Dia) |

**Tabelas desconectadas (seleção sem filtrar a página):** `Modo`, `VersaoSel`, `RelacaoSel`, `ObraSel`, `TemaSel`.

### 6.2 Regras de modelagem

- Relações **1:N unidirecionais** das dimensões para os fatos; a ponte de afiliações usa filtro bidirecional **somente** se medido e justificado.
- Chaves inteiras; texto só em dimensões.
- Tabela `dEra` relacionada por `IdEra` (não por intervalo de datas no DAX).
- Tudo que é "texto longo" (bio) fica fora do modelo ou truncado no ETL para reduzir tamanho.
- Pastas de exibição nas medidas: `00 Seleção`, `10 Ficha HTML`, `20 CSS`, `30 SVG`, `40 JS`, `50 Analítico`.

---

## 7. Padrões DAX → HTML/SVG/JS

> **Nota de implementação (F4, 19/10/2026):** a seleção, a ficha e o radar foram implementados em JavaScript sobre
> a medida `[JS Gotham]` (como na Pokédex de referência), não com as medidas DAX de seleção abaixo. A troca de
> personagem é client-side e instantânea; o gate F4a passa a medir o 1º render da medida. Ver `contracts/measure-catalog.md`.

### 7.1 Medida de seleção com prioridade

```dax
Id Selecionado =
VAR _versao = [Id Versao Clicada]      -- clique no carrossel de versões
VAR _rel    = [Id Relacao Clicada]     -- clique em nó do grafo
VAR _lista  = SELECTEDVALUE ( dPersonagem[IdPersonagem] )
VAR _dono   = LOOKUPVALUE ( dVersao[IdPersonagem], dVersao[IdVersao], _versao )
RETURN
    -- clique em versão só vale se for do personagem da lista (descarta cliques antigos)
    IF ( NOT ISBLANK ( _versao ) && _dono = _lista, _versao,
         COALESCE ( _rel, [Id Versao Padrao] ) )
```

### 7.2 Radar SVG dos atributos

```dax
SVG Radar =
VAR _n = 6
VAR _r = 80
VAR _pontos =
    CONCATENATEX (
        dStat,
        VAR _ang = 2 * PI () * ( dStat[Ordem] - 1 ) / _n - PI () / 2
        VAR _v   = [Valor Stat] / 100 * _r
        RETURN
            FORMAT ( 100 + _v * COS ( _ang ), "0.0", "en-US" ) & ","
                & FORMAT ( 100 + _v * SIN ( _ang ), "0.0", "en-US" ),
        " ", dStat[Ordem], ASC
    )
RETURN
    "<svg viewBox='0 0 200 200' class='radar'>"
        & [SVG Radar Grade]
        & "<polygon class='radar-area' points='" & _pontos & "'/>"
        & "</svg>"
```

> 💡 **Armadilha clássica em pt-BR:** `FORMAT` sem o terceiro argumento gera `12,5` (vírgula decimal) e quebra o SVG. Sempre use `"en-US"`.

`[Valor Stat]` usa `SWITCH ( SELECTEDVALUE ( dStat[Codigo] ), "INT", ..., "FOR", ... )` lendo a versão em `[Id Selecionado]`.

### 7.3 HTML + CSS separados

```dax
HTML Ficha =
VAR _nome = LOOKUPVALUE ( dVersao[NomeVersao], dVersao[IdVersao], [Id Selecionado] )
RETURN
    [CSS Base] & [CSS Faccao]
        & "<div class='bc-card " & [Classe Faccao] & "'>"
        & "<div class='bc-scan'></div>"
        & "<h1 class='bc-title'>" & [HTML Escape Nome] & "</h1>"
        & [SVG Radar]
        & [HTML Afiliacoes]
        & "</div>"
```

Regras:

- Atributos HTML **sempre com aspas simples**.
- Medida `[HTML Escape …]` substitui `&`, `<`, `>` e `'` (ex.: **Ra's al Ghul**!).
- `[CSS Faccao]` é gerada a partir de `dPersonagem[Faccao]` e dos tokens em `src/css/tokens.css` (embutidos pelo build).

### 7.4 Serialização do modelo para JS

```dax
JS Gotham =
"window.GOTHAM=window.GOTHAM||{};GOTHAM.v=["
    & CONCATENATEX (
        dVersao,
        "{id:" & dVersao[IdVersao]
            & ",p:" & dVersao[IdPersonagem]
            & ",n:'" & SUBSTITUTE ( dVersao[NomeVersao], "'", "\'" ) & "'"
            & ",a:" & dVersao[IdArquetipo]
            & ",s:[" & dVersao[Int] & "," & dVersao[For] & "," & dVersao[Vel] & ","
                     & dVersao[Dur] & "," & dVersao[Pod] & "," & dVersao[Com] & "]"
            & ",img:'" & dVersao[UrlImagem] & "'}",
        ",", dVersao[IdVersao], ASC
    )
    & "];GOTHAM.m=" & [JS Matriz Arquetipos]
    & ";GOTHAM.g=" & [JS Golpes] & ";"
```

Cada página de app = `[JS Gotham]` + `[JS App Arena]` (código vindo de `src/js/arena.js`, embutido pelo build). Use chaves curtas (`n`, `a`, `s`) para reduzir o tamanho da string.

### 7.5 Estado resiliente a redesenho

```js
// src/js/arena.js  (sem aspas duplas!)
const S = (window.GOTHAM_STATE = window.GOTHAM_STATE || {});
S.arena = S.arena || { turno: 0, times: null, log: [] };
// render() sempre lê de S.arena — se o Power BI redesenhar o visual, a batalha continua
```

---

## 8. Game design: Arena, arquétipos e fórmulas

> Tudo aqui é **design ficcional do projeto**, não canônico. Fica em `data/seeds/` e é balanceado por simulação.

### 8.1 Arquétipos (equivalente aos tipos)

| Sigla | Arquétipo | Exemplos |
|---|---|---|
| EST | Estrategista / Detetive | Batman, Oráculo, Ra's al Ghul |
| LUT | Lutador marcial | Asa Noturna, Cassandra Cain, Lady Shiva |
| BRU | Brutamonte | Bane, Crocodilo, Solomon Grundy |
| TEC | Tecnológico | Sr. Frio, Lucius Fox, Chapeleiro Louco |
| MET | Meta-humano | Cara-de-Barro, Superman (convidado) |
| MIS | Místico / Sobrenatural | Etrigan, Zatanna, Corte das Corujas (Talons) |
| PSI | Psicológico / Manipulador | Coringa, Espantalho, Charada, Hugo Strange |
| FUR | Furtivo / Assassino | Mulher-Gato, Deathstroke, Capuz Vermelho |

### 8.2 Matriz de vantagens (ataque → defesa) — proposta inicial

| Atk \ Def | EST | LUT | BRU | TEC | MET | MIS | PSI | FUR |
|---|---|---|---|---|---|---|---|---|
| **EST** | 1 | 1 | 2 | 2 | 1 | ½ | ½ | 1 |
| **LUT** | 1 | 1 | ½ | 1 | ½ | 1 | 2 | 2 |
| **BRU** | ½ | 2 | 1 | 2 | 1 | 1 | 1 | ½ |
| **TEC** | ½ | 1 | 2 | 1 | 2 | ½ | 1 | 1 |
| **MET** | 1 | 2 | 1 | ½ | 1 | ½ | 1 | 2 |
| **MIS** | 2 | 1 | 1 | 1 | 2 | 1 | ½ | 1 |
| **PSI** | ½ | 2 | 2 | 1 | 1 | 1 | 1 | 1 |
| **FUR** | 2 | 1 | ½ | 2 | ½ | 1 | 1 | 1 |

Critério de aceite do balanceamento: na simulação de todos-contra-todos, nenhum arquétipo com taxa de vitória fora de **45%–55%**.

### 8.3 Atributos de batalha (derivados dos powerstats 0–100)

```
PV     = 120 + 2 × Durabilidade
AtkFis = (Força + Combate) / 2
AtkTat = (Inteligência + Poder) / 2
Def    = (Durabilidade + Combate) / 2
Ordem  = Velocidade  (empate → aleatório)
Crit%  = 4% + Combate / 20 %
```

### 8.4 Fórmula de dano (inspirada na fórmula dos jogos de RPG por turno, nível 50)

```
Base  = ((2 × 50 / 5 + 2) × PoderGolpe × Atk / Def) / 50 + 2
Mod   = Especialidade (1,5 se arquétipo do golpe = do usuário)
      × Matchup (matriz)
      × Crítico (1,5)
      × Aleatório (0,85 – 1,00)
Dano  = floor(Base × Mod)
```

**Transformações** (1 por batalha, por equipe): +25% em dois atributos e troca de arquétipo opcional (ex.: Bane com Veneno → BRU com +For/+Dur; Coringa não transforma, mas aplica "Gás do Riso" que reduz Precisão).

**IA:** escolhe o golpe com maior dano esperado; troca de personagem se o matchup recebido ≥ 2 e houver reserva com matchup ≤ ½.

### 8.5 Captura na Patrulha

```
Chance = min(0,95, Base_raridade × (1 − 2/3 × PVatual/PVmax) × Gadget × Bônus_bairro)
Base: comum 0,60 · incomum 0,40 · raro 0,20 · lendário 0,05
Gadget: Batarangue 1,0 · Bola-Gel 1,5 · Gancho 1,2 (+ fuga −) · Fumaça 2,0 só contra FUR
```

---

## 9. Identidade visual "Gotham Noir"

### 9.1 Tokens (`src/css/tokens.css`)

```css
:root {
  --g-bg: #07090c;          /* noite de Gotham */
  --g-panel: #10141a;
  --g-line: #1f2a36;
  --g-text: #d7dde4;
  --g-muted: #7d8794;
  --bat-yellow: #f5c518;    /* Bat-sinal */
  --arkham-green: #39d98a;
  --joker-purple: #7b2cbf;
  --blood: #c1121f;
  --ice: #8ecae6;
  --ivy: #2d6a4f;
  --owl-bronze: #a47148;
  --font-ui: 'Rajdhani', 'Barlow Condensed', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;   /* telas do Batcomputador */
  --font-title: 'Bebas Neue', sans-serif;
}
```

### 9.2 Temas animados por facção (CSS puro)

| Facção / tema | Efeito |
|---|---|
| Gotham (padrão) | Chuva diagonal + relâmpago ocasional |
| Coringa / Espantalho | Névoa verde pulsante, cartas caindo / gás |
| Sr. Frio | Cristais de gelo e respiração congelada nas bordas |
| Hera Venenosa | Vinhas crescendo nos cantos (`stroke-dashoffset`) |
| Charada | `?` verdes surgindo e sumindo |
| Duas-Caras | Moeda girando (3D `rotateY`), card dividido em duas metades |
| Corte das Corujas | Penas caindo, vinheta bronze |
| Bat-família | Bat-sinal varrendo o fundo |
| Vagalume | Brasas subindo |

### 9.3 Microinterações

- Scanline e "typing effect" no título do Batcomputador.
- Transição entre versões: *glitch* de 300 ms.
- Arena: shake de tela no crítico, número de dano flutuante, barra de PV com atraso (efeito "ghost").
- **Acessibilidade:** respeitar `prefers-reduced-motion`, contraste AA para texto, nunca só cor para indicar vantagem (usar ↑↓ e ×2/×½).

---

## 10. Estrutura do repositório

```
gotham-database/
├─ CLAUDE.md                     # regras globais para todos os agentes
├─ .claude/agents/               # definições dos subagentes (§13)
├─ contracts/                    # contratos entre agentes (fonte da verdade)
│  ├─ data-dictionary.md
│  ├─ js-data-schema.json
│  ├─ design-tokens.md
│  └─ measure-catalog.md
├─ handoffs/                     # relatórios de entrega de cada agente
├─ etl/
│  ├─ extract/  (superhero.py, comicvine.py, wikidata.py, tmdb.py, igdb.py)
│  ├─ transform/
│  ├─ quality/  (schemas pandera)
│  ├─ graph/    (centralidade networkx)
│  └─ run_etl.py
├─ data/
│  ├─ raw/        (cache, gitignored)
│  ├─ seeds/      (arquetipos.csv, matchup.csv, golpes.csv, bairros.csv, versoes.csv)
│  └─ curated/    (*.parquet / *.csv versionados)
├─ src/
│  ├─ dax/        (1 arquivo .dax por medida)
│  ├─ css/        (tokens.css, faccoes.css, ficha.css, arena.css…)
│  └─ js/         (arena.js, quiz.js, patrulha.js, rede.js, timeline.js, core.js)
├─ build/
│  ├─ build_model.py    # escreve medidas no TMDL, embutindo CSS/JS
│  ├─ build_report.py   # gera/atualiza páginas PBIR
│  └─ checks.py         # aspas duplas, tamanho máximo, chaves órfãs
├─ powerbi/
│  └─ GothamDatabase.pbip  (+ .SemanticModel/ TMDL, .Report/ PBIR)
├─ tests/
│  ├─ js/  (Vitest: dano, IA, captura, balanceamento)
│  ├─ etl/ (pytest: schemas, contagens, chaves)
│  └─ bpa/ (regras Best Practice Analyzer)
├─ docs/ (arquitetura.md, prints/, post-blog.md)
└─ .github/workflows/ci.yml
```

---

## 11. Time multiagente

### 11.1 Por que multiagentes

Cada parte do projeto exige uma especialidade diferente (curadoria de lore, engenharia de dados, DAX, design, JS de jogos, balanceamento). Agentes especializados, com **contexto limpo e instruções focadas**, produzem melhor do que um agente generalista com contexto saturado — desde que haja **contratos claros** entre eles e **revisão independente**.

### 11.2 Elenco

| Agente (arquivo) | Apelido | Responsabilidade | Entregáveis |
|---|---|---|---|
| `orquestrador` | **Alfred** | Planeja fases, quebra tarefas, mantém contratos, integra e decide conflitos | `contracts/*`, plano de sprint, merges |
| `curador-lore` | **Oráculo** | Seleção de personagens (~150–250), versões, obras, afiliações, arquétipos; checagem canônica com fontes | `data/seeds/*.csv` com coluna `fonte` |
| `engenheiro-dados` | **Lucius** | ETL Python, cache, normalização, deduplicação entre fontes, validação, centralidade | `etl/`, `data/curated/`, relatório de qualidade |
| `modelador-semantico` | **Gordon** | Modelo TMDL em estrela, relações, tabelas desconectadas, Power Query M | `.SemanticModel/`, `data-dictionary.md` |
| `engenheiro-dax` | **Batcomputador** | Medidas de seleção, HTML, SVG, serialização JS, analíticas | `src/dax/*.dax`, `measure-catalog.md` |
| `designer-ui` | **Selina** | Tokens, CSS por facção, animações, layout das páginas, acessibilidade | `src/css/*`, mockups, `design-tokens.md` |
| `dev-js-apps` | **Robin** | Apps JS: Arena, Quiz, Patrulha, Rede, Timeline | `src/js/*` |
| `game-designer` | **Ra's** | Fórmulas, matriz de arquétipos, golpes, tabela de encontros; balanceamento via simulação | `data/seeds/matchup.csv`, `golpes.csv`, relatório de balanceamento |
| `revisor-qa` | **Coruja** | Revisor **independente**: testes, performance (DAX Studio), BPA, acessibilidade, checagem de contratos | `handoffs/review-*.md` com aprovado/reprovado |
| `documentador` | **Vicki Vale** | README, documentação de arquitetura, post de blog, roteiro de vídeo/LinkedIn | `README.md`, `docs/` |

### 11.3 Contratos (o que torna o paralelismo seguro)

| Contrato | Dono | Consumidores |
|---|---|---|
| `data-dictionary.md` (tabelas, colunas, tipos, chaves) | Gordon | Lucius, Batcomputador, Coruja |
| `js-data-schema.json` (formato do objeto `GOTHAM`) | Batcomputador | Robin, Ra's, Coruja |
| `design-tokens.md` (cores, fontes, classes por facção) | Selina | Batcomputador, Robin |
| `measure-catalog.md` (nome, pasta, propósito, dependências) | Batcomputador | Coruja, Vicki |

**Regra:** só o dono altera o contrato; mudança exige nota no handoff e aviso ao Alfred, que repassa aos consumidores.

### 11.4 Protocolo de handoff

Todo agente termina escrevendo `handoffs/<fase>-<agente>-<tarefa>.md`:

```markdown
## Entrega: <tarefa>
- **Status:** pronto para revisão | bloqueado
- **Arquivos alterados:** ...
- **Decisões tomadas (e por quê):** ...
- **Contratos afetados:** nenhum | <qual e o que mudou>
- **Como testar:** comandos exatos
- **Pendências / riscos:** ...
```

---

## 12. Fluxo de trabalho, fases e quality gates

```
F0 Spike ─▶ F1 Curadoria ─▶ F2 ETL ─▶ F3 Modelo ─▶ ┌ F4a DAX      ┐ ─▶ F5 Integração ─▶ F6 QA ─▶ F7 Publicação
 (Alfred,     (Oráculo,       (Lucius)   (Gordon)    │ F4b Design   │     (Alfred)         (Coruja)   (Vicki)
  Robin)       Ra's)                                 │ F4c JS apps  │
                                                     └ F4d Balanço  ┘
                                                       (paralelo)
```

| Fase | Objetivo | Gate de saída (aprovado pela Coruja) |
|---|---|---|
| **F0 – Spike técnico** | Provar que o HTML Content executa JS, medir limite prático de tamanho de string, testar PBIP + build Python | Página "hello world" com JS animado + estado na `window` sobrevivendo a redesenho |
| **F1 – Curadoria** | Lista de personagens, versões, obras, arquétipos, seeds de game design | Seeds com 100% das linhas com `fonte`; amostra de 20 fatos checada contra 2 fontes |
| **F2 – ETL** | Coleta, cache, merge entre fontes, validação | `pytest` verde; 0 chaves órfãs; taxa de match entre fontes reportada |
| **F3 – Modelo** | TMDL em estrela, Power Query, tabelas desconectadas | BPA sem erros críticos; dicionário de dados completo |
| **F4a – DAX** | Medidas de seleção, HTML, SVG, JS | Cada medida < orçamento de tamanho; troca de personagem < 1,5 s no DAX Studio |
| **F4b – Design** | Tokens, CSS de facções, layouts | Contraste AA; `prefers-reduced-motion` respeitado; mockup aprovado |
| **F4c – JS apps** | Arena, Quiz, Patrulha, Rede, Timeline | Vitest verde; 0 aspas duplas; funciona com dados mock do schema |
| **F4d – Balanceamento** | Simulação todos-contra-todos | Taxas de vitória por arquétipo entre 45–55% |
| **F5 – Integração** | Build completo, páginas montadas | Relatório abre sem erro; navegação entre todas as páginas |
| **F6 – QA** | Testes de ponta a ponta, performance, revisão de lore | Checklist §14 100% |
| **F7 – Publicação** | Publish to web, README, post | Link público funcionando; README com prints e GIFs |

**Ciclo de cada tarefa:** Alfred atribui → agente executa → handoff → **Coruja revisa sem ver o raciocínio do autor** → aprovado (merge) ou reprovado (volta com lista objetiva) → máximo 3 ciclos, depois Alfred escala para você decidir.

---

## 13. Definições dos agentes (`.claude/agents/`)

> Formato de subagente do Claude Code (frontmatter + instruções). Ajuste `model` conforme seu plano: `opus` para raciocínio pesado, `sonnet` para execução, `haiku` para tarefas mecânicas.

### 13.1 `CLAUDE.md` (regras globais)

```markdown
# Gotham Database — regras globais
- Idioma: código e nomes técnicos em português sem acento (IdPersonagem), comentários em pt-BR.
- Fonte da verdade: /contracts. Nunca altere um contrato que não é seu.
- JS e HTML: PROIBIDO aspas duplas. Use aspas simples ou template literals.
- DAX: FORMAT numérico sempre com "en-US" quando o valor vai para SVG/JS/CSS.
- Escape de texto vindo de dados: & < > ' (ex.: Ra's al Ghul).
- Toda entrega termina com handoff em /handoffs seguindo o template.
- Nunca commite chaves de API (.env no .gitignore).
- Não invente fatos de lore: sem fonte, marque como "pendente de verificação".
```

### 13.2 `orquestrador.md`

```markdown
---
name: orquestrador
description: Alfred. Planeja fases, distribui tarefas aos subagentes, mantém /contracts e integra entregas. Use no início de cada fase e sempre que houver conflito entre agentes.
tools: Read, Write, Edit, Glob, Grep, Bash, Agent
model: opus
---
Você coordena o projeto Gotham Database.
1. Leia CLAUDE.md, o plano (docs/plano.md) e todos os handoffs abertos.
2. Quebre a fase atual em tarefas pequenas (≤ 1 entregável cada) com critério de aceite.
3. Dispare em paralelo apenas tarefas que dependem de contratos já congelados.
4. Toda entrega passa pelo revisor-qa antes de ser considerada concluída.
5. Após 3 reprovações seguidas na mesma tarefa, pare e peça decisão humana.
6. Ao fim da fase, escreva handoffs/Fx-resumo.md com o que foi feito e o que falta.
```

### 13.3 `curador-lore.md`

```markdown
---
name: curador-lore
description: Oráculo. Especialista no universo Batman (HQs, games, séries, filmes, animações). Seleciona personagens, versões, obras, afiliações e arquétipos com fontes verificáveis.
tools: Read, Write, Edit, WebSearch, WebFetch, Glob
model: opus
---
- Produza CSVs em data/seeds/ seguindo contracts/data-dictionary.md.
- Cada linha factual precisa de coluna fonte (URL). Fatos com apenas 1 fonte: confianca=baixa.
- Priorize cobertura: Bat-família, galeria de vilões clássica, Corte das Corujas, Liga das Sombras, GCPD, aliados frequentes.
- Versões por mídia: inclua apenas encarnações com diferença real de atributos ou visual.
- Atribua arquétipo com justificativa de 1 linha.
- Nunca copie textos longos das fontes; resuma com suas palavras.
```

### 13.4 `engenheiro-dados.md`

```markdown
---
name: engenheiro-dados
description: Lucius. Constrói o ETL em Python (extract/transform/quality/graph), cache em data/raw e saída em data/curated.
tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
model: sonnet
---
- Respeite limites de taxa (backoff exponencial, cache em disco, User-Agent identificado).
- Chaves via .env. Saídas determinísticas (ordenação estável) para diffs limpos.
- Merge entre fontes: chave canônica = IdPersonagem do seed; casamento por nome normalizado + aliases + Wikidata QID. Reporte taxa de match.
- Valide com pandera; falha de schema interrompe o pipeline.
- Calcule grau, intermediação e PageRank com networkx em etl/graph.
- Termine com pytest verde e handoff contendo contagens por tabela.
```

### 13.5 `modelador-semantico.md`

```markdown
---
name: modelador-semantico
description: Gordon. Dono do modelo TMDL em estrela, Power Query M e contracts/data-dictionary.md.
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
---
- Esquema em estrela, relações 1:N unidirecionais, chaves inteiras.
- Tabelas desconectadas: Modo, VersaoSel, RelacaoSel, ObraSel, TemaSel.
- Oculte colunas técnicas; organize pastas de exibição.
- Rode o Best Practice Analyzer (Tabular Editor CLI) e corrija erros críticos.
- Qualquer mudança de coluna atualiza o dicionário e é comunicada ao orquestrador.
```

### 13.6 `engenheiro-dax.md`

```markdown
---
name: engenheiro-dax
description: Batcomputador. Escreve medidas DAX de seleção, HTML, SVG, CSS embutido, serialização JS e medidas analíticas. Dono de contracts/js-data-schema.json e measure-catalog.md.
tools: Read, Write, Edit, Bash, Glob, Grep
model: opus
---
- Uma medida por arquivo em src/dax/. Use VAR/RETURN, sem cálculo repetido.
- HTML com aspas simples; textos de dados sempre passam pela medida de escape.
- FORMAT(..., "en-US") em tudo que vira SVG/CSS/JS.
- Serialize para JS com chaves curtas, respeitando js-data-schema.json.
- Meça no DAX Studio: tempo e tamanho (caracteres) de cada medida pesada; registre no handoff.
```

### 13.7 `designer-ui.md`

```markdown
---
name: designer-ui
description: Selina. Identidade visual Gotham Noir: tokens, CSS por facção, animações, layout de páginas e acessibilidade.
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
---
- Comece por contracts/design-tokens.md; CSS sempre via variáveis.
- Animações só com transform/opacity (performance); respeite prefers-reduced-motion.
- Contraste AA; nunca use apenas cor para transmitir vantagem/desvantagem.
- Não desenhe personagens, logos ou marcas registradas; use formas genéricas e as imagens vindas das fontes por URL.
- Entregue protótipo HTML estático em docs/prototipos/ para revisão antes de integrar.
```

### 13.8 `dev-js-apps.md`

```markdown
---
name: dev-js-apps
description: Robin. Desenvolve as apps JavaScript (Arena, Quiz, Patrulha em canvas, Rede de Relações, Timeline) que rodam dentro do visual HTML Content.
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
---
- JS puro, ES2020, sem aspas duplas, sem dependências externas não aprovadas.
- Estado em window.GOTHAM_STATE; render idempotente (pode ser chamado N vezes).
- Lógica pura (dano, IA, captura) separada da renderização para ser testável em Node.
- Desenvolva contra dados mock gerados de js-data-schema.json; testes Vitest obrigatórios.
- Canvas: requestAnimationFrame, pixel art com imageSmoothingEnabled=false, nenhum asset de cenário externo.
```

### 13.9 `game-designer.md`

```markdown
---
name: game-designer
description: Ra's. Define e balanceia fórmulas, matriz de arquétipos, golpes, transformações e tabelas de encontro/captura.
tools: Read, Write, Edit, Bash, Glob
model: opus
---
- Mantenha data/seeds/matchup.csv, golpes.csv, bairros.csv.
- Rode a simulação todos-contra-todos (tests/js/balance.test.js) com seed fixa.
- Meta: cada arquétipo entre 45% e 55% de vitórias; nenhum personagem acima de 75% contra a média.
- Documente cada ajuste (antes/depois) em handoffs.
```

### 13.10 `revisor-qa.md`

```markdown
---
name: revisor-qa
description: Coruja. Revisor independente. Avalia entregas sem acesso ao raciocínio do autor, roda testes, mede performance e valida contratos, lore e acessibilidade.
tools: Read, Bash, Glob, Grep, WebSearch, WebFetch
model: opus
---
- Você NÃO edita código. Você aprova ou reprova com lista objetiva e reproduzível.
- Sempre rode: pytest, vitest, build/checks.py, BPA. Anexe a saída resumida.
- Cheque aderência aos contratos e ao CLAUDE.md.
- Amostre 10 fatos de lore e confirme em fonte independente.
- Escreva handoffs/review-<tarefa>.md com veredito: APROVADO | REPROVADO (+ motivos).
```

### 13.11 `documentador.md`

```markdown
---
name: documentador
description: Vicki Vale. Documentação técnica, README com prints/GIFs, post de blog e texto para LinkedIn.
tools: Read, Write, Edit, Glob, Grep
model: sonnet
---
- README: o que é, link publicado, arquitetura (diagrama), como rodar, decisões técnicas, créditos e aviso legal.
- Post de blog no formato: resultado → técnicas → o que leva para relatórios reais.
- Linguagem clara, sem exagero; números reais (personagens, obras, medidas, testes).
```

---

## 14. Testes e qualidade

### 14.1 Automatizados (CI)

| Camada | Ferramenta | O que verifica |
|---|---|---|
| ETL | pytest + pandera | Schemas, unicidade de chaves, sem órfãos, contagens mínimas |
| Build | `build/checks.py` | 0 aspas duplas em JS/HTML; tamanho de cada medida abaixo do orçamento; tokens CSS existentes |
| JS | Vitest | Fórmula de dano, IA, captura, quiz; snapshot do render com dados mock |
| Balanceamento | Vitest (simulação) | Faixa 45–55% por arquétipo |
| Modelo | Tabular Editor BPA | Regras de boas práticas (relações, colunas ocultas, formatação) |

### 14.2 Manuais (checklist F6)

- [ ] Trocar 20 personagens seguidos sem erro visual ou "clique fantasma".
- [ ] Clique em versão de outro personagem é ignorado após troca na lista.
- [ ] Redimensionar/alternar página no meio de uma batalha e voltar: estado preservado.
- [ ] Nomes com apóstrofo e acento renderizam (Ra's al Ghul, Señor Ácido…).
- [ ] Tempo de troca de personagem < 1,5 s (DAX Studio + Performance Analyzer).
- [ ] Publicado na web: imagens carregam; nenhuma chave exposta.
- [ ] Modo reduzido de movimento funciona.
- [ ] Amostra de lore revisada (10 fatos, 2 fontes cada).

---

## 15. Riscos e mitigação

| Risco | Impacto | Mitigação |
|---|---|---|
| Visual HTML Content não executar JS ou ter limite de tamanho | Alto | **F0 Spike** antes de tudo; plano B: páginas JS mais enxutas, dados paginados por medida |
| Limites de taxa (Comic Vine/IGDB) | Médio | ETL com cache em disco, backoff, coleta incremental |
| Fontes divergentes (nomes, datas) | Médio | Chave canônica no seed, Wikidata como desempate, coluna `confianca` |
| String DAX gigante deixa o relatório lento | Alto | Chaves curtas, só colunas necessárias, medir em cada PR |
| Imagens externas quebrarem (hotlink) | Médio | Fallback para silhueta genérica em CSS; checagem periódica de URLs |
| Escopo explodir (jogos demais) | Alto | MVP primeiro (Batcomputador + Painel), depois uma página de jogo por sprint |
| Agentes divergirem | Médio | Contratos congelados por fase, orquestrador único, revisor independente |

---

## 16. Roadmap sugerido

| Sprint | Entregas | Resultado visível |
|---|---|---|
| **1** | F0 Spike + F1 Curadoria (50 personagens) + ETL básico | "Hello Gotham" com JS e lista de personagens |
| **2** | Modelo + Batcomputador (ficha, radar, temas por facção) | **MVP apresentável** |
| **3** | Modos Arkham/Versões/Capas + Painel do Comissário | Página analítica para portfólio |
| **4** | Rede de Relações + Linha do Tempo | Visualizações avançadas |
| **5** | Arena + balanceamento | Página de jogo principal |
| **6** | Quiz + Patrulha em Gotham | Minijogos |
| **7** | Meta da Arena (`fSimulacao`) + Caso do Dia + Comparador | Diferenciais técnicos |
| **8** | Expansão para ~200 personagens, layout mobile, QA final, publicação, README e post | Lançamento |

---

## 17. Prompt de kickoff

Cole no Claude Code na raiz do repositório (com `CLAUDE.md` e `.claude/agents/` criados):

```text
Você é o orquestrador (Alfred) do projeto Gotham Database. Leia CLAUDE.md e docs/plano.md
(este documento). Comece pela Fase 0:
1. Use o agente dev-js-apps para criar um spike: medida DAX que retorna HTML + JS com uma
   animação simples e um contador guardado em window.GOTHAM_STATE.
2. Use o agente engenheiro-dax para criar build/build_model.py que injeta essa medida no TMDL
   a partir de src/dax e src/js, e build/checks.py que reprova aspas duplas.
3. Envie ambos ao revisor-qa.
Ao final, escreva handoffs/F0-resumo.md com o que funcionou, limites medidos
(tamanho máximo de string que renderizou bem) e recomendação para a Fase 1.
Não avance para a Fase 1 sem minha aprovação.
```

---

## 18. Aspectos legais e créditos

- Projeto **pessoal, sem fins comerciais**, para estudo e portfólio.
- Batman e personagens relacionados pertencem à **DC Comics / Warner Bros. Discovery**. Imagens são referenciadas por URL das fontes originais, não redistribuídas no repositório.
- Não desenhar personagens/logos oficiais em SVG/canvas; a Patrulha usa sprites genéricos originais.
- Dados: SuperHero API, Comic Vine, Wikidata (CC0), TMDB (atribuição obrigatória: "This product uses the TMDB API but is not endorsed or certified by TMDB"), IGDB, DC Database/Fandom (CC BY-SA, com atribuição).
- Respeitar termos de uso de cada API (limites, atribuição, proibição de uso comercial quando houver).
- Inspiração: *Pokédex em Power BI* de Kelven Cardoso — citar no README.
