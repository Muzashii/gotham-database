// Lógica pura do Batcomputador (src/js/batcomputador.js) + contrato do objeto window.GOTHAM.
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const ler = (rel) => readFileSync(new URL(rel, import.meta.url), 'utf8');

function carregar() {
  const ctx = vm.createContext({ Math, String, Number, Array, Object });
  ctx.globalThis = ctx;
  vm.runInContext(ler('../../src/js/batcomputador.js'), ctx);
  return ctx.GOTHAM_BC;
}

function dados() {
  const ctx = vm.createContext({});
  ctx.window = ctx;
  vm.runInContext(ler('./fixtures/gotham.js'), ctx);
  return ctx.GOTHAM;
}

describe('batcomputador.js — lógica', () => {
  const L = carregar();

  it('escapa HTML, inclusive apóstrofo (Ra’s al Ghul em atributo)', () => {
    expect(L.esc(`Ra's <b>&`)).toBe('Ra&#39;s &lt;b&gt;&amp;');
    expect(L.esc(null)).toBe('');
  });

  it('filtra por busca sem acento, alinhamento, afiliação, era e favoritos', () => {
    const p = [
      { id: 1, n: 'Batman', c: 'Batman', ci: 'Bruce Wayne', al: 'Herói', af: [1, 6], er: 1 },
      { id: 41, n: `Ra's al Ghul`, c: '', ci: `Ra's al Ghul`, al: 'Vilão', af: [2, 4], er: 3 },
      { id: 7, n: 'Oráculo', c: 'Batgirl', ci: 'Barbara Gordon', al: 'Herói', af: [1, 5], er: 2 },
    ];
    const ids = (f) => L.filtrar(p, f).map((x) => x.id);
    expect(ids({ busca: 'oraculo' })).toEqual([7]);
    expect(ids({ busca: 'WAYNE' })).toEqual([1]);
    expect(ids({ alin: 'Vilão' })).toEqual([41]);
    expect(ids({ afil: 1 })).toEqual([1, 7]);
    expect(ids({ era: 3 })).toEqual([41]);
    expect(ids({ fav: true, favoritos: [7] })).toEqual([7]);
    expect(ids({})).toEqual([1, 41, 7]);
  });

  it('índice de ameaça é a média arredondada com nível por faixa', () => {
    expect(L.ameaca([100, 26, 27, 50, 47, 100])).toEqual({ valor: 58, nivel: 'Alto' });
    expect(L.ameaca([10, 10, 10, 10, 10, 10]).nivel).toBe('Baixo');
    expect(L.ameaca([90, 90, 90, 90, 90, 90]).nivel).toBe('Extremo');
  });

  it('radar: 1º vértice no topo e valores limitados a 0–100', () => {
    const pts = L.pontosRadar([100, 0, 0, 0, 0, 150], 80, 100, 100);
    expect(pts[0]).toEqual([100, 20]);
    expect(pts[1]).toEqual([100, 100]);
    expect(Math.hypot(pts[5][0] - 100, pts[5][1] - 100)).toBeCloseTo(80, 0);
  });

  it('vantagens leem a linha (ataque) e a coluna (defesa) da matriz', () => {
    const m = [[1, 2, 0.5], [0.5, 1, 1], [2, 1, 1]];
    expect(L.vantagens(m, 1)).toEqual({ forte: [2], fraco: [3], vulneravel: [3], resiste: [2] });
  });

  it('relações nos dois sentidos, mais fortes primeiro, com rótulo de mentor/organização', () => {
    const rel = [[1, 3, 'mentor', 3], [1, 19, 'inimigo', 1], [16, 1, 'organização', 1]];
    const r = L.relacoesDe(rel, 1);
    expect(r.map((x) => x.outro)).toEqual([3, 16, 19]);
    expect(L.rotuloRelacao(r[0])).toBe('pupilo');
    expect(L.rotuloRelacao(r[1])).toBe('liderado por');
    expect(L.relacoesDe(rel, 3)[0]).toMatchObject({ outro: 1, sai: false });
    expect(L.rotuloRelacao(L.relacoesDe(rel, 3)[0])).toBe('mentor');
  });

  it('agrupa relações por pessoa: um item com todos os rótulos e o peso mais forte', () => {
    const rel = [[1, 6, 'família', 3], [1, 6, 'mentor', 3], [1, 6, 'organização', 1], [1, 19, 'inimigo', 1]];
    const g = L.agruparRelacoes(L.relacoesDe(rel, 1));
    expect(g.map((x) => x.outro)).toEqual([6, 19]);
    expect(g[0].rotulos).toEqual(['família', 'pupilo', 'lidera']);
    expect(g[0].peso).toBe(3);
  });

  it('número do arquivo com 3 dígitos', () => {
    expect(L.numeroArquivo(7)).toBe('#BAT-007');
  });

  it('não contém aspas duplas (quebrariam a string DAX)', () => {
    expect(ler('../../src/js/batcomputador.js').includes(String.fromCharCode(34))).toBe(false);
  });
});

describe('window.GOTHAM (fixture gerada de data/curated) segue contracts/js-data-schema.json', () => {
  const D = dados();
  const schema = JSON.parse(ler('../../contracts/js-data-schema.json'));

  it('tem todas as chaves de topo do contrato', () => {
    expect(Object.keys(D).sort()).toEqual(Object.keys(schema.properties).sort());
  });

  it('cada personagem tem os campos obrigatórios e referências válidas', () => {
    const req = schema.properties.p.items.required;
    const arqs = new Set(D.ar.map((a) => a.id));
    const eras = new Set(D.er.map((e) => e.id));
    const vers = new Set(D.v.map((v) => v.id));
    expect(D.p.length).toBe(50);
    for (const p of D.p) {
      for (const k of req) expect(p, `${p.n}.${k}`).toHaveProperty(k);
      expect(arqs.has(p.a)).toBe(true);
      expect(eras.has(p.er)).toBe(true);
      expect(vers.has(p.v)).toBe(true);
      expect(p.ap.length).toBe(D.md.length);
    }
  });

  it('matriz 8×8 com multiplicadores do contrato e versões com 6 atributos 0–100', () => {
    expect(D.m.length).toBe(D.ar.length);
    for (const linha of D.m) {
      expect(linha.length).toBe(D.ar.length);
      for (const x of linha) expect([0.5, 1, 2]).toContain(x);
    }
    for (const v of D.v) {
      expect(v.s.length).toBe(6);
      for (const x of v.s) expect(x >= 0 && x <= 100).toBe(true);
    }
  });

  it('relações apontam para personagens existentes', () => {
    const ids = new Set(D.p.map((p) => p.id));
    for (const [o, d] of D.rel) {
      expect(ids.has(o) && ids.has(d)).toBe(true);
    }
  });
});

describe('robustez com dados imperfeitos', () => {
  const L = carregar();
  it('vantagens não quebram com linha vazia na matriz (bug do membro em branco)', () => {
    const m = [[], [1, 2], [0.5, 1]];
    expect(() => L.vantagens(m, 1)).not.toThrow();
  });
});
