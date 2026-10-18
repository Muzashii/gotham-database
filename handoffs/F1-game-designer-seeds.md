## Entrega: F1 — seeds de game design (Ra's)

- **Status:** pronto para revisão
- **Arquivos alterados:** `data/seeds/{arquetipos,matchup,golpes,versao_golpe,gadgets,bairros,encontros}.csv`
- **Decisões tomadas (e por quê):**
  - Arquétipos e matriz 8×8 transcritos do plano §8.1/§8.2 sem mudanças — balanceamento é a F4d (simulação).
  - 24 golpes (3 por arquétipo): 1 forte/impreciso, 1 médio, 1 utilitário com efeito. Cada versão recebe os 3 do
    seu arquétipo + o 1º golpe de um arquétipo secundário (cobertura), escolhido pelo estilo do personagem.
  - Gadgets = §8.5. Bairros = §3.6, com `BonusCaptura` (Ilha Arkham 1,2 pela segurança; Diamond/Ace 0,9) e
    recarga no Diamond District.
  - Encontros: só não-heróis (capturados vão para Arkham/Blackgate); peso pela raridade
    (comum 10, incomum 6, raro 3, lendário 1). Lendários: Batman, Coringa, Ra's, Batman Que Ri, Superman
    (Batman e Superman não aparecem em encontros por serem heróis).
- **Contratos afetados:** `data-dictionary.md` v0.2 (nova tabela `dGadget`)
- **Como testar:** `python -m pytest tests/etl -q`
- **Pendências / riscos:** nada balanceado ainda; transformações (Hellbat, Veneno, Lázaro) ficam para a sprint 5.
