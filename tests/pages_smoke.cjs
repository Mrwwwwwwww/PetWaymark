// Static file demo: verify actual bilingual output, download, print and no network.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
 const browser = await chromium.launch({headless:true, ...(process.env.PETWAYMARK_CHROME ? {executablePath:process.env.PETWAYMARK_CHROME} : {})});
 try {
  const page = await browser.newPage({viewport:{width:390,height:844}});
  const errors=[]; page.on('pageerror',e=>errors.push(e.message));
  const remote=[];page.on('request',r=>{if(/^https?:/.test(r.url()))remote.push(r.url());});
  await page.goto('file://'+path.resolve('_site/index.html'));
  await page.waitForFunction(()=>document.querySelector('#checklist').textContent.length>0);
  const count = await page.locator('#example option').count(); assert(count>=21);
  for(let i=0;i<count;i++) {
   await page.selectOption('#example',{index:i});
   const result = await page.locator('#json').textContent();
   const zh = await page.locator('#checklist').textContent(); assert(zh.length>100);
   await page.click('#language');
   assert.match(await page.locator('#limits').textContent(),/zero verified routes/);
   assert.equal(await page.locator('#json').textContent(),result);
   assert((await page.locator('#checklist').textContent()).length>100);
   await page.click('#language');
  }
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
  const waiting=page.waitForEvent('download');await page.click('#export');const download=await waiting;
  const payload=JSON.parse(fs.readFileSync(await download.path(),'utf8'));assert.equal(payload.synthetic,true);assert.equal(payload.data_version,'2026.10.08-draft.1');
  assert.deepEqual(payload.result,JSON.parse(await page.locator('#json').textContent()));
  await page.emulateMedia({media:'print'});assert.equal(await page.locator('#limits').isVisible(),true);
  await page.pdf({path:'/tmp/petwaymark-pages.pdf',format:'A4'});
  assert.deepEqual(errors,[]);assert.deepEqual(remote,[]);
  console.log(`${count} static bilingual examples, JSON download, print and mobile checks passed`);
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
