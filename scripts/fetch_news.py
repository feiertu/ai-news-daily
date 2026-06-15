#!/usr/bin/env python3
"""AI Hot Tracker — 每日资讯抓取脚本
从 https://aihot.joeplab.cn 获取所有信源的最新 AI 资讯，生成 Markdown 摘要。
"""

import json
import urllib.request
import sys
from datetime import datetime, timezone, timedelta

BASE = "https://aihot.joeplab.cn"

# 信源优先级：排前面的先展示
PRIORITY_SOURCES = [
    "aihot", "36kr", "ithome", "sspai", "chinai",
    "ifanr", "arxiv", "github", "interconnects", "latentspace", "devto"
]


def fetch_json(path):
    """请求 API 并返回 JSON"""
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "AI-News-Daily/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ⚠️ 请求失败 {url}: {e}", file=sys.stderr)
        return None


def is_recent(article):
    """判断文章是否在最近24小时内"""
    t = article.get("time_ago", "")
    return any(unit in t for unit in ["分钟前", "小时前"])


def fetch_all_news():
    """获取所有信源的文章"""
    # 获取信源列表 + 名称映射
    sources_data = fetch_json("/api/sources")
    if not sources_data:
        print("❌ 无法获取信源列表", file=sys.stderr)
        return [], {}

    name_map = {s["key"]: s["name"] for s in sources_data.get("sources", [])}

    all_articles = []
    for key in PRIORITY_SOURCES:
        if key not in name_map:
            continue
        data = fetch_json(f"/api/source/{key}")
        if not data:
            continue
        for a in data.get("articles", []):
            a["source_key"] = key
            all_articles.append(a)

    return all_articles, name_map


def format_markdown(articles, name_map):
    """生成 Markdown 日报"""
    now = datetime.now(timezone(timedelta(hours=8)))
    date_str = now.strftime("%Y-%m-%d")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()]

    lines = [
        f"# 🤖 AI 资讯日报 — {date_str} {weekday}",
        "",
        f"> 自动抓取自 [AI Hot Tracker](https://aihot.joeplab.cn)，覆盖 {len(name_map)} 个信源。",
        f"> 更新时间：{now.strftime('%H:%M')} (UTC+8)",
        "",
        "---",
        "",
    ]

    # 按信源分组
    grouped = {}
    for a in articles:
        key = a.get("source_key", "other")
        grouped.setdefault(key, []).append(a)

    # 只保留24h内的
    recent_count = 0
    for key in PRIORITY_SOURCES:
        if key not in grouped:
            continue
        src_articles = [a for a in grouped[key] if is_recent(a)]
        if not src_articles:
            continue

        src_name = name_map.get(key, key)
        lines.append(f"## 📌 {src_name}")
        lines.append("")

        for a in src_articles[:8]:  # 每个信源最多8条
            title = a.get("title", "无标题")
            url = a.get("url", "#")
            desc = a.get("description", "")[:120]
            time_ago = a.get("time_ago", "")

            lines.append(f"- **[{title}]({url})**")
            if desc:
                lines.append(f"  > {desc}")
            lines.append(f"  `{time_ago}`")
            lines.append("")
            recent_count += 1

    if recent_count == 0:
        lines.append("> ⚠️ 今日暂无最近24小时内的资讯，请稍后再试。")
    else:
        lines.append(f"> 📊 共收录 **{recent_count}** 条24小时内资讯")

    lines.extend([
        "",
        "---",
        "",
        f"*🤖 本日报由 GitHub Actions 自动生成 · [AI Hot Tracker](https://aihot.joeplab.cn)*",
    ])

    return "\n".join(lines)


def main():
    print("🔍 正在获取 AI Hot Tracker 资讯...")
    articles, name_map = fetch_all_news()
    print(f"✅ 共获取 {len(articles)} 篇文章")

    md = format_markdown(articles, name_map)
    print(md)

    # 同时输出到文件
    now = datetime.now(timezone(timedelta(hours=8)))
    filename = f"digest/{now.strftime('%Y-%m-%d')}.md"
    import os
    os.makedirs("digest", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n📄 已保存到 {filename}")


if __name__ == "__main__":
    main()
