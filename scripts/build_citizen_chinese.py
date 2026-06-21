#!/usr/bin/env python3
"""Build the reusable 公民中文 localization bundle."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apply_local_polish import (
    COMPONENT_CLASSES,
    MANUFACTURERS,
    MATERIALS,
    MISSION_TYPES,
    SLOT_TERMS,
    STAT_TERMS,
    SUBTYPE_TERMS,
    TYPE_WORDS,
    clean_localized_name,
    load_json,
    polish_machine_text,
)


def compact_size_tokens(value: str) -> str:
    text = str(value or "")
    text = re.sub(r"[（(]\s*S0*(\d+)\s*尺寸\s*[）)]", r"(S\1)", text, flags=re.I)
    text = re.sub(r"\bS0+(\d+)\s*尺寸\b", r"S\1", text, flags=re.I)
    text = re.sub(r"\bS0+(\d+)\b", r"S\1", text)
    return text.strip()


def add_entry(entries: dict[str, dict[str, Any]], key: str, zh: str, source: str, domain: str, priority: int) -> None:
    clean_key = str(key or "").strip()
    clean_zh = str(zh or "").strip()
    if not clean_key or not clean_zh:
        return
    existing = entries.get(clean_key)
    sources = set(existing.get("sources", [])) if existing else set()
    sources.add(source)
    if not existing or priority >= int(existing.get("priority", 0)):
        entries[clean_key] = {
            "zh": clean_zh,
            "domain": domain,
            "source": source,
            "sources": sorted(sources),
            "priority": priority,
        }
    else:
        existing["sources"] = sorted(sources)


def add_simple_dict(
    entries: dict[str, dict[str, Any]],
    payload: dict[str, Any],
    source: str,
    domain: str,
    priority: int,
) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in payload.items():
        if str(key).startswith("_") or not value:
            continue
        clean_key = str(key).strip()
        clean_zh = str(value).strip()
        if clean_key and clean_zh:
            result[clean_key] = clean_zh
            add_entry(entries, clean_key, clean_zh, source, domain, priority)
    return result


def add_star_citizen_localization(entries: dict[str, dict[str, Any]], bot_assets: Path) -> dict[str, Any]:
    base = bot_assets / "localization" / "starcitizen"
    names: dict[str, str] = {}
    locations: dict[str, str] = {}
    source_counts: dict[str, int] = {}
    if not base.exists():
        return {"names": names, "locations": locations, "sourceCounts": source_counts}

    for source_name, relative, domain in (
        ("itemsByEnglish", "items/by-english.json", "item-name"),
        ("componentCandidates", "items/component-candidates.json", "component-name"),
        ("botComponents", "bot/component-names.json", "component-name"),
        ("botShips", "bot/ship-names.json", "ship-name"),
        ("ships", "ships/names.json", "ship-name"),
    ):
        payload = load_json(base / relative, {})
        count = 0
        if isinstance(payload, dict):
            for key, value in payload.items():
                clean_key = str(key or "").strip()
                clean_value = clean_localized_name(value)
                if not clean_key or not clean_value:
                    continue
                names[clean_key] = clean_value
                add_entry(entries, clean_key, clean_value, f"starcitizen-localization:{relative}", domain, 130)
                count += 1
        source_counts[source_name] = count

    item_records = load_json(base / "items/names.json", {})
    item_count = 0
    if isinstance(item_records, dict):
        for value in item_records.values():
            if not isinstance(value, dict):
                continue
            english = str(value.get("english") or "").strip()
            chinese = clean_localized_name(value.get("chinese"))
            if not english or not chinese:
                continue
            if chinese.startswith("[") and chinese.endswith("]"):
                continue
            names[english] = chinese
            add_entry(entries, english, chinese, "starcitizen-localization:items/names.json", "item-name", 125)
            item_count += 1
    source_counts["itemRecords"] = item_count

    for relative in ("locations/names.json", "bot/location-names.json"):
        payload = load_json(base / relative, {})
        if not isinstance(payload, dict):
            continue
        before = len(locations)
        for key, value in payload.items():
            clean_key = str(key or "").strip()
            clean_value = str(value or "").strip()
            if clean_key and clean_value:
                locations[clean_key] = clean_value
                add_entry(entries, clean_key, clean_value, f"starcitizen-localization:{relative}", "location-name", 130)
        source_counts[relative] = len(locations) - before

    source_counts["totalNames"] = len(names)
    source_counts["totalLocations"] = len(locations)
    return {"names": names, "locations": locations, "sourceCounts": source_counts}


def load_component_matrix(entries: dict[str, dict[str, Any]], matrix_path: Path) -> dict[str, str]:
    matrix = load_json(matrix_path, {})
    result: dict[str, str] = {}
    for category_id, category in (matrix.get("categories") or {}).items():
        columns = [str(col[0]) for col in category.get("columns") or [] if isinstance(col, list) and col]
        try:
            english_index = columns.index("英文名")
            chinese_index = columns.index("中文名")
        except ValueError:
            continue
        for row in category.get("rows") or []:
            values = row.get("values") or []
            if english_index >= len(values) or chinese_index >= len(values):
                continue
            english = str(values[english_index]).strip()
            chinese = str(values[chinese_index]).strip()
            if english and chinese and english != chinese:
                result[english] = chinese
                add_entry(entries, english, chinese, "bot-component-matrix-erkul", f"component:{category_id}", 70)
    return result


def build_blueprint_maps(
    entries: dict[str, dict[str, Any]],
    flowcld_path: Path,
    index_path: Path,
) -> dict[str, Any]:
    flowcld = load_json(flowcld_path, {})
    by_record_guid: dict[str, dict[str, Any]] = {}
    by_internal_name: dict[str, str] = {}
    by_english_name: dict[str, str] = {}
    flowcld_items = flowcld.get("items") if isinstance(flowcld, dict) else []

    for item in flowcld_items or []:
        if not isinstance(item, dict):
            continue
        raw_zh = str(item.get("blueprintNameCn") or "").strip()
        zh = polish_machine_text(compact_size_tokens(raw_zh))
        record_guid = str(item.get("recordGuid") or "").strip()
        internal_name = str(item.get("internalName") or "").strip()
        english_name = str(item.get("blueprintName") or "").strip()
        if record_guid:
            payload = {
                "zh": zh,
                "rawZh": raw_zh,
                "english": english_name,
                "internalName": internal_name,
                "categoryName": item.get("categoryName"),
                "subcategory": item.get("subcategory"),
                "manufacturer": item.get("manufacturer"),
                "grade": item.get("grade"),
                "itemClass": item.get("itemClass"),
                "itemClassCn": COMPONENT_CLASSES.get(str(item.get("itemClass") or "")),
                "rewardMissionTypes": item.get("rewardMissionTypes") or [],
                "rewardMissionTypesCn": [
                    MISSION_TYPES.get(str(name), str(name)) for name in (item.get("rewardMissionTypes") or [])
                ],
            }
            by_record_guid[record_guid] = {key: value for key, value in payload.items() if value not in ("", None, [])}
        if zh:
            if internal_name:
                by_internal_name[internal_name] = zh
                add_entry(entries, internal_name, zh, "flowcld", "blueprint-internal-name", 90)
            if english_name:
                by_english_name[english_name] = zh
                add_entry(entries, english_name, zh, "flowcld", "blueprint-name", 90)

    index = load_json(index_path, {})
    polished_by_record_guid: dict[str, str] = {}
    for record in index.get("records") or []:
        record_id = str(record.get("id") or "").strip()
        zh_name = polish_machine_text(compact_size_tokens(str((record.get("zh") or {}).get("name") or "")))
        english_name = str(record.get("name") or "").strip()
        if record_id and zh_name:
            polished_by_record_guid[record_id] = zh_name
        if english_name and zh_name:
            add_entry(entries, english_name, zh_name, "citizen-chinese-polish", "blueprint-name", 95)

    return {
        "byRecordGuid": by_record_guid,
        "byInternalName": by_internal_name,
        "byEnglishName": by_english_name,
        "polishedByRecordGuid": polished_by_record_guid,
    }


def load_mining_signal_calibration(entries: dict[str, dict[str, Any]], signal_path: Path) -> dict[str, Any]:
    calibration = load_json(signal_path, {})
    if not isinstance(calibration, dict):
        return {}

    for key, value in (calibration.get("materialLabels") or {}).items():
        add_entry(entries, key, value, "mining-signal-calibration", "material", 105)

    for value in (calibration.get("locationLabels") or {}).values():
        if not isinstance(value, dict):
            continue
        english = str(value.get("en") or "").strip()
        chinese = str(value.get("zh") or "").strip()
        if english and chinese:
            add_entry(entries, english, chinese, "mining-signal-calibration", "mining-location", 90)

    return calibration


def strip_priority(entries: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        key: {field: value for field, value in entry.items() if field != "priority"}
        for key, entry in sorted(entries.items(), key=lambda item: item[0].lower())
    }


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    site = Path(__file__).resolve().parents[1]
    bot_assets_default = root / "work" / "sc-spectrum-qq-bot-handoff" / "sc-spectrum-qq-bot" / "assets"

    parser = argparse.ArgumentParser(description="Build 公民中文 localization bundle")
    parser.add_argument("--bot-assets", type=Path, default=bot_assets_default)
    parser.add_argument("--flowcld", type=Path, default=site / "data" / "flowcld-blueprint-calibration.json")
    parser.add_argument("--index", type=Path, default=site / "data" / "blueprint-index.json")
    parser.add_argument("--mining-signals", type=Path, default=site / "data" / "mineral-signal-calibration.json")
    parser.add_argument("--output", type=Path, default=site / "data" / "citizen-chinese-localization.json")
    args = parser.parse_args()

    entries: dict[str, dict[str, Any]] = {}

    starcitizen = add_star_citizen_localization(entries, args.bot_assets)

    n55_components = add_simple_dict(
        entries,
        load_json(args.bot_assets / "component-name-n55.json", {}),
        "bot-n55",
        "component-name",
        80,
    )
    local_components = add_simple_dict(
        entries,
        load_json(args.bot_assets / "component-name-local.json", {}),
        "bot-local",
        "component-name",
        85,
    )
    ships = add_simple_dict(
        entries,
        load_json(args.bot_assets / "ship-name-zh.json", {}),
        "bot-ship-name",
        "ship-name",
        75,
    )
    matrix_components = load_component_matrix(entries, args.bot_assets / "component-matrix-erkul.json")

    for key, value in MATERIALS.items():
        add_entry(entries, key, value, "flowcld-local-polish", "material", 100)
    for key, value in MANUFACTURERS.items():
        add_entry(entries, key, value, "local-polish", "manufacturer", 80)
    for source, domain in (
        (TYPE_WORDS, "type-word"),
        (STAT_TERMS, "stat-term"),
        (SLOT_TERMS, "crafting-slot"),
        (SUBTYPE_TERMS, "subtype"),
        (COMPONENT_CLASSES, "component-class"),
        (MISSION_TYPES, "mission-type"),
    ):
        for key, value in source.items():
            add_entry(entries, key, value, "local-polish", domain, 80)

    mining_signals = load_mining_signal_calibration(entries, args.mining_signals)
    blueprints = build_blueprint_maps(entries, args.flowcld, args.index)
    terms = {key: entry["zh"] for key, entry in sorted(entries.items(), key=lambda item: item[0].lower())}

    output = {
        "schemaVersion": 1,
        "name": "公民中文",
        "slug": "citizen-chinese",
        "description": "Merged Star Citizen Chinese localization from N55/bot assets, FlowCLD blueprint translations, and local polish rules.",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "botN55": str(args.bot_assets / "component-name-n55.json"),
            "botLocal": str(args.bot_assets / "component-name-local.json"),
            "botShipNames": str(args.bot_assets / "ship-name-zh.json"),
            "botComponentMatrix": str(args.bot_assets / "component-matrix-erkul.json"),
            "starCitizenLocalization": str(args.bot_assets / "localization" / "starcitizen"),
            "flowcld": "https://flowcld.xyz/tools/blueprint",
            "flowcldCache": str(args.flowcld),
            "blueprintIndex": str(args.index),
            "miningSignals": str(args.mining_signals),
        },
        "summary": {
            "entryCount": len(entries),
            "termCount": len(terms),
            "n55ComponentCount": len(n55_components),
            "localComponentCount": len(local_components),
            "matrixComponentCount": len(matrix_components),
            "shipNameCount": len(ships),
            "starCitizenLocalizationCount": len(starcitizen["names"]),
            "starCitizenLocationCount": len(starcitizen["locations"]),
            "flowcldBlueprintCount": len(blueprints["byRecordGuid"]),
            "polishedBlueprintCount": len(blueprints["polishedByRecordGuid"]),
            "materialCount": len(MATERIALS),
            "manufacturerCount": len(MANUFACTURERS),
            "missionTypeCount": len(MISSION_TYPES),
            "miningSignalMaterialCount": len((mining_signals.get("signals") or {})),
        },
        "terms": terms,
        "entries": strip_priority(entries),
        "components": {
            "n55": n55_components,
            "local": local_components,
            "matrix": matrix_components,
            "starcitizen": starcitizen["names"],
        },
        "ships": ships,
        "locations": {
            key: {"zh": value, "source": "starcitizen-localization"}
            for key, value in sorted(starcitizen["locations"].items())
        },
        "blueprints": blueprints,
        "materials": {
            key: {"zh": value, "label": f"{value} ({key})", "source": "flowcld-local-polish"}
            for key, value in sorted(MATERIALS.items())
        },
        "miningSignals": mining_signals,
        "manufacturers": MANUFACTURERS,
        "componentClasses": COMPONENT_CLASSES,
        "missionTypes": MISSION_TYPES,
        "taxonomy": {
            "typeWords": TYPE_WORDS,
            "statTerms": STAT_TERMS,
            "slotTerms": SLOT_TERMS,
            "subtypeTerms": SUBTYPE_TERMS,
        },
        "starCitizenLocalization": {
            "sourceCounts": starcitizen["sourceCounts"],
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"Built {output['name']} localization bundle: {args.output}")
    print(json.dumps(output["summary"], ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
