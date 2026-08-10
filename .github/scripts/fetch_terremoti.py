#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scarica gli ultimi terremoti rilevati dalla Rete Sismica Nazionale (INGV)
e scrive terremoti.json: l'istantanea pubblicata su GitHub Pages.

La pagina index.html però NON dipende da questo snapshot: carica i dati
in tempo reale dall'API INGV direttamente dal browser (CORS permesso),
e usa terremoti.json solo come fallback se la rete è giù.
"""
import json
import math
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

API = "https://webservices.ingv.it/fdsnws/event/1/query"
HOURS = 48            # finestra temporale dello snapshot
MIN_MAG = 0.0         # minima magnitudo inclusa (INGV rileva anche molto deboli)

OUT = "terremoti.json"

# Casa: Viale delle Cascine 124, Pisa (43.7247258 N, 10.3802555 E)
HOME_LAT, HOME_LON = 43.7247258, 10.3802555

# 16 settori della rosa dei venti in senso orario da nord
_DIRS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
         "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]


def haversine_km(lat1, lon1, lat2, lon2):
    """Distanza in km tra due coordinate (Haversine)."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def bearing_deg(lat1, lon1, lat2, lon2):
    """Azimut da nord (orario, 0-360) dal punto 1 al punto 2."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = (math.cos(p1) * math.sin(p2)
         - math.sin(p1) * math.cos(p2) * math.cos(dl))
    return (math.degrees(math.atan2(x, y)) + 360.0) % 360.0


def direction_deg(bearing):
    """Settore della rosa dei venti (16 direzioni) per un azimut."""
    i = int((bearing + 11.25) // 22.5) % 16
    return _DIRS[i]


def fetch_events(start, end, minmag):
    params = {
        "format": "geojson",
        "starttime": start,
        "endtime": end,
        "minmag": str(minmag),
        "eventtype": "earthquake",
        # area: Italia e mari circostanti
        "minlat": "35.5", "maxlat": "47.5", "minlon": "6.0", "maxlon": "19.5",
        "orderby": "time",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "terremoti-pisa/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=HOURS)
    data = fetch_events(
        start.strftime("%Y-%m-%dT%H:%M:%S"),
        now.strftime("%Y-%m-%dT%H:%M:%S"),
        MIN_MAG,
    )

    events = []
    for f in data.get("features", []):
        p = f.get("properties", {})
        g = f.get("geometry", {}).get("coordinates", [None, None, None])
        mag = p.get("mag")
        if mag is None:
            continue
        lat = g[1] if len(g) > 1 else None
        lon = g[0] if g else None
        dist = haversine_km(HOME_LAT, HOME_LON, lat, lon) if lat is not None and lon is not None else None
        azi = bearing_deg(HOME_LAT, HOME_LON, lat, lon) if lat is not None and lon is not None else None
        events.append({
            "id": p.get("eventId"),
            "time": p.get("time"),
            "mag": float(mag),
            "magType": p.get("magType") or "ML",
            "place": (p.get("place") or "—").strip(),
            "depth": g[2] if len(g) > 2 and g[2] is not None else None,
            "lat": lat,
            "lon": lon,
            "type": p.get("type", "earthquake"),
            "distKm": round(dist, 1) if dist is not None else None,
            "azimut": round(azi, 1) if azi is not None else None,
            "dir": direction_deg(azi) if azi is not None else None,
        })

    events.sort(key=lambda e: e["time"], reverse=True)

    mags = [e["mag"] for e in events if e["mag"] is not None]
    depths = [e["depth"] for e in events if e["depth"] is not None]
    dists = [e["distKm"] for e in events if e.get("distKm") is not None]
    snapshot = {
        "generated": now.isoformat(),
        "windowHours": HOURS,
        "count": len(events),
        "maxmag": max(mags) if mags else None,
        "avgDepth": round(sum(depths) / len(depths), 1) if depths else None,
        "home": {"lat": HOME_LAT, "lon": HOME_LON, "label": "Viale delle Cascine 124, Pisa"},
        "closest": min(dists) if dists else None,
        "events": events,
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, ensure_ascii=False, indent=1)
    print(f"[ok] {len(events)} eventi ({start:%Y-%m-%d %H:%M} → {now:%H:%M} UTC), max M{snapshot['maxmag']} → {OUT}")


if __name__ == "__main__":
    main()