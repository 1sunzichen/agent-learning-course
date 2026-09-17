/* 课程 v2：仅保存学习者提交的证据，不执行或验证练习代码。 */
const CURRICULUM = `
最小任务助手：接收任务并调用一个只读工具|工具返回空值，保留错误而非编造结果
工具参数契约与白名单|传入未知工具和缺失参数，断言拒绝执行
为助手加入资料检索和来源|检索无命中时明确回答证据不足
会话记录与任务状态分别落盘|重启后恢复同一任务且不串入另一用户数据
助手逐步输出事件|中途断流后标记未完成，不能伪报成功
保存可修改的执行计划|执行中用户改变目标，废弃旧计划剩余步骤
用测试反馈修正助手结果|注入错误结果，限制修正次数并保留失败
为工具加入超时、重试与幂等键|模拟响应丢失后重试，副作用只发生一次
按任务ID记录工具输入输出与耗时|工具异常时仍能串起完整调用链
交付助手v0.1与运行说明|全新目录按说明运行正常与失败用例
控制助手上下文预算|长对话下仍保留任务约束和未完成步骤
记录每任务token与费用估算|超预算时停止并报告已花费用和剩余任务
版本化提示词并保留基线|换一种任务表述，比较结果而非只改措辞
校验助手结构化结果|非法JSON及字段类型错误均被捕获
为只读工具加入可失效缓存|资料更新后旧缓存失效且跨用户隔离
隔离资料中的不可信指令|资料诱导越权调用时工具层拒绝
显式定义任务状态与合法转移|等待澄清时用户改口，旧执行不再继续
并发执行独立只读工具|一个工具失败，其他结果仍可追踪
建立固定任务评测集与基线报告|加入失败用例，成功率分母包含失败
单Agent阶段验收与故障复盘|关闭答案重建核心循环并重跑所有回归
增加可选协调者和工作者|同任务单Agent可完成时保留简单路径
用有类型的阶段产物连接流水线|中间阶段缺字段，下游禁止使用无效结果
持久化编排状态与事件|写入检查点后杀进程，恢复未完成步骤
中断恢复与副作用账本|执行成功但确认丢失，重启重试不重复生效
定义消息协议与任务版本号|重复、乱序和过期消息被正确处理
共享状态加入版本冲突处理|两个工作者同时更新，冲突不得静默覆盖
部分失败、重试与降级策略|一路不可用时返回带缺口标记的部分结果
端到端deadline与取消传播|子任务超时后停止排队与无意义重试
比较单Agent与多Agent架构|同任务同评测集报告成功率、成本和p50/p95耗时
交付助手v0.2及恢复演示|组合断网、重启、重试，核对副作用账本
按依赖分解任务并验证完成条件|无法满足的依赖应阻塞并解释原因
事件路由、去重与死信记录|重复投递和未知事件不会丢失或无限循环
共享记忆的归属与有效期|过期或他人资料不能影响当前任务
限制循环、跳数与等待时间|构造循环委派，有限步骤内退出
串联跨Agent trace与错误原因|某分支失败仍能定位任务和父子调用
为多Agent设置统一预算|并行分支同时花费，整体不越预算
人审暂停与用户改口|暂停后修改目标，旧审批不可用于新计划
公平复跑单Agent与多Agent|固定模型、工具、任务和重复次数，记录失败与方差
最小权限与工具授权边界|低权限工作者请求写操作，确定性拒绝
编排阶段验收与选型决策|按实测决定保留多Agent、局部采用或退回单Agent
用LangChain适配助手已有接口|同评测集与原实现回归比较
用LangGraph表达既有任务状态|非法状态跳转和重启恢复符合既定契约
为助手接入一个MCP只读工具|工具发现失败和参数不兼容时可诊断
统一评测入口、配置与报告格式|故意破坏一项能力，评测必须捕获退化
为助手资料检索加入切块与重排|相似但不相关文档不能冒充有效证据
按数据量和过滤需求比较向量库|删除资料后检索不应返回已删除内容
比较embedding方案与成本|换领域或同义表达后记录召回变化
建立检索标注集与质量报告|无答案问题独立计分，不能只看有命中样本
验证框架检查点与人审恢复|暂停重启后审批一次，副作用仍只执行一次
追踪一次框架调用到源码边界|定位重试或状态保存的真实责任层
记录框架迁移收益与代价|同样故障在原生与框架实现下对照排查
生态阶段验收与依赖锁定|新环境复建，固定评测集无未解释退化
收敛持续项目需求与验收范围|用户改变报告需求，更新版本与验收样例
给助手增加可替换的联网检索适配器|断网、无结果和冲突来源均保留证据缺口
根据阶段对比结果选择协作方式|禁止只为使用多Agent而增加角色，重测复杂度收益
输出带来源和缺口的任务报告|部分资料缺失，报告不能宣称完整完成
给持续项目增加API与任务查询|重复提交、取消和跨用户读取均受控
在本机容器验证部署与恢复|重启服务后状态恢复，失败可回滚
用真实结果写项目说明和架构取舍|指出一个未解决失败，不能虚构成功率
最终演示、独立复现与下一轮计划|陌生变式任务闭卷完成，记录未达标项并排复习
`.trim().split('\n').map((line,i)=>{const [output,variant]=line.split('|');return {day:i+1,output,variant};});
const LEARNING_KEY = 'agent-learning-v2';
const STAGES = ['看懂示例','脱离答案实现','改变条件仍能完成','隔几天独立复现'];
let storageProblem = '';
function readLearning() {
  try {
    const raw = localStorage.getItem(LEARNING_KEY);
    if(raw) { const data=JSON.parse(raw); if(data.version!==2 || !data.lessons || !data.history) throw Error('学习记录格式无法识别'); return data; }
    // 原版唯一完成来源是 AUTO_DONE；保留快照，绝不升级成能力证据。
    const data={version:2,lessons:{},history:{autoDone:{...AUTO_DONE},source:'旧版自动标记（材料生成）；历史自报进度，未验证',migratedAt:new Date().toISOString()}};
    localStorage.setItem(LEARNING_KEY,JSON.stringify(data)); return data;
  } catch(e) { storageProblem='存储不可用或记录格式异常；原数据未覆盖。请先导出/检查浏览器存储。'; return {version:2,lessons:{},history:{autoDone:{...AUTO_DONE}}}; }
}
let learning=readLearning();
function persist(next) {
  if(storageProblem) { alert(storageProblem); return false; }
  try { localStorage.setItem(LEARNING_KEY,JSON.stringify(next)); learning=next; return true; }
  catch(e) { alert('保存失败：浏览器存储不可用或已满。本次输入仍在页面，请复制备份。'); return false; }
}
function escapeText(s) { return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function localDate(date=new Date()) { return [date.getFullYear(),String(date.getMonth()+1).padStart(2,'0'),String(date.getDate()).padStart(2,'0')].join('-'); }
function later(days) { const d=new Date();d.setDate(d.getDate()+days);return localDate(d); }
function recordOf(day) { return learning.lessons[day] || {events:[],due:''}; }
function stageOf(day) { return recordOf(day).events.reduce((n,e)=>e.result==='pass'?Math.max(n,e.stage+1):n,0); }
function loadDone() { const result={};CURRICULUM.forEach(c=>{if(stageOf(c.day)===4)result[c.day]=true;});return result; }
function saveEvidence(day) {
  const stage=Number(document.getElementById('stage-'+day).value);
  const evidence=document.getElementById('evidence-'+day).value.trim();
  const result=document.getElementById('result-'+day).value;
  const due=document.getElementById('due-'+day).value;
  if(!evidence || !due) return alert('请填写证据和下次复习日期。证据应包含命令/产物位置、预期与实际结果。');
  if(due<=localDate()) return alert('下次复习日期请选择明天或之后；到期任务可今天执行并记录。');
  const rec=recordOf(day), previous=stageOf(day);
  if(stage>previous) return alert('请先提交前一层级证据，不从历史完成记录跳级。');
  if(stage===3 && result==='pass') {
    const variation=rec.events.find(e=>e.stage===2 && e.result==='pass');
    if(!variation || Date.now()-Date.parse(variation.at)<3*86400000) return alert('独立复现至少安排在首次变式通过 3 天后；现在可以记录未通过或重做前面层级。');
  }
  const next=JSON.parse(JSON.stringify(learning));
  next.lessons[day]={...rec,due,events:[...rec.events,{stage,result,evidence,at:new Date().toISOString()}]};
  if(persist(next)) {renderCheckin();document.getElementById('lesson-'+day).open=true;document.getElementById('save-status').textContent='第 '+day+' 关已保存（学习者自报，未自动验证代码）。';}
}
function exportLearning() {
  const all={};try {for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k===LEARNING_KEY || /quiz|agent|checkin/i.test(k)) all[k]=localStorage.getItem(k);}}catch(e){alert('无法读取存储');return;}
  const url=URL.createObjectURL(new Blob([JSON.stringify(all,null,2)],{type:'application/json'}));
  const a=document.createElement('a');a.href=url;a.download='agent-learning-backup.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function renderCheckin() {
  const done=loadDone(), next=nextLesson(done), today=localDate();
  const due=CURRICULUM.filter(c=>recordOf(c.day).due && recordOf(c.day).due<=today);
  document.getElementById('reviewQueue').innerHTML=due.length?due.map(c=>'<button onclick="openLesson('+c.day+')">第 '+c.day+' 关 · '+escapeText(recordOf(c.day).due)+'</button>').join(''):'暂无到期复习。首次变式通过后至少隔 3 天独立复现，之后建议再隔 7 天复习。';
  document.getElementById('ckPhases').innerHTML=PHASES.map(ph=>'<section class="phase '+ph.cls+'"><h2 class="phase-head"><span class="dot"></span>'+ph.name+'<span class="cnt">复现证据 '+CURRICULUM.filter(c=>c.day>=ph.from&&c.day<=ph.to&&done[c.day]).length+'/'+(ph.to-ph.from+1)+'</span></h2>'+CURRICULUM.filter(c=>c.day>=ph.from&&c.day<=ph.to).map(c=>{
    const d=c.day,e=entryOf(d),r=recordOf(d),st=stageOf(d),last=r.events.at(-1);
    const status=last?.result==='fail'?'最近尝试未通过 · 待修复':st?STAGES[st-1]+' · 已提交证据':'尚无学习证据';
    return '<details class="lesson" id="lesson-'+d+'"><summary><span class="dnum">'+d+'</span><span><b>'+escapeText(c.output)+'</b><small>'+escapeText(status)+(AUTO_DONE[d]?' · 材料已准备':'')+(learning.history.autoDone?.[d]?' · 历史自报记录':'')+'</small></span></summary><div class="lesson-body"><p><b>项目产出：</b>'+escapeText(c.output)+'。在同一个「Agent 任务助手」项目中提交可运行增量或可复核报告。</p><p><b>失败 / 变式：</b>'+escapeText(c.variant)+'。</p><p><b>验收证据：</b>产物路径或提交号 + 运行命令/评审步骤 + 输入、预期、实际结果 + 失败原因。新增至少一个正常和一个失败用例，纳入项目回归集。</p>'+([20,40,52,60].includes(d)?'<p class="gate"><b>阶段验收：</b>重跑本阶段全部回归集，报告通过数/总数、失败清单、成本和耗时；写明验收人、环境、命令和是否达标。未达标则修复重测。第40关必须附单/多Agent公平对比；第60关包含陌生变式和独立复现。页面不替你判定结果。</p>':'')+'<details><summary>原课程参考 · '+escapeText(e[2]+' '+e[3])+'</summary><p>原练习文件：<code>060/001/'+escapeText(e[4])+'</code>（原规划路径，未保证每个文件已生成）。已有代码保留。</p></details><label>本次层级<select id="stage-'+d+'">'+STAGES.map((s,i)=>'<option value="'+i+'" '+(i===Math.min(st,3)?'selected':'')+'>'+s+'</option>').join('')+'</select></label><label>本次结果<select id="result-'+d+'"><option value="pass">自报通过（需证据）</option><option value="fail">未通过 / 需要帮助</option></select></label><label>证据与复盘<textarea id="evidence-'+d+'" rows="4" placeholder="例如：提交 abc123；pytest tests/test_task.py；超时后应停止；实际重试3次后退出；日志 evidence/day-'+d+'.txt"></textarea></label><label>下次复习日期<input id="due-'+d+'" type="date" value="'+later(st>=3?7:3)+'"></label><p class="hint">看懂 → 闭卷实现 → 改条件 → 至少隔3天闭卷复现。复习失败时保留历史证据并记录待修复。</p><button onclick="saveEvidence('+d+')">保存本次证据</button><details><summary>证据历史（'+r.events.length+'）</summary>'+r.events.map(x=>'<p>'+escapeText(x.at+' · '+STAGES[x.stage]+' · '+(x.result==='pass'?'自报通过':'未通过'))+'<br><span class="evidence">'+escapeText(x.evidence)+'</span></p>').join('')+'</details></div></details>';
  }).join('')+'</section>').join('');
  document.getElementById('ckDay').textContent=next<=60?next:'—';
  document.getElementById('ckDone').textContent=Object.keys(done).length;
  document.getElementById('ckMiss').textContent=due.length;
  document.getElementById('ckStreak').textContent=Object.keys(learning.history.autoDone||{}).filter(k=>learning.history.autoDone[k]).length;
  document.getElementById('ckPbar').style.width=Object.keys(done).length/60*100+'%';
  if(storageProblem)document.getElementById('save-status').textContent=storageProblem;
}
function openLesson(day){switchTab('checkin');const el=document.getElementById('lesson-'+day);el.open=true;el.scrollIntoView({behavior:'smooth',block:'start'});}
