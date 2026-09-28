
'use strict';
/* clase-slides core v1.3, adapted to walk #lienzo > section (slides and
   section posters) and to also emit 'slidechange' and data-deck-active,
   which the lesson's own modules use. */
/* ═══════════════════════════════════════════════════════════════════════
   CORE v1.3 — navigation engine: auto-generated section menu, steps
   (fragments), progress line, keyboard shortcuts, #/n hash, idle dimming,
   pinch zoom in full screen.
   Emits 'diapositiva' on every slide or step change (animations use it to
   pause off-screen) and 'slidechange' on every slide change.
   Space/Enter on buttons, links or selects does not navigate. No swipe
   navigation (it clashed with zoom and touch scrolling).
   ═══════════════════════════════════════════════════════════════════════ */
(function(){
  const esc  = document.getElementById('escenario');
  const dps  = Array.from(document.querySelectorAll('#lienzo > section'));
  const N    = dps.length;
  const frags  = dps.map(d => Array.from(d.querySelectorAll('.frag')));
  const vistos = dps.map(() => 0);
  let i = 0;

  const menu = document.getElementById('menu');
  const recta = document.getElementById('recta');
  const lleno = document.getElementById('recta-lleno');
  const contador = document.getElementById('contador');
  const secciones = [];
  dps.forEach((d, k) => {
    const s = d.dataset.seccion || '—';
    if (!secciones.length || secciones[secciones.length - 1].nombre !== s)
      secciones.push({ nombre: s, inicio: k });
  });
  const botones = secciones.map(sec => {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = sec.nombre;
    b.dataset.seccion = sec.nombre;
    b.addEventListener('click', () => irA(sec.inicio, false));
    menu.appendChild(b);
    if (sec.inicio > 0) {
      const t = document.createElement('div');
      t.className = 'tick';
      t.style.left = (sec.inicio / N * 100) + '%';
      recta.appendChild(t);
    }
    return b;
  });

  function pinta(){
    const previo = dps.findIndex(d => d.hasAttribute('data-deck-active'));
    dps.forEach((d, k) => {
      const on = (k === i);
      d.classList.toggle('activa', on);
      if (on) d.setAttribute('data-deck-active', ''); else d.removeAttribute('data-deck-active');
      d.setAttribute('aria-hidden', on ? 'false' : 'true');
      d.inert = !on;
    });
    frags[i].forEach((f, k) => f.classList.toggle('frag-on', k < vistos[i]));
    const sec = dps[i].dataset.seccion;
    botones.forEach(b => {
      const cur = (b.dataset.seccion === sec);
      b.classList.toggle('actual', cur);
      if (cur) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current');
    });
    esc.classList.toggle('sin-pasos', frags[i].length === 0 && dps[i].id !== 'dp-hero');
    contador.textContent = String(i + 1);          /* current slide only; the total goes in data-total */
    contador.dataset.total = N;
    lleno.style.width = ((i + 1) / N * 100) + '%';
    history.replaceState(null, '', '#/' + (i + 1));
    if (previo !== i) {
      if (document.activeElement && document.activeElement !== document.body && !document.activeElement.closest('.barra, .flecha, .pie')) document.activeElement.blur();
      document.dispatchEvent(new CustomEvent('slidechange', { detail: { index: i, previousIndex: previo, slide: dps[i], reason: 'nucleo' } }));
    }
    document.dispatchEvent(new CustomEvent('diapositiva', { detail: { i: i, id: dps[i].id || '' } }));
  }
  function irA(n, todosLosFrag){
    i = Math.max(0, Math.min(N - 1, n));
    vistos[i] = todosLosFrag ? frags[i].length : 0;
    pinta();
  }
  function sig(){
    if (vistos[i] < frags[i].length) { vistos[i]++; pinta(); }
    else if (i < N - 1) { i++; vistos[i] = 0; pinta(); }
  }
  function ant(){
    if (vistos[i] > 0) { vistos[i]--; pinta(); }
    else if (i > 0) { i--; vistos[i] = frags[i].length; pinta(); }
  }
  /* ← → change slide WITHOUT walking the steps (that is ↓ ↑);
     space keeps the classic step-by-step advance. */
  function sigDp(){ if (i < N - 1) { i++; vistos[i] = 0; pinta(); } }
  function antDp(){ if (i > 0) { i--; vistos[i] = frags[i].length; pinta(); } }

  document.getElementById('btn-sig').addEventListener('click', sigDp);
  document.getElementById('btn-ant').addEventListener('click', antDp);
  document.getElementById('btn-fs').addEventListener('click', pantallaCompleta);
  /* ↑ ↓ buttons dispatch the same keys, so they also drive animation
     phases that listen for ArrowUp/ArrowDown. */
  const teclaVert = k => dispatchEvent(new KeyboardEvent('keydown', { key: k }));
  document.querySelectorAll('.flecha.aba').forEach(b => b.addEventListener('click', () => teclaVert('ArrowDown')));
  document.querySelectorAll('.flecha.arr').forEach(b => b.addEventListener('click', () => teclaVert('ArrowUp')));
  function pantallaCompleta(){
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen().catch(() => {});
  }

  /* Touch zoom in full screen. Mobile browsers disable native pinch inside
     the Fullscreen API, so it is emulated: two fingers zoom, one finger pans
     while zoomed, and everything resets on exit. */
  (() => {
    const esc = document.getElementById('escenario');
    let s = 1, tx = 0, ty = 0, pinch = null, pan = null, base = null;
    window.__zoomActivo = () => s > 1.001 || pinch !== null;
    const dist = t => Math.hypot(t[0].clientX - t[1].clientX, t[0].clientY - t[1].clientY);
    const mid  = t => ({ x: (t[0].clientX + t[1].clientX) / 2, y: (t[0].clientY + t[1].clientY) / 2 });
    const mideBase = () => {
      const r = esc.getBoundingClientRect();
      base = { L0: r.left - tx, T0: r.top - ty, W: r.width / s, H: r.height / s };
    };
    const clampPan = () => {
      const vw = innerWidth, vh = innerHeight, sw = base.W * s, sh = base.H * s;
      tx = sw <= vw + 1 ? (vw - sw) / 2 - base.L0 : Math.min(-base.L0, Math.max(vw - sw - base.L0, tx));
      ty = sh <= vh + 1 ? (vh - sh) / 2 - base.T0 : Math.min(-base.T0, Math.max(vh - sh - base.T0, ty));
    };
    const aplica = () => {
      esc.style.transformOrigin = '0 0';
      esc.style.transform = s > 1.001 ? `translate(${tx}px,${ty}px) scale(${s})` : '';
    };
    document.addEventListener('touchstart', e => {
      if (!document.fullscreenElement) return;
      if (e.touches.length === 2) {
        mideBase();
        pinch = { d: dist(e.touches), m: mid(e.touches), s, tx, ty };
        pan = null;
        e.preventDefault();
      } else if (e.touches.length === 1 && s > 1.001) {
        const t = e.target;
        if (t instanceof Element && t.closest('input, button, a, summary, [data-cp]')) return;
        mideBase();
        pan = { x: e.touches[0].clientX, y: e.touches[0].clientY, tx, ty, moved: false };
      }
    }, { passive: false, capture: true });
    document.addEventListener('touchmove', e => {
      if (!document.fullscreenElement) return;
      if (pinch && e.touches.length === 2) {
        e.preventDefault();
        const ns = Math.min(5, Math.max(1, pinch.s * dist(e.touches) / pinch.d));
        const m = mid(e.touches), k = ns / pinch.s;
        tx = m.x - (pinch.m.x - pinch.tx) * k;
        ty = m.y - (pinch.m.y - pinch.ty) * k;
        s = ns; clampPan(); aplica();
      } else if (pan && e.touches.length === 1) {
        const dx = e.touches[0].clientX - pan.x, dy = e.touches[0].clientY - pan.y;
        if (!pan.moved && Math.abs(dx) + Math.abs(dy) > 6) pan.moved = true;
        if (pan.moved) { e.preventDefault(); tx = pan.tx + dx; ty = pan.ty + dy; clampPan(); aplica(); }
      }
    }, { passive: false, capture: true });
    document.addEventListener('touchend', e => {
      if (e.touches.length < 2) pinch = null;
      if (e.touches.length === 0) pan = null;
    }, true);
    document.addEventListener('fullscreenchange', () => {
      if (!document.fullscreenElement) { s = 1; tx = ty = 0; aplica(); }
    });
  })();

  addEventListener('keydown', e => {
    if (e.target instanceof Element && e.target.matches('input, textarea, select')) return;
    if ((e.key === ' ' || e.key === 'Enter') && e.target instanceof Element && e.target.closest('button, a, summary')) return;
    switch (e.key) {
      case 'ArrowRight': case 'PageDown': e.preventDefault(); sigDp(); break;
      case ' ': e.preventDefault(); (e.shiftKey ? ant : sig)(); break;
      case 'ArrowLeft': case 'PageUp': e.preventDefault(); antDp(); break;
      /* ↓ ↑: steps within the slide — reveal or hide fragments.
         On an animated slide without fragments the phase control acts. */
      case 'ArrowDown': e.preventDefault(); if (vistos[i] < frags[i].length) { vistos[i]++; pinta(); } break;
      case 'ArrowUp':   e.preventDefault(); if (vistos[i] > 0) { vistos[i]--; pinta(); } break;
      case 'Home': e.preventDefault(); irA(0, false); break;
      case 'End':  e.preventDefault(); irA(N - 1, false); break;
      case 'f': case 'F': pantallaCompleta(); break;
    }
  });

  /* No swipe navigation: buttons and keyboard cover it, and the gesture
     clashed with zoom and touch scrolling. */

  function deHash(){
    const m = location.hash.match(/^#\/(\d+)$/);
    if (m) { const n = parseInt(m[1], 10) - 1; if (n >= 0 && n < N && n !== i) irA(n, false); }
  }
  addEventListener('hashchange', deHash);

  let temporizador;
  function despierta(){
    esc.classList.remove('quieto');
    clearTimeout(temporizador);
    temporizador = setTimeout(() => esc.classList.add('quieto'), 3500);
  }
  ['pointermove', 'pointerdown', 'keydown'].forEach(ev => addEventListener(ev, despierta));

  const m0 = location.hash.match(/^#\/(\d+)$/);
  if (m0) { const n = parseInt(m0[1], 10) - 1; if (n >= 0 && n < N) i = n; }
  pinta();
  despierta();
})();

