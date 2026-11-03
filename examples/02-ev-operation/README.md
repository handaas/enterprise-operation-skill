# 新能源汽车企业经营跟踪

- 用户需求：生成比亚迪股份有限公司经营分析报告，关注排名、融资和趋势标签。
- 决策用途：跟踪行业龙头的外部经营信号。
- 本轮结果：**本轮检查通过**
- 实际工具调用：9；失败 0
- 章节覆盖率：82%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 排名需保留口径字段
- 融资记录日期和轮次不应混淆
- 趋势标签不得扩写为确定性预测

## 本轮自动检查发现


## 使用局限

- 仅反映本次 HandaaS 数据产品返回范围与生成时点，不等同于官方证明。
- 空结果必须保留为空，不能解释为该事项客观不存在。
- 不能从标签直接推导未来销量或盈利。

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 enterprise-operation-skill/scripts/compose_report.py --enterprise '比亚迪股份有限公司' --page-size 8 --output enterprise-operation-skill/output/02-ev-operation/report.json --report-output enterprise-operation-skill/output/02-ev-operation/report.html
```

## 逐场景业务复核

本轮正式真实产物已逐项复核；结论限于上游公开数据、本次分页样本及报告声明口径。

- **pass** 排名需保留口径字段：enterprise_rankings当前页8条，记录保留榜单名称、类型、发布年份、级别、发布单位及排名。 本轮实际产物：technical_status=passed，successful_data_calls=8，subject.enterprise=比亚迪股份有限公司，match_raw=比亚迪股份有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=8,total=76; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=8,total=86; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=76; 融资次数=7; 相似项目总量=86; 上榜级别数=3; 榜单类型数=5; 融资轮次=定向增发 → 定向增发 → 战略投资 → 战略投资 → IPO → IPO → A轮; 当前页展示项目数=8; 正面舆情率=30.0%; 品牌发源地=广东省深圳市、深圳市、泸州市; 税务资质数=3]；sections=[product_tags=0, company_trends=1, recent_qualifications=0, brand_profile=4, business_scale=2, enterprise_rankings=8, financing_info=7, tax_qualifications=3, similar_projects=8, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。
- **pass** 融资记录日期和轮次不应混淆：financing_info共7条；融资时间、轮次、金额为独立字段，摘要/指标保留7次轮次轨迹。 本轮实际产物：technical_status=passed，successful_data_calls=8，subject.enterprise=比亚迪股份有限公司，match_raw=比亚迪股份有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=8,total=76; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=8,total=86; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=76; 融资次数=7; 相似项目总量=86; 上榜级别数=3; 榜单类型数=5; 融资轮次=定向增发 → 定向增发 → 战略投资 → 战略投资 → IPO → IPO → A轮; 当前页展示项目数=8; 正面舆情率=30.0%; 品牌发源地=广东省深圳市、深圳市、泸州市; 税务资质数=3]；sections=[product_tags=0, company_trends=1, recent_qualifications=0, brand_profile=4, business_scale=2, enterprise_rankings=8, financing_info=7, tax_qualifications=3, similar_projects=8, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。
- **pass** 趋势标签不得扩写为确定性预测：近期动向明确仅为数据源标签，不能作为经营预测或领先信号。 本轮实际产物：technical_status=passed，successful_data_calls=8，subject.enterprise=比亚迪股份有限公司，match_raw=比亚迪股份有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:data,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:data,rows=8,total=76; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=8,total=86; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 上榜次数=76; 融资次数=7; 相似项目总量=86; 上榜级别数=3; 榜单类型数=5; 融资轮次=定向增发 → 定向增发 → 战略投资 → 战略投资 → IPO → IPO → A轮; 当前页展示项目数=8; 正面舆情率=30.0%; 品牌发源地=广东省深圳市、深圳市、泸州市; 税务资质数=3]；sections=[product_tags=0, company_trends=1, recent_qualifications=0, brand_profile=4, business_scale=2, enterprise_rankings=8, financing_info=7, tax_qualifications=3, similar_projects=8, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":9,"empty_sections":2,"coverage_pct":82}。

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)