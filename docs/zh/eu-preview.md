# 欧盟证据研究预览

双语本机网页与 CLI 共用离线评估内核，范围为单只自有犬猫。
依赖安装见仓库 README；无需模型密钥、账号、付费接口，不保存用户档案。

```sh
python -m packages.cli tests/fixtures/eu/cross-member.json --eu-preview --assessment-at 2026-10-08
python -m packages.cli tests/fixtures/eu/domestic.json --eu-preview --assessment-at 2026-10-08 --format checklist --language zh-CN
python -m packages.cli tests/fixtures/eu/owner-not-moving.json --eu-preview --assessment-at 2026-10-08
python -m apps.web.server --port 8766
```

打开 `http://127.0.0.1:8766/?example=eu-owner` 或 `/?example=eu-boarding`。
可选择德法荷国内、DE→FR、FR→NL、NL→DE及DE→IE未覆盖示例。
展开“欧盟证据输入”填写主人是否移动及日期、书面授权、匿名文件和事件日期。
不要填写芯片号码、联系方式或私人地址。切换语言保留输入，JSON与打印不输出原始档案。

先分类再诊断。主人不移动而跨境寄游、用途／所有权／主人移动未知、成员国不支持、
陪同关系未确定时，停止普通跨成员国分支。书面授权、主人前后五个民用日期与
运输产品分别检查；货舱本身不决定法律分类。尚未处理时区时刻或真实责任证据。
`classification_resolved=true`仅表示可运行研究诊断。

单一成员国内移动不执行跨成员国狂犬／护照草稿，本地要求仍未复核。
跨成员国输出三条不执行的部分约束与标识／护照范本日期诊断。
`model_date_consistent`不证明文件完整有效、居住资格、签发主体、持续免疫或订舱／保管落实。
纹身例外仍须确认；健康证与抗体辅助函数仅供研究，不是跨境时间轴或入境判定。

[27国清单](../../data/coverage/eu-members.json)列德法荷部分查阅及其余24国本地叠加缺口。
共同框架不等于成员国完整覆盖。全部结果仍`unsupported`；无经核实运输路线、估时、排名，
已验证可行路线数零。原件责任仍待安排。证书过渡、例外、条款附件及不可读来源
详见[第6周查阅记录](../research/week6/README.md)。

[English](../en/eu-preview.md)
