# 财联社涨停分析推送

每天下午5点自动爬取财联社涨停分析，推送到 Telegram。

## 工作原理

1. 🔍 **访问财联社搜索页**：`https://www.cls.cn/searchPage?keyword=X月X日涨停分析`
2. 🔗 **查找文章**：找到标题为"【X月X日涨停分析】"的文章
3. 📄 **打开文章页**：使用 Playwright 模拟浏览器访问
4. 📋 **提取内容**：提取文章正文内容
5. 📱 **推送**：原样发送到 Telegram

## 技术栈

- **Playwright**：模拟浏览器，获取动态渲染内容
- **python-telegram-bot**：Telegram 推送
- **GitHub Actions**：定时运行

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

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt
playwright install chromium

# 设置环境变量
export TELEGRAM_BOT_TOKEN="你的token"
export TELEGRAM_CHAT_ID="你的chat_id"

# 运行
cd src
python main.py
```
