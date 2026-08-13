# MCP 工具参考 — enterprise-operation-mcp-server

本 skill 连接的 MCP server：`handaas-mcp-server/enterprise-operation-mcp-server`（“企业经营分析洞察”）。

> **重要**：经营分析工具入参为 `matchKeyword`（**企业全称** / 注册号 / 统一社会信用代码 / 企业 id）+ `keywordType`；当用户只给企业关键词时，必须先调关键词模糊查询补全全称。

## 通用约定

- `keywordType` 枚举：`name`（企业名称）/ `nameId`（企业 id）/ `regNumber`（注册号）/ `socialCreditCode`（统一社会信用代码）。
- 分页：`pageIndex` 从 1 开始；企业排名 / 相似项目 `pageSize` 单页最多 10。
- 0/1 布尔字段（公司趋势）：`0` 表示“否”，`1` 表示“是”。

---

## 工具清单

### 1. `operation_insight_product_tags` — 产品标签

用途：返回企业的产品标签，用于识别产品特性与类别。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 企业名称 / 注册号 / 统一社会信用代码 / 企业 id（无全称则先调 fuzzy_search） |
| `keywordType` | string | 否 | 主体类型：name / nameId / regNumber / socialCreditCode |

返回：`tagNames`（产品标签 list of string）。

product_id：`66c33eff3c0917a9a02feb6f`。

---

### 2. `operation_insight_company_trends` — 公司趋势标签

用途：返回企业近 3/6/12 个月的动向标签，包括人员扩张、开设/注销分子公司、新增城市、新增融资、异地中标、入选榜单、法人变更、剩余租约等。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 企业名称 / 注册号 / 统一社会信用代码 / 企业 id |
| `keywordType` | string | 否 | 主体类型：name / nameId / regNumber / socialCreditCode |

返回：`isStaffExpandIn3Month/6Month/12Month`（人员扩张 0/1）、`isFoundSubsidiaryIn3Month` / `isCancelSubsidiaryIn3Month`（开设/注销子公司）、`isFoundBranchIn3Month` / `isCancelBranchIn3Month`（开设/注销分公司）、`isExpandNewCityIn3Month/6Month/12Month`（新增城市）、`isNewFinancingIn3Month/6Month/12Month`（新增融资）、`isDiffAreaWinBidIn3Month/6Month/12Month`（异地中标）、`isAuthorityListIn6Month/12Month`（入选榜单）、`isLegalRpAlterIn3Month/6Month/12Month`（法人变更）、`nYearLeaseAboutToExpire`（剩余租约年限）。

product_id：`67f3af2fac893a1d33dadebe`。

---

### 3. `operation_insight_brand_profile` — 品牌概况

用途：返回企业品牌基本信息，包括品牌发源地、创立年份、所属行业、主营产品。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 企业名称 / 注册号 / 统一社会信用代码 / 企业 id |
| `keywordType` | string | 否 | 主体类型：name / nameId / regNumber / socialCreditCode |

返回：`brandCradleList`（品牌发源地 list）、`brandCreateTime`（品牌创立年份 list）、`brandIndustryList`（品牌所属行业 list）、`brandProductList`（主营产品 list）。

product_id：`66c33eff3c0917a9a02feb80`。

---

### 4. `operation_insight_enterprise_rankings` — 企业排名

用途：返回企业上榜信息，包括榜单类型、上榜公司名、榜单名称、排名、发布年份、榜单级别、发布单位。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 企业名称 / 注册号 / 统一社会信用代码 / 企业 id |
| `keywordType` | string | 否 | 主体类型：name / nameId / regNumber / socialCreditCode |
| `pageIndex` | int | 否 | 从 1 开始（默认 1） |
| `pageSize` | int | 否 | 单页最多 10 |

返回（list + `total`）：`rankingListType`（榜单类型：世界500强/中国500强/民营500强/新经济500强/制造业500强/制造业民营500强 等）、`rankingListCompanyName`（上榜公司名）、`rankingListName`（榜单名称）、`rank`（排名）、`rankingListYear`（发布年份）、`rankingListLevel`（榜单级别）、`rankingListInstitution`（发布单位）。

product_id：`67f3be85ac893a1d33dadfbf`。

---

### 5. `operation_insight_business_scale` — 经营规模

用途：返回企业的经营规模信息，包括算法识别的企业人员规模与年营业额区间。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 企业名称 / 注册号 / 统一社会信用代码 / 企业 id |
| `keywordType` | string | 否 | 主体类型：name / nameId / regNumber / socialCreditCode |

返回：`enterpriseScale`（人员规模）、`annualTurnover`（年营业额）。

product_id：`67189489ae286373219cdd32`。

---

### 6. `operation_insight_fuzzy_search` — 关键词模糊查询企业

用途：根据企业名称 / 人名 / 品牌 / 产品 / 岗位等关键词模糊查询企业列表，用于补全企业全称。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 匹配关键词 |
| `pageIndex` | int | 否 | 分页开始位置（默认 1） |
| `pageSize` | int | 否 | 单页最多 50 |

返回：`total` + 企业列表（`name`、`nameId`、`regCapitalValue`、`foundTime`、`operStatus`、`address`、`legalRepresentative`、`enterpriseType`、`catchReason` 命中原因等）。

product_id：`675cea1f0e009a9ea37edaa1`。

---

### 7. `operation_insight_news_sentiment_stats` — 舆情情感统计

用途：统计企业舆情的情感类型分布（消极/中立/积极/未知）及其趋势变化。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 企业名称 / 注册号 / 统一社会信用代码 / 企业 id |
| `keywordType` | string | 否 | 主体类型：name / nameId / regNumber / socialCreditCode |

返回：`newsSentimentStats`（情感统计 dict：neutral/negative/positive/unknown）、`sentimentLabelList`（情感类别 list）、`newsSentimentTrend`（舆情趋势 list of {month, stats: {negative, positive}}）。

product_id：`66b338e274bf098447db7efd`。

---

### 8. `operation_insight_similar_projects` — 相似项目

用途：返回与企业相关的相似项目，包括所属企业、最新融资轮次、项目概述等。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 企业名称 / 注册号 / 统一社会信用代码 / 企业 id |
| `pageIndex` | int | 否 | 从 1 开始（默认 1） |
| `pageSize` | int | 否 | 单页最多 10（默认 10） |
| `keywordType` | string | 否 | 主体类型：name / nameId / regNumber / socialCreditCode |

返回（list + `total`）：`projectName`（项目名称）、`enterpriseName`（所属企业）、`nameId`（所属企业 id）、`financingSeries`（最新轮次）、`fpIntroduction`（项目概述）、`logo`（项目图片）。

product_id：`66b0a51fce5e524754b8502d`。

---

### 9. `operation_insight_tax_qualifications` — 税务资质

用途：返回企业税务资质信息，包括纳税人识别号、纳税人名称、资质全称、有效期起止。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 企业名称 / 注册号 / 统一社会信用代码 / 企业 id |
| `keywordType` | string | 否 | 主体类型：name / nameId / regNumber / socialCreditCode |

返回：`tpQualificationList`（list of {tpId, tpName, qualification, begin, end}：纳税人识别号 / 纳税人名称 / 资质全称 / 有效期起 / 有效期止）。

product_id：`66a0f66a5646e2b0fc8ae758`。

---

### 10. `operation_insight_financing_info` — 融资信息

用途：返回企业融资信息，包括融资次数、融资记录、融资金额、融资轮次、融资时间、投资方。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 企业名称 / 注册号 / 统一社会信用代码 / 企业 id |
| `keywordType` | string | 否 | 主体类型：name / nameId / regNumber / socialCreditCode |

返回：`fpFinancingCount`（融资次数）、`fpFinancingList`（list of {financingAmount, financingSeries, financingTime, investorList}：融资金额 / 融资轮次 / 融资时间 / 投资方）。

product_id：`66a0f56efc5601eba12cc2e3`。

---

## 推荐调用顺序（报告编排）

1. （若仅有关键词）`operation_insight_fuzzy_search` → 取 `name` 作为全称。
2. `operation_insight_business_scale` → 经营规模 KV。
3. `operation_insight_brand_profile` → 品牌概况 KV。
4. `operation_insight_product_tags` → 产品标签 tags。
5. `operation_insight_company_trends` → 公司趋势标签 tags。
6. `operation_insight_enterprise_rankings` → 企业排名表。
7. `operation_insight_financing_info` → 融资信息表。
8. `operation_insight_tax_qualifications` → 税务资质表。
9. `operation_insight_similar_projects` → 相似项目表。
10. `operation_insight_news_sentiment_stats` → 舆情情感统计表。

> 单次全量报告通常调用 9-10 个工具；除 fuzzy_search 外入参均为企业主体 `matchKeyword` + `keywordType`。
