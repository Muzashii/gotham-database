"""Regrava tables/_Medidas.tmdl a partir de src/dax (+ templates src/html, src/css, src/js)."""
import sys

from gotham_build import MODELO, TABELA_MEDIDAS, ErroBuild, ler_medidas, medidas_para_tmdl, tamanho_literal


def main() -> int:
    try:
        medidas = ler_medidas()
        tmdl = medidas_para_tmdl(medidas)
    except ErroBuild as e:
        print(f"ERRO: {e}")
        return 1
    destino = MODELO / "definition" / "tables" / f"{TABELA_MEDIDAS}.tmdl"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(tmdl, encoding="utf-8", newline="\n")
    for md in medidas:
        print(f"  {md.nome:<24} {tamanho_literal(md.expressao):>7} chars estáticos")
    print(f"OK: {len(medidas)} medidas -> {destino.relative_to(MODELO.parent.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
