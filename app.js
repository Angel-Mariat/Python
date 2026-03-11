// ===== Default seed events =====
const DEFAULT_EVENTS = [
  { id: '1', name: 'College Annual Fest', date: '2026-04-15', time: '09:00', description: 'Annual cultural extravaganza featuring music, dance, drama, and art competitions.', category: 'fest' },
  { id: '2', name: 'Tech Symposium', date: '2026-05-10', time: '10:00', description: 'A day of tech talks, hackathons, and workshops led by industry experts.', category: 'workshop' },
  { id: '3', name: 'Sports Week Opening', date: '2026-06-01', time: '08:00', description: 'Kick-off ceremony for the inter-department sports week.', category: 'sports' },
  { id: '4', name: 'Guest Lecture: AI & Future', date: '2026-04-22', time: '14:00', description: 'Special seminar by Dr. Priya Sharma on Artificial Intelligence and its impact on education.', category: 'seminar' },
  { id: '5', name: 'Mid-Semester Exams', date: '2026-03-25', time: '09:00', description: 'Mid-semester examination period begins.', category: 'academic' },
];

// ===== Storage helpers =====
function getEvents() {
  let events = localStorage.getItem('college_events');
  if (!events) {
    localStorage.setItem('college_events', JSON.stringify(DEFAULT_EVENTS));
    events = JSON.stringify(DEFAULT_EVENTS);
  }
  return JSON.parse(events);
}

function getUpcomingEvents() {
  const now = new Date();
  return getEvents()
    .filter(e => new Date(e.date + 'T' + (e.time || '00:00')) >= now)
    .sort((a, b) => new Date(a.date) - new Date(b.date));
}

// ===== Formatting helpers =====
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const FULL_MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const DAYS = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

function formatDateLong(dateStr) {
  const d = new Date(dateStr);
  return `${DAYS[d.getDay()]}, ${d.getDate()} ${FULL_MONTHS[d.getMonth()]} ${d.getFullYear()}`;
}

function formatTime12(time24) {
  if (!time24) return '';
  const [h, m] = time24.split(':').map(Number);
  const ampm = h >= 12 ? 'PM' : 'AM';
  const hr = h % 12 || 12;
  return `${hr}:${String(m).padStart(2, '0')} ${ampm}`;
}

function daysUntil(dateStr) {
  const now = new Date();
  const target = new Date(dateStr);
  now.setHours(0, 0, 0, 0);
  target.setHours(0, 0, 0, 0);
  return Math.round((target - now) / (1000 * 60 * 60 * 24));
}

// ===== Countdown timer =====
let countdownInterval = null;

function startCountdown(event) {
  const heroSection = document.getElementById('countdownHero');
  const emptyState = document.getElementById('emptyState');

  if (!event) {
    heroSection.style.display = 'none';
    emptyState.style.display = 'block';
    return;
  }

  heroSection.style.display = 'block';
  emptyState.style.display = 'none';

  // Fill hero info
  document.getElementById('heroEventName').textContent = event.name;
  document.getElementById('heroEventDate').querySelector('span').textContent =
    formatDateLong(event.date) + (event.time ? ' • ' + formatTime12(event.time) : '');

  document.getElementById('heroEventDesc').textContent = event.description || '';

  // Category label
  const label = document.getElementById('heroLabel');
  const catText = event.category ? event.category.charAt(0).toUpperCase() + event.category.slice(1) : 'Event';
  label.innerHTML = `⚡ Next Event &middot; <span class="category-badge ${event.category || 'other'}">${catText}</span>`;

  // Start the ticking countdown
  if (countdownInterval) clearInterval(countdownInterval);

  function tick() {
    const targetDate = new Date(event.date + 'T' + (event.time || '00:00'));
    const now = new Date();
    let diff = targetDate - now;

    if (diff <= 0) {
      document.getElementById('cdDays').textContent = '00';
      document.getElementById('cdHours').textContent = '00';
      document.getElementById('cdMinutes').textContent = '00';
      document.getElementById('cdSeconds').textContent = '00';
      clearInterval(countdownInterval);
      return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    diff -= days * 1000 * 60 * 60 * 24;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    diff -= hours * 1000 * 60 * 60;
    const mins = Math.floor(diff / (1000 * 60));
    diff -= mins * 1000 * 60;
    const secs = Math.floor(diff / 1000);

    document.getElementById('cdDays').textContent = String(days).padStart(2, '0');
    document.getElementById('cdHours').textContent = String(hours).padStart(2, '0');
    document.getElementById('cdMinutes').textContent = String(mins).padStart(2, '0');
    document.getElementById('cdSeconds').textContent = String(secs).padStart(2, '0');
  }

  tick();
  countdownInterval = setInterval(tick, 1000);
}

// ===== Render upcoming events list =====
function renderUpcomingEvents(events) {
  const section = document.getElementById('upcomingSection');
  const grid = document.getElementById('eventsGrid');

  if (events.length === 0) {
    section.style.display = 'none';
    return;
  }

  section.style.display = 'block';
  grid.innerHTML = '';

  events.forEach((event, i) => {
    const d = new Date(event.date);
    const dLeft = daysUntil(event.date);

    let daysClass = '';
    let daysText = '';
    if (dLeft === 0) {
      daysClass = 'today';
      daysText = '🔴 Today';
    } else if (dLeft <= 7) {
      daysClass = 'soon';
      daysText = `${dLeft} day${dLeft > 1 ? 's' : ''} left`;
    } else {
      daysText = `${dLeft} days left`;
    }

    const card = document.createElement('div');
    card.className = 'event-card';
    card.style.animationDelay = `${i * 0.06}s`;

    card.innerHTML = `
      <div class="date-badge">
        <span class="day">${d.getDate()}</span>
        <span class="month">${MONTHS[d.getMonth()]}</span>
      </div>
      <div class="event-info">
        <h3>${escapeHtml(event.name)}</h3>
        <div class="event-meta">
          <span>${formatDateLong(event.date)}</span>
          ${event.time ? `<span>${formatTime12(event.time)}</span>` : ''}
          ${event.category ? `<span class="category-badge ${event.category}">${capitalize(event.category)}</span>` : ''}
        </div>
      </div>
      <div class="days-left ${daysClass}">${daysText}</div>
    `;

    grid.appendChild(card);
  });
}

// ===== Utility =====
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// ===== Init =====
function init() {
  const upcoming = getUpcomingEvents();
  startCountdown(upcoming[0] || null);
  renderUpcomingEvents(upcoming);
}

init();
