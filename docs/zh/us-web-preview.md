# 美国研究预览与双语本机网页

按[README](../../README.zh-CN.md)安装Python 3.11+与依赖后：

```sh
python -m apps.web.server --port 8766
```

打开`http://127.0.0.1:8766`，选方向、评估／出行日期、犬猫、服务动物分类、用途、
所有权变化及陪同方式。未知保持未知；仅单宠，不需私人标识。主人同行／独行链接填入明确标为合成的输入。
普通宠物行程须明确选择“非服务动物”和“不变更所有权”；机构寄游超出本版范围。

评估后可以保留输入切换语言、导出脱敏JSON、打印完整交接清单。
候选为未覆盖研究路径；已排除结果仅针对此图和输入，不是许可、订舱或推荐。
精确窗口、陪同／保管／接收／原件责任待安排。网页与CLI使用同一内核，仅翻译提示文本。
无账号、模型密钥、云服务、跟踪、cookie或付费运行依赖。
本机服务仅监听回环地址，本版非已托管纯静态站点；[交付取舍](../decisions/0005-local-bilingual-web.md)已记录。
Ctrl+C停止；端口占用时通过`--port`选择可用端口。

| 方向 | 小城接驳例子 | 证据边界 |
|---|---|---|
| `dom.us.ca-ny` | 文图拉→LAX→JFK→金斯顿 | NY官方正文不可读，入州、实际航段与设施待核 |
| `dom.us.ny-tx` | 金斯顿→JFK→DFW→登顿 | TX犬猫页面已读，年龄／首针／地方／应急条件未复核 |
| `dom.us.tx-ca` | 登顿→DFW→LAX→文图拉 | CA页面已读，螺旋蝇来源地叠加及完整附件未复核 |

另有全道路候选比较。人宠同行车辆、旅客客舱／行李、无主人陪同活体承运／货运分开，
普通配送不能补活体首末段。航司名称仅标识政策范围。机场节点仅为地理示例，不证明实际经营航段、
设施、犬猫条件、仓位或道路连通。里程、时间和费用为null；其余州／途经州仍未覆盖。

CLI离线示例（均为合成输入）：

```sh
python -m packages.cli tests/fixtures/us-domestic/owner.json --corridor dom.us.ca-ny --assessment-at 2026-10-08 --format checklist --language zh-CN
python -m packages.cli tests/fixtures/us-domestic/unaccompanied.json --corridor dom.us.ny-tx --assessment-at 2026-10-08
python -m packages.cli tests/fixtures/us-domestic/owner.json --corridor dom.us.tx-ca --assessment-at 2026-10-08
python -m unittest discover -s tests -v
```

[州清单](../../data/coverage/us-state-overlays.json)、[美国图](../../data/corridors/us-preview.json)、
[来源查阅和不可读页面](../research/week5/README.md)可核对。
CA／TX为已读待独立复核，NY为来源不可读。两条新增部分约束仍为草稿，不是完整州／承运包；
证书存在不证明日期和内容合格。美国国内不套CDC国际入境旅行史。无人类复核批准或已验证可行路线。

本机`/assess`接收同一匿名URL编码表单，`output=json`返回脱敏结果，不提供私人档案上传或公开API。
界面使用原生表单，JavaScript负责保留输入切语言与打印；HTTP集成验证所有当前方向、犬猫／未知、
主人同行／独行／未知的中英状态与原因一致。
