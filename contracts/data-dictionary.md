# Dicionário de dados

- **Dono:** modelador-semantico (Gordon) · **Consumidores:** engenheiro-dados, engenheiro-dax, revisor-qa
- **Versão:** 0.4 (F3). Seeds, tabelas curadas e modelo semântico definidos.

Convenções: chaves `Id*` são `int64`; texto apenas em dimensões; prefixos `d` (dimensão),
`f` (fato), `b` (ponte). Relações N:1 unidirecionais (o lado 1 filtra o lado N), inclusive cadeias dimensão → dimensão (ex.: dArquetipo → dPersonagem → dVersao).

## Tabelas existentes no modelo (F0)

| Tabela | Tipo | Colunas | Observação |
|---|---|---|---|
| `_Medidas` | Medidas | `_` (oculta) | Gerada por `build/build_model.py`. Não editar. |
| `SpikeTamanho` | Desconectada | `Caracteres` int64 (oculta), `Rotulo` string (ordenada por `Caracteres`) | Só F0: mede o limite prático de tamanho de string no visual. Mantida até a F5 (o link público mostra a página F0). |

## Seeds da F1 (`data/seeds/*.csv`) — v0.2, congelado ao fim da F1

UTF-8, separador vírgula, cabeçalho na 1ª linha. **Toda linha tem `fonte`** (URL ou "design do projeto …").
Textos sem aspas duplas (vão para HTML/JS). Teste: `tests/etl/test_seeds.py`.

| Arquivo | → Tabela | Chave | Colunas além das do §6 / observações |
|---|---|---|---|
| `personagens.csv` | `dPersonagem` | `IdPersonagem` | `Alinhamento` ∈ Herói/Vilão/Anti-herói/Neutro; `JustificativaArquetipo`; `MidiaEstreia` ∈ HQ/Animação/Série/Filme/Game; `WikipediaTitulo`, `WikidataQid`, `IdSuperHeroApi` (chaves cruzadas p/ ETL); `confianca` ∈ alta (2+ fontes concordam) / media (fontes divergem em persona ou edição) / baixa (1 fonte); `nota` |
| `versoes.csv` | `dVersao` | `IdVersao` = `IdPersonagem`×100 + n | F1 só tem a versão padrão (`n`=1). Atributos 0–100 (SuperHero API ou estimativa do curador → `confianca` baixa) |
| `eras.csv` | `dEra` | `IdEra` | `AnoFim` = 9999 para era em andamento; eras contíguas |
| `afiliacoes.csv` | `dAfiliacao` | `IdAfiliacao` | `nota` |
| `personagem_afiliacao.csv` | `bPersonagemAfiliacao` | (`IdPersonagem`, `IdAfiliacao`) | `Papel` ∈ Líder/Membro/Ex-membro/Aliado |
| `obras.csv` | `dObra` | `IdObra` | F1 só tem as obras de estreia |
| `aparicoes.csv` | `fAparicao` | (`IdPersonagem`, `IdObra`) | F1 só tem estreias (`EhEstreia`=1) |
| `arquetipos.csv` | `dArquetipo` | `IdArquetipo` | design |
| `matchup.csv` | `fMatchup` | (`IdAtaque`, `IdDefesa`) | 64 linhas; ∈ {0.5, 1, 2} |
| `golpes.csv` | `dGolpe` | `IdGolpe` | `Categoria` ∈ Físico/Tático; 3 por arquétipo |
| `versao_golpe.csv` | `bVersaoGolpe` | (`IdVersao`, `IdGolpe`) | 4 por versão (3 do arquétipo + 1 de cobertura) |
| `gadgets.csv` | `dGadget` (novo) | `IdGadget` | `MultCaptura`, `SoContraArquetipo` (vazio = todos) — §8.5 |
| `bairros.csv` | `dBairro` | `IdBairro` | `BonusCaptura`, `TemRecarga`, `Cor` |
| `encontros.csv` | `fEncontro` | (`IdBairro`, `IdPersonagem`) | só não-heróis; `Raridade` = da versão |

## Tabelas curadas da F2 (`data/curated/*.csv`) — v0.3

Saída de `python -m etl.run_etl`; tipos e regras em `etl/quality/schemas.py` (pandera, `strict=True`) —
**esta é a fonte da verdade das colunas que o Power Query lê na F3**. Ordenadas pela chave, UTF-8, LF.
Colunas de proveniência dos seeds (`fonte`, `nota`, `WikipediaTitulo`) ficam fora do modelo.
**Power Query:** os CSVs não têm BOM — declarar `Encoding=65001` em `Csv.Document`. `IdObra` cabe em Int64 (máx. ≈ 1,2 bi).

| Tabela | Linhas (F2) | Diferenças em relação ao §6 / aos seeds |
|---|---|---|
| `dPersonagem` | 50 | + `WikidataQid`, `IdSuperHeroApi`, `ComicVineId`, `EdicoesComicVine` (Int64 anuláveis), `confianca` |
| `dVersao` | 50 | sem `fonte`. `EhTransformacao` é inteiro 0/1 (não booleano) |
| `dEra`, `dAfiliacao`, `dArquetipo`, `dGolpe`, `dGadget`, `dBairro` | 8, 6, 8, 24, 4, 6 | sem `fonte`/`nota` |
| `dMidia` (nova) | 5 | `IdMidia`, `Nome` (HQ, Animação, Série, Filme, Game) |
| `dObra` | 319 | + `IdMidia`, `Granularidade` (Obra/Série/Episódio — séries e episódios coexistem; filtre por granularidade em análises), `WikidataQid`. `IdObra` 1–48 = obras de estreia; Wikidata = número do QID + 1.000.000.000 (estável) |
| `fAparicao` | 689 | estreias (`Relevancia` 3) + obras do Wikidata P674 (`Relevancia` 1) |
| `fRelacao` | 116 | + `Fonte` (propriedade Wikidata ou afiliação). `TipoRelacao` ∈ aliado/inimigo/mentor/família/romance/rival/organização; `Peso` por tipo. Tipos simétricos (todos menos mentor e organização) guardados uma vez, com `IdOrigem` < `IdDestino` |
| `dCentralidade` | 50 | `Grau`, `Intermediacao`, `PageRank` (grafo não dirigido, ponderado) |
| `dStat` | 6 | INT, FOR, VEL, DUR, POD, COM |
| `bPersonagemAfiliacao`, `bVersaoGolpe`, `fMatchup`, `fEncontro` | 54, 200, 64, 42 | sem `fonte` |

<!-- modelo:inicio -->
## Modelo semântico (F3) — gerado por `build/build_tabelas.py`

Fonte de cada tabela: `LerCsv("<tabela>")` → `data/curated/<tabela>.csv` no GitHub (UTF-8, en-US).
Colunas `Id*` e técnicas ficam ocultas; tudo com `summarizeBy: none` exceto `EdicoesComicVine`.

### Tabelas

| Tabela | Colunas (tipo; *oculta*) | Descrição |
|---|---|---|
| `dPersonagem` | *IdPersonagem* (int64), Nome (string), Codinome (string), IdentidadeCivil (string), Alinhamento (string), *IdArquetipo* (int64), *JustificativaArquetipo* (string), Faccao (string), PrimeiraAparicao (string), AnoEstreia (int64), *IdEra* (int64), MidiaEstreia (string), Criadores (string), *WikidataQid* (string), *IdSuperHeroApi* (int64), *ComicVineId* (int64), *EdicoesComicVine* (int64), confianca (string) | Um personagem por linha (50 na F2). Chave canônica do projeto. |
| `dVersao` | *IdVersao* (int64), *IdPersonagem* (int64), NomeVersao (string), *IdMidia* (int64), Int (int64), For (int64), Vel (int64), Dur (int64), Pod (int64), Com (int64), *IdArquetipo* (int64), EhTransformacao (int64), Raridade (string), *UrlImagem* (string), confianca (string) | Encarnação de um personagem com atributos de batalha (0–100). F2: só a versão padrão (Id×100+1). |
| `dEra` | *IdEra* (int64), Nome (string), AnoInicio (int64), AnoFim (int64), Ordem (int64) | Eras editoriais (limites por convenção). |
| `dMidia` | *IdMidia* (int64), Nome (string) | HQ, Animação, Série, Filme, Game. |
| `dAfiliacao` | *IdAfiliacao* (int64), Nome (string), Tipo (string) | Grupos (Bat-família, GCPD, Liga das Sombras…). |
| `bPersonagemAfiliacao` | *IdPersonagem* (int64), *IdAfiliacao* (int64), Papel (string) | Ponte personagem × afiliação. Filtro só da dimensão para a ponte; use TREATAS no DAX. |
| `dObra` | *IdObra* (int64), Titulo (string), TipoMidia (string), *IdMidia* (int64), Granularidade (string), Ano (int64), *IdEra* (int64), *Plataforma* (string), *UrlCapa* (string), *WikidataQid* (string) | Obras (estreias + Wikidata P674) com mídia e granularidade. |
| `fAparicao` | *IdPersonagem* (int64), *IdObra* (int64), *IdVersao* (int64), EhEstreia (int64), Relevancia (int64) | Personagem × obra. EhEstreia=1 marca a primeira aparição. |
| `fRelacao` | *IdOrigem* (int64), *IdDestino* (int64), TipoRelacao (string), Peso (int64), *Fonte* (string) | Arestas tipadas entre personagens (simétricas em forma canônica Origem < Destino). |
| `dArquetipo` | *IdArquetipo* (int64), Nome (string), Sigla (string), Cor (string), Icone (string) | 8 arquétipos de combate (design). |
| `fMatchup` | *IdAtaque* (int64), *IdDefesa* (int64), Multiplicador (double) | Multiplicador de dano arquétipo atacante × defensor. |
| `dGolpe` | *IdGolpe* (int64), Nome (string), *IdArquetipo* (int64), Categoria (string), Poder (int64), Precisao (int64), Efeito (string) | Golpes/gadgets de batalha (design). |
| `bVersaoGolpe` | *IdVersao* (int64), *IdGolpe* (int64) | Ponte versão × golpe (4 por versão). |
| `dGadget` | *IdGadget* (int64), Nome (string), MultCaptura (double), *SoContraArquetipo* (int64), Efeito (string) | Gadgets de captura da Patrulha. |
| `dBairro` | *IdBairro* (int64), Nome (string), BonusCaptura (double), TemRecarga (int64), Cor (string) | Bairros de Gotham da Patrulha. |
| `fEncontro` | *IdBairro* (int64), *IdPersonagem* (int64), Peso (int64), Raridade (string) | Bairro × personagem com peso de sorteio. |
| `dCentralidade` | *IdPersonagem* (int64), Grau (int64), Intermediacao (double), PageRank (double) | Grau, intermediação e PageRank da rede de relações (calculados no ETL). |
| `dStat` | Ordem (int64), Codigo (string), Rotulo (string) | Os 6 atributos, na ordem do radar. |
| `Modo` | Ordem (int64), Modo (string), Icone (string) | Desconectada. Modo da ficha do Batcomputador. |
| `TemaSel` | Ordem (int64), Faccao (string), Tema (string) | Desconectada. Tema visual por facção (classes fx-* de contracts/design-tokens.md). |
| `VersaoSel` | IdVersao (int64), NomeVersao (string) | Desconectada. Cópia desconectada das versões (clique no carrossel de versões). |
| `RelacaoSel` | IdPersonagem (int64), Nome (string) | Desconectada. Cópia desconectada dos personagens (clique em nó do grafo). |
| `ObraSel` | IdObra (int64), Titulo (string) | Desconectada. Cópia desconectada das obras (clique em marco da linha do tempo). |

### Relações (todas N:1, filtro único da dimensão para o fato)

| De (N) | Para (1) | Ativa | Motivo |
|---|---|---|---|
| `dPersonagem.IdArquetipo` | `dArquetipo.IdArquetipo` | sim |  |
| `dPersonagem.IdEra` | `dEra.IdEra` | **não** | ambígua com dEra→dObra→fAparicao; era de estreia via USERELATIONSHIP |
| `dVersao.IdPersonagem` | `dPersonagem.IdPersonagem` | sim |  |
| `dVersao.IdArquetipo` | `dArquetipo.IdArquetipo` | **não** | ambígua com dArquetipo→dPersonagem→dVersao; arquétipo da versão (transformações) via USERELATIONSHIP |
| `dVersao.IdMidia` | `dMidia.IdMidia` | sim |  |
| `bPersonagemAfiliacao.IdPersonagem` | `dPersonagem.IdPersonagem` | sim |  |
| `bPersonagemAfiliacao.IdAfiliacao` | `dAfiliacao.IdAfiliacao` | sim |  |
| `dObra.IdEra` | `dEra.IdEra` | sim |  |
| `dObra.IdMidia` | `dMidia.IdMidia` | sim |  |
| `fAparicao.IdPersonagem` | `dPersonagem.IdPersonagem` | sim |  |
| `fAparicao.IdObra` | `dObra.IdObra` | sim |  |
| `fAparicao.IdVersao` | `dVersao.IdVersao` | **não** | ambígua com dPersonagem→dVersao→fAparicao |
| `fRelacao.IdOrigem` | `dPersonagem.IdPersonagem` | sim |  |
| `fRelacao.IdDestino` | `dPersonagem.IdPersonagem` | **não** | duas relações para a mesma tabela; destino via USERELATIONSHIP |
| `fMatchup.IdAtaque` | `dArquetipo.IdArquetipo` | sim |  |
| `fMatchup.IdDefesa` | `dArquetipo.IdArquetipo` | **não** | duas relações para a mesma tabela; defesa via USERELATIONSHIP |
| `dGolpe.IdArquetipo` | `dArquetipo.IdArquetipo` | **não** | ambígua com dArquetipo→dPersonagem→dVersao→bVersaoGolpe |
| `bVersaoGolpe.IdVersao` | `dVersao.IdVersao` | sim |  |
| `bVersaoGolpe.IdGolpe` | `dGolpe.IdGolpe` | sim |  |
| `dGadget.SoContraArquetipo` | `dArquetipo.IdArquetipo` | **não** | vazio = vale contra todos; ativa, o filtro por arquétipo esconderia os gadgets universais |
| `fEncontro.IdBairro` | `dBairro.IdBairro` | sim |  |
| `fEncontro.IdPersonagem` | `dPersonagem.IdPersonagem` | sim |  |
| `dCentralidade.IdPersonagem` | `dPersonagem.IdPersonagem` | sim |  |

<!-- modelo:fim -->

## Tabelas planejadas (F1–F3) — ver `docs/plano.md` §6

| Tabela | Tipo | Grão | Colunas |
|---|---|---|---|
| `dPersonagem` | Dimensão | personagem | `IdPersonagem` int64 PK, `Nome`, `Codinome`, `IdentidadeCivil`, `Alinhamento`, `IdArquetipo` int64, `PrimeiraAparicao`, `AnoEstreia` int64, `IdEra` int64, `Criadores`, `UrlImagem`, `Faccao` |
| `dVersao` | Dimensão | encarnação | `IdVersao` int64 PK, `IdPersonagem` int64, `NomeVersao`, `IdMidia` int64, `Int`/`For`/`Vel`/`Dur`/`Pod`/`Com` int64 (0–100), `IdArquetipo` int64, `EhTransformacao` bool, `Raridade`, `UrlImagem` |
| `dObra` | Dimensão | obra | `IdObra` PK, `Titulo`, `TipoMidia` (HQ/Série/Animação/Filme/Game), `Ano`, `IdEra`, `Plataforma`, `UrlCapa` |
| `dEra` | Dimensão | era | `IdEra` PK, `Nome`, `AnoInicio`, `AnoFim`, `Ordem` |
| `dAfiliacao` | Dimensão | grupo | `IdAfiliacao` PK, `Nome`, `Tipo` |
| `bPersonagemAfiliacao` | Ponte | personagem × grupo | `IdPersonagem`, `IdAfiliacao`, `Papel` |
| `fAparicao` | Fato | personagem × obra | `IdPersonagem`, `IdObra`, `IdVersao`, `EhEstreia`, `Relevancia` |
| `fRelacao` | Fato | par direcionado | `IdOrigem`, `IdDestino`, `TipoRelacao`, `Peso` |
| `dArquetipo` | Dimensão | 8 linhas | `IdArquetipo` PK, `Nome`, `Sigla`, `Cor`, `Icone` |
| `fMatchup` | Fato | arquétipo × arquétipo | `IdAtaque`, `IdDefesa`, `Multiplicador` decimal |
| `dGolpe` | Dimensão | golpe | `IdGolpe` PK, `Nome`, `IdArquetipo`, `Categoria`, `Poder`, `Precisao`, `Efeito` |
| `bVersaoGolpe` | Ponte | versão × golpe | `IdVersao`, `IdGolpe` |
| `dBairro` / `fEncontro` | Dim/Fato | bairro × personagem | `IdBairro`, `IdPersonagem`, `Peso`, `Raridade` |
| `dCentralidade` | Dimensão | personagem | `IdPersonagem`, `Grau`, `Intermediacao`, `PageRank` |
| `dStat` | Auxiliar | 6 linhas | `Ordem`, `Codigo`, `Rotulo` |
| `fSimulacao` | Fato | versão × versão | `IdVersaoA`, `IdVersaoB`, `Lutas`, `VitoriasA`, `TurnosMedios`, `DanoMedioA` |
| `dCaso` / `bCasoPista` | Dim/Ponte | caso / caso × pista | `IdCaso`, `IdCulpado`, `Dificuldade`; `Ordem`, `TipoPista`, `Valor` |

Desconectadas: `Modo`, `VersaoSel`, `RelacaoSel`, `ObraSel`, `TemaSel`.
