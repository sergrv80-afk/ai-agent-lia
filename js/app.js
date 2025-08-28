// ==== Theme toggle ====
(function(){
  var btn=document.getElementById('themeToggle');
  var html=document.documentElement;
  function setTheme(t){ html.setAttribute('data-theme',t); try{localStorage.setItem('theme',t)}catch(e){}; btn.textContent = t==='dark'?'🌙':'☀️'; }
  btn?.addEventListener('click',function(){ setTheme((html.getAttribute('data-theme')||'dark')==='dark'?'light':'dark'); });
  setTheme(html.getAttribute('data-theme')|| (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark':'light'));
})();

// ==== Burger menu (mobile) ====
(function(){
  var b=document.getElementById('burger');
  var p=document.getElementById('mobilePanel');
  if(!b||!p) return;
  
  b.addEventListener('click',function(){
    var open=p.classList.toggle('open');
    b.classList.toggle('active', open);
    b.setAttribute('aria-expanded',open?'true':'false');
    
    // Блокируем скролл при открытом меню
    if(open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  });
  
  // Закрываем меню при клике на ссылку
  p.addEventListener('click',function(e){ 
    if(e.target.tagName==='A'){ 
      p.classList.remove('open'); 
      b.classList.remove('active');
      b.setAttribute('aria-expanded','false');
      document.body.style.overflow = '';
    } 
  });
  
  // Закрываем меню при клике вне его
  document.addEventListener('click', function(e) {
    if (!b.contains(e.target) && !p.contains(e.target) && p.classList.contains('open')) {
      p.classList.remove('open');
      b.classList.remove('active');
      b.setAttribute('aria-expanded','false');
      document.body.style.overflow = '';
    }
  });
})();

// ==== Smooth scroll ====
document.querySelectorAll('a[href^="#"]').forEach(function(link){
  link.addEventListener('click',function(e){
    var id=this.getAttribute('href'); if(!id||id==='#') return;
    var t=document.querySelector(id); if(t){ e.preventDefault(); t.scrollIntoView({behavior:'smooth'}); }
  });
});

// ==== Reveal on scroll ====
(function(){
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var els = document.querySelectorAll('[data-reveal]');
  if(reduce){ els.forEach(function(el){ el.classList.add('visible'); }); return; }
  if(!('IntersectionObserver' in window)){ els.forEach(function(el){ el.classList.add('visible'); }); return; }
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(ent){ if(ent.isIntersecting){ ent.target.classList.add('visible'); io.unobserve(ent.target); } });
  }, {threshold:0.18});
  els.forEach(function(el){ io.observe(el); });
})();

// ==== Typing effect in hero ====
(function(){
  var words=["работает 24/7","записывает клиентов","автоматизирует","приносит прибыль","анализирует"];
  var i=0,j=0,del=false,el=document.getElementById('typed'); if(!el) return;
  function step(){
    var w=words[i];
    if(!del){ j++; el.textContent=w.slice(0,j); if(j===w.length){ del=true; setTimeout(step,900); return; } }
    else{ j--; el.textContent=w.slice(0,j); if(j===0){ del=false; i=(i+1)%words.length; } }
    setTimeout(step, del?45:85);
  }
  step();
})();

// ==== Reviews carousel ====
(function(){
  var track=document.getElementById('track'), dots=document.getElementById('dots');
  if(!track||!dots) return;
  
  var slides=[].slice.call(track.children);
  var currentIndex = 0;
  
  // Создаем точки навигации
  dots.innerHTML='';
  slides.forEach(function(_,idx){ 
    var d=document.createElement('div'); 
    d.className='dot'+(idx===0?' active':''); 
    d.addEventListener('click',function(){ goToSlide(idx); }); 
    dots.appendChild(d); 
  });
  
  // Функция перехода к слайду
  function goToSlide(index) {
    currentIndex = index;
    var cardWidth = getCardWidth();
    track.style.transform='translateX('+(-index*cardWidth)+'px)';
    
    // Обновляем активную точку
    [].forEach.call(dots.children,function(d,i){ 
      d.classList.toggle('active', i===index); 
    });
    
    resetTimer();
  }
  
  // Получаем ширину карточки с учетом отступов
  function getCardWidth() {
    var slide = slides[0];
    var styles = getComputedStyle(slide);
    return slide.offsetWidth + parseFloat(styles.marginRight || 0) + 20; // 20px gap
  }
  
  // Следующий слайд
  function nextSlide() {
    var nextIndex = (currentIndex + 1) % slides.length;
    goToSlide(nextIndex);
  }
  
  // Предыдущий слайд
  function prevSlide() {
    var prevIndex = (currentIndex - 1 + slides.length) % slides.length;
    goToSlide(prevIndex);
  }
  
  // Автопрокрутка
  var timer = null;
  function resetTimer() {
    clearInterval(timer);
    timer = setInterval(nextSlide, 5000); // 5 секунд
  }
  
  // Запускаем автопрокрутку
  resetTimer();
  
  // Обработка изменения размера окна
  addEventListener('resize', function() {
    goToSlide(currentIndex);
  });
  
  // Добавляем клавиатурное управление
  document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowLeft') {
      prevSlide();
    } else if (e.key === 'ArrowRight') {
      nextSlide();
    }
  });
  
  // Добавляем свайп для мобильных устройств
  var startX = 0;
  var endX = 0;
  
  track.addEventListener('touchstart', function(e) {
    startX = e.touches[0].clientX;
  });
  
  track.addEventListener('touchend', function(e) {
    endX = e.changedTouches[0].clientX;
    var diff = startX - endX;
    
    if (Math.abs(diff) > 50) { // Минимальное расстояние для свайпа
      if (diff > 0) {
        nextSlide(); // Свайп влево
      } else {
        prevSlide(); // Свайп вправо
      }
    }
  });
})();

// ==== Animate hero bars ====
(function(){
  var bars=document.querySelectorAll('#bars rect'); if(!bars.length) return;
  bars.forEach(function(b,k){ var h=+b.getAttribute('height'); b.setAttribute('height',0); b.setAttribute('y',120);
    setTimeout(function(){ b.style.transition='height .7s ease,y .7s ease'; b.setAttribute('height',h); b.setAttribute('y',120-h); },300+k*120);
  });
})();

// ==== Subtle parallax on hero phone ====
(function(){
  var phone=document.querySelector('.hero .phone'); if(!phone) return;
  var rect=null; function updateRect(){ rect=phone.getBoundingClientRect(); }
  updateRect(); addEventListener('resize',updateRect);
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; if(reduce) return;
  window.addEventListener('mousemove',function(e){ if(!rect) return; var cx=rect.left+rect.width/2, cy=rect.top+rect.height/2; var dx=(e.clientX-cx)/rect.width, dy=(e.clientY-cy)/rect.height; phone.style.transform='rotateX('+(-dy*4)+'deg) rotateY('+(dx*4)+'deg) translateZ(0)'; });
  phone.addEventListener('mouseleave',function(){ phone.style.transform='none'; });
})();

// ==== Active navigation tracking ====
(function(){
  var navLinks = document.querySelectorAll('.menu a, .mobile-panel a');
  var sections = document.querySelectorAll('section[id]');
  
  function updateActiveNav() {
    var scrollPos = window.scrollY + 100;
    
    sections.forEach(function(section) {
      var sectionTop = section.offsetTop;
      var sectionHeight = section.offsetHeight;
      var sectionId = section.getAttribute('id');
      
      if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
        // Убираем активный класс у всех ссылок
        navLinks.forEach(function(link) {
          link.classList.remove('active');
        });
        
        // Добавляем активный класс к текущей ссылке
        var activeLink = document.querySelector('.menu a[href="#' + sectionId + '"], .mobile-panel a[href="#' + sectionId + '"]');
        if (activeLink) {
          activeLink.classList.add('active');
        }
      }
    });
  }
  
  // Обновляем активную ссылку при скролле
  window.addEventListener('scroll', updateActiveNav);
  
  // Инициализируем активное состояние
  updateActiveNav();
})();

// ==== Header scroll animation ====
(function(){
  var header = document.querySelector('header');
  var lastScrollTop = 0;
  
  function handleScroll() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
    
    lastScrollTop = scrollTop;
  }
  
  window.addEventListener('scroll', handleScroll);
  handleScroll(); // Инициализация
})();

// ==== Industry cards interaction ====
(function(){
  var industryCards = document.querySelectorAll('.industry-card');
  
  industryCards.forEach(function(card) {
    card.addEventListener('click', function() {
      // Убираем активный класс у всех карточек
      industryCards.forEach(function(c) {
        c.classList.remove('active');
      });
      
      // Добавляем активный класс к текущей карточке
      this.classList.add('active');
      
      // Показываем уведомление (можно заменить на модальное окно)
      var industryName = this.querySelector('h3').textContent;
      console.log('Выбрана отрасль:', industryName);
      
      // Здесь можно добавить показ дополнительной информации
      // Например, модальное окно с примерами использования для этой отрасли
    });
  });
})();
