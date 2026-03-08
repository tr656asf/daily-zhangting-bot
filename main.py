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
    # 考虑北京时间
    return (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d')

def is_trading_day(date_str):
    if DEBUG_DATE:
        print(f"🛠 调试模式：强制判定 {date_str} 为交易日")
        return True
    try:
        dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        if dt.weekday() >= 5: return False
        resp = requests.get(f"https://timor.tech/api/holiday/info/{date_str}", timeout=10)
        return resp.json()['type']['type'] == 0
    except:
        return True 

def scrape():
    target_date_str = get_target_date()
    dt_obj = datetime.datetime.strptime(target_date_str, '%Y-%m-%d')
    date_keyword = f"{dt_obj.month}月{dt_obj.day}日"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print(f"🚀 正在通过 API 拦截模式访问财联社 (目标: {date_keyword})...")
        target_text = ""

        # API 拦截逻辑
        def handle_response(response):
            nonlocal target_text
            if "telegraph" in response.url and response.status == 200:
                try:
                    json_data = response.json()
                    for item in json_data.get('data', {}).get('roll_data', []):
                        content = item.get('content', '')
                        if "全市场共" in content and "涨停" in content and date_keyword in content:
                            target_text = content
                            print("✅ 已从 API 响应中截获目标数据！")
                except:
                    pass

        page.on("response", handle_response)
        page.goto("https://www.cls.cn/telegraph", wait_until="networkidle", timeout=60000)
        
        if not target_text:
            print("💡 第一页未找到，正在向下滚动触发加载...")
            for _ in range(12): # 增加滚动次数以找回旧数据
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(1000)
                if target_text: break

        browser.close()
        
        if not target_text:
            raise Exception(f"🔎 未发现 {date_keyword} 的总结电报。")

        # --- 核心解析逻辑 ---
        try:
            # 这里的正则增加了对空格和换行的兼容
            zt = re.search(r"共\s*(\d+)\s*股涨停", target_text).group(1)
            lb = re.search(r"连板股总数\s*(\d+)\s*只", target_text).group(1)
            fail = re.search(r"(\d+)\s*股封板未遂", target_text).group(1)
            rate = re.search(r"封板率为\s*(\d+%)", target_text).group(1)
            focus = re.search(r"焦点股方面，(.*?)(?:。|$)", target_text, re.S).group(1).strip()
            
            return (f"📊 财联社盘后分析 ({date_keyword})\n\n"
                    f"✅ 涨停总数：{zt}\n"
                    f"🔗 连板总数：{lb}\n"
                    f"❌ 封板未遂：{fail}\n"
                    f"📈 封板率：{rate}\n\n"
                    f"🔥 焦点股：\n{focus}")
        except Exception as e:
            raise Exception(f"解析失败: {e}\n抓取内容: {target_text[:50]}...")

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
            sys.exit(1)
    else:
        send_tg_msg(f"💤 {t_date} 非交易日，程序已休眠。")
