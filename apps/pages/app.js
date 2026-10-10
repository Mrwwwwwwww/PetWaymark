'use strict';
// Generated, attributed place slice; names do not imply rule coverage.
const bundle = window.PETWAYMARK_PAGE;
const locations = bundle.locations.countries;
const places = Object.fromEntries(Object.entries(locations).map(([code, country]) => [code, {
  name: country.name,
  cities: Object.fromEntries(country.cities.map(city => [city.name, city.areas.map(area => area.name)]))
}]));
const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.hash.length <= 6000 ? location.hash.slice(1) : 'invalid=1');
const validFormat = [...params.keys()].every(key => ['pet','origin','destination'].includes(key) && params.getAll(key).length === 1);
const trim = value => typeof value === 'string' ? value.trim().slice(0,60) : '';
function readPlace(raw) {
  try {
    if (typeof raw !== 'string' || raw.length > 1500) return null;
    const p = JSON.parse(raw);
    const validName = name => typeof name === 'string' && name.length <= 60 && !/[\u0000-\u001f\u007f]/.test(name);
    if (!p || typeof p.country !== 'string' || !Object.hasOwn(places,p.country) || !validName(p.city) || !p.city.trim() || !validName(p.area) || typeof p.manual !== 'boolean') return null;
    if (!p.manual && (!Object.hasOwn(places[p.country].cities,p.city) || (p.area && !places[p.country].cities[p.city].includes(p.area)))) return null;
    const city = locations[p.country].cities.find(c => c.name === p.city);
    const area = city?.areas.find(a => a.name === p.area);
    if (!p.manual && ((p.cityId && p.cityId !== city.id) || (p.areaId && p.areaId !== area?.id))) return null;
    return {country:p.country, city:trim(p.city), area:trim(p.area), manual:p.manual,
      cityId:p.manual ? null : city.id, areaId:p.manual ? null : area?.id || null};
  } catch { return null; }
}
const label = p => `${places[p.country].name} / ${p.city} / ${p.area || '区 / 乡镇未填'}${p.manual ? '（手填，地点未核实）' : ''}`;
const state = {pet:validFormat && ['dog','cat'].includes(params.get('pet')) ? params.get('pet') : '', origin:readPlace(validFormat ? params.get('origin') : null), destination:readPlace(validFormat ? params.get('destination') : null)};
function query() {
  const q = new URLSearchParams();
  if (state.pet) q.set('pet',state.pet);
  for (const side of ['origin','destination']) if (state[side]) q.set(side,JSON.stringify(state[side]));
  return q.toString();
}
if ($('journey')) {
  let active, draft;
  const dialog = $('picker');
  function updateHome() {
    $('pet-value').textContent = {dog:'狗',cat:'猫'}[state.pet] || '选狗或猫';
    for (const side of ['origin','destination']) $(side+'-value').textContent = state[side] ? label(state[side]) : '国家 → 城市 → 区 / 乡镇';
  }
  function options(id, values, prompt, selected) {
    const s = $(id); s.replaceChildren(new Option(prompt,''));
    values.forEach(v=>s.add(new Option(v,v)));
    s.value = values.includes(selected) ? selected : '';
  }
  function refresh() {
    const cityNames = draft.country ? Object.keys(places[draft.country].cities) : [];
    $('city-step').hidden = !draft.country;
    $('area-step').hidden = !draft.city;
    options('city',cityNames,'请选择城市',draft.city);
    options('area',draft.city ? places[draft.country].cities[draft.city] : [],'请选择区 / 乡镇',draft.area);
    $('search-step').hidden = !draft.country;
    $('missing-step').hidden = !draft.country;
    $('city-only').hidden = !draft.city;
    $('place-search').value = '';
    $('search-status').textContent = draft.city ? (places[draft.country].cities[draft.city].length ? '当前搜索：区 / 乡镇' : '这个城市的区 / 乡镇还没收录。可手填或只选到城市。') : '当前搜索：城市';
    $('confirm-place').disabled = !draft.area;
    $('confirm-place').textContent = draft.area ? '确认地点' : '选好区 / 乡镇后确认';
    $('manual-city').value = draft.city;
    $('manual-area').value = draft.area;
    $('picker-error').hidden = true;
  }
  function savePlace(p) { state[active] = readPlace(JSON.stringify({country:p.country,city:p.city,area:p.area,manual:p.manual})); updateHome(); dialog.close(); }
  for (const id of ['pet','origin','destination']) $(id).onclick = () => {
    active = id;
    $('picker-title').textContent = {pet:'带什么宠物',origin:'从哪里出发',destination:'到哪里去'}[id];
    $('pet-options').hidden = id !== 'pet'; $('place-options').hidden = id === 'pet';
    if (id !== 'pet') {
      const old = state[id];
      draft = old && !old.manual ? {...old} : {country:old?.country || '',city:'',area:'',manual:false};
      $('country').value = draft.country; refresh();
      if (old?.manual) { $('manual-city').value=old.city; $('manual-area').value=old.area; }
    }
    dialog.showModal();
  };
  $('close-picker').onclick = () => dialog.close();
  document.querySelectorAll('[data-pet]').forEach(b=>b.onclick=()=>{state.pet=b.dataset.pet;updateHome();dialog.close();});
  $('country').onchange = () => {draft={country:$('country').value,city:'',area:'',manual:false};refresh();};
  $('city').onchange = () => {draft.city=$('city').value;draft.area='';refresh();};
  $('area').onchange = () => {draft.area=$('area').value;refresh();};
  $('place-search').oninput = () => {
    const isArea = !!draft.city, id = isArea ? 'area' : 'city';
    const all = isArea ? places[draft.country].cities[draft.city] : Object.keys(places[draft.country].cities);
    const filtered = all.filter(v=>v.toLowerCase().includes($('place-search').value.trim().toLowerCase()));
    options(id,filtered,isArea ? '请选择区 / 乡镇' : '请选择城市',draft[id]);
    $('search-status').textContent = filtered.length ? `找到 ${filtered.length} 个收录的${isArea ? '区 / 乡镇' : '城市'}` : '这里还没收录。可以在下面手动填写。';
  };
  $('confirm-place').onclick = () => {if(draft.area) savePlace({...draft});};
  $('city-only').onclick = () => savePlace({...draft,area:''});
  $('use-manual').onclick = () => {
    const city = trim($('manual-city').value);
    if (!city) { $('picker-error').textContent='请填写城市名称。';$('picker-error').hidden=false;$('manual-city').focus();return; }
    savePlace({country:draft.country,city,area:trim($('manual-area').value),manual:true});
  };
  $('journey').onsubmit = event => {
    event.preventDefault();
    const missing = ['pet','origin','destination'].find(k=>!state[k]);
    const same = state.origin && state.destination && ['country','city','area'].every(k=>state.origin[k]===state.destination[k]);
    const message = missing ? {pet:'先选一下宠物：狗还是猫？',origin:'请选出发地。',destination:'请选目的地。'}[missing] : same ? '出发地和目的地相同，请检查一下。' : '';
    $('form-error').textContent=message;$('form-error').hidden=!message;
    if(message) {$(missing || 'destination').focus();return;}
    location.href='result.html#'+query();
  };
  updateHome();
}
if ($('trip')) {
  const submitted = location.hash.length > 1;
  if (!submitted) Object.assign(state,{pet:'cat',origin:{country:'CN',city:'上海市',area:'',manual:false},destination:{country:'CN',city:'北京市',area:'',manual:false}});
  const pet = {dog:'狗',cat:'猫'}[state.pet] || '宠物未选';
  const origin=state.origin ? label(state.origin) : '出发地未填', destination=state.destination ? label(state.destination) : '目的地未填';
  const description = `${origin} → ${destination} · ${pet}`;
  $('trip').textContent='示例清单：'+description;
  const complete = !!state.pet && !!state.origin && !!state.destination;
  const same = complete && ['country','city','area'].every(k=>state.origin[k]===state.destination[k]);
  const usable = complete && !same;
  $('ready').textContent=description+'。绿色仅表示填写完整，不表示能出行。';
  if(!usable) {$('ready-state').textContent='请检查';$('ready-state').className='state yellow';$('ready').textContent=same ? '出发地和目的地相同，请返回修改。' : '行程不完整，请返回选择狗或猫、出发地和目的地。';}
  $('edit').href='index.html#'+query();
  const cross = usable && state.origin.country !== state.destination.country;
  $('cross-border').hidden=!cross;
  $('authority-help').textContent = cross ? '分别向出发和入境两端的主管部门确认，不要把入境规定当作出境要求。' : usable && state.origin.country === 'CN' ? '中国国内可先找当地农业农村部门，问清具体材料和办理点。' : '向当地动物卫生主管部门确认；美国还要问目的州部门，法国要问当地主管部门。国家入口不能代替当地要求。';
  $('area-gap').hidden=!(usable && (!state.origin.area || !state.destination.area || state.origin.manual || state.destination.manual));
  $('source-context').textContent=usable ? '按你选择的国家列出查询入口。这些链接不代表已确认适用于你的行程；城市和乡镇的办理点仍要询问。' : '以下是固定示例的官方查询入口。请先返回补全行程。';
  const countries = new Set(usable ? [state.origin.country,state.destination.country] : ['CN']);
  const entries=[];
  if(countries.has('CN')) entries.push(['中国：农业农村部《动物检疫管理办法》','https://xmsyj.moa.gov.cn/gzdt/202209/t20220909_6408945.htm','查询检疫规定；具体材料、办理点和现行适用性待确认。'],['中国铁路 12306','https://www.12306.cn/index/','如乘铁路，在站内搜索“宠物托运”，询问具体站点、日期和接收条件。']);
  if(cross && state.destination.country==='CN') entries.push(['中国：携带宠物入境公告（商务部转载）','https://www.mofcom.gov.cn/zcfb/zgdwjjmywg/art/2019/art_71739ec848d14deca4ec330fad835774.html','查询中国入境事项；现行内容、附件和适用范围待核实。']);
  if(countries.has('US')) entries.push(['美国 CDC：动物入境说明','https://www.cdc.gov/importation/bringing-an-animal-into-the-us/index.html','美国入境查询入口；犬猫要求不同，还要查询 USDA 和目的州要求。若从美国出发，不能拿入境规定当出境规定。']);
  if(countries.has('FR')) entries.push(['欧盟委员会：从非欧盟国家带宠物入境','https://food.ec.europa.eu/animals/live-animal-movements/dogs-cats-and-ferrets/bringing-pet-eu-non-eu-country_en','欧盟入境查询入口；法国当地要求仍未核实，不能用于判断法国国内运输或从法国出境。']);
  $('source-list').replaceChildren(...entries.map(([title,url,note])=>{
    const li=document.createElement('li'),a=document.createElement('a'),small=document.createElement('small');
    a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=title+' ↗';small.textContent=note;li.append(a,document.createElement('br'),small);return li;
  }));
  const candidates = usable ? bundle.rules.filter(rule => {
    const scope = rule.scope;
    if (!scope.species.includes(state.pet)) return false;
    // Missing transport, travel/vaccine history etc. stays an explicit question.
    // This is candidate selection, never a finding that a rule applies.
    if (scope.subdivisions.length) return false;
    const match = (region, country) => region === 'any' || region === country ||
      (region === 'EU' && country === 'FR') || (region === 'any_non_eu' && country !== 'FR');
    if (!match(scope.origin, state.origin.country) || !match(scope.destination, state.destination.country)) return false;
    if (scope.movement_category === 'carried_entry' || scope.movement_category === 'all_imports' || scope.movement_category === 'non_commercial_pet') return cross;
    if (scope.movement_category === 'intra_eu_pet') return false;
    return scope.movement_category === 'domestic_pet' && !cross;
  }) : [];
  $('rule-questions').replaceChildren(...candidates.map(rule => {
    const li = document.createElement('li'); li.textContent = rule.question + '（待确认）'; return li;
  }));
  $('rule-gap').textContent = candidates.length ? '这些问题来自尚未复核的资料。还要补充年龄、接种与旅行史、是否随主人同行、日期、乘坐方式和中转；目前不能确定哪些要求适用。' : '现有资料还没有覆盖这趟行程的具体要求。上面是通用问法，需要承运方和当地主管部门答复。';
  $('data-version').textContent = `规则整理版本：${bundle.dataVersion}；页面构建：${bundle.builtAt}。核实可行路线为 0。`;
  $('location-provenance').textContent = `地名切片版本：${bundle.locations.version}。仅收录中国、美国、法国的少量城市；父级来自 GeoNames 编码，未完成政府逐项核对。中文显示名由本项目整理。`;
  $('rule-provenance').replaceChildren(...candidates.map(rule => {
    const p = document.createElement('p');
    p.textContent = `${rule.id} · ${rule.review.status} · 独立复核日期：${rule.review.last_verified_at || '未知'}。适用范围：${JSON.stringify(rule.scope)}；有效性：${JSON.stringify(rule.validity)}。`;
    for (const source of rule.sources) {
      const a = document.createElement('a'); a.href = source.url; a.textContent = source.title['zh-CN']; a.target = '_blank'; a.rel = 'noopener noreferrer';
      p.append(document.createElement('br'), a, document.createTextNode(` · ${source.id} · 查阅：${source.accessed_at}；查阅不等于复核。`));
    }
    return p;
  }));
  $('questions').value=`我准备从${origin}到${destination}，带一只${pet}。品种____，体重____公斤，出发日期____，乘坐方式____，是否中转____。请问这趟能否接收？需要哪些证件、在哪里办理、先办哪项？受理后多久能拿到，有没有等待期，到出发那天还有效吗？还缺哪些信息才能答复？方便给我官方说明链接吗？`;
  $('copy').onclick=async()=>{
    try {await navigator.clipboard.writeText($('questions').value);$('copy-status').textContent='已复制。可以粘贴给你准备咨询的机构。';}
    catch {$('questions').focus();$('questions').select();$('copy-status').textContent='浏览器没允许自动复制。文字已选中，请手动复制。';}
  };
  function preparePrint() { $('sources').open=true; $('print-questions').textContent=$('questions').value; }
  window.addEventListener('beforeprint', preparePrint);
  $('print').onclick=()=>{preparePrint();window.print();};
}

// Browser back/forward can replace a fragment on the same document.
window.addEventListener("hashchange", () => location.reload());
