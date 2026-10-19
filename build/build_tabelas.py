"""Gera o modelo em estrela no TMDL a partir do contrato das tabelas curadas.

Escreve (todos gerados — não editar à mão):
  definition/expressions.tmdl            função M LerCsv (Web.Contents com RelativePath: atualizável no serviço)
  definition/tables/<curada>.tmdl        uma por tabela de data/curated
  definition/tables/<desconectada>.tmdl  Modo, TemaSel, VersaoSel, RelacaoSel, ObraSel
  definition/relationships.tmdl          relações 1:N unidirecionais (ativas/inativas por modelo_spec.py)
  definition/model.tmdl                  refs de tabelas (preserva as propriedades do modelo)
  contracts/data-dictionary.md           seção entre <!-- modelo:inicio --> e <!-- modelo:fim -->
"""
from __future__ import annotations

import re
import sys
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import modelo_spec as spec  # noqa: E402
from etl.quality.schemas import SCHEMAS  # noqa: E402

DEF = RAIZ / "powerbi" / "GothamDatabase.SemanticModel" / "definition"
TIPO_TMDL = {"int64": "int64", "Int64": "int64", "float64": "double", "str": "string"}
TIPO_M = {"int64": "Int64.Type", "Int64": "Int64.Type", "float64": "type number", "str": "type text"}
# Arquivos gerados — NÃO EDITAR À MÃO. Sem cabeçalho no TMDL: linhas /// viram descrição no Desktop.


def tipo_base(col) -> str:
    """dtype pandera -> chave de TIPO_TMDL/TIPO_M ('string[python]' e 'str' viram 'str')."""
    s = str(col.dtype)
    return "str" if s.startswith("str") else s


def tag(*partes: str) -> str:
    """lineageTag determinístico (o Desktop aceita qualquer GUID estável)."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "gotham-database:" + ":".join(partes)))


def nome(n: str) -> str:
    return n if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", n) else "'" + n.replace("'", "''") + "'"


def oculta(tabela: str, col: str) -> bool:
    return bool(re.match(r"Id[A-Z]", col)) or col in spec.OCULTAS_EXTRA or col == "SoContraArquetipo"


def bloco_m(linhas: list[str]) -> list[str]:
    return ["\t\tsource ="] + ["\t\t\t\t" + l for l in linhas]


def tabela_curada(t: str) -> str:
    schema = SCHEMAS[t]
    out = [f"/// {spec.DESCRICAO[t]}", f"table {t}", f"\tlineageTag: {tag(t)}", ""]
    for c, col in schema.columns.items():
        tipo = tipo_base(col)
        out += [f"\tcolumn {nome(c)}", f"\t\tdataType: {TIPO_TMDL[tipo]}"]
        if oculta(t, c):
            out.append("\t\tisHidden")
        if c in spec.FORMATO:
            out.append(f"\t\tformatString: {spec.FORMATO[c]}")
        elif TIPO_TMDL[tipo] == "int64":
            out.append("\t\tformatString: 0")
        out.append(f"\t\tlineageTag: {tag(t, c)}")
        out.append(f"\t\tsummarizeBy: {'sum' if c in spec.SOMAR else 'none'}")
        out.append(f"\t\tsourceColumn: {c}")
        if c in spec.CATEGORIA:
            out.append(f"\t\tdataCategory: {spec.CATEGORIA[c]}")
        if (t, c) in spec.ORDENAR_POR:
            out.append(f"\t\tsortByColumn: {spec.ORDENAR_POR[(t, c)]}")
        out += ["", "\t\tannotation SummarizationSetBy = Automatic", ""]
    tipos = ", ".join(f'{{"{c}", {TIPO_M[tipo_base(col)]}}}' for c, col in schema.columns.items())
    out += [f"\tpartition {t} = m", "\t\tmode: import"]
    out += bloco_m(["let", f'    Fonte = LerCsv("{t}"),',
                    f'    Tipos = Table.TransformColumnTypes(Fonte, {{{tipos}}}, "en-US")', "in", "    Tipos"])
    out += ["", "\tannotation PBI_ResultType = Table", ""]
    return "\n".join(out)


def tabela_desconectada(t: str, d: dict) -> str:
    out = [f"/// Desconectada. {d['descricao']}", f"table {t}", f"\tlineageTag: {tag(t)}", ""]
    for c, tipo in d["colunas"]:
        out += [f"\tcolumn {nome(c)}", f"\t\tdataType: {tipo}"]
        if tipo == "int64":
            out += ["\t\tisHidden", "\t\tformatString: 0"]
        out += [f"\t\tlineageTag: {tag(t, c)}", "\t\tsummarizeBy: none", f"\t\tsourceColumn: {c}"]
        if c in d["ordenar"]:
            out.append(f"\t\tsortByColumn: {d['ordenar'][c]}")
        out += ["", "\t\tannotation SummarizationSetBy = Automatic", ""]
    out += [f"\tpartition {t} = m", "\t\tmode: import"]
    out += bloco_m(["let", f"    Fonte = {d['m']}", "in", "    Fonte"])
    out += ["", "\tannotation PBI_ResultType = Table", ""]
    return "\n".join(out)


def expressions() -> str:
    return "\n".join([
        "/// Lê um CSV de data/curated do repositório público. Web.Contents com URL base fixa + RelativePath",
        "/// é o padrão que o serviço do Power BI consegue atualizar (fonte não dinâmica).",
        "expression LerCsv =",
        "\t\t(nome as text) as table =>",
        "\t\tlet",
        f'\t\t    Bruto = Web.Contents("{spec.URL_BASE}", [RelativePath = "{spec.CAMINHO_CURADO}" & nome & ".csv"]),',
        "\t\t    Csv = Csv.Document(Bruto, [Delimiter = \",\", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),",
        "\t\t    Cabecalho = Table.PromoteHeaders(Csv, [PromoteAllScalars = true]),",
        "\t\t    // célula vazia no CSV = ausente (null), não texto vazio: ISBLANK() funciona no DAX",
        "\t\t    Nulos = Table.ReplaceValue(Cabecalho, \"\", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalho))",
        "\t\tin",
        "\t\t    Nulos",
        f"\tlineageTag: {tag('LerCsv')}",
        "",
        "\tannotation PBI_ResultType = Function",
        "",
    ])


def relationships() -> str:
    # Relações não aceitam descrição (///) no TMDL: os motivos das inativas ficam no dicionário de dados
    out = []
    for de, para, ativa, _motivo in spec.RELACOES:
        out.append(f"relationship {tag('rel', de, para)}")
        if not ativa:
            out.append("\tisActive: false")
        out += [f"\tfromColumn: {de}", f"\ttoColumn: {para}", ""]
    return "\n".join(out)


def model_tmdl(tabelas: list[str]) -> str:
    atual = (DEF / "model.tmdl").read_text(encoding="utf-8")
    corpo = re.sub(r"\n*(ref table .*\n?)+", "\n", atual)
    corpo = re.sub(r"annotation PBI_QueryOrder = .*", "annotation PBI_QueryOrder = " +
                   "[" + ",".join(f'"{t}"' for t in tabelas) + "]", corpo)
    return corpo.rstrip("\n") + "\n\n" + "\n".join(f"ref table {nome(t)}" for t in tabelas) + "\n"


def dicionario() -> str:
    linhas = ["<!-- modelo:inicio -->", "## Modelo semântico (F3) — gerado por `build/build_tabelas.py`", "",
              "Fonte de cada tabela: `LerCsv(\"<tabela>\")` → `data/curated/<tabela>.csv` no GitHub (UTF-8, en-US).",
              "Colunas `Id*` e técnicas ficam ocultas; tudo com `summarizeBy: none` exceto `EdicoesComicVine`.", "",
              "### Tabelas", "", "| Tabela | Colunas (tipo; *oculta*) | Descrição |", "|---|---|---|"]
    for t, schema in SCHEMAS.items():
        cols = ", ".join((f"*{c}*" if oculta(t, c) else c) + f" ({TIPO_TMDL[tipo_base(col)]})"
                         for c, col in schema.columns.items())
        linhas.append(f"| `{t}` | {cols} | {spec.DESCRICAO[t]} |")
    for t, d in spec.DESCONECTADAS.items():
        linhas.append(f"| `{t}` | " + ", ".join(f"{c} ({tp})" for c, tp in d["colunas"]) + f" | Desconectada. {d['descricao']} |")
    linhas += ["", "### Relações (todas N:1, filtro único da dimensão para o fato)", "",
               "| De (N) | Para (1) | Ativa | Motivo |", "|---|---|---|---|"]
    linhas += [f"| `{de}` | `{para}` | {'sim' if a else '**não**'} | {m} |" for de, para, a, m in spec.RELACOES]
    linhas += ["", "<!-- modelo:fim -->"]
    return "\n".join(linhas)


def gerar() -> dict[Path, str]:
    arquivos = {DEF / "expressions.tmdl": expressions(), DEF / "relationships.tmdl": relationships()}
    for t in SCHEMAS:
        arquivos[DEF / "tables" / f"{t}.tmdl"] = tabela_curada(t)
    for t, d in spec.DESCONECTADAS.items():
        arquivos[DEF / "tables" / f"{t}.tmdl"] = tabela_desconectada(t, d)
    arquivos[DEF / "model.tmdl"] = model_tmdl(spec.MANUAIS + list(SCHEMAS) + list(spec.DESCONECTADAS))
    dic = RAIZ / "contracts" / "data-dictionary.md"
    texto = dic.read_text(encoding="utf-8")
    bloco = dicionario()
    if "<!-- modelo:inicio -->" in texto:
        texto = re.sub(r"<!-- modelo:inicio -->.*<!-- modelo:fim -->", lambda m: bloco, texto, flags=re.S)
    else:
        texto = texto.replace("## Tabelas planejadas (F1–F3)", bloco + "\n\n## Tabelas planejadas (F1–F3)")
    arquivos[dic] = texto
    return arquivos


def main() -> int:
    arquivos = gerar()
    for caminho, conteudo in arquivos.items():
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(conteudo if conteudo.endswith("\n") else conteudo + "\n", encoding="utf-8", newline="\n")
    n_tab = sum(1 for p in arquivos if p.parent.name == "tables")
    ativas = sum(1 for r in spec.RELACOES if r[2])
    print(f"OK: {n_tab} tabelas, {len(spec.RELACOES)} relações ({ativas} ativas) em {DEF.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
