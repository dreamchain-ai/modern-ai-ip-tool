import folium
import os, sys
import webbrowser
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.config import MAP_FILE

ip_history = []


def generate_map(lat, lon, ip, city="", region="", country=""):
    global ip_history

    ip_history.append({
        "lat": lat,
        "lon": lon,
        "ip": ip,
        "city": city,
        "region": region,
        "country": country
    })

    m = folium.Map(location=[lat, lon], zoom_start=5)

    for idx, info in enumerate(ip_history):
        color = "red" if idx == len(ip_history) - 1 else "blue"
        folium.Marker(
            [info["lat"], info["lon"]],
            tooltip=f'IP: {info["ip"]}',
            popup=f'{info["ip"]} - {info["city"]}, {info["region"]}, {info["country"]}',
            icon=folium.Icon(color=color)
        ).add_to(m)

    abs_path = os.path.abspath(MAP_FILE)
    m.save(abs_path)

    webbrowser.open(f"file:///{abs_path.replace(os.sep, '/')}" )
