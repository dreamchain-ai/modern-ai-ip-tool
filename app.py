import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import ipaddress
import geoip2.database
import folium
import webview
import os
import threading

# ----------------- CONFIG ----------------- #
DATABASE_PATH = "GeoLite2-City.mmdb"
MAP_FILE = "ip_map.html"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ----------------- FUNCTIONS ----------------- #
def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def lookup_ip():
    ip = ip_entry.get().strip()
    if not ip:
        messagebox.showerror("Error", "Please enter an IP address.")
        return
    if not validate_ip(ip):
        messagebox.showerror("Error", "Invalid IP address format.")
        return

    try:
        reader = geoip2.database.Reader(DATABASE_PATH)
        response = reader.city(ip)
        reader.close()

        country_var.set(response.country.name or "N/A")
        region_var.set(response.subdivisions.most_specific.name or "N/A")
        city_var.set(response.city.name or "N/A")
        postal_var.set(response.postal.code or "N/A")
        latitude_var.set(response.location.latitude or 0)
        longitude_var.set(response.location.longitude or 0)

        update_map(response.location.latitude, response.location.longitude, ip)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to lookup IP:\n{e}")

def detect_my_ip():
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    ip_entry.delete(0, "end")
    ip_entry.insert(0, local_ip)
    lookup_ip()

def update_map(lat, lon, ip):
    if lat is None or lon is None:
        messagebox.showinfo("Map", "No location data available for this IP.")
        return

    # Generate folium map
    m = folium.Map(location=[lat, lon], zoom_start=8)
    folium.Marker(
        [lat, lon],
        tooltip=f"IP: {ip}\nLat:{lat} Lon:{lon}",
        popup=f"IP: {ip}"
    ).add_to(m)
    m.save(MAP_FILE)

    # Open map in PyWebview inside a new thread
    threading.Thread(target=open_map_window, daemon=True).start()

def open_map_window():
    # PyWebview window (fully offline)
    webview.create_window("IP Map", os.path.abspath(MAP_FILE))
    webview.start(gui='tk')  # Uses Tkinter as backend

# ----------------- GUI ----------------- #
root = ctk.CTk()
root.title("Offline AI IP Tracker")
root.geometry("500x500")

frame = ctk.CTkFrame(root, corner_radius=15)
frame.pack(fill="both", expand=True, padx=20, pady=20)

# IP Entry
ctk.CTkLabel(frame, text="IP Address:").grid(row=0, column=0, sticky="w")
ip_entry = ctk.CTkEntry(frame, width=200)
ip_entry.grid(row=0, column=1, padx=5, pady=5)

detect_btn = ctk.CTkButton(frame, text="Detect My IP", command=detect_my_ip)
detect_btn.grid(row=0, column=2, padx=5)

lookup_btn = ctk.CTkButton(frame, text="Lookup", command=lookup_ip)
lookup_btn.grid(row=1, column=1, pady=10)

# Output fields
country_var = ctk.StringVar()
region_var = ctk.StringVar()
city_var = ctk.StringVar()
postal_var = ctk.StringVar()
latitude_var = ctk.StringVar()
longitude_var = ctk.StringVar()

fields = [
    ("Country", country_var),
    ("Region", region_var),
    ("City", city_var),
    ("Postal Code", postal_var),
    ("Latitude", latitude_var),
    ("Longitude", longitude_var),
]

row_index = 2
for label, var in fields:
    ctk.CTkLabel(frame, text=f"{label}:").grid(row=row_index, column=0, sticky="w", pady=5)
    ctk.CTkEntry(frame, textvariable=var, state="readonly", width=250).grid(row=row_index, column=1, columnspan=2, padx=5, pady=5)
    row_index += 1

# Info Label
ctk.CTkLabel(frame, text="Interactive map will open in a new window.", text_color="gray").grid(row=row_index, column=0, columnspan=3, pady=10)

root.mainloop()
