import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import requests
import ipaddress
import folium
import os
from io import BytesIO
from PIL import Image, ImageTk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

API_URL = "https://ipapi.co/{}/json/"

# ----------------- Functions ----------------- #
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

    # Try online API
    try:
        response = requests.get(API_URL.format(ip), timeout=5)
        data = response.json()
        if "error" in data:
            messagebox.showerror("Lookup Error", data.get("reason", "Unknown error"))
            return
    except:
        messagebox.showwarning("Offline", "Cannot reach API. Showing local IP info only.")
        data = {
            "country_name": "N/A",
            "region": "N/A",
            "city": "N/A",
            "postal": "N/A",
            "latitude": 0,
            "longitude": 0
        }

    # Update fields
    country_var.set(data.get("country_name", ""))
    region_var.set(data.get("region", ""))
    city_var.set(data.get("city", ""))
    postal_var.set(data.get("postal", ""))
    latitude_var.set(data.get("latitude", ""))
    longitude_var.set(data.get("longitude", ""))

    # Update map
    lat = data.get("latitude", 0)
    lon = data.get("longitude", 0)
    update_map(lat, lon, ip)

def detect_my_ip():
    try:
        ip = requests.get("https://api.ipify.org").text
        ip_entry.delete(0, "end")
        ip_entry.insert(0, ip)
        lookup_ip()
    except:
        messagebox.showerror("Error", "Unable to detect your public IP.")

def update_map(lat, lon, ip):
    # Generate folium map
    m = folium.Map(location=[lat, lon], zoom_start=8)
    folium.Marker(
        [lat, lon],
        tooltip=f"IP: {ip}\nLat:{lat} Lon:{lon}",
        popup=f"IP: {ip}"
    ).add_to(m)

    # Save map as HTML
    map_path = "map.html"
    m.save(map_path)

    # Convert HTML map to image for offline display
    # This is a simple workaround using static image
    # You need selenium or web engine for full interactive offline map
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(450, 300)
        driver.get("file://" + os.path.abspath(map_path))
        driver.save_screenshot("map.png")
        driver.quit()

        img = Image.open("map.png")
        img = img.resize((450, 300))
        img_tk = ImageTk.PhotoImage(img)
        map_label.configure(image=img_tk)
        map_label.image = img_tk
    except:
        # fallback: no interactive map, show placeholder
        map_label.configure(text="Map unavailable offline", image="", width=450, height=300)

# ----------------- GUI ----------------- #
root = ctk.CTk()
root.title("Modern AI IP Tracker")
root.geometry("500x650")

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

# Map display
map_label = ctk.CTkLabel(frame, text="Map will appear here", width=450, height=300)
map_label.grid(row=row_index, column=0, columnspan=3, pady=15)

root.mainloop()
