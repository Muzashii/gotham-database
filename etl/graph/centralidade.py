"""Centralidade da rede de relações (networkx): quem é o "hub" do universo."""
from __future__ import annotations

import networkx as nx
import pandas as pd


def centralidade(personagens: pd.Series, relacoes: pd.DataFrame) -> pd.DataFrame:
    """Grau, intermediação e PageRank num grafo não dirigido e ponderado.

    Arestas paralelas (ex.: inimigo + organização) somam peso. Todos os personagens entram como nó,
    inclusive os isolados (grau 0).
    """
    g = nx.Graph()
    g.add_nodes_from(int(p) for p in personagens)
    for r in relacoes.itertuples():
        a, b = int(r.IdOrigem), int(r.IdDestino)
        if g.has_edge(a, b):
            g[a][b]["peso"] += int(r.Peso)
        else:
            g.add_edge(a, b, peso=int(r.Peso))
    # intermediação usa distância: relação mais forte = caminho mais curto
    for _, _, d in g.edges(data=True):
        d["distancia"] = 1.0 / d["peso"]
    inter = nx.betweenness_centrality(g, weight="distancia", normalized=True)
    pr = nx.pagerank(g, weight="peso")
    return pd.DataFrame({
        "IdPersonagem": sorted(g.nodes),
        "Grau": [g.degree(n) for n in sorted(g.nodes)],
        "Intermediacao": [round(inter[n], 6) for n in sorted(g.nodes)],
        "PageRank": [round(pr[n], 6) for n in sorted(g.nodes)],
    })
