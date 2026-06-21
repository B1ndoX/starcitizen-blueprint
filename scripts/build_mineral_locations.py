#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
API_BASE = "https://api.uexcorp.uk/2.0"
SG_MINING_URL = "https://sg-mining-finder.pages.dev/"

RESOURCE_FILES = {
    "commodities": "commodities",
    "starSystems": "star_systems",
    "planets": "planets",
    "moons": "moons",
    "pointsOfInterest": "poi",
    "orbits": "orbits",
    "spaceStations": "space_stations",
}

MATERIAL_ALIASES = {
    "Pressurized Ice": "Ice",
}

NAME_ZH = {
    "Nyx": "尼克斯",
    "Pyro": "派罗",
    "Stanton": "斯坦顿",
    "ArcCorp": "弧光星",
    "Hurston": "赫斯顿",
    "MicroTech": "微科星",
    "microTech": "微科星",
    "Crusader": "十字军",
    "Pyro I": "派罗 I",
    "Monox": "莫诺克斯",
    "Bloom": "盛放星",
    "Pyro IV": "派罗 IV",
    "Pyro V": "派罗 V",
    "Terminus": "终点",
    "Delamar": "戴拉玛",
    "Aberdeen": "阿伯丁",
    "Adir": "阿迪尔",
    "Arial": "阿里尔",
    "Calliope": "卡利俄珀",
    "Cellin": "塞林",
    "Clio": "克利俄",
    "Daymar": "戴玛",
    "Euterpe": "欧忒耳佩",
    "Fairo": "法伊罗",
    "Fuego": "福埃戈",
    "Ignis": "伊格尼斯",
    "Ita": "伊塔",
    "Lyria": "莱里亚",
    "Magda": "玛格达",
    "Vatra": "瓦特拉",
    "Vuur": "武尔",
    "Wala": "瓦拉",
    "Yela": "耶拉",
    "Aaron Halo": "亚伦环",
    "Keeger Belt": "基格带",
    "Glaciem Ring": "冰川环",
    "Pyro Asteroid Clusters": "派罗小行星群",
    "Pyro Clusters": "派罗小行星群",
    "OV Breaker Stations": "OV 破碎站",
    "Akiro Cluster Alpha": "亚基罗星团 Alpha",
    "Akiro Cluster": "亚基罗星团",
    "Yela Ring": "耶拉环带",
}

LAGRANGE_PREFIX = {
    "ArcCorp": "ARC",
    "Crusader": "CRU",
    "Hurston": "HUR",
    "microTech": "MIC",
}

STATION_ZH = {
    "ARC-L1 Wide Forest Station": "弧L1 广袤森林站",
    "CRU-L1 Ambitious Dream Station": "十L1 雄心伟梦站",
    "CRU-L4 Shallow Fields Station": "十L4 轻浅田野站",
    "HUR-L1 Green Glade Station": "赫L1 绿色林地",
    "HUR-L2 Faithful Dream Station": "赫L2 坚贞梦想站",
    "HUR-L4 Melodic Fields Station": "赫L4 旋律领域站",
    "MIC-L2 Long Forest Station": "微L2 长林站",
    "MIC-L5 Modern Icarus Station": "微L5 现代伊卡洛斯站",
}


def fetch_resource(resource: str) -> list[dict]:
    req = Request(f"{API_BASE}/{resource}/", headers={"User-Agent": "A-Yuan-Blueprint-Atlas/1.0"})
    with urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("status") != "ok":
        raise RuntimeError(f"UEX API returned {payload.get('status')} for {resource}")
    return payload["data"]


def fetch_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "A-Yuan-Blueprint-Atlas/1.0"})
    with urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", "ignore")


def ids(value: object) -> list[int]:
    if value in (None, ""):
        return []
    return [int(part) for part in str(value).split(",") if part.strip()]


def zh_name(name: str | None) -> str:
    if not name:
        return "未知"
    return NAME_ZH.get(name, name)


def lagrange_label(name: str, code: str | None, station: dict | None = None) -> tuple[str, str]:
    if station:
        station_name = station.get("name") or name
        return STATION_ZH.get(station_name) or station.get("nickname") or zh_name(station_name), station_name
    for prefix, short in LAGRANGE_PREFIX.items():
        marker = f"{prefix} Lagrange Point "
        if name.startswith(marker):
            number = name.removeprefix(marker)
            return f"{short}-L{number}", name
    if code:
        return code, name
    return zh_name(name), name


def location_entry(item: dict, kind: str, station_by_orbit: dict[int, dict] | None = None) -> dict:
    name = item.get("nickname") or item.get("name") or "Unknown"
    if kind == "lagrangePoints":
        zh, en = lagrange_label(name, item.get("code"), (station_by_orbit or {}).get(item.get("id")))
    else:
        en = name
        zh = zh_name(name)
    return {
        "id": item.get("id"),
        "zh": zh,
        "en": en,
        "systemZh": zh_name(item.get("star_system_name")),
        "systemEn": item.get("star_system_name") or "",
        "parentZh": zh_name(item.get("planet_name") or item.get("orbit_name")),
        "parentEn": item.get("planet_name") or item.get("orbit_name") or "",
    }


def first_with_locations(candidates: list[dict | None]) -> dict | None:
    for candidate in candidates:
        if not candidate:
            continue
        if any(candidate.get(field) for field in ("ids_star_systems", "ids_planets", "ids_moons", "ids_poi", "ids_orbits")):
            return candidate
    return next((candidate for candidate in candidates if candidate), None)


def raw_commodity_for(name: str, by_name: dict[str, dict], by_id: dict[int, dict]) -> dict | None:
    base = MATERIAL_ALIASES.get(name, name)
    current = by_name.get(base) or by_name.get(name)
    candidates: list[dict | None] = []
    if current:
        if current.get("is_raw"):
            candidates.append(current)
        candidates.append(by_id.get(current.get("id_parent")))
    for suffix in (" (Raw)", " (Ore)", " (Pure)"):
        candidates.append(by_name.get(base + suffix))
    return first_with_locations(candidates) or current


def load_signal_calibration() -> dict:
    path = DATA_DIR / "mineral-signal-calibration.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def js_object_source(html: str, const_name: str) -> str:
    marker = f"const {const_name} = "
    start = html.index(marker) + len(marker)
    while start < len(html) and html[start].isspace():
        start += 1
    opening = html[start]
    closing = "}" if opening == "{" else "]"
    depth = 0
    in_string: str | None = None
    escaped = False
    for index in range(start, len(html)):
        char = html[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == in_string:
                in_string = None
            continue
        if char in ("'", '"'):
            in_string = char
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return html[start : index + 1]
    raise ValueError(f"Unable to parse {const_name}")


def strip_js_comments(source: str) -> str:
    return re.sub(r"//.*", "", source)


def normalize_sg_location_code(code: str) -> str:
    return re.sub(r"-\d+$", "", code)


def load_sg_mining_data() -> dict:
    try:
        html = fetch_text(SG_MINING_URL)
        location_names = json.loads(js_object_source(html, "LOCATION_NAMES"))
        ship_data = json.loads(strip_js_comments(js_object_source(html, "SHIP_DATA_47")))
        radar_source = js_object_source(html, "RADAR_DATA")
    except Exception:
        return {"locationsByName": {}, "shipData": {}, "radar": {}}

    radar: dict[str, dict] = {}
    for match in re.finditer(r"name:\s*'([^']+)'\s*,\s*rs:\s*(\d+).*?maxCluster:\s*(\d+)", radar_source, re.S):
        name, base, max_cluster = match.groups()
        radar[name.upper()] = {
            "base": int(base),
            "maxCluster": int(max_cluster),
            "values": [int(base) * count for count in range(1, int(max_cluster) + 1)],
        }
    radar["ALUMINUM"] = radar.get("ALUMINIUM", {})

    locations_by_name = {value: normalize_sg_location_code(key) for key, value in location_names.items()}
    locations_by_name["Yela Ring"] = "YELB"
    locations_by_name["Yela Belt"] = "YELB"
    locations_by_name["Glaciem Ring"] = "GLACIUM"
    locations_by_name["Pyro Clusters"] = "PYRO_DEEP"

    return {"locationsByName": locations_by_name, "shipData": ship_data, "radar": radar}


def sg_ore_key(material_name: str, commodity_name: str | None) -> str:
    base = MATERIAL_ALIASES.get(material_name, material_name)
    if base == "Ice" or commodity_name == "Ice (Raw)":
        return "ICE"
    if base == "Aluminum":
        return "ALUMINUM"
    if base in {"Quantainium", "Quantanium"}:
        return "QUANTANIUM"
    return re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_").upper()


def location_code_for_signal(location: dict, sg_data: dict) -> str | None:
    en = location.get("en") or ""
    zh = location.get("zh") or ""
    if en in sg_data["locationsByName"]:
        return sg_data["locationsByName"][en]
    if zh in sg_data["shipData"]:
        return zh
    code_match = re.match(r"([A-Z]{3}-L\d)\b", en) or re.match(r"([A-Z]{3}-L\d)\b", zh)
    if code_match and code_match.group(1) in sg_data["shipData"]:
        return code_match.group(1)
    return None


def signal_for_location(location: dict, ore_key: str, sg_data: dict) -> dict | None:
    code = location_code_for_signal(location, sg_data)
    if not code:
        return None
    row = next((item for item in sg_data["shipData"].get(code, []) if item[0] == ore_key), None)
    radar = sg_data["radar"].get(ore_key)
    if not row or not radar:
        return None
    return {
        "values": radar["values"],
        "base": radar["base"],
        "maxCluster": radar["maxCluster"],
        "probability": row[1],
        "sourceLocation": code,
    }


def annotate_location_signals(groups: dict[str, list[dict]], ore_key: str, sg_data: dict) -> None:
    for locations in groups.values():
        for location in locations:
            signal = signal_for_location(location, ore_key, sg_data)
            if signal:
                location["signal"] = signal


def main() -> None:
    resources = {key: fetch_resource(path) for key, path in RESOURCE_FILES.items()}
    lookup = {
        key: {item["id"]: item for item in value}
        for key, value in resources.items()
        if key not in {"commodities", "spaceStations"}
    }
    station_by_orbit = {
        item["id_orbit"]: item
        for item in resources["spaceStations"]
        if item.get("id_orbit")
    }
    signal_calibration = load_signal_calibration()
    sg_data = load_sg_mining_data()
    signal_by_material = signal_calibration.get("signals") or {}
    commodities = resources["commodities"]
    by_name = {item["name"]: item for item in commodities}
    by_id = {item["id"]: item for item in commodities}

    blueprint_index = json.loads((DATA_DIR / "blueprint-index.json").read_text())
    material_names = sorted({material["name"] for record in blueprint_index["records"] for tier in record.get("tiers", []) for slot in tier.get("slots", []) for material in slot.get("options", [])})

    materials: dict[str, dict] = {}
    for name in material_names:
        commodity = raw_commodity_for(name, by_name, by_id)
        groups = {
            "starSystems": [location_entry(lookup["starSystems"][item_id], "starSystems") for item_id in ids(commodity.get("ids_star_systems") if commodity else None) if item_id in lookup["starSystems"]],
            "planets": [location_entry(lookup["planets"][item_id], "planets") for item_id in ids(commodity.get("ids_planets") if commodity else None) if item_id in lookup["planets"]],
            "moons": [location_entry(lookup["moons"][item_id], "moons") for item_id in ids(commodity.get("ids_moons") if commodity else None) if item_id in lookup["moons"]],
            "pointsOfInterest": [location_entry(lookup["pointsOfInterest"][item_id], "pointsOfInterest") for item_id in ids(commodity.get("ids_poi") if commodity else None) if item_id in lookup["pointsOfInterest"]],
            "lagrangePoints": [location_entry(lookup["orbits"][item_id], "lagrangePoints", station_by_orbit) for item_id in ids(commodity.get("ids_orbits") if commodity else None) if item_id in lookup["orbits"]],
        }
        ore_key = sg_ore_key(name, commodity.get("name") if commodity else None)
        annotate_location_signals(groups, ore_key, sg_data)
        materials[name] = {
            "commodityId": commodity.get("id") if commodity else None,
            "commodityName": commodity.get("name") if commodity else None,
            "commodityCode": commodity.get("code") if commodity else None,
            "sourceUrl": f"https://uexcorp.space/mining/locations/commodity/{(commodity.get('name') or name).lower().replace(' ', '-').replace('(', '').replace(')', '')}/" if commodity else "",
            "locations": groups,
            "signal": signal_by_material.get(name) or {},
            "hasReliableLocations": any(groups.values()),
        }

    output = {
        "metadata": {
            "name": "Star Citizen mineral locations",
            "source": "UEX API 2.0",
            "sourceUrl": "https://api.uexcorp.uk/2.0/",
            "signalSource": signal_calibration.get("source", ""),
            "locationSignalSource": SG_MINING_URL,
            "signalUpdatedAt": signal_calibration.get("updatedAt", ""),
            "retrievedAt": datetime.now(timezone.utc).isoformat(),
            "note": "UEX data is community-maintained and may not reflect live servers. Empty entries are shown as no reliable mining location instead of inferred locations.",
        },
        "materials": materials,
    }
    (DATA_DIR / "mineral-locations.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
