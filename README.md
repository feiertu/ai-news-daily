# AI News Daily 📰

每日自动抓取 [AI Hot Tracker](https://aihot.joeplab.cn) 的 AI 资讯，生成 Markdown 日报。

## 信源覆盖

AI精选 · 36kr · IT之家 · 少数派 · ChinAI · 爱范儿 · arxiv · GitHub · Interconnects · Latent Space · Dev.to

## 工作方式

- ⏰ **每天 08:57 (北京时间)** GitHub Actions 自动运行
- 📥 抓取所有 11 个信源的最新文章
- 📄 生成日报保存到 `digest/YYYY-MM-DD.md`
- 🚀 可选创建 GitHub Issue 推送通知

## 手动触发

在 GitHub 仓库的 Actions 页面，点击 "Daily AI News Digest" → "Run workflow"

## 目录结构

```
├── .github/workflows/daily-news.yml   # GitHub Actions 配置
├── scripts/fetch_news.py              # 抓取脚本
└── digest/                            # 每日日报存档
    ├── 2026-06-15.md
    └── ...
```
