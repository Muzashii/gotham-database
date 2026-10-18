"""Gera dist/preview/<template>.html com valores mock, dentro de um harness que simula o
visual HTML Content (redesenho via script e via innerHTML) para testar sem Power BI."""
import sys
from pathlib import Path

from gotham_build import DIR_HTML, RAIZ, ErroBuild, ler_mock, template_para_html

HARNESS = RAIZ / "build" / "preview_harness.html"


def main() -> int:
    saida = RAIZ / "dist" / "preview"
    saida.mkdir(parents=True, exist_ok=True)
    harness = HARNESS.read_text(encoding="utf-8")
    for tpl in sorted(DIR_HTML.glob("*.html")):
        try:
            html = template_para_html(tpl.name, ler_mock(tpl.name))
        except ErroBuild as e:
            print(f"ERRO: {e}")
            return 1
        # o conteúdo vai num <template>; o harness o injeta como o visual faria
        pagina = harness.replace("%%TITULO%%", tpl.stem).replace("%%CONTEUDO%%", html)
        destino = saida / tpl.name
        destino.write_text(pagina, encoding="utf-8")
        print(f"OK: {destino.relative_to(RAIZ)} ({len(html):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
