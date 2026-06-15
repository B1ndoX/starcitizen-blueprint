# SC Blueprint Atlas

一个面向 PC 查询、可部署到 NAS 或 GitHub Pages 的《星际公民》蓝图查询静态网站。

另外包含一个舰队官网风格页：`fleet.html`。它是独立静态页面，不影响蓝图查询工具。

## 本地检查

```bash
cd blueprint-site
python3 -m http.server 4173
```

然后打开 `http://127.0.0.1:4173/`。

## 更新 SCMDB 数据

```bash
cd blueprint-site
python3 scripts/build_data.py
python3 scripts/translate_index_google.py
python3 scripts/fetch_flowcld_calibration.py
python3 scripts/apply_local_polish.py
```

第一步读取 SCMDB 公开数据，生成 `data/blueprint-index.json`。第二步使用 Google Translate 生成中文缓存。第三步从 FlowCLD 公开蓝图列表抓取精简中文名称校准表。第四步优先使用 FlowCLD 中文蓝图名，机器人项目里的本地汉化词库作为补充，Google Translate 只作为兜底。

## NAS 方案

NAS 上建议使用 Docker Compose 跑 Caddy 静态服务：

```bash
cd blueprint-site
docker compose -f docker-compose.nas.yml up -d --build
```

默认映射到 NAS 的 `8088` 端口。之后可以在 NAS 控制面板里用反向代理、域名和 HTTPS 指向这个端口。

## GitHub Pages 方案

把 `blueprint-site` 作为一个独立 GitHub 仓库根目录时，`.github/workflows/pages.yml` 可以直接发布到 GitHub Pages。

发布前在仓库设置里启用 Pages，并把来源设置为 GitHub Actions。

## 数据说明

- 蓝图、材料、制作时间来自 SCMDB 的 `crafting_blueprints` 数据。
- 物品类型、尺寸、厂商等来自 SCMDB 的 `crafting_items` 数据。
- 获取来源来自 SCMDB mission 数据中的 blueprint reward pool 匹配。
- 中文蓝图名优先使用 FlowCLD 精简名称校准表 `data/flowcld-blueprint-calibration.json`，机器人本地汉化词库 `data/local-polish-names.json` 作为补充，Google Translate 作为兜底。
- 当前生成版本写在页面顶部。
