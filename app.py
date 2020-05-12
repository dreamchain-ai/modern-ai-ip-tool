import customtkinter as ctk
from tkinter import messagebox
import ipaddress
import geoip2.database
import folium
from tkhtmlview import HTMLLabel
import threading
import time
import os

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

def animate_field_update(field_var, value):
    """Brief highlight animation for updated fields."""
    field_var.set("")  # Clear field
    for i in range(3):
        field_var.set(value[:i])  # Show partial text
        time.sleep(0.05)
    field_var.set(value)

def lookup_ip_thread():
    """Threaded IP lookup to avoid blocking UI."""
    ip = ip_entry.get().strip()
    if not ip:
        messagebox.showerror("Error", "Please enter an IP address.")
        return
    if not validate_ip(ip):
        messagebox.showerror("Error", "Invalid IP address format.")
        return

    # Show loading
    loading_label.configure(text="Looking up IP...")
    time.sleep(0.1)  # Small delay for animation

    try:
        reader = geoip2.database.Reader(DATABASE_PATH)
        response = reader.city(ip)
        reader.close()

        # Animate field updates
        threading.Thread(target=animate_field_update, args=(country_var, response.country.name or "N/A"), daemon=True).start()
        threading.Thread(target=animate_field_update, args=(region_var, response.subdivisions.most_specific.name or "N/A"), daemon=True).start()
        threading.Thread(target=animate_field_update, args=(city_var, response.city.name or "N/A"), daemon=True).start()
        threading.Thread(target=animate_field_update, args=(postal_var, response.postal.code or "N/A"), daemon=True).start()
        threading.Thread(target=animate_field_update, args=(latitude_var, str(response.location.latitude or 0)), daemon=True).start()
        threading.Thread(target=animate_field_update, args=(longitude_var, str(response.location.longitude or 0)), daemon=True).start()

        # Update map with fade effect
        update_map(response.location.latitude, response.location.longitude, ip)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to lookup IP:\n{e}")
    finally:
        loading_label.configure(text="")  # Remove loading

def lookup_ip():
    threading.Thread(target=lookup_ip_thread, daemon=True).start()

def detect_my_ip():
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    ip_entry.delete(0, "end")
    ip_entry.insert(0, local_ip)
    lookup_ip()

def update_map(lat, lon, ip):
    """Update map with fade-out/fade-in animation."""
    # Fade out (simulate by clearing HTML content)
    html_map_label.set_html("<p>Updating map...</p>")

    m = folium.Map(location=[lat, lon], zoom_start=8)
    folium.Marker([lat, lon], tooltip=f"IP: {ip}\nLat:{lat} Lon:{lon}", popup=f"IP: {ip}").add_to(m)
    m.save(MAP_FILE)

    # Small delay for smooth transition
    time.sleep(0.3)

    # Load new map
    with open(MAP_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_map_label.set_html(html_content)

# ----------------- GUI ----------------- #
root = ctk.CTk()
root.title("Offline AI IP Tracker")
root.geometry("600x750")

frame = ctk.CTkFrame(root, corner_radius=15)
frame.pack(fill="both", expand=True, padx=20, pady=20)

# IP Entry
ctk.CTkLabel(frame, text="IP Address:").grid(row=0, column=0, sticky="w")
ip_entry = ctk.CTkEntry(frame, width=200)
ip_entry.grid(row=0, column=1, padx=5, pady=5)

# Animated Buttons (hover effect)
lookup_btn = ctk.CTkButton(frame, text="Lookup", command=lookup_ip)
lookup_btn.grid(row=1, column=1, pady=10)

detect_btn = ctk.CTkButton(frame, text="Detect My IP", command=detect_my_ip)
detect_btn.grid(row=0, column=2, padx=5)

# Loading label
loading_label = ctk.CTkLabel(frame, text="", text_color="orange")
loading_label.grid(row=1, column=0, columnspan=3, pady=5)

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

# Embedded HTML map
html_map_label = HTMLLabel(frame, html="<p>Map preview will appear here</p>", width=550, height=350)
html_map_label.grid(row=row_index, column=0, columnspan=3, pady=15)

root.mainloop()
