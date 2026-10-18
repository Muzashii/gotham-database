// F0 spike: prova que o visual executa JS e que o estado em window.GOTHAM_STATE
// sobrevive ao redesenho. PROIBIDO aspas duplas (quebram a string DAX).
(function (G) {
  const S = (G.GOTHAM_STATE = G.GOTHAM_STATE || {});
  const L = (G.GOTHAM_SPIKE = G.GOTHAM_SPIKE || {});

  // ---- lógica pura (testada em Node, tests/js/spike.test.js) ----
  L.novoEstado = function (agora) {
    return { contador: 0, renders: 0, vias: [], inicio: agora, raf: 0 };
  };
  L.registrarRender = function (st, via) {
    st.renders += 1;
    if (st.vias.indexOf(via) < 0) st.vias.push(via);
    return st;
  };
  L.incrementar = function (st) {
    st.contador += 1;
    return st.contador;
  };
  // varredura senoidal do holofote: x em [0,1 .. 0,9] da largura
  L.posicaoHolofote = function (t, largura) {
    return largura / 2 + Math.sin(t / 1400) * largura * 0.4;
  };
  L.formatarHora = function (ms) {
    const d = new Date(ms);
    const p = (n) => String(n).padStart(2, '0');
    return p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds());
  };

  // ---- renderização (só no navegador) ----
  const doc = G.document;
  if (!doc) return;
  const raiz = doc.getElementById('gd-spike');
  if (!raiz || raiz.dataset.gdRan) return; // já rodou neste DOM (script + onerror)
  raiz.dataset.gdRan = '1';

  const via = doc.currentScript ? 'script' : 'onerror';
  const st = (S.spike = S.spike || L.novoEstado(Date.now()));
  L.registrarRender(st, via);

  const $ = (id) => doc.getElementById(id);
  const marcar = (id, ok) => {
    const el = $(id);
    if (!el) return;
    el.textContent = ok ? 'ativo' : 'inativo';
    el.className = 'gd-v ' + (ok ? 'gd-ok' : 'gd-no');
  };

  function pintar() {
    marcar('gd-js-script', via === 'script');
    if (via === 'onerror') marcar('gd-js-img', true);
    $('gd-renders').textContent = String(st.renders);
    $('gd-count').textContent = String(st.contador);
    $('gd-desde').textContent = 'estado desde ' + L.formatarHora(st.inicio);
    const pl = $('gd-payload');
    $('gd-size').textContent = (pl ? pl.textContent.length : 0).toLocaleString('pt-BR') + ' recebidos';
  }

  $('gd-inc').addEventListener('click', () => {
    L.incrementar(st);
    pintar();
  });
  pintar();

  // holofote varrendo as nuvens; cancela o loop do render anterior para não duplicar
  if (st.raf) G.cancelAnimationFrame(st.raf);
  const cv = $('gd-sky');
  const ctx = cv && cv.getContext ? cv.getContext('2d') : null;
  if (!ctx) return;
  const calmo = G.matchMedia && G.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function quadro(t) {
    const w = (cv.width = cv.clientWidth || 320);
    const h = (cv.height = cv.clientHeight || 90);
    ctx.fillStyle = '#07090c';
    ctx.fillRect(0, 0, w, h);
    const x = L.posicaoHolofote(calmo ? 0 : t, w);
    const g = ctx.createLinearGradient(w / 2, h, x, 0);
    g.addColorStop(0, 'rgba(245,197,24,0.45)');
    g.addColorStop(1, 'rgba(245,197,24,0.02)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.moveTo(w / 2 - 6, h);
    ctx.lineTo(x - 40, 0);
    ctx.lineTo(x + 40, 0);
    ctx.lineTo(w / 2 + 6, h);
    ctx.fill();
    ctx.fillStyle = 'rgba(125,135,148,0.18)';
    for (let i = 0; i < 6; i++) {
      const cx = ((i * 97 + (calmo ? 0 : t / 60)) % (w + 120)) - 60;
      ctx.beginPath();
      ctx.ellipse(cx, 18 + (i % 3) * 10, 50, 10, 0, 0, Math.PI * 2);
      ctx.fill();
    }
    if (!calmo && raiz.isConnected) st.raf = G.requestAnimationFrame(quadro);
  }
  st.raf = G.requestAnimationFrame(quadro);
})(typeof window !== 'undefined' ? window : globalThis);
