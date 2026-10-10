const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');const {pathToFileURL}=require('node:url');
(async()=>{
 const root=path.resolve(process.env.PETWAYMARK_PAGES_ROOT || '_site');
 const artifacts=path.resolve(process.env.PETWAYMARK_ARTIFACTS || '/tmp/petwaymark-v2-checks');fs.mkdirSync(artifacts,{recursive:true});
 const browser=await chromium.launch({headless:true,...(process.env.PETWAYMARK_CHROME?{executablePath:process.env.PETWAYMARK_CHROME}:{})});
 const page=await browser.newPage({viewport:{width:390,height:844}});const errors=[],remote=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))remote.push(r.url());});
 const home=pathToFileURL(path.join(root,'index.html')).href,result=pathToFileURL(path.join(root,'result.html')).href;
 const go=async url=>{await page.goto('about:blank');await page.goto(url);};
 const place=(country,city)=>JSON.stringify({country,city,area:'',manual:true});
 const route=(o,d,oc='某出发城市',dc='某目的城市')=>result+'#'+new URLSearchParams({pet:'dog',origin:place(o,oc),destination:place(d,dc)});
 await go(home);await page.screenshot({path:path.join(artifacts,'v2-home.png'),fullPage:true});
 await page.click('#origin');await page.selectOption('#country','CN');
 assert.equal(await page.locator('#country option').count(),251);assert.equal(await page.locator('#subdivision option').count(),35);
 await page.selectOption('#subdivision','23');assert.match(await page.textContent('#city'),/上海/);assert.doesNotMatch(await page.textContent('#city'),/北京/);
 await page.selectOption('#city','上海市');await page.selectOption('#area','徐汇区');await page.selectOption('#subdivision','22');
 assert.equal(await page.inputValue('#city'),'');assert.equal(await page.inputValue('#area'),'');assert.equal(await page.locator('#confirm-place').isDisabled(),true);
 await page.selectOption('#subdivision','23');await page.selectOption('#city','上海市');await page.click('#city-only');
 await page.click('#destination');await page.selectOption('#country','CN');await page.selectOption('#subdivision','22');await page.selectOption('#city','北京市');await page.click('#city-only');
 await page.click('#pet');await page.click('[data-pet=dog]');await page.click('#journey button[type=submit]');await page.waitForURL(/result.html/);
 assert.match(await page.textContent('#trip'),/上海市.*北京市/);checks.push('34省级入口；省州联动、切换清子级；上海→北京提交');
 const shanghaiRoute=page.url();
 for(const id of ['route','supplies','quarantine','timeline']) assert(await page.locator('#'+id).isVisible());
 assert.match(await page.textContent('#cn-quarantine'),/经验信息，办理前向当地农业农村主管部门核实/);
 assert.match(await page.textContent('#cn-quarantine'),/提前 3 天申报/);assert.match(await page.textContent('#testing-point'),/上海市.*待补充/);
 assert.match(await page.textContent('#timeline-certificate'),/约两天.*经验信息.*提前 3 天申报/);checks.push('四步骤、用品通用建议、检疫经验和官方对照、按出发城的检测占位');
 await page.screenshot({path:path.join(artifacts,'v2-result.png'),fullPage:true});
 await page.locator('#quarantine').screenshot({path:path.join(artifacts,'v2-quarantine.png')});
 await page.click('#open-pet');await page.fill('#breed','法国斗牛犬');await page.fill('#weight','12.5');await page.fill('#age','36');await page.selectOption('#neutered','yes');await page.selectOption('#immunity','none');await page.selectOption('#shortnose','yes');
 await page.screenshot({path:path.join(artifacts,'v2-pet.png')});await page.click('#pet-form button[type=submit]');
 assert.match(await page.textContent('#pet-advice'),/短鼻.*暂缓订位/);assert.match(await page.textContent('#pet-advice'),/12.5 公斤/);assert.match(await page.textContent('#pet-advice'),/未接种或过期.*暂缓/);
 assert.doesNotMatch(page.url(),/12.5|法国斗牛犬/);await page.reload();assert.match(await page.textContent('#pet-summary'),/法国斗牛犬/);
 await page.selectOption('#transport','rail');assert.doesNotMatch(await page.textContent('#pet-advice'),/航司/);assert.match(await page.textContent('#route-advice'),/铁路/);
 await page.click('#open-pet');await page.click('#delete-pet');await page.click('#close-pet');await page.reload();assert.match(await page.textContent('#pet-summary'),/尚未填写/);checks.push('宠物资料本机保存、重载、删除；短鼻/重量/年龄/免疫调整路线和提醒；铁路切换');
 const combos=[['CN','CN'],['CN','US'],['US','FR'],['JP','AU'],['DE','FR'],['HK','MO'],['TW','JP']];
 for(const [o,d] of combos){
  await go(route(o,d));const visible=await page.locator('body').innerText();
  if(![o,d].includes('CN')){assert.equal(await page.locator('#cn-quarantine').isVisible(),false);assert.doesNotMatch(visible,/农业农村部|21 天|5 天|A证|出发前约两天/);assert.match(visible,/办理点、地址、电话：待补充/);}
  if(![o,d].includes('US'))assert.doesNotMatch(visible,/美国 CDC|美国入境的犬|USDA/);
  if(![o,d].some(c=>['DE','FR'].includes(c)))assert.doesNotMatch(visible,/欧盟委员会/);
  if(o==='JP')assert.equal(await page.locator('#source-list li').count(),0);
 }
 checks.push('七种国家组合：规则、官方入口、材料、检测点仅显示关联辖区；缺数据明确该问谁');
 await go(route('CN','DE'));assert.match(await page.textContent('#rule-provenance'),/eu.ec.rabies.primary-wait/);
 await go(route('DE','FR'));assert.equal(await page.locator('#rule-questions li').count(),0);checks.push('欧盟成员资格筛选不再只认法国；欧盟内部资料缺失不套非欧盟入境');
 await go(shanghaiRoute);await page.evaluate(()=>localStorage.setItem('petwaymark.pet.v2.dog','{"breed":"<img src=x>","weight":"NaN"}'));await page.reload();assert.match(await page.textContent('#pet-summary'),/尚未填写/);
 await page.evaluate(()=>{Storage.prototype.setItem=()=>{throw Error('blocked')};});await page.click('#open-pet');await page.fill('#breed','犬');await page.click('#pet-form button[type=submit]');assert.match(await page.textContent('#pet-storage-status'),/尚未保存/);await page.click('#close-pet');checks.push('无效本机数据忽略；存储拒绝不假称保存');
 await go(home);await page.click('#origin');await page.selectOption('#country','CN');await page.selectOption('#subdivision','HK');assert.equal(await page.inputValue('#country'),'HK');assert.doesNotMatch(await page.textContent('#city'),/北京/);checks.push('港澳台省级入口切到源辖区，避免内地规则混入');
 for(const width of [320,375,390,768]){
  await page.setViewportSize({width,height:844});await go(shanghaiRoute);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.click('#open-pet');assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.click('#close-pet');
 }
 checks.push('320/375/390/768px 结果和宠物填写页无横向溢出');
 assert.deepEqual(errors,[]);assert.deepEqual(remote,[]);checks.push('零脚本错误；零远程请求、零上传');
 fs.writeFileSync(path.join(artifacts,'v2-checks.json'),JSON.stringify({checks,errors,remote},null,2)+'\n');
 console.log(JSON.stringify({passed:checks.length,errors,remote},null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
