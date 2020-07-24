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

ctk.set_appearance_mode("Dark")  # Dark mode
ctk.set_default_color_theme("dark-blue")  # Modern theme

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
        field_var.set(value[:i])  # Partial text for effect
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

    loading_label.configure(text="Looking up IP...")
    time.sleep(0.05)  # Slight delay for animation

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

        # Update map with fade
        update_map(response.location.latitude, response.location.longitude, ip)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to lookup IP:\n{e}")
    finally:
        loading_label.configure(text="")

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
    """Update map with fade effect."""
    html_map_label.set_html("<p>Updating map...</p>")  # fade-out effect
    m = folium.Map(location=[lat, lon], zoom_start=8)
    folium.Marker([lat, lon], tooltip=f"IP: {ip}\nLat:{lat} Lon:{lon}", popup=f"IP: {ip}").add_to(m)
    m.save(MAP_FILE)
    time.sleep(0.2)  # small transition delay
    with open(MAP_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_map_label.set_html(html_content)

# ----------------- GUI ----------------- #
root = ctk.CTk()
root.title("Offline AI IP Tracker")
root.geometry("620x750")

# Main frame
frame = ctk.CTkFrame(root, corner_radius=15)
frame.pack(fill="both", expand=True, padx=20, pady=20)

# Top row: IP input + buttons
ip_frame = ctk.CTkFrame(frame, corner_radius=10)
ip_frame.pack(fill="x", pady=(10, 15), padx=10)

ctk.CTkLabel(ip_frame, text="IP Address:").pack(side="left", padx=(10,5))
ip_entry = ctk.CTkEntry(ip_frame, width=200)
ip_entry.pack(side="left", padx=(0,10))

detect_btn = ctk.CTkButton(ip_frame, text="Detect My IP", command=detect_my_ip, width=120, fg_color="#1f6aa5", hover_color="#3a86ff")
detect_btn.pack(side="left", padx=5)

lookup_btn = ctk.CTkButton(ip_frame, text="Check IP", command=lookup_ip, width=100, fg_color="#1f6aa5", hover_color="#3a86ff")
lookup_btn.pack(side="left", padx=5)

# Loading label
loading_label = ctk.CTkLabel(frame, text="", text_color="orange")
loading_label.pack(pady=5)

# Output fields frame
output_frame = ctk.CTkFrame(frame, corner_radius=10)
output_frame.pack(fill="x", padx=10, pady=10)

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

for label, var in fields:
    row = ctk.CTkFrame(output_frame)
    row.pack(fill="x", pady=3, padx=5)
    ctk.CTkLabel(row, text=f"{label}: ", width=120, anchor="w").pack(side="left")
    ctk.CTkEntry(row, textvariable=var, state="readonly").pack(side="left", fill="x", expand=True)

# Embedded HTML map
html_map_label = HTMLLabel(frame, html="<p>Map preview will appear here</p>", width=580, height=350)
html_map_label.pack(pady=15)

root.mainloop()
