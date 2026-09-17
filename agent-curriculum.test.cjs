const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(__dirname+'/agent-checkin.html','utf8');
const original=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const code=fs.readFileSync(__dirname+'/agent-curriculum.js','utf8');
function env(seed={}) {
 const data={...seed},elements={},alerts=[];
 const ctx={console,Date,Blob,URL,setTimeout,alert:x=>alerts.push(x),localStorage:{getItem:k=>data[k]??null,setItem:(k,v)=>{data[k]=v;}},document:{getElementById:id=>elements[id]??=( {value:'',textContent:'',innerHTML:'',style:{},classList:{toggle(){}}} )}};
 vm.createContext(ctx);vm.runInContext(original,ctx);vm.runInContext(code,ctx);
 return {ctx,data,elements,alerts,run:s=>vm.runInContext(s,ctx)};
}
let e=env({'quiz-state':'{"wrong":["quiz-1-4::0"]}','legacy-checkin':'{"9":true}'});
assert.equal(e.run('CURRICULUM.length'),60);assert.equal(e.run('new Set(CURRICULUM.map(c=>c.day)).size'),60);
assert(e.run('CURRICULUM.every(c=>c.output && c.variant && entryOf(c.day))'));
assert.equal(e.run('Object.keys(loadDone()).length'),0);assert.equal(e.run('Object.keys(learning.history.autoDone).length'),7);
assert.equal(e.data['quiz-state'],'{"wrong":["quiz-1-4::0"]}');assert.equal(e.data['legacy-checkin'],'{"9":true}');
e.run('renderCheckin()');assert.equal((e.elements.ckPhases.innerHTML.match(/id="lesson-/g)||[]).length,60);
function submit(stage,result='pass',evidence='commit abc; test normal+failure; expected=actual') {
 for(const [k,v] of Object.entries({stage,result,evidence,due:e.run('later(3)')})) e.ctx.document.getElementById(k+'-1').value=String(v);
 e.run('saveEvidence(1)');
}
submit(2);assert.equal(e.run('stageOf(1)'),0);
submit(0,'pass','');assert.equal(e.run('stageOf(1)'),0);
submit(0);submit(1);submit(2);assert.equal(e.run('stageOf(1)'),3);
submit(3);assert.equal(e.run('stageOf(1)'),3);
e.run('learning.lessons[1].events[2].at=new Date(Date.now()-4*86400000).toISOString()');submit(3);assert.equal(e.run('stageOf(1)'),4);
submit(3,'fail');assert.equal(e.run('recordOf(1).events.length'),5);assert(e.elements.ckPhases.innerHTML.includes('最近尝试未通过'));
e=env(e.data);assert.equal(e.run('stageOf(1)'),4);assert.equal(e.run('recordOf(1).events.length'),5);
e.run('learning.lessons[1].due=localDate();renderCheckin()');assert(e.elements.reviewQueue.innerHTML.includes('openLesson(1)'));
const bad=env({'agent-learning-v2':'broken'});assert.equal(bad.data['agent-learning-v2'],'broken');assert.equal(bad.run('persist(learning)'),false);
e.ctx.localStorage.setItem=()=>{throw Error('quota')};assert.equal(e.run('persist(learning)'),false);
console.log('PASS: 60 lessons, legacy preservation, no mastery migration, evidence sequence, 3-day delay, append-only failures, reload, due queue, corrupt/quota handling.');
