"""Valida os JSON do PBIP/PBIR contra os schemas oficiais da Microsoft (com cache em .cache/)
e o contraste AA dos tokens de texto."""
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

import pytest

import gotham_build as gb

CACHE = gb.RAIZ / ".cache" / "schemas"
PBI = gb.RAIZ / "powerbi"


def baixar(url: str) -> dict:
    destino = CACHE / re.sub(r"[^\w.]+", "_", url.split("json-schemas/")[-1])
    if not destino.is_file():
        destino.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "gotham-database-tests"})
        with urllib.request.urlopen(req, timeout=30) as r:
            destino.write_bytes(r.read())
    return json.loads(destino.read_text(encoding="utf-8-sig"))


def arquivos_json():
    return sorted(
        p for p in PBI.rglob("*")
        if p.suffix in (".json", ".pbir", ".pbism", ".pbip")
        and "StaticResources" not in p.parts
        and ".pbi" not in p.parts  # configurações locais do Desktop, sem $schema
    )


@pytest.mark.rede
@pytest.mark.parametrize("arq", arquivos_json(), ids=lambda p: p.relative_to(PBI).as_posix())
def test_json_pbip_valida_no_schema_oficial(arq: Path):
    jsonschema = pytest.importorskip("jsonschema")
    referencing = pytest.importorskip("referencing")
    dados = json.loads(arq.read_text(encoding="utf-8"))
    url = dados["$schema"]
    registro = referencing.Registry(retrieve=lambda u: referencing.Resource.from_contents(baixar(u)))
    try:
        schema = baixar(url)
    except urllib.error.HTTPError as e:
        if e.code == 404:  # o Desktop grava versões de schema que a Microsoft ainda não publicou
            pytest.skip(f"schema ainda não publicado pela Microsoft: {url}")
        raise
    validador = jsonschema.validators.validator_for(schema)(schema, registry=registro)
    erros = sorted(validador.iter_errors(dados), key=lambda e: list(e.path))
    assert not erros, "\n".join(f"{list(e.path)}: {e.message[:200]}" for e in erros[:10])


# ---------------------------------------------------------------- contraste AA


def luminancia(hexcor: str) -> float:
    rgb = [int(hexcor[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(a: str, b: str) -> float:
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


@pytest.mark.parametrize("texto", ["--g-text", "--g-muted", "--bat-yellow", "--arkham-green", "--ice"])
@pytest.mark.parametrize("fundo", ["--g-bg", "--g-panel"])
def test_tokens_de_texto_tem_contraste_aa(texto, fundo):
    css = (gb.DIR_CSS / "tokens.css").read_text(encoding="utf-8")
    t = dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})", css))
    assert contraste(t[texto], t[fundo]) >= 4.5
