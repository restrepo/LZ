/* Scales the fixed lesson canvas to the 19:9 stage, and switches the chrome
   to light colours on accent-field posters. */
(function(){
  const esc = document.getElementById('escenario'), lz = document.getElementById('lienzo');
  if (!esc || !lz) return;
  const ancho = lz.offsetWidth || %%WIDTH%%;
  const ajusta = () => { lz.style.transform = 'scale(' + (esc.clientWidth / ancho) + ')'; };
  if (window.ResizeObserver) new ResizeObserver(ajusta).observe(esc);
  addEventListener('resize', ajusta);
  ajusta();
  document.addEventListener('diapositiva', () => {
    const d = lz.querySelector('section.activa');
    esc.classList.toggle('en-poster', !!(d && d.classList.contains('poster')));
  });
})();
