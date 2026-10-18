"""GET JSON com cache em disco (data/raw/cache), backoff exponencial e User-Agent identificado."""
from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CACHE = RAIZ / "data" / "raw" / "cache"
UA = "gotham-database/0.1 (projeto de portfolio; https://github.com/Muzashii/gotham-database)"
PAUSA = 1.0  # segundos entre requisições reais (cortesia com APIs públicas)
_ultima = 0.0
SOMENTE_CACHE = False  # --offline: proíbe rede (reprodutibilidade)


def get_json(url: str, *, cabecalhos: dict[str, str] | None = None, tentativas: int = 6,
             chave_cache: str | None = None, url_real: str | None = None) -> dict:
    """Retorna o JSON de `url`, do cache se existir. Repete com backoff em 429/5xx e falhas de rede.

    `url_real` permite requisitar uma URL com segredo (api_key) mantendo o cache indexado por
    `chave_cache` (sem o segredo).
    """
    global _ultima
    chave = hashlib.sha256((chave_cache or url).encode("utf-8")).hexdigest()[:24]
    arq = CACHE / f"{chave}.json"
    if arq.is_file():
        return json.loads(arq.read_text(encoding="utf-8"))
    if SOMENTE_CACHE:
        raise RuntimeError(f"modo offline e sem cache para {chave_cache or url}")
    espera = 2.0
    for n in range(tentativas):
        atraso = PAUSA - (time.monotonic() - _ultima)
        if atraso > 0:
            time.sleep(atraso)
        req = urllib.request.Request(url_real or url, headers={"User-Agent": UA, **(cabecalhos or {})})
        ultima_tentativa = n == tentativas - 1
        try:
            _ultima = time.monotonic()
            with urllib.request.urlopen(req, timeout=90) as r:
                dados = json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or ultima_tentativa:
                raise
            retry = e.headers.get("Retry-After")
            time.sleep(float(retry) if retry and retry.isdigit() else espera)
            espera *= 2
            continue
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if ultima_tentativa:
                raise
            time.sleep(espera)
            espera *= 2
            continue
        # Erros com HTTP 200: MediaWiki usa {"error": {"code": ...}}; Comic Vine usa status_code != 1
        # (e "error": "OK" no sucesso; 107 = limite de taxa).
        erro = None
        if isinstance(dados, dict):
            if isinstance(dados.get("error"), dict):
                erro = dados["error"]
            elif "status_code" in dados and dados["status_code"] != 1:
                # 107 = limite por HORA: esperar segundos não resolve, então falha na hora (sem retry)
                erro = {"code": dados["status_code"], "info": dados.get("error")}
        if erro:
            if erro.get("code") in ("ratelimited", "maxlag") and not ultima_tentativa:
                time.sleep(espera)
                espera *= 2
                continue
            raise RuntimeError(f"API devolveu erro para {url}: {erro}")  # nunca vai para o cache
        break
    CACHE.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return dados
