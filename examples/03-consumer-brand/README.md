# 消费品牌经营评估

- 用户需求：查看贵州茅台酒股份有限公司的品牌、经营规模和企业排名。
- 决策用途：支持渠道合作和品牌评估。
- 本轮结果：**本轮检查通过**
- 实际工具调用：9；失败 0
- 章节覆盖率：82%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 品牌和产品标签需去除空值
- 排名应带可识别的榜单或口径信息
- 摘要应反映真实返回维度而非固定套话

## 本轮自动检查发现


## 使用局限

- 仅反映本次 HandaaS 数据产品返回范围与生成时点，不等同于官方证明。
- 空结果必须保留为空，不能解释为该事项客观不存在。
- 品牌热度不等同于市场份额。

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 enterprise-operation-skill/scripts/compose_report.py --enterprise '贵州茅台酒股份有限公司' --page-size 8 --output enterprise-operation-skill/output/03-consumer-brand/report.json --report-output enterprise-operation-skill/output/03-consumer-brand/report.html
```

## 逐场景业务复核

本轮正式真实产物已逐项复核；结论限于上游公开数据、本次分页样本及报告声明口径。

- **pass** 品牌和产品标签需去除空值：product_tags为空并保持空；brand_profile仅保留实际品牌字段，无空值条目。 本轮实际产物：technical_status=passed，successful_data_calls=8，subject.enterprise=贵州茅台酒股份有限公司，match_raw=贵州茅台酒股份有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=8,total=25; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=8,total=55; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=25; 融资次数=4; 相似项目总量=55; 上榜级别数=2; 榜单类型数=2; 融资轮次=上市后 → 战略投资 → 上市后 → 上市; 当前页展示项目数=8; 正面舆情率=18.1%; 品牌发源地=仁怀市茅台镇、遵义市; 税务资质数=1]；sections=[product_tags=0, company_trends=1, recent_qualifications=0, brand_profile=4, business_scale=2, enterprise_rankings=8, financing_info=4, tax_qualifications=1, similar_projects=8, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。
- **pass** 排名应带可识别的榜单或口径信息：enterprise_rankings当前页8条、total25，保留榜单名/类型/年份/级别/发布单位。 本轮实际产物：technical_status=passed，successful_data_calls=8，subject.enterprise=贵州茅台酒股份有限公司，match_raw=贵州茅台酒股份有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=8,total=25; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=8,total=55; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=25; 融资次数=4; 相似项目总量=55; 上榜级别数=2; 榜单类型数=2; 融资轮次=上市后 → 战略投资 → 上市后 → 上市; 当前页展示项目数=8; 正面舆情率=18.1%; 品牌发源地=仁怀市茅台镇、遵义市; 税务资质数=1]；sections=[product_tags=0, company_trends=1, recent_qualifications=0, brand_profile=4, business_scale=2, enterprise_rankings=8, financing_info=4, tax_qualifications=1, similar_projects=8, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。
- **pass** 摘要应反映真实返回维度而非固定套话：摘要动态列出9个实际非空section，没有再列空的产品标签与近期新获资质，并注明未覆盖章节不推断。 本轮实际产物：technical_status=passed，successful_data_calls=8，subject.enterprise=贵州茅台酒股份有限公司，match_raw=贵州茅台酒股份有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=8,total=25; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=8,total=55; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=25; 融资次数=4; 相似项目总量=55; 上榜级别数=2; 榜单类型数=2; 融资轮次=上市后 → 战略投资 → 上市后 → 上市; 当前页展示项目数=8; 正面舆情率=18.1%; 品牌发源地=仁怀市茅台镇、遵义市; 税务资质数=1]；sections=[product_tags=0, company_trends=1, recent_qualifications=0, brand_profile=4, business_scale=2, enterprise_rankings=8, financing_info=4, tax_qualifications=1, similar_projects=8, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)