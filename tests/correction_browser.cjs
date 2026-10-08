// Shared assertions for the local app and file:// Pages demo. Never submits an issue.
const assert=require('node:assert/strict');
module.exports=async function checkCorrection(page) {
 const original=await page.evaluate(()=>{
  const node=document.getElementById('correction-context');
  return node ? JSON.parse(node.textContent) : {...window.PETWAYMARK_DEMO.examples.find(e=>e.id===document.getElementById('example').value).correction_context};
 });
 for (const language of ['en','zh-CN']) {
  await page.evaluate(ctx=>window.PetWaymarkCorrection({...ctx,pet:{passport:'PRIVATE-ID-CANARY'},journey_id:'PRIVATE-JOURNEY-CANARY'}),{...original,language});
  await page.locator('.correction-panel summary').click();
  assert.match(await page.locator('.correction-panel > p').first().textContent(),language==='en' ? /Opening the draft sends this preview text to GitHub/ : /打开草稿会把预览文本发送给GitHub/);
  const preview=page.locator('#correction-preview');
  const initial=await preview.inputValue();
  assert(!initial.includes('PRIVATE-'));
  assert(!initial.includes('2026-11-10'));
  assert(!initial.includes('2026-11-01'));
  assert(!initial.includes('certificate_issued_at'));
  assert(!initial.includes('journey_id'));
  assert.match(initial,/Engine version \/ 引擎版本: 0.1.0/);
  assert.match(initial,/Dataset version \/ 数据版本: 2026.10.08-draft.2/);
  assert(initial.includes('Language / 语言: '+language));
  const href=await page.locator('#correction-open').getAttribute('href');
  assert.equal(new URL(href).searchParams.get('body'),initial);
  assert.equal(new URL(href).searchParams.get('template'),original.rule_ids.length ? 'rule_error.md' : 'route_problem.md');
  const edit=initial+'\n合成更正 & + # % ?';
  await preview.fill(edit);
  assert.equal(new URL(await page.locator('#correction-open').getAttribute('href')).searchParams.get('body'),edit);
  await page.selectOption('#correction-kind','route_problem.md');
  assert.equal(new URL(await page.locator('#correction-open').getAttribute('href')).searchParams.get('template'),'route_problem.md');
  await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.copiedCorrection=text}}}));
  await page.click('#correction-copy');
  assert.equal(await page.evaluate(()=>window.copiedCorrection),edit);
  await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined}));
  await page.click('#correction-copy');
  assert.equal(await preview.evaluate(el=>el.selectionStart),0);
  assert.equal(await preview.evaluate(el=>el.selectionEnd),edit.length);
  const long=edit+'\n'+ '合成长上下文'.repeat(4000);
  await preview.fill(long);
  assert.equal(await page.locator('#correction-open').getAttribute('href'),null);
  assert.equal(await preview.inputValue(),long);
  assert.equal(await page.locator('#correction-copy').isEnabled(),true);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 }
 await page.evaluate(()=>window.PetWaymarkCorrection({engine_version:'0.1.0',dataset_version:'2026.10.08-draft.2',language:'en',rule_ids:[],reason_codes:['unknown_rule']}));
 await page.locator('.correction-panel summary').click();
 assert.equal(await page.locator('#correction-kind').inputValue(),'route_problem.md');
 assert.match(await page.locator('#correction-preview').inputValue(),/\(none \/ 无\)/);
 assert.match(new URL(await page.locator('#correction-open').getAttribute('href')).searchParams.get('body'),/unknown_rule/);
 console.log('PASS: correction allowlist privacy, bilingual editable URL encoding, both templates, no-rule reports, long-context fallback and offline copy; no issue submitted.');
};
