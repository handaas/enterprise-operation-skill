# enterprise-operation-skill：已验收示例

本目录只展示 **6 个完全通过的真实正向场景**（最低要求4例）。

每例均为真实、非空、非缓存调用；技术检查、独立业务检查和离线浏览器检查全部通过。报告保持原实测字节，不把空数据、报错处理或仅生成页面计作通过。

| 场景 | 真实使用需求 | 报告 |
|---|---|---|
| [成长型科技企业经营画像](01-growth-overview/README.md) | 分析华为技术有限公司的品牌、经营规模、融资、排名和舆情结构。 | [HTML](01-growth-overview/report.html) / [MD](01-growth-overview/report.md) / [JSON](01-growth-overview/report.json) |
| [新能源汽车企业经营跟踪](02-ev-operation/README.md) | 生成比亚迪股份有限公司经营分析报告，关注排名、融资和趋势标签。 | [HTML](02-ev-operation/report.html) / [MD](02-ev-operation/report.md) / [JSON](02-ev-operation/report.json) |
| [消费品牌经营评估](03-consumer-brand/README.md) | 查看贵州茅台酒股份有限公司的品牌、经营规模和企业排名。 | [HTML](03-consumer-brand/report.html) / [MD](03-consumer-brand/report.md) / [JSON](03-consumer-brand/report.json) |
| [平台企业经营画像](04-platform-operation/README.md) | 分析北京京东世纪贸易有限公司的品牌、融资、相似项目和舆情情感。 | [HTML](04-platform-operation/report.html) / [MD](04-platform-operation/report.md) / [JSON](04-platform-operation/report.json) |
| [工程企业经营能力初筛](05-construction-operation/README.md) | 评估中国建筑第八工程局有限公司的经营规模、排名、税务资质和舆情。 | [HTML](05-construction-operation/report.html) / [MD](05-construction-operation/report.md) / [JSON](05-construction-operation/report.json) |
| [小分页交付验证](07-small-page/README.md) | 生成腾讯科技（深圳）有限公司经营报告，列表类章节仅取前 5 条用于管理层快报。 | [HTML](07-small-page/report.html) / [MD](07-small-page/report.md) / [JSON](07-small-page/report.json) |

- [逐例验收结果](results.json) · [业务复核](review.json) · [证据摘要](evidence-index.json)
- [完整测试记录](../test-records/live-replaced-20261027/README.md)仅用于审计，不属于可展示示例。
- 当前数据与结论限于原查询时点及公开样本；覆盖率不代表准确率或低风险。
