
/*! SmartVizitka Sticky Video Widget — single-source version (one <video> moved between mini & modal) */
(function(){
  var s = document.currentScript;
  var cfg = {
    side: s.dataset.side || 'left',
    vertical: s.dataset.vertical || 'bottom',
    offsetX: +s.dataset.offsetX || 20,
    offsetY: +s.dataset.offsetY || 20,
    miniWidth: +s.dataset.miniWidth || 132,
    aspect: (s.dataset.aspect || '9:16').split(':').map(Number),
    srcMp4: s.dataset.srcMp4 || '',
    srcWebm: s.dataset.srcWebm || '',
    poster: s.dataset.poster || '',
    ctaText: s.dataset.ctaText || 'Подключиться бесплатно',
    ctaUrl: s.dataset.ctaUrl || '#',
    hideBelow: +(s.dataset.hideBelow || 0),
    autopause: (s.dataset.autopause || 'true') === 'true',
    zIndex: +s.dataset.zIndex || 60,
    hideOn: (function(){ try{ return JSON.parse(s.dataset.hideOn||'[]'); }catch(e){ return []; }})()
  };

  var path = location.pathname || '/';
  if (cfg.hideOn && cfg.hideOn.some(function(p){ return path.startsWith(p); })) return;

  function hiddenByWidth(){ return cfg.hideBelow && window.innerWidth < cfg.hideBelow; }

  var h = Math.round(cfg.miniWidth * (cfg.aspect[1]/cfg.aspect[0]));
  var css = `
  [data-svww]{position:fixed; inset:auto auto auto auto; width:${cfg.miniWidth}px; height:${h}px; z-index:${cfg.zIndex};}
  ${cfg.side==='right' ? `[data-svww]{ right:${cfg.offsetX}px; }` : `[data-svww]{ left:${cfg.offsetX}px; }`}
  ${cfg.vertical==='middle' ? `[data-svww]{ top:50%; transform:translateY(-50%);} ` : `[data-svww]{ bottom:${cfg.offsetY}px; }`}
  [data-svww]{ display:none; }
  [data-svww].on{ display:block; }
  [data-svww] .svw-card{position:relative; width:100%; height:100%; border:1px solid var(--line, #e6eaf3);
    border-radius:16px; box-shadow:var(--shadow, 0 8px 22px rgba(0,0,0,.08)); overflow:hidden; background:#000;}
  [data-svww] video.svw-media{width:100%; height:100%; object-fit:cover; display:block; background:#000;}
  /* [data-svww] .svw-ind{position:absolute; top:8px; ${cfg.side==='right'?'left:8px;':'right:8px;'} font-size:14px;
    background:rgba(0,0,0,.45); color:#fff; padding:4px 6px; border-radius:8px; pointer-events:none} */
  [data-svww] .svw-cta{position:absolute; left:8px; right:8px; bottom:8px; display:flex; align-items:center; justify-content:center;
    font:600 14px/1.1 Inter,system-ui,sans-serif; padding:10px 12px; border-radius:12px; text-decoration:none;
    color:#fff; background:linear-gradient(135deg,var(--primary,#6c5ce7),#9a83ff); box-shadow:0 10px 28px rgba(124,92,255,.35)}
  [data-svww] .svw-cta:focus{ outline:2px solid var(--primary,#6c5ce7); outline-offset:2px; }
  [data-svww] .svw-hit{position:absolute; inset:0; background:transparent; border:0; padding:0; cursor:pointer;}
  [data-svww] .svw-hit:focus{ outline:2px solid var(--accent,#00b894); outline-offset:-4px; }
  [data-svww] .svw-tip{position:absolute; ${cfg.side==='right'?'left:8px;':'right:8px;'} bottom:54px; background:var(--panel,#fff);
    color:var(--text,#1e2230); border:1px solid var(--line,#e6eaf3); border-radius:10px; padding:8px 10px; font-size:12px; box-shadow:var(--shadow,0 8px 22px rgba(0,0,0,.08)); opacity:0; transform:translateY(6px); transition:.25s;}
  [data-svww] .svw-card:hover .svw-tip{ opacity:1; transform:none; }
  @media (max-width:720px){
    [data-svww]{ width: min(${cfg.miniWidth}px, 35vw); height:auto; aspect-ratio:${cfg.aspect[0]} / ${cfg.aspect[1]}; ${cfg.vertical==='middle'?'top:unset; transform:none;':''}; bottom:${cfg.offsetY}px;}
  }
  .svw-modal{position:fixed; inset:0; z-index:${cfg.zIndex+1}; display:none;}
  .svw-modal.on{ display:block; }
  .svw-backdrop{position:absolute; inset:0; background:rgba(0,0,0,.6);}
  .svw-dialog{position:absolute; inset:0; display:grid; place-items:center; padding:20px;}
  .svw-box{width:${cfg.miniWidth * 2}px; background:var(--panel,#101729); border-radius:16px; border:1px solid var(--line,#1e2a44); box-shadow:var(--shadow, 0 12px 32px rgba(0,0,0,.35)); padding:16px; display:grid; gap:12px;}
  /* .svw-close{position:absolute; top:14px; right:16px; background:rgba(0,0,0,.45); color:#fff; border:0; width:36px; height:36px; border-radius:10px; cursor:pointer;} */
  .svw-player{width:100%; height:${cfg.miniWidth * 2 * (cfg.aspect[1]/cfg.aspect[0])}px; background:#000;}
  .svw-player video{width:100%; height:100%; display:block; object-fit:cover;}
  .svw-cta-modal{display:inline-flex; align-items:center; justify-content:center; padding:12px 16px; border-radius:12px;
    background:linear-gradient(135deg,var(--primary,#6c5ce7),#9a83ff); color:#fff; text-decoration:none; font-weight:800; font-size:15px;}
  @media (max-width:720px){
    .svw-box{width:min(${cfg.miniWidth * 2}px, 90vw);}
    .svw-player{height:auto; max-height:70vh;}
  }
  @media (prefers-reduced-motion: reduce){
    [data-svww] .svw-tip{ transition:none; }
  }`;
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  // Root mini container
  var root = document.createElement('div');
  root.setAttribute('data-svww','');
  root.setAttribute('role','button');
  root.setAttribute('tabindex','0');
  root.setAttribute('aria-label','Открыть видео о SmartVizitka');

  var card = document.createElement('div');
  card.className = 'svw-card';
  root.appendChild(card);

  // Single <video> element used everywhere
  var v = document.createElement('video');
  v.className = 'svw-media';
  v.muted = true;           // mini: no sound
  v.autoplay = true;        // mini: try autoplay
  v.loop = true;            // mini: loop teaser
  v.playsInline = true;
  v.setAttribute('playsinline','');
  v.setAttribute('preload','metadata');
  if (cfg.poster) v.poster = cfg.poster;
  if (cfg.srcWebm) { var sw = document.createElement('source'); sw.src = cfg.srcWebm; sw.type='video/webm'; v.appendChild(sw); }
  if (cfg.srcMp4) { var sm = document.createElement('source'); sm.src = cfg.srcMp4; sm.type='video/mp4'; v.appendChild(sm); }
  card.appendChild(v);

  // Mute indicator - УБРАН
  // var ind = document.createElement('div');
  // ind.className = 'svw-ind';
  // ind.textContent = '🔇';
  // card.appendChild(ind);

  // CTA mini
  var cta = document.createElement('a');
  cta.className = 'svw-cta';
  cta.href = cfg.ctaUrl;
  cta.target = '_self';
  cta.rel = 'noopener';
  cta.textContent = cfg.ctaText;
  cta.addEventListener('click', function(){ emit('cta_click', {place:'mini'}); });
  card.appendChild(cta);

  // Tooltip once per session
  var tipShown = sessionStorage.getItem('svw_tip') === '1';
  var tip = document.createElement('div');
  tip.className = 'svw-tip';
  tip.textContent = 'Нажмите, чтобы развернуть';
  if (!tipShown) card.appendChild(tip);

  // Invisible hit button
  var hit = document.createElement('button');
  hit.className = 'svw-hit';
  hit.setAttribute('aria-label','Открыть видео');
  hit.addEventListener('click', openModal);
  hit.addEventListener('keydown', function(e){
    if (e.code === 'Enter' || e.code === 'Space') { e.preventDefault(); openModal(); }
  });
  card.appendChild(hit);

  // Modal with same <video> re-parented
  var modal = document.createElement('div');
  modal.className = 'svw-modal';
  modal.setAttribute('role','dialog');
  modal.setAttribute('aria-modal','true');

  var backdrop = document.createElement('div'); backdrop.className = 'svw-backdrop';
  backdrop.addEventListener('click', closeModal);
  var dialog = document.createElement('div'); dialog.className = 'svw-dialog';
  var box = document.createElement('div'); box.className = 'svw-box';
  // var close = document.createElement('button'); close.className='svw-close'; close.setAttribute('aria-label','Закрыть'); close.innerHTML='✕';
  // close.addEventListener('click', closeModal);
  var player = document.createElement('div'); player.className='svw-player';

  // Placeholder to allow moving video back & forth
  // In modal we append the same <video> node into player.
  // In mini we append it back to card.
  // box.appendChild(close); // УБРАНА КНОПКА ЗАКРЫТИЯ
  box.appendChild(player);
  var cta2 = document.createElement('a'); cta2.className='svw-cta-modal'; cta2.href = cfg.ctaUrl; cta2.textContent = cfg.ctaText;
  cta2.addEventListener('click', function(){ emit('cta_click', {place:'modal'}); });
  box.appendChild(cta2);
  dialog.appendChild(box);
  modal.appendChild(backdrop);
  modal.appendChild(dialog);

  document.body.appendChild(root);
  document.body.appendChild(modal);

  // Visibility logic
  function updateVisibility(){
    if (hiddenByWidth()) { root.classList.remove('on'); pauseMini(); }
    else { root.classList.add('on'); }
  }
  updateVisibility();
  window.addEventListener('resize', updateVisibility);

  // Autopause for mini
  function pauseMini(){ if (!v.paused) v.pause(); }
  function playMini(){ v.play().catch(function(){}); }
  if (cfg.autopause){
    if ('IntersectionObserver' in window){
      var io = new IntersectionObserver(function(es){
        es.forEach(function(ent){ if (ent.isIntersecting) playMini(); else pauseMini(); });
      }, { threshold: 0.25 });
      io.observe(root);
    }
    document.addEventListener('visibilitychange', function(){
      if (document.hidden) pauseMini(); else playMini();
    });
  }

  // Analytics payloads
  var widgetId = 'svw_'+Math.random().toString(36).slice(2,7);
  var seen = {impr:false, viewable:false};
  function emit(ev, extra){
    var payload = Object.assign({
      event: ev,
      widget_id: widgetId,
      page_url: location.href,
      timestamp: Date.now(),
      session_id: (sessionStorage.getItem('svw_sid') || (function(){ var id='sid_'+Math.random().toString(36).slice(2); sessionStorage.setItem('svw_sid', id); return id; })()),
      variant: 'A',
      position: cfg.side + '-' + cfg.vertical
    }, extra||{});
    (window.dataLayer = window.dataLayer || []).push(payload);
    if (typeof window.SVWidget?.onEvent === 'function'){ try{ window.SVWidget.onEvent(payload); }catch(e){} }
  }
  if (!seen.impr){ seen.impr = true; emit('widget_impression'); }
  var viewTimer = null, visibleNow=false;
  var ro = new IntersectionObserver(function(es){
    es.forEach(function(e){
      var vbl = e.isIntersecting && !hiddenByWidth();
      if (visibleNow===vbl) return;
      visibleNow = vbl;
      if (vbl && !seen.viewable){
        clearTimeout(viewTimer);
        viewTimer = setTimeout(function(){ if (visibleNow){ seen.viewable=true; emit('widget_viewable'); } }, 1000);
      } else { clearTimeout(viewTimer); }
    });
  }, {threshold:0.2});
  ro.observe(root);

  if (!tipShown){
    setTimeout(function(){ if (tip){ tip.style.opacity='1'; tip.style.transform='none'; } }, 300);
    setTimeout(function(){ if (tip && tip.parentNode){ tip.parentNode.removeChild(tip); sessionStorage.setItem('svw_tip','1'); } }, 3000);
  }

  // Quartiles (tracked in modal where user really watches)
  var q25=false,q50=false,q75=false,q100=false;
  function resetQuartiles(){ q25=q50=q75=q100=false; }
  function onQuartiles(){
    var d = v.duration || 0; if (!d || !isFinite(d)) return;
    var t = v.currentTime || 0;
    if (!q25 && t >= d*0.25){ q25=true; emit('video_quartile_25'); }
    if (!q50 && t >= d*0.50){ q50=true; emit('video_quartile_50'); }
    if (!q75 && t >= d*0.75){ q75=true; emit('video_quartile_75'); }
    if (!q100 && t >= d*0.99){ q100=true; emit('video_quartile_100'); }
  }

  function openModal(){
    emit('widget_open');
    
    // Move the same <video> into modal
    player.appendChild(v);

    // Switch to "big" mode: sound + no controls + no loop + start from beginning
    v.muted = false;
    v.controls = false; // УБРАНЫ ЭЛЕМЕНТЫ ПЛЕЕРА
    v.loop = false;
    v.currentTime = 0; // ВИДЕО НАЧИНАЕТСЯ С НАЧАЛА

    // Play video from beginning
    var p = v.play();
    if (p && typeof p.then==='function'){ p.then(function(){ emit('sound_on'); emit('video_play',{mode:'modal'}); }).catch(function(){}); }

    // Focus/keys
    modal.classList.add('on');
    root.setAttribute('aria-expanded','true');
    // close.focus(); // УБРАНА КНОПКА ЗАКРЫТИЯ

    function key(e){
      if (e.key === 'Escape'){ e.preventDefault(); closeModal(); }
      if (e.key === 'Tab'){ trapFocus(e); }
    }
    modal.addEventListener('keydown', key);
    modal._onKey = key;

    // Track quartiles & pause/play
    resetQuartiles();
    v.addEventListener('timeupdate', onQuartiles);
    v.addEventListener('pause', onPause);
    v.addEventListener('play', onPlay);
  }

  function onPause(){ emit('video_pause',{mode:'modal'}); }
  function onPlay(){ emit('video_play',{mode:'modal'}); }

  function trapFocus(e){
    var focusables = modal.querySelectorAll('a[href],button:not([disabled]),video,[tabindex]:not([tabindex="-1"])');
    focusables = Array.prototype.filter.call(focusables, function(el){ return el.offsetParent !== null; });
    if (!focusables.length) return;
    var first = focusables[0], last = focusables[focusables.length-1];
    if (e.shiftKey && document.activeElement === first){ e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last){ e.preventDefault(); first.focus(); }
  }

  function closeModal(){
    // Remember state
    var wasPlaying = !v.paused && !v.ended;
    var time = v.currentTime || 0;

    // Stop events
    v.removeEventListener('timeupdate', onQuartiles);
    v.removeEventListener('pause', onPause);
    v.removeEventListener('play', onPlay);

    modal.classList.remove('on');
    root.setAttribute('aria-expanded','false');

    // Return the same <video> back to mini card
    card.insertBefore(v, card.firstChild);

    // Switch to "mini" mode: muted, loop, no controls
    v.controls = false;
    v.muted = true;
    v.loop = true;

    try { v.currentTime = time; } catch(e){}
    if (wasPlaying) { v.play().catch(function(){}); }

    // Focus back
    root.focus({preventScroll:true});
    emit('widget_close');
  }

  document.addEventListener('keydown', function(e){
    if (modal.classList.contains('on') && e.key==='Escape'){ closeModal(); }
  });

  // Expose minimal API
  window.SVWidget = window.SVWidget || {};
  window.SVWidget.open = openModal;
  window.SVWidget.close = closeModal;

  // Show widget after first frame
  v.addEventListener('loadeddata', function(){ root.classList.add('on'); }, {once:true});
  v.play().catch(function(){ /* poster-only until user clicks */ });
})();
