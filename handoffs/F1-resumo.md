# F1 — Resumo (Alfred)

**Status:** gate F1 **aprovado** pela Coruja no ciclo 2 (`handoffs/review-F1.md`). Os 3 achados menores do
ciclo 2 (N1–N3) foram corrigidos em seguida.

## Entregas

| Item | Onde |
|---|---|
| 50 personagens curados (Bat-família 15, GCPD 3, galeria 28, Liga das Sombras 3, convidados 3) | `data/seeds/personagens.csv` |
| Versão padrão de cada um, com 6 atributos (32 da SuperHero API, 18 estimados → `confianca` baixa) | `versoes.csv` |
| 8 eras, 6 afiliações (53+1 vínculos), 48 obras de estreia, 50 estreias | `eras.csv`, `afiliacoes.csv`, `personagem_afiliacao.csv`, `obras.csv`, `aparicoes.csv` |
| Game design: 8 arquétipos, matriz 8×8, 24 golpes, 200 vínculos versão×golpe, 4 gadgets, 6 bairros, 42 encontros | `arquetipos.csv`, `matchup.csv`, `golpes.csv`, `versao_golpe.csv`, `gadgets.csv`, `bairros.csv`, `encontros.csv` |
| Extratores com cache, backoff e User-Agent (base do ETL da F2) | `etl/extract/` |
| Coleta e checagem cruzada de fatos | `etl/curadoria/`, `handoffs/F1-checagem-fatos.md` |
| Termos e limites das fontes | `docs/fontes.md` |
| Contrato dos seeds | `contracts/data-dictionary.md` v0.2 |

## Gate F1

| Critério (plano §12) | Resultado |
|---|---|
| 100% das linhas com `fonte` | ✔ (teste automático em todos os 14 seeds) |
| Amostra de 20 fatos checada contra 2 fontes | ✔ 25 estreias confirmadas automaticamente + 10 fatos amostrados pela Coruja em fontes independentes (dc.com, DCU Guide, Wikipédia fr/de) |
| Revisão independente | ✔ ciclo 1 reprovado (1 ano errado: Signal 2014→2013), ciclo 2 aprovado |

Qualidade: `confianca` alta 25 · media 7 · baixa 18. Testes: 137 (pytest).

## O que aprendemos

- A **SuperHero API não serve como fonte de lore**: cobre ~60% da lista e tem erros (estreia da Mulher-Gato,
  nome civil do Coringa). Fica só para atributos e como 2ª fonte.
- O **infobox da Wikipédia em inglês também erra** (ano do Signal). A amostragem manual em fonte
  independente pegou o que a checagem automática não pegaria (erro de exatamente 1 ano).

## Pendências para as próximas fases

- Corte das Corujas sem membros (sprint 2) — falta fonte limpa para William Cobb e Lincoln March.
- Criadores do Alfred e mês de capa de 52 #7: divergência entre fontes, registrada na `nota`.
- Termos da IGDB: verificar manualmente antes da F2.
- 18 atributos estimados: revisar no balanceamento (F4d).
- Versões alternativas (Hellbat, Veneno, BTAS, Arkham…) e transformações: sprint 3/5.

## Recomendação para a F2 (ETL)

Lucius transforma `data/seeds` + extratores em `etl/run_etl.py` → `data/curated/*.csv`, com validação
(pandera), centralidade (networkx, precisa de `fRelacao` — a curar) e contagem de aparições via Comic Vine
(chave gratuita, 200 req/recurso/hora, uso não comercial).

**Não avançar para a F2 sem aprovação humana.**
