"""Pipeline completo: seeds + Wikidata (+ Comic Vine, se houver chave) -> data/curated/*.csv.

    python -m etl.run_etl            # usa o cache em data/raw/cache quando existir
    python -m etl.run_etl --offline  # falha se precisar de rede (reprodutibilidade)

Saída determinística (ordenada pela chave) para diffs limpos. Gera também
data/curated/_qualidade.json e handoffs/F2-relatorio-qualidade.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from etl.extract import comicvine, http, wikidata
from etl.graph.centralidade import centralidade
from etl.quality.schemas import SCHEMAS, validar
from etl.transform import modelo

RAIZ = http.RAIZ
SEEDS = RAIZ / "data" / "seeds"
CURADO = RAIZ / "data" / "curated"

PK = {
    "dPersonagem": ["IdPersonagem"], "dVersao": ["IdVersao"], "dEra": ["IdEra"], "dMidia": ["IdMidia"],
    "dAfiliacao": ["IdAfiliacao"], "bPersonagemAfiliacao": ["IdPersonagem", "IdAfiliacao"], "dObra": ["IdObra"],
    "fAparicao": ["IdPersonagem", "IdObra"], "fRelacao": ["IdOrigem", "IdDestino", "TipoRelacao"],
    "dArquetipo": ["IdArquetipo"], "fMatchup": ["IdAtaque", "IdDefesa"], "dGolpe": ["IdGolpe"],
    "bVersaoGolpe": ["IdVersao", "IdGolpe"], "dGadget": ["IdGadget"], "dBairro": ["IdBairro"],
    "fEncontro": ["IdBairro", "IdPersonagem"], "dCentralidade": ["IdPersonagem"], "dStat": ["Ordem"],
}


def seed(nome: str) -> pd.DataFrame:
    return pd.read_csv(SEEDS / nome, dtype=str, keep_default_na=False)


def ints(df: pd.DataFrame, *cols: str) -> pd.DataFrame:
    return df.astype({c: "int64" for c in cols})


def sem(df: pd.DataFrame, *cols: str) -> pd.DataFrame:
    return df.drop(columns=[c for c in cols if c in df.columns])


def construir(offline: bool = False) -> tuple[dict[str, pd.DataFrame], dict]:
    if offline:
        http.SOMENTE_CACHE = True
    pers = ints(seed("personagens.csv"), "IdPersonagem", "IdArquetipo", "AnoEstreia", "IdEra")
    eras = ints(seed("eras.csv"), "IdEra", "AnoInicio", "AnoFim", "Ordem")
    qid_para_id = dict(zip(pers.WikidataQid, pers.IdPersonagem))
    rel_qualidade: dict = {"gerado_em": date.today().isoformat(), "fontes": {}}

    # --- Comic Vine (opcional)
    pers["ComicVineId"] = pd.array([None] * len(pers), dtype="Int64")
    pers["EdicoesComicVine"] = pd.array([None] * len(pers), dtype="Int64")
    chave = comicvine.chave()
    if chave:
        casados = 0
        for i, p in pers.iterrows():
            r = comicvine.buscar(p.WikipediaTitulo, p.IdentidadeCivil, chave)
            if r:
                casados += 1
                pers.at[i, "ComicVineId"], pers.at[i, "EdicoesComicVine"] = r["id"], r["edicoes"]
        rel_qualidade["fontes"]["Comic Vine"] = {"casados": casados, "total": len(pers)}
    else:
        rel_qualidade["fontes"]["Comic Vine"] = {"status": "não coletado (sem COMICVINE_API_KEY)"}

    # --- cobertura das fontes (chave canônica = IdPersonagem do seed). QID e id da SuperHero API foram
    # casados na curadoria (F1) e aqui só se mede o preenchimento; obras e relações medem dados efetivamente obtidos.
    rel_qualidade["fontes"]["Wikidata — QID preenchido no seed"] = {"casados": int((pers.WikidataQid != "").sum()), "total": len(pers)}
    rel_qualidade["fontes"]["SuperHero API — id preenchido no seed"] = {"casados": int((pers.IdSuperHeroApi != "").sum()), "total": len(pers)}

    # --- obras e aparições
    wd_obras, wd_ap, est_obras = modelo.obras_wikidata(wikidata.obras(list(qid_para_id)), eras, qid_para_id,
                                                       ano_maximo=date.today().year)
    obras_seed = ints(sem(seed("obras.csv"), "fonte"), "IdObra", "Ano", "IdEra")
    ap_seed = ints(sem(seed("aparicoes.csv"), "fonte"), "IdPersonagem", "IdObra", "IdVersao", "EhEstreia", "Relevancia")
    d_obra, f_ap, duplicadas = modelo.obras_e_aparicoes(obras_seed, ap_seed, wd_obras, wd_ap)
    rel_qualidade["obras"] = {**est_obras, "duplicadas_com_seed": duplicadas, "total_no_modelo": len(d_obra)}
    rel_qualidade["granularidade"] = d_obra.Granularidade.value_counts().sort_index().to_dict()
    com_obra_wd = set(wd_ap.IdPersonagem)
    rel_qualidade["fontes"]["Wikidata — personagens com obras (P674)"] = {"casados": len(com_obra_wd), "total": len(pers)}

    # --- relações e centralidade
    afil = ints(sem(seed("personagem_afiliacao.csv"), "fonte"), "IdPersonagem", "IdAfiliacao")
    wd_rel = wikidata.relacoes(list(qid_para_id))
    f_rel = modelo.relacoes(wd_rel, qid_para_id, afil)
    d_cent = centralidade(pers.IdPersonagem, f_rel)
    rel_qualidade["relacoes"] = f_rel.TipoRelacao.value_counts().sort_index().to_dict()
    so_wd = f_rel[f_rel.Fonte.str.startswith("Wikidata")]  # arestas de organização vêm do seed, não contam
    com_rel = set(so_wd.IdOrigem) | set(so_wd.IdDestino)
    rel_qualidade["fontes"]["Wikidata — personagens com relações"] = {"casados": len(com_rel), "total": len(pers)}
    rel_qualidade["isolados"] = pers.loc[pers.IdPersonagem.isin(d_cent.loc[d_cent.Grau == 0, "IdPersonagem"]), "Nome"].tolist()

    vers = ints(sem(seed("versoes.csv"), "fonte"), "IdVersao", "IdPersonagem", "IdMidia", "Int", "For", "Vel", "Dur",
                "Pod", "Com", "IdArquetipo", "EhTransformacao")
    gad = sem(seed("gadgets.csv"), "fonte")
    gad = gad.assign(IdGadget=gad.IdGadget.astype("int64"), MultCaptura=gad.MultCaptura.astype("float64"),
                     SoContraArquetipo=pd.to_numeric(gad.SoContraArquetipo.replace("", None)).astype("Int64"))
    bai = sem(seed("bairros.csv"), "fonte")
    bai = bai.assign(IdBairro=bai.IdBairro.astype("int64"), BonusCaptura=bai.BonusCaptura.astype("float64"),
                     TemRecarga=bai.TemRecarga.astype("int64"))
    mt = sem(seed("matchup.csv"), "fonte")
    mt = ints(mt, "IdAtaque", "IdDefesa").assign(Multiplicador=mt.Multiplicador.astype("float64"))

    d_pers = sem(pers, "fonte", "nota", "WikipediaTitulo")
    d_pers = d_pers.assign(IdSuperHeroApi=pd.to_numeric(d_pers.IdSuperHeroApi.replace("", None)).astype("Int64"))

    tabelas = {
        "dPersonagem": d_pers,
        "dVersao": vers,
        "dEra": sem(eras, "fonte", "nota"),
        "dMidia": modelo.d_midia(),
        "dAfiliacao": ints(sem(seed("afiliacoes.csv"), "fonte", "nota"), "IdAfiliacao"),
        "bPersonagemAfiliacao": afil,
        "dObra": d_obra,
        "fAparicao": f_ap,
        "fRelacao": f_rel,
        "dArquetipo": ints(sem(seed("arquetipos.csv"), "fonte"), "IdArquetipo"),
        "fMatchup": mt,
        "dGolpe": ints(sem(seed("golpes.csv"), "fonte"), "IdGolpe", "IdArquetipo", "Poder", "Precisao"),
        "bVersaoGolpe": ints(sem(seed("versao_golpe.csv"), "fonte"), "IdVersao", "IdGolpe"),
        "dGadget": gad,
        "dBairro": bai,
        "fEncontro": ints(sem(seed("encontros.csv"), "fonte"), "IdBairro", "IdPersonagem", "Peso"),
        "dCentralidade": d_cent,
        "dStat": modelo.d_stat(),
    }
    tabelas = {n: df.sort_values(PK[n], ignore_index=True) for n, df in tabelas.items()}
    rel_qualidade["orfas"] = validar(tabelas)
    rel_qualidade["linhas"] = {n: len(df) for n, df in tabelas.items()}
    top = d_cent.merge(pers[["IdPersonagem", "Nome"]]).sort_values("Intermediacao", ascending=False).head(5)
    rel_qualidade["hubs"] = [f"{r.Nome} ({r.Intermediacao:.3f})" for r in top.itertuples()]
    ap_por_midia = f_ap.merge(d_obra[["IdObra", "TipoMidia"]]).TipoMidia.value_counts().sort_index()
    rel_qualidade["aparicoes_por_midia"] = ap_por_midia.to_dict()
    return tabelas, rel_qualidade


def gravar(tabelas: dict[str, pd.DataFrame], qualidade: dict) -> None:
    CURADO.mkdir(parents=True, exist_ok=True)
    for nome, df in tabelas.items():
        df.to_csv(CURADO / f"{nome}.csv", index=False, encoding="utf-8", lineterminator="\n")
    (CURADO / "_qualidade.json").write_text(json.dumps(qualidade, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
                                            encoding="utf-8")
    md = ["# F2 — Relatório de qualidade do ETL (gerado por `etl/run_etl.py`)", "",
          f"Gerado em {qualidade['gerado_em']}. Todas as tabelas passaram nos schemas pandera; "
          f"**{sum(qualidade['orfas'].values())} chaves órfãs** em {len(qualidade['orfas'])} relações verificadas.", "",
          "## Contagem por tabela", "", "| Tabela | Linhas |", "|---|---|",
          *[f"| `{n}` | {q} |" for n, q in qualidade["linhas"].items()], "",
          "## Casamento entre fontes (chave canônica = `IdPersonagem` do seed)", "", "| Fonte | Casados |", "|---|---|"]
    for f, v in qualidade["fontes"].items():
        md.append(f"| {f} | {v['casados']}/{v['total']} ({v['casados'] / v['total']:.0%}) |" if "casados" in v
                  else f"| {f} | {v['status']} |")
    o = qualidade["obras"]
    md += ["", "## Obras (Wikidata P674)", "",
           f"- Obras brutas: {o['obras_brutas']} → descartadas: fora do escopo de mídia {o['obras_fora_do_escopo']}, "
           f"sem rótulo {o['obras_sem_rotulo']}, sem data {o['obras_sem_data']}, futuras {o['obras_futuras']}, "
           f"anteriores à 1ª era {o['obras_antes_da_1a_era']} → no modelo {o['obras_no_modelo']}",
           f"- Total em `dObra` (com as {o['total_no_modelo'] - o['obras_no_modelo'] + len(o['duplicadas_com_seed'])} obras de estreia, "
           f"menos as unificadas): {o['total_no_modelo']}",
           "- Granularidade: " + ", ".join(f"{k} {v}" for k, v in qualidade["granularidade"].items()),
           f"- Duplicadas com obras-seed (unificadas): {len(o['duplicadas_com_seed'])}",
           *[f"  - {d}" for d in o["duplicadas_com_seed"]],
           f"- Aparições por mídia: " + ", ".join(f"{k} {v}" for k, v in qualidade["aparicoes_por_midia"].items()),
           "", "## Rede de relações", "",
           "- Arestas por tipo: " + ", ".join(f"{k} {v}" for k, v in qualidade["relacoes"].items()),
           "- Maiores intermediações (hubs): " + "; ".join(qualidade["hubs"]),
           "- Sem nenhuma relação: " + (", ".join(qualidade["isolados"]) or "nenhum"), ""]
    (RAIZ / "handoffs" / "F2-relatorio-qualidade.md").write_text("\n".join(md), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--offline", action="store_true", help="só usa o cache local; falha se faltar algo")
    args = ap.parse_args()
    tabelas, qualidade = construir(offline=args.offline)
    gravar(tabelas, qualidade)
    print(f"OK: {len(tabelas)} tabelas em {CURADO.relative_to(RAIZ)} · órfãs: {sum(qualidade['orfas'].values())}")
    for n, q in qualidade["linhas"].items():
        print(f"  {n:<22} {q:>6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
