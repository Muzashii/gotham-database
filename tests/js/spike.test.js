// Lógica pura do spike (src/js/spike.js) executada fora do Power BI, em um contexto vm sem DOM.
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

function carregar() {
  const ctx = vm.createContext({ Math, Date, String });
  ctx.globalThis = ctx;
  vm.runInContext(readFileSync(new URL('../../src/js/spike.js', import.meta.url), 'utf8'), ctx);
  return ctx;
}

describe('spike.js', () => {
  it('sem DOM só expõe a lógica e cria o estado na window', () => {
    const G = carregar();
    expect(G.GOTHAM_STATE).toEqual({});
    expect(typeof G.GOTHAM_SPIKE.incrementar).toBe('function');
  });

  it('registra renders sem duplicar vias', () => {
    const L = carregar().GOTHAM_SPIKE;
    const st = L.novoEstado(0);
    L.registrarRender(st, 'script');
    L.registrarRender(st, 'script');
    L.registrarRender(st, 'onerror');
    expect(st.renders).toBe(3);
    expect(st.vias).toEqual(['script', 'onerror']);
  });

  it('incrementa o contador', () => {
    const L = carregar().GOTHAM_SPIKE;
    const st = L.novoEstado(0);
    expect(L.incrementar(st)).toBe(1);
    expect(L.incrementar(st)).toBe(2);
  });

  it('holofote fica entre 10% e 90% da largura', () => {
    const L = carregar().GOTHAM_SPIKE;
    for (let t = 0; t < 20000; t += 137) {
      const x = L.posicaoHolofote(t, 300);
      expect(x).toBeGreaterThanOrEqual(30);
      expect(x).toBeLessThanOrEqual(270);
    }
  });

  it('redesenho com DOM reaproveita o estado da window e não roda duas vezes no mesmo DOM', () => {
    // DOM falso mínimo: só o que spike.js usa; canvas sem getContext encerra antes do rAF
    const fonte = readFileSync(new URL('../../src/js/spike.js', import.meta.url), 'utf8');
    const novoDom = () => {
      const els = {};
      const el = (id) =>
        (els[id] = els[id] || { id, dataset: {}, textContent: '', className: '', ouvintes: [],
          addEventListener(_, fn) { this.ouvintes.push(fn); } });
      return { els, document: { currentScript: {}, getElementById: el } };
    };
    const G = vm.createContext({ Math, Date, String, cancelAnimationFrame() {} });
    G.globalThis = G;

    let dom = novoDom();
    G.document = dom.document;
    vm.runInContext(fonte, G);
    dom.els['gd-inc'].ouvintes[0]();
    dom.els['gd-inc'].ouvintes[0]();
    vm.runInContext(fonte, G); // mesmo DOM (ex.: onerror depois do script): ignorado
    expect(G.GOTHAM_STATE.spike.renders).toBe(1);

    dom = novoDom(); // visual redesenhado: DOM novo, window igual
    G.document = dom.document;
    vm.runInContext(fonte, G);
    expect(G.GOTHAM_STATE.spike.renders).toBe(2);
    expect(dom.els['gd-count'].textContent).toBe('2');
    expect(dom.els['gd-js-script'].textContent).toBe('ativo');
  });

  it('não contém aspas duplas', () => {
    const src = readFileSync(new URL('../../src/js/spike.js', import.meta.url), 'utf8');
    expect(src.includes(String.fromCharCode(34))).toBe(false);
  });
});
