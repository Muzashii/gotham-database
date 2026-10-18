"""Validação das tabelas curadas (pandera) + integridade referencial. Falha interrompe o pipeline."""
from __future__ import annotations

import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

INT = "int64"
TXT = "str"
STAT = Column(INT, Check.in_range(0, 100))


def _pk(*cols: str) -> dict:
    return {"unique": list(cols)} if len(cols) > 1 else {}


SCHEMAS: dict[str, DataFrameSchema] = {
    "dPersonagem": DataFrameSchema({
        "IdPersonagem": Column(INT, unique=True), "Nome": Column(TXT), "Codinome": Column(TXT, nullable=True),
        "IdentidadeCivil": Column(TXT), "Alinhamento": Column(TXT, Check.isin(["Herói", "Vilão", "Anti-herói", "Neutro"])),
        "IdArquetipo": Column(INT), "JustificativaArquetipo": Column(TXT), "Faccao": Column(TXT),
        "PrimeiraAparicao": Column(TXT), "AnoEstreia": Column(INT, Check.in_range(1938, 2100)), "IdEra": Column(INT),
        "MidiaEstreia": Column(TXT), "Criadores": Column(TXT), "WikidataQid": Column(TXT, Check.str_matches(r"^Q\d+$")),
        "IdSuperHeroApi": Column("Int64", nullable=True), "ComicVineId": Column("Int64", nullable=True),
        "EdicoesComicVine": Column("Int64", nullable=True), "confianca": Column(TXT, Check.isin(["alta", "media", "baixa"])),
    }, strict=True),
    "dVersao": DataFrameSchema({
        "IdVersao": Column(INT, unique=True), "IdPersonagem": Column(INT), "NomeVersao": Column(TXT), "IdMidia": Column(INT),
        "Int": STAT, "For": STAT, "Vel": STAT, "Dur": STAT, "Pod": STAT, "Com": STAT, "IdArquetipo": Column(INT),
        "EhTransformacao": Column(INT, Check.isin([0, 1])),
        "Raridade": Column(TXT, Check.isin(["comum", "incomum", "raro", "lendario"])),
        "UrlImagem": Column(TXT, nullable=True), "confianca": Column(TXT),
    }, strict=True),
    "dEra": DataFrameSchema({"IdEra": Column(INT, unique=True), "Nome": Column(TXT), "AnoInicio": Column(INT),
                             "AnoFim": Column(INT), "Ordem": Column(INT, unique=True)}, strict=True),
    "dMidia": DataFrameSchema({"IdMidia": Column(INT, unique=True), "Nome": Column(TXT, unique=True)}, strict=True),
    "dAfiliacao": DataFrameSchema({"IdAfiliacao": Column(INT, unique=True), "Nome": Column(TXT), "Tipo": Column(TXT)}, strict=True),
    "bPersonagemAfiliacao": DataFrameSchema({"IdPersonagem": Column(INT), "IdAfiliacao": Column(INT),
                                             "Papel": Column(TXT, Check.isin(["Líder", "Membro", "Ex-membro", "Aliado"]))},
                                            strict=True, **_pk("IdPersonagem", "IdAfiliacao")),
    "dObra": DataFrameSchema({
        "IdObra": Column(INT, unique=True), "Titulo": Column(TXT, Check(lambda s: ~s.str.contains('"'))),
        "TipoMidia": Column(TXT, Check.isin(["HQ", "Animação", "Série", "Filme", "Game"])), "IdMidia": Column(INT),
        "Granularidade": Column(TXT, Check.isin(["Obra", "Série", "Episódio"])),
        "Ano": Column(INT, Check.in_range(1938, 2100)), "IdEra": Column(INT), "Plataforma": Column(TXT, nullable=True),
        "UrlCapa": Column(TXT, nullable=True), "WikidataQid": Column(TXT, nullable=True),
    }, strict=True),
    "fAparicao": DataFrameSchema({"IdPersonagem": Column(INT), "IdObra": Column(INT), "IdVersao": Column(INT),
                                  "EhEstreia": Column(INT, Check.isin([0, 1])), "Relevancia": Column(INT, Check.in_range(1, 3))},
                                 strict=True, **_pk("IdPersonagem", "IdObra")),
    "fRelacao": DataFrameSchema({
        "IdOrigem": Column(INT), "IdDestino": Column(INT),
        "TipoRelacao": Column(TXT, Check.isin(["aliado", "inimigo", "mentor", "família", "romance", "rival", "organização"])),
        "Peso": Column(INT, Check.in_range(1, 5)), "Fonte": Column(TXT),
    }, strict=True, checks=[Check(lambda d: d.IdOrigem != d.IdDestino, error="auto-relação"),
                            Check(lambda d: ~d.TipoRelacao.isin(["inimigo", "romance", "família", "rival"])
                                  | (d.IdOrigem < d.IdDestino), error="relação simétrica fora da forma canônica")],
       **_pk("IdOrigem", "IdDestino", "TipoRelacao")),
    "dArquetipo": DataFrameSchema({"IdArquetipo": Column(INT, unique=True), "Nome": Column(TXT), "Sigla": Column(TXT, unique=True),
                                   "Cor": Column(TXT, Check.str_matches(r"^#[0-9a-f]{6}$")), "Icone": Column(TXT)}, strict=True),
    "fMatchup": DataFrameSchema({"IdAtaque": Column(INT), "IdDefesa": Column(INT),
                                 "Multiplicador": Column("float64", Check.isin([0.5, 1.0, 2.0]))},
                                strict=True, **_pk("IdAtaque", "IdDefesa")),
    "dGolpe": DataFrameSchema({"IdGolpe": Column(INT, unique=True), "Nome": Column(TXT), "IdArquetipo": Column(INT),
                               "Categoria": Column(TXT, Check.isin(["Físico", "Tático"])), "Poder": Column(INT, Check.in_range(0, 150)),
                               "Precisao": Column(INT, Check.in_range(1, 100)), "Efeito": Column(TXT, nullable=True)}, strict=True),
    "bVersaoGolpe": DataFrameSchema({"IdVersao": Column(INT), "IdGolpe": Column(INT)}, strict=True, **_pk("IdVersao", "IdGolpe")),
    "dGadget": DataFrameSchema({"IdGadget": Column(INT, unique=True), "Nome": Column(TXT), "MultCaptura": Column("float64"),
                                "SoContraArquetipo": Column("Int64", nullable=True), "Efeito": Column(TXT, nullable=True)}, strict=True),
    "dBairro": DataFrameSchema({"IdBairro": Column(INT, unique=True), "Nome": Column(TXT), "BonusCaptura": Column("float64"),
                                "TemRecarga": Column(INT, Check.isin([0, 1])), "Cor": Column(TXT)}, strict=True),
    "fEncontro": DataFrameSchema({"IdBairro": Column(INT), "IdPersonagem": Column(INT), "Peso": Column(INT, Check.gt(0)),
                                  "Raridade": Column(TXT)}, strict=True, **_pk("IdBairro", "IdPersonagem")),
    "dCentralidade": DataFrameSchema({"IdPersonagem": Column(INT, unique=True), "Grau": Column(INT, Check.ge(0)),
                                      "Intermediacao": Column("float64", Check.in_range(0, 1)),
                                      "PageRank": Column("float64", Check.in_range(0, 1))}, strict=True),
    "dStat": DataFrameSchema({"Ordem": Column(INT, unique=True), "Codigo": Column(TXT, unique=True), "Rotulo": Column(TXT)}, strict=True),
}

# (tabela, coluna) -> (tabela referenciada, coluna)
FKS = [
    ("dPersonagem", "IdArquetipo", "dArquetipo", "IdArquetipo"), ("dPersonagem", "IdEra", "dEra", "IdEra"),
    ("dVersao", "IdPersonagem", "dPersonagem", "IdPersonagem"), ("dVersao", "IdArquetipo", "dArquetipo", "IdArquetipo"),
    ("dVersao", "IdMidia", "dMidia", "IdMidia"),
    ("bPersonagemAfiliacao", "IdPersonagem", "dPersonagem", "IdPersonagem"),
    ("bPersonagemAfiliacao", "IdAfiliacao", "dAfiliacao", "IdAfiliacao"),
    ("dObra", "IdEra", "dEra", "IdEra"), ("dObra", "IdMidia", "dMidia", "IdMidia"),
    ("fAparicao", "IdPersonagem", "dPersonagem", "IdPersonagem"), ("fAparicao", "IdObra", "dObra", "IdObra"),
    ("fAparicao", "IdVersao", "dVersao", "IdVersao"),
    ("fRelacao", "IdOrigem", "dPersonagem", "IdPersonagem"), ("fRelacao", "IdDestino", "dPersonagem", "IdPersonagem"),
    ("fMatchup", "IdAtaque", "dArquetipo", "IdArquetipo"), ("fMatchup", "IdDefesa", "dArquetipo", "IdArquetipo"),
    ("dGolpe", "IdArquetipo", "dArquetipo", "IdArquetipo"),
    ("bVersaoGolpe", "IdVersao", "dVersao", "IdVersao"), ("bVersaoGolpe", "IdGolpe", "dGolpe", "IdGolpe"),
    ("dGadget", "SoContraArquetipo", "dArquetipo", "IdArquetipo"),
    ("fEncontro", "IdBairro", "dBairro", "IdBairro"), ("fEncontro", "IdPersonagem", "dPersonagem", "IdPersonagem"),
    ("dCentralidade", "IdPersonagem", "dPersonagem", "IdPersonagem"),
]


def validar(tabelas: dict[str, pd.DataFrame]) -> dict[str, int]:
    """Valida schemas e chaves; levanta exceção no primeiro problema. Retorna órfãs por FK (sempre 0)."""
    faltando = set(SCHEMAS) - set(tabelas)
    if faltando:
        raise ValueError(f"tabelas ausentes: {sorted(faltando)}")
    for nome, schema in SCHEMAS.items():
        schema.validate(tabelas[nome], lazy=True)
    orfas = {}
    for t, c, rt, rc in FKS:
        valores = set(tabelas[t][c].dropna().astype("int64"))
        perdidas = valores - set(tabelas[rt][rc].astype("int64"))
        orfas[f"{t}.{c}"] = len(perdidas)
        if perdidas:
            raise ValueError(f"chaves órfãs em {t}.{c} -> {rt}.{rc}: {sorted(perdidas)[:10]}")
    return orfas


__all__ = ["SCHEMAS", "FKS", "validar", "ler_curado", "pa"]


def ler_curado(pasta) -> dict[str, pd.DataFrame]:
    """Lê data/curated/*.csv com os tipos declarados nos schemas (o mesmo contrato que o Power Query usa)."""
    tabelas = {}
    for nome, schema in SCHEMAS.items():
        tipos = {c: str(col.dtype) for c, col in schema.columns.items()}
        tabelas[nome] = pd.read_csv(pasta / f"{nome}.csv", dtype=tipos, encoding="utf-8")
    return tabelas
