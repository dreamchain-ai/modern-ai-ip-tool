# modern-ai-ip-tool
Modern AI-style desktop app for looking up and visualizing IP address information.

Built with **Python** and **CustomTkinter**, this tool lets you:

- Validate IPv4 addresses
- Detect your own public IP
- Look up GeoIP information (country, region, city, postal code, coordinates)
- Open an interactive map in your browser centered on the IP location

The UI mimics a modern "AI app" aesthetic with dark/light themes and smooth field updates.

---

## Features

- **Modern desktop UI**
  - Built using `customtkinter` for a clean, dark/light theme interface.
  - Responsive layout with animated field updates when results are loaded.

- **IP validation & lookup**
  - Validates IP format before lookup.
  - Uses a local GeoIP2 database to resolve:
    - Country
    - Region / subdivision
    - City
    - Postal code
    - Latitude & longitude

- **Detect my IP**
  - Tries `https://api.ipify.org` to detect your public IP.
  - Falls back to local hostname resolution if the external API is not reachable.

- **Map visualization**
  - Generates `ip_map.html` with a pin at the resolved coordinates.
  - Opens the map in your default browser.

---

## Project Structure

Key files and folders:

- `app.py` – Main GUI application.
- `src/config.py` – Shared configuration, including GeoIP database path.
- `src/ip_utils.py` – IP validation helpers.
- `src/map_utils.py` – Map generation (e.g. writing `ip_map.html` and opening it in a browser).
- `db/` – Expected location of the GeoIP2 database file.
- `ip_map.html` – Generated map file (overwritten on each lookup).

---

## Requirements

- **Python** 3.9+ (other 3.x may work but is not guaranteed).
- A **GeoIP2 city database** file (e.g. `GeoLite2-City.mmdb`) placed under the `db/` directory.

Python packages (typical):

- `customtkinter`
- `geoip2`
- `requests`

You can install dependencies with:

```bash
pip install customtkinter geoip2 requests
```

If you are using a virtual environment, make sure it is activated before installing and running.

---

## GeoIP Database Setup

1. **Download a GeoIP2/GeoLite2 City database** from MaxMind.
2. Place the `.mmdb` file inside the `db/` directory of this project.
3. Ensure that `src/config.py` points to the correct path, for example:

   ```python
   # src/config.py
   DATABASE_PATH = "db/GeoLite2-City.mmdb"
   ```

4. Without this file, lookups will fail with an error when `geoip2.database.Reader` is used.

---

## Running the App

1. **Clone** the repository or download the source.
2. (Optional) Create and activate a virtual environment.
3. **Install dependencies**:

   ```bash
   pip install customtkinter geoip2 requests
   ```

4. **Configure the GeoIP database** as described above.
5. **Run the app** from the project root:

   ```bash
   python app.py
   ```

The main window should open with fields for IP entry, a *Detect My IP* button, and read-only fields for location information.

---

## Usage

- **Check a specific IP**
  - Type an IPv4 address into the `IP Address` field.
  - Click **Check IP**.
  - The fields for Country, Region, City, Postal Code, Latitude and Longitude will update.
  - A browser window/tab will open showing a map centered on the IP location.

- **Detect your own public IP**
  - Click **Detect My IP**.
  - The app will:
    - Try to get your public IP from `https://api.ipify.org`.
    - Fall back to your machine’s hostname/IP if the external call fails.
  - It will then automatically perform a lookup on that IP.

- **Toggle theme**
  - Click **Toggle Theme** to switch between dark and light appearance modes.

---

## Troubleshooting

- **"Failed to lookup IP" error**
  - Check that the `.mmdb` database file exists in `db/`.
  - Confirm that `DATABASE_PATH` in `src/config.py` matches the actual file name.
  - Ensure you have installed the `geoip2` package.

- **App window does not start**
  - Ensure you are running the correct Python version (3.9+ recommended).
  - Check that `customtkinter` is installed in your active environment.

- **Map does not open**
  - Confirm that `ip_map.html` is being generated in the project root.
  - Make sure your system has a default browser configured.

---

## License

See `LICENSE` for full license text.

