"""Especificação do modelo semântico (dono: modelador-semantico / Gordon).

Colunas e tipos vêm de etl/quality/schemas.py (contrato das tabelas curadas); aqui ficam só as
decisões de modelagem: relações, o que fica oculto, ordenação, formatos e tabelas desconectadas.
"""

# Repositório público lido pelo Power Query (permite atualização no serviço sem gateway)
URL_BASE = "https://raw.githubusercontent.com"
CAMINHO_CURADO = "Muzashii/gotham-database/main/data/curated/"

DESCRICAO = {
    "dPersonagem": "Um personagem por linha (50 na F2). Chave canônica do projeto.",
    "dVersao": "Encarnação de um personagem com atributos de batalha (0–100). F2: só a versão padrão (Id×100+1).",
    "dEra": "Eras editoriais (limites por convenção).",
    "dMidia": "HQ, Animação, Série, Filme, Game.",
    "dAfiliacao": "Grupos (Bat-família, GCPD, Liga das Sombras…).",
    "bPersonagemAfiliacao": "Ponte personagem × afiliação. Filtro só da dimensão para a ponte; use TREATAS no DAX.",
    "dObra": "Obras (estreias + Wikidata P674) com mídia e granularidade.",
    "fAparicao": "Personagem × obra. EhEstreia=1 marca a primeira aparição.",
    "fRelacao": "Arestas tipadas entre personagens (simétricas em forma canônica Origem < Destino).",
    "dArquetipo": "8 arquétipos de combate (design).",
    "fMatchup": "Multiplicador de dano arquétipo atacante × defensor.",
    "dGolpe": "Golpes/gadgets de batalha (design).",
    "bVersaoGolpe": "Ponte versão × golpe (4 por versão).",
    "dGadget": "Gadgets de captura da Patrulha.",
    "dBairro": "Bairros de Gotham da Patrulha.",
    "fEncontro": "Bairro × personagem com peso de sorteio.",
    "dCentralidade": "Grau, intermediação e PageRank da rede de relações (calculados no ETL).",
    "dStat": "Os 6 atributos, na ordem do radar.",
}

# (de tabela.coluna (lado N), para tabela.coluna (lado 1), ativa, motivo se inativa)
RELACOES = [
    ("dPersonagem.IdArquetipo", "dArquetipo.IdArquetipo", True, ""),
    ("dPersonagem.IdEra", "dEra.IdEra", False,
     "ambígua com dEra→dObra→fAparicao; era de estreia via USERELATIONSHIP"),
    ("dVersao.IdPersonagem", "dPersonagem.IdPersonagem", True, ""),
    ("dVersao.IdArquetipo", "dArquetipo.IdArquetipo", False,
     "ambígua com dArquetipo→dPersonagem→dVersao; arquétipo da versão (transformações) via USERELATIONSHIP"),
    ("dVersao.IdMidia", "dMidia.IdMidia", True, ""),
    ("bPersonagemAfiliacao.IdPersonagem", "dPersonagem.IdPersonagem", True, ""),
    ("bPersonagemAfiliacao.IdAfiliacao", "dAfiliacao.IdAfiliacao", True, ""),
    ("dObra.IdEra", "dEra.IdEra", True, ""),
    ("dObra.IdMidia", "dMidia.IdMidia", True, ""),
    ("fAparicao.IdPersonagem", "dPersonagem.IdPersonagem", True, ""),
    ("fAparicao.IdObra", "dObra.IdObra", True, ""),
    ("fAparicao.IdVersao", "dVersao.IdVersao", False, "ambígua com dPersonagem→dVersao→fAparicao"),
    ("fRelacao.IdOrigem", "dPersonagem.IdPersonagem", True, ""),
    ("fRelacao.IdDestino", "dPersonagem.IdPersonagem", False, "duas relações para a mesma tabela; destino via USERELATIONSHIP"),
    ("fMatchup.IdAtaque", "dArquetipo.IdArquetipo", True, ""),
    ("fMatchup.IdDefesa", "dArquetipo.IdArquetipo", False, "duas relações para a mesma tabela; defesa via USERELATIONSHIP"),
    ("dGolpe.IdArquetipo", "dArquetipo.IdArquetipo", False,
     "ambígua com dArquetipo→dPersonagem→dVersao→bVersaoGolpe"),
    ("bVersaoGolpe.IdVersao", "dVersao.IdVersao", True, ""),
    ("bVersaoGolpe.IdGolpe", "dGolpe.IdGolpe", True, ""),
    ("dGadget.SoContraArquetipo", "dArquetipo.IdArquetipo", False,
     "vazio = vale contra todos; ativa, o filtro por arquétipo esconderia os gadgets universais"),
    ("fEncontro.IdBairro", "dBairro.IdBairro", True, ""),
    ("fEncontro.IdPersonagem", "dPersonagem.IdPersonagem", True, ""),
    ("dCentralidade.IdPersonagem", "dPersonagem.IdPersonagem", True, ""),
]

# colunas visíveis apesar da regra geral (Id* e técnicas ficam ocultas)
# Plataforma e EdicoesComicVine estão 100% vazias na F2 (sem fonte/sem chave): ocultas até terem dados
OCULTAS_EXTRA = {"WikidataQid", "IdSuperHeroApi", "ComicVineId", "UrlImagem", "UrlCapa", "Fonte", "JustificativaArquetipo",
                 "Plataforma", "EdicoesComicVine"}
CATEGORIA = {"UrlImagem": "ImageUrl", "UrlCapa": "ImageUrl"}
ORDENAR_POR = {
    ("dEra", "Nome"): "Ordem", ("dMidia", "Nome"): "IdMidia", ("dStat", "Rotulo"): "Ordem",
    ("dStat", "Codigo"): "Ordem", ("dArquetipo", "Nome"): "IdArquetipo", ("dArquetipo", "Sigla"): "IdArquetipo",
}
FORMATO = {
    "Intermediacao": "0.000", "PageRank": "0.000", "Multiplicador": "0.0#", "MultCaptura": "0.0#",
    "BonusCaptura": "0.0#", "Ano": "0", "AnoEstreia": "0", "AnoInicio": "0", "AnoFim": "0",
    "EdicoesComicVine": "#,0",
}
SOMAR = {"EdicoesComicVine"}  # única coluna aditiva; o resto é atributo (summarizeBy none)

# Tabelas desconectadas (seleção sem filtrar a página) — plano §6.1
DESCONECTADAS = {
    "Modo": {
        "descricao": "Modo da ficha do Batcomputador.",
        "colunas": [("Ordem", "int64"), ("Modo", "string"), ("Icone", "string")],
        "m": '#table(type table [Ordem = Int64.Type, Modo = text, Icone = text], '
             '{{1, "Arquivo", "🦇"}, {2, "Arkham", "🏥"}, {3, "Versões", "🎭"}, {4, "Capas", "📚"}})',
        "ordenar": {"Modo": "Ordem"},
    },
    "TemaSel": {
        "descricao": "Tema visual por facção (classes fx-* de contracts/design-tokens.md).",
        "colunas": [("Ordem", "int64"), ("Faccao", "string"), ("Tema", "string")],
        "m": '#table(type table [Ordem = Int64.Type, Faccao = text, Tema = text], {'
             '{1, "gotham", "Gotham (chuva)"}, {2, "batfamilia", "Bat-família"}, {3, "coringa", "Coringa"}, '
             '{4, "espantalho", "Espantalho"}, {5, "frio", "Sr. Frio"}, {6, "hera", "Hera Venenosa"}, '
             '{7, "charada", "Charada"}, {8, "duascaras", "Duas-Caras"}, {9, "corujas", "Corte das Corujas"}, '
             '{10, "vagalume", "Vagalume"}})',
        "ordenar": {"Tema": "Ordem"},
    },
    "VersaoSel": {
        "descricao": "Cópia desconectada das versões (clique no carrossel de versões).",
        "colunas": [("IdVersao", "int64"), ("NomeVersao", "string")],
        "m": 'Table.SelectColumns(dVersao, {"IdVersao", "NomeVersao"})',
        "ordenar": {},
    },
    "RelacaoSel": {
        "descricao": "Cópia desconectada dos personagens (clique em nó do grafo).",
        "colunas": [("IdPersonagem", "int64"), ("Nome", "string")],
        "m": 'Table.SelectColumns(dPersonagem, {"IdPersonagem", "Nome"})',
        "ordenar": {},
    },
    "ObraSel": {
        "descricao": "Cópia desconectada das obras (clique em marco da linha do tempo).",
        "colunas": [("IdObra", "int64"), ("Titulo", "string")],
        "m": 'Table.SelectColumns(dObra, {"IdObra", "Titulo"})',
        "ordenar": {},
    },
}

# Tabelas mantidas à mão no TMDL (não geradas aqui)
MANUAIS = ["_Medidas", "SpikeTamanho"]
