---
name: enterprise-operation-report
description: Use for generating a professional enterprise operation analysis report (企业经营分析报告) from the HandaaS enterprise-operation MCP — covering 产品标签、公司趋势标签、品牌概况、经营规模、企业排名、融资信息、税务资质、相似项目、舆情情感统计. Trigger when users ask for “企业经营分析报告”, “企业经营分析”, “企业运营分析”, “企业经营画像”, “查一家公司的经营情况”, “企业排名查询”, “融资信息查询”, “舆情情感分析”, or “企业经营洞察”. Infer the canonical enterprise name (auto-fuzzy-completing a keyword), pick the right MCP tools, and produce HTML + Markdown + JSON reports automatically. MCP 服务名称触发词：企业经营动态分析。
---

# 企业经营分析报告

## 用户契约

把“企业经营分析报告”作为面向用户的调用短语。`enterprise-operation-report` 仅为内部包名。

当本 skill 处于激活状态：

1. 不要向用户索要 product_id、MCP 工具名、API 字段、内部参数或凭证信息；只接受企业名称、统一社会信用代码、注册号或企业 ID。
2. 接受自然目标，例如“查一下某某公司的经营情况”“分析这家企业的运营状况”“给我一份某某公司的经营分析报告”“看看这家公司的融资与排名”。
3. 当用户只给关键词时，自动调用关键词模糊查询补全企业全称，再查经营分析详情。
4. 优先使用 MCP 连接（`ENTERPRISE_OPERATION_MCP_URL` Remote MCP 或本地 `handaas-mcp-server/enterprise-operation-mcp-server`）；不要让用户处理签名或凭证。
5. 同时产出 HTML（可分享交付）、Markdown（知识库 / wiki）、JSON（系统集成）三类产物。
6. 报告正文必须是专业研究报告风格：只见企业经营事实与结构化数据，绝不出现工具名、入参、product_id、内部字段或空表。
7. 绝不打印 `secret_id`、`secret_key`、签名、token 或原始签名请求。
8. 默认 dry-run；真实付费 / 凭证调用需用户明确要求且 MCP 连接配置完整。
9. 数据为空时明确说明数据范围 / 口径，不渲染空表、不臆造事实。


- MCP 返回的嵌套 JSON 字符串（如金额 `{"coinType":"人民币","value":430000000.0}`、地址 `{"city":"杭州市",...}`）必须解析为可读文本（如"4.30 亿 人民币"、"浙江省杭州市"），绝不在报告正文、表格或指标中输出原始 JSON 字符串。
- 报告所有章节标题、指标卡标签必须用中文；`core_analysis.sections` 的 `title` 字段必须中文，不可显示英文 key（如 `holders`、`investments`）。
- 指标值必须可读化：金额格式为"X 亿/万 + 币种"，地址拼接省市区，比率显示百分号。详见 `references/report-output.md` 的「数据格式约束」。

## 付费调用与分页预算（强制）

每次 MCP 业务调用和每一页明细请求都可能计费；希望得到 total / 页数计算**不是**全量拉取的授权。

1. **先计划再调用**：调用前先推导本次报告必需的结论、需要的数据维度、工具与参数方案、所需页数和最大调用预算。上游 total 未知时，第一个必要的明细页同时用于发现 total 与报告数据，绝不为此页重复付费。
2. **优先统计 / 概况接口**：当结论可由经营规模、品牌概况等聚合接口回答时优先使用它们；仅在结论、图表、代表性记录或用户明确要求全量/计数时才拉取明细。只有在用户确实要求综合报告时才跑完整流水线，绝不因为工具存在就全部调用。
3. **预算内取数**：使用 schema 允许的合理最大 pageSize 获取所需行数，达到证据/样本目标即停止，且始终在显式预算内。额外翻页必须有缺失结论的正当理由，而不是“想填满所有章节”。不得用样本分布冒充全量结论。
4. **复用相同请求**：同一任务/报告内相同的工具+参数只调用一次（含首屏规划数据）；渲染只用本地已保存 JSON 重渲，不重跑 compose/MCP。禁止自动重试、重复拉取相同统计/明细、并行拉取相同数据。补充查询前先列出具体缺口并复用已返回记录。
5. **总数与完整性口径**：`total_pages` / `remaining_pages` 只是按请求 pageSize 的估算；短而未完的页在预算内要继续翻。仅当稳定有效的 total 与实扫条数一致才算完整采集；报错、提前空页、重复页、total 变化/缺失或数量溢出均视为不完整。因显式预算或样本目标提前停止的都是部分采集，绝不宣称全量数据。
6. **预算不足要说清缺口**：若预算不足以支撑某个关键结论，在申请扩大授权前先说明证据缺口与预计的额外调用数；不得静默降级结论，也不得擅自扩大计费范围。

本 skill 分页明细：企业排名 `operation_insight_enterprise_rankings` 与相似项目 `operation_insight_similar_projects` 支持 pageIndex/pageSize（单页最多 10），CLI `--max-pages`（默认 1）为其共同页数预算；其余维度接口不支持 pageIndex，关键词模糊查询仅用于主体确认，均保持单次调用。

## MCP 服务入口

- MCP 服务当前名称：企业经营动态分析（连接仍使用原服务目录标识）。

- 上游 MCP 项目：`handaas-mcp-server/enterprise-operation-mcp-server`（“企业经营分析洞察”）。
- Remote MCP：设置环境变量 `ENTERPRISE_OPERATION_MCP_URL`（streamable-http），可选 `ENTERPRISE_OPERATION_MCP_TOKEN`。
- 本地 MCP：设置 `HANDAAS_MCP_SERVER_ROOT` 指向 `handaas-mcp-server` 仓库根目录；该 server 自己的 `.env` 提供 `INTEGRATOR_ID` / `SECRET_ID` / `SECRET_KEY`。
- 首次真实查询前，运行 `scripts/mcp_client.py ping` 与 `scripts/mcp_client.py list-tools` 验证连通。

## 按需加载 references

- 不清楚该 MCP 有哪些工具、参数、返回字段、何时调用：`references/mcp-tools-reference.md`。
- 报告结构、章节、质量底线、渲染工作流：`references/report-output.md`。

## 意图路由

| 用户意图 | 内部工作流 |
| --- | --- |
| 查一家公司的全维度经营分析报告 | 调产品标签 + 公司趋势 + 品牌 + 规模 + 排名 + 融资 + 税务 + 相似项目 + 舆情组装全量报告；`compose_report.py --enterprise ...` |
| 只要品牌概况 / 经营规模 | 仅调对应工具，按 KV 组装 |
| 只要企业排名 / 融资信息 / 税务资质 / 相似项目 | 用对应工具，按表组装 |
| 只要舆情情感统计 | `operation_insight_news_sentiment_stats`，按表组装 |
| 只要产品标签 / 公司趋势标签 | 用对应工具，按 tags 组装 |
| 只给关键词（不是全称） | 先 `operation_insight_fuzzy_search` 补全全称，再查详情 |
| 只要 JSON / 只要 HTML / 只要 Markdown | 用 `--output`（JSON）或 `--report-output`（HTML+MD），或 `render_report.py` 重渲染 |
| 连接 / 工具不存在 / 传参错误 | `mcp_client.py ping` / `list-tools` 排查；报脱敏后的缺失项 |

## Golden path for 企业经营分析报告

1. **解析企业全称**：若输入含“公司/集团/有限/院/厂/中心/事务所/合作社/合伙”等后缀视为全称；否则调 `operation_insight_fuzzy_search` 取首个命中。
2. **调经营分析工具**：产品标签、公司趋势标签、品牌概况、经营规模、企业排名、融资信息、税务资质、相似项目、舆情情感统计。入参为 `matchKeyword`（企业全称）+ `keywordType`。
3. **组装统一报告**：核心分析含产品标签（tags）、公司趋势标签（tags）、品牌概况（KV）、经营规模（KV）、企业排名（表）、融资信息（表）、税务资质（表）、相似项目（表）、舆情情感统计（表）。
4. **渲染三件套**：`compose_report.py --enterprise ... --output ... --report-output ...` 直接产出 JSON + HTML + Markdown；或 `render_report.py --input ... --output ...` 重渲染。
5. **返回路径**：返回 JSON、HTML、Markdown 文件路径，以及企业全称映射与数据口径。

- **渲染前置检查**：执行会产出含图表 HTML / PDF 的报告命令前，先验证 `node --version` 与本 skill 自带 `assets/vendor/echarts.min.js` 存在；内嵌静态 SVG 的生成需要 Node.js（推荐当前 LTS，无需 npm 包），缺失时报告生成明确报错。查看已生成的 HTML 与 Markdown 输出不需要 Node。

## AI 内容审校（正常生成已内置，离线复核可重放）

脚本只负责去重、单位与有效性分类；以下语义核对必须由当前 AI 逐项完成，并在 `content_review.corrections` 保留原值、规范值与证据位置。正常生成（`build_payload` / CLI 非 `--dry-run`）在组装阶段已自动执行同一 `apply_content_review`，证书有效性按报告 `data_source.generated_at` 判定；`--dry-run` 与正常生成共用同一条路径且只执行一次。离线入口仅用于复核已有报告，重复调用保留此前修正记录。

1. **品牌发源地**：`深圳市、广东省深圳市、广东` 是同一地点的层级重复，保留最具体名称；不同城市（如深圳与泸州）不合并。不得把“品牌发源地”扩写成总部或注册地。
2. **融资轮次**：按融资时间排序取最新一轮，不把上游返回顺序拼成“定向增发 → 定向增发 → …”的轮次轨迹；单轮记录也要标明“最新”而非“历史全部”。
3. **税务资质时效**：按“有效期止”与报告生成日期分类为有效、已过期、日期不明/上游长期有效；`9999-12-31` 不等于已核验永久有效，缺失日期不能当当前有效。过期记录保留在明细中。
4. **榜单**：缺排名的记录保留在明细表，但不进入排名图（图表会把 `-` 当 0，误读为第一名）；同榜单同年重复记录只保留完全一致的一条。
5. **舆情与样本**：情感占比是算法标签分布，分母是返回样本；不把“正面率”写成公众评价。趋势按月份排序，缺月不插值。
6. **主体确认**：输入未唯一确认时不调用主体数据、不生成经营评价；候选记录只作候选展示，不能拼成目标企业画像。

离线修订已有报告（不调用 MCP，不覆盖 `examples/`）：

```python
import json
from compose_report import apply_content_review, render_html, render_markdown

report = json.load(open("examples/01-growth-overview/report.json", encoding="utf-8"))
revised = apply_content_review(report)
json.dump(revised, open("output/content-quality-review/01-growth-overview/report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open("output/content-quality-review/01-growth-overview/report.md", "w", encoding="utf-8").write(render_markdown(revised))
```

`apply_content_review` 修正品牌发源地层级重复、重复指标卡、融资轮次口径、税务资质有效期列、排名图缺失值与榜单重复，并刷新摘要/洞察；不新增融资、榜单或资质事实。

## 脚本速查

```bash
# 校验连接配置（脱敏）
python scripts/validate_config.py --allow-placeholders

# 连通性自测
python scripts/mcp_client.py ping
python scripts/mcp_client.py list-tools

# 干跑（不调真实 API，用样例数据组装报告骨架）
python scripts/compose_report.py \
  --enterprise "示例科技有限公司" \
  --dry-run \
  --output output/enterprise_operation.json \
  --report-output output/enterprise_operation.html

# 真实查询 + 渲染（需 MCP 连接就绪）
python scripts/compose_report.py \
  --enterprise "示例科技有限公司" \
  --output output/enterprise_operation.json \
  --report-output output/enterprise_operation.html

# 明细页数预算：默认仅 1 页；先按报告结论计划所需页数，再显式授权扩大
python scripts/compose_report.py --enterprise "示例科技有限公司" --page-size 10 --max-pages 3 --report-output output/enterprise_operation.html

# 手动调单个工具
python scripts/mcp_client.py call-tool \
  --tool operation_insight_brand_profile \
  --arguments-json '{"matchKeyword": "示例科技有限公司", "keywordType": "name"}'

# 重渲染已有 JSON
python scripts/render_report.py --input output/enterprise_operation.json --output output/enterprise_operation.html
python scripts/render_report.py --input output/enterprise_operation.json --output output/enterprise_operation.md
```

## 输出字段

- `subject`：企业全称、匹配关键词、主体类型、是否自动补全。
- `abstract` / `summary`：封面摘要与详细摘要。
- `metrics`：人员规模、年营业额、上榜次数、融资次数、相似项目数。
- `caliber`：匹配对象、匹配方式、数据范围、产品、局限。
- `core_analysis`：产品标签（tags）、公司趋势标签（tags）、品牌概况（KV）、经营规模（KV）、企业排名（表）、融资信息（表）、税务资质（表）、相似项目（表）、舆情情感统计（表）。
- `representative_records`：代表性上榜记录（榜单名称 / 排名 / 发布年份）。
- `insights`：结构化解读（经营规模 / 行业地位 / 资本运作活跃度 / 近期动向）。
- `data_source`：MCP server、数据产品、生成时间、是否 dry-run。

若 API 调用失败，明确报出缺失的配置 / 缺失的工具 / MCP 错误 / 参数校验错误 / 上游网络错误，给出 dry-run 命令或配置步骤，绝不暴露密钥。
