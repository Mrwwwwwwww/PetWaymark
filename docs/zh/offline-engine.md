# 离线条件判定

[English](../en/offline-engine.md) · [日期与信任决定](../decisions/0003-offline-evaluation.md)

第 3 周实现五种条件表达式并执行全部 9 个第 2 周边界案例。
10 条公开规则仍为草稿，公开评估保持 `unsupported`；已验证可行路线仍为零。
运行无需网络或模型密钥；CLI 校验依赖只需首次安装。

在仓库根目录运行：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m packages.cli tests/fixtures/boundaries/boundary.unknown-carrier.json --assessment-at 2026-10-08
.venv/bin/python -m unittest discover -s tests -v
```

退出码 0 表示生成有效评估，包含未覆盖／不可行结果；无效输入、规则包或日期返回 2。
第 2 周扁平 fixture 只评估所列规则；普通 profile 使用 `pet`、`journey`、`documents`、`events` 嵌套对象，评估全套公开规则。
用户输入不能覆写 CLI 默认未覆盖状态。

字段参考[规则契约](rule-contract.md)。旅程分类包括起终地区、用途、`ownership_transfer`、陪同、运输模式、宠物／主人入境日期、六个月旅行史、接种分支、可选属地及承运确认。
宠物分类包含犬猫及 `service_animal`；缺失不补为允许。出发地不能证明过去六个月旅行史；日期是当地日历日期，不是时间戳。

标准库 API 为 `packages.engine.evaluate(profile, validated_rules, assessment_at=...)`。
API 调用者先校验结构／引用；`load_repository()` 自动执行仓库校验。
覆盖与范围缺口解决声明属于维护者可信元数据，不从用户表单传入。
假想已复核记录仅在测试内存中创建，身份显式写“合成、非真实人员”；不进入正式规则目录。

结果包含状态、缺口、原因码、适用／不适用规则 ID、修订号、双语消息与官方证据定位。
草稿失败只是诊断，不据此宣称不可行。满足输入规则包不等于实际收运或已订舱；外部确认输入亦未经内核独立验证。
