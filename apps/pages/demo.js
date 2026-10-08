'use strict';
const data = window.PETWAYMARK_DEMO;
const words = {
  'zh-CN': {title:'宠途路标：看清出行缺口', intro:'免费公益开源的犬猫出行研究工具。选择固定合成样例，查看原因、证件时间轴与待确认事项。自填行程评估请运行仓库中的本地网页。', limits:'早期研究预览：规则均为待核草稿，无已验证路线。不是订舱服务，不接单；没有实时运力、报价或服务确认。样例诊断不能作为出行许可，出行前须向主管机关、兽医及实际承运人核实。', label:'合成样例（固定输入，非真实旅程）', print:'打印清单', export:'导出合成 JSON', heading:'原因与待确认事项', repo:'源码 / 本地自填网页', coverage:'48 案例覆盖审计', privacy:'演示不采集行程、无账户、无分析脚本。托管平台仍按其政策处理访问请求。纠错请使用仓库 issue，勿上传证件、芯片号或联系方式。', json:'查看内核 JSON'},
  en: {title:'PetWaymark: understand the gaps', intro:'A free, public-benefit open-source research tool for dog and cat travel. Choose a fixed synthetic example to inspect reasons, document timelines and confirmation gaps. Run the local web app for your own inputs.', limits:'Early research preview: all rules are unreviewed drafts; zero verified routes. No booking or order acceptance. No live capacity, prices or service confirmation. These diagnostics are not travel permission; check with authorities, a veterinarian and the actual carrier before travel.', label:'Synthetic example (fixed input, not a real trip)', print:'Print checklist', export:'Export synthetic JSON', heading:'Reasons and confirmation gaps', repo:'Source / local input form', coverage:'48-case coverage audit', privacy:'The demo collects no journey data and has no accounts or analytics scripts. The hosting platform processes requests under its own policies. Use repository issues for corrections; do not upload documents, chip numbers or contact details.', json:'Inspect engine JSON'}
};
let lang = new URLSearchParams(location.search).get('lang') === 'en' ? 'en' : 'zh-CN';
const select = document.getElementById('example');
for (const example of data.examples) { const option = document.createElement('option'); option.value = example.id; option.textContent = example.id; select.append(option); }
function current() { return data.examples.find(e => e.id === select.value); }
function render() {
  document.documentElement.lang = lang;
  for (const [id, value] of Object.entries(words[lang])) document.getElementById(id === 'json' ? 'json-label' : id).textContent = value;
  document.getElementById('language').textContent = lang === 'en' ? '简体中文' : 'English';
  document.getElementById('version').textContent = `Engine ${data.engine_version} · Data ${data.data_version} · ${data.assessment_at} · SYNTHETIC`;
  document.getElementById('checklist').textContent = current().checklists[lang];
  document.getElementById('json').textContent = JSON.stringify(current().result, null, 2);
}
document.getElementById('language').onclick = () => {lang = lang === 'en' ? 'zh-CN' : 'en'; render();};
select.onchange = render;
document.getElementById('print').onclick = () => window.print();
document.getElementById('export').onclick = () => {
  const payload = {engine_version:data.engine_version, data_version:data.data_version, synthetic:true, assessment_at:data.assessment_at, example_id:current().id, result:current().result};
  const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], {type:'application/json'}));
  const link = document.createElement('a'); link.href = url; link.download = `petwaymark-${current().id}.json`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
};
render();
