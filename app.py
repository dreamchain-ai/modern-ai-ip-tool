import customtkinter as ctk
from tkinter import messagebox
import ipaddress
import geoip2.database
import folium
import webview
import threading
import os
import time

# ----------------- CONFIG ----------------- #
DATABASE_PATH = "GeoLite2-City.mmdb"
MAP_FILE = "ip_map.html"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ----------------- FUNCTIONS ----------------- #
def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def animate_field_update(field_var, value):
    field_var.set("")
    for i in range(3):
        field_var.set(value[:i])
        time.sleep(0.05)
    field_var.set(value)

def update_map(lat, lon, ip):
    """Generate Folium map and update pywebview window."""
    m = folium.Map(location=[lat, lon], zoom_start=8)
    folium.Marker([lat, lon], tooltip=f"IP: {ip}\nLat:{lat} Lon:{lon}", popup=f"IP: {ip}").add_to(m)
    m.save(MAP_FILE)

    # Reload map in webview
    if hasattr(update_map, "webview_window"):
        update_map.webview_window.load_url("file://" + os.path.abspath(MAP_FILE))

def lookup_ip_thread():
    ip = ip_entry.get().strip()
    if not ip:
        messagebox.showerror("Error", "Please enter an IP address.")
        return
    if not validate_ip(ip):
        messagebox.showerror("Error", "Invalid IP address format.")
        return

    loading_label.configure(text="Looking up IP...")
    try:
        reader = geoip2.database.Reader(DATABASE_PATH)
        response = reader.city(ip)
        reader.close()

        for var, val in zip([country_var, region_var, city_var, postal_var, latitude_var, longitude_var],
                            [response.country.name, response.subdivisions.most_specific.name, response.city.name,
                             response.postal.code, str(response.location.latitude), str(response.location.longitude)]):
            threading.Thread(target=animate_field_update, args=(var, val or "N/A"), daemon=True).start()

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

def toggle_theme():
    current = ctk.get_appearance_mode()
    ctk.set_appearance_mode("Light" if current=="Dark" else "Dark")

# ----------------- GUI ----------------- #
root = ctk.CTk()
root.title("Offline AI IP Tracker")
root.geometry("650x750")

frame = ctk.CTkFrame(root, corner_radius=15)
frame.pack(fill="both", expand=True, padx=20, pady=20)

# Top: IP Entry + buttons
top_frame = ctk.CTkFrame(frame, corner_radius=10)
top_frame.pack(fill="x", pady=(10,15), padx=10)

ctk.CTkLabel(top_frame, text="IP Address:").pack(side="left", padx=(10,5))
ip_entry = ctk.CTkEntry(top_frame, width=200)
ip_entry.pack(side="left", padx=(0,10))

detect_btn = ctk.CTkButton(top_frame, text="Detect My IP", command=detect_my_ip, width=120, fg_color="#1f6aa5", hover_color="#3a86ff")
detect_btn.pack(side="left", padx=5)

lookup_btn = ctk.CTkButton(top_frame, text="Check IP", command=lookup_ip, width=100, fg_color="#1f6aa5", hover_color="#3a86ff")
lookup_btn.pack(side="left", padx=5)

theme_btn = ctk.CTkButton(top_frame, text="Toggle Theme", command=toggle_theme, width=120)
theme_btn.pack(side="left", padx=5)

# Loading label
loading_label = ctk.CTkLabel(frame, text="", text_color="orange")
loading_label.pack(pady=5)

# Output fields
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

# ----------------- PyWebview Embedded Map ----------------- #
update_map.webview_window = webview.create_window(
    "IP Map", os.path.abspath(MAP_FILE), width=600, height=350, resizable=True, frameless=False
)

# Start Tkinter and Webview together (pywebview handles main loop)
webview.start(gui='tk', debug=False)
