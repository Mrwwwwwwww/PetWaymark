# 中国出境文件链预览

离线研究工具分别评估中国→美国、中国→欧盟的犬猫文件链。所有公开结果为
`unsupported`，文件诊断不执行法律批准；正式复核规则与已验证可行路线均为零。
不订舱、不接单、不证明原件已经交付。无需账号、模型密钥、付费接口或文件上传。

```sh
.venv/bin/python -m packages.cli tests/fixtures/outbound/cn-us-dog.json --outbound-preview --assessment-at 2026-10-08 --format checklist --language zh-CN
.venv/bin/python -m packages.cli tests/fixtures/outbound/cn-eu-cat.json --outbound-preview --assessment-at 2026-10-08
.venv/bin/python -m apps.web.server --port 8766
```

打开`http://127.0.0.1:8766/?example=outbound-us`或`/?example=outbound-eu`。
选择犬猫及陪同；展开“欧盟证据输入”填写主人、标识及接种日期，展开“中国出境文件与预约输入”
填写文件、口岸、拟预约及匿名责任角色。网页、CLI、JSON下载和打印清单调用同一模块；
切换语言保留输入及原因。仅本机开发服务，纯静态托管仍顺延。

[四份合成夹具](../../tests/fixtures/outbound/)分别对应两方向犬猫，各自测试主人、授权及无陪同旅客。
欧盟主人不移动、无陪同、书面授权缺失或日期关系不符时先停止普通文件诊断；
独立货运模式不替代欧盟法律分类。美国犬旅行史／疫苗来源另分，不套主人五日条件；
中国大陆起运不能声称只有低风险旅行史。美国签发疫苗犬和服务动物保持独立未覆盖出口。

| 输入／输出 | 含义 |
|---|---|
| `journey.departure_at`／`entry_at` | 分开记录起运日与抵达日。 |
| `first_entry_member`／`destination_member`／`entry_airport` | 首入境国、最终成员国与口岸分别记录；表列口岸不证明设施收运。 |
| `events.rabies_vaccination_at`／`primary_protocol_completed_at`／`titre_sample_at` | 接种、初次程序完成及采血独立锚点；加强针持续有效性未核。 |
| `documents.origin_certificate_issued_at` | 中国出口证签发，不代替美国表格或欧盟入境证书。 |
| `certificate_issued_at`／`certificate_endorsed_at`／`issuer_route` | 美国兽医签署与政府背书分别记录；欧盟区分官方签发和授权签发后背书。 |
| `appointments.certificate_at`／`document_check_at` | 拟最终签发／背书预约与欧盟文件标识检查日期；超窗显示原因，不自动预约。 |
| `events.document_delivery_at`／`responsibility.*_role` | 拟原件交付日期、携带／交付／接收匿名角色；保管和交付始终未确认。 |
| `entry_time`／`entry_timezone`，`onward_entry_time`／`onward_entry_timezone`，`events.tapeworm_at`／`tapeworm_timezone` | 受保护区犬处理小时研究；时间须带明确时差及IANA时区，后续受保护成员国另填入境时刻。 |

时间轴区分申请、属地查验／出口签发、标识、接种／程序、采血、入境文件签发／背书、
入境和交付，显示依赖与已知界限，未知日期保持null。日级倒排只是研究估算，不是营业时间、
节假日、预约可用性、证书真伪、实验室认可或适运判断；没有自动节假日排期器。
小时比较转为UTC，拒绝无时差、与IANA不符或夏令时跳过的本地时刻，重复时刻用时差区分。

美国犬口岸诊断使用已读设施机场清单，区分SEA仅货运、LAX转货运提示及回执／设施机场、日期匹配；
不套到猫。猫仍需抵达健康检查、州、USDA与承运核实。欧盟AMS仅2024表列部分查阅；
欧委会索引失败，德FRA、法CDG及其他口岸未核。首入境、后续目的地、本地叠加、商业查验中心、
设施营业时间与实际收运分开，不产出联运路线或容量。

依据见[第7周来源与缺口](../research/week7/README.md)、
[覆盖清单](../../data/coverage/cn-outbound.json)、[设计取舍](../decisions/0007-cn-outbound-timeline.md)。
两位合格独立人工复核、现行中国属地／货运流程、欧盟完整附件清单、美国APHIS／州和运输证据均待完成，
不推导反向旅程，不将页面查阅算作人工审核。
