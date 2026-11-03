# 工程企业经营能力初筛

- 用户需求：评估中国建筑第八工程局有限公司的经营规模、排名、税务资质和舆情。
- 决策用途：为工程合作前的经营能力审阅提供资料。
- 本轮结果：**本轮检查通过**
- 实际工具调用：9；失败 0
- 章节覆盖率：73%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 规模与排名指标应避免重复计数
- 税务资质为空时不得推断为无资质
- 舆情统计应明确数据覆盖口径

## 本轮自动检查发现


## 使用局限

- 仅反映本次 HandaaS 数据产品返回范围与生成时点，不等同于官方证明。
- 空结果必须保留为空，不能解释为该事项客观不存在。
- 不能替代项目履约记录、资质原件和财务审计。

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 enterprise-operation-skill/scripts/compose_report.py --enterprise '中国建筑第八工程局有限公司' --page-size 10 --output enterprise-operation-skill/output/05-construction-operation/report.json --report-output enterprise-operation-skill/output/05-construction-operation/report.html
```

## 逐场景业务复核

本轮正式真实产物已逐项复核；结论限于上游公开数据、本次分页样本及报告声明口径。

- **pass** 规模与排名指标应避免重复计数：经营规模只列人员30000人以上/营业额10亿以上；排名工具empty，未以其他指标补排名或重复计数。 本轮实际产物：technical_status=passed，successful_data_calls=6，subject.enterprise=中国建筑第八工程局有限公司，match_raw=中国建筑第八工程局有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:empty,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:empty,rows=None,total=None; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=10,total=118; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=30000人以上; 年营业额=10亿以上; 融资次数=1; 相似项目总量=118; 融资轮次=战略投资; 当前页展示项目数=10; 正面舆情率=48.2%; 税务资质数=2]；sections=[product_tags=0, company_trends=1, recent_qualifications=1, brand_profile=0, business_scale=2, enterprise_rankings=0, financing_info=1, tax_qualifications=2, similar_projects=10, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":8,"empty_sections":3,"coverage_pct":73}。
- **pass** 税务资质为空时不得推断为无资质：tax_qualifications真实返回2条，按源数据展示；未出现“空即无资质”的推断。 本轮实际产物：technical_status=passed，successful_data_calls=6，subject.enterprise=中国建筑第八工程局有限公司，match_raw=中国建筑第八工程局有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:empty,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:empty,rows=None,total=None; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=10,total=118; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=30000人以上; 年营业额=10亿以上; 融资次数=1; 相似项目总量=118; 融资轮次=战略投资; 当前页展示项目数=10; 正面舆情率=48.2%; 税务资质数=2]；sections=[product_tags=0, company_trends=1, recent_qualifications=1, brand_profile=0, business_scale=2, enterprise_rankings=0, financing_info=1, tax_qualifications=2, similar_projects=10, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":8,"empty_sections":3,"coverage_pct":73}。
- **pass** 舆情统计应明确数据覆盖口径：舆情统计与12月趋势独立呈现，情感解读限定为算法标签和当前数据源口径。 本轮实际产物：technical_status=passed，successful_data_calls=6，subject.enterprise=中国建筑第八工程局有限公司，match_raw=中国建筑第八工程局有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:empty,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:empty,rows=None,total=None; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=10,total=118; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=30000人以上; 年营业额=10亿以上; 融资次数=1; 相似项目总量=118; 融资轮次=战略投资; 当前页展示项目数=10; 正面舆情率=48.2%; 税务资质数=2]；sections=[product_tags=0, company_trends=1, recent_qualifications=1, brand_profile=0, business_scale=2, enterprise_rankings=0, financing_info=1, tax_qualifications=2, similar_projects=10, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":8,"empty_sections":3,"coverage_pct":73}。

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)