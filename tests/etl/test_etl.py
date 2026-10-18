"""ETL da F2: transformações puras, centralidade, validação e as tabelas curadas commitadas."""
import pandas as pd
import pandera.errors
import pytest

from etl.graph.centralidade import centralidade
from etl.quality.schemas import SCHEMAS, ler_curado, validar
from etl.run_etl import CURADO
from etl.transform import modelo


@pytest.mark.parametrize("tipo,serie,esperado", [
    ("video game", "video game series", "Game"),
    ("animated film", "film series", "Animação"),
    ("film", "animated film series", "Animação"),
    ("film", "film trilogy", "Filme"),
    ("television series episode", "animated television series", "Animação"),
    ("television series episode", "", "Série"),
    ("limited series", "", "HQ"),
    ("comic book storyline", "comic book series", "HQ"),
    ("esports discipline", "video game series", None),
    ("literary work", "", None),
    ("", "", None),
])
def test_classificar_midia(tipo, serie, esperado):
    assert modelo.classificar_midia(tipo, serie) == esperado


def test_limpar_texto_troca_aspas_duplas():
    assert modelo.limpar_texto('O "Cavaleiro" das Trevas') == "O “Cavaleiro” das Trevas"
    assert '"' not in modelo.limpar_texto('aspas "soltas')


ERAS = pd.DataFrame({"IdEra": [1, 4], "AnoInicio": [1938, 1986], "AnoFim": [1985, 2100]})


def _seed_obras():
    obras = pd.DataFrame({"IdObra": [5], "Titulo": ["Batman #436"], "TipoMidia": ["HQ"], "Ano": [1989], "IdEra": [4],
                          "Plataforma": [""], "UrlCapa": [""]})
    ap = pd.DataFrame({"IdPersonagem": [5], "IdObra": [5], "IdVersao": [501], "EhEstreia": [1], "Relevancia": [3]})
    return obras, ap


def test_filme_batman_1989_nao_e_a_hq_batman_436():
    """Regressão: título contido no outro + mesmo ano não basta para unificar obras."""
    linhas = [{"obra": "Q116852", "titulo": "Batman", "personagem": "Q1", "tipo": "film", "serie_tipo": "", "data": "1989-06-23"}]
    wd_obras, wd_ap, _ = modelo.obras_wikidata(linhas, ERAS, {"Q1": 1})
    obras, ap = _seed_obras()
    d_obra, f_ap, dup = modelo.obras_e_aparicoes(obras, ap, wd_obras, wd_ap)
    assert dup == [] and len(d_obra) == 2


def test_obra_igual_unifica_e_mantem_estreia():
    linhas = [{"obra": "Q9", "titulo": "Batman #436", "personagem": "Q5", "tipo": "comic", "serie_tipo": "", "data": "1989-08-01"}]
    wd_obras, wd_ap, _ = modelo.obras_wikidata(linhas, ERAS, {"Q5": 5})
    obras, ap = _seed_obras()
    d_obra, f_ap, dup = modelo.obras_e_aparicoes(obras, ap, wd_obras, wd_ap)
    assert len(dup) == 1 and len(d_obra) == 1 and d_obra.WikidataQid.iloc[0] == "Q9"
    assert f_ap.to_dict("records") == [{"IdPersonagem": 5, "IdObra": 5, "IdVersao": 501, "EhEstreia": 1, "Relevancia": 3}]


def test_obras_sem_data_ou_fora_do_escopo_sao_descartadas_e_contadas():
    linhas = [{"obra": "Q1", "titulo": "A", "personagem": "Q5", "tipo": "film", "serie_tipo": "", "data": ""},
              {"obra": "Q2", "titulo": "B", "personagem": "Q5", "tipo": "literary work", "serie_tipo": "", "data": "1990"}]
    d, ap, est = modelo.obras_wikidata(linhas, ERAS, {"Q5": 5})
    assert d.empty and est["obras_sem_data"] == 1 and est["obras_fora_do_escopo"] == 1


def test_relacoes_inclui_organizacao_e_remove_duplicatas():
    wd = [{"origem": "Q1", "destino": "Q2", "tipo": "mentor", "propriedade": "P802"},
          {"origem": "Q1", "destino": "Q2", "tipo": "mentor", "propriedade": "P1066"},
          {"origem": "Q1", "destino": "Q1", "tipo": "inimigo", "propriedade": "P7047"}]
    afil = pd.DataFrame({"IdPersonagem": [1, 2, 3], "IdAfiliacao": [1, 1, 1], "Papel": ["Líder", "Membro", "Aliado"]})
    r = modelo.relacoes(wd, {"Q1": 1, "Q2": 2}, afil)
    assert sorted(zip(r.IdOrigem, r.IdDestino, r.TipoRelacao)) == [(1, 2, "mentor"), (1, 2, "organização")]


def test_centralidade_inclui_isolados_e_hub():
    rel = pd.DataFrame({"IdOrigem": [1, 1, 1], "IdDestino": [2, 3, 4], "Peso": [1, 1, 1]})
    c = centralidade(pd.Series([1, 2, 3, 4, 5]), rel).set_index("IdPersonagem")
    assert c.loc[5, "Grau"] == 0 and c.loc[1, "Grau"] == 3
    assert c.Intermediacao.idxmax() == 1


# ---------------------------------------------------------------- tabelas curadas (sem rede)


@pytest.fixture(scope="module")
def curado():
    return ler_curado(CURADO)


def test_tabelas_curadas_passam_nos_schemas_e_sem_orfas(curado):
    assert set(validar(curado).values()) == {0}


def test_tamanhos_minimos(curado):
    assert len(curado["dPersonagem"]) == 50
    assert len(curado["dObra"]) >= 200 and len(curado["fAparicao"]) >= 500
    assert len(curado["fRelacao"]) >= 100  # 115 pares únicos na F2
    assert set(curado["dObra"].TipoMidia) == {"HQ", "Animação", "Série", "Filme", "Game"}


def test_toda_obra_tem_aparicao_e_todo_personagem_tem_estreia(curado):
    ap = curado["fAparicao"]
    assert set(curado["dObra"].IdObra) == set(ap.IdObra)
    assert set(ap.loc[ap.EhEstreia == 1, "IdPersonagem"]) == set(curado["dPersonagem"].IdPersonagem)


def test_batman_e_o_hub_da_rede(curado):
    c = curado["dCentralidade"].merge(curado["dPersonagem"][["IdPersonagem", "Nome"]])
    assert c.sort_values("Intermediacao").Nome.iloc[-1] == "Batman"


def test_validacao_reprova_atributo_fora_da_faixa(curado):
    ruim = {**curado, "dVersao": curado["dVersao"].assign(For=101)}
    with pytest.raises(pandera.errors.SchemaErrors):
        validar(ruim)


def test_validacao_reprova_chave_orfa(curado):
    extra = curado["fAparicao"].iloc[[0]].assign(IdObra=-1)
    ruim = {**curado, "fAparicao": pd.concat([curado["fAparicao"], extra])}
    with pytest.raises(ValueError, match="órfãs"):
        validar(ruim)


def test_todo_schema_tem_csv(curado):
    assert set(curado) == set(SCHEMAS)


# ---------------------------------------------------------------- regressões da revisão F2


def test_relacao_simetrica_registrada_nos_dois_itens_vira_um_par():
    """B1: Batman inimigo de Coringa e Coringa inimigo de Batman = 1 aresta (menor id -> maior id)."""
    wd = [{"origem": "Q19", "destino": "Q1", "tipo": "inimigo", "propriedade": "P7047"},
          {"origem": "Q1", "destino": "Q19", "tipo": "inimigo", "propriedade": "P7047"}]
    r = modelo.relacoes(wd, {"Q1": 1, "Q19": 19}, pd.DataFrame(columns=["IdPersonagem", "IdAfiliacao", "Papel"]))
    assert list(zip(r.IdOrigem, r.IdDestino, r.TipoRelacao)) == [(1, 19, "inimigo")]


def test_mentor_mantem_a_direcao():
    wd = [{"origem": "Q3", "destino": "Q1", "tipo": "mentor", "propriedade": "P802"}]
    r = modelo.relacoes(wd, {"Q1": 1, "Q3": 3}, pd.DataFrame(columns=["IdPersonagem", "IdAfiliacao", "Papel"]))
    assert list(zip(r.IdOrigem, r.IdDestino)) == [(3, 1)]


def test_filme_com_genero_animacao_e_animacao():
    assert modelo.classificar_midia("film", "", "animated film|superhero film") == "Animação"
    assert modelo.classificar_midia("film", "", "superhero film") == "Filme"


@pytest.mark.parametrize("tipo,esperado", [("television series episode", "Episódio"), ("animated television series", "Série"),
                                            ("comic book series", "Série"), ("film series", "Obra"), ("film", "Obra"),
                                            ("video game", "Obra")])
def test_granularidade(tipo, esperado):
    assert modelo.granularidade(tipo) == esperado


def test_descartes_contados_e_titulo_de_episodio_com_serie():
    base = {"personagem": "Q5", "serie_tipo": "", "generos": "", "serie": ""}
    linhas = [
        {**base, "obra": "Q1", "titulo": "Q1", "tipo": "film", "data": "2000"},                 # sem rótulo
        {**base, "obra": "Q2", "titulo": "Futuro", "tipo": "film", "data": "2999"},             # futura
        {**base, "obra": "Q3", "titulo": "Detective Comics", "tipo": "comic book series", "data": "1937"},  # antes da 1ª era
        {**base, "obra": "Q4", "titulo": "Pilot", "tipo": "television series episode", "serie": "Smallville", "data": "2001"},
    ]
    d, ap, est = modelo.obras_wikidata(linhas, ERAS, {"Q5": 5}, ano_maximo=2026)
    assert (est["obras_sem_rotulo"], est["obras_futuras"], est["obras_antes_da_1a_era"]) == (1, 1, 1)
    assert est["obras_brutas"] == sum(v for k, v in est.items() if k not in ("obras_brutas",))
    assert d.Titulo.tolist() == ["Smallville — Pilot"] and d.Granularidade.tolist() == ["Episódio"]


def test_schema_reprova_relacao_simetrica_nao_canonica(curado):
    linha = pd.DataFrame([{"IdOrigem": 19, "IdDestino": 1, "TipoRelacao": "inimigo", "Peso": 1, "Fonte": "x"}])
    ruim = {**curado, "fRelacao": pd.concat([curado["fRelacao"], linha], ignore_index=True)}
    with pytest.raises(pandera.errors.SchemaErrors):
        validar(ruim)


def test_contagens_do_relatorio_fecham():
    import json
    q = json.loads((CURADO / "_qualidade.json").read_text(encoding="utf-8"))["obras"]
    descartes = sum(v for k, v in q.items() if k.startswith("obras_") and k not in ("obras_brutas", "obras_no_modelo"))
    assert q["obras_brutas"] == descartes + q["obras_no_modelo"]
