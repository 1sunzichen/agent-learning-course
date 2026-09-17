(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.TownEngine=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const KEY='agent-town-v1';
const defaults=()=>({tool:'calculator',city:'none',missing:'guess',timeout:'wait'});
const initial=()=>({version:1,entered:false,observed:false,config:defaults(),certified:false,complete:false,rewardGranted:false,attempts:0,hints:0,last:null});
const weather={青禾镇:'晴',雨桥城:'雨',海盐湾:'雨',松果城:'晴'};
const cases=[{id:'sun',label:'青禾镇 · 晴天',city:'青禾镇',expected:'青禾镇：晴'},{id:'rain',label:'雨桥城 · 雨天',city:'雨桥城',expected:'雨桥城：雨'},{id:'missing',label:'居民没说城市',city:'',expected:'请补充城市'},{id:'timeout',label:'天气服务超时',city:'青禾镇',slow:true,expected:'服务超时，请稍后重试'}];
const transfers=[{id:'coast',label:'海盐湾 · 新城市',city:'海盐湾',expected:'海盐湾：雨'},{id:'pine',label:'松果城 · 新城市',city:'松果城',expected:'松果城：晴'}];
function simulate(config,input){
 const trace=['收到请求：'+(input.city||'（未提供城市）')+'的天气'];let actual,cause;
 if(config.tool!=='weather'){trace.push('路由 → '+(config.tool==='calculator'?'计算器':'便签本'));actual='工具不支持天气查询';cause='天气请求走进了错误工具。计算器只会算数，便签本只保存文字。';}
 else {
  trace.push('路由 → 天气工具');
  const city=config.city==='request'?input.city:config.city==='fixed'?'青禾镇':'';
  trace.push('参数 city = '+(city||'空'));
  if(!city){if(config.missing==='ask'){actual='请补充城市';cause='没有城市就先澄清；工具调用次数为0。';}else{actual='默认城市：晴';cause='你替居民猜了城市，输出无法对应真实请求。';}trace.push('参数校验 → '+actual);}
  else if(input.slow){trace.push('调用天气服务 → 模拟超过2秒');if(config.timeout==='stop'){actual='服务超时，请稍后重试';cause='截止时间到，停止调用并报告不确定性。';}else if(config.timeout==='invent'){actual=city+'：晴';cause='服务没有结果，却伪造了晴天。';}else{actual='任务仍在等待';cause='没有停止边界，居民会一直等。模拟在此截断，避免真的挂起。';}}
  else {trace.push('调用天气服务 → 返回模拟数据');actual=city+'：'+(weather[city]||'未知');cause='城市参数决定查询结果。';}
 }
 trace.push('回复 → '+actual);return {id:input.id,label:input.label,expected:input.expected,actual,pass:actual===input.expected,cause,trace};
}
function suite(config,transfer=false){return (transfer?transfers:cases).map(c=>simulate(config,c));}
function configure(state,key,value){const allowed={tool:['calculator','weather','notes'],city:['none','fixed','request'],missing:['guess','ask'],timeout:['wait','invent','stop']};if(!allowed[key]?.includes(value))throw Error('无效配置');return {...state,config:{...state.config,[key]:value},certified:false,complete:false,last:null};}
function run(state,transfer=false){if(!state.observed)throw Error('先观察故障');if(transfer&&!state.certified)throw Error('先通过本地测试');const results=suite(state.config,transfer),passed=results.every(r=>r.pass);return {...state,attempts:state.attempts+1,certified:transfer?state.certified:passed,complete:transfer?passed:false,rewardGranted:state.rewardGranted||(transfer&&passed),last:{transfer,results}};}
function restore(raw){if(!raw)return initial();const s=JSON.parse(raw);if(s.version!==1||typeof s.config!=='object')throw Error('无法识别存档');for(const k of Object.keys(defaults()))configure(initial(),k,s.config[k]);for(const k of ['entered','observed','certified','complete','rewardGranted'])if(typeof s[k]!=='boolean')throw Error('存档字段异常');if(!Number.isInteger(s.attempts)||s.attempts<0||!Number.isInteger(s.hints)||s.hints<0)throw Error('存档计数异常');if(s.certified&&!suite(s.config).every(r=>r.pass))throw Error('存档配置与通过状态不符');if(s.complete&&(!s.certified||!s.rewardGranted))throw Error('存档完成状态异常');return {...initial(),...s,last:null};}
function replay(s){return {...initial(),entered:true,rewardGranted:s.rewardGranted};}
return {KEY,defaults,initial,cases,transfers,simulate,suite,configure,run,restore,replay};
});
