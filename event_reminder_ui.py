import tkinter as tk
from tkinter import messagebox
import json

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
    name = name_entry.get()
    date = date_entry.get()

    events = load_events()
    events.append({"name": name, "date": date})
    save_events(events)

    messagebox.showinfo("Success", "Event Added!")

    name_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)

def show_events():
    events = load_events()

    event_list.delete(0, tk.END)

    for e in events:
        event_list.insert(tk.END, f"{e['name']} - {e['date']}")

root = tk.Tk()
root.title("College Event Reminder")
root.geometry("400x400")

title = tk.Label(root, text="College Event Reminder", font=("Arial", 16))
title.pack(pady=10)

name_label = tk.Label(root, text="Event Name")
name_label.pack()

name_entry = tk.Entry(root)
name_entry.pack()

date_label = tk.Label(root, text="Event Date (YYYY-MM-DD)")
date_label.pack()

date_entry = tk.Entry(root)
date_entry.pack()

add_button = tk.Button(root, text="Add Event", command=add_event)
add_button.pack(pady=10)

show_button = tk.Button(root, text="Show Events", command=show_events)
show_button.pack()

event_list = tk.Listbox(root, width=40)
event_list.pack(pady=20)

root.mainloop()