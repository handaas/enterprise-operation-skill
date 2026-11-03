# 平台企业经营画像

- 用户需求：分析北京京东世纪贸易有限公司的品牌、融资、相似项目和舆情情感。
- 决策用途：识别平台企业经营与竞品线索。
- 本轮结果：**本轮检查通过**
- 实际工具调用：9；失败 0
- 章节覆盖率：82%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 相似项目应作为线索而非关联企业事实
- 舆情情感的四类计数不能互相替代
- 融资与税务资质章节必须按源数据独立展示

## 本轮自动检查发现


## 使用局限

- 仅反映本次 HandaaS 数据产品返回范围与生成时点，不等同于官方证明。
- 空结果必须保留为空，不能解释为该事项客观不存在。
- 相似项目由数据产品算法给出，不构成竞争关系认定。

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 enterprise-operation-skill/scripts/compose_report.py --enterprise '北京京东世纪贸易有限公司' --page-size 10 --output enterprise-operation-skill/output/04-platform-operation/report.json --report-output enterprise-operation-skill/output/04-platform-operation/report.html
```

## 逐场景业务复核

本轮正式真实产物已逐项复核；结论限于上游公开数据、本次分页样本及报告声明口径。

- **pass** 相似项目应作为线索而非关联企业事实：similar_projects明确“共242个、展示当前页10条”，作为相似项目记录，未写成关联企业或股权关系。 本轮实际产物：technical_status=passed，successful_data_calls=8，subject.enterprise=北京京东世纪贸易有限公司，match_raw=北京京东世纪贸易有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=10,total=13; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=10,total=242; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=13; 融资次数=3; 相似项目总量=242; 上榜级别数=2; 榜单类型数=3; 融资轮次=战略投资 → 战略投资 → A轮; 当前页展示项目数=10; 正面舆情率=29.6%; 品牌发源地=北京; 税务资质数=2]；sections=[product_tags=0, company_trends=1, recent_qualifications=0, brand_profile=2, business_scale=2, enterprise_rankings=10, financing_info=3, tax_qualifications=2, similar_projects=10, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。
- **pass** 舆情情感的四类计数不能互相替代：news_sentiment分列积极1298、消极371、中立2695及未知等返回计数，未互相替代。 本轮实际产物：technical_status=passed，successful_data_calls=8，subject.enterprise=北京京东世纪贸易有限公司，match_raw=北京京东世纪贸易有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=10,total=13; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=10,total=242; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=13; 融资次数=3; 相似项目总量=242; 上榜级别数=2; 榜单类型数=3; 融资轮次=战略投资 → 战略投资 → A轮; 当前页展示项目数=10; 正面舆情率=29.6%; 品牌发源地=北京; 税务资质数=2]；sections=[product_tags=0, company_trends=1, recent_qualifications=0, brand_profile=2, business_scale=2, enterprise_rankings=10, financing_info=3, tax_qualifications=2, similar_projects=10, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。
- **pass** 融资与税务资质章节必须按源数据独立展示：financing_info=3、tax_qualifications=2，来自独立工具并分章展示。 本轮实际产物：technical_status=passed，successful_data_calls=8，subject.enterprise=北京京东世纪贸易有限公司，match_raw=北京京东世纪贸易有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=10,total=13; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=10,total=242; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=13; 融资次数=3; 相似项目总量=242; 上榜级别数=2; 榜单类型数=3; 融资轮次=战略投资 → 战略投资 → A轮; 当前页展示项目数=10; 正面舆情率=29.6%; 品牌发源地=北京; 税务资质数=2]；sections=[product_tags=0, company_trends=1, recent_qualifications=0, brand_profile=2, business_scale=2, enterprise_rankings=10, financing_info=3, tax_qualifications=2, similar_projects=10, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)