# PetWaymark · 宠途路标

[English](README.md)

面向中国、美国和欧盟犬猫出行的中英双语开源规划项目，重点解决小城接驳、陆路／铁路／航空联运、证件时间轴与交接信息缺口。

PetWaymark 是纯公益开源项目，主要目的是帮助宠物主人，与任何商业品牌无关。项目本身免费开放；任何合规服务商都可平等通过开放接口接入，项目不经营、不收单、不偏向任何商家。后续服务对接／跳转到服务商自有渠道，合规、隐私与动物福利要求始终保留。

**当前为第 2 周数据契约，尚无可运行的规划器或已验证可行线路。** 首版拟面向单只自有犬猫、个人非商业移动；分别识别用途、所有权变化、陪同方式和主人旅行日期。服务犬采用独立复核分支。

计划输出路线备选、证件时间轴、费用分项、交接清单以及可追溯官方依据的解释。未知规则不能变成允许。预定状态为 `eligible`（满足已核实条件）、`conditional`（需补件或确认）、`ineligible`（明确阻塞）、`unsupported`（必要规则未覆盖）；任何状态都不代表已订舱或实际承运确认。

## 本地阅读与检查

阅读无需账号或模型密钥。用 Python 3.11+ 检查骨架和规则契约，首次安装开发依赖：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/check_scaffold.py
.venv/bin/python scripts/validate_data.py
.venv/bin/python -m unittest discover -s tests -v
```

- [规则与来源契约](docs/zh/rule-contract.md) · [English](docs/en/rule-contract.md)
- [规则草稿清单](data/rules/README.md) · [第 2 周查阅记录](docs/research/week2/README.md)
- [规划扩展约定](docs/decisions/0002-planning-extension-contract.md)
- [走廊候选与未覆盖边界](docs/zh/corridors.md)、[机器可读覆盖清单](data/coverage/week1-candidates.json)
- [Petra 复用决定与字段映射](docs/decisions/0001-petra-reuse.md)
- [名称与域名重查](docs/zh/name-check.md)
- 访谈准备：[中文](docs/zh/interviews.md) · [English](docs/en/interviews.md)
- [研究证据与快照](docs/research/week1/README.md)
- [贡献指南](CONTRIBUTING.md)、[治理](GOVERNANCE.md)、[行为准则](CODE_OF_CONDUCT.md)、[安全](SECURITY.md)

## 目录

| 目录 | 规划用途 |
|---|---|
| `apps/web` | 双语演示、打印 |
| `packages/schema`、`engine`、`cli`、`mcp` | 数据契约、确定性内核、本地工具、后续只读接口 |
| `data/rules/{cn,us,eu,carriers}` | 版本化规则维护源；正式发布须人工复核 |
| `data/{sources,airports,corridors,providers,coverage}` | 来源、设施、走廊、中立名录、覆盖缺口 |
| `tests/{fixtures,regression}` | 合成边界契约及后续内核回归 |
| `docs/{zh,en,decisions}`、`scripts`、`.github` | 文档、决定、校验与贡献模板 |

中国↔美国、中国↔欧盟、美国↔欧盟的六个方向独立验收。欧盟首批深核德国、法国、荷兰。所有候选当前均为 `unsupported`；研究清单中的机场代码不能证明航线或宠物产品可用。尚未接入实时价格、航班或宠物位。

## 许可

自有代码与文档采用 [Apache-2.0](LICENSE)；`data/` 下自有整理数据采用 [CC BY 4.0](LICENSE-DATA)，详见[范围说明](data/README.md)。Petra 研究快照保留原 CC BY 4.0 许可与[第三方归属](THIRD_PARTY_NOTICES.md)。官方原文、商标及第三方数据库不因此获得本项目再许可。

第 1 周未创建外部仓库、账号、软件包或域名。
