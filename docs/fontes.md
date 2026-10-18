# Fontes de dados — endpoints, limites e termos (verificado na F1, 18/10/2026)

Regra do projeto: APIs com chave/limite **nunca** são chamadas pelo Power Query. O ETL (`etl/`)
coleta com cache em disco (`data/raw/cache`, fora do Git), pausa entre requisições, backoff exponencial
em 429/5xx e User-Agent identificado (`etl/extract/http.py`).

| Fonte | Uso no projeto | Acesso | Limites | Termos / atribuição | Verificação |
|---|---|---|---|---|---|
| **Wikipédia (en)** | Estreia, criadores, nome civil (infobox) | MediaWiki API, sem chave | Sem limite fixo; requisições em série; backoff em `ratelimited`/429 | Texto CC BY-SA — usamos só **fatos** curtos, com link para o artigo na coluna `fonte` | [API:Etiquette](https://www.mediawiki.org/wiki/API:Etiquette) ✔ — exige User-Agent com contato e proíbe requisições paralelas |
| **Wikidata** | QID, criadores (P170), primeira aparição (P4584) | SPARQL público | Mesma etiqueta Wikimedia | CC0 | ✔ (P4584 tem pouca cobertura: 8/50) |
| **SuperHero API (akabab)** | Powerstats, 2ª fonte de estreia, imagens | JSON estático via jsDelivr, sem chave | CDN | Sem licença declarada no README — usamos só números e URLs de imagem (hotlink, não redistribuídas) | ✔ — **qualidade baixa** em biografia (ex.: estreia da Mulher-Gato e nome civil do Coringa errados) |
| **Comic Vine** | Contagem de edições, relações, capas (F2+) | Chave gratuita | **200 requisições por recurso por hora** | **Só uso não comercial**; link para a Comic Vine em toda página que usa os dados | [API](https://comicvine.gamespot.com/api/) ✔ |
| **TMDB** | Filmes/séries/animações (F2+) | Chave gratuita | não informado na FAQ | Exibir “This product uses the TMDB API but is not endorsed or certified by TMDB.” + logo aprovado nos créditos; uso comercial exige licença | [FAQ](https://developer.themoviedb.org/docs/faq) ✔ |
| **IGDB** | Games (F2+) | OAuth via Twitch (client credentials) | conhecido: ~4 req/s | Uso comercial exige parceria | ⚠ docs devolveram 403 ao acesso automatizado — **pendente de verificação manual** |
| **DC Database (Fandom)** | Só dados faltantes | MediaWiki API | Etiqueta Wikimedia/Fandom | CC BY-SA, com atribuição | não usado ainda |

## Consequências

- Página de créditos do relatório (F7) precisa dos avisos da Comic Vine e da TMDB.
- Chaves (`COMICVINE_API_KEY`, `TMDB_API_KEY`, `IGDB_*`) só em `.env` (ver `.env.example`).
- A SuperHero API é usada para **atributos** e como **2ª fonte**, nunca como fonte primária de fato de lore.
