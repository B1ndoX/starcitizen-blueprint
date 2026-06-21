#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
API_BASE = "https://api.uexcorp.uk/2.0"

RESOURCE_FILES = {
    "commodities": "commodities",
    "starSystems": "star_systems",
    "planets": "planets",
    "moons": "moons",
    "pointsOfInterest": "poi",
    "orbits": "orbits",
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
    "Bloom": "布鲁姆",
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
    "Aaron Halo": "亚伦光环",
    "Keeger Belt": "基格带",
    "Glaciem Ring": "冰川环",
    "Pyro Asteroid Clusters": "派罗小行星群",
    "Pyro Clusters": "派罗小行星群",
    "OV Breaker Stations": "OV 破碎站",
    "Akiro Cluster Alpha": "亚基罗星团 Alpha",
    "Akiro Cluster": "亚基罗星团",
    "Yela Ring": "耶拉环",
}

LAGRANGE_PREFIX = {
    "ArcCorp": "ARC",
    "Crusader": "CRU",
    "Hurston": "HUR",
    "microTech": "MIC",
}


def fetch_resource(resource: str) -> list[dict]:
    req = Request(f"{API_BASE}/{resource}/", headers={"User-Agent": "A-Yuan-Blueprint-Atlas/1.0"})
    with urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("status") != "ok":
        raise RuntimeError(f"UEX API returned {payload.get('status')} for {resource}")
    return payload["data"]


def ids(value: object) -> list[int]:
    if value in (None, ""):
        return []
    return [int(part) for part in str(value).split(",") if part.strip()]


def zh_name(name: str | None) -> str:
    if not name:
        return "未知"
    return NAME_ZH.get(name, name)


def lagrange_label(name: str, code: str | None) -> tuple[str, str]:
    for prefix, short in LAGRANGE_PREFIX.items():
        marker = f"{prefix} Lagrange Point "
        if name.startswith(marker):
            number = name.removeprefix(marker)
            return f"{short}-L{number}", name
    if code:
        return code, name
    return zh_name(name), name


def location_entry(item: dict, kind: str) -> dict:
    name = item.get("nickname") or item.get("name") or "Unknown"
    if kind == "lagrangePoints":
        zh, en = lagrange_label(name, item.get("code"))
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


def main() -> None:
    resources = {key: fetch_resource(path) for key, path in RESOURCE_FILES.items()}
    lookup = {key: {item["id"]: item for item in value} for key, value in resources.items() if key != "commodities"}
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
            "lagrangePoints": [location_entry(lookup["orbits"][item_id], "lagrangePoints") for item_id in ids(commodity.get("ids_orbits") if commodity else None) if item_id in lookup["orbits"]],
        }
        materials[name] = {
            "commodityId": commodity.get("id") if commodity else None,
            "commodityName": commodity.get("name") if commodity else None,
            "commodityCode": commodity.get("code") if commodity else None,
            "sourceUrl": f"https://uexcorp.space/mining/locations/commodity/{(commodity.get('name') or name).lower().replace(' ', '-').replace('(', '').replace(')', '')}/" if commodity else "",
            "locations": groups,
            "hasReliableLocations": any(groups.values()),
        }

    output = {
        "metadata": {
            "name": "Star Citizen mineral locations",
            "source": "UEX API 2.0",
            "sourceUrl": "https://api.uexcorp.uk/2.0/",
            "retrievedAt": datetime.now(timezone.utc).isoformat(),
            "note": "UEX data is community-maintained and may not reflect live servers. Empty entries are shown as no reliable mining location instead of inferred locations.",
        },
        "materials": materials,
    }
    (DATA_DIR / "mineral-locations.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
