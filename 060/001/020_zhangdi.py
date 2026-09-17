#!/usr/bin/env python3
"""
张帝秋招定级器 · 层级式 Multi-Agent 实战（基于 020.py 结构）

把「张帝秋招汇总」里的企业，用 2-1 层级式架构，按统一权重规则重新定级排序。
核心权重（orchestrator 顶层控制，贯穿每个 worker）：
  北京户口 > 北京工作地 > 专业匹配 > 薪酬

和 020.py 的结构一一对应（策略/执行分离）：
  020.py 的 orchestrator_plan（拆任务）  → 这里变成「定义 WEIGHT_RULE + 提供 COMPANIES 清单」
  020.py 的 worker（执行子任务）        → 这里变成「评估单个企业 → 输出定级 + 理由」
  020.py 的 orchestrator_summarize（汇总）→ 这里变成「按权重排序出最终总表」

区别：企业清单是已知输入，不需要 LLM 拆任务；orchestrator 的核心职责
从「拆任务」变成了「定规则 + 汇总排序」。

执行流程（python3 020_zhangdi.py）：

COMPANIES 企业清单
  └─ for 每家企业 → worker 评估（按权重规则打分定级）
  └─ orchestrator 汇总所有定级 → 按权重排序 → 最终总表

（worker 已用 asyncio.gather 并发评估 28 家企业，对应 1-18 async_tools.py；
orchestrator 汇总只调一次，保持同步。）
"""

from openai import OpenAI, AsyncOpenAI
import asyncio

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# 异步客户端：worker 并发评估用（对应 1-18 的 asyncio.gather）
aclient = AsyncOpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# 权重规则（orchestrator 顶层定义，通过 system prompt 注入每个 worker）
WEIGHT_RULE = """请按以下优先级给企业打分定级（S / A / B / C / 剔除）：
1. 北京户口（最高权重）：能解决北京落户 → 至少 A 级
2. 北京工作地：真实工作地在北京市区 → 加分
3. 专业匹配：材料/化学/矿物加工，或 SEM/FTIR/TGA/Raman 表征对口 → 加分
4. 薪酬：年薪 20W+ → 加分
与工科+体制内路径背离（如纯销售、教培）→ C 级或直接建议剔除"""

# 待评估企业清单（从「张帝秋招汇总」全量提取，每条含 地点/户口/岗位/薪酬 关键信息）
# 按汇总里的梯队分组排列
COMPANIES = [
    # ── S级（核心绝杀）──
    "国家能源集团（煤炭产业院/低碳院）：北京，落户极高（国资委单列），产业研究/规划咨询/碳资产管理，首年20-25W+七险二金",
    "北方华创：北京亦庄，落户极高（经开区专项），半导体工艺/应用支持工程师，绩效奖金+签约奖金+企业年金+宿舍",
    "深圳新凯来技术：北京/深圳，落户极高（国家战略），先进材料开发/机械设计工程师，研发高薪+专项福利",
    "中冶京诚：北京亦庄，落户极高（人社部单列），资源综合利用/冶金固废/规划管培，3年免费宿舍+九险二金",
    "中国兵器工业集团（在京科研院所）：北京，落户极高（央企编制单列），理化分析检测/材料研发/总体工艺",
    "中国航发621所（航材院）：北京海淀，落户极高（国防单列），复合材料研发/微观结构分析，硕士25-36W带事业编制",
    # ── A+级（攻坚主力）──
    "招商银行北京分行：北京，落户高（股份行指标大户），综合运营培养生/职能管理，首年20W",
    "中建八局北京公司：北京/雄安，落户高，职能管理/基础设施/绿色建造",
    "京东方BOE：北京等，落户高（视考核配给），制程技术培训生/工艺开发/材料研发",
    "中铁资源集团（海淀总部）：北京海淀，落户中高，选矿技术管理/资源规划，见习期>15W（海外外派24-34W）",
    "电科金仓（中国电科旗下）：北京，落户中高（央企单列），售前管培生",
    "中建一局三公司：北京，落户高，工程管理/职能管培",
    # ── A级（在京补充/主场狙击）──
    "拓竹科技Bambu：北京/深圳，落户中（视高精尖配额），材料工程师/结构测试，互联网大厂薪酬",
    "联想集团：北京，落户中，技术/供应链/职能",
    "深南电路：北京（产线在南方），落户中（需求证），客户经理岗，硕士12-23W",
    # ── B+级（京外顶配退路）──
    "永富物产：杭州，无北京户口，大宗商品研究员，20W+提成上不封顶",
    "热联集团：杭州，无北京户口，大宗商品期货专员/业务管培，国企高提成",
    "万华化学：山东烟台/宁波，无北京户口，工艺开发/材料研发，硕士首年20-30W+",
    # ── B级（京外保底/兜底）──
    "中国能建安徽院：合肥，无北京户口，综合能源研究/新能源工程师",
    "中国五环工程：武汉，无北京户口，工艺设计/工业环保",
    "中核四0四：甘肃嘉峪关，无北京户口，专业技术类（化工/材料/环境）",
    "紫金矿业：福建/矿区/海外，无北京户口，选矿/采矿工程师，年薪20-30W+",
    "厦门钨业：厦门/赣州，无北京户口，冶炼工艺/材料研发/选矿工程师",
    "雅砻江水电/航发沈阳606所/中化蓝天：成都/沈阳/绍兴，无北京户口",
    # ── C+级（外企高薪销售）──
    "基恩士中国：北京等24城，无北京户口，销售工程师，首年18-22W次年23-31W",
    # ── C级（外地局/异地机构）──
    "中建八局一/二公司、四局、三局、中铁一局、中电二：济南/广州/西安/无锡等，极难解决京户",
    "国泰海通湖南分公司/华宝新能/远景能源/爱科赛博/南瑞继保/中电海康/四威/芯恩/恒信：长沙/深圳/青岛/西安等，无北京户口",
    # ── D级（坚决剔除）──
    "晓禾教育/新东方/桃李未来/杭州科技职院/常州信息职大/山东医药大学/宜昌事业单位：偏离工程与体制内轨道",
]


def llm(system, user):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


async def worker(company):
    """worker（异步）：按权重规则评估单个企业，输出「定级 + 理由」"""
    resp = await aclient.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是求职定级专家。" + WEIGHT_RULE},
            {"role": "user", "content": f"请评估这家企业，输出格式：定级（S/A/B/C/剔除）+ 一句话理由。\n\n企业信息：{company}"},
        ],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


def orchestrator_summarize(results):
    """orchestrator：汇总所有 worker 的定级，按权重排序出最终总表"""
    joined = "\n".join(f"- {r}" for r in results)
    return llm(
        "你是求职总顾问。把下面的定级结果，按「北京户口 > 北京工作地 > 专业匹配 > 薪酬」"
        "的权重排成最终总表，S 级排最前，建议剔除的放最后并说明原因。",
        f"各企业定级结果：\n{joined}\n\n请输出最终排序总表：",
    )


async def main():
    print("=" * 55)
    print("  张帝秋招定级器（层级式：orchestrator + workers）")
    print("=" * 55)

    # 28 家 worker 并发评估（asyncio.gather，对应 1-18）
    results = await asyncio.gather(*[worker(c) for c in COMPANIES])

    print("\n🔧 各 worker 定级结果：")
    for i, r in enumerate(results, 1):
        print(f"  worker{i}: {r}")

    # orchestrator 汇总排序（同步，只调一次，不需要并发）
    final = orchestrator_summarize(results)
    print("\n📋 最终总表（按权重排序）：")
    print(final)


if __name__ == "__main__":
    asyncio.run(main())
