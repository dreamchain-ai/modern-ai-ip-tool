import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import ipaddress
import folium
import os
from io import BytesIO
from PIL import Image, ImageTk

ctk.set_appearance_mode("Dark")  # Dark mode
ctk.set_default_color_theme("blue")  # Accent color

# ----------------- Functions ----------------- #
def validate_ip(ip):
    """Check if the input is a valid IP address"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def lookup_ip():
    """Lookup IP information offline"""
    ip = ip_entry.get().strip()
    if not ip:
        messagebox.showerror("Error", "Please enter an IP address.")
        return
    if not validate_ip(ip):
        messagebox.showerror("Error", "Invalid IP address format.")
        return

    # Offline info
    country_var.set("N/A")
    region_var.set("N/A")
    city_var.set("N/A")
    postal_var.set("N/A")
    latitude_var.set("0")
    longitude_var.set("0")

    update_map(0, 0, ip)

def detect_my_ip():
    """Detect local IP (offline)"""
    # We can only detect private IP offline
    import socket
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        ip_entry.delete(0, "end")
        ip_entry.insert(0, local_ip)
        lookup_ip()
    except:
        messagebox.showerror("Error", "Unable to detect local IP.")

def update_map(lat, lon, ip):
    """Generate offline map centered at coordinates"""
    m = folium.Map(location=[lat, lon], zoom_start=2)
    folium.Marker([lat, lon], tooltip=f"IP: {ip}\nLat:{lat} Lon:{lon}", popup=f"IP: {ip}").add_to(m)

    # Save map as HTML
    map_path = "map.html"
    m.save(map_path)

    # Render static image from HTML using PIL placeholder
    # Fully offline, cannot render interactive map without browser engine
    map_label.configure(text=f"Map centered at ({lat},{lon})\nInteractive map requires browser", image="", width=450, height=300)

# ----------------- GUI ----------------- #
root = ctk.CTk()
root.title("Offline AI-Style IP Tracker")
root.geometry("500x600")

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

# Map display placeholder
map_label = ctk.CTkLabel(frame, text="Map will appear here", width=450, height=300)
map_label.grid(row=row_index, column=0, columnspan=3, pady=15)

root.mainloop()
