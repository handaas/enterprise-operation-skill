# 成长型科技企业经营画像

- 用户需求：分析华为技术有限公司的品牌、经营规模、融资、排名和舆情结构。
- 决策用途：形成经营概览并识别后续深挖维度。
- 本轮结果：**本轮检查通过**
- 实际工具调用：9；失败 0
- 章节覆盖率：82%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 经营规模、品牌、融资和排名应分章呈现
- 趋势与舆情必须来自返回统计
- 分页列表不得超过 10 条
- quality_report 与章节填充一致

## 本轮自动检查发现


## 使用局限

- 仅反映本次 HandaaS 数据产品返回范围与生成时点，不等同于官方证明。
- 空结果必须保留为空，不能解释为该事项客观不存在。
- 经营规模标签不等同于审计财务数据。

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 enterprise-operation-skill/scripts/compose_report.py --enterprise '华为技术有限公司' --page-size 10 --output enterprise-operation-skill/output/01-growth-overview/report.json --report-output enterprise-operation-skill/output/01-growth-overview/report.html
```

## 逐场景业务复核

本轮正式真实产物已逐项复核；结论限于上游公开数据、本次分页样本及报告声明口径。

- **pass** 经营规模、品牌、融资和排名应分章呈现：经营规模、品牌、排名、税务、相似项目、舆情分别为独立section；融资工具empty且未伪造融资记录。摘要只列9个实际非空section，不再声称覆盖空的产品标签/融资。 本轮实际产物：technical_status=passed，successful_data_calls=7，subject.enterprise=华为技术有限公司，match_raw=华为技术有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=10,total=18; operation_insight_financing_info:empty,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=10,total=24; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=18; 相似项目总量=24; 上榜级别数=2; 榜单类型数=3; 当前页展示项目数=10; 正面舆情率=53.6%; 品牌发源地=深圳市、广东省深圳市、广东; 税务资质数=3]；sections=[product_tags=0, company_trends=1, recent_qualifications=1, brand_profile=2, business_scale=2, enterprise_rankings=10, financing_info=0, tax_qualifications=3, similar_projects=10, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。
- **pass** 趋势与舆情必须来自返回统计：company_trends来自operation_insight_company_trends；news_sentiment及12月趋势来自operation_insight_news_sentiment_stats，正面舆情率53.6%。 本轮实际产物：technical_status=passed，successful_data_calls=7，subject.enterprise=华为技术有限公司，match_raw=华为技术有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=10,total=18; operation_insight_financing_info:empty,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=10,total=24; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=18; 相似项目总量=24; 上榜级别数=2; 榜单类型数=3; 当前页展示项目数=10; 正面舆情率=53.6%; 品牌发源地=深圳市、广东省深圳市、广东; 税务资质数=3]；sections=[product_tags=0, company_trends=1, recent_qualifications=1, brand_profile=2, business_scale=2, enterprise_rankings=10, financing_info=0, tax_qualifications=3, similar_projects=10, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。
- **pass** 分页列表不得超过 10 条：enterprise_rankings与similar_projects当前页均10条，pageSize=10；相似项目total24与当前页10分列。 本轮实际产物：technical_status=passed，successful_data_calls=7，subject.enterprise=华为技术有限公司，match_raw=华为技术有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=10,total=18; operation_insight_financing_info:empty,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=10,total=24; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=18; 相似项目总量=24; 上榜级别数=2; 榜单类型数=3; 当前页展示项目数=10; 正面舆情率=53.6%; 品牌发源地=深圳市、广东省深圳市、广东; 税务资质数=3]；sections=[product_tags=0, company_trends=1, recent_qualifications=1, brand_profile=2, business_scale=2, enterprise_rankings=10, financing_info=0, tax_qualifications=3, similar_projects=10, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。
- **pass** quality_report 与章节填充一致：11节中9节填充、2节为空、coverage82%，与product_tags/financing_info为空一致。 本轮实际产物：technical_status=passed，successful_data_calls=7，subject.enterprise=华为技术有限公司，match_raw=华为技术有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=10,total=18; operation_insight_financing_info:empty,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=10,total=24; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=18; 相似项目总量=24; 上榜级别数=2; 榜单类型数=3; 当前页展示项目数=10; 正面舆情率=53.6%; 品牌发源地=深圳市、广东省深圳市、广东; 税务资质数=3]；sections=[product_tags=0, company_trends=1, recent_qualifications=1, brand_profile=2, business_scale=2, enterprise_rankings=10, financing_info=0, tax_qualifications=3, similar_projects=10, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)
[页面截图](browser.png)