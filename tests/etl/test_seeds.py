"""Gate F1: integridade dos seeds (contrato em contracts/data-dictionary.md)."""
import csv
import re
from pathlib import Path

import pytest

SEEDS = Path(__file__).resolve().parents[2] / "data" / "seeds"

CABECALHOS = {
    "personagens.csv": ["IdPersonagem", "Nome", "Codinome", "IdentidadeCivil", "Alinhamento", "IdArquetipo",
                        "JustificativaArquetipo", "Faccao", "PrimeiraAparicao", "AnoEstreia", "IdEra", "MidiaEstreia",
                        "Criadores", "WikipediaTitulo", "WikidataQid", "IdSuperHeroApi", "fonte", "confianca", "nota"],
    "versoes.csv": ["IdVersao", "IdPersonagem", "NomeVersao", "IdMidia", "Int", "For", "Vel", "Dur", "Pod", "Com",
                    "IdArquetipo", "EhTransformacao", "Raridade", "UrlImagem", "fonte", "confianca"],
    "eras.csv": ["IdEra", "Nome", "AnoInicio", "AnoFim", "Ordem", "fonte", "nota"],
    "arquetipos.csv": ["IdArquetipo", "Nome", "Sigla", "Cor", "Icone", "fonte"],
    "matchup.csv": ["IdAtaque", "IdDefesa", "Multiplicador", "fonte"],
    "afiliacoes.csv": ["IdAfiliacao", "Nome", "Tipo", "fonte", "nota"],
    "personagem_afiliacao.csv": ["IdPersonagem", "IdAfiliacao", "Papel", "fonte"],
    "obras.csv": ["IdObra", "Titulo", "TipoMidia", "Ano", "IdEra", "Plataforma", "UrlCapa", "fonte"],
    "aparicoes.csv": ["IdPersonagem", "IdObra", "IdVersao", "EhEstreia", "Relevancia", "fonte"],
    "golpes.csv": ["IdGolpe", "Nome", "IdArquetipo", "Categoria", "Poder", "Precisao", "Efeito", "fonte"],
    "versao_golpe.csv": ["IdVersao", "IdGolpe", "fonte"],
    "gadgets.csv": ["IdGadget", "Nome", "MultCaptura", "SoContraArquetipo", "Efeito", "fonte"],
    "bairros.csv": ["IdBairro", "Nome", "BonusCaptura", "TemRecarga", "Cor", "fonte"],
    "encontros.csv": ["IdBairro", "IdPersonagem", "Peso", "Raridade", "fonte"],
}
FACCOES = {"gotham", "batfamilia", "coringa", "espantalho", "frio", "hera", "charada", "duascaras", "corujas", "vagalume"}
RARIDADES = {"comum", "incomum", "raro", "lendario"}


def ler(nome):
    with open(SEEDS / nome, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ids(nome, col):
    return {int(r[col]) for r in ler(nome)}


@pytest.mark.parametrize("nome", sorted(CABECALHOS))
def test_cabecalho_bate_com_o_contrato(nome):
    with open(SEEDS / nome, encoding="utf-8") as f:
        assert next(csv.reader(f)) == CABECALHOS[nome]


@pytest.mark.parametrize("nome", sorted(CABECALHOS))
def test_toda_linha_tem_fonte(nome):
    sem = [i for i, r in enumerate(ler(nome), 2) if not r["fonte"].strip()]
    assert not sem, f"linhas sem fonte: {sem}"


@pytest.mark.parametrize("nome", sorted(CABECALHOS))
def test_sem_aspas_duplas_nos_textos(nome):
    """Textos vão para HTML/JS com aspas simples; aspas duplas quebrariam a string DAX."""
    for r in ler(nome):
        for k, v in r.items():
            assert '"' not in v, f"{nome}:{k}={v!r}"


@pytest.mark.parametrize("nome,chave", [
    ("personagens.csv", ("IdPersonagem",)), ("versoes.csv", ("IdVersao",)), ("eras.csv", ("IdEra",)),
    ("arquetipos.csv", ("IdArquetipo",)), ("matchup.csv", ("IdAtaque", "IdDefesa")),
    ("afiliacoes.csv", ("IdAfiliacao",)), ("personagem_afiliacao.csv", ("IdPersonagem", "IdAfiliacao")),
    ("obras.csv", ("IdObra",)), ("aparicoes.csv", ("IdPersonagem", "IdObra")), ("golpes.csv", ("IdGolpe",)),
    ("versao_golpe.csv", ("IdVersao", "IdGolpe")), ("gadgets.csv", ("IdGadget",)), ("bairros.csv", ("IdBairro",)),
    ("encontros.csv", ("IdBairro", "IdPersonagem")),
])
def test_chave_unica(nome, chave):
    valores = [tuple(r[c] for c in chave) for r in ler(nome)]
    assert len(valores) == len(set(valores))


@pytest.mark.parametrize("nome,col,ref,refcol", [
    ("personagens.csv", "IdArquetipo", "arquetipos.csv", "IdArquetipo"),
    ("personagens.csv", "IdEra", "eras.csv", "IdEra"),
    ("versoes.csv", "IdPersonagem", "personagens.csv", "IdPersonagem"),
    ("versoes.csv", "IdArquetipo", "arquetipos.csv", "IdArquetipo"),
    ("personagem_afiliacao.csv", "IdPersonagem", "personagens.csv", "IdPersonagem"),
    ("personagem_afiliacao.csv", "IdAfiliacao", "afiliacoes.csv", "IdAfiliacao"),
    ("obras.csv", "IdEra", "eras.csv", "IdEra"),
    ("aparicoes.csv", "IdPersonagem", "personagens.csv", "IdPersonagem"),
    ("aparicoes.csv", "IdObra", "obras.csv", "IdObra"),
    ("aparicoes.csv", "IdVersao", "versoes.csv", "IdVersao"),
    ("matchup.csv", "IdAtaque", "arquetipos.csv", "IdArquetipo"),
    ("matchup.csv", "IdDefesa", "arquetipos.csv", "IdArquetipo"),
    ("golpes.csv", "IdArquetipo", "arquetipos.csv", "IdArquetipo"),
    ("versao_golpe.csv", "IdVersao", "versoes.csv", "IdVersao"),
    ("versao_golpe.csv", "IdGolpe", "golpes.csv", "IdGolpe"),
    ("encontros.csv", "IdBairro", "bairros.csv", "IdBairro"),
    ("encontros.csv", "IdPersonagem", "personagens.csv", "IdPersonagem"),
])
def test_sem_chaves_orfas(nome, col, ref, refcol):
    orfas = {int(r[col]) for r in ler(nome)} - ids(ref, refcol)
    assert not orfas


def test_cinquenta_personagens_com_versao_padrao_e_estreia():
    pers = ids("personagens.csv", "IdPersonagem")
    assert len(pers) == 50
    assert {int(v["IdPersonagem"]) for v in ler("versoes.csv")} == pers
    assert {int(a["IdPersonagem"]) for a in ler("aparicoes.csv") if a["EhEstreia"] == "1"} == pers


def test_dominios_dos_personagens():
    for p in ler("personagens.csv"):
        assert p["Alinhamento"] in {"Herói", "Vilão", "Anti-herói", "Neutro"}
        assert p["Faccao"] in FACCOES
        assert p["MidiaEstreia"] in {"HQ", "Animação", "Série", "Filme", "Game"}
        assert p["confianca"] in {"alta", "media", "baixa"}
        assert p["JustificativaArquetipo"].strip(), "arquétipo sem justificativa"
        assert re.fullmatch(r"Q\d+", p["WikidataQid"]), p["Nome"]


def test_confianca_alta_exige_duas_fontes():
    for p in ler("personagens.csv"):
        if p["confianca"] == "alta":
            assert len(p["fonte"].split()) >= 2, p["Nome"]


def test_era_bate_com_o_ano_de_estreia():
    eras = {int(e["IdEra"]): (int(e["AnoInicio"]), int(e["AnoFim"])) for e in ler("eras.csv")}
    for p in ler("personagens.csv"):
        a, b = eras[int(p["IdEra"])]
        assert a <= int(p["AnoEstreia"]) <= b, p["Nome"]


def test_eras_contiguas():
    eras = sorted((int(e["AnoInicio"]), int(e["AnoFim"])) for e in ler("eras.csv"))
    for (_, fim), (ini, _) in zip(eras, eras[1:]):
        assert ini == fim + 1


def test_atributos_entre_0_e_100_e_raridade_valida():
    for v in ler("versoes.csv"):
        for k in ("Int", "For", "Vel", "Dur", "Pod", "Com"):
            assert 0 <= int(v[k]) <= 100, (v["NomeVersao"], k)
        assert v["Raridade"] in RARIDADES
        assert v["confianca"] in {"alta", "baixa"}


def test_matriz_completa_8x8_com_multiplicadores_validos():
    m = ler("matchup.csv")
    assert len(m) == 64
    assert {float(r["Multiplicador"]) for r in m} <= {0.5, 1.0, 2.0}


def test_cada_arquetipo_tem_3_golpes_e_cada_versao_4():
    por_arq = {}
    for g in ler("golpes.csv"):
        por_arq[g["IdArquetipo"]] = por_arq.get(g["IdArquetipo"], 0) + 1
        assert 0 <= int(g["Poder"]) <= 120 and 0 < int(g["Precisao"]) <= 100
    assert sorted(por_arq.values()) == [3] * 8
    por_versao = {}
    for vg in ler("versao_golpe.csv"):
        por_versao[vg["IdVersao"]] = por_versao.get(vg["IdVersao"], 0) + 1
    assert set(por_versao.values()) == {4}


def test_encontros_so_com_nao_herois_e_raridade_da_versao():
    alin = {p["IdPersonagem"]: p["Alinhamento"] for p in ler("personagens.csv")}
    rar = {v["IdPersonagem"]: v["Raridade"] for v in ler("versoes.csv")}
    for e in ler("encontros.csv"):
        assert alin[e["IdPersonagem"]] != "Herói"
        assert e["Raridade"] == rar[e["IdPersonagem"]]
    assert ids("encontros.csv", "IdBairro") == ids("bairros.csv", "IdBairro")


def test_cobertura_do_plano():
    """Prioridades do curador: Bat-família, galeria clássica, Liga das Sombras, GCPD."""
    pa = ler("personagem_afiliacao.csv")
    por_af = {}
    for r in pa:
        por_af[int(r["IdAfiliacao"])] = por_af.get(int(r["IdAfiliacao"]), 0) + 1
    assert por_af[1] >= 12 and por_af[2] >= 20 and por_af[4] >= 3 and por_af[5] >= 3
