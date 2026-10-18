"""Checagens de build (gate do CI). Sai com código 1 se algo reprovar.

1. Aspas duplas em src/js, src/css e src/html (fora dos slots [[dax:...]]).
2. Crases triplas (quebram o bloco ``` do TMDL).
3. Slots de template apontando para arquivos inexistentes ou de tipo desconhecido
   ([[svg:...]]), e ``` dentro de src/dax.
4. var(--token) usado em CSS/HTML/JS sem definição em src/css/tokens.css.
5. Medidas acima do orçamento de caracteres estáticos (build/budget.json).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from gotham_build import (
    DIR_CSS,
    DIR_HTML,
    DIR_JS,
    RAIZ,
    ErroBuild,
    ler_medidas,
    medidas_para_tmdl,
    parse_template,
    tamanho_literal,
)

RE_VAR = re.compile(r"var\(\s*(--[\w-]+)")
RE_DEF = re.compile(r"(--[\w-]+)\s*:")
RE_SLOT = re.compile(r"\[\[(\w+):")
SLOTS = {"css", "js", "dax"}


def rel(p: Path) -> str:
    return p.relative_to(RAIZ).as_posix()


def texto_sem_slots_dax(caminho: Path) -> str:
    pedacos = parse_template(caminho.read_text(encoding="utf-8"), caminho.name)
    return "".join(p.valor if p.tipo == "txt" else "" for p in pedacos)


def checar_aspas(erros: list[str]) -> None:
    arquivos = [*DIR_JS.rglob("*.js"), *DIR_CSS.rglob("*.css"), *DIR_HTML.rglob("*.html")]
    for arq in arquivos:
        texto = texto_sem_slots_dax(arq) if arq.suffix == ".html" else arq.read_text(encoding="utf-8")
        for n, linha in enumerate(texto.splitlines(), 1):
            if '"' in linha:
                erros.append(f'{rel(arq)}:{n}: aspas duplas proibidas -> {linha.strip()[:80]}')
            if "```" in linha:
                erros.append(f"{rel(arq)}:{n}: crase tripla proibida")


def checar_slots(erros: list[str]) -> None:
    for tpl in DIR_HTML.rglob("*.html"):
        for tipo in sorted(set(RE_SLOT.findall(tpl.read_text(encoding="utf-8"))) - SLOTS):
            erros.append(f"{rel(tpl)}: tipo de slot desconhecido [[{tipo}:")
        try:
            pedacos = parse_template(tpl.read_text(encoding="utf-8"), tpl.name)
        except ErroBuild as e:
            erros.append(str(e))
            continue
        for p in pedacos:
            if p.tipo in ("css", "js") and not ((DIR_CSS if p.tipo == "css" else DIR_JS) / p.valor).is_file():
                erros.append(f"{rel(tpl)}: slot [[{p.tipo}:{p.valor}]] aponta para arquivo inexistente")


def checar_tokens(erros: list[str]) -> None:
    definidos = set(RE_DEF.findall((DIR_CSS / "tokens.css").read_text(encoding="utf-8")))
    for arq in [*DIR_CSS.rglob("*.css"), *DIR_HTML.rglob("*.html"), *DIR_JS.rglob("*.js")]:
        for n, linha in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
            for token in RE_VAR.findall(linha):
                if token not in definidos:
                    erros.append(f"{rel(arq)}:{n}: token CSS indefinido {token}")


def checar_orcamento(erros: list[str]) -> list[tuple[str, int, int]]:
    orc = json.loads((RAIZ / "build" / "budget.json").read_text(encoding="utf-8"))
    relatorio = []
    try:
        medidas = ler_medidas()
    except ErroBuild as e:
        erros.append(str(e))
        return relatorio
    try:
        medidas_para_tmdl(medidas)  # reprova ``` dentro de src/dax
    except ErroBuild as e:
        erros.append(str(e))
    for md in medidas:
        limite = orc["medidas"].get(md.nome, orc["padrao"])
        tam = tamanho_literal(md.expressao)
        relatorio.append((md.nome, tam, limite))
        if tam > limite:
            erros.append(f"medida '{md.nome}': {tam} chars estáticos > orçamento {limite}")
    return relatorio


def main() -> int:
    erros: list[str] = []
    checar_aspas(erros)
    checar_slots(erros)
    checar_tokens(erros)
    for nome, tam, limite in checar_orcamento(erros):
        print(f"  {nome:<24} {tam:>7} / {limite:<7} chars")
    if erros:
        print(f"\nREPROVADO ({len(erros)}):")
        for e in erros:
            print(f"  - {e}")
        return 1
    print("APROVADO: checks.py sem erros")
    return 0


if __name__ == "__main__":
    sys.exit(main())
