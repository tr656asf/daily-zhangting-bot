# 涨停分析报告推送

每天下午5点自动获取A股涨停数据，推送到 Telegram。

## 数据说明

**数据源**：AkShare（开源金融数据接口）
- 直接对接东方财富、交易所官方数据
- 无需爬取网页，数据准确稳定
- 包含涨停股票数、连板数、焦点股等

**推送格式**：
```
【2月27日涨停分析】AkShare2月27日电，今日全市场共75股涨停，连板股总数10只，最高8连板。焦点股方面，克来机电8连板、蓝科高新5连板...
```

## 部署步骤

### 1. Fork 到 GitHub

### 2. 配置 Secrets
Settings → Secrets → Actions：
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### 3. 启用 Actions
Actions → Daily Report → Enable

### 4. 测试运行
Actions → Daily Report → Run workflow

## 定时说明

- **运行时间**：工作日每天北京时间 **17:00**（下午5点）
- **自动跳过**：周末（周六、周日）

## 技术栈

- Python 3.11
- AkShare（金融数据）
- python-telegram-bot（推送）
- GitHub Actions（定时任务）
