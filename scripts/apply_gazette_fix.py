from pathlib import Path
import re

path = Path("index.html")
html = path.read_text(encoding="utf-8")

# Wrap the slide rail in a stage with full-height 5% click zones.
old = '<div class="slides-track" id="leadSlides" aria-label="Tutoriel ChatGPT Sites">'
new = '''<div class="deck-stage" id="deckStage">
            <button class="edge-zone left" type="button" id="deckPrevEdge" aria-label="Slide précédente">
              <span class="edge-pill" aria-hidden="true">←</span>
            </button>
            <div class="slides-track" id="leadSlides" aria-label="Tutoriel ChatGPT Sites">'''
if old in html and 'id="deckStage"' not in html:
    html = html.replace(old, new, 1)

old_close = '''          </div>

          <div class="deck-controls" aria-label="Contrôles du tutoriel">'''
new_close = '''          </div>
            <button class="edge-zone right" type="button" id="deckNextEdge" aria-label="Slide suivante">
              <span class="edge-pill" aria-hidden="true">→</span>
            </button>
          </div>

          <div class="deck-controls" aria-label="Contrôles du tutoriel">'''
if 'id="deckNextEdge"' not in html:
    html = html.replace(old_close, new_close, 1)

css = r'''
    /* ===== Correctifs mini-deck / navigation ===== */
    .lead-deck-shell{
      display:grid !important;
      grid-template-rows:auto minmax(0,1fr) auto;
      height:100%;
      min-height:100%;
      position:relative;
    }
    .deck-stage{
      position:relative;
      min-height:0;
      height:100%;
      overflow:hidden;
    }
    .slides-track{
      height:100%;
      align-items:stretch;
      overflow-x:auto;
      overflow-y:hidden;
      scroll-snap-type:x mandatory;
      scroll-padding-inline:0;
      scrollbar-gutter:stable both-edges;
    }
    .slides-track::-webkit-scrollbar{height:10px;width:10px}
    .slides-track::-webkit-scrollbar-thumb{background:#bccdd7;border-radius:999px}
    .slides-track::-webkit-scrollbar-track{background:transparent}
    .learning-slide{
      height:100%;
      min-height:0;
      aspect-ratio:auto !important;
      overflow:auto;
      overscroll-behavior:contain;
      scrollbar-width:thin;
      scrollbar-color:#9ab2c0 transparent;
    }
    .learning-slide::-webkit-scrollbar{width:10px;height:10px}
    .learning-slide::-webkit-scrollbar-thumb{background:#9ab2c0;border-radius:999px}
    .learning-slide::-webkit-scrollbar-track{background:transparent}
    .edge-zone{
      position:absolute;
      top:0;
      bottom:0;
      width:5%;
      min-width:40px;
      max-width:84px;
      border:0;
      padding:0;
      margin:0;
      background:transparent;
      cursor:pointer;
      z-index:6;
      display:flex;
      align-items:center;
      justify-content:center;
      transition:background .15s ease;
    }
    .edge-zone.left{left:0}
    .edge-zone.right{right:0}
    .edge-zone:hover{background:linear-gradient(to right, rgba(22,50,74,.08), transparent)}
    .edge-zone.right:hover{background:linear-gradient(to left, rgba(22,50,74,.08), transparent)}
    .edge-zone:disabled{cursor:default;opacity:.35}
    .edge-pill{
      display:grid;
      place-items:center;
      width:42px;
      height:42px;
      border-radius:999px;
      background:rgba(255,255,255,.88);
      color:var(--navy);
      box-shadow:0 8px 24px rgba(22,50,74,.16);
      font-size:20px;
      font-weight:900;
      opacity:.22;
      transition:opacity .15s ease, transform .15s ease;
      pointer-events:none;
    }
    .deck-stage:hover .edge-pill,
    .lead-deck-shell.is-fullscreen .edge-pill,
    .edge-zone:focus-visible .edge-pill{opacity:.95}
    .edge-zone:hover .edge-pill{transform:scale(1.05)}
    .news-type-icon{
      display:inline-grid;
      place-items:center;
      width:24px;
      height:24px;
      border-radius:8px;
      background:var(--soft-blue);
      color:var(--blue);
      font-size:13px;
      line-height:1;
      flex:0 0 24px;
    }
    .local .news-type-icon{background:var(--soft-mint);color:#2c8e78}
    .logistics .news-type-icon{background:var(--soft-orange);color:#b77817}
    .news-kicker .dot{display:none}
    .lead-deck-shell:fullscreen{
      width:100vw;
      height:100vh;
      max-width:none;
      max-height:none;
      padding:22px;
      border:0;
      border-radius:0;
      background:var(--paper);
      box-shadow:none;
    }
    .lead-deck-shell:fullscreen .deck-stage{height:100%}
    .lead-deck-shell:fullscreen .learning-slide{
      min-height:calc(100vh - 168px);
      height:100%;
    }
    .lead-deck-shell:fullscreen .edge-zone{
      min-width:56px;
      max-width:110px;
    }
    .lead-deck-shell:fullscreen .edge-pill{
      width:56px;
      height:56px;
      font-size:28px;
      opacity:.98;
    }
    @media (max-width:980px){
      .lead-deck-shell{min-height:780px}
    }
    @media (max-width:700px){
      .lead-deck-shell{min-height:0}
      .deck-stage{min-height:620px}
      .learning-slide{min-height:620px}
      .edge-zone{min-width:30px;max-width:40px}
      .edge-pill{width:34px;height:34px;font-size:18px;opacity:.85}
    }
'''
if '/* ===== Correctifs mini-deck / navigation ===== */' not in html:
    html = html.replace('</style>', css + '\n  </style>', 1)

script_pattern = re.compile(r'<script>\s*\(\(\) => \{.*?\}\)\(\);\s*</script>', re.S)
new_script = r'''<script>
    (() => {
      const deck = document.getElementById('leadDeck');
      const track = document.getElementById('leadSlides');
      const slides = Array.from(track.querySelectorAll('.learning-slide'));
      const prev = document.getElementById('deckPrev');
      const next = document.getElementById('deckNext');
      const prevEdge = document.getElementById('deckPrevEdge');
      const nextEdge = document.getElementById('deckNextEdge');
      const indicator = document.getElementById('slideIndicator');
      const fullscreen = document.getElementById('deckFullscreen');
      let current = 0;
      let rafId = null;

      const updateDisabled = () => {
        const atStart = current === 0;
        const atEnd = current === slides.length - 1;
        prev.disabled = atStart;
        prevEdge.disabled = atStart;
        next.disabled = atEnd;
        nextEdge.disabled = atEnd;
      };

      const update = () => {
        const trackRect = track.getBoundingClientRect();
        let bestIndex = 0;
        let bestDistance = Infinity;
        slides.forEach((slide, index) => {
          const distance = Math.abs(slide.getBoundingClientRect().left - trackRect.left);
          if (distance < bestDistance) {
            bestDistance = distance;
            bestIndex = index;
          }
        });
        current = bestIndex;
        indicator.textContent = `${current + 1} / ${slides.length}`;
        updateDisabled();
      };

      const goTo = (index) => {
        current = Math.max(0, Math.min(index, slides.length - 1));
        slides[current].scrollIntoView({behavior:'smooth', block:'nearest', inline:'start'});
        window.setTimeout(update, 300);
      };

      const scheduleUpdate = () => {
        if (rafId) cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(update);
      };

      [prev, prevEdge].forEach(btn => btn.addEventListener('click', () => goTo(current - 1)));
      [next, nextEdge].forEach(btn => btn.addEventListener('click', () => goTo(current + 1)));
      track.addEventListener('scroll', scheduleUpdate, {passive:true});

      fullscreen.addEventListener('click', async () => {
        try {
          if (!document.fullscreenElement) await deck.requestFullscreen();
          else await document.exitFullscreen();
        } catch (e) {}
      });

      document.addEventListener('fullscreenchange', () => {
        const active = document.fullscreenElement === deck;
        fullscreen.textContent = active ? '× Quitter le plein écran' : '⛶ Plein écran';
        deck.classList.toggle('is-fullscreen', active);
        window.setTimeout(update, 60);
      });

      document.addEventListener('keydown', (event) => {
        const active = document.fullscreenElement === deck || deck.matches(':hover');
        if (!active) return;
        if (event.key === 'ArrowRight') {
          event.preventDefault();
          goTo(current + 1);
        }
        if (event.key === 'ArrowLeft') {
          event.preventDefault();
          goTo(current - 1);
        }
        if (event.key === 'Escape' && document.fullscreenElement === deck) {
          document.exitFullscreen().catch(() => {});
        }
      });
      update();
    })();
  </script>'''
html, count = script_pattern.subn(new_script, html, 1)
if count != 1:
    raise RuntimeError('Unable to replace deck script')

icons = {
    '<span class="news-kicker"><i class="dot"></i> IA • OpenAI</span>': '<span class="news-kicker"><span class="news-type-icon" aria-hidden="true">🧠</span> IA • OpenAI</span>',
    '<span class="news-kicker"><i class="dot"></i> IA • Sécurité</span>': '<span class="news-kicker"><span class="news-type-icon" aria-hidden="true">🛡️</span> IA • Sécurité</span>',
    '<span class="news-kicker"><i class="dot"></i> IA • Création</span>': '<span class="news-kicker"><span class="news-type-icon" aria-hidden="true">✨</span> IA • Création</span>',
    '<span class="news-kicker"><i class="dot"></i> Normandie • Réseau</span>': '<span class="news-kicker"><span class="news-type-icon" aria-hidden="true">⚓</span> Normandie • Réseau</span>',
    '<span class="news-kicker"><i class="dot"></i> Normandie • Digital twin</span>': '<span class="news-kicker"><span class="news-type-icon" aria-hidden="true">🧭</span> Normandie • Digital twin</span>',
    '<span class="news-kicker"><i class="dot"></i> Logistique • Computer vision</span>': '<span class="news-kicker"><span class="news-type-icon" aria-hidden="true">📦</span> Logistique • Computer vision</span>',
}
for old_icon, new_icon in icons.items():
    html = html.replace(old_icon, new_icon)

path.write_text(html, encoding="utf-8")
