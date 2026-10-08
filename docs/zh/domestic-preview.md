# 中国国内研究预览

第4周交付首个离线数据与引擎预览，无模型密钥、账号和运行时网络依赖。
两组中国候选不等于已验证可行线路；美国与网页工作按第5周推进。

按[README](../../README.zh-CN.md)安装依赖后运行：

```sh
python -m packages.cli tests/fixtures/domestic/owner.json --corridor dom.cn.east --assessment-at 2026-10-08
python -m packages.cli tests/fixtures/domestic/owner.json --corridor dom.cn.south --assessment-at 2026-10-08 --format checklist --language zh-CN
python -m packages.cli tests/fixtures/domestic/unaccompanied.json --corridor dom.cn.east --assessment-at 2026-10-08
python -m packages.cli tests/fixtures/domestic/infeasible.json --corridor dom.cn.east --assessment-at 2026-10-08 --format checklist --language zh-CN
```

把打印输出重定向到本地`.txt`文件即可打印；切换`--language en`得到英文。
两种语言的ID、状态、原因码、来源一致。默认JSON供离线集成。
有效的未覆盖／不可行评估返回0；无效JSON、日期、控制字段或数据返回2并在stderr说明。

| ID | 道路 | 铁路研究枢纽 | 陆空研究枢纽 |
|---|---|---|---|
| `dom.cn.east` | 湖州 → 清远 | 湖州 → 上海虹桥 → 广州南 → 清远 | 湖州 → PVG → CAN → 清远 |
| `dom.cn.south` | 清远 → 廊坊 | 清远 → 广州南 → 北京西 → 廊坊 | 清远 → CAN → PEK → 廊坊 |

主人同行档案得到最多三个有差异的候选：自驾、铁路同行及首末段接驳、航空旅客托运行李及首末段接驳。
独行分别使用独行道路承运／独行铁路分支，不能套用旅客行李。道路服务商与接驳车辆仍未核实、未安排。
铁路历史站点证据与2026双模式产品分别记录，不宣称具体日期站对或班次可收运。
航空旅客行李与独立货运分开；独立货运产品与货站未覆盖。产品主体仅用于限定来源，不推荐品牌。

所有公开候选为 **unsupported**、不排名、无估时费用仓位、未订舱。
铁路体重／尺寸即使超限仍只作草稿诊断，不把未审核数据变成正式法规判断。
国内完整要求及全程道路需人工复核；不把中国入境规则套给国内出行。
`infeasible.json`明确给出无法自驾、航段拒收、铁路窗口错过，所有图中路径被排除。
这是合成操作反例，不是真实拒收或全世界无出行办法；末段接驳拒收同样剔除整条路径。

`preview`支持无个人信息的`journey_id`、正整数`plan_revision`、布尔／null的`can_drive`，
以及按稳定分段ID索引的`segments`。分段仅接受`reported_acceptance`（unknown／declined）
和`handover_window_met`（布尔／null）；缺失为未知，没有自动时刻窗口计算。
不得通过输入覆写证据、覆盖或角色。改日期需调用方升版本；输入报告不是承运确认。

每段打印到达设施作为交接地理范围，窗口待确认，陪同／宠物保管／接收／原件保管均待安排，
并附来源URL、定位和查阅日期。项目不分配实际保管责任。精确柜台／营业部、收运窗口、
文件、照护、延误和备选安排均须在外部确认；不订舱、不接单。改期或原地照护也可作为合理选择。

[决定与契约](../decisions/0004-domestic-preview.md) ·
[来源与未完成核实](../research/week4/README.md) ·
[图数据](../../data/corridors/cn-preview.json) · [English](../en/domestic-preview.md)
