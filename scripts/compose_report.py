#!/usr/bin/env python3
"""Compose an enterprise operation insight report via the enterprise-operation MCP.

Calls the upstream enterprise-operation-mcp-server tools and assembles a
structured JSON payload rendered into a professional HTML / Markdown report.
Supports ``--dry-run`` which returns a well-formed skeleton from the bundled
sample data WITHOUT contacting the MCP.

Workflow (real run):
  1. Resolve the canonical enterprise name (fuzzy search if only a keyword).
  2. Query product tags / company trends / brand profile / business scale /
     enterprise rankings / financing info / tax qualifications / similar
     projects / news sentiment stats.
  3. Build unified report JSON with 9 domain sections.

This file never prints secrets; MCP credentials live in the server's own .env.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import pathlib
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence

from common import REPORT_BANNER, REPORT_TYPE, attach_pagination, call_tool_once, collect_detail_pages, paid_call_scope, json_dumps, load_json_file, print_json
import mcp_client
from render_report import render_html, render_markdown, html_to_pdf

SAMPLE_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets" / "report.example.json"

# Enterprise-operation MCP tools.
T_FUZZY = "operation_insight_fuzzy_search"
T_PRODUCT_TAGS = "operation_insight_product_tags"
T_COMPANY_TRENDS = "operation_insight_company_trends"
T_BRAND_PROFILE = "operation_insight_brand_profile"
T_RANKINGS = "operation_insight_enterprise_rankings"
T_BUSINESS_SCALE = "operation_insight_business_scale"
T_NEWS_SENTIMENT = "operation_insight_news_sentiment_stats"
T_SIMILAR_PROJECTS = "operation_insight_similar_projects"
T_TAX_QUALIFICATIONS = "operation_insight_tax_qualifications"
T_FINANCING_INFO = "operation_insight_financing_info"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _is_empty_response(value: Any) -> bool:
    if value is None or value == "" or value == {}:
        return True
    if isinstance(value, str):
        text = value.strip().lower()
        return any(token in text for token in ("查询数据为空", "暂无数据", "未查询到", "未检索到", "no data"))
    if isinstance(value, dict):
        for key in ("text", "message", "msg"):
            if key in value and _is_empty_response(value.get(key)):
                return True
        containers = [value.get(key) for key in ("resultList", "list", "items", "data") if key in value]
        if containers and all(item in (None, [], {}) for item in containers):
            total = value.get("total")
            return total in (None, 0, "0")
    return False


def _is_api_error(value: Any) -> bool:
    """Return True only for failed calls; platform empty-data text is not an error."""
    if value is None or _is_empty_response(value):
        return False
    if isinstance(value, str):
        text = value.lower()
        return any(token in text for token in (
            "接口调用失败", "查询失败", "状态码：4", "状态码：5",
            "upstream timeout", "tool failed", "unauthorized", "forbidden",
        ))
    if isinstance(value, dict):
        if value.get("isError") is True or value.get("is_error") is True or value.get("success") is False:
            return True
        if any(value.get(key) not in (None, "", False) for key in ("_error", "error")):
            return True
        code = value.get("code")
        if code not in (None, 0, "0", 200, "200", 10001, "10001"):
            return True
        return any(_is_api_error(value.get(key)) for key in ("text", "message", "msg") if key in value)
    return False


def _first_list(value: Any) -> List[Any]:
    if _is_api_error(value) or _is_empty_response(value):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("resultList", "list", "items"):
            if isinstance(value.get(key), list):
                return value[key]
        nested = value.get("data")
        if isinstance(nested, list):
            return nested
        if isinstance(nested, dict):
            return _first_list(nested)
    return []


def _first_record(value: Any) -> Dict[str, Any]:
    if _is_api_error(value) or _is_empty_response(value):
        return {}
    for record in _first_list(value):
        if isinstance(record, dict) and _has_evidence(record):
            return record
    if isinstance(value, dict):
        envelope = {"resultList", "list", "items", "data", "total", "pageNo", "pageSize", "text", "message", "msg", "code"}
        if not set(value).issubset(envelope) and _has_evidence(value):
            return value
    return {}


def _has_evidence(value: Any) -> bool:
    if value is None or value == "" or value == "-":
        return False
    if _is_api_error(value) or _is_empty_response(value):
        return False
    if isinstance(value, dict):
        return any(_has_evidence(item) for key, item in value.items() if key not in {"total", "pageNo", "pageSize"})
    if isinstance(value, (list, tuple, set)):
        return any(_has_evidence(item) for item in value)
    return True


def _meaningful_row(row: Mapping[str, Any]) -> bool:
    return any(_has_evidence(value) for value in row.values())


def _attach_call_status(report: Dict[str, Any], calls: Mapping[str, Any]) -> Dict[str, Any]:
    """Disclose failed and genuine-empty domains without exposing upstream details."""
    failed = [name for name, payload in calls.items() if _is_api_error(payload)]
    empty = [name for name, payload in calls.items() if not _is_api_error(payload) and _is_empty_response(payload)]
    source = report.setdefault("data_source", {})
    source["failed_products"] = failed
    source["empty_products"] = empty
    return report


def _apply_resolution_limit(report: Dict[str, Any], resolved: Mapping[str, Any]) -> Dict[str, Any]:
    subject = report.setdefault("subject", {})
    subject["resolved"] = False
    subject["requires_confirmation"] = True
    subject["resolve_reason"] = resolved.get("reason", "主体未唯一确认")
    subject["candidate_sample"] = list(resolved.get("candidate_sample") or [])
    if resolved.get("fuzzy_total") is not None:
        subject["fuzzy_total"] = resolved.get("fuzzy_total")
    message = "输入未唯一确认到特定企业；已停止主体专属数据调用，不生成该企业的经营、风险或舆情评价。请使用候选企业全称或企业标识重试。"
    report["abstract"] = message
    report["summary"] = message
    report["executive_summary"] = [message]
    report["metrics"] = []
    report["representative_records"] = []
    report["insights"] = [{"feature": "主体确认受限", "evidence": subject["resolve_reason"], "interpretation": message}]
    report.setdefault("data_source", {})["subject_resolution"] = "confirmation_required"
    return report


def _text(value: Any, limit: int = 0) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        t = json.dumps(value, ensure_ascii=False)
    else:
        t = str(value)
    t = " ".join(t.split())
    if limit and len(t) > limit:
        return t[: limit - 1].rstrip() + "…"
    return t


def _int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_call(tool: str, arguments: Dict[str, Any]) -> Any:
    try:
        result = call_tool_once(mcp_client.call_tool, tool, arguments)
        # Detect API error responses (405, etc.) and return error marker
        if _is_api_error(result):
            return {"_error": "API错误", "_raw": result}
        return result
    except Exception as exc:
        return {"_error": str(exc)}


def _safe_total(payload: Any) -> Any:
    if isinstance(payload, dict):
        if _is_api_error(payload):
            return None
        return payload.get("total")
    return None


def _collect_detail_pages(tool: str, arguments: Dict[str, Any], max_pages: int) -> Dict[str, Any]:
    """Total-driven detail collection within an explicit paid-page budget (default 1 page).

    The first paid page serves both as report data and as total discovery; it is
    never refetched. Additional pages are only requested inside the budget.
    """
    return collect_detail_pages(
        _safe_call, tool, dict(arguments), get_rows=_first_list, get_total=_safe_total,
        is_error=_is_api_error, max_pages=max_pages,
    )


# --------------------------------------------------------------------------- #
# Resolution
# --------------------------------------------------------------------------- #

def resolve_enterprise_name(raw: str) -> Dict[str, Any]:
    raw = (raw or "").strip()
    if not raw:
        return {"keyword": "", "enterprise": "", "resolved": False, "requires_confirmation": True, "reason": "关键词为空", "candidate_sample": []}
    # A full legal-name-looking input is already an explicit subject selection.
    if any(suffix in raw for suffix in ("公司", "有限", "院", "厂", "中心", "事务所", "合作社", "合伙")):
        return {"keyword": raw, "enterprise": raw, "resolved": True, "requires_confirmation": False, "reason": "用户提供企业全称", "candidate_sample": []}

    fuzzy = _safe_call(T_FUZZY, {"matchKeyword": raw, "pageSize": 10})
    records = [item for item in _first_list(fuzzy) if isinstance(item, dict)]
    total = _int(_safe_total(fuzzy))
    id_keys = ("nameId", "id", "enterpriseId", "regNumber", "socialCreditCode")
    exact = [
        item for item in records
        if raw == str(item.get("name") or "").strip()
        or any(raw == str(item.get(key) or "").strip() for key in id_keys)
    ]
    if len(exact) == 1:
        record = exact[0]
        name = str(record.get("name") or raw).strip()
        return {"keyword": raw, "enterprise": name, "resolved": True, "requires_confirmation": False, "reason": "与候选企业全称或标识精确匹配", "fuzzy_total": total, "record": record, "candidate_sample": []}
    if len(records) == 1 and total == 1:
        record = records[0]
        name = str(record.get("name") or "").strip()
        if name:
            return {"keyword": raw, "enterprise": name, "resolved": True, "requires_confirmation": False, "reason": "模糊查询唯一命中", "fuzzy_total": total, "record": record, "candidate_sample": []}

    candidates = []
    for item in records[:5]:
        candidate = {"name": str(item.get("name") or "").strip()}
        for key in id_keys:
            if item.get(key) not in (None, ""):
                candidate[key] = str(item.get(key))
        if candidate.get("name") or len(candidate) > 1:
            candidates.append(candidate)
    if candidates:
        reason = f"模糊查询命中 {total if total is not None else '多个'} 个候选，未唯一确认主体"
    else:
        reason = "模糊查询未唯一命中企业，需提供企业全称或企业标识"
    return {
        "keyword": raw, "enterprise": raw, "resolved": False, "requires_confirmation": True,
        "reason": reason, "fuzzy_total": total, "candidate_sample": candidates,
    }



def _dedupe_metrics(metrics: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Keep one card per label; merge a useful hint/delta instead of duplicating."""
    out: List[Dict[str, Any]] = []
    by_label: Dict[str, Dict[str, Any]] = {}
    for item in metrics:
        if not isinstance(item, Mapping):
            continue
        row = dict(item)
        label = str(row.get("label") or "")
        if not label:
            continue
        if label in by_label:
            existing = by_label[label]
            if row.get("hint") and row.get("hint") not in str(existing.get("hint") or ""):
                existing["hint"] = f"{existing.get('hint')}；{row.get('hint')}".strip("；")
            if row.get("delta") and not existing.get("delta"):
                existing["delta"] = row.get("delta")
            continue
        by_label[label] = row
        out.append(row)
    return out


def _derive_core_metrics(metrics: List[Dict[str, Any]], core: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Derive additional metrics from core analysis sections."""
    rankings = core.get("enterprise_rankings", []) if isinstance(core, dict) else []
    financing = core.get("financing_info", []) if isinstance(core, dict) else []
    similar = core.get("similar_projects", []) if isinstance(core, dict) else []
    sentiment = core.get("news_sentiment", []) if isinstance(core, dict) else []
    brand = core.get("brand_profile", {}) if isinstance(core, dict) else {}
    tax = core.get("tax_qualifications", []) if isinstance(core, dict) else []
    if isinstance(rankings, list) and rankings:
        try:
            levels = set(str(r.get("榜单级别", "")) for r in rankings if r.get("榜单级别"))
            if levels:
                metrics.append({"label": "上榜级别数", "value": str(len(levels)), "hint": "不同榜单级别的数量"})
            types = set(str(r.get("榜单类型", "")) for r in rankings if r.get("榜单类型"))
            if types:
                metrics.append({"label": "榜单类型数", "value": str(len(types)), "hint": "不同榜单类型的数量"})
        except Exception:
            pass
    if isinstance(financing, list) and financing:
        try:
            latest = max(
                (r for r in financing if isinstance(r, dict)),
                key=lambda r: str(r.get("融资时间") or ""),
                default=None,
            )
            if latest and latest.get("融资轮次") not in (None, "", "-"):
                metrics.append({
                    "label": "最新融资轮次",
                    "value": str(latest.get("融资轮次")),
                    "hint": f"按融资时间排序的最新记录（{latest.get('融资时间') or '日期不明'}）；不等同于全部轮次轨迹",
                })
        except (TypeError, ValueError):
            pass
    if isinstance(similar, list) and similar:
        metrics.append({"label": "本次采集项目数", "value": str(len(similar)), "hint": "本次响应实际采集的相似项目记录数（受分页预算限制，不等于上游总量）"})
    if isinstance(sentiment, list) and sentiment:
        try:
            total = sum(int(r.get("数量", 0)) for r in sentiment if str(r.get("数量", "0")).isdigit())
            positive = sum(int(r.get("数量", 0)) for r in sentiment if "积极" in str(r.get("情感类型", "")) and str(r.get("数量", "0")).isdigit())
            if total > 0:
                metrics.append({"label": "正面舆情率", "value": f"{positive/total*100:.1f}%", "hint": "正面舆情占总舆情比例"})
        except (ValueError, TypeError):
            pass
    if isinstance(brand, dict) and brand:
        origin = brand.get("品牌发源地")
        if origin and str(origin) not in ("-", "", "None"):
            metrics.append({"label": "品牌发源地", "value": "、".join(_normalize_origins(str(origin).split("、"))) or str(origin), "hint": "品牌创立地点"})
    if isinstance(tax, list) and tax:
        metrics.append({"label": "税务资质数", "value": str(len(tax)), "hint": "本次返回的税务资质记录数；有效性见明细表，过期/日期不明不视为当前有效"})
    return metrics


# --------------------------------------------------------------------------- #
# Section builders
# --------------------------------------------------------------------------- #

def build_subject(raw: str, resolved: Mapping[str, Any], keyword_type: str) -> Dict[str, Any]:
    return {
        "enterprise": resolved.get("enterprise") or raw,
        "matchKeyword": resolved.get("enterprise") or raw,
        "keywordType": keyword_type,
        "match_raw": raw,
        "resolved": bool(resolved.get("resolved")),
        "resolve_reason": resolved.get("reason", ""),
    }


def build_caliber(subject: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "match_target": subject.get("enterprise") or subject.get("match_raw"),
        "match_type": f"企业经营分析数据按企业主体匹配（keywordType={subject.get('keywordType', 'name')}）",
        "data_scope": "产品标签、公司趋势标签、品牌概况、经营规模、企业排名、融资信息、税务资质、相似项目、舆情情感统计",
        "products": ["产品标签", "公司趋势标签", "品牌概况", "经营规模", "企业排名", "融资信息", "税务资质", "相似项目", "舆情情感统计"],
        "limit": "数据来自企业经营分析公开数据源；少量字段可能存在更新延迟。",
    }


def build_metrics(scale: Any, rankings: Any, financing: Any, similar: Any) -> List[Dict[str, Any]]:
    metrics: List[Dict[str, Any]] = []
    s = scale if isinstance(scale, dict) else {}
    if s.get("enterpriseScale"):
        metrics.append({"label": "人员规模", "value": _text(s.get("enterpriseScale")), "hint": "算法识别的企业人员规模"})
    if s.get("annualTurnover"):
        metrics.append({"label": "年营业额", "value": _text(s.get("annualTurnover")), "hint": "算法识别的企业年营业额区间"})
    rankings_total = _int(_safe_total(rankings)) if isinstance(rankings, dict) else None
    if rankings_total is not None:
        metrics.append({"label": "上榜次数", "value": _text(rankings_total), "hint": "企业上榜榜单总数"})
    f = financing if isinstance(financing, dict) else {}
    if f.get("fpFinancingCount") is not None:
        metrics.append({"label": "融资次数", "value": _text(f.get("fpFinancingCount")), "hint": "历史融资次数"})
    similar_total = _int(_safe_total(similar)) if isinstance(similar, dict) else None
    if similar_total is not None:
        metrics.append({"label": "相似项目总量", "value": _text(similar_total), "hint": "上游响应返回的相似项目 total"})
    return [m for m in metrics if m.get("value") not in ("", None, "-")]


def _tags_str(payload: Any, key: str) -> str:
    p = payload if isinstance(payload, dict) else {}
    val = p.get(key)
    if isinstance(val, list):
        return "、".join(_text(t) for t in val if t)
    return _text(val)


def _normalize_origins(values: Sequence[Any]) -> List[str]:
    """Drop hierarchical duplicate region labels without merging distinct places.

    ``["深圳市", "广东省深圳市", "广东"]`` -> ``["广东省深圳市"]`` because both
    shorter labels are contained in the most specific one. ``["广东省深圳市",
    "泸州市"]`` stays as two distinct origins.
    """
    labels = [re.sub(r"\s+", "", _text(v)) for v in values if _text(v)]
    unique: List[str] = []
    for label in labels:
        if label not in unique:
            unique.append(label)
    keep: List[str] = []
    for label in sorted(unique, key=len, reverse=True):
        if any(label != other and label in other for other in keep):
            continue
        keep.append(label)
    # preserve the upstream order for readability
    return [label for label in unique if label in keep]


def _brand_kv(brand: Any) -> Dict[str, Any]:
    b = brand if isinstance(brand, dict) else {}
    kv: Dict[str, Any] = {}
    if isinstance(b.get("brandCradleList"), list) and b["brandCradleList"]:
        kv["品牌发源地"] = "、".join(_normalize_origins(b["brandCradleList"]))
    # brandCreateTime may be a list of strings OR a dict {min:"2003年", max:"..."}
    bct = b.get("brandCreateTime")
    bct_str = ""
    if isinstance(bct, list) and bct:
        bct_str = "、".join(_text(t) for t in bct if t)
    elif isinstance(bct, dict):
        # upstream returns {"min":"2003年"} (and optionally "max")
        parts = []
        if bct.get("min"):
            parts.append(_text(bct.get("min")))
        if bct.get("max"):
            parts.append(_text(bct.get("max")))
        bct_str = "、".join(parts)
    elif bct:
        bct_str = _text(bct)
    if bct_str:
        kv["品牌创立年份"] = bct_str
    if isinstance(b.get("brandIndustryList"), list) and b["brandIndustryList"]:
        kv["品牌所属行业"] = "、".join(_text(t) for t in b["brandIndustryList"] if t)
    if isinstance(b.get("brandProductList"), list) and b["brandProductList"]:
        kv["主营产品"] = "、".join(_text(t) for t in b["brandProductList"] if t)
    return kv


def _scale_kv(scale: Any) -> Dict[str, Any]:
    s = scale if isinstance(scale, dict) else {}
    kv: Dict[str, Any] = {}
    if s.get("enterpriseScale"):
        kv["人员规模"] = _text(s.get("enterpriseScale"))
    if s.get("annualTurnover"):
        kv["年营业额"] = _text(s.get("annualTurnover"))
    return kv


def _ranking_rows(rankings: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()
    for item in _first_list(rankings):
        if not isinstance(item, dict):
            continue
        row = {
            "榜单名称": _text(item.get("rankingListName")) or "-",
            "榜单类型": _text(item.get("rankingListType")) or "-",
            "上榜公司名": _text(item.get("rankingListCompanyName")) or "-",
            "排名": _text(item.get("rank") or "-"),
            "发布年份": _text(item.get("rankingListYear") or "-"),
            "榜单级别": _text(item.get("rankingListLevel")) or "-",
            "发布单位": _text(item.get("rankingListInstitution")) or "-",
        }
        key = tuple(row.values())
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _financing_rows(financing: Any) -> List[Dict[str, Any]]:
    out = []
    f = financing if isinstance(financing, dict) else {}
    for item in _first_list(f.get("fpFinancingList") if isinstance(f.get("fpFinancingList"), list) else f):
        if not isinstance(item, dict):
            continue
        investors = item.get("investorList")
        investors_str = "、".join(_text(t) for t in investors if t) if isinstance(investors, list) else _text(investors)
        out.append({
            "融资时间": _text(item.get("financingTime")) or "-",
            "融资轮次": _text(item.get("financingSeries")) or "-",
            "融资金额": _text(item.get("financingAmount")) or "-",
            "投资方": investors_str or "-",
        })
    return out


def _date_validity(end: Any, as_of: Optional[dt.date] = None) -> str:
    text = _text(end)
    if not text or text == "-":
        return "日期不明"
    if text.startswith("9999"):
        return "长期有效（上游）"
    try:
        end_date = dt.date.fromisoformat(text[:10])
    except ValueError:
        return "日期格式不明"
    today = as_of or dt.date.today()
    return "有效" if end_date >= today else f"已过期（{text[:10]}）"


def _tax_rows(tax: Any) -> List[Dict[str, Any]]:
    out = []
    t = tax if isinstance(tax, dict) else {}
    for item in _first_list(t.get("tpQualificationList") if isinstance(t.get("tpQualificationList"), list) else t):
        if not isinstance(item, dict):
            continue
        end = _text(item.get("end"))
        out.append({
            "纳税人识别号": _text(item.get("tpId")) or "-",
            "纳税人名称": _text(item.get("tpName")) or "-",
            "资质全称": _text(item.get("qualification")) or "-",
            "有效期起": _text(item.get("begin")) or "-",
            "有效期止": end or "-",
            "有效性": _date_validity(end),
        })
    return out


def _similar_rows(similar: Any) -> List[Dict[str, Any]]:
    out = []
    for item in _first_list(similar):
        if not isinstance(item, dict):
            continue
        out.append({
            "项目名称": _text(item.get("projectName")) or "-",
            "所属企业": _text(item.get("enterpriseName")) or "-",
            "最新轮次": _text(item.get("financingSeries")) or "-",
            "项目概述": _text(item.get("fpIntroduction"), limit=120) or "-",
        })
    return out


def _sentiment_rows(sentiment: Any) -> List[Dict[str, Any]]:
    """Produce sentiment distribution rows (情感类型/数量) for charting — excludes trend."""
    out = []
    s = sentiment if isinstance(sentiment, dict) else {}
    stats = s.get("newsSentimentStats")
    label_map = {"positive": "积极", "negative": "消极", "neutral": "中立", "unknown": "未知"}
    if isinstance(stats, dict):
        for key, label in label_map.items():
            val = stats.get(key)
            if val is not None and _int(val) != 0:
                out.append({"情感类型": label, "数量": _text(val)})
    return out


def _sentiment_trend_rows(sentiment: Any) -> List[Dict[str, Any]]:
    """Flatten newsSentimentTrend [{month, stats:{negative,positive}}] into
    monthly rows for the multi_line chart: {月份, 积极, 消极}."""
    out: List[Dict[str, Any]] = []
    s = sentiment if isinstance(sentiment, dict) else {}
    trend = s.get("newsSentimentTrend")
    if not isinstance(trend, list):
        return out
    for item in trend:
        if not isinstance(item, dict):
            continue
        month = item.get("month")
        raw_stats = item.get("stats")
        stats: Mapping[str, Any] = raw_stats if isinstance(raw_stats, dict) else {}
        out.append({
            "月份": _text(month),
            "积极": _int(stats.get("positive")) or 0,
            "消极": _int(stats.get("negative")) or 0,
        })
    return sorted(out, key=lambda row: str(row.get("月份") or ""))


def _recent_qualifications_tags(company_trends: Any) -> str:
    """Combine qualificationIn6MonthList / qualificationIn12MonthList into a
    deduped '近期新获资质' tag string."""
    p = company_trends if isinstance(company_trends, dict) else {}
    seen = []
    for key in ("qualificationIn6MonthList", "qualificationIn12MonthList"):
        val = p.get(key)
        if isinstance(val, list):
            for q in val:
                t = _text(q)
                if t and t not in seen:
                    seen.append(t)
    return "、".join(seen)


def build_core_analysis(
    product_tags: Any,
    company_trends: Any,
    brand: Any,
    scale: Any,
    rankings: Any,
    financing: Any,
    tax: Any,
    similar: Any,
    sentiment: Any,
) -> Dict[str, Any]:
    product_tags_str = _tags_str(product_tags, "tagNames")
    company_trends_str = _build_company_trends_tags(company_trends)
    recent_qualifications_str = _recent_qualifications_tags(company_trends)
    brand_kv = _brand_kv(brand)
    scale_kv = _scale_kv(scale)
    ranking_rows = _ranking_rows(rankings)
    ranking_chart_rows = [
        row for row in ranking_rows
        if str(row.get("排名", "")).replace(",", "").strip().isdigit()
    ]
    financing_rows = _financing_rows(financing)
    tax_rows = _tax_rows(tax)
    similar_rows = _similar_rows(similar)
    sentiment_rows = _sentiment_rows(sentiment)
    sentiment_trend_rows = _sentiment_trend_rows(sentiment)

    rankings_total = _safe_total(rankings) if isinstance(rankings, dict) else None
    similar_total = _safe_total(similar) if isinstance(similar, dict) else None

    sections = [
        {"key": "product_tags", "title": "产品标签", "kind": "tags"},
        {"key": "company_trends", "title": "公司趋势标签", "kind": "tags"},
        {"key": "recent_qualifications", "title": "近期新获资质", "kind": "tags",
         "note": "近 6/12 个月新获得的资质（来源：公司趋势标签）"},
        {"key": "brand_profile", "title": "品牌概况", "kind": "kv"},
        {"key": "business_scale", "title": "经营规模", "kind": "kv"},
        {"key": "enterprise_rankings_chart", "title": "企业排名（有明确排名）", "kind": "bar",
         "note": f"仅展示有明确排名的记录；共 {rankings_total if rankings_total is not None else '未返回总数'} 次上榜，本次采集 {len(ranking_rows)} 条（排名数值越小越靠前）",
         "chart": {"name": "榜单名称", "value": "排名", "orient": "h"},
         "columns": [("榜单名称", "榜单名称"), ("排名", "排名"), ("发布年份", "发布年份")]},
        {"key": "enterprise_rankings", "title": "企业排名明细", "kind": "table",
         "note": f"共 {rankings_total if rankings_total is not None else '未返回总数'} 次上榜，本次采集 {len(ranking_rows)} 条；未返回排名的记录保留在表中，不进入排名图",
         "columns": [("榜单名称", "榜单名称"), ("榜单类型", "榜单类型"), ("上榜公司名", "上榜公司名"), ("排名", "排名"), ("发布年份", "发布年份"), ("榜单级别", "榜单级别"), ("发布单位", "发布单位")]},
        {"key": "financing_info", "title": "融资信息", "kind": "table", "note": "按上游返回顺序展示历史融资记录；未按时间重排",
         "columns": [("融资时间", "融资时间"), ("融资轮次", "融资轮次"), ("融资金额", "融资金额"), ("投资方", "投资方")]},
        {"key": "tax_qualifications", "title": "税务资质", "kind": "table",
         "note": "有效性按“有效期止”与报告生成日期比较；9999-12-31 记为上游长期有效，缺失日期记为日期不明",
         "columns": [("纳税人识别号", "纳税人识别号"), ("纳税人名称", "纳税人名称"), ("资质全称", "资质全称"), ("有效期起", "有效期起"), ("有效期止", "有效期止"), ("有效性", "有效性")]},
        {"key": "similar_projects", "title": "相似项目", "kind": "table",
         "note": f"共 {similar_total if similar_total is not None else '未返回总数'} 个相似项目，本次采集 {len(similar_rows)} 条",
         "columns": [("项目名称", "项目名称"), ("所属企业", "所属企业"), ("最新轮次", "最新轮次"), ("项目概述", "项目概述")]},
        {"key": "news_sentiment", "title": "舆情情感统计", "kind": "pie", "note": "情感类型数量占比",
         "chart": {"name": "情感类型", "value": "数量", "donut": True},
         "columns": [("情感类型", "情感类型"), ("数量", "数量")]},
        {"key": "news_sentiment_trend", "title": "舆情月度趋势", "kind": "multi_line",
         "note": "近 12 个月舆情积极/消极数量趋势（来源：newsSentimentTrend）",
         "chart": {"x": "月份", "series": ["积极", "消极"]},
         "columns": [("月份", "月份"), ("积极", "积极"), ("消极", "消极")]},
    ]
    return {
        "sections": sections,
        "product_tags": product_tags_str,
        "company_trends": company_trends_str,
        "recent_qualifications": recent_qualifications_str,
        "brand_profile": brand_kv,
        "business_scale": scale_kv,
        "enterprise_rankings": ranking_rows,
        "enterprise_rankings_chart": ranking_chart_rows,
        "financing_info": financing_rows,
        "tax_qualifications": tax_rows,
        "similar_projects": similar_rows,
        "news_sentiment": sentiment_rows,
        "news_sentiment_trend": sentiment_trend_rows,
    }


def _build_company_trends_tags(payload: Any) -> str:
    """Translate 0/1 trend flags into Chinese tags."""
    p = payload if isinstance(payload, dict) else {}
    mapping = [
        ("isStaffExpandIn3Month", "近3个月人员扩张"),
        ("isStaffExpandIn6Month", "近6个月人员扩张"),
        ("isStaffExpandIn12Month", "近12个月人员扩张"),
        ("isFoundSubsidiaryIn3Month", "近3个月开设子公司"),
        ("isCancelSubsidiaryIn3Month", "近3个月注销子公司"),
        ("isFoundBranchIn3Month", "近3个月开设分公司"),
        ("isCancelBranchIn3Month", "近3个月注销分公司"),
        ("isExpandNewCityIn3Month", "近3个月新增城市"),
        ("isExpandNewCityIn6Month", "近6个月新增城市"),
        ("isExpandNewCityIn12Month", "近12个月新增城市"),
        ("isNewFinancingIn3Month", "近3个月新增融资"),
        ("isNewFinancingIn6Month", "近6个月新增融资"),
        ("isNewFinancingIn12Month", "近12个月新增融资"),
        ("isDiffAreaWinBidIn3Month", "近3个月异地中标"),
        ("isDiffAreaWinBidIn6Month", "近6个月异地中标"),
        ("isDiffAreaWinBidIn12Month", "近12个月异地中标"),
        ("isAuthorityListIn6Month", "近6个月入选榜单"),
        ("isAuthorityListIn12Month", "近12个月入选榜单"),
        ("isLegalRpAlterIn3Month", "近3个月法人变更"),
        ("isLegalRpAlterIn6Month", "近6个月法人变更"),
        ("isLegalRpAlterIn12Month", "近12个月法人变更"),
    ]
    tags = []
    for key, label in mapping:
        if p.get(key) in (1, "1", True):
            tags.append(label)
    if p.get("nYearLeaseAboutToExpire") is not None:
        tags.append(f"剩余租约 {p.get('nYearLeaseAboutToExpire')} 年")
    return "、".join(tags)


def build_records(core: Mapping[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for item in core.get("enterprise_rankings") or []:
        out.append({
            "榜单名称": item.get("榜单名称") or "-",
            "排名": item.get("排名") or "-",
            "发布年份": item.get("发布年份") or "-",
        })
    return out[:20]


def _sentiment_concentration(rows: List[Mapping[str, Any]]) -> Dict[str, Any]:
    """Compute share of each sentiment from {情感类型,数量} distribution rows."""
    items = []
    for r in rows:
        try:
            items.append((r.get("情感类型", "-"), float(str(r.get("数量", 0)).replace(",", ""))))
        except (TypeError, ValueError):
            items.append((r.get("情感类型", "-"), 0.0))
    total = sum(v for _, v in items)
    if not total:
        return {}
    by_label = {lbl: v / total * 100 for lbl, v in items}
    items.sort(key=lambda x: x[1], reverse=True)
    return {"top": items[0][0], "top_share": items[0][1] / total * 100, "by_label": by_label, "total": total}


def build_insights(subject: Mapping[str, Any], core: Mapping[str, Any], metrics: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    insights: List[Dict[str, Any]] = []
    metric_map = {m["label"]: str(m["value"]) for m in metrics}
    scale = metric_map.get("人员规模")
    turnover = metric_map.get("年营业额")
    rankings_total = metric_map.get("上榜次数")
    financing_count = metric_map.get("融资次数")
    company_trends_str = core.get("company_trends") or ""

    if scale or turnover:
        evid = "、".join(p for p in (f"人员规模 {scale}" if scale else "", f"年营业额 {turnover}" if turnover else "") if p)
        insights.append({
            "feature": "经营规模",
            "evidence": evid + "。",
            "interpretation": "人员规模与营业额仅描述数据源记录的经营体量，不能单独推出资源调配能力或抗风险能力。",
        })
    # ranking trend: best rank + level coverage
    ranking_rows = core.get("enterprise_rankings") or []
    if ranking_rows:
        parsed = []
        for r in ranking_rows:
            try:
                parsed.append((r.get("榜单名称", "-"), int(float(str(r.get("排名")).replace(",", ""))), r.get("榜单级别", "-"), r.get("发布年份", "-")))
            except (TypeError, ValueError):
                continue
        if parsed:
            best = min(parsed, key=lambda x: x[1])
            levels = sorted(set(p[2] for p in parsed if p[2] not in ("-", "")))
            insights.append({
                "feature": "行业地位",
                "evidence": f"累计上榜 {rankings_total or len(parsed)} 次，最高排名为“{best[0]}”第 {best[1]} 名（{best[2]}，{best[3]}），覆盖级别：{'、'.join(levels) or '-'}。",
                "interpretation": "榜单记录仅描述该榜单的入选与排名结果；需核验榜单方法、年份和样本范围，不能直接认定行业标杆。",
            })
    # financing latest stage (rows are typically ordered earliest→latest; pick the latest by time)
    financing_rows = core.get("financing_info") or []
    if financing_rows:
        def _ftime(r: Mapping[str, Any]) -> str:
            return str(r.get("融资时间") or "")
        latest = max(financing_rows, key=_ftime) if any(_ftime(r) for r in financing_rows) else financing_rows[-1]
        insights.append({
            "feature": "资本运作活跃度",
            "evidence": f"历史融资 {financing_count or len(financing_rows)} 次，最新一轮为“{latest.get('融资轮次', '-')}”（{latest.get('融资时间', '-')}，金额 {latest.get('融资金额', '-')}）。",
            "interpretation": "融资记录描述历史资本事件；融资次数和轮次不等同于外部认可度，也不能单独证明规模化扩张或上市准备。",
        })
    elif financing_count:
        insights.append({
            "feature": "资本运作活跃度",
            "evidence": f"历史融资 {financing_count} 次。",
            "interpretation": "融资次数仅描述历史资本事件频次，需结合金额、投资方及资金用途进一步判断。",
        })
    # sentiment share
    sentiment_rows = core.get("news_sentiment") or []
    if sentiment_rows:
        conc = _sentiment_concentration(sentiment_rows)
        if conc:
            pos_share = conc["by_label"].get("积极")
            neg_share = conc["by_label"].get("消极")
            share_clause = ""
            if pos_share is not None and neg_share is not None:
                ratio = (pos_share / neg_share) if neg_share > 0 else None
                share_clause = f"（积极占比 {pos_share:.0f}%，消极占比 {neg_share:.0f}%，正负比 {ratio:.1f}:1）" if ratio else f"（积极占比 {pos_share:.0f}%）"
            insights.append({
                "feature": "舆情情感分布",
                "evidence": f"“{conc['top']}”占比最高约 {conc['top_share']:.0f}%{share_clause}。",
                "interpretation": "情感占比仅描述算法标签分布，不能直接等同于企业实力、公众形象或品牌口碑。",
            })
    if company_trends_str:
        # take first 3 tags as evidence
        tags_preview = "、".join(company_trends_str.split("、")[:3])
        insights.append({
            "feature": "近期动向",
            "evidence": f"近期动向标签：{tags_preview} 等。",
            "interpretation": "动向标签仅描述数据源记录的近期变化，不能单独作为经营节奏的领先信号。",
        })
    # tax qualification validity: expired and unknown dates are not current
    tax_rows = core.get("tax_qualifications") or []
    if tax_rows:
        statuses: Dict[str, int] = {}
        for row in tax_rows:
            label = str(row.get("有效性") or "日期不明")
            bucket = "有效" if label.startswith("有效") else ("已过期" if label.startswith("已过期") else ("长期有效" if label.startswith("长期") else "日期不明"))
            statuses[bucket] = statuses.get(bucket, 0) + 1
        detail = "、".join(f"{k} {v} 条" for k, v in statuses.items())
        insights.append({
            "feature": "税务资质时效",
            "evidence": f"本次返回税务资质记录 {len(tax_rows)} 条：{detail}。",
            "interpretation": "有效期止缺失或格式不明时不能视为当前有效；已过期记录仍可作为历史资质保留，但不代表当前适用。",
        })
    # recent new qualifications
    recent_qual_str = core.get("recent_qualifications") or ""
    if recent_qual_str:
        insights.append({
            "feature": "资质增厚",
            "evidence": f"近期新获资质：{recent_qual_str}。",
            "interpretation": "新增资质仅证明相应认定记录发生变化；其适用范围需核验，不能直接推断技术实力提升。",
        })
    if not insights:
        insights.append({
            "feature": "数据完整性",
            "evidence": "部分维度未返回有效数据。",
            "interpretation": "建议核对匹配关键词是否为企业全称，或检查 MCP 连接与上游数据产品覆盖范围。",
        })
    return insights


def _populated_section_titles(core: Mapping[str, Any]) -> List[str]:
    titles: List[str] = []
    sections = core.get("sections")
    if not isinstance(sections, list):
        return titles
    for section in sections:
        if not isinstance(section, dict):
            continue
        key = section.get("key")
        title = section.get("title")
        if isinstance(key, str) and isinstance(title, str) and _has_evidence(core.get(key)):
            titles.append(title)
    return titles


def build_abstract(subject: Mapping[str, Any], core: Mapping[str, Any], metrics: Sequence[Mapping[str, Any]]) -> str:
    name = subject.get("enterprise") or subject.get("match_raw") or "目标企业"
    section_titles = _populated_section_titles(core)
    if section_titles:
        parts = [f"本报告以“{name}”为分析对象，基于企业经营分析大数据。本次有效数据覆盖：{'、'.join(section_titles)}。"]
    else:
        parts = [f"本报告以“{name}”为分析对象；本次未返回有效经营分析章节，不生成经营判断。"]
    if metrics:
        kv = "、".join(f"{m['label']} {m['value']}" for m in metrics[:5])
        parts.append(f"关键指标包括：{kv}。")
    parts.append("报告仅对已返回字段作结构化描述；未覆盖章节不作推断，相关记录仍需结合来源口径核验。")
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Dry-run sample
# --------------------------------------------------------------------------- #

def build_dry_run_payload(raw: str, keyword_type: str) -> Dict[str, Any]:
    try:
        sample = load_json_file(SAMPLE_PATH)
    except Exception:
        sample = {}
    sample = sample if isinstance(sample, dict) else {}
    subject = sample.get("subject") or {"enterprise": raw, "matchKeyword": raw, "keywordType": keyword_type, "match_raw": raw}
    subject = {**subject, "match_raw": raw, "keywordType": keyword_type}
    core = sample.get("core_analysis") or {}
    metrics = sample.get("metrics") or []
    return _assemble(subject, core, metrics, dry_run=True)


def _tax_validity_from_row(row: Mapping[str, Any], as_of: Optional[dt.date] = None) -> str:
    return _date_validity(row.get("有效期止"), as_of)


def _refresh_quality_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """Refresh section-fill metrics after offline review changed sections.

    ``0`` is a populated value; None/""/[]/{} and documented empty sentinels are
    empty. coverage_pct is section fill only, never an accuracy claim.
    """
    core = report.get("core_analysis") or {}
    sections = core.get("sections")
    if isinstance(sections, list) and sections:
        total = len(sections)
        populated = sum(1 for s in sections if isinstance(s, dict) and _has_evidence(core.get(s.get("key"))))
    else:
        keys = [k for k in core if k != "sections"]
        total = max(1, len(keys))
        populated = sum(1 for k in keys if _has_evidence(core.get(k)))
    source = report.setdefault("data_source", {})
    source["quality_report"] = {
        "total_sections": total,
        "populated_sections": populated,
        "empty_sections": total - populated,
        "coverage_pct": round(populated / max(1, total) * 100),
        "metric": "section_fill_rate",
        "note": "章节填充率，仅表示有返回内容的 section 占比，不是内容准确率",
    }
    return report


def _merge_review_records(previous: Any, current: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Keep earlier review records when the same report is processed again."""
    merged: List[Dict[str, Any]] = []
    seen = set()
    for item in list(previous or []) + list(current or []):
        if not isinstance(item, Mapping):
            continue
        row = dict(item)
        key = json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)
        if key in seen:
            continue
        seen.add(key)
        merged.append(row)
    return merged


def apply_content_review(report: Mapping[str, Any], source_evidence: Optional[Any] = None) -> Dict[str, Any]:
    """Rebuild operation narrative from fields already present in a report.

    Pure/offline: no MCP call and no new facts. Repairs deterministic issues that
    are visible in the payload and records each change under
    ``content_review.corrections``:

    * hierarchical duplicate brand origins ("深圳市/广东省深圳市/广东");
    * duplicated "近一年获证" cards and a misleading round-by-round financing trail;
    * tax qualification validity (expired / date-unknown are not current);
    * ranking chart rows that contain "-" (rendered as 0 = best) and duplicate rows.
    """
    out = copy.deepcopy(dict(report))
    corrections: List[Dict[str, Any]] = []
    subject = out.get("subject") or {}
    core = out.get("core_analysis") or {}
    source = out.get("data_source") or {}
    previous_review = source.get("content_review") or {}
    generated_at = source.get("generated_at")
    try:
        as_of = dt.datetime.fromisoformat(str(generated_at)).date() if generated_at else dt.date.today()
    except (ValueError, TypeError):
        as_of = dt.date.today()

    # Brand origins: dedupe hierarchy but keep distinct cities.
    brand = core.get("brand_profile") or {}
    if isinstance(brand, dict) and brand.get("品牌发源地"):
        before = str(brand.get("品牌发源地"))
        after = "、".join(_normalize_origins(before.split("、"))) or before
        if after != before:
            brand["品牌发源地"] = after
            corrections.append({
                "field": "core_analysis.brand_profile.品牌发源地",
                "before": before,
                "after": after,
                "reason": "同一地点的“市/省/省+市”层级重复，仅保留最具体名称；不同城市不合并",
            })

    # Tax rows: add validity without dropping expired/unknown rows.
    tax_rows = core.get("tax_qualifications") or []
    for row in tax_rows:
        if not isinstance(row, dict):
            continue
        before = row.get("有效性")
        after = _tax_validity_from_row(row, as_of)
        if before != after:
            row["有效性"] = after
            corrections.append({
                "field": "core_analysis.tax_qualifications[].有效性",
                "before": before,
                "after": after,
                "reason": "按有效期止与报告生成日期比较；缺失日期或 9999 不按普通有效处理",
            })

    # Section specs: add validity column; split ranking chart from full table.
    sections = [s for s in (core.get("sections") or []) if isinstance(s, dict)]
    for section in sections:
        if section.get("key") == "tax_qualifications":
            cols = [c for c in (section.get("columns") or []) if isinstance(c, (list, tuple))]
            if not any(c[0] == "有效性" for c in cols):
                cols.append(("有效性", "有效性"))
                section["columns"] = cols
                corrections.append({
                    "field": "core_analysis.sections[tax_qualifications].columns",
                    "before": "无有效性列",
                    "after": "增加“有效性”列",
                    "reason": "避免把过期或日期不明的税务资质当作当前有效",
                })
        if section.get("key") == "enterprise_rankings" and section.get("kind") == "bar":
            old_note = section.get("note", "")
            section["kind"] = "table"
            section["title"] = "企业排名明细"
            section["note"] = f"{old_note}；未返回排名的记录保留在表中，不进入排名图"
            section["columns"] = [("榜单名称", "榜单名称"), ("榜单类型", "榜单类型"), ("上榜公司名", "上榜公司名"), ("排名", "排名"), ("发布年份", "发布年份"), ("榜单级别", "榜单级别"), ("发布单位", "发布单位")]
            chart_section = {
                "key": "enterprise_rankings_chart",
                "title": "企业排名（有明确排名）",
                "kind": "bar",
                "note": "仅展示有明确排名的记录；排名数值越小越靠前。缺失排名不进入图表，避免被当作第 0 名。",
                "chart": {"name": "榜单名称", "value": "排名", "orient": "h"},
                "columns": [("榜单名称", "榜单名称"), ("排名", "排名"), ("发布年份", "发布年份")],
            }
            if not any(s.get("key") == "enterprise_rankings_chart" for s in sections):
                sections.insert(sections.index(section), chart_section)
            corrections.append({
                "field": "core_analysis.sections[enterprise_rankings]",
                "before": "单一 bar 图，缺排名记录按 0 进入图表",
                "after": "bar 图仅保留有明确排名记录，另设明细表保留全部记录",
                "reason": "图表值 0 会被误读为最高排名；缺失值不能补 0",
            })
    core["sections"] = sections

    # Remove exact duplicate ranking rows and rebuild chart data.
    ranking_rows = [r for r in (core.get("enterprise_rankings") or []) if isinstance(r, dict)]
    unique_rankings: List[Dict[str, Any]] = []
    seen_rank = set()
    for row in ranking_rows:
        key = tuple(str(row.get(k) or "") for k in ("榜单名称", "榜单类型", "上榜公司名", "排名", "发布年份", "榜单级别", "发布单位"))
        if key in seen_rank:
            continue
        seen_rank.add(key)
        unique_rankings.append(row)
    if len(unique_rankings) != len(ranking_rows):
        corrections.append({
            "field": "core_analysis.enterprise_rankings",
            "before": f"{len(ranking_rows)} 条",
            "after": f"{len(unique_rankings)} 条",
            "reason": "完全重复的榜单记录只保留一条",
        })
    core["enterprise_rankings"] = unique_rankings
    core["enterprise_rankings_chart"] = [
        row for row in unique_rankings
        if str(row.get("排名", "")).replace(",", "").strip().isdigit()
    ]
    if not core["enterprise_rankings_chart"]:
        core["sections"] = [s for s in core.get("sections", []) if s.get("key") != "enterprise_rankings_chart"]

    # Sort sentiment trend chronologically (chart expects time order).
    trend = core.get("news_sentiment_trend") or []
    if isinstance(trend, list) and trend:
        core["news_sentiment_trend"] = sorted(trend, key=lambda r: str((r or {}).get("月份") or ""))

    # Metrics: dedupe, replace financing trail, normalize brand origin.
    metrics = _dedupe_metrics([dict(m) for m in (out.get("metrics") or []) if isinstance(m, dict)])
    for metric in metrics:
        if metric.get("label") == "品牌发源地" and brand.get("品牌发源地"):
            metric["value"] = brand.get("品牌发源地")
        if metric.get("label") == "融资轮次":
            financing_rows = [r for r in (core.get("financing_info") or []) if isinstance(r, dict)]
            latest = max(financing_rows, key=lambda r: str(r.get("融资时间") or ""), default=None)
            before = metric.get("value")
            if latest and latest.get("融资轮次") not in (None, "", "-"):
                metric["label"] = "最新融资轮次"
                metric["value"] = str(latest.get("融资轮次"))
                metric["hint"] = f"按融资时间排序的最新记录（{latest.get('融资时间') or '日期不明'}）；不等同于全部轮次轨迹"
                corrections.append({
                    "field": "metrics[融资轮次]",
                    "before": before,
                    "after": metric["value"],
                    "reason": "原指标把上游返回顺序拼成轮次轨迹或仅给单轮；改为按日期的最新一轮并说明口径",
                })
        if metric.get("label") == "税务资质数":
            metric["hint"] = "本次返回的税务资质记录数；有效性见明细表，过期/日期不明不视为当前有效"
    out["metrics"] = metrics

    # Rebuild narrative from corrected core/metrics.
    insights = build_insights(subject, core, metrics)
    out["insights"] = insights
    out["executive_summary"] = [item["interpretation"] for item in insights][:5] or [build_abstract(subject, core, metrics)[:120]]
    abstract = build_abstract(subject, core, metrics)
    out["abstract"] = abstract
    out["summary"] = abstract
    source["content_review"] = {
        "mode": "offline_report_fields_only",
        "source_evidence_supplied": bool(source_evidence),
        "reviewed_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "corrections": _merge_review_records(previous_review.get("corrections"), corrections),
        "not_changed": [
            "未重新查询 MCP；未新增融资、榜单、税务资质或品牌事实",
            "过期税务资质与缺日期记录保留，只增加有效性标签",
            "缺失排名不从图表删除业务记录，仍保留在明细表",
        ],
    }
    out["data_source"] = source
    return _refresh_quality_report(out)


def _assemble(subject: Mapping[str, Any], core: Mapping[str, Any], metrics: Sequence[Mapping[str, Any]], *, dry_run: bool) -> Dict[str, Any]:
    metrics = _dedupe_metrics(metrics)
    abstract = build_abstract(subject, core, metrics)
    records = build_records(core)
    insights = build_insights(subject, core, metrics)
    # Quality gate: count populated core-analysis sections.
    ca = core if isinstance(core, dict) else {}
    secs = ca.get("sections", [])
    if secs:
        total_secs = len(secs)
        populated = sum(1 for s in secs if isinstance(s, dict) and _has_evidence(ca.get(s.get("key"))))
    else:
        total_secs = max(1, len([k for k in ca if k != "sections"]))
        populated = sum(1 for k in ca if k != "sections" and _has_evidence(ca.get(k)))
    quality_report = {
        "total_sections": total_secs,
        "populated_sections": populated,
        "empty_sections": total_secs - populated,
        "coverage_pct": round(populated / max(1, total_secs) * 100),
    }
    if populated == 0:
        import sys
        print("⚠️ 质量门禁警告: 所有核心分析维度均无数据", file=sys.stderr)
    title = f"{subject.get('enterprise') or '目标企业'} 企业经营分析报告"
    report = {
        "report_type": REPORT_TYPE,
        "title": title,
        "banner": REPORT_BANNER,
        "subject": dict(subject),
        "abstract": abstract,
        "summary": abstract,
        "executive_summary": [item["interpretation"] for item in insights][:5] or [abstract[:120]],
        "metrics": list(metrics),
        "caliber": build_caliber(subject),
        "core_analysis": dict(core),
        "representative_records": records,
        "insights": insights,
        "data_source": {
            "mcp_server": "enterprise-operation-mcp-server",
            "products": [
                {"name": "产品标签", "product_id": "66c33eff3c0917a9a02feb6f"},
                {"name": "公司趋势标签", "product_id": "67f3af2fac893a1d33dadebe"},
                {"name": "品牌概况", "product_id": "66c33eff3c0917a9a02feb80"},
                {"name": "企业排名", "product_id": "67f3be85ac893a1d33dadfbf"},
                {"name": "经营规模", "product_id": "67189489ae286373219cdd32"},
                {"name": "舆情情感统计", "product_id": "66b338e274bf098447db7efd"},
                {"name": "相似项目", "product_id": "66b0a51fce5e524754b8502d"},
                {"name": "税务资质", "product_id": "66a0f66a5646e2b0fc8ae758"},
                {"name": "融资信息", "product_id": "66a0f56efc5601eba12cc2e3"},
            ],
            "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "dry_run": dry_run,
            "quality_report": quality_report,
        },
    }
    return apply_content_review(report)


@paid_call_scope
def build_payload(raw: str, keyword_type: str, page_size: int, max_pages: Optional[int] = 1) -> Dict[str, Any]:
    if isinstance(max_pages, bool) or not isinstance(max_pages, int) or max_pages < 1:
        raise ValueError("max_pages 必须为正整数")
    resolved = resolve_enterprise_name(raw)
    if resolved.get("requires_confirmation"):
        subject = build_subject(raw, resolved, keyword_type)
        return _apply_resolution_limit(_assemble(subject, {"sections": []}, [], dry_run=False), resolved)
    enterprise = resolved["enterprise"]
    mk_args: Dict[str, Any] = {"matchKeyword": enterprise, "keywordType": keyword_type}

    product_tags = _safe_call(T_PRODUCT_TAGS, mk_args)
    company_trends = _safe_call(T_COMPANY_TRENDS, mk_args)
    brand = _safe_call(T_BRAND_PROFILE, mk_args)
    scale = _safe_call(T_BUSINESS_SCALE, mk_args)
    rankings = _collect_detail_pages(T_RANKINGS, {**mk_args, "pageIndex": 1, "pageSize": min(page_size, 10)}, max_pages)
    financing = _safe_call(T_FINANCING_INFO, mk_args)
    tax = _safe_call(T_TAX_QUALIFICATIONS, mk_args)
    similar = _collect_detail_pages(T_SIMILAR_PROJECTS, {**mk_args, "pageIndex": 1, "pageSize": min(page_size, 10)}, max_pages)
    sentiment = _safe_call(T_NEWS_SENTIMENT, mk_args)

    subject = build_subject(raw, resolved, keyword_type)
    core = build_core_analysis(
        product_tags, company_trends, brand, scale, rankings, financing, tax, similar, sentiment
    )
    metrics = build_metrics(scale, rankings, financing, similar)
    _derive_core_metrics(metrics, core if isinstance(core, dict) else {})
    report = _assemble(subject, core, metrics, dry_run=False)
    report = attach_pagination(report, {"企业排名": rankings, "相似项目": similar})
    return _attach_call_status(report, {"产品标签": product_tags, "趋势标签": company_trends, "品牌概况": brand, "经营规模": scale, "企业排名": rankings, "融资信息": financing, "税务资质": tax, "相似项目": similar, "舆情统计": sentiment})


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(description="Compose an enterprise-operation insight report via the enterprise-operation MCP.")
    parser.add_argument("--enterprise", required=True, help="企业全称或关键词（关键词将自动模糊补全）")
    parser.add_argument("--keyword-type", default="name", help="主体类型：name/nameId/regNumber/socialCreditCode")
    parser.add_argument("--page-size", type=int, default=10, help="分页大小（最多 10）")
    parser.add_argument("--max-pages", type=int, default=1, help="企业排名 / 相似项目最多查询页数（正整数，默认 1 页；按报告结论需要先计划预算再显式扩大）")
    parser.add_argument("--dry-run", action="store_true", help="不调用真实 MCP，使用样例数据组装报告骨架")
    parser.add_argument("--output", help="输出 JSON 路径；省略则打印到 stdout")
    parser.add_argument("--report-output", help="同时输出 HTML 报告（.html）与 Markdown 报告（.md）")
    parser.add_argument("--pdf-output", help="额外输出 PDF 报告（.pdf）；需要 Playwright + Chromium")
    args = parser.parse_args()

    if not 1 <= args.page_size <= 10:
        parser.error("--page-size 必须在 1 到 10 之间")
    if args.max_pages < 1:
        parser.error("--max-pages 必须为正整数")
    if args.dry_run:
        payload = build_dry_run_payload(args.enterprise, args.keyword_type)
    else:
        payload = build_payload(args.enterprise, args.keyword_type, args.page_size, args.max_pages)

    if args.output:
        out = pathlib.Path(args.output).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json_dumps(payload, pretty=True), encoding="utf-8")
        print_json({"ok": True, "json": str(out), "dry_run": args.dry_run})
    else:
        print_json(payload)

    if args.report_output:
        base_out = pathlib.Path(args.report_output).expanduser()
        base_out.parent.mkdir(parents=True, exist_ok=True)
        html_path = base_out.with_suffix(".html") if base_out.suffix.lower() not in (".html", ".htm") else base_out
        md_path = html_path.with_suffix(".md")
        html_path.write_text(render_html(payload), encoding="utf-8")
        md_path.write_text(render_markdown(payload), encoding="utf-8")
        if args.pdf_output:
            pdf_path = pathlib.Path(args.pdf_output).expanduser()
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            html_to_pdf(render_html(payload), str(pdf_path))
        print_json({"ok": True, "html": str(html_path), "markdown": str(md_path), "pdf": str(pdf_path) if args.pdf_output else None, "dry_run": args.dry_run})


if __name__ == "__main__":
    main()
