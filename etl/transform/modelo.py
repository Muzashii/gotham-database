"""Transforma seeds + fontes externas nas tabelas do modelo em estrela (docs/plano.md §6).

Funções puras sobre DataFrames: recebem os dados já extraídos e não fazem rede.
"""
from __future__ import annotations

import re
import unicodedata

import pandas as pd

MIDIAS = [(1, "HQ"), (2, "Animação"), (3, "Série"), (4, "Filme"), (5, "Game")]
ID_MIDIA = {nome: i for i, nome in MIDIAS}
PRIORIDADE_MIDIA = ["Game", "Animação", "Filme", "Série", "HQ"]  # obra com vários tipos: o mais específico vence
STATS = [(1, "INT", "Inteligência"), (2, "FOR", "Força"), (3, "VEL", "Velocidade"),
         (4, "DUR", "Durabilidade"), (5, "POD", "Poder"), (6, "COM", "Combate")]
PESO_RELACAO = {"inimigo": 1, "organização": 1, "aliado": 2, "romance": 2, "família": 3, "mentor": 3}
OFFSET_OBRA_WIKIDATA = 1_000_000_000  # IdObra = número do QID + offset (estável entre execuções)
PALAVRAS_HQ = ("comic", "graphic novel", "one-shot", "storyline", "story arc", "manga", "limited series",
               "crossover", "magazine", "anthology", "album", "annual", "ongoing series")
SIMETRICAS = {"inimigo", "romance", "família", "rival"}  # par canônico (menor id, maior id); aliado/mentor têm direção


def classificar_midia(tipo: str, serie_tipo: str, generos: str = "") -> str | None:
    """Rótulo en do tipo Wikidata (+ tipo da série-mãe e gêneros) -> mídia do projeto, ou None (fora do escopo)."""
    t, s, g = (tipo or "").lower(), (serie_tipo or "").lower(), (generos or "").lower()
    if not t or any(k in t for k in ("esports", "literary", "list", "franchise")):
        return None
    if "video game" in t:
        return "Game"
    if "anim" in t or "anime" in t or "cartoon" in t:
        return "Animação"
    if "episode" in t:
        return "Animação" if ("anim" in s or "cartoon" in s or "scooby" in s or "anim" in g) else "Série"
    if "film" in t:  # muitas animações têm P31 = "film" e o gênero (P136) = animação
        return "Animação" if ("anim" in s or "anim" in g) else "Filme"
    if any(k in t for k in ("television", "tv series", "miniseries", "web series")):
        return "Animação" if "anim" in g else "Série"
    if any(k in t for k in PALAVRAS_HQ):
        return "HQ"
    return None


def granularidade(tipo: str) -> str:
    """Episódio, Série (coleção de episódios/edições) ou Obra (filme, game, edição, graphic novel)."""
    t = (tipo or "").lower()
    if "episode" in t:
        return "Episódio"
    if ("series" in t or "serial" in t) and "film series" not in t:
        return "Série"
    return "Obra"


def normalizar(txt: str) -> str:
    s = unicodedata.normalize("NFKD", txt or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def limpar_texto(txt: str) -> str:
    """Textos vão para HTML/JS com aspas simples no DAX: aspas duplas viram tipográficas."""
    return re.sub(r'"([^"]*)"', r"“\1”", txt or "").replace('"', "”")


def era_do_ano(eras: pd.DataFrame, ano: int) -> int | None:
    m = eras[(eras.AnoInicio <= ano) & (eras.AnoFim >= ano)]
    return int(m.IdEra.iloc[0]) if len(m) else None


# ---------------------------------------------------------------- obras e aparições


def obras_wikidata(linhas: list[dict], eras: pd.DataFrame, qid_para_id: dict[str, int],
                   ano_maximo: int = 2100) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """(dObra, aparições, estatísticas) a partir das linhas cruas do extrator.

    Descarta e conta, nesta ordem: fora do escopo de mídia, sem rótulo, sem data, futuras (> ano_maximo)
    e anteriores à 1ª era. As contagens fecham: brutas = descartadas + no modelo.
    """
    cols = ["obra", "titulo", "personagem", "tipo", "serie_tipo", "serie", "generos", "data"]
    df = pd.DataFrame(linhas, columns=cols).fillna("")
    df["midia"] = [classificar_midia(t, s, g) for t, s, g in zip(df.tipo, df.serie_tipo, df.generos)]
    est = {"obras_brutas": df.obra.nunique()}
    restantes = set(df.obra)

    def descartar(chave: str, manter: pd.Series) -> None:
        nonlocal df, restantes
        ok = set(df.loc[manter, "obra"])
        est[chave] = len(restantes - ok)
        df = df[df.obra.isin(ok) & manter]
        restantes = ok

    descartar("obras_fora_do_escopo", df.midia.notna())
    descartar("obras_sem_rotulo", ~df.titulo.str.fullmatch(r"Q\d+"))
    df = df.assign(ano=pd.to_numeric(df.data.str[:4], errors="coerce"))
    descartar("obras_sem_data", df.ano.notna())
    descartar("obras_futuras", df.ano <= ano_maximo)
    df = df.assign(IdEra=[era_do_ano(eras, int(a)) for a in df.ano])
    descartar("obras_antes_da_1a_era", df.IdEra.notna())

    rank = {m: i for i, m in enumerate(PRIORIDADE_MIDIA)}
    df = df.assign(r=df.midia.map(rank), gran=df.tipo.map(granularidade))
    # episódio ganha o nome da série no título ("Smallville — Pilot")
    df["titulo"] = [f"{s} — {t}" if g == "Episódio" and s and s not in t else t
                    for s, t, g in zip(df.serie, df.titulo, df.gran)]
    # obra com vários P31: mídia mais específica e, dentro dela, granularidade mais fina (Episódio > Série > Obra)
    df = df.assign(rg=df.gran.map({"Episódio": 0, "Série": 1, "Obra": 2}))
    obras = (df.sort_values(["obra", "r", "rg", "ano"])
               .groupby("obra", as_index=False)
               .agg(titulo=("titulo", "first"), midia=("midia", "first"), gran=("gran", "first"), ano=("ano", "min")))
    obras["IdObra"] = obras.obra.str[1:].astype("int64") + OFFSET_OBRA_WIKIDATA
    obras["IdEra"] = [era_do_ano(eras, int(a)) for a in obras.ano]
    d_obra = pd.DataFrame({
        "IdObra": obras.IdObra, "Titulo": obras.titulo.map(limpar_texto), "TipoMidia": obras.midia,
        "IdMidia": obras.midia.map(ID_MIDIA), "Granularidade": obras.gran, "Ano": obras.ano.astype("int64"),
        "IdEra": obras.IdEra.astype("int64"), "Plataforma": "", "UrlCapa": "", "WikidataQid": obras.obra,
    })
    ap = df[df.obra.isin(set(obras.obra))][["obra", "personagem"]].drop_duplicates()
    ap = ap.assign(IdObra=ap.obra.str[1:].astype("int64") + OFFSET_OBRA_WIKIDATA,
                   IdPersonagem=ap.personagem.map(qid_para_id))
    est["obras_no_modelo"] = len(d_obra)
    return d_obra, ap[["IdPersonagem", "IdObra"]].dropna().astype("int64"), est


def obras_e_aparicoes(seed_obras: pd.DataFrame, seed_ap: pd.DataFrame, wd_obras: pd.DataFrame,
                      wd_ap: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Une obras de estreia (seed) e obras do Wikidata, deduplicando por título normalizado."""
    # obras de estreia: edições de HQ (Obra) e episódios de TV (as 2 de Animação)
    seed = seed_obras.assign(IdMidia=seed_obras.TipoMidia.map(ID_MIDIA), WikidataQid="",
                             Granularidade=seed_obras.TipoMidia.map(lambda m: "Episódio" if m == "Animação" else "Obra"))
    seed = seed[["IdObra", "Titulo", "TipoMidia", "IdMidia", "Granularidade", "Ano", "IdEra", "Plataforma", "UrlCapa",
                 "WikidataQid"]]
    # mesma obra = mesma mídia, ano ±1 e título normalizado idêntico ao da obra-seed (ou ao trecho depois de
    # " — ", usado nos episódios: "Batman: The Animated Series — Joker's Favor"). Substring não basta:
    # "Batman" (filme de 1989) não é "Batman #436" (HQ de 1989).
    remapear, duplicadas = {}, []
    for o in wd_obras.itertuples():
        nt = normalizar(o.Titulo)
        for s in seed.itertuples():
            candidatos = {normalizar(s.Titulo), normalizar(s.Titulo.split(" — ")[-1])}
            if nt and nt in candidatos and o.TipoMidia == s.TipoMidia and abs(int(s.Ano) - int(o.Ano)) <= 1:
                remapear[o.IdObra] = s.IdObra
                duplicadas.append(f"{o.WikidataQid} “{o.Titulo}” = obra-seed {s.IdObra} “{s.Titulo}”")
                seed.loc[seed.IdObra == s.IdObra, "WikidataQid"] = o.WikidataQid
                break
    wd = wd_obras[~wd_obras.IdObra.isin(remapear)]
    d_obra = pd.concat([seed, wd], ignore_index=True).sort_values("IdObra", ignore_index=True)

    estreias = seed_ap.assign(EhEstreia=1)[["IdPersonagem", "IdObra", "IdVersao", "EhEstreia", "Relevancia"]]
    outras = wd_ap.assign(IdObra=wd_ap.IdObra.replace(remapear))
    outras = outras.assign(IdVersao=outras.IdPersonagem * 100 + 1, EhEstreia=0, Relevancia=1)
    f_ap = (pd.concat([estreias, outras], ignore_index=True)
              .sort_values(["IdPersonagem", "IdObra", "EhEstreia"], ascending=[True, True, False])
              .drop_duplicates(["IdPersonagem", "IdObra"], keep="first")
              .reset_index(drop=True))
    return d_obra, f_ap, duplicadas


# ---------------------------------------------------------------- relações


def relacoes(wd_rel: list[dict], qid_para_id: dict[str, int], afiliacao: pd.DataFrame) -> pd.DataFrame:
    """fRelacao: arestas do Wikidata + arestas de organização (Líder -> membro da mesma afiliação)."""
    linhas = [{"IdOrigem": qid_para_id[r["origem"]], "IdDestino": qid_para_id[r["destino"]],
               "TipoRelacao": r["tipo"], "Fonte": f"Wikidata {r['propriedade']}"}
              for r in wd_rel if r["origem"] in qid_para_id and r["destino"] in qid_para_id and r["origem"] != r["destino"]]
    for af, grupo in afiliacao.groupby("IdAfiliacao"):
        lideres = grupo.loc[grupo.Papel == "Líder", "IdPersonagem"]
        membros = grupo.loc[grupo.Papel.isin(["Membro", "Ex-membro"]), "IdPersonagem"]
        for l in lideres:
            for m in membros:
                if l != m:
                    linhas.append({"IdOrigem": int(l), "IdDestino": int(m), "TipoRelacao": "organização",
                                   "Fonte": f"seed personagem_afiliacao (afiliação {af})"})
    df = pd.DataFrame(linhas, columns=["IdOrigem", "IdDestino", "TipoRelacao", "Fonte"])
    # relações simétricas (Batman inimigo de Coringa = Coringa inimigo de Batman) viram um par canônico;
    # sem isso o par conta em dobro quando o Wikidata registra a relação nos dois itens
    sim = df.TipoRelacao.isin(SIMETRICAS)
    a, b = df.IdOrigem.copy(), df.IdDestino.copy()
    df.loc[sim, "IdOrigem"] = a[sim].where(a[sim] < b[sim], b[sim])
    df.loc[sim, "IdDestino"] = b[sim].where(a[sim] < b[sim], a[sim])
    df = df.drop_duplicates(["IdOrigem", "IdDestino", "TipoRelacao"]).sort_values(
        ["IdOrigem", "IdDestino", "TipoRelacao"], ignore_index=True)
    df["Peso"] = df.TipoRelacao.map(PESO_RELACAO).astype("int64")
    return df[["IdOrigem", "IdDestino", "TipoRelacao", "Peso", "Fonte"]]


# ---------------------------------------------------------------- dimensões auxiliares


def d_midia() -> pd.DataFrame:
    return pd.DataFrame(MIDIAS, columns=["IdMidia", "Nome"])


def d_stat() -> pd.DataFrame:
    return pd.DataFrame(STATS, columns=["Ordem", "Codigo", "Rotulo"])
