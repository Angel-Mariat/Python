// ===== Default seed events (same as app.js) =====
const DEFAULT_EVENTS = [
  { id: '1', name: 'College Annual Fest', date: '2026-04-15', time: '09:00', description: 'Annual cultural extravaganza featuring music, dance, drama, and art competitions.', category: 'fest' },
  { id: '2', name: 'Tech Symposium', date: '2026-05-10', time: '10:00', description: 'A day of tech talks, hackathons, and workshops led by industry experts.', category: 'workshop' },
  { id: '3', name: 'Sports Week Opening', date: '2026-06-01', time: '08:00', description: 'Kick-off ceremony for the inter-department sports week.', category: 'sports' },
  { id: '4', name: 'Guest Lecture: AI & Future', date: '2026-04-22', time: '14:00', description: 'Special seminar by Dr. Priya Sharma on Artificial Intelligence and its impact on education.', category: 'seminar' },
  { id: '5', name: 'Mid-Semester Exams', date: '2026-03-25', time: '09:00', description: 'Mid-semester examination period begins.', category: 'academic' },
];

// ===== Storage =====
function getEvents() {
  let events = localStorage.getItem('college_events');
  if (!events) {
    localStorage.setItem('college_events', JSON.stringify(DEFAULT_EVENTS));
    events = JSON.stringify(DEFAULT_EVENTS);
  }
  return JSON.parse(events);
}

function saveEvents(events) {
  localStorage.setItem('college_events', JSON.stringify(events));
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
}

// ===== Formatting =====
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const FULL_MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const DAYS_NAMES = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

function formatDateLong(dateStr) {
  const d = new Date(dateStr);
  return `${d.getDate()} ${FULL_MONTHS[d.getMonth()]} ${d.getFullYear()}`;
}

function formatTime12(time24) {
  if (!time24) return '';
  const [h, m] = time24.split(':').map(Number);
  const ampm = h >= 12 ? 'PM' : 'AM';
  const hr = h % 12 || 12;
  return `${hr}:${String(m).padStart(2, '0')} ${ampm}`;
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

// ===== Toast =====
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  toast.innerHTML = `<span>${icons[type] || '✅'}</span> ${escapeHtml(message)}`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('toast-exit');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ===== Form elements =====
const form = document.getElementById('eventForm');
const eventIdField = document.getElementById('eventId');
const nameInput = document.getElementById('eventName');
const dateInput = document.getElementById('eventDate');
const timeInput = document.getElementById('eventTime');
const descInput = document.getElementById('eventDescription');
const catInput = document.getElementById('eventCategory');
const submitBtn = document.getElementById('submitBtn');
const cancelBtn = document.getElementById('cancelBtn');
const formTitle = document.getElementById('formTitle');
const formSubtitle = document.getElementById('formSubtitle');

let editingId = null;

// ===== Form submit =====
form.addEventListener('submit', function(e) {
  e.preventDefault();

  const name = nameInput.value.trim();
  const date = dateInput.value;
  const time = timeInput.value;
  const description = descInput.value.trim();
  const category = catInput.value;

  if (!name || !date) {
    showToast('Please fill in event name and date.', 'error');
    return;
  }

  const events = getEvents();

  if (editingId) {
    // Update existing event
    const idx = events.findIndex(e => e.id === editingId);
    if (idx !== -1) {
      events[idx] = { ...events[idx], name, date, time, description, category };
      saveEvents(events);
      showToast(`"${name}" updated successfully!`, 'success');
    }
    cancelEdit();
  } else {
    // Add new event
    const newEvent = {
      id: generateId(),
      name,
      date,
      time,
      description,
      category,
    };
    events.push(newEvent);
    saveEvents(events);
    showToast(`"${name}" added successfully!`, 'success');
  }

  form.reset();
  renderEvents();
});

// ===== Edit mode =====
function startEdit(id) {
  const events = getEvents();
  const event = events.find(e => e.id === id);
  if (!event) return;

  editingId = id;
  nameInput.value = event.name;
  dateInput.value = event.date;
  timeInput.value = event.time || '';
  descInput.value = event.description || '';
  catInput.value = event.category || 'other';

  formTitle.textContent = '✏️ Edit Event';
  formSubtitle.textContent = `Editing "${event.name}" — make your changes and save.`;
  submitBtn.textContent = '💾 Save Changes';
  cancelBtn.style.display = 'inline-flex';

  // Scroll to form
  form.scrollIntoView({ behavior: 'smooth', block: 'center' });
  nameInput.focus();
}

function cancelEdit() {
  editingId = null;
  form.reset();
  formTitle.textContent = '➕ Add New Event';
  formSubtitle.textContent = 'Fill in the details to create a new campus event.';
  submitBtn.textContent = '➕ Add Event';
  cancelBtn.style.display = 'none';
}

// ===== Delete =====
let deleteTargetId = null;

function openDeleteModal(id, name) {
  deleteTargetId = id;
  document.getElementById('deleteModalText').textContent = `Are you sure you want to delete "${name}"? This action cannot be undone.`;
  document.getElementById('deleteModal').style.display = 'flex';
}

function closeDeleteModal() {
  deleteTargetId = null;
  document.getElementById('deleteModal').style.display = 'none';
}

document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
  if (!deleteTargetId) return;

  let events = getEvents();
  const event = events.find(e => e.id === deleteTargetId);
  const name = event ? event.name : 'Event';
  events = events.filter(e => e.id !== deleteTargetId);
  saveEvents(events);

  // If we were editing this event, cancel edit
  if (editingId === deleteTargetId) cancelEdit();

  closeDeleteModal();
  showToast(`"${name}" deleted.`, 'info');
  renderEvents();
});

// Close modal on overlay click
document.getElementById('deleteModal').addEventListener('click', function(e) {
  if (e.target === this) closeDeleteModal();
});

// ===== Render events list =====
function renderEvents() {
  const events = getEvents().sort((a, b) => new Date(a.date) - new Date(b.date));
  const container = document.getElementById('adminEventsList');
  const emptyState = document.getElementById('adminEmpty');
  const countSpan = document.getElementById('eventCount');

  countSpan.textContent = `(${events.length})`;

  if (events.length === 0) {
    container.innerHTML = '';
    emptyState.style.display = 'block';
    return;
  }

  emptyState.style.display = 'none';
  container.innerHTML = '';

  events.forEach((event, i) => {
    const row = document.createElement('div');
    row.className = 'admin-event-row';
    row.style.animationDelay = `${i * 0.04}s`;

    const d = new Date(event.date);
    const isPast = d < new Date(new Date().toDateString());

    row.innerHTML = `
      <div class="date-badge" style="${isPast ? 'opacity: 0.4;' : ''}">
        <span class="day">${d.getDate()}</span>
        <span class="month">${MONTHS[d.getMonth()]}</span>
      </div>
      <div class="event-info">
        <h3 style="${isPast ? 'opacity: 0.5; text-decoration: line-through;' : ''}">${escapeHtml(event.name)}</h3>
        <div class="meta">
          <span>📅 ${formatDateLong(event.date)}</span>
          ${event.time ? `<span>🕐 ${formatTime12(event.time)}</span>` : ''}
          ${event.category ? `<span class="category-badge ${event.category}">${capitalize(event.category)}</span>` : ''}
          ${isPast ? '<span style="color: var(--text-muted);">Past event</span>' : ''}
        </div>
      </div>
      <div class="row-actions">
        <button class="btn btn-secondary btn-icon" title="Edit" onclick="startEdit('${event.id}')">✏️</button>
        <button class="btn btn-danger btn-icon" title="Delete" onclick="openDeleteModal('${event.id}', '${escapeHtml(event.name).replace(/'/g, "\\'")}')">🗑️</button>
      </div>
    `;

    container.appendChild(row);
  });
}

// ===== Init =====
renderEvents();
