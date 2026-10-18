"""Checagem cruzada da estreia: personagens.csv × fontes brutas (Wikipédia, SuperHero API, Wikidata).

Compara título-base + número da edição. Gera handoffs/F1-checagem-fatos.md.
Requer data/raw/curadoria.json (rode antes: python -m etl.curadoria.coletar).
"""
from __future__ import annotations

import csv
import json
import re
import sys

from etl.extract.http import RAIZ

SERIES = ["detective comics", "batman", "action comics", "world's finest", "all-american", "new teen titans",
          "huntress", "hawkman", "demon", "52", "suicide squad", "legends of the dark knight", "vengeance of bane",
          "son of the demon", "shadow of the bat", "sword of azrael", "richard dragon", "dark days", "joker's favor",
          "batman beyond", "rebirth"]


def chave(txt: str) -> tuple[str | None, str | None, str | None, int | None]:
    """(série, volume, número, ano) extraídos de um texto de estreia."""
    t = (txt or "").lower().replace("’", "'")
    serie = next((s for s in sorted(SERIES, key=len, reverse=True) if s in t), None)
    num = re.search(r"#\s*(\d+)", t)
    vol = re.search(r"vol(?:ume)?\.?\s*(\d+)", t)
    ano = re.search(r"\b(19[3-9]\d|20[0-4]\d)\b", t)
    return serie, (vol.group(1) if vol else None), (num.group(1) if num else None), (int(ano.group(1)) if ano else None)


def concorda(a: str, b: str) -> bool:
    """Mesma série e: mesmo número (e volume, se ambos têm) — ou, sem número de um lado, mesmo ano (±1).

    Ano de capa e de venda podem diferir em 1, por isso a tolerância. Limitação conhecida: com a mesma
    edição, um erro de exatamente 1 ano (como o do Signal na F1) não é detectado — isso é coberto pela
    amostragem manual da revisão.
    """
    (sa, va, na, aa), (sb, vb, nb, ab) = chave(a), chave(b)
    if sa is None or sa != sb:
        return False
    if va and vb and va != vb:
        return False
    if aa and ab and abs(aa - ab) > 1:
        return False
    if na and nb:
        return na == nb
    if not na and not nb:  # edição única sem número (ex.: graphic novel), sem conflito de ano
        return True
    return bool(aa and ab)


def trechos(txt: str) -> list[str]:
    """Fontes listam várias identidades num texto só: compara trecho a trecho."""
    return [t for t in re.split(r"<br\s*/?>|\||;|(?<!vol)\.\s|\(as ", txt or "") if t.strip()]


def main() -> int:
    raw = {x["IdPersonagem"]: x for x in json.load(open(RAIZ / "data/raw/curadoria.json", encoding="utf-8"))}
    linhas, n2 = [], 0
    for p in csv.DictReader(open(RAIZ / "data/seeds/personagens.csv", encoding="utf-8")):
        r = raw[p["IdPersonagem"]]
        alvo = p["PrimeiraAparicao"]
        wp = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", r["wikipedia"]["estreia"] or "")
        res = {"Wikipédia": any(concorda(alvo, t) for t in trechos(wp))}
        if r["superhero"]:
            res["SuperHero API"] = any(concorda(alvo, t) for t in trechos(r["superhero"]["estreia"]))
        if r["wikidata"].get("estreia"):
            res["Wikidata"] = any(concorda(alvo, e) for e in r["wikidata"]["estreia"])
        ok = sum(res.values())
        n2 += ok >= 2
        linhas.append(f"| {p['IdPersonagem']} | {p['Nome']} | {alvo} | "
                      + ", ".join(f"{k} {'✔' if v else '✖'}" for k, v in res.items())
                      + f" | {ok} | {p['confianca']} |")
    md = ["# F1 — Checagem cruzada de estreias (gerado por `etl/curadoria/checar.py`)", "",
          f"**{n2} de {len(linhas)}** estreias confirmadas por 2+ fontes independentes "
          "(gate F1: amostra de 20 fatos checada em 2 fontes).", "",
          "Critério: mesma série, volume e número de edição, ano compatível (±1, capa × venda); sem número, exige ano em ambos.",
          "Limitação: erro de exatamente 1 ano na mesma edição não é detectado (coberto pela amostragem manual).",
          "Na Wikipédia, a comparação é feita contra o infobox inteiro (que lista várias identidades).", "",
          "| Id | Personagem | Estreia no seed | Fontes | Concordâncias | confianca |", "|---|---|---|---|---|---|", *linhas, ""]
    (RAIZ / "handoffs/F1-checagem-fatos.md").write_text("\n".join(md), encoding="utf-8")
    print(f"{n2}/{len(linhas)} estreias com 2+ fontes concordantes -> handoffs/F1-checagem-fatos.md")
    return 0 if n2 >= 20 else 1


if __name__ == "__main__":
    sys.exit(main())
