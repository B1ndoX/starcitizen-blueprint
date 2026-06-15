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

## Fleet Site QA - 2026-06-15

final result: passed.

Reference used:
- Public Thingy & Thingy site: `https://www.thingyandthingy.com/`.
- Extracted style signals: oversized compressed display type, heavy black outline, hot red/pink/yellow/green palette, rounded label stickers, thick black shadows, marquee strip, playful anti-corporate copy rhythm.
- Source CSS/font signals inspected from Webflow output: `#ff4e47`, `#ffabcc`, `#f5b200`, `#3dd23d`, `#c5ff8d`, `#05051a`; display families included `Kosmos`, `Mdnichrome`, and condensed headline styles.

Checks:
- Added `fleet.html`, `assets/fleet.css`, and `assets/fleet.js` as an independent static fleet homepage.
- Kept the existing blueprint query app as `index.html`; added only a small `舰队官网` link in the existing top bar.
- Local preview served from `http://127.0.0.1:4174/` because port `4173` was already occupied.
- In-app browser loaded `http://127.0.0.1:4174/fleet.html`; title, hero, join CTA, and wing section were present.
- Desktop viewport screenshot passed visual check for large outlined headline, sticker labels, sticky nav, hero CTAs, and marquee band.
- Mobile viewport 390x844 loaded in a fresh tab with no horizontal overflow; `document.body.scrollWidth` matched `innerWidth`.
- Role filter interaction passed: selecting `战斗` highlighted `Redline Escort` and dimmed the other wing cards.
- Recruit dialog interaction passed: `申请加入` opens the modal, entering `A Yuan` and submitting generated `A YUAN / 战斗护航 / 申请卡已生成`.
- Blueprint home page check passed: `舰队官网` link exists, no horizontal overflow, and no console errors were reported.
- Updated hero identity to real GVY material from the public RSI org page: `星际远航者`, `GVY`, `Galactic Voyagers`, 31 members, and the public GVY logo.
- Replaced the old floating role tags with all 31 public members using RSI citizen handles and avatar images. Member items no longer link to public RSI citizen pages.
- Converted the physics wall into an idle battle toy: members are circular avatars with horizontal name labels above them, no rank text, random weapon or empty-hand assignment, equal starting HP, automatic nearby attacks, HP loss, knockback, and death removal.
- The battle toy uses Matter.js physics: members drop in from the top of the hero area, collide with each other and the hero walls, stack at the bottom, and can be freely dragged; after release gravity pulls them back into the fight.
- Fighter avatar size is calculated from member count, with a minimum size and text size so a larger roster stays readable.
- Desktop battle audit passed: 31 fighters rendered, zero member profile links, 31 weapon labels, 31 HP bars, no rank text, no horizontal overflow, attack effects visible, HP changed, and members died/disappeared over time.
- Drag audit passed: dragging a fighter upward and releasing it let gravity pull it back down into the fight.
- 390px mobile battle audit passed: 31 fighters rendered, zero member profile links, 31 weapon labels, 31 HP bars, calculated fighter size 55px, no rank text, and no horizontal overflow.
- Recruit modal clarified that real applications must be submitted on RSI after login; local form now uses `游戏 ID` with placeholder `例如：你的游戏ID` and includes a direct link to the public GVY RSI page.
- Removed the default button-like white/gray fighter background; fighter elements now use a transparent shell so only the avatar, name, health bar, and combat icon are visible.
- Replaced visible weapon text labels with local inline SVG combat icons for fist, short blade, rifle, shotgun, beam, and injector variants; the UI no longer displays what weapon a member is holding.
- Added continuous hop impulses so every living member keeps bouncing during combat instead of settling into a static pile.
- Added hit feedback and damage-scaled knockback: attacked avatars flash hot red, attack flashes render by effect type, and heavier hits push targets farther away.
- Tightened the physics side walls to reduce fighters clipping into the hero edge during knockback.
- Latest fleet JS syntax check passed with bundled Node.js. Local browser automation with system Chrome was attempted, but Chrome aborted under the current automation sandbox before screenshot capture.
- Updated the hero sticker copy to `勇敢追寻，无限探索，欢迎加入！`.
- Reworked idle hops from mostly vertical impulses into randomized angled jumps with varied lift height, side force, and angular velocity.
- Added Matter.js collision-start feedback: fighters receive a short impact-based bounce when they hit another fighter or a wall/floor, with randomized side bias and cooldown to keep motion lively without exploding the stack.
- Replaced the temporary inline/data-URI combat icons with 8 local original SVG weapon assets under `assets/weapons/`, loosely mapped to Dead Cells-style categories: balanced blade, twin daggers, broadsword, nutcracker, triple bow, marksman bow, laser crossbow, and knockback shield.
- Removed the visible yellow weapon badge frame; weapon SVGs now stay visually attached to the avatar frame with outline/drop-shadow styling.
- Added target-seeking combat AI: each living member tracks the nearest living member, jumps with randomized height and target-biased side force, and moves toward or kites targets depending on weapon range.
- Added weapon-specific combat tuning: light weapons attack faster, heavy weapons hit harder and knock back more, bows/crossbows attack from farther away, and shields can reduce damage and reflect knockback.
- Added multi-projectile attack flashes for multi-shot weapons and a shield flash when a block triggers.
- Replaced the failed downloaded-image cutouts with clean locally generated SVG weapons under `assets/weapons-generated/`; the active app no longer references the temporary `weapons-real` cutout outputs.
- Enlarged weapons so they read as held equipment attached to the member avatar instead of small badges.
- Added weapon-specific held animations: sword/axe slash, greatsword chop, spear stab, bow/crossbow/pistol recoil, and shield bash.
- Reworked ranged attacks into real projectiles: arrows, bolts, and bullets travel across the hero field and resolve damage on impact after the flight delay.
- Slowed the overall combat pacing by increasing weapon cooldowns and adding a larger randomized attack delay.
- Chrome headless screenshots captured `/private/tmp/fleet-weapons.png` and `/private/tmp/fleet-weapons-delayed.png`; the delayed capture showed fallen members fighting with large held weapons and visible flying arrows.
- Synced Matter.js body angle into the avatar/weapon layer so fighters visually roll like circular tumblers during combat, while the member name label remains outside that rotated layer and stays horizontal.
- Added target-relative weapon aiming: each fighter computes the angle to its current target, compensates for the rolling avatar body's rotation, and uses that value for idle weapon orientation and attack animations so melee, ranged, and shield actions point toward the target instead of always swinging forward.
- Replaced generated SVG weapon art with cleaned transparent PNG assets cut from the available `outputs/dead-cells-like-cartoon-weapons-many-types-transparent.png` source and stored under `assets/weapons-output/`.
- Split weapon rendering into an aim parent layer and an action child layer so target-facing rotation updates smoothly while slash, chop, stab, recoil, and shield-bash animations only apply relative motion.
- Reworked combat timing into a simple state machine inspired by Stream Avatars-style public battle behavior: acquire target, wind up, resolve hit/projectile, recover, then wait for cooldown. This avoids repeated immediate hit animation restarts.
- Chrome headless screenshot captured `/private/tmp/fleet-outputs-weapons.png`; the capture showed the new transparent PNG weapons attached to rolling avatars.
- Added optimized runtime weapon PNGs under `assets/weapons-runtime/`: source cutouts were resized, low-alpha pixels removed, and neutral checkerboard/white background leaks stripped, fixing the bow's visible white checker remnants.
- Weapon images are predecoded before physics starts, avatar images use async/low-priority loading, and weapon CSS was reduced from multiple drop-shadow filters to one lighter shadow to improve first-load smoothness.
- Chrome headless screenshot captured `/private/tmp/fleet-runtime-weapons.png`; the capture showed cleaned runtime weapons and no obvious checkerboard remnants on the bow.
- Reduced ranged weapon weighting with a deterministic weapon deck: for the current 31-member roster, bows/crossbows/pistols now appear 5 times total, while melee and shield fighters dominate the pile.
- Reduced fighter size calculation for crowded rosters; desktop verification showed the current roster rendering at about 59px per member instead of the larger earlier sizing.
- Retuned combat locomotion so living members hop more actively toward their nearest target, with faster target-biased hop intervals and stronger melee chase while ranged fighters keep more distance.
- In-app browser audit on `http://127.0.0.1:4175/fleet.html` passed: 31 fighters rendered, ranged count was 5, 24 fighters had taken damage after the run-up, no horizontal overflow was detected, and 12/12 sampled fighters moved or rotated during a 0.9s motion check.
- Replaced the high-frequency hop nudges with frog-jump locomotion: fighters now get one discrete target-facing launch velocity every 1.1-2.1s, idle hops wait 1.4-2.6s, and the continuous chase force is reduced to a light directional correction.
- Follow-up in-app browser motion sampling passed with `fleet.js?v=20260615-11`: sampled fighters showed large vertical jump steps up to about 28-152px while small jitter counts stayed low, with no horizontal overflow.
- Added 2D stomp-jump reactions: a fighter can launch from a nearby member as a temporary support, while the support receives a restrained opposite/downward reaction velocity and spin so mid-air or stacked fighters can be kicked away without explosive force.
- Added hit-feedback throttling so rapid damage still updates HP and physics, but repeated `is-hit`/block flashes are rate-limited instead of causing members to visually flicker nonstop.
- Follow-up browser audit with `fleet.js?v=20260615-13` passed: 31 fighters rendered, 25 had taken damage after run-up, no horizontal overflow was detected, and visible hit feedback cooled from 3 active flashes to 1 after 700ms.
- Added final-winner celebration: when only one fighter remains alive, combat stops, the winner receives a highlighted victory state, a top victory banner appears, and 72 confetti/party pieces fall through the combat field once.
- Natural browser run with `fleet.js?v=20260615-14` and `fleet.css?v=20260615-12` passed: the battle reached one survivor, the victory banner displayed `🎉 pagelevel218 胜利！`, 72 confetti pieces were present at trigger time, and no horizontal overflow was detected.
- Added a mutual-destruction ending: if death resolution leaves zero living fighters, the battle now overrides any prior winner state and displays `💥 无人生还` with a no-survivors celebration layer.
- Committed attacks and already-fired projectiles now finish resolving even if the attacker dies during windup or flight, making final trade kills possible instead of silently canceling the second hit.
- Browser verification with `fleet.js?v=20260615-16` and `fleet.css?v=20260615-13` passed: 31 fighters loaded, current resources were active, and no horizontal overflow was detected.
- Reworked fleet page width from a fixed 1180px stage to responsive `clamp(1180px, 88vw, 1840px)` sizing, with hero height tied to viewport height instead of a fixed 16:9-like composition.
- Responsive browser measurement passed at 1280x720, 1600x900, 2200x1000, and 2560x1080: hero/content widths scaled from 1180px to 1408px to 1840px, no horizontal overflow was detected, and the bottom `返回顶部` action now targets `#pageTop`.

Known note:
- The page is a static prototype. The recruitment form generates a local application card only; it does not submit to RSI or send data to a server.
