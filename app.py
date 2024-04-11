import customtkinter as ctk
from tkinter import messagebox
import geoip2.database
import socket
import threading
import requests
import time

from src.config import DATABASE_PATH
from src.ip_utils import validate_ip
from src.map_utils import generate_map

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

def animate_field_update(field_var, value):
    """Animate text typing in entry field"""
    field_var.set("")
    def update_char(i=0):
        if i <= len(value):
            field_var.set(value[:i])
            root.after(50, update_char, i+1)
    update_char()

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

        country = response.country.name or "N/A"
        region = response.subdivisions.most_specific.name or "N/A"
        city = response.city.name or "N/A"
        postal = response.postal.code or "N/A"
        latitude = response.location.latitude or 0
        longitude = response.location.longitude or 0

        # Animate updates for all fields
        for var, val in zip(
            [country_var, region_var, city_var, postal_var, latitude_var, longitude_var],
            [country, region, city, postal, str(latitude), str(longitude)]
        ):
            animate_field_update(var, val)

        # Update and open map in browser
        generate_map(latitude, longitude, ip, city, region, country)

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
root.title("Modern AI IP Tracker with Browser Map")
root.geometry("1000x550")

# ---------- Main Frame ---------- #
main_frame = ctk.CTkFrame(root, corner_radius=15)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# ---------- Top Bar ---------- #
top_bar1 = ctk.CTkFrame(main_frame, corner_radius=10)
top_bar1.pack(fill="x", pady=(10,5), padx=10)

ctk.CTkLabel(top_bar1, text="IP Address:").pack(side="left", padx=(10,5))
ip_entry = ctk.CTkEntry(top_bar1, width=250)
ip_entry.pack(side="left", padx=(0,10), fill="x", expand=True)

detect_btn = ctk.CTkButton(top_bar1, text="Detect My IP", command=detect_my_ip, width=120, fg_color="#1f6aa5", hover_color="#3a86ff")
detect_btn.pack(side="left", padx=5)

lookup_btn = ctk.CTkButton(top_bar1, text="Check IP", command=lookup_ip, width=100, fg_color="#1f6aa5", hover_color="#3a86ff")
lookup_btn.pack(side="left", padx=5)

theme_btn = ctk.CTkButton(top_bar1, text="Toggle Theme", command=toggle_theme, width=120)
theme_btn.pack(side="left", padx=5)

# ---------- Loading Label ---------- #
loading_label = ctk.CTkLabel(main_frame, text="", text_color="orange")
loading_label.pack(pady=5)

# ---------- Info Panel ---------- #
info_panel = ctk.CTkFrame(main_frame, corner_radius=15)
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
    row = ctk.CTkFrame(info_panel, corner_radius=10)
    row.pack(fill="x", pady=5, padx=10)
    ctk.CTkLabel(row, text=f"{label}: ", width=120, anchor="w").pack(side="left")
    ctk.CTkEntry(row, textvariable=var, state="readonly").pack(side="left", fill="x", expand=True)

# ---------- Footer ---------- #
footer_label = ctk.CTkLabel(main_frame, text="Modern AI IP Tracker (Browser Map)", text_color="#3a86ff")
footer_label.pack(pady=10)

# ---------- Start GUI ---------- #
root.mainloop()
