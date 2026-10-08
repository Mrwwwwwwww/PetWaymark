"""Project planning suggestions only; no rescue, treatment or custody confirmation."""


def checklist(language='zh-CN'):
    if language not in ('en', 'zh-CN'):
        raise ValueError('unsupported checklist language')
    items = [
        ('Offline emergency / postponement preparation — arrangements unconfirmed',
         '离线应急／改期待办 — 安排均未确认'),
        ('[ ] Pause travel if the owner is unavailable or a leg, pickup or care is unconfirmed; consider postponing or staying in familiar local care.',
         '[ ] 主人无法同行或某段／接收／照护未确认时，暂停出行；考虑改期或熟悉的原地照护。'),
        ('[ ] Privately record the current animal custodian, authorized backup receiver and their contact method; confirm consent and availability. Do not publish contacts here.',
         '[ ] 私下记录当前宠物保管人、已授权备选接收人及联系方式；确认本人同意和可接收，不在仓库公开。'),
        ('[ ] Privately identify each original document, its present custodian and return/transfer arrangement; keep copies separately. Copies do not replace required originals.',
         '[ ] 私下逐件记录原件、当前保管人及退回／转交安排，副本分开保留；副本不能替代所需原件。'),
        ('[ ] Confirm an alternative original-document custodian and an authorized local carer before relying on them; unconfirmed alternatives remain unknown.',
         '[ ] 先确认原件保管备选与已授权当地照护者，再依赖安排；未确认备选保持未知。'),
        ('[ ] Independently contact the actual carrier/receiving party about missed pickup, cancellation and overnight responsibility; check with the issuing authority about documents and a veterinarian about urgent animal health concerns.',
         '[ ] 自主向实际承运／接收责任方核实错过接收、取消及过夜责任；文件问签发机关，动物急诊问题联系兽医。'),
        ('[ ] On postponement, recalculate departure, arrival, owner movement, inspections, certificate windows and appointments; recheck current official rules and dated acceptance for every leg.',
         '[ ] 改期后重算出发、抵达、主人移动、查验、证件窗口与预约；逐段重核现行官方规则及日期限定接受。'),
        ('Project suggestions, not official requirements. No medical treatment, agency service, timed rescue or confirmed transport is promised.',
         '以上为项目准备建议，非官方要求；不承诺医疗、代办、限时救援或确认运输。'),
    ]
    return '\n' + '\n'.join(pair[1 if language == 'zh-CN' else 0] for pair in items) + '\n'
