import customtkinter as ctk
from tkinter import messagebox
import ipaddress
import geoip2.database
import folium
from PIL import Image, ImageTk
import threading
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ---------------- CONFIG ---------------- #
DATABASE_PATH = "GeoLite2-City.mmdb"
MAP_HTML = "ip_map.html"
MAP_PNG = "ip_map.png"

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
    field_var.set("")
    for i in range(3):
        field_var.set(value[:i])
        time.sleep(0.05)
    field_var.set(value)

def generate_map_image(lat, lon, ip):
    # Create folium map
    m = folium.Map(location=[lat, lon], zoom_start=8)
    folium.Marker([lat, lon], tooltip=f"IP: {ip}", popup=f"IP: {ip}").add_to(m)
    m.save(MAP_HTML)

    # Convert HTML to PNG using headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=650,400")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("file:///" + os.path.abspath(MAP_HTML))
    time.sleep(1)  # allow map to render
    driver.save_screenshot(MAP_PNG)
    driver.quit()

    # Load PNG into Tkinter
    img = Image.open(MAP_PNG)
    img = img.resize((600, 350), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    map_label.configure(image=photo)
    map_label.image = photo  # keep reference

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

        # Animate fields
        for var, val in zip(
            [country_var, region_var, city_var, postal_var, latitude_var, longitude_var],
            [response.country.name, response.subdivisions.most_specific.name, response.city.name,
             response.postal.code, str(response.location.latitude), str(response.location.longitude)]
        ):
            threading.Thread(target=animate_field_update, args=(var, val or "N/A"), daemon=True).start()

        # Update map image
        threading.Thread(target=generate_map_image, args=(response.location.latitude, response.location.longitude, ip), daemon=True).start()

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

# ---------------- GUI ---------------- #
root = ctk.CTk()
root.title("Offline AI IP Tracker")
root.geometry("650x800")

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

# Map image
map_label = ctk.CTkLabel(frame)
map_label.pack(pady=15)

root.mainloop()
