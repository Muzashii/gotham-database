"""Gera/atualiza o relatório PBIR (powerbi/GothamDatabase.Report) e o arquivo .pbip.

Visuais e páginas criados aqui têm nomes fixos (prefixo 'gd') e são regravados a cada
execução; visuais adicionados à mão no Desktop (outros nomes) são preservados.

O visual HTML Content (AppSource) só entra no relatório quando o GUID for conhecido:
- detectado automaticamente em report.json -> publicCustomVisuals (após importar o visual
  uma vez no Desktop e salvar), ou
- configurado em build/config.json -> htmlContent.visualType.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from gotham_build import DIR_CSS, RAIZ

PBI = RAIZ / "powerbi"
NOME = "GothamDatabase"
REL = PBI / f"{NOME}.Report"
DEF = REL / "definition"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric"
TEMA = "GothamNoir.json"

# a primeira página é a principal (abre no link público)
PAGINAS = [
    {"name": "gdBatcomputador", "displayName": "Batcomputador", "visuais": ["gdBatcomputadorHtml"]},
    {"name": "gdPainel", "displayName": "Painel do Comissário", "visuais": ["gdPainelHtml"]},
    {"name": "gdF0Spike", "displayName": "F0 Spike", "visuais": ["gdSpikeSlicer", "gdSpikeTamanho", "gdSpikeHtml"]},
]


def gravar(caminho: Path, dados: dict) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def ler(caminho: Path) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8")) if caminho.is_file() else {}


def tokens() -> dict[str, str]:
    css = (DIR_CSS / "tokens.css").read_text(encoding="utf-8")
    return dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})", css))


def campo_coluna(tabela: str, coluna: str) -> dict:
    return {
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": tabela}}, "Property": coluna}},
        "queryRef": f"{tabela}.{coluna}",
        "nativeQueryRef": coluna,
    }


def campo_medida(medida: str, tabela: str = "_Medidas") -> dict:
    return {
        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": tabela}}, "Property": medida}},
        "queryRef": f"{tabela}.{medida}",
        "nativeQueryRef": medida,
    }


def container(nome: str, x: int, y: int, w: int, h: int, z: int, visual: dict) -> dict:
    return {
        "$schema": f"{SCHEMA}/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": nome,
        "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z},
        "visual": visual,
    }


def visuais_f0(guid_html: str | None, papel_html: str) -> dict[str, dict]:
    v = {
        "gdSpikeSlicer": container(
            "gdSpikeSlicer", 16, 16, 260, 80, 0,
            {
                "visualType": "slicer",
                "query": {"queryState": {"Values": {"projections": [campo_coluna("SpikeTamanho", "Rotulo")]}}},
                "objects": {"data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}]},
                "drillFilterOtherVisuals": True,
            },
        ),
        "gdSpikeTamanho": container(
            "gdSpikeTamanho", 16, 112, 260, 110, 1000,
            {
                "visualType": "card",
                "query": {"queryState": {"Values": {"projections": [campo_medida("Tamanho HTML Spike")]}}},
                "drillFilterOtherVisuals": True,
            },
        ),
    }
    if guid_html:
        v["gdBatcomputadorHtml"] = container(
            "gdBatcomputadorHtml", 0, 0, 1280, 720, 0,
            {
                "visualType": guid_html,
                "query": {"queryState": {papel_html: {"projections": [campo_medida("HTML Batcomputador")]}}},
                "drillFilterOtherVisuals": True,
            },
        )
        v["gdPainelHtml"] = container(
            "gdPainelHtml", 0, 0, 1280, 720, 0,
            {
                "visualType": guid_html,
                "query": {"queryState": {papel_html: {"projections": [campo_medida("HTML Painel")]}}},
                "drillFilterOtherVisuals": True,
            },
        )
        v["gdSpikeHtml"] = container(
            "gdSpikeHtml", 292, 16, 972, 688, 2000,
            {
                "visualType": guid_html,
                "query": {"queryState": {papel_html: {"projections": [campo_medida("HTML Spike")]}}},
                "drillFilterOtherVisuals": True,
            },
        )
    return v


def tema() -> dict:
    t = tokens()
    return {
        "name": "Gotham Noir",
        "dataColors": [t["--bat-yellow"], t["--arkham-green"], t["--ice"], t["--joker-purple"],
                       t["--blood"], t["--owl-bronze"], t["--ivy"], t["--g-muted"]],
        "background": t["--g-bg"],
        "foreground": t["--g-text"],
        "tableAccent": t["--bat-yellow"],
        "textClasses": {
            "callout": {"color": t["--bat-yellow"]},
            "label": {"color": t["--g-text"]},
            "title": {"color": t["--g-text"]},
        },
        "visualStyles": {
            "*": {"*": {"background": [{"color": {"solid": {"color": t["--g-panel"]}}, "transparency": 0}]}},
            "page": {"*": {"background": [{"color": {"solid": {"color": t["--g-bg"]}}, "transparency": 0}]}},
        },
    }


def detectar_guid(report: dict, config: dict) -> str | None:
    cfg = config.get("htmlContent", {}).get("visualType")
    if cfg:
        return cfg
    for guid in report.get("publicCustomVisuals", []):
        if guid.startswith("htmlContent"):
            return guid
    return None


def main() -> int:
    config = ler(RAIZ / "build" / "config.json")
    report_atual = ler(DEF / "report.json")
    guid = detectar_guid(report_atual, config)
    papel = config.get("htmlContent", {}).get("papel", "content")

    gravar(PBI / f"{NOME}.pbip", {
        "$schema": f"{SCHEMA}/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [{"report": {"path": f"{NOME}.Report"}}],
        "settings": {"enableAutoRecovery": True},
    })
    gravar(REL / "definition.pbir", {
        "$schema": f"{SCHEMA}/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {"byPath": {"path": f"../{NOME}.SemanticModel"}},
    })
    gravar(DEF / "version.json", {
        "$schema": f"{SCHEMA}/item/report/definition/versionMetadata/1.0.0/schema.json",
        "version": "2.0.0",
    })

    report = dict(report_atual)  # preserva o que o Desktop gravou
    # mantém a versão de schema que o Desktop gravou (pode ser mais nova que a nossa)
    report.setdefault("$schema", f"{SCHEMA}/item/report/definition/report/3.0.0/schema.json")
    report.setdefault("themeCollection", {})["customTheme"] = {
        "name": TEMA,
        "reportVersionAtImport": {"visual": "2.0.0", "report": "3.0.0", "page": "2.0.0"},
        "type": "RegisteredResources",
    }
    pacotes = [p for p in report.get("resourcePackages", []) if p.get("name") != "RegisteredResources"]
    registrados = next((p for p in report.get("resourcePackages", []) if p.get("name") == "RegisteredResources"),
                       {"name": "RegisteredResources", "type": "RegisteredResources", "items": []})
    registrados["items"] = [i for i in registrados["items"] if i.get("name") != TEMA]
    registrados["items"].append({"name": TEMA, "path": TEMA, "type": "CustomTheme"})
    report["resourcePackages"] = pacotes + [registrados]
    if guid and guid not in report.get("publicCustomVisuals", []):
        report.setdefault("publicCustomVisuals", []).append(guid)
    gravar(DEF / "report.json", report)
    gravar(REL / "StaticResources" / "RegisteredResources" / TEMA, tema())

    meta = ler(DEF / "pages" / "pages.json")
    nossas = [pg["name"] for pg in PAGINAS]
    ordem = nossas + [p for p in meta.get("pageOrder", []) if p not in nossas]  # páginas feitas à mão vão depois
    gravar(DEF / "pages" / "pages.json", {
        "$schema": f"{SCHEMA}/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": ordem,
        "activePageName": ordem[0],
    })

    visuais = visuais_f0(guid, papel)
    for pg in PAGINAS:
        base = DEF / "pages" / pg["name"]
        pagina = ler(base / "page.json")
        pagina.update({
            "$schema": f"{SCHEMA}/item/report/definition/page/2.0.0/schema.json",
            "name": pg["name"],
            "displayName": pg["displayName"],
            "displayOption": "FitToPage",
            "height": 720,
            "width": 1280,
        })
        gravar(base / "page.json", pagina)
        for nome in pg["visuais"]:
            if nome in visuais:
                gravar(base / "visuals" / nome / "visual.json", visuais[nome])

    print(f"OK: relatório PBIR em {REL.relative_to(RAIZ)}")
    if guid:
        print(f"  HTML Content: {guid} (papel '{papel}')")
    else:
        print("  AVISO: visual HTML Content ainda não importado. Abra o .pbip no Desktop, importe")
        print("  'HTML Content' do AppSource, salve e rode este script de novo (ver docs/f0-spike.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
