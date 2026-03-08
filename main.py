import os
import requests
import datetime
import re
from playwright.sync_api import sync_playwright

# 获取环境变量
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
# 新增：调试日期环境变量 (格式如: 2026-03-06)
DEBUG_DATE = os.getenv('DEBUG_DATE')

def get_target_date():
    """确定当前运行的目标日期"""
    if DEBUG_DATE:
        return DEBUG_DATE
    return datetime.datetime.now().strftime('%Y-%m-%d')

def is_trading_day(date_str):
    """判断指定日期是否为交易日"""
    # 如果处于调试模式，我们强制让它返回 True，以便运行后续爬虫逻辑
    if DEBUG_DATE:
        print(f"🛠 调试模式：强制判定 {date_str} 为交易日")
        return True
        
    try:
        response = requests.get(f"https://timor.tech/api/holiday/info/{date_str}")
        data = response.json()
        return data['type']['type'] == 0
    except:
        # 基础保底逻辑
        dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return dt.weekday() < 5

def scrape_and_parse():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.cls.cn/telegraph")
        
        # 调试模式下，我们可能需要向下滚动一下，以防目标日期的电报在第二页
        if DEBUG_DATE:
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(1000)

        # 优化定位：寻找包含关键词的电报
        # 如果是调试，我们寻找包含特定日期（如 "3月6日"）的电报
        target_content = None
        items = page.locator(".telegraph-list .item").all()
        
        # 转换日期格式用于匹配，例如 2026-03-06 转为 3月6日
        dt_obj = datetime.datetime.strptime(get_target_date(), '%Y-%m-%d')
        date_keyword = f"{dt_obj.month}月{dt_obj.day}日"

        for item in items:
            text = item.inner_text()
            if "全市场共" in text and "涨停" in text and date_keyword in text:
                target_content = text
                break
        
        if not target_content:
            raise Exception(f"未找到 {date_keyword} 的涨停分析数据")

        # ... (正则提取逻辑保持不变) ...
        return format_message(target_content) # 假设提取逻辑封装在此

if __name__ == "__main__":
    current_date = get_target_date()
    if is_trading_day(current_date):
        try:
            report = scrape_and_parse()
            send_tg_msg(report)
        except Exception as e:
            send_tg_msg(f"❌ 运行失败: {str(e)}")
    else:
        send_tg_msg(f"💤 {current_date} 非交易日，跳过抓取。")
