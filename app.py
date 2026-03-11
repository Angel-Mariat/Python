"""
College Event Reminder System
===============================
A Python desktop application for managing and tracking college events
with a live countdown timer and desktop notifications.

Beyond-Syllabus Libraries Used:
    - customtkinter  : Modern dark-themed GUI toolkit
    - tkcalendar     : Calendar-based date picker widget
    - plyer          : Cross-platform desktop notifications

Author  : Student
Date    : March 2026
"""

import json
import os
from datetime import datetime, timedelta
import customtkinter as ctk
from tkcalendar import DateEntry
from plyer import notification

# ============================================================
# Configuration
# ============================================================
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.json")

CATEGORIES = [
    "Academic", "Cultural", "Sports",
    "Workshop", "Seminar", "Fest", "Other"
]

CATEGORY_COLORS = {
    "Academic":  "#818cf8",
    "Cultural":  "#f472b6",
    "Sports":    "#4ade80",
    "Workshop":  "#fbbf24",
    "Seminar":   "#22d3ee",
    "Fest":      "#c084fc",
    "Other":     "#94a3b8",
}

DEFAULT_EVENTS = [
    {
        "id": "1",
        "name": "College Annual Fest",
        "date": "2026-04-15",
        "time": "09:00",
        "description": "Annual cultural extravaganza featuring music, dance, and art.",
        "category": "Fest",
    },
    {
        "id": "2",
        "name": "Tech Symposium",
        "date": "2026-05-10",
        "time": "10:00",
        "description": "Tech talks, hackathons, and workshops by industry experts.",
        "category": "Workshop",
    },
    {
        "id": "3",
        "name": "Sports Week Opening",
        "date": "2026-06-01",
        "time": "08:00",
        "description": "Kick-off ceremony for inter-department sports week.",
        "category": "Sports",
    },
    {
        "id": "4",
        "name": "Guest Lecture: AI & Future",
        "date": "2026-04-22",
        "time": "14:00",
        "description": "Seminar by Dr. Priya Sharma on AI in education.",
        "category": "Seminar",
    },
    {
        "id": "5",
        "name": "Mid-Semester Exams",
        "date": "2026-03-25",
        "time": "09:00",
        "description": "Mid-semester examination period begins.",
        "category": "Academic",
    },
]


# ============================================================
# Event Manager — handles data persistence and CRUD
# ============================================================
class EventManager:
    """Manages event data: load, save, add, edit, delete, query."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.events: list[dict] = self._load()

    # --- Persistence ---------------------------------------------------

    def _load(self) -> list[dict]:
        """Load events from JSON file; seed defaults if file missing."""
        if not os.path.exists(self.filepath):
            self._save(DEFAULT_EVENTS)
            return list(DEFAULT_EVENTS)
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Migrate old format (no id field)
                for i, evt in enumerate(data):
                    if "id" not in evt:
                        evt["id"] = str(i + 1)
                return data
        except (json.JSONDecodeError, IOError):
            return list(DEFAULT_EVENTS)

    def _save(self, data: list[dict] | None = None):
        """Persist current events to JSON file."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data or self.events, f, indent=2, ensure_ascii=False)

    # --- CRUD ----------------------------------------------------------

    def add(self, name: str, date: str, time: str, desc: str, cat: str) -> dict:
        """Add a new event and save."""
        event = {
            "id": self._next_id(),
            "name": name,
            "date": date,
            "time": time,
            "description": desc,
            "category": cat,
        }
        self.events.append(event)
        self._save()
        return event

    def update(self, event_id: str, **fields):
        """Update an existing event by ID."""
        for evt in self.events:
            if evt["id"] == event_id:
                evt.update(fields)
                self._save()
                return True
        return False

    def delete(self, event_id: str) -> bool:
        """Delete an event by ID."""
        before = len(self.events)
        self.events = [e for e in self.events if e["id"] != event_id]
        if len(self.events) < before:
            self._save()
            return True
        return False

    def get_all_sorted(self) -> list[dict]:
        """Return all events sorted by date ascending."""
        return sorted(self.events, key=lambda e: e.get("date", ""))

    def get_upcoming(self) -> list[dict]:
        """Return future events sorted by date."""
        today = datetime.today().strftime("%Y-%m-%d")
        return [e for e in self.get_all_sorted() if e["date"] >= today]

    def get_next(self) -> dict | None:
        """Return the soonest upcoming event, or None."""
        upcoming = self.get_upcoming()
        return upcoming[0] if upcoming else None

    def find(self, event_id: str) -> dict | None:
        """Find event by ID."""
        for e in self.events:
            if e["id"] == event_id:
                return e
        return None

    def _next_id(self) -> str:
        """Generate a unique ID."""
        import time, random
        return f"{int(time.time())}{random.randint(100, 999)}"


# ============================================================
# Helper Functions
# ============================================================
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

DAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


def format_date_long(date_str: str) -> str:
    """Convert '2026-04-15' to 'Wednesday, 15 April 2026'."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{DAYS[d.weekday()]}, {d.day} {MONTHS[d.month - 1]} {d.year}"
    except ValueError:
        return date_str


def format_time_12h(time_str: str) -> str:
    """Convert '14:00' to '2:00 PM'."""
    if not time_str:
        return ""
    try:
        h, m = map(int, time_str.split(":"))
        ampm = "PM" if h >= 12 else "AM"
        hr = h % 12 or 12
        return f"{hr}:{m:02d} {ampm}"
    except ValueError:
        return time_str


def days_until(date_str: str) -> int:
    """Return the number of days from today to the given date."""
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (target - datetime.today().date()).days
    except ValueError:
        return -1


def send_notification(title: str, message: str):
    """Send a desktop notification using plyer."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="EventPulse",
            timeout=8,
        )
    except Exception:
        pass  # Ignore if notification fails on unsupported platform


# ============================================================
# Application GUI
# ============================================================
class EventPulseApp(ctk.CTk):
    """Main application window with Dashboard and Admin tabs."""

    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.title("EventPulse — College Event Reminder")
        self.geometry("960x680")
        self.minsize(800, 600)

        # Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Data manager
        self.manager = EventManager(DATA_FILE)
        self.editing_id = None  # Track edit mode

        # --- Build UI ---
        self._build_header()
        self._build_tabs()

        # Start live countdown
        self._tick_countdown()

        # Check for today's events and notify
        self._check_today_notifications()

    # ----------------------------------------------------------------
    # Header
    # ----------------------------------------------------------------
    def _build_header(self):
        """Build the top header bar."""
        header = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Brand
        brand_frame = ctk.CTkFrame(header, fg_color="transparent")
        brand_frame.pack(side="left", padx=20)

        ctk.CTkLabel(
            brand_frame, text="🎓 EventPulse",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#c084fc",
        ).pack(side="left")

        ctk.CTkLabel(
            brand_frame, text="  College Event Reminder",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
        ).pack(side="left", padx=(4, 0))

    # ----------------------------------------------------------------
    # Tabs
    # ----------------------------------------------------------------
    def _build_tabs(self):
        """Create the tabbed interface."""
        self.tabview = ctk.CTkTabview(
            self,
            fg_color="#0f0f23",
            segmented_button_selected_color="#7c3aed",
            segmented_button_selected_hover_color="#6d28d9",
            segmented_button_unselected_color="#1e1e3a",
            segmented_button_unselected_hover_color="#2a2a4a",
        )
        self.tabview.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        # --- Dashboard Tab ---
        self.tab_dashboard = self.tabview.add("📅  Dashboard")
        self._build_dashboard()

        # --- Admin Tab ---
        self.tab_admin = self.tabview.add("⚙️  Admin Panel")
        self._build_admin()

    # ================================================================
    # DASHBOARD TAB
    # ================================================================
    def _build_dashboard(self):
        """Build the dashboard showing countdown and event list."""
        container = ctk.CTkScrollableFrame(
            self.tab_dashboard, fg_color="transparent"
        )
        container.pack(fill="both", expand=True, padx=4, pady=4)

        # --- Countdown Hero ---
        self.hero_frame = ctk.CTkFrame(
            container, fg_color="#16163a",
            corner_radius=16, border_width=1, border_color="#2d2d5e"
        )
        self.hero_frame.pack(fill="x", pady=(0, 16))

        # Label
        self.hero_label = ctk.CTkLabel(
            self.hero_frame, text="⚡ NEXT EVENT",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#a78bfa",
        )
        self.hero_label.pack(anchor="w", padx=24, pady=(20, 0))

        # Event name
        self.hero_name = ctk.CTkLabel(
            self.hero_frame, text="—",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#e2e8f0",
        )
        self.hero_name.pack(anchor="w", padx=24, pady=(6, 0))

        # Event date & description
        self.hero_date = ctk.CTkLabel(
            self.hero_frame, text="",
            font=ctk.CTkFont(size=13),
            text_color="#64748b",
        )
        self.hero_date.pack(anchor="w", padx=24, pady=(2, 0))

        self.hero_desc = ctk.CTkLabel(
            self.hero_frame, text="",
            font=ctk.CTkFont(size=12),
            text_color="#475569",
            wraplength=600, justify="left",
        )
        self.hero_desc.pack(anchor="w", padx=24, pady=(4, 0))

        # Countdown boxes
        cd_frame = ctk.CTkFrame(self.hero_frame, fg_color="transparent")
        cd_frame.pack(anchor="w", padx=24, pady=(16, 24))

        self.cd_labels = {}
        for unit in ["Days", "Hours", "Minutes", "Seconds"]:
            box = ctk.CTkFrame(cd_frame, fg_color="#1e1e42", corner_radius=12,
                               border_width=1, border_color="#2d2d5e",
                               width=90, height=80)
            box.pack(side="left", padx=6)
            box.pack_propagate(False)

            val = ctk.CTkLabel(
                box, text="00",
                font=ctk.CTkFont(size=30, weight="bold"),
                text_color="#a78bfa",
            )
            val.pack(expand=True)

            lbl = ctk.CTkLabel(
                box, text=unit.upper(),
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color="#475569",
            )
            lbl.pack(pady=(0, 8))

            self.cd_labels[unit.lower()] = val

        # --- Empty state ---
        self.empty_label = ctk.CTkLabel(
            container,
            text="📭  No upcoming events.\nGo to Admin Panel to add events!",
            font=ctk.CTkFont(size=14),
            text_color="#475569",
            justify="center",
        )

        # --- Upcoming Events Header ---
        ctk.CTkLabel(
            container, text="📋 Upcoming Events",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e2e8f0", anchor="w",
        ).pack(fill="x", pady=(4, 8))

        # Event list container
        self.events_list_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.events_list_frame.pack(fill="x")

        # Initial render
        self._refresh_dashboard()

    def _refresh_dashboard(self):
        """Refresh the dashboard data."""
        upcoming = self.manager.get_upcoming()
        next_evt = upcoming[0] if upcoming else None

        # Update hero
        if next_evt:
            self.hero_frame.pack(fill="x", pady=(0, 16))
            self.empty_label.pack_forget()

            cat = next_evt.get("category", "Other")
            self.hero_label.configure(text=f"⚡ NEXT EVENT  •  {cat}")
            self.hero_name.configure(text=next_evt["name"])

            date_text = f"📅  {format_date_long(next_evt['date'])}"
            if next_evt.get("time"):
                date_text += f"  •  {format_time_12h(next_evt['time'])}"
            self.hero_date.configure(text=date_text)
            self.hero_desc.configure(text=next_evt.get("description", ""))
        else:
            self.hero_frame.pack_forget()
            self.empty_label.pack(pady=40)

        # Render event cards
        for widget in self.events_list_frame.winfo_children():
            widget.destroy()

        for evt in upcoming:
            self._create_event_card(self.events_list_frame, evt)

    def _create_event_card(self, parent, event: dict):
        """Create a single event card in the list."""
        card = ctk.CTkFrame(
            parent, fg_color="#12122a",
            corner_radius=12, border_width=1, border_color="#1e1e3a",
            height=70,
        )
        card.pack(fill="x", pady=4)
        card.pack_propagate(False)

        # Date badge
        d = datetime.strptime(event["date"], "%Y-%m-%d")
        months_short = ["Jan","Feb","Mar","Apr","May","Jun",
                        "Jul","Aug","Sep","Oct","Nov","Dec"]

        badge = ctk.CTkFrame(card, fg_color="#7c3aed", corner_radius=10,
                             width=52, height=52)
        badge.pack(side="left", padx=(14, 12), pady=9)
        badge.pack_propagate(False)

        ctk.CTkLabel(badge, text=str(d.day),
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#fff").pack(expand=True)
        ctk.CTkLabel(badge, text=months_short[d.month - 1].upper(),
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color="#cccccc").pack(pady=(0, 4))

        # Info
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=10)

        ctk.CTkLabel(info, text=event["name"],
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#e2e8f0", anchor="w").pack(fill="x")

        meta_parts = [format_date_long(event["date"])]
        if event.get("time"):
            meta_parts.append(format_time_12h(event["time"]))
        if event.get("category"):
            meta_parts.append(event["category"])

        ctk.CTkLabel(info, text="  •  ".join(meta_parts),
                     font=ctk.CTkFont(size=11),
                     text_color="#64748b", anchor="w").pack(fill="x")

        # Days left badge
        d_left = days_until(event["date"])
        if d_left == 0:
            badge_text, badge_color = "TODAY", "#22c55e"
        elif d_left <= 7:
            badge_text, badge_color = f"{d_left}d left", "#f59e0b"
        else:
            badge_text, badge_color = f"{d_left}d left", "#7c3aed"

        ctk.CTkLabel(
            card, text=badge_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=badge_color,
            fg_color="#1a1a35", corner_radius=20,
            width=70, height=28,
        ).pack(side="right", padx=14)

    # ================================================================
    # ADMIN TAB
    # ================================================================
    def _build_admin(self):
        """Build the admin panel with form and event list."""
        container = ctk.CTkScrollableFrame(
            self.tab_admin, fg_color="transparent"
        )
        container.pack(fill="both", expand=True, padx=4, pady=4)

        # --- Form Card ---
        form_card = ctk.CTkFrame(
            container, fg_color="#16163a",
            corner_radius=16, border_width=1, border_color="#2d2d5e"
        )
        form_card.pack(fill="x", pady=(0, 16))

        self.form_title = ctk.CTkLabel(
            form_card, text="➕  Add New Event",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e2e8f0",
        )
        self.form_title.pack(anchor="w", padx=24, pady=(20, 4))

        self.form_subtitle = ctk.CTkLabel(
            form_card, text="Fill in the details to create a new campus event.",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
        )
        self.form_subtitle.pack(anchor="w", padx=24, pady=(0, 16))

        # Grid layout for uniform form fields
        grid_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        grid_frame.pack(fill="x", padx=24, pady=(0, 10))
        grid_frame.columnconfigure((0, 1), weight=1)

        # Name
        name_group = ctk.CTkFrame(grid_frame, fg_color="transparent")
        name_group.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 10))

        ctk.CTkLabel(name_group, text="EVENT NAME *",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#94a3b8").pack(anchor="w", pady=(0, 4))

        self.name_entry = ctk.CTkEntry(
            name_group, placeholder_text="e.g. Annual Tech Fest",
            height=38, corner_radius=8,
            fg_color="#1e1e42", border_color="#2d2d5e",
        )
        self.name_entry.pack(fill="x")

        # Category
        cat_group = ctk.CTkFrame(grid_frame, fg_color="transparent")
        cat_group.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 10))

        ctk.CTkLabel(cat_group, text="CATEGORY",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#94a3b8").pack(anchor="w", pady=(0, 4))

        self.cat_menu = ctk.CTkOptionMenu(
            cat_group, values=CATEGORIES, height=38,
            corner_radius=8,
            fg_color="#1e1e42", button_color="#2d2d5e",
            dropdown_fg_color="#1e1e42",
        )
        self.cat_menu.pack(fill="x")

        # Date (using tkcalendar DateEntry)
        date_group = ctk.CTkFrame(grid_frame, fg_color="transparent")
        date_group.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 10))

        ctk.CTkLabel(date_group, text="DATE *  (Calendar Picker)",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#94a3b8").pack(anchor="w", pady=(0, 4))

        self.date_entry = DateEntry(
            date_group, width=20,
            background="#7c3aed", foreground="white",
            borderwidth=0, date_pattern="yyyy-mm-dd",
            font=("Inter", 11),
        )
        self.date_entry.pack(fill="x", ipady=6)

        # Time
        time_group = ctk.CTkFrame(grid_frame, fg_color="transparent")
        time_group.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 10))

        ctk.CTkLabel(time_group, text="TIME",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#94a3b8").pack(anchor="w", pady=(0, 4))

        self.time_entry = ctk.CTkEntry(
            time_group, placeholder_text="HH:MM (e.g. 14:00)",
            height=38, corner_radius=8,
            fg_color="#1e1e42", border_color="#2d2d5e",
        )
        self.time_entry.pack(fill="x")

        # Row 3: Description
        ctk.CTkLabel(form_card, text="DESCRIPTION",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#94a3b8").pack(anchor="w", padx=24, pady=(0, 4))

        self.desc_text = ctk.CTkTextbox(
            form_card, height=70, corner_radius=8,
            fg_color="#1e1e42", border_color="#2d2d5e", border_width=1,
            font=ctk.CTkFont(size=12),
        )
        self.desc_text.pack(fill="x", padx=24, pady=(0, 16))

        # Buttons
        btn_row = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(0, 20))

        self.submit_btn = ctk.CTkButton(
            btn_row, text="➕  Add Event", height=40,
            corner_radius=8, fg_color="#7c3aed",
            hover_color="#6d28d9",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_submit,
        )
        self.submit_btn.pack(side="left")

        self.cancel_btn = ctk.CTkButton(
            btn_row, text="Cancel", height=40,
            corner_radius=8, fg_color="#2a2a4a",
            hover_color="#3a3a5a", text_color="#94a3b8",
            font=ctk.CTkFont(size=13),
            command=self._cancel_edit,
        )
        # cancel_btn hidden initially

        # --- Events List ---
        ctk.CTkLabel(
            container, text="📋 All Events",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e2e8f0", anchor="w",
        ).pack(fill="x", pady=(4, 8))

        self.admin_list_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.admin_list_frame.pack(fill="x")

        self.admin_empty = ctk.CTkLabel(
            container,
            text="📭  No events yet. Use the form above to add one!",
            font=ctk.CTkFont(size=13), text_color="#475569",
        )

        self._refresh_admin_list()

    def _refresh_admin_list(self):
        """Re-render the admin events list."""
        for widget in self.admin_list_frame.winfo_children():
            widget.destroy()

        events = self.manager.get_all_sorted()

        if not events:
            self.admin_empty.pack(pady=20)
            return
        self.admin_empty.pack_forget()

        months_short = ["Jan","Feb","Mar","Apr","May","Jun",
                        "Jul","Aug","Sep","Oct","Nov","Dec"]

        for evt in events:
            row = ctk.CTkFrame(
                self.admin_list_frame, fg_color="#12122a",
                corner_radius=12, border_width=1, border_color="#1e1e3a",
                height=65,
            )
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)

            d = datetime.strptime(evt["date"], "%Y-%m-%d")
            is_past = d.date() < datetime.today().date()

            # Date badge
            badge = ctk.CTkFrame(row, fg_color="#7c3aed" if not is_past else "#3a3a5a",
                                 corner_radius=10, width=48, height=48)
            badge.pack(side="left", padx=(12, 10), pady=8)
            badge.pack_propagate(False)

            ctk.CTkLabel(badge, text=str(d.day),
                         font=ctk.CTkFont(size=16, weight="bold"),
                         text_color="#fff").pack(expand=True)
            ctk.CTkLabel(badge, text=months_short[d.month - 1].upper(),
                         font=ctk.CTkFont(size=8, weight="bold"),
                         text_color="#ddd").pack(pady=(0, 3))

            # Info
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, pady=8)

            name_color = "#64748b" if is_past else "#e2e8f0"
            ctk.CTkLabel(info, text=evt["name"],
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=name_color, anchor="w").pack(fill="x")

            meta = f"📅 {format_date_long(evt['date'])}"
            if evt.get("time"):
                meta += f"  •  🕐 {format_time_12h(evt['time'])}"
            if evt.get("category"):
                meta += f"  •  {evt['category']}"
            if is_past:
                meta += "  •  (Past)"

            ctk.CTkLabel(info, text=meta,
                         font=ctk.CTkFont(size=10),
                         text_color="#475569", anchor="w").pack(fill="x")

            # Action buttons
            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.pack(side="right", padx=12)

            eid = evt["id"]
            ctk.CTkButton(
                actions, text="✏️", width=36, height=36,
                corner_radius=8, fg_color="#2a2a4a",
                hover_color="#3a3a5a",
                command=lambda e=eid: self._start_edit(e),
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                actions, text="🗑️", width=36, height=36,
                corner_radius=8, fg_color="#3a1a1a",
                hover_color="#5a2a2a", text_color="#ef4444",
                command=lambda e=eid: self._confirm_delete(e),
            ).pack(side="left", padx=2)

    # ----------------------------------------------------------------
    # Form Handlers
    # ----------------------------------------------------------------
    def _on_submit(self):
        """Handle form submission for add/edit."""
        name = self.name_entry.get().strip()
        date = self.date_entry.get().strip()
        time_val = self.time_entry.get().strip()
        desc = self.desc_text.get("1.0", "end").strip()
        cat = self.cat_menu.get()

        # Validation
        if not name:
            self._show_message("⚠️  Please enter an event name.", "warning")
            return
        if not date:
            self._show_message("⚠️  Please select a date.", "warning")
            return

        if self.editing_id:
            # Update existing event
            self.manager.update(
                self.editing_id,
                name=name, date=date, time=time_val,
                description=desc, category=cat,
            )
            self._show_message(f"✅  '{name}' updated successfully!")
            self._cancel_edit()
        else:
            # Add new event
            self.manager.add(name, date, time_val, desc, cat)
            self._show_message(f"✅  '{name}' added successfully!")

        # Clear form
        self._clear_form()
        self._refresh_admin_list()
        self._refresh_dashboard()

    def _start_edit(self, event_id: str):
        """Populate form with event data for editing."""
        evt = self.manager.find(event_id)
        if not evt:
            return

        self.editing_id = event_id

        # Fill form
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, evt["name"])

        self.date_entry.set_date(datetime.strptime(evt["date"], "%Y-%m-%d"))

        self.time_entry.delete(0, "end")
        self.time_entry.insert(0, evt.get("time", ""))

        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", evt.get("description", ""))

        self.cat_menu.set(evt.get("category", "Other"))

        # Update form title
        self.form_title.configure(text="✏️  Edit Event")
        self.form_subtitle.configure(text=f'Editing "{evt["name"]}" — make changes and save.')
        self.submit_btn.configure(text="💾  Save Changes")
        self.cancel_btn.pack(side="left", padx=(10, 0))

        # Switch to admin tab
        self.tabview.set("⚙️  Admin Panel")

    def _cancel_edit(self):
        """Exit edit mode and reset form."""
        self.editing_id = None
        self.form_title.configure(text="➕  Add New Event")
        self.form_subtitle.configure(text="Fill in the details to create a new campus event.")
        self.submit_btn.configure(text="➕  Add Event")
        self.cancel_btn.pack_forget()
        self._clear_form()

    def _clear_form(self):
        """Clear all form fields."""
        self.name_entry.delete(0, "end")
        self.time_entry.delete(0, "end")
        self.desc_text.delete("1.0", "end")
        self.cat_menu.set("Other")

    def _confirm_delete(self, event_id: str):
        """Show a confirmation dialog before deleting."""
        evt = self.manager.find(event_id)
        if not evt:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("380x180")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 380) // 2
        y = self.winfo_y() + (self.winfo_height() - 180) // 2
        dialog.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(dialog, fg_color="#1a1a2e", corner_radius=0)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            frame, text="🗑️  Delete Event?",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(20, 8))

        ctk.CTkLabel(
            frame,
            text=f'Are you sure you want to delete\n"{evt["name"]}"?',
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8", justify="center",
        ).pack(pady=(0, 16))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(
            btn_frame, text="Cancel", width=100, height=36,
            fg_color="#2a2a4a", hover_color="#3a3a5a",
            command=dialog.destroy,
        ).pack(side="left", padx=6)

        def do_delete():
            self.manager.delete(event_id)
            if self.editing_id == event_id:
                self._cancel_edit()
            dialog.destroy()
            self._show_message(f"🗑️  '{evt['name']}' deleted.")
            self._refresh_admin_list()
            self._refresh_dashboard()

        ctk.CTkButton(
            btn_frame, text="Delete", width=100, height=36,
            fg_color="#dc2626", hover_color="#b91c1c",
            command=do_delete,
        ).pack(side="left", padx=6)

    # ----------------------------------------------------------------
    # Countdown Timer
    # ----------------------------------------------------------------
    def _tick_countdown(self):
        """Update the countdown labels every second."""
        next_evt = self.manager.get_next()

        if next_evt:
            target_str = next_evt["date"]
            if next_evt.get("time"):
                target_str += f" {next_evt['time']}"
                target = datetime.strptime(target_str, "%Y-%m-%d %H:%M")
            else:
                target = datetime.strptime(target_str, "%Y-%m-%d")

            diff = target - datetime.now()

            if diff.total_seconds() > 0:
                total_secs = int(diff.total_seconds())
                days = total_secs // 86400
                hours = (total_secs % 86400) // 3600
                mins = (total_secs % 3600) // 60
                secs = total_secs % 60

                self.cd_labels["days"].configure(text=f"{days:02d}")
                self.cd_labels["hours"].configure(text=f"{hours:02d}")
                self.cd_labels["minutes"].configure(text=f"{mins:02d}")
                self.cd_labels["seconds"].configure(text=f"{secs:02d}")
            else:
                for key in self.cd_labels:
                    self.cd_labels[key].configure(text="00")

        # Schedule next tick
        self.after(1000, self._tick_countdown)

    # ----------------------------------------------------------------
    # Notifications (plyer — beyond syllabus)
    # ----------------------------------------------------------------
    def _check_today_notifications(self):
        """Send desktop notification for events happening today."""
        today = datetime.today().strftime("%Y-%m-%d")
        for evt in self.manager.events:
            if evt["date"] == today:
                send_notification(
                    title=f"🎓 Today: {evt['name']}",
                    message=evt.get("description", "You have an event today!"),
                )

    # ----------------------------------------------------------------
    # Status Messages
    # ----------------------------------------------------------------
    def _show_message(self, text: str, msg_type: str = "info"):
        """Show a temporary status message at the bottom."""
        color = "#22c55e" if "✅" in text else "#f59e0b" if msg_type == "warning" else "#94a3b8"

        msg = ctk.CTkLabel(
            self, text=text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color,
            fg_color="#1a1a2e",
            corner_radius=8,
            height=36,
        )
        msg.place(relx=0.5, rely=0.96, anchor="center")
        self.after(3000, msg.destroy)


# ============================================================
# Entry Point
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  EventPulse — College Event Reminder")
    print("  Libraries: customtkinter, tkcalendar, plyer")
    print("=" * 50)
    print("  Starting application...")

    app = EventPulseApp()
    app.mainloop()
