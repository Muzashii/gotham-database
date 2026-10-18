# F0 — Como validar o spike no Power BI Desktop

Esta parte **precisa ser feita à mão** (o Power BI Desktop não estava instalado na máquina
onde o spike foi construído). Leva ~10 minutos.

## Pré-requisitos

- Power BI Desktop (versão recente) com a opção de pré-visualização
  **"Salvar projeto do Power BI (.pbip)"** e **"Formato de relatório avançado (PBIR)"** ligadas
  (*Arquivo › Opções › Recursos de visualização*).

## Passos

1. `python build/build_model.py && python build/build_report.py`
2. Abra `powerbi/GothamDatabase.pbip`. Clique em **Atualizar** para carregar `SpikeTamanho`.
3. Página **F0 Spike**: devem existir o slicer de tamanho e o cartão `Tamanho HTML Spike`.
4. Importe o visual **HTML Content** do AppSource (*Visualizações › … › Obter mais visuais*).
   Use a edição **padrão** (a *lite*/*Secure* não executa scripts — é exatamente o que o spike testa;
   se quiser, importe as duas e compare).
5. Salve (Ctrl+S) e feche o Desktop. Rode `python build/build_report.py` de novo: ele detecta o GUID
   em `report.json` e adiciona o visual `gdSpikeHtml` ligado a `[HTML Spike]`. Reabra o `.pbip`.
   (Alternativa: arraste o visual e a medida `HTML Spike` à mão.)
6. Preencha a tabela abaixo e cole em `handoffs/F0-resumo.md`.

## O que observar

| Teste | Como | Resultado esperado |
|---|---|---|
| JS via `<script>` | cartão "JS via script" | ✔ ativo |
| JS via `onerror` | cartão "JS via onerror" | ✔ ativo (caminho de reserva se o visual usa innerHTML) |
| Estado na `window` | clique +1 três vezes, troque o slicer, volte | contador continua em 3; "Renderizações" sobe |
| Troca de página | vá a outra página e volte | o contador sobrevive? (anote: o visual pode ser recriado) |
| Animação | chuva + holofote | fluida; sem duplicar velocidade após vários redesenhos |
| Limite de tamanho | suba o slicer até 5 milhões | anote o maior valor em que "recebidos" bate com o pedido e o visual não trava |
| Tempo | *Exibir › Analisador de desempenho* | tempo do visual HTML em cada tamanho |

## Sem Power BI

`python build/build_preview.py` gera `dist/preview/spike.html`, um harness que simula os dois
modos de redesenho do visual (com e sem execução de `<script>`).
