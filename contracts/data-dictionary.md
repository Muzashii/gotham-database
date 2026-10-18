# Dicionário de dados

- **Dono:** modelador-semantico (Gordon) · **Consumidores:** engenheiro-dados, engenheiro-dax, revisor-qa
- **Versão:** 0.2 (F1). Seeds congelados; tabelas do modelo seguem rascunho até a F3.

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
