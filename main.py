import os
import requests
import datetime
import re
from playwright.sync_api import sync_playwright

# 从 GitHub Secrets 获取敏感信息
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def send_tg_msg(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    requests.post(url, json=payload)

def is_trading_day():
    # 获取当前日期 (YYYY-MM-DD)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    # 使用开源节假日 API (例如 timor.tech)
    try:
        response = requests.get(f"https://timor.tech/api/holiday/info/{today}")
        data = response.json()
        # type: 0 是工作日, 1 是周末, 2 是节日, 3 是调休
        # 注意：中国股市在“调休后的周六日”也是不交易的
        if data['type']['type'] == 0:
            return True
        return False
    except:
        # 如果 API 失效，退化到基础周六日判断
        weekday = datetime.datetime.now().weekday()
        return weekday < 5

def scrape_and_parse():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.cls.cn/telegraph")
        # 寻找包含核心关键词的电报
        content_element = page.locator("text='全市场共'").first
        content = content_element.inner_text()
        
        # 正则提取
        date_str = re.search(r"(\d+月\d+日)", content).group(1)
        zt_num = re.search(r"共(\d+)股涨停", content).group(1)
        lb_num = re.search(r"连板股总数(\d+)只", content).group(1)
        fail_num = re.search(r"(\d+)股封板未遂", content).group(1)
        rate = re.search(r"封板率为(\d+%)", content).group(1)
        focus = re.search(r"焦点股方面，(.*?)。", content).group(1)
        
        msg = (f"📊 财联社盘后分析 ({date_str})\n\n"
               f"✅ 涨停总数：{zt_num}\n"
               f"🔗 连板总数：{lb_num}\n"
               f"❌ 封板未遂：{fail_num}\n"
               f"📈 封板率：{rate}\n\n"
               f"🔥 焦点股：\n{focus}")
        return msg

if __name__ == "__main__":
    if True:
        try:
            report = scrape_and_parse()
            send_tg_msg(report)
        except Exception as e:
            send_tg_msg(f"❌ 抓取失败: {str(e)}")
    else:
        send_tg_msg("💤 今日非交易日，休息中。")
