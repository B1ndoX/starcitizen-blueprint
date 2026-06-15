# 公民中文本地化包

文件：`citizen-chinese-localization.json`

这是给网页和机器人共用的星际公民中文本地化包，来源包含：

- 机器人 N55 组件汉化：`component-name-n55.json`
- 机器人本地组件/飞船汉化：`component-name-local.json`、`ship-name-zh.json`、`component-matrix-erkul.json`
- FlowCLD 蓝图汉化：`https://flowcld.xyz/tools/blueprint`
- 本项目人工校准词表：材料、制造商、组件类别、任务类型、制作槽位等

## 常用字段

- `terms`：最方便调用的平铺词典，英文名或内部名到中文名。
- `entries`：带来源和领域的结构化词条。
- `blueprints.byRecordGuid`：按 FlowCLD/SCMDB 蓝图 GUID 查询。
- `blueprints.byInternalName`：按 FlowCLD internalName 查询。
- `blueprints.polishedByRecordGuid`：本网页最终展示用的润色蓝图名。
- `materials`：材料名，格式包含中文名和 `中文 (English)` 标签。
- `manufacturers`、`componentClasses`、`missionTypes`：制造商、组件类别、任务类型词表。

## 重新生成

项目已配置本地 Python 3.12 虚拟环境：

```bash
.venv/bin/python blueprint-site/scripts/apply_local_polish.py
.venv/bin/python blueprint-site/scripts/build_citizen_chinese.py
```

如果需要先刷新 FlowCLD：

```bash
.venv/bin/python blueprint-site/scripts/fetch_flowcld_calibration.py --delay 0.1
```
