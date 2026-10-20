// Batcomputador: ficha de personagem renderizada no visual HTML Content a partir de window.GOTHAM
// (contrato: contracts/js-data-schema.json). Estado em window.GOTHAM_STATE.bc: sobrevive ao redesenho.
// PROIBIDO aspas duplas (quebram a string DAX).
(function (G) {
  const S = (G.GOTHAM_STATE = G.GOTHAM_STATE || {});
  const L = (G.GOTHAM_BC = G.GOTHAM_BC || {});
  const STATS = ['Inteligência', 'Força', 'Velocidade', 'Durabilidade', 'Poder', 'Combate'];
  const COR_REL = { inimigo: '#c1121f', aliado: '#39d98a', mentor: '#f5c518', 'família': '#8ecae6', romance: '#e07aa8', rival: '#e07a1f', 'organização': '#7d8794' };
  const PARTICULAS = { coringa: '♠♥♦♣', charada: '?', frio: '❄✦', hera: '❦', corujas: '❧', vagalume: '•', espantalho: '∴', duascaras: '◐' };

  // ---------------------------------------------------------------- lógica pura (testada em Node)
  L.esc = function (t) {
    return String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/'/g, '&#39;');
  };
  L.normalizar = function (t) {
    return String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  };
  // filtros: { busca, alin, afil (id), era (id), fav (bool), favoritos (array de ids) }
  L.filtrar = function (pessoas, f) {
    const q = L.normalizar(f.busca).trim();
    return pessoas.filter(function (p) {
      if (q && L.normalizar([p.n, p.c, p.ci].join(' ')).indexOf(q) < 0) return false;
      if (f.alin && p.al !== f.alin) return false;
      if (f.afil && p.af.indexOf(f.afil) < 0) return false;
      if (f.era && p.er !== f.era) return false;
      if (f.fav && (f.favoritos || []).indexOf(p.id) < 0) return false;
      return true;
    });
  };
  // Índice de Ameaça = média dos 6 atributos; nível por faixa
  L.ameaca = function (s) {
    const v = Math.round(s.reduce(function (a, b) { return a + b; }, 0) / s.length);
    const nivel = v >= 75 ? 'Extremo' : v >= 55 ? 'Alto' : v >= 35 ? 'Moderado' : 'Baixo';
    return { valor: v, nivel: nivel };
  };
  // vértices do radar: atributo i no ângulo 2πi/n - π/2 (começa no topo, sentido horário)
  L.pontosRadar = function (s, r, cx, cy) {
    return s.map(function (v, i) {
      const ang = (2 * Math.PI * i) / s.length - Math.PI / 2;
      const k = (Math.max(0, Math.min(100, v)) / 100) * r;
      return [+(cx + k * Math.cos(ang)).toFixed(1), +(cy + k * Math.sin(ang)).toFixed(1)];
    });
  };
  // vantagens do arquétipo a (1-based) na matriz m[atk][def]
  L.vantagens = function (m, a) {
    const i = a - 1;
    const forte = [], fraco = [], vulneravel = [], resiste = [];
    const linha = function (k) { return m[k] || []; }; // matriz incompleta não derruba a ficha
    for (let j = 0; j < m.length; j++) {
      if (linha(i)[j] >= 2) forte.push(j + 1);
      if (linha(i)[j] <= 0.5) fraco.push(j + 1);
      if (linha(j)[i] >= 2) vulneravel.push(j + 1);
      if (linha(j)[i] <= 0.5) resiste.push(j + 1);
    }
    return { forte: forte, fraco: fraco, vulneravel: vulneravel, resiste: resiste };
  };
  // relações de um personagem (nos dois sentidos), mais fortes primeiro
  L.relacoesDe = function (rel, id) {
    const out = [];
    rel.forEach(function (r) {
      if (r[0] === id) out.push({ outro: r[1], tipo: r[2], peso: r[3], sai: true });
      else if (r[1] === id) out.push({ outro: r[0], tipo: r[2], peso: r[3], sai: false });
    });
    return out.sort(function (a, b) { return b.peso - a.peso || a.outro - b.outro; });
  };
  L.rotuloRelacao = function (r) {
    if (r.tipo === 'mentor') return r.sai ? 'pupilo' : 'mentor';
    if (r.tipo === 'organização') return r.sai ? 'lidera' : 'liderado por';
    return r.tipo;
  };
  // uma linha por pessoa (vários tipos viram 'família · mentor'), peso = o mais forte; ordem estável
  L.agruparRelacoes = function (rels) {
    const porOutro = {}, ordem = [];
    rels.forEach(function (r) {
      let g = porOutro[r.outro];
      if (!g) { g = porOutro[r.outro] = { outro: r.outro, peso: 0, rotulos: [], tipos: [] }; ordem.push(g); }
      g.peso = Math.max(g.peso, r.peso);
      const rot = L.rotuloRelacao(r);
      if (g.rotulos.indexOf(rot) < 0) g.rotulos.push(rot);
      if (g.tipos.indexOf(r.tipo) < 0) g.tipos.push(r.tipo);
    });
    return ordem.sort(function (a, b) { return b.peso - a.peso || a.outro - b.outro; });
  };
  L.numeroArquivo = function (id) {
    return '#BAT-' + String(id).padStart(3, '0');
  };

  // ---------------------------------------------------------------- renderização (só no navegador)
  const doc = G.document;
  const D = G.GOTHAM;
  if (!doc) return;
  const raiz = doc.getElementById('bc-raiz');
  if (!raiz || raiz.dataset.bcRan) return; // já rodou neste DOM (script + onerror)
  if (!D || !D.p || !D.p.length) {
    const aviso = raiz.querySelector('.bc-pag');
    if (aviso) aviso.textContent = 'dados indisponíveis — atualize o relatório';
    return;
  }
  raiz.dataset.bcRan = '1';

  const st = (S.bc = S.bc || { sel: 1, busca: '', alin: '', afil: 0, era: 0, fav: false, favoritos: [] });
  const porId = {};
  D.p.forEach(function (p) { porId[p.id] = p; });
  const versao = {};
  D.v.forEach(function (v) { versao[v.id] = v; });
  const arq = {};
  D.ar.forEach(function (a) { arq[a.id] = a; });
  const era = {};
  D.er.forEach(function (e) { era[e.id] = e; });
  const E = L.esc;
  if (!porId[st.sel]) st.sel = D.p[0].id;

  raiz.innerHTML =
    `<div class='bc-fx'></div><div class='bc-part'></div>
    <header class='bc-top'><span class='bc-logo'>GOTHAM DATABASE</span><span class='bc-pag'>Batcomputador</span>
      <span class='bc-cont' id='bc-cont'></span></header>
    <aside class='bc-lista'>
      <input id='bc-busca' class='bc-busca' type='search' placeholder='Buscar nome, codinome, identidade…' aria-label='Buscar personagem'>
      <div class='bc-filtros'>
        <select id='bc-alin' aria-label='Alinhamento'><option value=''>Alinhamento</option>
          ${['Herói', 'Vilão', 'Anti-herói', 'Neutro'].map(function (a) { return `<option>${a}</option>`; }).join('')}</select>
        <select id='bc-afil' aria-label='Afiliação'><option value='0'>Afiliação</option>
          ${D.af.map(function (a) { return `<option value='${a.id}'>${E(a.n)}</option>`; }).join('')}</select>
        <select id='bc-era' aria-label='Era de estreia'><option value='0'>Era</option>
          ${D.er.map(function (e) { return `<option value='${e.id}'>${E(e.n)}</option>`; }).join('')}</select>
        <button id='bc-fav' class='bc-favbtn' type='button' title='Só favoritos' aria-pressed='false'>☆</button>
      </div>
      <ul id='bc-itens' class='bc-itens' role='listbox' aria-label='Personagens'></ul>
    </aside>
    <main id='bc-ficha' class='bc-ficha'></main>
    <aside id='bc-lado' class='bc-lado'></aside>`;

  const $ = function (id) { return doc.getElementById(id); };
  $('bc-busca').value = st.busca;
  $('bc-alin').value = st.alin;
  $('bc-afil').value = String(st.afil);
  $('bc-era').value = String(st.era);

  function retrato(p, classe) {
    const img = (versao[p.v] || {}).img;
    return `<div class='${classe}'>${img ? `<img src='${E(img)}' alt='' loading='lazy' onerror='this.remove()'>` : ''}</div>`;
  }

  function pintarLista() {
    const lista = L.filtrar(D.p, st);
    $('bc-cont').textContent = lista.length + (lista.length === 1 ? ' arquivo encontrado' : ' arquivos encontrados');
    // roving tabindex (padrão listbox): só um item entra na ordem do Tab; ↑/↓ navegam; F favorita
    const focavel = lista.some(function (p) { return p.id === st.sel; }) ? st.sel : (lista[0] || {}).id;
    $('bc-itens').innerHTML = lista.map(function (p) {
      const sel = p.id === st.sel;
      const fav = st.favoritos.indexOf(p.id) >= 0;
      return `<li class='bc-item fx-${E(p.f)}${sel ? ' bc-sel' : ''}' role='option' aria-selected='${sel}' tabindex='${p.id === focavel ? 0 : -1}' data-id='${p.id}'>
        ${retrato(p, 'bc-mini')}<span class='bc-in'><b>${E(p.n)}</b><small>${E((arq[p.a] || {}).s)} · ${E(p.al)}</small></span>
        <button type='button' tabindex='-1' class='bc-estrela${fav ? ' bc-on' : ''}' data-fav='${p.id}' aria-pressed='${fav}' aria-label='Favoritar ${E(p.n)} (tecla F)'>${fav ? '★' : '☆'}</button></li>`;
    }).join('') || `<li class='bc-vazio'>Nenhum arquivo com esses filtros.</li>`;
    const ativo = $('bc-itens').querySelector('.bc-sel');
    if (ativo && ativo.scrollIntoView) ativo.scrollIntoView({ block: 'nearest' });
  }

  function radar(s) {
    const R = 74, C = 100;
    const grade = [0.25, 0.5, 0.75, 1].map(function (k) {
      return `<polygon class='bc-grade' points='${L.pontosRadar([100, 100, 100, 100, 100, 100], R * k, C, C).map(function (q) { return q.join(','); }).join(' ')}'/>`;
    }).join('');
    const eixos = L.pontosRadar([100, 100, 100, 100, 100, 100], R, C, C);
    const rot = L.pontosRadar([100, 100, 100, 100, 100, 100], R + 16, C, C);
    return `<svg viewBox='0 0 200 200' class='bc-radar' role='img' aria-label='Atributos: ${s.map(function (v, i) { return STATS[i] + ' ' + v; }).join(', ')}'>
      ${grade}${eixos.map(function (q) { return `<line class='bc-eixo' x1='${C}' y1='${C}' x2='${q[0]}' y2='${q[1]}'/>`; }).join('')}
      <polygon class='bc-area' points='${L.pontosRadar(s, R, C, C).map(function (q) { return q.join(','); }).join(' ')}'/>
      ${rot.map(function (q, i) { return `<text x='${q[0]}' y='${q[1]}' class='bc-rot'>${STATS[i].slice(0, 3).toUpperCase()}</text>`; }).join('')}
    </svg>`;
  }

  function pintarFicha() {
    const p = porId[st.sel];
    const v = versao[p.v];
    const a = arq[p.a];
    const am = L.ameaca(v.s);
    const totalAp = p.ap.reduce(function (x, y) { return x + y; }, 0);
    raiz.className = 'bc fx-' + p.f;
    $('bc-ficha').innerHTML =
      `<div class='bc-card bc-glitch'>
        <span class='bc-num' aria-hidden='true'>${L.numeroArquivo(p.id)}</span>
        <h1 class='bc-nome'>${E(p.n)}</h1>
        <p class='bc-sub'>${E(p.c && p.c !== p.n ? p.c + ' · ' : '')}${E(p.ci)}</p>
        <div class='bc-chips'>
          <span class='bc-chip'>${E(era[p.er].n)}</span><span class='bc-chip'>${E(p.me)} · ${p.ano}</span>
          <span class='bc-chip bc-amea-${am.nivel.toLowerCase()}'>Ameaça ${am.nivel}</span>
          <span class='bc-chip' style='border-color:${E(a.c)}'>${E(a.s)} · ${E(a.n)}</span>
          <span class='bc-chip'>${E(p.al)}</span>
        </div>
        <div class='bc-corpo'>
          ${retrato(p, 'bc-foto')}
          <div class='bc-radar-box'>${radar(v.s)}
            <div class='bc-barras'>${v.s.map(function (x, i) {
              return `<div class='bc-b'><span>${STATS[i]}</span><i><em style='width:${x}%'></em></i><b>${x}</b></div>`;
            }).join('')}<div class='bc-total'>Índice de Ameaça <b>${am.valor}</b></div></div>
          </div>
        </div>
        <div class='bc-mini3'>
          <div><b>${totalAp}</b><span>aparições catalogadas</span></div>
          <div><b>${p.gr}</b><span>ligações na rede</span></div>
          <div><b>${p.ano}</b><span>ano de estreia</span></div>
        </div>
        <p class='bc-estreia'><span>Primeira aparição</span> ${E(p.e)}<br><span>Criadores</span> ${E(p.cr)}</p>
      </div>`;

    const vt = L.vantagens(D.m, p.a);
    const chips = function (ids, mult) {
      return ids.filter(function (id) { return arq[id]; }).map(function (id) { return `<span class='bc-chip' style='border-color:${E(arq[id].c)}'>${E(arq[id].s)} <b>${mult}</b></span>`; }).join('') || `<span class='bc-nada'>—</span>`;
    };
    const rels = L.agruparRelacoes(L.relacoesDe(D.rel, p.id)).slice(0, 9);
    const maxAp = Math.max.apply(null, p.ap.concat([1]));
    const afs = D.af.filter(function (x) { return p.af.indexOf(x.id) >= 0; }).map(function (x) { return E(x.n); });
    $('bc-lado').innerHTML =
      `<section class='bc-box'><h2>Arquétipo · ${E(a.n)}</h2><p class='bc-just'>${E(p.j)}</p>
        <div class='bc-vt'><span>Forte contra ${vt.forte.length}</span>${chips(vt.forte, '×2 ↑')}</div>
        <div class='bc-vt'><span>Vulnerável a ${vt.vulneravel.length}</span>${chips(vt.vulneravel, '×2 ↓')}</div>
        <div class='bc-vt'><span>Resiste a ${vt.resiste.length}</span>${chips(vt.resiste, '×½')}</div></section>
      <section class='bc-box'><h2>Rede de relações</h2>
        ${rels.filter(function (r) { return porId[r.outro]; }).map(function (r) {
          const o = porId[r.outro];
          return `<button type='button' class='bc-rel' data-id='${o.id}' aria-label='Abrir ${E(o.n)}: ${E(r.rotulos.join(', '))}'><i style='background:${COR_REL[r.tipos[0]] || '#7d8794'}'></i>${E(o.n)}<small>${E(r.rotulos.join(' · '))}</small></button>`;
        }).join('') || `<span class='bc-nada'>Sem relações catalogadas no Wikidata.</span>`}
        ${afs.length ? `<p class='bc-afs'>${afs.join(' · ')}</p>` : ''}</section>
      <section class='bc-box'><h2>Aparições por mídia</h2>
        ${D.md.map(function (m, i) {
          return `<div class='bc-b'><span>${E(m)}</span><i><em style='width:${(100 * p.ap[i]) / maxAp}%'></em></i><b>${p.ap[i]}</b></div>`;
        }).join('')}</section>`;
    particulas(p.f);
  }

  function particulas(f) {
    const box = raiz.querySelector('.bc-part');
    const chars = PARTICULAS[f];
    if (!chars || (G.matchMedia && G.matchMedia('(prefers-reduced-motion: reduce)').matches)) { box.innerHTML = ''; return; }
    let h = '';
    for (let i = 0; i < 18; i++) {
      const ch = chars[i % chars.length];
      h += `<span style='left:${(i * 53) % 100}%;animation-delay:${((i * 0.7) % 6).toFixed(1)}s;animation-duration:${(6 + (i % 5)).toFixed(0)}s'>${ch}</span>`;
    }
    box.innerHTML = h;
  }

  // falha de render vira aviso na página (o visual não tem console) em vez de coluna vazia
  function seguro(nome, fn) {
    try {
      fn();
    } catch (e) {
      const onde = String((e && e.stack) || '').split(String.fromCharCode(10)).slice(0, 3).join(' | ');
      const msg = `<div class='bc-erro' role='alert'>Erro ao montar ${nome}: ${E(e && e.message)}<br>${E(onde)}</div>`;
      if (nome === 'lista') {
        $('bc-itens').innerHTML = msg;
      } else {
        $('bc-ficha').innerHTML = msg; // nunca deixa a ficha anterior visível com dados de outro personagem
        $('bc-lado').innerHTML = '';
      }
    }
  }

  function selecionar(id, focar) {
    if (!porId[id] || id === st.sel) return;
    st.sel = id;
    seguro('lista', pintarLista);
    seguro('ficha', pintarFicha);
    // mantém ↑/↓ funcionando depois de clicar numa relação (o botão clicado some no redesenho)
    if (focar) {
      const item = $('bc-itens').querySelector('.bc-sel');
      if (item) item.focus({ preventScroll: true }); else raiz.focus({ preventScroll: true });
    }
  }

  raiz.addEventListener('click', function (ev) {
    const fav = ev.target.closest('[data-fav]');
    if (fav) {
      alternarFavorito(+fav.getAttribute('data-fav'));
      return;
    }
    const alvo = ev.target.closest('[data-id]');
    if (alvo) selecionar(+alvo.getAttribute('data-id'), true);
    if (ev.target.id === 'bc-fav') {
      st.fav = !st.fav;
      pintarBotaoFav();
      pintarLista();
    }
  });
  function alternarFavorito(id) {
    const k = st.favoritos.indexOf(id);
    if (k >= 0) st.favoritos.splice(k, 1); else st.favoritos.push(id);
    pintarLista();
  }
  function pintarBotaoFav() {
    const b = $('bc-fav');
    b.textContent = st.fav ? '★' : '☆';
    b.setAttribute('aria-pressed', String(st.fav));
  }
  $('bc-busca').addEventListener('input', function (ev) { st.busca = ev.target.value; pintarLista(); });
  $('bc-alin').addEventListener('change', function (ev) { st.alin = ev.target.value; pintarLista(); });
  $('bc-afil').addEventListener('change', function (ev) { st.afil = +ev.target.value; pintarLista(); });
  $('bc-era').addEventListener('change', function (ev) { st.era = +ev.target.value; pintarLista(); });
  raiz.addEventListener('keydown', function (ev) {
    const tag = ev.target.tagName;
    // Enter/Espaço num item da lista seleciona; ↑/↓ navegam — exceto dentro de um <select> (mudaria o filtro)
    const noItem = ev.target.classList && ev.target.classList.contains('bc-item');
    if ((ev.key === 'Enter' || ev.key === ' ') && noItem) {
      ev.preventDefault();
      selecionar(+ev.target.getAttribute('data-id'), true);
      return;
    }
    if ((ev.key === 'f' || ev.key === 'F') && noItem) {
      ev.preventDefault();
      alternarFavorito(+ev.target.getAttribute('data-id'));
      // com 'Só favoritos', desfavoritar tira o item da lista: o foco vai para o item focável restante ou a raiz
      const item = $('bc-itens').querySelector(`[data-id='${ev.target.getAttribute('data-id')}']`) ||
        $('bc-itens').querySelector(`[tabindex='0']`);
      (item || raiz).focus({ preventScroll: true });
      return;
    }
    if ((ev.key !== 'ArrowDown' && ev.key !== 'ArrowUp') || tag === 'SELECT' || tag === 'TEXTAREA') return;
    const lista = L.filtrar(D.p, st);
    const i = lista.findIndex(function (p) { return p.id === st.sel; });
    const j = Math.max(0, Math.min(lista.length - 1, i + (ev.key === 'ArrowDown' ? 1 : -1)));
    if (lista[j]) { ev.preventDefault(); selecionar(lista[j].id, tag !== 'INPUT'); }
  });
  pintarBotaoFav();

  seguro('lista', pintarLista);
  seguro('ficha', pintarFicha);
})(typeof window !== 'undefined' ? window : globalThis);
