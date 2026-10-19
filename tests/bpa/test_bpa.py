"""Regras de boas práticas do modelo (subconjunto do Best Practice Analyzer do Tabular Editor), lidas do TMDL.

Severidade entre colchetes como no BPA: [Erro] falha o gate F3; [Aviso] também falha aqui, por política do projeto.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[2]
DEF = RAIZ / "powerbi" / "GothamDatabase.SemanticModel" / "definition"
sys.path.insert(0, str(RAIZ / "build"))
import build_tabelas  # noqa: E402
import modelo_spec as spec  # noqa: E402


def ler_tabelas() -> dict[str, dict]:
    """{tabela: {'descricao': bool, 'colunas': {col: {prop: valor}}, 'medidas': {nome: {prop: valor}}}}."""
    tabelas = {}
    for arq in (DEF / "tables").glob("*.tmdl"):
        texto = arq.read_text(encoding="utf-8")
        m = re.search(r"^table (.+)$", texto, re.M)
        nome = m.group(1).strip("'")
        antes = texto[: m.start()]
        t = {"descricao": bool(re.search(r"^/// ", antes, re.M)), "colunas": {}, "medidas": {}}
        atual = None
        for linha in texto.splitlines():
            if mc := re.match(r"^\tcolumn (.+)$", linha):
                atual = t["colunas"].setdefault(mc.group(1).strip("'"), {})
            elif mm := re.match(r"^\tmeasure (.+?) =", linha):
                atual = t["medidas"].setdefault(mm.group(1).strip("'"), {})
            elif re.match(r"^\t\S", linha):
                atual = None
            elif atual is not None and (mp := re.match(r"^\t\t(\w+)(?::\s*(.*))?$", linha)):
                atual[mp.group(1)] = mp.group(2) if mp.group(2) is not None else True
        tabelas[nome] = t
    return tabelas


def ler_relacoes() -> list[dict]:
    texto = (DEF / "relationships.tmdl").read_text(encoding="utf-8")
    rels = []
    for bloco in re.split(r"^relationship ", texto, flags=re.M)[1:]:
        props = dict(re.findall(r"^\t(\w+): (.+)$", bloco, re.M))
        de_t, de_c = props["fromColumn"].split(".")
        para_t, para_c = props["toColumn"].split(".")
        rels.append({"de": (de_t, de_c), "para": (para_t, para_c), "ativa": props.get("isActive") != "false",
                     "filtro": props.get("crossFilteringBehavior", "oneDirection"),
                     "card": (props.get("fromCardinality", "many"), props.get("toCardinality", "one"))})
    return rels


TABELAS = ler_tabelas()
RELACOES = ler_relacoes()


def test_erro_toda_relacao_e_muitos_para_um():
    assert all(r["card"] == ("many", "one") for r in RELACOES)


def test_erro_sem_filtro_bidirecional():
    assert all(r["filtro"] == "oneDirection" for r in RELACOES)


def test_erro_relacoes_ativas_sem_caminho_ambiguo():
    """Entre duas tabelas não pode haver mais de um caminho de filtro ativo (o Power BI recusa o modelo)."""
    filtra = defaultdict(list)  # lado 1 filtra lado N
    for r in RELACOES:
        if r["ativa"]:
            filtra[r["para"][0]].append(r["de"][0])

    def caminhos(origem, destino, visitados=()):
        if origem == destino:
            return 1
        return sum(caminhos(p, destino, visitados + (origem,)) for p in filtra[origem] if p not in visitados)

    nos = set(TABELAS)
    ambiguos = [(a, b, n) for a in nos for b in nos if a != b and (n := caminhos(a, b)) > 1]
    assert not ambiguos


def test_erro_no_maximo_uma_relacao_ativa_entre_duas_tabelas():
    pares = [(r["de"][0], r["para"][0]) for r in RELACOES if r["ativa"]]
    assert len(pares) == len(set(pares))


def test_erro_colunas_das_relacoes_existem_e_tem_o_mesmo_tipo():
    for r in RELACOES:
        (dt, dc), (pt, pc) = r["de"], r["para"]
        assert dc in TABELAS[dt]["colunas"] and pc in TABELAS[pt]["colunas"], r
        assert TABELAS[dt]["colunas"][dc]["dataType"] == TABELAS[pt]["colunas"][pc]["dataType"] == "int64", r


def test_erro_lado_1_da_relacao_e_unico_nos_dados():
    for r in RELACOES:
        t, c = r["para"]
        valores = pd.read_csv(RAIZ / "data" / "curated" / f"{t}.csv", usecols=[c])[c]
        assert valores.is_unique, f"{t}.{c} não é único: relação {r['de']} -> {r['para']}"


def test_aviso_chaves_estrangeiras_ocultas():
    for r in RELACOES:
        t, c = r["de"]
        assert TABELAS[t]["colunas"][c].get("isHidden"), f"{t}.{c}"


def test_aviso_colunas_numericas_sem_soma_implicita():
    for t, d in TABELAS.items():
        for c, p in d["colunas"].items():
            if p.get("dataType") in ("int64", "double") and c not in spec.SOMAR:
                assert p.get("summarizeBy") == "none", f"{t}.{c}"


def test_aviso_chaves_nao_sao_ponto_flutuante():
    for t, d in TABELAS.items():
        for c, p in d["colunas"].items():
            if re.match(r"Id[A-Z]", c):  # IdentidadeCivil não é chave
                assert p["dataType"] == "int64", f"{t}.{c}"


def test_aviso_modelo_desencoraja_medidas_implicitas():
    assert re.search(r"^\tdiscourageImplicitMeasures$", (DEF / "model.tmdl").read_text(encoding="utf-8"), re.M)


def test_aviso_medidas_tem_pasta_de_exibicao():
    for t, d in TABELAS.items():
        for m, p in d["medidas"].items():
            assert p.get("displayFolder"), f"{t}[{m}]"


def test_aviso_tabelas_do_modelo_tem_descricao():
    for t in [*spec.DESCRICAO, *spec.DESCONECTADAS]:
        assert TABELAS[t]["descricao"], t


def test_aviso_sort_by_aponta_para_coluna_existente():
    for t, d in TABELAS.items():
        for c, p in d["colunas"].items():
            if "sortByColumn" in p:
                assert p["sortByColumn"] in d["colunas"], f"{t}.{c}"


def test_toda_tabela_tem_arquivo_e_ref_no_model():
    refs = {r.strip("'") for r in re.findall(r"^ref table (.+)$", (DEF / "model.tmdl").read_text(encoding="utf-8"), re.M)}
    assert refs == set(TABELAS)


def test_desconectadas_sem_relacao():
    usadas = {r["de"][0] for r in RELACOES} | {r["para"][0] for r in RELACOES}
    assert not (set(spec.DESCONECTADAS) & usadas)


def test_todas_as_tabelas_curadas_estao_no_modelo():
    from etl.quality.schemas import SCHEMAS
    assert set(SCHEMAS) <= set(TABELAS)


@pytest.mark.parametrize("caminho", sorted(build_tabelas.gerar(), key=str), ids=lambda p: p.name)
def test_tmdl_gerado_esta_sincronizado(caminho):
    """Rode build/build_tabelas.py depois de mudar schemas.py/modelo_spec.py ou de salvar no Desktop."""
    esperado = build_tabelas.gerar()[caminho]
    esperado = esperado if esperado.endswith("\n") else esperado + "\n"
    assert caminho.read_text(encoding="utf-8") == esperado
