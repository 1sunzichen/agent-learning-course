"""Read course sources, never import/execute them; build offline per-file guides."""
import ast, collections, hashlib, html, json, pathlib, re, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'file-guides'
TOPICS = {}
for line in (OUT/'tools/topics.txt').read_text().splitlines():
    key,*vals=line.split('|'); TOPICS[key]=dict(zip(['title','purpose','why','pros','cons','fit','unfit','experiment'],vals))
NUM={'001':'1-4','003':'1-5','005':'1-6','007':'1-7',**{f'{i:03}':f'1-{i}' for i in range(8,20)},**{f'{i:03}':f'2-{i-19}' for i in range(20,28)},'028':'2-10',**{f'{i:03}':f'2-{i-18}' for i in range(29,38)},**{f'{i:03}':f'3-{i-37}' for i in range(38,43)},'043':'3-8','044':'3-9'}
NAMED=dict(zip('stream_agent plan_agent reflect_agent robust_tools robust_tools_real trace_agent full_agent ctx_window token_cost prompt_eng structured_out caching prompt_sec dialogue_fsm async_tools agent_eval orchestrator pipeline collab competitive a2a shared_state fault_tolerance concurrency multi_agent_project'.split(),'1-5 1-6 1-7 1-8 1-8 1-9 1-10 1-11 1-12 1-13 1-14 1-15 1-16 1-17 1-18 1-19 2-1 2-2 2-3 2-4 2-5 2-6 2-7 2-8 2-10'.split()))
NOTES={
'029.py':['decompose 返回 None，main 随后对它调用 len，会失败；route 也返回 None。execute 的 results 未初始化，且把 append 的返回值赋回列表。L53 的工具执行和追加结果还位于 for 循环外，需要放回循环内才能逐项委派。当前还不能完成路由演示。'],
'030.py':['subscribe 和 publish 只有 result = None，main 的订阅位置也未实现。因此当前发布消息不会触发三个 agent 回调；图中不会虚构这条调用边。'],
'031.py':['Blackboard.write/read 以及 advisor_agent 的关键逻辑未实现。main 用列表中的 agent 变量间接调用四个角色，但黑板不会被正确填充。'],
'032.py':['DFS 缺少遇到灰色节点时报告环的分支；detect_loop 的重复状态和步数检查未实现。当前代码会漏报示例中的异常。'],
'033.py':['start_trace、record_span 和 call_agent 返回 None，没有生成标识或追加 span；render_tree 能遍历树，但目前没有有效记录供它展示。'],
'034.py':['cost_of 固定返回 0，allocate 只有 pass，main 没有实现预算中止判断。因此当前输出零费用，不能说明预算控制已完成。'],
'035.py':['is_critical 固定返回 False，ask_human 固定批准；main 先调用 run_step 再检查审批，而且没有拒绝后的中止分支。这里只打印模拟动作，但真正实现时必须先审批再执行。'],
'035.go':['回复来自 humanReplies 预设队列，队列用完默认批准；并非真实人工输入。main 在审批判断前已经调用 runStep，拒绝只能阻止后续步骤。runStep 目前只返回文字；接真实动作前必须调整顺序。'],
'036.py':['completion_rate、efficiency_score、overall 都固定返回 0；quality_score 只读样例字段。当前总分尚未真正实现。'],
'037.py':['has_permission 固定返回 False，execute 被拒绝时返回空串，没有写审计日志。当前所有请求都会被拒绝，但并没有完成角色白名单与审计功能。'],
'038.py':['此文件使用 create_tool_calling_agent / AgentExecutor 的接口写法。天气工具是本地示例；框架组装处仍有填空。按源码理解接口职责，实际安装版本是否支持需另行核对。'],
'038.go':['用自定义工具表和 agentLoop 演示工具分发，没有调用 LangChain，也没有真实大模型请求。表达式由本文件的递归下降解析器处理。'],
'038_real.py':['使用 ChatOpenAI 和 create_agent 连接真实模型；get_weather 先查城市坐标，匹配成功后再查天气，共两次 Open-Meteo HTTP 请求；无匹配城市时提前返回。calc 用 AST 白名单计算，不执行任意 Python 语句。框架根据模型回复动态调用注册工具，静态图中的注册边不代表每次都会调用。'],
'038_real.go':['直接用 HTTP 与模型通信，再由 agentRun 分发工具；没有 LangChain 依赖。getWeather 连接真实天气服务，calcRun 使用本地算术解析器。'],
'039.py':['使用真实 LangGraph/ChatOpenAI 接口，但图组装仍有填空。workers_node 内按列表逐项调用模型，画成多个节点不会自动变成并行。'],
'039.go':['这是自定义 graph 类型，不是 LangGraph SDK。计划与 worker 结果采用演示逻辑，按边顺序运行。'],
'040.py':['同一个脚本分客户端与 --server 两种入口，通过子进程标准输入输出通信。请求分发仍有填空；协议教学代码不能直接认定为完整 MCP 服务。'],
'040.go':['客户端启动当前程序的服务端模式，通过管道传 JSON-RPC；不是在同一函数里假装网络调用。它仍然是最小协议示例。'],
'041.go':['agent 查本地模拟知识表，judge 做关键词判断；没有真实 LLM 裁判请求。适合研究评测流程，不能据此评价大模型能力。'],
'042.py':['vec 使用字符二元组计数，不能理解深层语义。rerank_with_llm 会真实调用模型，rerank_local 是本地降级分支；仍有切块、打分等填空。'],
'042.go':['向量来自字符二元组，稀疏分数是简化公式，排序是本地计算；没有下载 embedding 模型，也没有调用真实重排模型。'],
'044.py':['generate_node 返回固定草稿，并不调用大模型。使用 SQLite checkpoint 的框架示例，人审和保存器相关位置仍有填空；与 Go 的 checkpoints.json 不共用存储格式。'],
'044.go':['自定义 Graph.load/save 用 JSON 文件保存状态，Graph.run 根据 resume 参数模拟暂停与继续。不是 LangGraph SDK，也不是 SQLite checkpoint。main 启动时删除旧 checkpoint，因此当前只演示同一进程内两次 run 的保存与恢复；跨进程恢复需调整入口。文件相对于启动工作目录。'],
'020_zhangdi.py':['把调度模式用于多维度的岗位/公司比较，使用 AsyncOpenAI 和异步 worker。维度优先级属于这个应用的输入约束，模型分析不等于已核实的现实信息。'],
'robust_tools.go':['用 context.WithTimeout 和带 context 的 HTTP 请求访问真实天气接口；缓存 map 由互斥锁保护。超时取消与 Python 线程等待超时机制不同。'],
'robust_tools_real.py':['通过 requests 访问真实天气服务，HTTP 请求带 timeout；与随机失败的本地 get_weather 模拟版用途不同。'],
}
DOCS={
'README.md':('总目录','课程文件导航','根据章节找到练习、完整示例和答案的入口。','先识别正在学的主题，再打开对应代码，避免把文件序号当课程序号。'),
'arch_compare.md':('2-9','多 Agent 架构比较','比较调度、流水线、协作与竞争模式。','任务的依赖关系不同，适合的协作方式也不同。'),
'review_phase1.md':('1-20','Phase 1 复盘','把单 Agent 的循环、工具、记忆和评测串起来。','会填局部代码后，需要能解释机制之间的关系。'),
'review_phase2.md':('2-20','Phase 2 复盘与架构表达','复盘多 Agent 分工、通信、状态和治理，并练习说明设计取舍。','面对实际问题或面试追问，需要说清为什么选这个方案。'),
'vector_db_compare.md':('3-6','向量存储比较','比较向量索引与数据库的检索、持久化和服务能力。','选择时除了召回，还要考虑更新、过滤、规模和运维。'),
'embed_compare.md':('3-7','Embedding 比较','按语言、维度和部署方式思考向量模型的选择。','检索表示影响召回，但需要在自己的数据上验证。'),
'langchain_src.md':('3-10','LangChain 源码阅读路线','沿 Runnable 与组合执行接口追踪调用链。','知道接口背后如何传输入、组织执行，才能定位框架行为。'),
'answers.md':('多节','练习答案与挑战提示','按关卡核对关键填空并回到原文件解释原因。','答案用来检查理解，不能替代自己追踪输入输出。'),
'answers-029-033.md':('2-11 至 2-15','029—033 参考答案','核对任务路由、事件总线、黑板、循环检测和追踪的实现。','这几节从分工走向通信与诊断，需要对照状态怎样变化。'),
'answers-033-044.md':('2-15 至 3-9','033—044 Python/Go 对照','按文件比较 Python 与 Go 的关键实现。','同一个机制可以用不同语言实现，但依赖和模拟程度可能不同。'),
'answers-034-037.md':('2-16 至 2-19','034—037 参考答案','核对预算、审批、评测和权限的关键逻辑。','这些机制约束执行过程，写出正常路径还不够。'),
'answers-038-042.md':('3-1 至 3-5','038—042 参考答案','核对框架、图流程、工具协议、评测和检索的示例。','需要区分框架接口与教学模拟的职责。'),
'answers-043-044.md':('3-8 至 3-9','043—044 参考答案','核对检索指标与暂停恢复的实现。','公式和恢复逻辑必须能用具体输入检验。'),
}
GO={x['name']:x for x in json.loads((OUT/'tools/go-analysis.json').read_text())}
BUILTINS=set('print len str int float bool list dict set tuple range enumerate zip isinstance type sorted sum min max abs round super getattr hasattr next iter any all callable id ord chr repr format map filter reversed object ValueError RuntimeError Exception KeyError TypeError'.split())
BORING=set('append extend items keys values get strip split join lower upper startswith endswith count sort pop add setdefault update copy encode decode'.split())
def callname(n):
    if isinstance(n,ast.Name): return n.id
    if isinstance(n,ast.Attribute): return callname(n.value)+'.'+n.attr
    if isinstance(n,ast.Subscript): return callname(n.value)+'[动态键]'
    if isinstance(n,ast.Call): return callname(n.func)+'()'
    if isinstance(n,ast.Lambda): return '匿名函数'
    return '动态对象'
def pyinfo(path):
    tree=ast.parse(path.read_text()); funcs=[]; calls=[]; refs=[]; owner='<模块入口>'; stack=[]; classnames=set()
    class Visitor(ast.NodeVisitor):
        def visit_ClassDef(self,n):
            classnames.add(n.name); stack.append(n.name)
            for a in n.body:self.visit(a)
            stack.pop()
        def visit_FunctionDef(self,n):
            nonlocal owner
            old=owner; name='.'.join(stack+[n.name]); funcs.append({'name':name,'line':n.lineno,'doc':(ast.get_docstring(n) or '').split('\n')[0]})
            for d in n.decorator_list:self.visit(d)
            owner=name;stack.append(n.name)
            for a in n.body:self.visit(a)
            stack.pop();owner=old
        visit_AsyncFunctionDef=visit_FunctionDef
        def visit_Call(self,n):
            calls.append({'from':owner,'to':callname(n.func),'line':n.lineno});self.generic_visit(n)
        def visit_Name(self,n):
            if isinstance(n.ctx,ast.Load):refs.append((owner,n.id,n.lineno))
    Visitor().visit(tree)
    blanks=sorted({n.lineno for n in ast.walk(tree) if isinstance(n,ast.Name) and re.fullmatch('_{3,}',n.id)})
    stubs=sorted({n.lineno for n in ast.walk(tree) if isinstance(n,ast.Pass) or isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and n.value.value is None})
    imports=sorted({a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names}|{n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)})
    direct={(c['from'],c['to'],c['line']) for c in calls}
    names={f['name'] for f in funcs}
    for fr,n,l in refs:
        if n in names and (fr,n,l) not in direct: calls.append({'from':fr,'to':n,'line':l,'kind':'ref'})
    return funcs,calls,imports,blanks,stubs

def graph_data(funcs,calls,go=False):
    nodes={f['name']:(f['name']+' · L'+str(f['line']),'local') for f in funcs}
    nodes['<模块入口>' if not go else '<程序入口>']=('模块顶层 / 条件入口' if not go else '程序入口','entry')
    edges=[]; names=set(nodes)
    if go and 'main' in names:edges.append(('<程序入口>','main','入口','solid'))
    for c in calls:
        fr,to,l=c['from'],c['to'],c['line']; kind=c.get('kind','call'); suffix=to.split('.')[-1]
        if go and (to.startswith('fmt.') or to in ['len','make','append','string','int','float64','rune','bool']):continue
        if not go and (to in BUILTINS or suffix in BORING):continue
        style='solid';label='L'+str(l)
        if kind=='ref':style='dashed';label+=' 引用/注册'
        if to not in names:
            match=[n for n in names if n.split('.')[-1]==suffix]
            if len(match)==1 and ('.' in to or suffix not in ['run','main']):
                to=match[0];style='dashed';label+=' 方法候选'
            else:
                if '[' in to or to in ['fn','agent','handler','scorer','worker_fn','func','dfs','walk']:
                    typ='dynamic';style='dashed'
                else:typ='external'
                nodes.setdefault(to,(to,typ))
        if fr not in nodes:nodes[fr]=(fr,'local')
        edges.append((fr,to,label,style))
    # Coalesce repeated callsites for readability without deleting callsite table.
    grouped=collections.defaultdict(list)
    for a,b,l,s in edges:grouped[(a,b,s)].append(l)
    edges=[(a,b,', '.join(dict.fromkeys(ls))[:100],s) for (a,b,s),ls in grouped.items()]
    return nodes,edges

def render_graph(name,nodes,edges):
    ids={n:'n'+str(i) for i,n in enumerate(nodes)}
    colors={'local':'#e1eee9','entry':'#243e36','external':'#f2ede4','dynamic':'#ffe4bb','read':'#e1eee9'}
    dot=['digraph G {','graph [rankdir=LR,bgcolor="transparent",pad="0.35",nodesep="0.28",ranksep="0.6"];','node [shape=box,style="rounded,filled",fontname="PingFang SC",fontsize=12,margin="0.16,0.11",color="#b8c4ba"];','edge [fontname="PingFang SC",fontsize=9,color="#8b9c92",fontcolor="#52675c"];']
    mer=['flowchart LR']
    for n,(label,typ) in nodes.items():
        dot.append(f'{ids[n]} [label={json.dumps(label,ensure_ascii=False)},fillcolor="{colors[typ]}",fontcolor="'+('#ffffff' if typ=='entry' else '#203c33')+'"];')
        mer.append(f'  {ids[n]}["{html.escape(label,quote=True)}"]')
    for a,b,l,s in edges:
        dot.append(f'{ids[a]} -> {ids[b]} [label={json.dumps(l,ensure_ascii=False)},style="{s}"];')
        mer.append(f'  {ids[a]} '+('-.->' if s=='dashed' else '-->')+f'|"{l}"| {ids[b]}')
    dot.append('}')
    (OUT/'graphs'/f'{name}.dot').write_text('\n'.join(dot))
    subprocess.run(['dot','-Tsvg',str(OUT/'graphs'/f'{name}.dot'),'-o',str(OUT/'graphs'/f'{name}.svg')],check=True,capture_output=True)
    return '\n'.join(mer)

def course(key):
    if re.fullmatch(r'[1-4]-\d+',key):
        p,n=map(int,key.split('-'));total=[0,0,20,40,52][p]+n
        return f'{key} · 全课程第 {total} 节'
    return key

def mdsection(title,body):return '\n## '+title+'\n\n'+body+'\n'
def esc(s):return html.escape(str(s),quote=True)
def bullets(items):return '\n'.join('- '+x for x in items)
def websection(title,items):return '<section><h2>'+esc(title)+'</h2>'+''.join('<p>'+esc(x)+'</p>' for x in items)+'</section>'

(OUT/'graphs').mkdir(exist_ok=True)
(OUT/'pages').mkdir(exist_ok=True)
files=sorted(f for f in ROOT.iterdir() if f.is_file() and f.suffix in ['.py','.go','.md','.json'])
records=[]
for path in files:
    name=path.name; digest=hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    funcs=[];calls=[];notes=[];imports=[];blanks=[];stubs=[];table=[]
    if path.suffix in ['.py','.go']:
        key=NUM.get(name[:3]) or NAMED.get(path.stem);t=TOPICS[key].copy()
        if key=='2-17':
            t['fit']='学习关键节点识别、模拟审批与中止流程。'
            if path.suffix=='.go':t['experiment']=t['experiment'].replace('run_step','runStep')
        if name=='044.go':t['experiment']='当前 main 会先删除旧 checkpoint。在副本中拆分首次运行与恢复入口，再检查重启后是否能够继续原草稿；原样重跑不能验证跨进程恢复。'
        if path.suffix=='.py':funcs,calls,imports,blanks,stubs=pyinfo(path)
        else:
            info=GO[name];assert not info.get('error'),info
            funcs,calls,imports=info['functions'],info['calls'],info['imports']
        notes.extend(NOTES.get(name,[]))
        if blanks:notes.append('仍有下划线占位表达式，源文件行号：'+', '.join(map(str,blanks))+'。相应路径在补完前不能正常执行。')
        if stubs:notes.append('检测到 None 赋值或 pass 的位置：'+', '.join(map(str,stubs))+'。这些也可能是正常初始化，需结合下方函数职责与源码判断；不能仅凭没有下划线认定完成。')
        if key=='1-8' and name in ['008.py','robust_tools.py']:notes.append('get_weather 用随机故障/等待模拟服务。Future.result(timeout=...) 只限制等待结果，不会杀掉线程；线程池上下文退出可能继续等待任务。')
        if key in ['1-5','1-6','1-9','1-10']:notes.append('模型请求与本地工具是不同边界：这些文件中的天气工具使用示例逻辑，不能将示例天气当成实时查询结果。')
        if 'eval' in [c['to'] for c in calls]:notes.append('源码存在 eval 调用。请先看表达式限制条件；调用图只能说明它被使用，不能证明输入已被安全限制。')
        remote=any(i.startswith(('openai','langchain','sentence_transformers','modelscope','requests','urllib','net/http')) for i in imports)
        runtime=('存在外部服务或模型依赖；执行前需按源文件配置依赖和凭据，可能联网或产生 API 费用。' if remote else '主要展示本地计算、内存状态或模拟流程；是否写文件/启动子进程请看调用表。')+' 本次只做静态解析，没有运行练习，也没有替你填写或修改原代码。'
        nodes,edges=graph_data(funcs,calls,path.suffix=='.go')
        legend='实线：源码中的直接调用；虚线：函数引用/注册、动态调用或按方法名推断的候选。L 是调用所在源码行号。箭头不表示执行顺序或每次必经；分支、循环、异步调度及框架内部调用需结合源码。灰色是外部/未解析目标，橙色是动态分发；省略 print、len 和常规容器操作以减少干扰。孤立函数可能尚未接入。'
        for f in funcs:
            outgoing=[c for c in calls if c['from']==f['name'] and c.get('kind')!='ref']
            ctext=', '.join(dict.fromkeys(c['to'] for c in outgoing)) or '未发现显式函数调用（可能直接计算、读写状态或尚未实现）'
            desc=f.get('doc','').split('\n')[0][:240] or '以源码函数体为准；下列调用展示其依赖。'
            table.append((f['name'],f['line'],desc,ctext))
        how='先从 '+('main（程序入口）' if path.suffix=='.go' else ('main 及模块入口' if any(f['name']=='main' for f in funcs) else '模块入口'))+' 出发，沿箭头找到本文件函数，再查看外部调用或动态分发。右侧调用清单保留所有静态调用点，能回到原文件逐行对照。'
        title=t['title']
    elif path.suffix=='.md':
        key,title,purpose,why=DOCS[name]
        t=dict(title=title,purpose=purpose,why=why,pros='把分散知识放在同一份文档里，便于复盘和按主题定位。',cons='文档中的代码片段、版本信息和设计意图可能与当前练习实现不同，需回到实际文件核对。',fit='查课、复盘、做代码对照和组织自己的解释。',unfit='把文字中的目标流程当作已运行通过的代码，或直接复制结论用于未经验证的项目。',experiment='任选文中一个机制，用“输入是什么、谁调用谁、失败会怎样”复述，再回到对应代码验证。')
        headings=[re.sub(r'^#+\s*','',l).strip() for l in path.read_text().splitlines() if re.match(r'^#{1,3}\s',l)]
        nodes={'start':('带着当前文件/问题阅读','entry')};edges=[];prev='start'
        for i,h in enumerate(headings[:14]):
            n='s'+str(i);nodes[n]=(h[:65],'read');edges.append((prev,n,'阅读路径','solid'));prev=n
        nodes['finish']=('回到练习验证并解释取舍','read');edges.append((prev,'finish','应用','solid'))
        legend='这是按文档标题顺序整理的阅读流程，不是函数调用图。超过 14 个标题时只展示前 14 个；完整内容请打开原文。'
        notes=['该文件是说明材料，没有可执行程序入口。']
        if name.startswith('answers'):notes.append('参考答案与当前代码状态分别维护；先检查实际函数体，尤其注意 result=None、固定返回值和审批先后顺序。')
        if name in ['embed_compare.md','vector_db_compare.md','langchain_src.md']:notes.append('文中的具体版本、性能和选型结论未在本次重新验证；本页只整理它的阅读用途。')
        runtime='阅读不会调用 API；文档中的代码片段只有在你另行执行时才会产生行为。';how='先确认所属关卡，按下面的标题路径阅读，然后打开对应代码验证。'
    else:
        key='3-9';title='暂停恢复的状态快照';data=json.loads(path.read_text())
        t=dict(title=title,purpose='保存 content 和 approved 字段，供 Go 的图流程保存/恢复草稿与审批状态。',why='程序暂停后内存会丢失，文件让下一次运行能够读取之前的状态。',pros='JSON 容易查看，教学中容易观察保存前后的字段变化。',cons='单文件写入不提供多会话隔离、并发事务或完整历史；本页不复制当前草稿值。',fit='044.go 的单机暂停恢复演示。',unfit='多个用户或进程同时读写同一个状态文件。',experiment='在副本目录运行 044.go，比较暂停前后 content 与 approved 字段，避免覆盖当前练习状态。')
        nodes={'a':('044.go · Graph.save · L48','local'),'b':('checkpoints.json\ncontent / approved','read'),'c':('044.go · Graph.load · L38','local'),'d':('Graph.run · L67 恢复流程','local'),'e':('main · L80 启动清理','entry')};edges=[('a','b','写入','solid'),('b','c','读取','solid'),('c','d','恢复状态','solid'),('e','b','删除旧文件','dashed')]
        legend='这是数据读写流程，不是本 JSON 文件里的函数调用。';notes=['当前 JSON 字段：'+', '.join(data.keys())+'。044.py 使用 SQLite 保存器，不读取这个 JSON 格式。','044.go 的 main 在 L80 删除旧 checkpoint；原样重启会清掉之前的状态。当前只演示同一进程内两次 run，跨进程恢复需调整入口。'];runtime='JSON 本身不执行代码。读写它的是 044.go，实际位置相对于启动工作目录。';how='先看谁写入，再看谁读取；检查恢复后的状态如何影响 reviewNode。'
    mermaid=render_graph(name,nodes,edges)
    content=f'# {name} · {title}\n\n课程：{course(key)}。源码快照 SHA-256 前 12 位：`{digest}`。\n\n[原文件](../{name}) · [网页阅读](pages/{name}.html) · [放大调用图](graphs/{name}.svg)\n'
    content+=mdsection('这份文件要完成什么',t['purpose'])+mdsection('为什么需要它',t['why'])
    content+=mdsection('当前文件的实际状态',bullets(notes+[runtime]))
    content+=mdsection('调用图 / 阅读与数据流程',legend+'\n\n![流程图](graphs/'+name+'.svg)\n\n<details><summary>Mermaid 图源</summary>\n\n```mermaid\n'+mermaid+'\n```\n\n</details>')
    content+=mdsection('从哪里开始看',how)
    if table:
        content+=mdsection('关键函数与依赖','| 函数 / 定义行 | 职责（源码注释供参考） | 函数体中的调用 |\n|---|---|---|\n'+'\n'.join('| `'+n+'` [L'+str(l)+']('+'../'+name+'#L'+str(l)+') | '+d.replace('|','／')+' | `'+c.replace('|','／')+'` |' for n,l,d,c in table))
    content+=mdsection('这样做的优点',t['pros'])+mdsection('代价与局限',t['cons'])+mdsection('适合什么场景',t['fit'])+mdsection('不适合直接照搬的场景',t['unfit'])+mdsection('改一个条件，检验是否理解',t['experiment']+'\n\n如果当前文件有未实现位置，先预测应该怎样变化，补齐后再验证；不要把“能启动”当作“实现正确”。')
    if calls:
        content+=mdsection('全部静态调用点','这是语法分析清单，包含图中省略的基础操作；不记录参数值。\n\n| 调用方 | 目标表达式 | 行号 | 类型 |\n|---|---|---|---|\n'+'\n'.join('| '+c['from']+' | `'+c['to']+'` | '+str(c['line'])+' | '+('函数引用/注册' if c.get('kind')=='ref' else '调用表达式')+' |' for c in calls))
    (OUT/(name+'.md')).write_text(content)
    sections=websection('01 / 要完成的事',[t['purpose']])+websection('02 / 为什么要做',[t['why']])+websection('03 / 当前代码状态',notes+[runtime])
    sections+='<section class="diagram"><div class="row"><h2>04 / '+('调用图' if funcs else '阅读 / 数据流程')+'</h2><a target="_blank" href="../graphs/'+name+'.svg">打开大图 ↗</a></div><p>'+esc(legend)+'</p><div class="graph"><img src="../graphs/'+name+'.svg" alt="'+esc(name)+' 的流程图"></div><p>'+esc(how)+'</p></section>'
    if table:
        sections+='<section><h2>05 / 函数定位</h2><div class="tablewrap"><table><thead><tr><th>函数 / 定义行</th><th>职责（源码注释）</th><th>内部调用</th></tr></thead><tbody>'+''.join('<tr><td><code>'+esc(n)+'</code><small>L'+str(l)+'</small></td><td>'+esc(d)+'</td><td><code>'+esc(c)+'</code></td></tr>' for n,l,d,c in table)+'</tbody></table></div></section>'
    sections+='<div class="twocol">'+websection('这样做的优点',[t['pros']])+websection('代价与局限',[t['cons']])+websection('适用场景',[t['fit']])+websection('不宜直接照搬',[t['unfit']])+'</div>'+websection('动手检验理解',[t['experiment'],'有未实现位置时先预测，再补齐验证。能启动不等于逻辑正确。'])
    if calls:sections+='<details><summary>查看全部 '+str(len(calls))+' 个静态调用 / 引用点</summary><div class="tablewrap"><table><tr><th>调用方</th><th>目标</th><th>源码行</th><th>类型</th></tr>'+''.join('<tr><td>'+esc(c['from'])+'</td><td><code>'+esc(c['to'])+'</code></td><td>'+str(c['line'])+'</td><td>'+('引用/注册' if c.get('kind')=='ref' else '调用')+'</td></tr>' for c in calls)+'</table></div></details>'
    page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(name+' · '+title)+'</title><link rel="stylesheet" href="../style.css"><body><main class="article"><nav><a href="../index.html">← 文件学习地图</a><a href="../../'+name+'">查看原文件</a><a href="../'+name+'.md" download>下载 Markdown</a></nav><header><p class="eyebrow">'+esc(course(key))+'</p><h1>'+esc(title)+'</h1><p class="filename">'+name+'</p><p class="muted">源码快照 '+digest+' · 静态解析 · 2026-09-10</p></header>'+sections+'<footer>图依据当前源码。阅读时优先核对“当前代码状态”，课程目标不代表已经实现。</footer></main></body></html>'
    (OUT/'pages'/(name+'.html')).write_text(page)
    records.append(dict(name=name,title=title,course=course(key),key=key,kind=path.suffix[1:],hash=digest,calls=len(calls),functions=len(funcs),notes=notes,purpose=t['purpose'],blanks=blanks))
(OUT/'catalog.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
(OUT/'catalog.js').write_text('window.FILE_GUIDES = '+json.dumps(records,ensure_ascii=False)+';\n')
(OUT/'README.md').write_text('# 文件学习地图\n\n[打开网页入口](index.html)\n\n覆盖原目录的 '+str(len(records))+' 个文件，每份对应同名 `.md`、网页和 SVG 图。程序图来自 AST 静态分析；Markdown 与 JSON 是阅读/数据流程。源码没有被修改或执行。\n\n再生成：先用 tools/inspect_go.go 更新 go-analysis.json，再运行 python3 tools/build_guides.py。需要 Python 3、Go 和 Graphviz dot。文字主题在 tools/topics.txt，逐文件说明在生成器 NOTES 中。\n\n|文件|关卡|主题|\n|---|---|---|\n'+'\n'.join(f'|[{r["name"]}]({r["name"]}.md)|{r["course"]}|{r["title"]}|' for r in records))
print(json.dumps({'files':len(records),'graphs':len(list((OUT/'graphs').glob('*.svg'))),'pages':len(list((OUT/'pages').glob('*.html')))},ensure_ascii=False))
