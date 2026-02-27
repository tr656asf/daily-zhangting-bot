# AkShare 每日涨停数据推送

每天下午5点自动获取A股涨停数据，推送到 Telegram。

## 功能特点

- 📈 **真实数据源**：使用 AkShare 金融数据接口，直接获取交易所数据
- 🕐 **定时推送**：工作日每天下午5点（北京时间）自动运行
- 📱 **Telegram 推送**：即时推送到手机
- 🆓 **零成本**：GitHub Actions 免费运行
- 🔒 **安全可靠**：不爬网页，使用官方数据源

## 数据来源

使用 [AkShare](https://www.akshare.xyz/) 开源金融数据接口，数据来源：
- 东方财富
- 上海证券交易所
- 深圳证券交易所

## 部署步骤

### 1. Fork 本项目到 GitHub

### 2. 配置 Secrets

在仓库 Settings → Secrets and variables → Actions 中添加：

| Secret 名称 | 说明 | 必填 |
|------------|------|------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | ✅ |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | ✅ |

### 3. 启用 Actions

Actions → AkShare Daily Report → Enable

### 4. 手动测试

Actions → AkShare Daily Report → Run workflow

## 推送内容示例

```
📊 2024年2月27日 涨停分析

🔥 涨停概况
今日涨停股票：85只
连板股票：23只
最高连板：8连板

📈 连板天梯
8连板：克来机电
5连板：蓝科高新
4连板：睿能科技、华扬联众
...

💡 热点板块
机器人概念：15只涨停
人工智能：12只涨停
汽车零部件：8只涨停
```

## 定时说明

- 运行时间：每天北京时间 17:00（下午5点）
- 运行条件：工作日（自动跳过周末和法定节假日）
- 时区：UTC+8（北京时间）

## 技术栈

- Python 3.10+
- AkShare（金融数据）
- python-telegram-bot（推送）
- GitHub Actions（定时任务）

## License

MIT
