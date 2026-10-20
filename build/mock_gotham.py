"""Gera o mesmo objeto window.GOTHAM que a medida [JS Gotham] produz, a partir de data/curated.

Usos: valores mock do preview (src/html/batcomputador.mock.json) e fixture dos testes JS
(tests/js/fixtures/gotham.js). Se a medida DAX mudar de formato, mude aqui também — o teste
tests/js/batcomputador.test.js confere o objeto contra contracts/js-data-schema.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
C = RAIZ / "data" / "curated"


def esc(t) -> str:
    """Mesmo escape da medida DAX (string JS entre aspas simples): \\, ', </, LF e CR."""
    if t is None or (isinstance(t, float) and pd.isna(t)):
        return ""
    return (str(t).replace("\\", "\\\\").replace("'", "\\'").replace("</", "<\\/")
            .replace("\n", "\\n").replace("\r", "\\r"))


def versao_padrao(v: pd.DataFrame, pid: int) -> int:
    """Mesma regra da medida: menor IdVersao não-transformação; senão a menor do personagem; senão 0."""
    dele = v[v.IdPersonagem == pid]
    base = dele[dele.EhTransformacao == 0]
    return int((base if len(base) else dele).IdVersao.min()) if len(dele) else 0


def num(x) -> str:
    x = float(x)
    return str(int(x)) if x.is_integer() else f"{x:.3f}".rstrip("0").rstrip(".")


def gerar() -> str:
    ler = lambda n: pd.read_csv(C / f"{n}.csv", keep_default_na=False)  # noqa: E731
    ar, mt, er, af, md = ler("dArquetipo"), ler("fMatchup"), ler("dEra"), ler("dAfiliacao"), ler("dMidia")
    v, p, rel, g, vg = ler("dVersao"), ler("dPersonagem"), ler("fRelacao"), ler("dGolpe"), ler("bVersaoGolpe")
    b, ap, ob, cen = ler("bPersonagemAfiliacao"), ler("fAparicao"), ler("dObra"), ler("dCentralidade")

    s_ar = ",".join(f"{{id:{r.IdArquetipo},s:'{esc(r.Sigla)}',n:'{esc(r.Nome)}',c:'{esc(r.Cor)}'}}" for r in ar.sort_values("IdArquetipo").itertuples())
    s_m = ",".join("[" + ",".join(num(x) for x in mt[mt.IdAtaque == a].sort_values("IdDefesa").Multiplicador) + "]"
                   for a in sorted(ar.IdArquetipo))
    s_er = ",".join(f"{{id:{r.IdEra},n:'{esc(r.Nome)}',i:{r.AnoInicio}}}" for r in er.sort_values("Ordem").itertuples())
    s_af = ",".join(f"{{id:{r.IdAfiliacao},n:'{esc(r.Nome)}'}}" for r in af.sort_values("IdAfiliacao").itertuples())
    s_md = ",".join(f"'{esc(n)}'" for n in md.sort_values("IdMidia").Nome)
    s_v = ",".join(
        f"{{id:{r.IdVersao},p:{r.IdPersonagem},n:'{esc(r.NomeVersao)}',a:{r.IdArquetipo},"
        f"s:[{r.Int},{r.For},{r.Vel},{r.Dur},{r.Pod},{r.Com}],img:'{esc(r.UrlImagem)}',t:{r.EhTransformacao},r:'{esc(r.Raridade)}'}}"
        for r in v.sort_values("IdVersao").itertuples())
    apm = ap.merge(ob[["IdObra", "IdMidia"]])
    ids_md = sorted(md.IdMidia)
    pessoas = []
    for r in p.sort_values("IdPersonagem").itertuples():
        afs = ",".join(str(x) for x in sorted(b[b.IdPersonagem == r.IdPersonagem].IdAfiliacao))
        aps = ",".join(str(int((apm[apm.IdPersonagem == r.IdPersonagem].IdMidia == m).sum())) for m in ids_md)
        c = cen[cen.IdPersonagem == r.IdPersonagem].iloc[0]
        pessoas.append(
            f"{{id:{r.IdPersonagem},n:'{esc(r.Nome)}',c:'{esc(r.Codinome)}',ci:'{esc(r.IdentidadeCivil)}',al:'{esc(r.Alinhamento)}',"
            f"a:{r.IdArquetipo},f:'{esc(r.Faccao)}',e:'{esc(r.PrimeiraAparicao)}',ano:{r.AnoEstreia},er:{r.IdEra},me:'{esc(r.MidiaEstreia)}',"
            f"cr:'{esc(r.Criadores)}',j:'{esc(r.JustificativaArquetipo)}',v:{versao_padrao(v, r.IdPersonagem)},af:[{afs}],ap:[{aps}],"
            f"gr:{c.Grau},in:{num(c.Intermediacao)}}}")
    s_rel = ",".join(f"[{r.IdOrigem},{r.IdDestino},'{esc(r.TipoRelacao)}',{r.Peso}]"
                     for r in rel.sort_values(["IdOrigem", "IdDestino"]).itertuples())
    s_g = ",".join(f"{{id:{r.IdGolpe},n:'{esc(r.Nome)}',a:{r.IdArquetipo},c:'{'F' if r.Categoria == 'Físico' else 'T'}',"
                   f"pw:{r.Poder},ac:{r.Precisao},ef:'{esc(r.Efeito)}'}}" for r in g.sort_values("IdGolpe").itertuples())
    s_vg = ",".join(f"[{r.IdVersao},{r.IdGolpe}]" for r in vg.sort_values(["IdVersao", "IdGolpe"]).itertuples())
    return (f"window.GOTHAM={{ar:[{s_ar}],m:[{s_m}],er:[{s_er}],af:[{s_af}],md:[{s_md}],v:[{s_v}],"
            f"p:[{','.join(pessoas)}],rel:[{s_rel}],g:[{s_g}],vg:[{s_vg}]}};")


def main() -> int:
    js = gerar()
    (RAIZ / "src" / "html" / "batcomputador.mock.json").write_text(
        json.dumps({"[JS Gotham]": js}, ensure_ascii=False), encoding="utf-8")
    fx = RAIZ / "tests" / "js" / "fixtures"
    fx.mkdir(parents=True, exist_ok=True)
    (fx / "gotham.js").write_text("// Gerado por build/mock_gotham.py — não editar.\n" + js + "\n", encoding="utf-8", newline="\n")
    print(f"OK: window.GOTHAM mock com {len(js):,} caracteres")
    return 0


if __name__ == "__main__":
    sys.exit(main())
