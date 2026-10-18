"""Wikidata (CC0) via SPARQL: fatos dos personagens, obras em que aparecem (P674) e relações entre eles."""
from __future__ import annotations

import urllib.parse

from .http import get_json

SPARQL = "https://query.wikidata.org/sparql"


def _consultar(consulta: str) -> list[dict]:
    url = f"{SPARQL}?{urllib.parse.urlencode({'query': consulta})}"
    dados = get_json(url, cabecalhos={"Accept": "application/sparql-results+json"})
    return [{k: v["value"] for k, v in b.items()} for b in dados["results"]["bindings"]]


def _qid(uri: str | None) -> str | None:
    return uri.rsplit("/", 1)[1] if uri else None


def fatos(qids: list[str]) -> dict[str, dict]:
    valores = " ".join(f"wd:{q}" for q in qids)
    consulta = f"""SELECT ?p ?ptLabel ?faLabel ?faData ?criadorLabel WHERE {{
      VALUES ?p {{ {valores} }}
      OPTIONAL {{ ?p rdfs:label ?ptLabel FILTER(LANG(?ptLabel)="pt") }}
      OPTIONAL {{ ?p wdt:P4584 ?fa . OPTIONAL {{ ?fa wdt:P577 ?faData }} }}
      OPTIONAL {{ ?p wdt:P170 ?criador }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}"""
    out: dict[str, dict] = {}
    for b in _consultar(consulta):
        g = b.get
        qid = _qid(g("p"))
        o = out.setdefault(qid, {"pt": g("ptLabel"), "estreia": set(), "criadores": set()})
        if g("faLabel"):
            o["estreia"].add(f"{g('faLabel')} ({(g('faData') or '')[:10]})")
        if g("criadorLabel"):
            o["criadores"].add(g("criadorLabel"))
    return {k: {**v, "estreia": sorted(v["estreia"]), "criadores": sorted(v["criadores"])} for k, v in out.items()}


def obras(qids: list[str]) -> list[dict]:
    """Uma linha por (obra, personagem, tipo da obra, tipo da série-mãe), com a data mais antiga.

    Tipos, série-mãe e gêneros vêm como rótulo em inglês (ex.: "animated film") para a classificação
    no transform. Título em inglês quando existir (rótulos pt do Wikidata às vezes são de outra obra
    homônima), senão pt. Data: publicação (P577), início (P580) ou criação (P571).
    """
    valores = " ".join(f"wd:{q}" for q in qids)
    consulta = f"""SELECT ?obra ?obraLabel ?p ?tipoEn ?serieTipoEn (SAMPLE(?serieEn) AS ?serieNome)
        (GROUP_CONCAT(DISTINCT ?generoEn; separator="|") AS ?generos) (MIN(?d) AS ?data) WHERE {{
      VALUES ?p {{ {valores} }}
      ?obra wdt:P674 ?p ; wdt:P31 ?tipo .
      OPTIONAL {{ ?tipo rdfs:label ?tipoEn FILTER(LANG(?tipoEn)="en") }}
      OPTIONAL {{ ?obra wdt:P577|wdt:P580|wdt:P571 ?d }}
      OPTIONAL {{ ?obra wdt:P179 ?serie . ?serie rdfs:label ?serieEn FILTER(LANG(?serieEn)="en")
                 OPTIONAL {{ ?serie wdt:P31 ?serieTipo .
                            ?serieTipo rdfs:label ?serieTipoEn FILTER(LANG(?serieTipoEn)="en") }} }}
      OPTIONAL {{ ?obra wdt:P136 ?genero . ?genero rdfs:label ?generoEn FILTER(LANG(?generoEn)="en") }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,pt". }}
    }} GROUP BY ?obra ?obraLabel ?p ?tipoEn ?serieTipoEn"""
    return [{"obra": _qid(b.get("obra")), "titulo": b.get("obraLabel"), "personagem": _qid(b.get("p")),
             "tipo": b.get("tipoEn") or "", "serie_tipo": b.get("serieTipoEn") or "",
             "serie": b.get("serieNome") or "", "generos": b.get("generos") or "",
             "data": (b.get("data") or "")[:10]}
            for b in _consultar(consulta)]


# propriedade Wikidata -> (TipoRelacao, inverter origem/destino)
RELACOES = {
    "P7047": ("inimigo", False),   # enemy of
    "P451": ("romance", False),    # unmarried partner
    "P26": ("romance", False),     # spouse
    "P3373": ("família", False),   # sibling
    "P22": ("família", False),     # father
    "P25": ("família", False),     # mother
    "P40": ("família", False),     # child
    "P1038": ("família", False),   # relative
    "P1066": ("mentor", True),     # student of: aluno -> mentor  ==> mentor -> aluno
    "P802": ("mentor", False),     # student: mentor -> aluno
    "P2546": ("aliado", False),    # sidekick of
    "P3342": ("aliado", False),    # significant person
}


def relacoes(qids: list[str]) -> list[dict]:
    """Arestas dirigidas entre os personagens da lista, tipadas pelas propriedades acima."""
    valores = " ".join(f"wd:{q}" for q in qids)
    props = " ".join(f"wdt:{p}" for p in RELACOES)
    consulta = f"""SELECT ?a ?prop ?b WHERE {{
      VALUES ?a {{ {valores} }} VALUES ?b {{ {valores} }} VALUES ?prop {{ {props} }}
      ?a ?prop ?b .
    }}"""
    saida = []
    for r in _consultar(consulta):
        prop = _qid(r["prop"])
        tipo, inverte = RELACOES[prop]
        a, b = _qid(r["a"]), _qid(r["b"])
        if inverte:
            a, b = b, a
        saida.append({"origem": a, "destino": b, "tipo": tipo, "propriedade": prop})
    return saida
