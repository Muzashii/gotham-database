"""Testes do núcleo do build (templates -> DAX/TMDL) e do checks.py."""
import re

import pytest

import checks
import gotham_build as gb


# ---------------------------------------------------------------- templates


def test_slot_dax_com_colchetes_aninhados():
    p = gb.parse_template("<b>[[dax:[Spike Linhas]]]</b>")
    assert [(x.tipo, x.valor) for x in p] == [("txt", "<b>"), ("dax", "[Spike Linhas]"), ("txt", "</b>")]


def test_slot_dax_ignora_colchete_dentro_de_string():
    p = gb.parse_template('[[dax:IF([A] > 1, "]]", "x")]]fim')
    assert p[0].valor == 'IF([A] > 1, "]]", "x")'
    assert p[1].valor == "fim"


def test_slot_nao_fechado_falha():
    with pytest.raises(gb.ErroBuild):
        gb.parse_template("<i>[[dax:[X]</i>")


def test_literal_dax_quebra_em_pedacos_e_escapa_aspas():
    texto = "a" * (gb.TAM_PEDACO * 2 + 5)
    lit = gb.literal_dax(texto)
    assert lit.count('" & "') == 2
    assert gb.literal_dax('x"y') == '"x""y"'


def test_literal_dax_nao_divide_aspas_escapadas_entre_pedacos():
    texto = "a" * (gb.TAM_PEDACO - 1) + '"b'
    pedacos = re_literais(gb.literal_dax(texto))
    assert "".join(p.replace('""', '"') for p in pedacos) == texto


def re_literais(expr):
    return re.findall(r'"((?:[^"]|"")*)"', expr)


def test_compactar_preserva_quebra_junto_ao_slot():
    """Regressão: comentário JS não pode engolir o slot nem palavras se fundirem."""
    tpl = "<script>\n  // dados\n[[dax:[JS Gotham]]]\n  GOTHAM.ok=1</script><p>Total: [[dax:[X]]] chars</p>"
    html = "".join(
        gb.compactar(p.valor) if p.tipo == "txt" else "<" + p.valor + ">" for p in gb.parse_template(tpl)
    )
    assert "// dados\n<[JS Gotham]>\nGOTHAM.ok=1" in html
    assert "Total: <[X]> chars" in html


def test_tamanho_literal_conta_aspas_escapadas_uma_vez():
    assert gb.tamanho_literal('"ab""c" & [M] & "d"') == 5


def test_html_spike_expande_template_e_mantem_slots_dax():
    md = {m.nome: m for m in gb.ler_medidas()}["HTML Spike"]
    assert "TEMPLATE(" not in md.expressao
    assert "( [Spike Payload] )" in md.expressao
    assert "window.GOTHAM_STATE" in md.expressao
    assert md.pasta == "99 Spike"
    assert md.templates == ["spike.html"]


def test_preview_usa_mock_e_gera_payload():
    html = gb.template_para_html("spike.html", gb.ler_mock("spike.html"))
    assert "x" * 1000 in html
    assert "[[" not in html


# ---------------------------------------------------------------- TMDL


def test_tmdl_tem_todas_as_medidas_e_metadados():
    medidas = gb.ler_medidas()
    tmdl = gb.medidas_para_tmdl(medidas)
    for md in medidas:
        assert f"measure {gb.nome_tmdl(md.nome)} = ```" in tmdl
    assert tmdl.count("```") == 2 * len(medidas)
    assert "displayFolder: 99 Spike" in tmdl
    assert "formatString: #,0" in tmdl
    assert "partition _Medidas = m" in tmdl


def test_nome_tmdl_cita_quando_necessario():
    assert gb.nome_tmdl("Medida") == "Medida"
    assert gb.nome_tmdl("HTML Spike") == "'HTML Spike'"
    assert gb.nome_tmdl("Ra's") == "'Ra''s'"


def test_tmdl_commitado_esta_atualizado():
    """O arquivo gerado no repositório deve bater com src/ (rode build/build_model.py)."""
    arq = gb.MODELO / "definition" / "tables" / "_Medidas.tmdl"
    assert arq.read_text(encoding="utf-8") == gb.medidas_para_tmdl(gb.ler_medidas())


def test_modelo_referencia_todas_as_tabelas():
    defn = gb.MODELO / "definition"
    refs = set(re.findall(r"^ref table (\S+)", (defn / "model.tmdl").read_text(encoding="utf-8"), re.M))
    arquivos = {p.stem for p in (defn / "tables").glob("*.tmdl")}
    assert refs == arquivos


# ---------------------------------------------------------------- checks.py


@pytest.fixture
def src_falso(tmp_path, monkeypatch):
    for nome in ("css", "js", "html"):
        (tmp_path / nome).mkdir()
    (tmp_path / "css" / "tokens.css").write_text(":root{--ok:#fff;}", encoding="utf-8")
    monkeypatch.setattr(checks, "DIR_CSS", tmp_path / "css")
    monkeypatch.setattr(checks, "DIR_JS", tmp_path / "js")
    monkeypatch.setattr(checks, "DIR_HTML", tmp_path / "html")
    monkeypatch.setattr(checks, "RAIZ", tmp_path)
    return tmp_path


def test_checks_reprova_aspas_duplas_em_js(src_falso):
    (src_falso / "js" / "a.js").write_text("const x = 'ok';\nconst y = \"ruim\";\n", encoding="utf-8")
    erros = []
    checks.checar_aspas(erros)
    assert len(erros) == 1 and "a.js:2" in erros[0]


def test_checks_aceita_aspas_dentro_de_slot_dax(src_falso):
    (src_falso / "html" / "t.html").write_text("<p>[[dax:FORMAT([X], \"0\", \"en-US\")]]</p>", encoding="utf-8")
    erros = []
    checks.checar_aspas(erros)
    assert erros == []


def test_checks_reprova_crase_tripla(src_falso):
    (src_falso / "js" / "a.js").write_text("const s = ```;", encoding="utf-8")
    erros = []
    checks.checar_aspas(erros)
    assert any("crase" in e for e in erros)


def test_checks_reprova_token_indefinido(src_falso):
    (src_falso / "css" / "a.css").write_text(".a{color:var(--ok);background:var(--nao-existe)}", encoding="utf-8")
    erros = []
    checks.checar_tokens(erros)
    assert len(erros) == 1 and "--nao-existe" in erros[0]


def test_checks_reprova_slot_para_arquivo_inexistente(src_falso):
    (src_falso / "html" / "t.html").write_text("<style>[[css:sumiu.css]]</style>", encoding="utf-8")
    erros = []
    checks.checar_slots(erros)
    assert len(erros) == 1 and "sumiu.css" in erros[0]


def test_checks_reprova_slot_de_tipo_desconhecido(src_falso):
    (src_falso / "html" / "t.html").write_text("<i>[[svg:radar]]</i>", encoding="utf-8")
    erros = []
    checks.checar_slots(erros)
    assert len(erros) == 1 and "[[svg:" in erros[0]


def test_checks_token_so_vale_se_definido_em_tokens_css(src_falso):
    (src_falso / "css" / "a.css").write_text(":root{--local:#000}.a{color:var(--local)}", encoding="utf-8")
    erros = []
    checks.checar_tokens(erros)
    assert len(erros) == 1 and "--local" in erros[0]


def test_checks_varre_subpastas(src_falso):
    (src_falso / "js" / "apps").mkdir()
    (src_falso / "js" / "apps" / "b.js").write_text('const x = "ruim";', encoding="utf-8")
    erros = []
    checks.checar_aspas(erros)
    assert len(erros) == 1 and "apps/b.js" in erros[0]


def test_checks_do_repositorio_passa():
    assert checks.main() == 0


def test_js_gotham_itera_dimensoes_sem_membro_em_branco():
    """Regressão F4: ALL(dArquetipo) trazia o membro em branco (FK vazia em dGadget) e deslocava a matriz."""
    expr = (gb.DIR_DAX / "JS Gotham.dax").read_text(encoding="utf-8")
    assert not re.search(r"\bALL\s*\(\s*d[A-Z]\w*\s*\)", expr)
    assert not re.search(r"CONCATENATEX\s*\(\s*d[A-Z]", expr)


def test_js_gotham_escapa_todo_texto_que_entra_em_string_js():
    """Revisão F4 (M1): nenhuma coluna entra entre aspas simples sem passar pelo escape (inclui LF/CR)."""
    expr = (gb.DIR_DAX / "JS Gotham.dax").read_text(encoding="utf-8")
    cru = re.findall(r"'\"\s*&\s*([dfb][A-Z]\w*\[\w+\])", expr)
    assert cru == [], f"colunas sem escape dentro de string JS: {cru}"
    bs = chr(92)  # barra invertida
    escapes = [
        f'"{bs}", "{bs}{bs}"',              # \  -> \\
        f'"\'", "{bs}\'"',                  # '  -> \'
        f'"</", "<{bs}/"',                  # </ -> <\/
        f'UNICHAR ( 10 ), "{bs}n"',         # LF -> \n
        f'UNICHAR ( 13 ), "{bs}r"',         # CR -> \r
    ]
    for alvo in escapes:
        assert expr.count(alvo) >= 21, f"escape ausente ou incompleto: {alvo}"


def test_contraste_aa_do_item_selecionado_da_lista():
    """Revisão F4 (B1): fundo opaco do item selecionado com texto secundário claro."""
    from test_pbip import contraste
    css = (gb.DIR_CSS / "batcomputador.css").read_text(encoding="utf-8")
    fundo = re.search(r"\.bc-sel \{[^}]*background: (#[0-9a-f]{6})", css).group(1)
    # a regra do selecionado precisa VENCER a cascata: especificidade maior que .bc-in small (0,1,1)
    assert ".bc-sel .bc-in small { color: var(--g-text); }" in css
    assert ".bc-sel small {" not in css, "seletor fraco: perderia para .bc-in small (achado do ciclo 2)"
    assert contraste("#d7dde4", fundo) >= 4.5
    assert contraste("#7d8794", fundo) < 4.5  # documenta por que o texto secundário não pode ficar em --g-muted
