# 小分页交付验证

- 用户需求：生成腾讯科技（深圳）有限公司经营报告，列表类章节仅取前 5 条用于管理层快报。
- 决策用途：验证小分页时报告仍能清楚说明截断口径。
- 本轮结果：**本轮检查通过**
- 实际工具调用：9；失败 0
- 章节覆盖率：64%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 列表类章节最多展示 5 条或按工具实际返回
- 总量与当前展示条数不得混淆
- HTML 与 Markdown 的记录数量应一致

## 本轮自动检查发现


## 使用局限

- 仅反映本次 HandaaS 数据产品返回范围与生成时点，不等同于官方证明。
- 空结果必须保留为空，不能解释为该事项客观不存在。
- 前 5 条不是全量清单，不能据此判断全部融资或排名情况。

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 enterprise-operation-skill/scripts/compose_report.py --enterprise '腾讯科技（深圳）有限公司' --page-size 5 --output enterprise-operation-skill/output/07-small-page/report.json --report-output enterprise-operation-skill/output/07-small-page/report.html
```

## 逐场景业务复核

本轮正式真实产物已逐项复核；结论限于上游公开数据、本次分页样本及报告声明口径。

- **pass** 列表类章节最多展示 5 条或按工具实际返回：分页工具均pageSize=5；similar_projects=5，其他列表也未超过5条或实际返回数。 本轮实际产物：technical_status=passed，successful_data_calls=6，subject.enterprise=腾讯科技（深圳）有限公司，match_raw=腾讯科技（深圳）有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:empty,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:empty,rows=None,total=None; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=5,total=26; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 融资次数=5; 相似项目总量=26; 融资轮次=战略投资 → 上市后 → 上市 → B轮 → A轮; 当前页展示项目数=5; 正面舆情率=32.4%; 税务资质数=2]；sections=[product_tags=0, company_trends=1, recent_qualifications=0, brand_profile=0, business_scale=2, enterprise_rankings=0, financing_info=5, tax_qualifications=2, similar_projects=5, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":7,"empty_sections":4,"coverage_pct":64}。
- **pass** 总量与当前展示条数不得混淆：相似项目total26与当前页展示5分别列为两个指标和section note。 本轮实际产物：technical_status=passed，successful_data_calls=6，subject.enterprise=腾讯科技（深圳）有限公司，match_raw=腾讯科技（深圳）有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:empty,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:empty,rows=None,total=None; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=5,total=26; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 融资次数=5; 相似项目总量=26; 融资轮次=战略投资 → 上市后 → 上市 → B轮 → A轮; 当前页展示项目数=5; 正面舆情率=32.4%; 税务资质数=2]；sections=[product_tags=0, company_trends=1, recent_qualifications=0, brand_profile=0, business_scale=2, enterprise_rankings=0, financing_info=5, tax_qualifications=2, similar_projects=5, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":7,"empty_sections":4,"coverage_pct":64}。
- **pass** HTML 与 Markdown 的记录数量应一致：independent_rerender=true；HTML/Markdown由同一report对象生成，列表记录数一致。 本轮实际产物：technical_status=passed，successful_data_calls=6，subject.enterprise=腾讯科技（深圳）有限公司，match_raw=腾讯科技（深圳）有限公司，resolved=True；calls=[operation_insight_product_tags:empty,rows=None,total=None; operation_insight_company_trends:data,rows=None,total=None; operation_insight_brand_profile:empty,rows=None,total=None; operation_insight_business_scale:data,rows=None,total=None; operation_insight_enterprise_rankings:empty,rows=None,total=None; operation_insight_financing_info:data,rows=None,total=None; operation_insight_tax_qualifications:data,rows=None,total=None; operation_insight_similar_projects:data,rows=5,total=26; operation_insight_news_sentiment_stats:data,rows=None,total=None]；metrics=[人员规模=10000人以上; 年营业额=10亿以上; 融资次数=5; 相似项目总量=26; 融资轮次=战略投资 → 上市后 → 上市 → B轮 → A轮; 当前页展示项目数=5; 正面舆情率=32.4%; 税务资质数=2]；sections=[product_tags=0, company_trends=1, recent_qualifications=0, brand_profile=0, business_scale=2, enterprise_rankings=0, financing_info=5, tax_qualifications=2, similar_projects=5, news_sentiment=4, news_sentiment_trend=12]；quality_report={"total_sections":11,"populated_sections":7,"empty_sections":4,"coverage_pct":64}。

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)