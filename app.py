import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "https://ipapi.co/{}/json/"

def lookup_ip():
    ip = ip_entry.get().strip()

    if not ip:
        messagebox.showerror("Error", "Please enter an IP address.")
        return

    try:
        response = requests.get(API_URL.format(ip), timeout=5)
        data = response.json()

        if "error" in data:
            messagebox.showerror("Lookup Error", data.get("reason", "Unknown error"))
            return

        # Update UI fields
        country_var.set(data.get("country_name", ""))
        region_var.set(data.get("region", ""))
        city_var.set(data.get("city", ""))
        postal_var.set(data.get("postal", ""))
        latitude_var.set(data.get("latitude", ""))
        longitude_var.set(data.get("longitude", ""))

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data:\n{e}")


# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("IP Information Lookup")
root.geometry("400x350")
root.resizable(False, False)

frame = ttk.Frame(root, padding=15)
frame.pack(fill="both", expand=True)

# Input: IP Address
ttk.Label(frame, text="IP Address:").grid(row=0, column=0, sticky="w")
ip_entry = ttk.Entry(frame, width=30)
ip_entry.grid(row=0, column=1, padx=5, pady=5)

lookup_button = ttk.Button(frame, text="Lookup", command=lookup_ip)
lookup_button.grid(row=0, column=2, padx=5)

# Output fields
country_var = tk.StringVar()
region_var = tk.StringVar()
city_var = tk.StringVar()
postal_var = tk.StringVar()
latitude_var = tk.StringVar()
longitude_var = tk.StringVar()

fields = [
    ("Country", country_var),
    ("Region", region_var),
    ("City", city_var),
    ("Postal Code", postal_var),
    ("Latitude", latitude_var),
    ("Longitude", longitude_var),
]

row_index = 1
for label, variable in fields:
    ttk.Label(frame, text=f"{label}:").grid(row=row_index, column=0, sticky="w", pady=3)
    ttk.Entry(frame, textvariable=variable, width=30, state="readonly").grid(row=row_index, column=1, padx=5)
    row_index += 1

root.mainloop()
