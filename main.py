import os
import requests
import datetime
import re
import sys
from playwright.sync_api import sync_playwright

# 配置信息
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
DEBUG_DATE = os.getenv('DEBUG_DATE')

def send_tg_msg(text):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("❌ 错误: 未配置 TG_TOKEN 或 TG_CHAT_ID")
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"发送消息失败: {e}")

def get_target_date():
    if DEBUG_DATE and DEBUG_DATE.strip():
        return DEBUG_DATE.strip()
    return datetime.datetime.now().strftime('%Y-%m-%d')

def is_trading_day(date_str):
    if DEBUG_DATE:
        print(f"🛠 调试模式：强制判定 {date_str} 为交易日")
        return True
    try:
        # 使用本地逻辑判断周末，减少对 API 的依赖
        dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        if dt.weekday() >= 5: return False
        
        # 进一步检查法定节假日
        resp = requests.get(f"https://timor.tech/api/holiday/info/{date_str}", timeout=10)
        return resp.json()['type']['type'] == 0
    except:
        return True # 出错时默认运行，防止错过抓取

def scrape():
    target_date_str = get_target_date()
    dt_obj = datetime.datetime.strptime(target_date_str, '%Y-%m-%d')
    date_keyword = f"{dt_obj.month}月{dt_obj.day}日"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"正在访问财联社，检索日期关键词: {date_keyword}")
        
        page.goto("https://www.cls.cn/telegraph", wait_until="networkidle")
        
        # 调试模式下多滚屏几次，确保能看到旧电报
        if DEBUG_DATE:
            for _ in range(3):
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(1000)

        items = page.locator(".telegraph-list .item").all()
        target_text = ""
        for item in items:
            text = item.inner_text()
            if "全市场共" in text and "涨停" in text and date_keyword in text:
                target_text = text
                break
        
        browser.close()
        
        if not target_text:
            raise Exception(f"未找到 {date_keyword} 的相关数据条目")

        # 正则解析
        try:
            zt = re.search(r"共(\d+)股涨停", target_text).group(1)
            lb = re.search(r"连板股总数(\d+)只", target_text).group(1)
            fail = re.search(r"(\d+)股封板未遂", target_text).group(1)
            rate = re.search(r"封板率为(\d+%)", target_text).group(1)
            focus = re.search(r"焦点股方面，(.*?)。", target_text).group(1)
            
            return (f"📊 财联社盘后分析 ({date_keyword})\n\n"
                    f"✅ 涨停总数：{zt}\n"
                    f"🔗 连板总数：{lb}\n"
                    f"❌ 封板未遂：{fail}\n"
                    f"📈 封板率：{rate}\n\n"
                    f"🔥 焦点股：\n{focus}")
        except Exception as e:
            raise Exception(f"解析文本失败: {e}\n原文内容: {target_text[:50]}...")

if __name__ == "__main__":
    t_date = get_target_date()
    if is_trading_day(t_date):
        try:
            msg = scrape()
            send_tg_msg(msg)
            print("🎉 任务圆满完成！")
        except Exception as e:
            err_msg = f"❌ 抓取失败: {str(e)}"
            print(err_msg)
            send_tg_msg(err_msg)
            sys.exit(1) # 只有真正的错误才抛出 exit 1
    else:
        send_tg_msg(f"💤 {t_date} 非交易日，程序已休眠。")
