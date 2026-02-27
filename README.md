# 财联社涨停分析推送

每天自动百度搜索财联社涨停分析，提取文章内容推送到 Telegram。

## 工作原理

1. 🔍 **百度搜索**：搜索"【X月X日涨停分析】财联社X月X日电"
2. 🔗 **打开第一个链接**：访问财联社文章页面
3. 📄 **提取内容**：从页面中提取 `class="dpu8C _2kCxD"` 的div内容
4. 📱 **Telegram推送**：将原文推送到你的Telegram

## 部署步骤

### 1. Fork 本项目到 GitHub

### 2. 配置 Secrets

在仓库 Settings → Secrets and variables → Actions 中添加：

| Secret 名称 | 说明 | 必填 |
|------------|------|------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | ✅ |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | ✅ |

### 3. 启用 Actions

Actions → Daily Report → Enable

### 4. 手动测试

Actions → Daily Report → Run workflow

## 推送内容示例

```
【2月27日涨停分析】财联社2月27日电，今日全市场共75股涨停，连板股总数10只，15股封板未遂，封板率为83%（不含ST股、退市股）。焦点股方面，投资先天算力的豫能控股晋级7连板，化工板块的金正大尾盘回封晋级4连板，有色金属概念章源钨业7天5板3连板，电力板块赣能股份3连板，家居概念洪兴股份3连板。
```

## 定时说明

- 运行时间：工作日每天北京时间 17:00（下午5点）
- 自动跳过：周末

## 技术栈

- Python 3.11
- requests + BeautifulSoup（爬取）
- python-telegram-bot（推送）
- GitHub Actions（定时任务）
