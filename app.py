import customtkinter as ctk
from tkinter import messagebox
import ipaddress
import geoip2.database
import folium
import socket
import threading
import os
from multiprocessing import Process
import requests
import time

# ---------------- CONFIG ---------------- #
DATABASE_PATH = "GeoLite2-City.mmdb"
MAP_FILE = "ip_map.html"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ---------------- FUNCTIONS ---------------- #
def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def animate_field_update(field_var, value):
    """Animate text typing in entry field"""
    field_var.set("")
    def update_char(i=0):
        if i <= len(value):
            field_var.set(value[:i])
            root.after(50, update_char, i+1)
    update_char()

def generate_map(lat, lon, ip):
    """Generate Folium map HTML"""
    m = folium.Map(location=[lat, lon], zoom_start=8)
    folium.Marker([lat, lon], tooltip=f"IP: {ip}", popup=f"IP: {ip}").add_to(m)
    m.save(MAP_FILE)

# ---------------- MAP PROCESS ---------------- #
map_process = None
map_window = None  # Reference to the PyWebview window

def run_webview():
    """Start PyWebview and keep reference to window"""
    import webview
    global map_window
    map_window = webview.create_window("IP Map", os.path.abspath(MAP_FILE), width=700, height=500, resizable=True)
    webview.start(debug=False)

def open_map_window(lat=0, lon=0, ip="N/A"):
    """Generate or refresh map and update webview window if running"""
    global map_process, map_window

    # Generate latest map HTML
    generate_map(lat, lon, ip)

    # Start PyWebview if not running
    if map_process is None or not map_process.is_alive():
        map_process = Process(target=run_webview)
        map_process.start()
    else:
        # Refresh existing window
        if map_window:
            try:
                import webview
                map_window.load_url(os.path.abspath(MAP_FILE))
            except Exception:
                # Fallback if refresh fails
                map_process.terminate()
                map_process = Process(target=run_webview)
                map_process.start()

# ---------------- IP LOOKUP ---------------- #
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

        # Animate updates for all fields
        for var, val in zip(
            [country_var, region_var, city_var, postal_var, latitude_var, longitude_var],
            [response.country.name, response.subdivisions.most_specific.name, response.city.name,
             response.postal.code, str(response.location.latitude), str(response.location.longitude)]
        ):
            animate_field_update(var, val or "N/A")

        # Refresh map
        open_map_window(response.location.latitude, response.location.longitude, ip)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to lookup IP:\n{e}")
    finally:
        loading_label.configure(text="")

def lookup_ip():
    threading.Thread(target=lookup_ip_thread, daemon=True).start()

# ---------------- DETECT PUBLIC IP ---------------- #
def detect_my_ip():
    loading_label.configure(text="Detecting public IP...")
    
    def detect_thread():
        try:
            try:
                ip = requests.get("https://api.ipify.org", timeout=5).text.strip()
            except requests.RequestException:
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)

            # Update entry safely
            def update_entry():
                ip_entry.delete(0, "end")
                ip_entry.insert(0, ip)
            root.after(0, update_entry)

            # Lookup IP info
            lookup_ip_thread()
        finally:
            root.after(0, lambda: loading_label.configure(text=""))

    threading.Thread(target=detect_thread, daemon=True).start()

# ---------------- THEME ---------------- #
def toggle_theme():
    current = ctk.get_appearance_mode()
    ctk.set_appearance_mode("Light" if current=="Dark" else "Dark")

# ---------------- GUI ---------------- #
root = ctk.CTk()
root.title("Modern AI IP Tracker")
root.geometry("900x850")

# ---------- Main Frame ---------- #
main_frame = ctk.CTkFrame(root, corner_radius=15)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# ---------- Top Bar ---------- #
top_bar1 = ctk.CTkFrame(main_frame, corner_radius=10)
top_bar1.pack(fill="x", pady=(10,5), padx=10)

ctk.CTkLabel(top_bar1, text="IP Address:").pack(side="left", padx=(10,5))
ip_entry = ctk.CTkEntry(top_bar1, width=250)
ip_entry.pack(side="left", padx=(0,10))

detect_btn = ctk.CTkButton(top_bar1, text="Detect My IP", command=detect_my_ip, width=120, fg_color="#1f6aa5", hover_color="#3a86ff")
detect_btn.pack(side="left", padx=5)

lookup_btn = ctk.CTkButton(top_bar1, text="Check IP", command=lookup_ip, width=100, fg_color="#1f6aa5", hover_color="#3a86ff")
lookup_btn.pack(side="left", padx=5)

top_bar2 = ctk.CTkFrame(main_frame, corner_radius=10)
top_bar2.pack(fill="x", pady=(0,10), padx=10)

theme_btn = ctk.CTkButton(top_bar2, text="Toggle Theme", command=toggle_theme, width=120)
theme_btn.pack(side="left", padx=5)

map_btn = ctk.CTkButton(top_bar2, text="Open Map", command=open_map_window, width=120, fg_color="#1f6aa5", hover_color="#3a86ff")
map_btn.pack(side="left", padx=5)

# ---------- Loading Label ---------- #
loading_label = ctk.CTkLabel(main_frame, text="", text_color="orange")
loading_label.pack(pady=5)

# ---------- Info Panel ---------- #
info_panel = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1f1f2e", border_width=1, border_color="#3a86ff")
info_panel.pack(fill="x", padx=20, pady=15)

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
    row = ctk.CTkFrame(info_panel, corner_radius=10, fg_color="#2a2a3d")
    row.pack(fill="x", pady=5, padx=10)
    ctk.CTkLabel(row, text=f"{label}: ", width=120, anchor="w").pack(side="left")
    ctk.CTkEntry(row, textvariable=var, state="readonly").pack(side="left", fill="x", expand=True)

# ---------- Footer ---------- #
footer_label = ctk.CTkLabel(main_frame, text="Modern AI Offline IP Tracker", text_color="#3a86ff")
footer_label.pack(pady=10)

# ---------- Handle Close ---------- #
def on_close():
    global map_process
    if map_process and map_process.is_alive():
        map_process.terminate()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# ---------- Start GUI ---------- #
root.mainloop()
