"""Coleta fatos brutos (Wikipédia + Wikidata + SuperHero API) para a lista de curadoria.

Entrada: data/seeds/personagens.csv (colunas IdPersonagem, WikipediaTitulo, IdSuperHeroApi).
Saída:   data/raw/curadoria.json — material bruto para o curador revisar (não vai para o modelo).
"""
from __future__ import annotations

import csv
import json
import sys

from etl.extract import superhero, wikidata, wikipedia
from etl.extract.http import RAIZ


def main() -> int:
    lista = list(csv.DictReader(open(RAIZ / "data/seeds/personagens.csv", encoding="utf-8")))
    sh = superhero.por_id()
    saida = []
    for linha in lista:
        info = wikipedia.infobox(linha["WikipediaTitulo"])
        print(f"  {linha['IdPersonagem']:>3} {info['titulo']} ({info['qid']})", flush=True)
        h = sh.get(int(linha["IdSuperHeroApi"])) if linha["IdSuperHeroApi"] else None
        saida.append({
            **linha, "wikipedia": info,
            "superhero": h and {"nome": h["name"], "nome_completo": h["biography"]["fullName"],
                                "estreia": h["biography"]["firstAppearance"], "stats": h["powerstats"],
                                "alinhamento": h["biography"]["alignment"], "img": h["images"]["md"]},
        })
    wd = wikidata.fatos([s["wikipedia"]["qid"] for s in saida if s["wikipedia"]["qid"]])
    for s in saida:
        s["wikidata"] = wd.get(s["wikipedia"]["qid"] or "", {})
    destino = RAIZ / "data/raw/curadoria.json"
    destino.write_text(json.dumps(saida, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"OK: {len(saida)} personagens -> {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
