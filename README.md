# 财联社涨停分析推送

每天下午5点自动百度搜索财联社涨停分析，推送到 Telegram。

## 工作原理

1. 🔍 **百度搜索**：搜索"【X月X日涨停分析】财联社"
2. 📄 **解析结果**：从搜索结果中提取em标签内容
3. 📱 **推送**：将提取的文本原样发送到 Telegram

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

## 推送内容示例

```
【2月27日涨停分析】财联社2月27日电，今日全市场共75股涨停，连板股总数10只，15股封板未遂，封板率为83%（不含ST股、退市股）。焦点股方面，投资先天算力的豫能控股晋级7连板...
```

## 定时说明

- **运行时间**：工作日每天北京时间 **17:00**（下午5点）
- **自动跳过**：周末（周六、周日）

## 测试参数

手动运行时可设置：
- **force_run**: `1` - 强制运行（跳过周末检查）
- **simulate_date**: `2026-02-05` - 指定日期（格式：YYYY-MM-DD）

## 技术栈

- Python 3.11
- requests + BeautifulSoup（百度搜索和解析）
- python-telegram-bot（推送）
- GitHub Actions（定时任务）
