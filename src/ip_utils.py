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

    return {
        "vpn": bool(data.get("vpn")) if data.get("vpn") is not None else None,
        "proxy": bool(data.get("proxy")) if data.get("proxy") is not None else None,
        "tor": bool(data.get("tor")) if data.get("tor") is not None else None,
        "hosting": bool(data.get("hosting")) if data.get("hosting") is not None else None,
    }
