## Entrega: F1 — curadoria dos 50 primeiros personagens (Oráculo)

- **Status:** pronto para revisão
- **Arquivos alterados:** `data/seeds/{personagens,versoes,eras,afiliacoes,personagem_afiliacao,obras,aparicoes}.csv`,
  `etl/extract/{http,wikipedia,wikidata,superhero}.py`, `etl/curadoria/{coletar,checar}.py`, `docs/fontes.md`,
  `handoffs/F1-checagem-fatos.md`
- **Decisões tomadas (e por quê):**
  - **Fonte primária de fatos = Wikipédia (infobox) + Wikidata**; SuperHero API só para atributos e como 2ª fonte.
    A API tem só ~30 dos personagens da lista e erros conhecidos (estreia da Mulher-Gato = Detective Comics #569;
    nome civil do Coringa = Jack Napier, que é do filme de 1989).
  - Seleção: Bat-família (15, incl. Lucius Fox), GCPD (3), galeria de vilões (28, com o Exterminador), Liga das Sombras (3), convidados
    (Superman, Zatanna, Etrigan) — cobre os 8 arquétipos (EST 10, FUR 9, LUT 7, TEC 6, PSI 6, MET 5, BRU 4, MIS 3).
  - **Corte das Corujas sem membros nesta sprint:** William Cobb não tem artigo próprio e Lincoln March cai no
    artigo genérico do Owlman — sem fonte limpa, ficam para a sprint 2 (afiliação já criada).
  - Estreia = primeira aparição do **personagem**, não da persona (ex.: Barbara Gordon = Detective Comics #359 como
    Batgirl; Damian = Son of the Demon 1987, bebê). Personas posteriores vão em `nota`.
  - `confianca`: alta = 2+ fontes concordam (25); media = fontes divergem em persona, edição ou mídia (7); baixa = 1 fonte (18).
    O checador (rígido após a revisão) conta 25 com 2+ fontes. Gordon fica `media` porque o Wikidata só confirma a série.
  - Atributos de 18 personagens sem entrada na SuperHero API foram **estimados** na escala da API → `confianca=baixa`.
  - Eras: limites são convenção; contíguas de 1938 a hoje (8 eras do plano §3.3).
- **Contratos afetados:** `data-dictionary.md` v0.2 (seção de seeds)
- **Como testar:**
  ```bash
  python -m pytest tests/etl -q            # integridade dos seeds (sem rede)
  python -m etl.curadoria.coletar          # rebaixa fontes (cache em data/raw/cache)
  python -m etl.curadoria.checar           # 25/50 estreias com 2+ fontes
  ```
- **Pendências / riscos:**
  - Criadores de Alfred divergem entre Wikipédia (Cameron/Kane) e Wikidata (Finger/Kane/Robinson) — marcado na `nota`.
  - Duke Thomas: ano de capa de Batman (vol. 2) #21 incerto (2013 vs 2014) — `confianca` baixa.
  - IGDB: termos não verificados (docs bloquearam acesso automatizado).

### Ciclo 2 — correções após `handoffs/review-F1.md`
- **B1** Signal: estreia Batman (vol. 2) #21 (ago 2013), confirmada em dc.com/characters/signal (Wikipédia en diz 2014). `personagens.csv` + `obras.csv`.
- **M1** Batman Que Ri: data de capa (set 2017). **M4** Oráculo → EST (exemplo do plano §8.1); golpes refeitos (EST + cobertura TEC).
- **M5/M6** notas de criadores de Damian e Alfred corrigidas. **M7** Exterminador na Galeria de Vilões. **M8** datas fora dos títulos de obras. **M9** imagem genérica do Zsasz removida (fallback de silhueta passa a disparar).
- **M2** `checar.py`: compara volume, número e ano (±1 entre capa e venda); exemplo da revisão agora é rejeitado. Consequência: Terry McGinnis rebaixado para `media` (estreia na TV × HQ #1 na API são obras diferentes).
- **M3** `http.py`: repete em timeout/queda de conexão e em `ratelimited`/`maxlag` com HTTP 200; respostas de erro nunca vão para o cache.
- Testes de regressão: `tests/etl/test_extract.py` (136 testes no total).
