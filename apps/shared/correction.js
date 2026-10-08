'use strict';
// Input is a server/build-time allowlisted projection, never a journey or export.
window.PetWaymarkCorrection = function (context) {
  const host = document.getElementById('correction');
  if (!host) return;
  host.replaceChildren();
  const zh = context.language === 'zh-CN';
  const tr = (en, cn) => zh ? cn : en;
  const details = document.createElement('details');
  details.className = 'correction-panel';
  const summary = document.createElement('summary');
  summary.textContent = tr('Report a correction — preview first', '报告纠错 — 先检查预览');
  details.append(summary);
  const warning = document.createElement('p');
  warning.textContent = tr('Only rule IDs, engine/data versions, reason codes and language are prefilled. Opening the draft sends this preview text to GitHub; an issue is published only when you submit there. Nothing is sent automatically. Remove private itineraries, passports, chip IDs, contacts and documents from any edits. Provide an official URL and original-language locator; unsourced experiences remain unverified leads and cannot update rules directly.', '仅预填规则ID、引擎／数据版本、原因码和语言。打开草稿会把预览文本发送给GitHub；只有在那里提交才发布issue。不会自动发送。编辑时删除私人行程、护照、芯片号、联系方式与单证。请提供官方链接与原文定位；无来源体验仅为待核线索，不能直接更新规则。');
  details.append(warning);
  const kindLabel=document.createElement('label');
  kindLabel.textContent=tr('Correction template', '纠错模板');
  const kind=document.createElement('select');kind.id='correction-kind';
  for(const [value,en,cn] of [['rule_error.md','Rule correction','规则纠错'],['route_problem.md','Route problem','路线问题']]) {
    const option=document.createElement('option');option.value=value;option.textContent=tr(en,cn);kind.append(option);
  }
  kind.value=context.rule_ids.length ? 'rule_error.md' : 'route_problem.md';
  kindLabel.append(kind);details.append(kindLabel);
  const textLabel=document.createElement('label');textLabel.htmlFor='correction-preview';
  textLabel.textContent=tr('Editable public preview; offline copy uses the same text', '可编辑公开预览；离线复制使用相同文本');
  details.append(textLabel);
  const preview=document.createElement('textarea');preview.id='correction-preview';preview.rows=14;
  preview.value=[
    `Rule IDs / 规则ID: ${context.rule_ids.join(', ') || '(none / 无)'} `,
    `Engine version / 引擎版本: ${context.engine_version}`,
    `Dataset version / 数据版本: ${context.dataset_version}`,
    `Reason codes / 原因码: ${context.reason_codes.join(', ') || '(none / 无)'}`,
    `Language / 语言: ${context.language}`,
    '', 'Actual / expected result / 实际与预期结果:',
    'Official source URL / 官方来源链接:',
    'Original-language locator and accessed date / 原文定位与访问日期:',
    'Effective period, conflicts and unknowns / 生效范围、冲突与未知:',
    'Minimal synthetic reproduction / 最小合成复现:',
    'Affiliation / 利益关联:',
    '',tr('No private journey or documents are prefilled. Rules remain draft pending actual independent review.', '未预填私人行程或单证。规则在真实独立复核完成前保持草稿。')
  ].join('\n');
  details.append(preview);
  const open=document.createElement('a');open.id='correction-open';
  open.textContent=tr('Open GitHub draft (account/network required)', '打开GitHub草稿（需账号与网络）');
  open.target='_blank';open.rel='noopener noreferrer';open.referrerPolicy='no-referrer';
  details.append(open);
  const copy=document.createElement('button');copy.type='button';copy.id='correction-copy';
  copy.textContent=tr('Copy preview / offline', '复制预览／离线');details.append(copy);
  const status=document.createElement('p');status.id='correction-status';status.setAttribute('aria-live','polite');details.append(status);
  function update() {
    const url=new URL('https://github.com/Mrwwwwwwww/PetWaymark/issues/new');
    url.searchParams.set('template',kind.value);
    url.searchParams.set('title',tr('Correction: research preview','纠错：研究预览'));
    url.searchParams.set('body',preview.value);
    // Long reports stay copyable without silently truncating evidence.
    if(url.href.length > 7500) {
      open.removeAttribute('href');open.setAttribute('aria-disabled','true');
      status.textContent=tr('Preview is too long for a reliable URL. Copy it and open the repository template manually.', '预览过长，无法可靠装入URL。请复制文本并手动打开仓库模板。');
    } else {
      open.href=url.href;open.removeAttribute('aria-disabled');status.textContent='';
    }
  }
  preview.addEventListener('input',update);kind.addEventListener('change',update);
  copy.onclick=async()=>{
    try {
      if (!navigator.clipboard?.writeText) throw new Error('clipboard unavailable');
      await navigator.clipboard.writeText(preview.value);
      status.textContent=tr('Copied. No upload performed.', '已复制，未上传。');
    } catch {
      preview.focus();preview.select();
      status.textContent=tr('Text selected. Use your device copy command; no account or network is needed.', '文本已选中，请使用设备复制命令；无需账号或网络。');
    }
  };
  host.append(details);update();
};
const correctionContext=document.getElementById('correction-context');
if(correctionContext) window.PetWaymarkCorrection(JSON.parse(correctionContext.textContent));
