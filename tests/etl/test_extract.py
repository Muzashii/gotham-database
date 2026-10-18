"""Regressões da revisão F1: comparador de estreias (M2) e cache HTTP (M3)."""
import io
import json
import urllib.error

import pytest

from etl.curadoria.checar import concorda
from etl.extract import http


@pytest.mark.parametrize("a,b,esperado", [
    ("Batman #999 (jan 2099)", "''Batman'' (16 July 1943)", False),          # caso da revisão: ano conflita
    ("Batman (vol. 2) #21 (ago 2013)", "Batman (vol. 2) #21 (2014)", True),  # capa x venda: ±1 ano
    ("Batman (vol. 2) #21 (2013)", "Batman (vol. 3) #21 (2013)", False),    # volume diferente
    ("Detective Comics #27 (maio 1939)", "Detective Comics #27", True),
    ("Detective Comics #27 (maio 1939)", "Detective Comics #38", False),
    ("Batman: Son of the Demon (1987)", "Batman: Son of the Demon", True),  # edição única sem número
    ("Batman Beyond — Rebirth (1999)", "Batman Beyond #1", False),          # episódio x HQ: obras diferentes
    ("Detective Comics #27", "Action Comics #27", False),
])
def test_concorda(a, b, esperado):
    assert concorda(a, b) is esperado


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


@pytest.fixture
def cache_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(http, "CACHE", tmp_path)
    monkeypatch.setattr(http, "PAUSA", 0)
    monkeypatch.setattr(http.time, "sleep", lambda s: None)
    return tmp_path


def test_ratelimited_com_http_200_repete_e_nao_vai_para_o_cache(cache_tmp, monkeypatch):
    respostas = [{"error": {"code": "ratelimited"}}, {"ok": 1}]
    monkeypatch.setattr(http.urllib.request, "urlopen",
                        lambda req, timeout: _Resp(json.dumps(respostas.pop(0)).encode()))
    assert http.get_json("https://exemplo.test/a") == {"ok": 1}
    [arq] = cache_tmp.iterdir()
    assert json.loads(arq.read_text(encoding="utf-8")) == {"ok": 1}


def test_erro_de_api_nunca_e_cacheado(cache_tmp, monkeypatch):
    monkeypatch.setattr(http.urllib.request, "urlopen",
                        lambda req, timeout: _Resp(json.dumps({"error": {"code": "badtitle"}}).encode()))
    with pytest.raises(RuntimeError):
        http.get_json("https://exemplo.test/b")
    assert not list(cache_tmp.iterdir())


def test_queda_de_conexao_repete(cache_tmp, monkeypatch):
    chamadas = []

    def urlopen(req, timeout):
        chamadas.append(1)
        if len(chamadas) == 1:
            raise urllib.error.URLError("conexão recusada")
        return _Resp(b"[1, 2]")

    monkeypatch.setattr(http.urllib.request, "urlopen", urlopen)
    assert http.get_json("https://exemplo.test/c") == [1, 2]
    assert len(chamadas) == 2


def test_trechos_nao_corta_volume():
    from etl.curadoria.checar import trechos
    assert any(concorda("Batman (vol. 2) #21 (2013)", t) for t in trechos("''Batman'' (vol. 2) #21 (New 52) (2014)"))


def _cv(monkeypatch, resultados):
    from etl.extract import comicvine
    monkeypatch.setattr(comicvine, "get_json", lambda url, **kw: {"status_code": 1, "results": resultados(url)})
    return comicvine


def _pers(nome, real, edicoes, cid):
    return {"id": cid, "name": nome, "real_name": real, "count_of_issue_appearances": edicoes,
            "publisher": {"name": "DC Comics"}, "first_appeared_in_issue": {"name": "X", "issue_number": "1"}}


def test_comicvine_terry_nao_casa_com_o_batman_de_bruce(monkeypatch):
    """N1 da revisão F2: manto compartilhado no título da Wikipédia."""
    todos = [_pers("Batman", "Bruce Wayne", 9000, 1), _pers("Terry McGinnis", "Terrence McGinnis", 300, 2)]
    cv = _cv(monkeypatch, lambda url: todos)
    r = cv.buscar("Batman (Terry McGinnis)", "Terry McGinnis", "chave")
    assert r["id"] == 2


def test_comicvine_casa_por_nome_civil_e_ignora_outras_editoras(monkeypatch):
    todos = [_pers("Robin", "Damian Wayne", 50, 3), _pers("Robin", "Dick Grayson", 5000, 4),
             {**_pers("Damian", "Damian Wayne", 9, 5), "publisher": {"name": "Marvel"}}]
    cv = _cv(monkeypatch, lambda url: todos)
    assert cv.buscar("Damian Wayne", "Damian Wayne", "chave")["id"] == 3


def test_comicvine_sem_casamento_exato_devolve_none(monkeypatch):
    cv = _cv(monkeypatch, lambda url: [_pers("Joker Jr.", "", 5, 6)])
    assert cv.buscar("Joker (character)", "desconhecida", "chave") is None
