'use strict';
const E=TownEngine,$=id=>document.getElementById(id);
let state=E.initial(),locked=false,storageBlocked=false;
try{state=E.restore(localStorage.getItem(E.KEY));}catch(e){storageBlocked=true;$('storageStatus').textContent='无法读取游戏存档；原值未覆盖。本次可临时试玩，刷新后不会保存。';}
function save(next){state=next;if(storageBlocked)return;try{localStorage.setItem(E.KEY,JSON.stringify(state));if(window.dispatchEvent)window.dispatchEvent(new CustomEvent('town-first-progress'));}catch(e){$('storageStatus').textContent='存档写入失败；本次仍可玩，刷新可能丢失进度。原课程数据不受影响。';}}
function say(text,speaker='滴答 · 天气机器人'){$('speaker').textContent=speaker;$('dialogue').textContent=text;}
function render(){
 $('welcome').hidden=state.entered;$('play').hidden=!state.entered||state.complete;$('controls').hidden=!state.observed;$('ending').hidden=!state.complete;$('transferBox').hidden=!state.certified;
 document.body.classList.toggle('repaired',state.complete);
 $('mapDesc').textContent='四区域完整关卡可从上方导航进入；主线按关解锁。'+(state.complete?'中央天气屏已亮起，滴答加入工作室。':'中央天气屏等待修复。');
 $('robotEyes').setAttribute('d',state.complete?'m-10 0 3-3 3 3m8 0 3-3 3 3':'m-9-3 5 5m0-5-5 5m14-5 5 5m0-5-5 5');
 $('boardText').textContent=state.complete?'青禾镇 · 晴':'天气离线';$('boardIcon').textContent=state.complete?'☀':'?';
 $('studioTitle').textContent=state.rewardGranted?'工作室 Lv.2 · 滴答已加入':'工作室 Lv.1 · 等待第一位伙伴';
 $('studioNote').textContent=state.rewardGranted?'伙伴奖励已领取，重复体验不会重复升级。':'修好天气机器人「滴答」，邀请它加入。';
 $('worldNote').textContent=state.complete?'天气屏恢复了。小葵带上遮阳棚，滴答留在工作室帮忙。':'小葵要去集市摆摊，却不知道该带伞还是遮阳棚。';
 const step=state.complete?4:state.certified?3:state.observed?2:state.entered?1:0;
 for(let i=0;i<4;i++){$('step'+i).className=i<step?'done':i===step?'active':'';if(i===step)$('step'+i).setAttribute('aria-current','step');else $('step'+i).removeAttribute('aria-current');}
 document.querySelectorAll('[data-tool]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.tool===state.config.tool)));
 for(const k of ['city','missing','timeout'])$(k).value=state.config[k];
 $('taskTitle').textContent=state.certified?'本地测试通过，去隔壁城市试试':state.observed?'修线路，让工具听懂居民':'先看一眼，哪里出错了？';
 if(state.complete)say('“不确定时先澄清，超时时诚实回复。我终于会好好工作了！”');
}
function lock(value){locked=value;document.querySelectorAll('button,select').forEach(el=>el.disabled=value);}
const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
async function animate(trace){$('trace').textContent='';for(const line of trace){$('trace').textContent+=($('trace').textContent?'\n':'')+line;$('trace').classList.remove('pulse');if(!reduced.matches){void $('trace').offsetWidth;$('trace').classList.add('pulse');await new Promise(resolve=>setTimeout(resolve,330));}}}
function renderResults(results,transfer){const out=$('results');out.replaceChildren();const heading=document.createElement('p');heading.className='result-heading';heading.textContent=(transfer?'异地挑战':'本地测试')+' · '+results.filter(r=>r.pass).length+'/'+results.length+' 通过';out.append(heading);
 results.forEach(r=>{const card=document.createElement('details');card.className='result'+(r.pass?' pass':'');card.open=!r.pass;const title=document.createElement('summary');title.textContent=(r.pass?'✓ ':'✕ ')+r.label;card.append(title);for(const text of ['预期：'+r.expected,'实际：'+r.actual,r.cause]){const p=document.createElement('p');p.textContent=text;card.append(p);}const trace=document.createElement('pre');trace.textContent=r.trace.join('\n');card.append(trace);out.append(card);});}
$('enter').onclick=()=>{save({...state,entered:true});render();say('“这是刚才的线路记录。请先回放，找到天气请求走错的地方。”','小葵 · 集市摊主');$('observe').focus();};
$('observe').onclick=async()=>{if(locked)return;lock(true);try{const r=E.simulate(E.defaults(),E.cases[0]);await animate(r.trace);save({...state,observed:true});render();say('“我把天气交给计算器了！请点选正确工具，再给它接上城市参数。”');}finally{lock(false);}};
function change(key,value){if(locked)return;save(E.configure(state,key,value));$('results').replaceChildren();render();say('线路已更新。重新运行测试，看看这次回复会怎样变化。');}
for(const b of document.querySelectorAll('[data-tool]'))b.onclick=()=>change('tool',b.dataset.tool);
for(const key of ['city','missing','timeout'])$(key).onchange=()=>change(key,$(key).value);
async function test(transfer=false){if(locked)return;lock(true);try{const next=E.run(state,transfer);const all=next.last.results;for(const result of all)await animate(result.trace);save(next);renderResults(all,transfer);render();if(!state.complete){const fail=all.find(r=>!r.pass);say(fail?'“'+fail.cause+'”': '“四项测试都通过了！隔壁两座城市也来找我们，试试同一套线路。”');}if(state.complete)$('ending').scrollIntoView({behavior:reduced.matches?'instant':'smooth',block:'nearest'});}catch(e){say('请先完成故障回放和本地测试，再继续。');}finally{lock(false);}}
$('test').onclick=()=>test();$('transfer').onclick=()=>test(true);
const hints=['先看工具的职责：天气请求应交给能查询天气的工具。点选工具就会改变线路。','一座城市通过不够。若雨桥城仍回复青禾镇，请检查 city 是否来自居民请求。','缺少城市时先追问；服务超时后停止并诚实报告。不能猜城市或编造晴天。'];
$('hint').onclick=()=>{const index=Math.min(state.hints,hints.length-1);$('hintText').textContent=hints[index];save({...state,hints:state.hints+1});};
$('replay').onclick=()=>{save(E.replay(state));trial=null;previousTrial=null;$('trialView').hidden=true;$('trialSteps').replaceChildren();$('results').replaceChildren();$('hintText').textContent='';$('trace').textContent='等待回放：居民 → 机器人 → 工具 → 回复';render();say('“再来修一次吧！这次试着不看提示，解释每个故障为什么发生。”','小葵 · 集市摊主');$('observe').focus();};
render();if(state.entered&&!state.complete)say(state.certified?'存档已恢复：本地测试通过，继续异地挑战。':state.observed?'存档已恢复：线路还在，继续修理并运行测试。':'存档已恢复：先回放故障。');

// 不计分的因果实验：冻结本次配置，逐步显示实际模拟轨迹。
let trial=null,previousTrial=null;
const meaning=line=>line.startsWith('收到请求')?'这是居民给机器人的信息，还没有调用任何工具。':line.startsWith('路由')?'先决定“让谁做事”。选错功能，后面的城市填得再对也没有用。':line.startsWith('参数')?'再决定“交给它什么”。city 是城市输入格；这里显示真正传入的值，不是居民原话。':line.startsWith('参数校验')?'信息不完整时，应该先补齐信息，而不是让工具凭空猜测。':line.startsWith('调用天气服务')?'现在才真正使用天气功能。这里使用本地教学数据；真实项目中通常是一次函数或接口调用。':'这是居民最终看到的回复。检查它是否真的回答了这位居民的问题。';
function revealTrial(){
 if(!trial)return;
 const line=trial.result.trace[trial.index++],card=document.createElement('div');card.className='trial-step';
 const title=document.createElement('b');title.textContent=trial.index+' / '+line;const explanation=document.createElement('p');explanation.textContent=meaning(line);card.append(title,explanation);$('trialSteps').append(card);
 $('trialNext').hidden=trial.index>=trial.result.trace.length;
 if($('trialNext').hidden){
  const changed=previousTrial?Object.keys(trial.config).filter(k=>trial.config[k]!==previousTrial.config[k]):[];
  const names={tool:'工具',city:'城市来源',missing:'缺参处理',timeout:'超时处理'};
  $('trialCompare').textContent=(previousTrial?'上一次：居民问 '+(previousTrial.city||'（未说城市）')+' → '+previousTrial.result.actual+'。这一次：居民问 '+(trial.city||'（未说城市）')+' → '+trial.result.actual+'。'+(changed.length?'你改了：'+changed.map(k=>names[k]).join('、')+'。':'线路没变；注意输入变化有没有传到工具。'):'这一单预期：'+trial.result.expected+'。实际：'+trial.result.actual+'。')+' '+trial.result.cause;
  previousTrial=trial;
 }
}
$('trialStart').onclick=()=>{
 const city=$('trialCity').value.trim(),slow=$('trialSlow').checked;
 const database={青禾镇:'晴',雨桥城:'雨',海盐湾:'雨',松果城:'晴'};
 const expected=!city?'请补充城市':slow?'服务超时，请稍后重试':city+'：'+(database[city]||'未知');
 trial={city,config:{...state.config},result:E.simulate(state.config,{city,slow,expected,id:'trial',label:'单次探索'}),index:0};
 $('trialView').hidden=false;$('trialSteps').replaceChildren();$('trialCompare').textContent='';$('trialRequest').textContent='本次请求：“'+(city||'……')+'天气怎样？” · 本次线路已固定，逐步查看不会改变配置。';revealTrial();
};
$('trialNext').onclick=revealTrial;
for(const b of document.querySelectorAll('[data-city]'))b.onclick=()=>{$('trialCity').value=b.dataset.city;};
$('loadTrap').onclick=()=>{let next=state;for(const [key,value] of Object.entries({tool:'weather',city:'fixed',missing:'ask',timeout:'stop'}))next=E.configure(next,key,value);save(next);$('results').replaceChildren();render();say('天气工具已经选对了。但我们把城市固定写成青禾镇。换一个居民来问，会发生什么？');};
