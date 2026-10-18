"""Wikidata (CC0) via SPARQL: rótulo pt, primeira aparição (P4584) e criadores (P170)."""
from __future__ import annotations

import urllib.parse

from .http import get_json

SPARQL = "https://query.wikidata.org/sparql"


def fatos(qids: list[str]) -> dict[str, dict]:
    valores = " ".join(f"wd:{q}" for q in qids)
    consulta = f"""SELECT ?p ?ptLabel ?faLabel ?faData ?criadorLabel WHERE {{
      VALUES ?p {{ {valores} }}
      OPTIONAL {{ ?p rdfs:label ?ptLabel FILTER(LANG(?ptLabel)="pt") }}
      OPTIONAL {{ ?p wdt:P4584 ?fa . OPTIONAL {{ ?fa wdt:P577 ?faData }} }}
      OPTIONAL {{ ?p wdt:P170 ?criador }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}"""
    url = f"{SPARQL}?{urllib.parse.urlencode({'query': consulta})}"
    dados = get_json(url, cabecalhos={"Accept": "application/sparql-results+json"})
    out: dict[str, dict] = {}
    for b in dados["results"]["bindings"]:
        g = lambda k: b.get(k, {}).get("value")  # noqa: E731
        qid = g("p").rsplit("/", 1)[1]
        o = out.setdefault(qid, {"pt": g("ptLabel"), "estreia": set(), "criadores": set()})
        if g("faLabel"):
            o["estreia"].add(f"{g('faLabel')} ({(g('faData') or '')[:10]})")
        if g("criadorLabel"):
            o["criadores"].add(g("criadorLabel"))
    return {k: {**v, "estreia": sorted(v["estreia"]), "criadores": sorted(v["criadores"])} for k, v in out.items()}
