# Week 12 maintenance evidence / 第12周维护证据

Snapshot: 2026-10-09 Asia/Shanghai. These are task stages executed during October 8–9,
not twelve elapsed weeks. [Machine ledger](evidence.json) separates evidence categories.

| Category / 类别 | Evidence / 证据 | Limit / 限制 |
|---|---|---|
| Maintenance / 维护 | [9965c85](https://github.com/Mrwwwwwwww/PetWaymark/commit/9965c85d8ac1677c46fb8c0f1ed227111a0ea79c), [CI success](https://github.com/Mrwwwwwwww/PetWaymark/actions/runs/37782458293); [c6722c2](https://github.com/Mrwwwwwwww/PetWaymark/commit/c6722c20749b5d59825be03e470008132d369c32), [CI success](https://github.com/Mrwwwwwwww/PetWaymark/actions/runs/37783577245) | Maintainer-led changes, not external feedback / 维护者主导，非外部反馈 |
| Self-use / 自用 | Local developer validation / 本地开发验证 | No real transport trial claimed / 不冒充真实运输试用 |
| Synthetic / 合成 | Baseline 200 Python tests, 48 audit cases, 22 fixed demo examples | Overlapping counts; never add them as users or 270 tests / 不相加成用户或270测试 |
| Independent adoption / 独立采用 | 0 documented, sample size 0, no links | No fabricated monthly active users / 不虚填月活 |
| Voluntary human trials / 真人试用 | 0 documented, sample size 0 | No feedback→fix loop / 无真实反馈闭环 |
| Independent rule review / 独立复核 | 0 qualified reviewers | 15 rules draft, no verification/due dates / 15条草稿，核实与到期日期未记录 |
| Verified feasible routes / 核实可行路线 | 0 | Official readings and synthetic diagnostics do not establish capacity / 官方查阅与合成诊断不证明运力 |

Maintenance hours, spend and downloads are unmeasured, not zero. The existing budget
of 15–20 hours/week and 1.5–2 hours for extensions is a planning assumption, not a time sheet.
本轮无实际人工工时、支出或下载测量；不得从机器会话时长推导人工投入。
T29 already exists in `data/rules/{cn,us,eu}`; retain the directories.

## Open defects and gates / 缺陷与门槛

[#3](https://github.com/Mrwwwwwwww/PetWaymark/issues/3),
[#4](https://github.com/Mrwwwwwwww/PetWaymark/issues/4),
[#5](https://github.com/Mrwwwwwwww/PetWaymark/issues/5) retain missing full official
chains and actual independent qualified review (T11/T66).
[#6](https://github.com/Mrwwwwwwww/PetWaymark/issues/6) tracks maintenance;
[#9](https://github.com/Mrwwwwwwww/PetWaymark/issues/9) tracks correction privacy.
No external defect report or adoption is established. 新功能完成不代表P0门槛通过。

## A→B decision / 阶段决策

Defer B. No demonstrated independent demand, qualified regional reviewers or operator
review is available. The offline example can expose versioned draft evidence without
private documents. Real custody exchange would need consenting operators, named
responsibilities, privacy/retention/revocation design and authorized field trials.
Simulation work uses synthetic records; field-trial, staffing and privacy costs remain
unestimated. No private photo store, PWA, automatic sync or hosted API is authorized here.

B继续暂缓：独立需求、人员、操作复核及真实试验成本未落实。仅交付离线示例，
保持草稿；不把模拟当采用，不新增实际交接或服务对接承诺。

## Application inventory / 申请证据盘点

Apache-2.0 code, CC BY 4.0 curated data, bilingual local software and fixed synthetic
Pages demo are implemented. Potential reuse is future value, not existing integrations.
[Official program](https://developers.openai.com/community/codex-for-oss) checked
2026-10-09; no published fixed star or maintenance-week threshold was identified.
Personal fields and interest choices stay blank; preparation is not submission.

## Delivered offline preparation / 离线交付

[Version-pinned integration tutorial](../../../examples/offline/README.md) reuses
structured draft rules with the production engine and preserves unknown coverage.
Six bilingual project preparation tasks are included in each printable planning
checklist: pause/postpone, consented local backup care, current/backup original-document
custodians, receiving roles, responsible channels and recalculation after date changes.
They are planning suggestions, not official rules, rescue or agency services.
T75/T51/T05 delivered; T41/T84 deferred under the selected offline-example scope.

固定版本离线只读示例展示结构化规则复用；打印清单加入原地照护、原件备选、
授权接收、责任方核实及改期重算。所有实际责任与接受仍未确认。
