"""Infobox (seção 0) de artigos da Wikipédia em inglês: QID, estreia e criadores."""
from __future__ import annotations

import re
import urllib.parse

from .http import get_json

API = "https://en.wikipedia.org/w/api.php"


def _campo(txt: str, nome: str) -> str | None:
    m = re.search(r"\|\s*" + nome + r"\s*=\s*(.*?)\n\s*\|", txt, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else None


def infobox(titulo: str) -> dict:
    q = urllib.parse.urlencode({
        "action": "query", "titles": titulo, "redirects": 1, "prop": "revisions|pageprops",
        "rvprop": "content", "rvslots": "main", "rvsection": 0, "ppprop": "wikibase_item",
        "format": "json", "formatversion": 2,
    })
    p = get_json(f"{API}?{q}")["query"]["pages"][0]
    txt = p.get("revisions", [{}])[0].get("slots", {}).get("main", {}).get("content", "")
    return {
        "titulo": p.get("title"),
        "url": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(p.get("title", titulo).replace(" ", "_")),
        "qid": p.get("pageprops", {}).get("wikibase_item"),
        # personagens nascidos na TV usam first_series/first_episode/first_comic em vez de debut
        "estreia": " <br> ".join(v for v in (_campo(txt, c) for c in
                                  ("debut", "first_series", "first_episode", "first_comic")) if v) or None,
        "criadores": _campo(txt, "creators"),
        "alter_ego": _campo(txt, "alter_ego"),
    }
