# Design QA

final result: passed with file-level verification and responsive in-app browser audit.

Reference used:
- Local announcement bot menu card: `work/sc-spectrum-qq-bot-handoff/sc-spectrum-qq-bot/data/menu-cards/bot-menu.png`.
- Key visual language: deep navy background, cyan diagonal grid lines, glass outer shell, orange group headings, compact command-row cards, cyan/orange state accents.

Checks:
- Data refreshed to `4.8.1-live.11952564`, with 1,553 blueprint records.
- FlowCLD calibration refreshed: 1,537 metadata records and 1,507 localized blueprint names.
- `公民中文` bundle rebuilt with 3,711 terms.
- Translation audit passed for key materials: 砬兰石, 欧拉特烃, 愈金, 塔兰导电石, 萨维里金属, 稀钛铁, 绿柱石, 铁, 钨.
- Component class labels verified: 军用, 民用, 隐形, 竞赛, 工业.
- Mission type labels verified for key Chinese categories: 雇佣兵, 舰船采矿, 货运, 快递, 打捞, 赏金猎人, 调查.
- Localized names no longer contain `S0x`, `尺寸`, or leaked `RADR_...` internal identifiers.
- Mission lists are no longer truncated at the data layer; max missions per source in the refreshed index is 96.
- PC viewport 1380x820: filter toolbar stays in one row, shell fits inside the viewport, and no horizontal overflow was detected.
- PC viewport 1180x820 and 900x820: filter toolbar reflows into two rows while the workbench remains usable; `scrollWidth` matched the viewport in both checks.
- Narrow stress viewport 760x820: filter toolbar reflows into four compact rows, results/detail stack into one column, and no horizontal overflow was detected.
- Filter panel is always visible, using larger dropdown menus and orange section labels instead of a chip wall.
- Filter panel was compacted into a single-row toolbar with fixed-width controls and inline labels.
- Native selects were replaced with custom dropdowns so long option lists use an internal 260px scroll area instead of escaping outside the page.
- Filter grid reviewed for width: columns + gaps + horizontal padding total about 1276px, below the filter card width.
- Filter panel now includes FlowCLD-style mission type filters.
- Component class dropdown is always visible; it shows `无` when the selected type is not `舰船组件`.
- Results/detail scrollbars now live inside internal scroll layers, with the outer rounded panels clipping the edge.
- Material labels are calibrated to FlowCLD wording, including `砬兰石 (Laranite)`, `欧拉特烃 (Ouratite)`, `愈金 (Riccite)`, and `塔兰导电石 (Taranite)`.
- Material labels keep the English source name after the Chinese name in UI, for example `砬兰石 (Laranite)`.
- Result rows and detail/material/source blocks use the announcement-menu command-card style.
- Ship component result rows now show the component type inline, for example `舰船组件 · 雷达 · GNP · 军用 · S1 · A 级`, without adding another filter dropdown.
- Search now uses structured fields instead of the legacy machine-translated `search` blob, so component queries do not get polluted by old terms such as `闪电电源有限公司`.
- Search audit passed for component terms: `护盾` 62/62 shield records, `电源` 75/75 power-plant records, `雷达` 60/60 radar records, `冷却器` 75/75 cooler records, `量子驱动` 57/57 quantum-drive records, plus mining laser, tractor beam, refueling, and salvage component terms.
- Search audit also covered category terms, materials in Chinese/English, manufacturers, sizes, and grades.
- Item display names normalize `S01尺寸` to compact `(S1)` format in the UI.
- `GNP` and `GRNP` are preserved as `GNP`; the bad machine translation `国民生产总值` is removed from both the blueprint index and the reusable `公民中文` bundle.
- `公民中文` active fields were rebuilt through the same local polish path; active terms contain zero `RADR_...` leaks and zero `S0x尺寸` tokens. Raw source fields may still preserve upstream `rawZh` for traceability.
- Python scripts compile under project `.venv` Python 3.12.13.
- Frontend JS syntax check passed with bundled Node.js.
- `公民中文` localization bundle generated at `data/citizen-chinese-localization.json`.

Known note:
- The site remains static and is not deployed; local preview is served from the existing `python3 -m http.server 4173` process.
- In-app browser audit successfully loaded `http://127.0.0.1:4173/` and checked responsive widths 1380, 1180, 900, and 760.
