# Dicionário de dados

- **Dono:** modelador-semantico (Gordon) · **Consumidores:** engenheiro-dados, engenheiro-dax, revisor-qa
- **Versão:** 0.3 (F2). Seeds e tabelas curadas definidos; o modelo TMDL segue na F3.

Convenções: chaves `Id*` são `int64`; texto apenas em dimensões; prefixos `d` (dimensão),
`f` (fato), `b` (ponte). Relações 1:N unidirecionais das dimensões para os fatos.

## Tabelas existentes no modelo (F0)

| Tabela | Tipo | Colunas | Observação |
|---|---|---|---|
| `_Medidas` | Medidas | `_` (oculta) | Gerada por `build/build_model.py`. Não editar. |
| `SpikeTamanho` | Desconectada | `Caracteres` int64 (oculta), `Rotulo` string (ordenada por `Caracteres`) | Só F0: mede o limite prático de tamanho de string no visual. Remover na F3. |

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
