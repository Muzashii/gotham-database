# Dicionário de dados

- **Dono:** modelador-semantico (Gordon) · **Consumidores:** engenheiro-dados, engenheiro-dax, revisor-qa
- **Versão:** 0.1 (F0 — rascunho). Será congelado ao fim da F1 junto com os seeds.

Convenções: chaves `Id*` são `int64`; texto apenas em dimensões; prefixos `d` (dimensão),
`f` (fato), `b` (ponte). Relações 1:N unidirecionais das dimensões para os fatos.

## Tabelas existentes no modelo (F0)

| Tabela | Tipo | Colunas | Observação |
|---|---|---|---|
| `_Medidas` | Medidas | `_` (oculta) | Gerada por `build/build_model.py`. Não editar. |
| `SpikeTamanho` | Desconectada | `Caracteres` int64 (oculta), `Rotulo` string (ordenada por `Caracteres`) | Só F0: mede o limite prático de tamanho de string no visual. Remover na F3. |

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
