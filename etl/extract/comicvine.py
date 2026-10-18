"""Comic Vine (opcional): contagem de edições e estreia por personagem.

Precisa de COMICVINE_API_KEY no ambiente ou em .env (chave gratuita, uso não comercial,
200 requisições por recurso por hora — ver docs/fontes.md). Sem chave, o ETL pula esta fonte.
A chave não entra no nome do arquivo de cache nem é gravada em disco.
"""
from __future__ import annotations

import os
import re
import unicodedata
import urllib.parse

from .http import RAIZ, get_json

API = "https://comicvine.gamespot.com/api"
CAMPOS = "id,name,real_name,count_of_issue_appearances,first_appeared_in_issue,publisher,site_detail_url"


def chave() -> str | None:
    if os.environ.get("COMICVINE_API_KEY"):
        return os.environ["COMICVINE_API_KEY"]
    env = RAIZ / ".env"
    if env.is_file():
        for linha in env.read_text(encoding="utf-8").splitlines():
            if linha.startswith("COMICVINE_API_KEY=") and linha.split("=", 1)[1].strip():
                return linha.split("=", 1)[1].strip()
    return None


def normalizar(nome: str) -> str:
    s = unicodedata.normalize("NFKD", nome or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def buscar(titulo_wikipedia: str, nome_civil: str, api_key: str) -> dict | None:
    """Melhor candidato DC: busca pelo nome civil (mais específico) e, sem acerto, pelo nome em inglês.

    Aceita só casamento exato de nome civil (`real_name`) ou de nome (`name`), nesta ordem de preferência;
    o desempate por nº de edições só vale entre candidatos do mesmo critério (evita casar Damian com
    o "Robin" mais frequente ou Terry McGinnis com o Batman de Bruce Wayne).
    Não testado com chave real — ver handoffs/F2-engenheiro-dados-etl.md.
    """
    nome_en = re.sub(r"\s*\(.*?\)", "", titulo_wikipedia or "").strip()
    parenteses = re.findall(r"\((.*?)\)", titulo_wikipedia or "")
    # "Batman (Terry McGinnis)": o título é de um manto compartilhado — casar por "Batman" pegaria Bruce Wayne
    if parenteses and normalizar(parenteses[0]) not in ("character", "dc comics", "comics"):
        nome_en = parenteses[0]
    civil = "" if normalizar(nome_civil) in ("", "desconhecida") else nome_civil
    for consulta in [q for q in (civil, nome_en) if q]:
        params = {"format": "json", "resources": "character", "query": consulta, "field_list": CAMPOS, "limit": 10}
        url_sem_chave = f"{API}/search/?{urllib.parse.urlencode(params)}"
        dados = get_json(url_sem_chave, chave_cache=url_sem_chave,
                         url_real=f"{url_sem_chave}&{urllib.parse.urlencode({'api_key': api_key})}")
        dc = [c for c in dados.get("results", []) if (c.get("publisher") or {}).get("name") == "DC Comics"]
        for criterio, alvos in (("real_name", {civil}), ("name", {nome_en, civil})):
            alvos = {normalizar(a) for a in alvos if a}
            bons = [c for c in dc if normalizar(c.get(criterio)) in alvos]
            if bons:
                melhor = max(bons, key=lambda c: c.get("count_of_issue_appearances") or 0)
                estreia = melhor.get("first_appeared_in_issue") or {}
                return {"id": melhor["id"], "nome": melhor["name"], "edicoes": melhor.get("count_of_issue_appearances"),
                        "estreia": f"{estreia.get('name') or ''} #{estreia.get('issue_number') or ''}".strip(),
                        "url": melhor.get("site_detail_url"), "criterio": criterio}
    return None
