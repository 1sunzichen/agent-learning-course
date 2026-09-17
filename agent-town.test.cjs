const assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm'),E=require('./agent-town-engine.js');
const good={tool:'weather',city:'request',missing:'ask',timeout:'stop'};
assert(E.suite(E.defaults()).every(r=>!r.pass));
assert(E.suite(good).every(r=>r.pass));assert(E.suite(good,true).every(r=>r.pass));
let combos=0,passing=0;
for(const tool of ['calculator','weather','notes'])for(const city of ['none','fixed','request'])for(const missing of ['guess','ask'])for(const timeout of ['wait','invent','stop']){combos++;if(E.suite({tool,city,missing,timeout}).every(r=>r.pass))passing++;}
assert.equal(combos,54);assert.equal(passing,1);
assert(!E.simulate({...good,city:'fixed'},E.cases[1]).pass);
assert.equal(E.simulate(good,E.cases[2]).actual,'请补充城市');
assert.equal(E.simulate({...good,timeout:'wait'},E.cases[3]).actual,'任务仍在等待');
assert.equal(E.simulate({...good,timeout:'invent'},E.cases[3]).actual,'青禾镇：晴');
let s={...E.initial(),entered:true,observed:true,config:good};
assert.throws(()=>E.run(s,true));assert.throws(()=>E.run(E.initial()));
s=E.run(s);assert(s.certified&&!s.complete&&!s.rewardGranted);
s=E.run(s,true);assert(s.complete&&s.rewardGranted);assert.equal(s.attempts,2);
s=E.run(s,true);assert.equal(s.rewardGranted,true);
let loaded=E.restore(JSON.stringify(s));assert(loaded.complete&&loaded.rewardGranted);assert.deepEqual(loaded.config,good);
s=E.replay(s);assert(s.rewardGranted&&!s.complete&&!s.certified&&!s.observed);assert.deepEqual(s.config,E.defaults());
s={...s,observed:true,config:good};s=E.run(s);s=E.run(s,true);assert.equal(s.rewardGranted,true);
s=E.configure(s,'city','fixed');assert(!s.complete&&!s.certified&&s.rewardGranted);assert.throws(()=>E.run(s,true));
assert.throws(()=>E.restore('broken'));assert.throws(()=>E.restore(JSON.stringify({...E.initial(),certified:true})));assert.throws(()=>E.configure(s,'tool','unknown'));
// DOM-free controller smoke test: real handlers, fake elements/storage; no user data touched.
const nodes={},handlers={},store={'quiz-state':'original quiz','agent-learning-v2':'original learning'};
function node(id){return nodes[id]??={id,hidden:false,value:'',textContent:'',className:'',classList:{toggle(){},add(){},remove(){}},append(){},replaceChildren(){},setAttribute(){},removeAttribute(){},focus(){},scrollIntoView(){},dataset:{}};}
const tools=['calculator','weather','notes'].map(tool=>({...node('tool-'+tool),dataset:{tool}}));
let ctx={TownEngine:E,console,localStorage:{getItem:k=>store[k]??null,setItem:(k,v)=>store[k]=v},window:{matchMedia:()=>({matches:true})},document:{getElementById:node,querySelectorAll:q=>q==='[data-tool]'?tools:[],body:node('body'),createElement:tag=>({...node('created'),tag})},setTimeout};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(__dirname+'/agent-town.js','utf8'),ctx);
(async()=>{node('enter').onclick();await node('observe').onclick();tools[1].onclick();for(const k of ['city','missing','timeout']){node(k).value=good[k];node(k).onchange();}await node('test').onclick();assert.equal(node('transferBox').hidden,false);await node('transfer').onclick();assert.equal(node('ending').hidden,false);assert.equal(E.restore(store[E.KEY]).complete,true);assert.equal(store['quiz-state'],'original quiz');assert.equal(store['agent-learning-v2'],'original learning');node('replay').onclick();assert.equal(E.restore(store[E.KEY]).rewardGranted,true);assert.equal(node('ending').hidden,true);node('loadTrap').onclick();node('trialCity').value='雨桥城';node('trialStart').onclick();while(!node('trialNext').hidden)node('trialNext').onclick();assert(node('trialCompare').textContent.includes('实际：青禾镇：晴'));node('city').value='request';node('city').onchange();node('trialStart').onclick();while(!node('trialNext').hidden)node('trialNext').onclick();assert(node('trialCompare').textContent.includes('雨桥城：雨'));assert(node('trialCompare').textContent.includes('你改了：城市来源'));console.log('PASS: 54 configurations, failures, migration challenge, replay, reward idempotence, restore, controller journey and course storage isolation.');})();
