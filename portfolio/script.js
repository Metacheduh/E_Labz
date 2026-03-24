// ═══════════════════════════════════════════════════════════
// E-Labz Portfolio v2 — Premium Interactive Effects
// Particles + Cursor spotlight + Counter animation + Tabs
// ═══════════════════════════════════════════════════════════

// ─── Particle System (subtle, connects with lines) ───
const canvas = document.getElementById('particles');
const ctx = canvas.getContext('2d');
let particles = [];
let w, h;

function resize() { w = canvas.width = window.innerWidth; h = canvas.height = window.innerHeight; }
resize();
window.addEventListener('resize', resize);

class Particle {
  constructor() { this.reset(); }
  reset() {
    this.x = Math.random() * w; this.y = Math.random() * h;
    this.vx = (Math.random() - 0.5) * 0.2; this.vy = (Math.random() - 0.5) * 0.2;
    this.r = Math.random() * 1.2 + 0.3; this.alpha = Math.random() * 0.3 + 0.05;
    const c = ['139,92,246','6,214,160','247,37,133','76,201,240'];
    this.color = c[Math.floor(Math.random() * c.length)];
  }
  update() { this.x += this.vx; this.y += this.vy; if (this.x < 0 || this.x > w || this.y < 0 || this.y > h) this.reset(); }
  draw() { ctx.beginPath(); ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2); ctx.fillStyle = `rgba(${this.color},${this.alpha})`; ctx.fill(); }
}

for (let i = 0; i < 60; i++) particles.push(new Particle());

function animateParticles() {
  ctx.clearRect(0, 0, w, h);
  particles.forEach(p => { p.update(); p.draw(); });
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x;
      const dy = particles[i].y - particles[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 100) {
        ctx.beginPath(); ctx.moveTo(particles[i].x, particles[i].y);
        ctx.lineTo(particles[j].x, particles[j].y);
        ctx.strokeStyle = `rgba(139,92,246,${0.04 * (1 - dist / 100)})`;
        ctx.lineWidth = 0.4; ctx.stroke();
      }
    }
  }
  requestAnimationFrame(animateParticles);
}
animateParticles();

// ─── Cursor Spotlight on Cards ───
document.addEventListener('mousemove', (e) => {
  const cards = document.querySelectorAll('.swarm-card, .project-card, .store-card, .service-card');
  cards.forEach(card => {
    const rect = card.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width * 100).toFixed(1) + '%';
    const y = ((e.clientY - rect.top) / rect.height * 100).toFixed(1) + '%';
    card.style.setProperty('--mouse-x', x);
    card.style.setProperty('--mouse-y', y);
  });
});

// ─── Nav Scroll ───
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => { nav.classList.toggle('scrolled', window.scrollY > 50); });

// ─── Animated Counters ───
function animateCounters() {
  const nums = document.querySelectorAll('.stat-num[data-count]');
  nums.forEach(el => {
    const target = parseInt(el.dataset.count);
    const suffix = el.dataset.count.includes('+') ? '+' : '';
    let current = 0;
    const step = Math.max(1, Math.floor(target / 40));
    const timer = setInterval(() => {
      current += step;
      if (current >= target) { current = target; clearInterval(timer); }
      el.textContent = current + suffix;
    }, 30);
  });
}

// ─── Scroll Reveal with Stagger ───
const revealEls = document.querySelectorAll('.swarm-card, .project-card, .agent-pill, .store-card, .service-card, .process-step, .section-visual');
revealEls.forEach(el => el.classList.add('reveal'));

let countersAnimated = false;
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      // Stagger based on sibling index
      const parent = entry.target.parentElement;
      const siblings = Array.from(parent.children).filter(c => c.classList.contains('reveal'));
      const idx = siblings.indexOf(entry.target);
      setTimeout(() => entry.target.classList.add('visible'), idx * 80);
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.05, rootMargin: '0px 0px -20px 0px' });
revealEls.forEach(el => observer.observe(el));

// Counter observer
const statsSection = document.querySelector('.hero-stats');
if (statsSection) {
  const counterObs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !countersAnimated) {
        countersAnimated = true;
        animateCounters();
        counterObs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  counterObs.observe(statsSection);
}

// ─── Marketplace Tabs ───
window.showTab = function(tabId) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(tabId).classList.remove('hidden');
  event.target.classList.add('active');
};

// ─── Mobile Nav Close on Link Click ───
document.querySelectorAll('.nav-links a').forEach(link => {
  link.addEventListener('click', () => document.querySelector('.nav-links').classList.remove('open'));
});

// ─── Swarm Live Timestamps ───
function updateSwarm() {
  const now = new Date();
  const t = now.toLocaleTimeString('en-US', { hour12: false });
  document.querySelectorAll('.swarm-card.active .swarm-status').forEach(el => {
    el.textContent = `● Active — ${t}`;
  });
}
setInterval(updateSwarm, 1000);
updateSwarm();

// ─── Smooth anchor scrolling offset for fixed nav ───
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = 80;
      window.scrollTo({ top: target.offsetTop - offset, behavior: 'smooth' });
    }
  });
});
