import json
from datetime import datetime

file = "events.json"

def load_events():
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return []

def save_events(events):
    with open(file, "w") as f:
        json.dump(events, f)

def add_event():
    name = input("Enter event name: ")
    date = input("Enter event date (YYYY-MM-DD): ")

    events = load_events()
    events.append({"name": name, "date": date})
    save_events(events)

    print("Event added successfully!")

def show_events():
    events = load_events()

    if not events:
        print("No events found")
        return

    print("\nUpcoming Events:")
    for e in events:
        print(e["name"], "-", e["date"])

def next_event():
    events = load_events()
    today = datetime.today()

    upcoming = []

    for e in events:
        event_date = datetime.strptime(e["date"], "%Y-%m-%d")
        if event_date >= today:
            upcoming.append((event_date, e["name"]))

    if upcoming:
        upcoming.sort()
        print("Next Event:", upcoming[0][1], "on", upcoming[0][0].date())
    else:
        print("No upcoming events")

while True:
    print("\n1 Add Event")
    print("2 Show Events")
    print("3 Next Event Reminder")
    print("4 Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        add_event()
    elif choice == "2":
        show_events()
    elif choice == "3":
        next_event()
    elif choice == "4":
        break