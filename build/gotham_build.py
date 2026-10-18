"""Núcleo do build: lê medidas de src/dax, expande templates HTML e gera DAX/TMDL.

Usado por build_model.py, build_preview.py e checks.py.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"
DIR_DAX = SRC / "dax"
DIR_HTML = SRC / "html"
DIR_CSS = SRC / "css"
DIR_JS = SRC / "js"
MODELO = RAIZ / "powerbi" / "GothamDatabase.SemanticModel"
TABELA_MEDIDAS = "_Medidas"

# Literais DAX longos são quebrados em pedaços concatenados com & para não depender
# de limites de tamanho de literal do motor/serializador.
TAM_PEDACO = 8000

RE_TEMPLATE = re.compile(r"TEMPLATE\(\s*([\w.\-]+)\s*\)")
RE_META = re.compile(r"^--\s*@(\w+):\s*(.*)$")


class ErroBuild(Exception):
    pass


# ---------------------------------------------------------------- templates


@dataclass
class Pedaco:
    tipo: str  # 'txt' | 'css' | 'js' | 'dax'
    valor: str


def parse_template(texto: str, origem: str = "?") -> list[Pedaco]:
    """Divide um template em literais e slots [[tipo:valor]].

    Slots dax podem conter colchetes ([Medida]); o fim do slot é o primeiro ']]'
    com colchetes balanceados e fora de string DAX.
    """
    pedacos: list[Pedaco] = []
    i = 0
    buf: list[str] = []
    while i < len(texto):
        m = re.match(r"\[\[(css|js|dax):", texto[i:])
        if not m:
            buf.append(texto[i])
            i += 1
            continue
        if buf:
            pedacos.append(Pedaco("txt", "".join(buf)))
            buf = []
        tipo = m.group(1)
        j = i + m.end()
        prof = 0
        em_str = False
        while True:
            if j >= len(texto):
                raise ErroBuild(f"{origem}: slot [[{tipo}: não fechado")
            c = texto[j]
            if c == '"':
                em_str = not em_str
            elif not em_str:
                if c == "[":
                    prof += 1
                elif c == "]":
                    if prof == 0 and texto[j : j + 2] == "]]":
                        break
                    prof -= 1
            j += 1
        pedacos.append(Pedaco(tipo, texto[i + m.end() : j].strip()))
        i = j + 2
    if buf:
        pedacos.append(Pedaco("txt", "".join(buf)))
    return pedacos


def ler_asset(tipo: str, nome: str) -> str:
    pasta = {"css": DIR_CSS, "js": DIR_JS}[tipo]
    caminho = pasta / nome
    if not caminho.is_file():
        raise ErroBuild(f"asset inexistente: src/{tipo}/{nome}")
    return caminho.read_text(encoding="utf-8")


def resolver_assets(pedacos: list[Pedaco]) -> list[Pedaco]:
    """Substitui slots css/js pelo conteúdo do arquivo e funde literais vizinhos."""
    saida: list[Pedaco] = []
    for p in pedacos:
        if p.tipo in ("css", "js"):
            p = Pedaco("txt", ler_asset(p.tipo, p.valor))
        if p.tipo == "txt" and saida and saida[-1].tipo == "txt":
            saida[-1] = Pedaco("txt", saida[-1].valor + p.valor)
        else:
            saida.append(p)
    return saida


def compactar(texto: str) -> str:
    """Remove a indentação no início das linhas e as linhas vazias.

    Mantém todas as quebras de linha (JS com // depende delas) e o texto colado nas bordas,
    para não fundir um comentário ou palavra com o slot vizinho. Atenção: também afeta o
    conteúdo de template literals multilinha e <pre>; nesses casos use \\n explícito.
    """
    texto = re.sub(r"\n[ \t]+", "\n", texto)
    return re.sub(r"\n{2,}", "\n", texto)


def literal_dax(texto: str) -> str:
    # quebra antes de escapar: um "" nunca fica dividido entre dois pedaços
    partes = [texto[k : k + TAM_PEDACO] for k in range(0, len(texto), TAM_PEDACO)] or [""]
    return " & ".join('"' + p.replace('"', '""') + '"' for p in partes)


def template_para_dax(nome: str) -> str:
    caminho = DIR_HTML / nome
    if not caminho.is_file():
        raise ErroBuild(f"template inexistente: src/html/{nome}")
    pedacos = resolver_assets(parse_template(caminho.read_text(encoding="utf-8"), nome))
    termos = []
    for p in pedacos:
        if p.tipo == "txt":
            txt = compactar(p.valor)
            if txt.strip():
                termos.append(literal_dax(txt))
        else:
            termos.append(f"( {p.valor} )")
    return "\n& ".join(termos) if termos else '""'


def template_para_html(nome: str, mock: dict[str, str]) -> str:
    """Renderiza o template com valores mock para os slots DAX (preview sem Power BI)."""
    caminho = DIR_HTML / nome
    pedacos = resolver_assets(parse_template(caminho.read_text(encoding="utf-8"), nome))
    saida = []
    for p in pedacos:
        if p.tipo == "txt":
            saida.append(compactar(p.valor))
        else:
            if p.valor not in mock:
                raise ErroBuild(f"{nome}: sem valor mock para slot {p.valor!r}")
            v = mock[p.valor]
            m = re.fullmatch(r"REPT:(.):(\d+)", v)
            saida.append(m.group(1) * int(m.group(2)) if m else v)
    return "".join(saida)


def ler_mock(nome_template: str) -> dict[str, str]:
    caminho = DIR_HTML / nome_template.replace(".html", ".mock.json")
    return json.loads(caminho.read_text(encoding="utf-8")) if caminho.is_file() else {}


# ---------------------------------------------------------------- medidas


@dataclass
class Medida:
    nome: str
    expressao: str
    pasta: str = ""
    formato: str = ""
    templates: list[str] = field(default_factory=list)


def ler_medidas() -> list[Medida]:
    medidas = []
    for arq in sorted(DIR_DAX.glob("*.dax")):
        meta: dict[str, str] = {}
        corpo = []
        for linha in arq.read_text(encoding="utf-8").splitlines():
            m = RE_META.match(linha.strip())
            if m:
                meta[m.group(1)] = m.group(2).strip()
            else:
                corpo.append(linha.rstrip())
        expr = "\n".join(corpo).strip()
        if not expr:
            raise ErroBuild(f"medida vazia: {arq.name}")
        templates = RE_TEMPLATE.findall(expr)
        expr = RE_TEMPLATE.sub(lambda m: template_para_dax(m.group(1)), expr)
        medidas.append(
            Medida(arq.stem, expr, meta.get("pasta", ""), meta.get("formato", ""), templates)
        )
    return medidas


def tamanho_literal(expr: str) -> int:
    """Soma dos caracteres em literais de string DAX (proxy do tamanho estático do HTML)."""
    return sum(len(s.replace('""', '"')) for s in re.findall(r'"((?:[^"]|"")*)"', expr))


# ---------------------------------------------------------------- TMDL


def nome_tmdl(nome: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nome):
        return nome
    return "'" + nome.replace("'", "''") + "'"


def medidas_para_tmdl(medidas: list[Medida]) -> str:
    out = [
        "/// Gerado por build/build_model.py a partir de src/dax — NÃO EDITAR À MÃO.",
        f"table {TABELA_MEDIDAS}",
        "",
    ]
    for md in medidas:
        if "```" in md.expressao:
            raise ErroBuild(f"{md.nome}: expressão contém ``` (quebra o TMDL)")
        out.append(f"\tmeasure {nome_tmdl(md.nome)} = ```")
        out.extend("\t\t\t" + l if l else "" for l in md.expressao.splitlines())
        out.append("\t\t\t```")
        if md.formato:
            out.append(f"\t\tformatString: {md.formato}")
        if md.pasta:
            out.append(f"\t\tdisplayFolder: {md.pasta}")
        out.append("")
    out += [
        "\tcolumn _",
        "\t\tdataType: string",
        "\t\tisHidden",
        "\t\tsummarizeBy: none",
        "\t\tsourceColumn: _",
        "",
        f"\tpartition {TABELA_MEDIDAS} = m",
        "\t\tmode: import",
        "\t\tsource =",
        "\t\t\t\tlet",
        "\t\t\t\t    Fonte = #table(type table [_ = text], {})",
        "\t\t\t\tin",
        "\t\t\t\t    Fonte",
        "",
    ]
    return "\n".join(out)
