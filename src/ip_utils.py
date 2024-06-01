import ipaddress
import os
import requests


def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def get_proxy_vpn_info(ip):
    token = os.getenv("IPINFO_TOKEN", "").strip()
    if not token:
        return {"vpn": None, "proxy": None, "tor": None, "hosting": None}

    url = f"https://ipinfo.io/{ip}/privacy"
    try:
        resp = requests.get(url, params={"token": token}, timeout=5)
        resp.raise_for_status()
        data = resp.json() or {}
    except Exception:
        return {"vpn": None, "proxy": None, "tor": None, "hosting": None}

    # Some responses may nest privacy info under a top-level "privacy" key,
    # or may encode flags as strings/ints instead of booleans. Normalize that here.

    if isinstance(data.get("privacy"), dict):
        privacy_data = data.get("privacy", {})
    else:
        privacy_data = data

    def _normalize_flag(value):
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            # Treat any non-zero value as True
            return bool(value)
        if isinstance(value, str):
            v = value.strip().lower()
            if v in {"true", "yes", "y", "1", "on"}:
                return True
            if v in {"false", "no", "n", "0", "off"}:
                return False
        # Unknown representation
        return None

    return {
        "vpn": _normalize_flag(privacy_data.get("vpn")),
        "proxy": _normalize_flag(privacy_data.get("proxy")),
        "tor": _normalize_flag(privacy_data.get("tor")),
        "hosting": _normalize_flag(privacy_data.get("hosting")),
    }
